"""Heuristic local parser for the PixelTravelMap MVP.

This module deliberately keeps parsing simple for phase 1. It proves the
contract from natural-language input to itinerary JSON without requiring a
live LLM key. The function boundary can later be replaced by an LLM structured
output call that targets the same schema.
"""

from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIR = PROJECT_ROOT / "examples" / "expected"
VALID_CATEGORIES = {
    "landmark",
    "museum",
    "food",
    "hotel",
    "nature",
    "transit",
    "shopping",
    "experience",
    "viewpoint",
}
VALID_TRANSPORT = {"self-drive", "train", "public-transit", "walk", "mixed", "unknown"}


@dataclass
class ParseNeedInput(Exception):
    """Raised when the MVP parser needs a concise user clarification."""

    message: str
    questions: list[str]

    def __str__(self) -> str:
        return self.message


SAMPLE_ROUTES = [
    {
        "name": "italy_france_switzerland_self_drive",
        "file": "italy_france_switzerland_self_drive.json",
        "keywords": ["意法瑞", "米兰", "瑞士", "自驾", "como", "milan"],
    },
    {
        "name": "beijing_family_trip",
        "file": "beijing_family_trip.json",
        "keywords": ["北京", "故宫", "亲子", "动物园", "颐和园"],
    },
    {
        "name": "japan_kansai_city_trip",
        "file": "japan_kansai_city_trip.json",
        "keywords": ["关西", "大阪", "京都", "奈良", "神户", "kansai"],
    },
]


CHINESE_DAY_WORDS = {
    "一天": 1,
    "两天": 2,
    "二天": 2,
    "三天": 3,
    "四天": 4,
    "五天": 5,
    "六天": 6,
    "七天": 7,
    "八天": 8,
    "九天": 9,
    "十天": 10,
}


def load_trip_template(filename: str) -> dict[str, Any]:
    with (EXPECTED_DIR / filename).open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_travel_text(text: str) -> dict[str, Any]:
    """Parse one travel description into itinerary JSON.

    Phase 1 supports the curated demo prompts from the roadmap. Unknown inputs
    return a structured clarification error instead of hallucinating an
    itinerary.
    """

    normalized = text.strip().lower()
    if not normalized:
        raise ParseNeedInput(
            "输入为空，无法生成行程。",
            ["请补充目的地。", "请补充旅行天数。"],
        )

    if "lat:" in normalized and "lon:" in normalized:
        return parse_coordinate_trip_text(text)

    has_days = bool(re.search(r"\d+\s*天", normalized)) or any(
        word in text for word in CHINESE_DAY_WORDS
    )
    has_destination = any(
        keyword.lower() in normalized
        for route in SAMPLE_ROUTES
        for keyword in route["keywords"]
    )

    if not has_destination or not has_days:
        questions: list[str] = []
        if not has_destination:
            questions.append("这次旅行的主要目的地是哪里？")
        if not has_days:
            questions.append("计划旅行几天？")
        raise ParseNeedInput("缺少生成地图的关键信息。", questions[:2])

    for route in SAMPLE_ROUTES:
        if any(keyword.lower() in normalized for keyword in route["keywords"]):
            return copy.deepcopy(load_trip_template(route["file"]))

    raise ParseNeedInput(
        "当前本地 MVP parser 还不认识这个目的地组合。",
        ["请先使用意法瑞、北京亲子游或日本关西三个 demo 输入之一。"],
    )


def load_trip_from_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_coordinate_trip_text(text: str) -> dict[str, Any]:
    """Parse reusable natural-language input with explicit POI coordinates."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = _metadata_value(lines, ["标题", "title"]) or "自定义 PixelTravelMap 行程"
    date_range = _metadata_value(lines, ["日期", "date", "dates"])
    start_date, end_date = _parse_date_range(date_range)
    transport = _metadata_value(lines, ["交通", "transport"]) or "mixed"
    if transport not in VALID_TRANSPORT:
        raise ParseNeedInput(
            "交通方式不在支持范围内。",
            [f"请使用这些 transport 值之一：{', '.join(sorted(VALID_TRANSPORT))}。"],
        )

    days: list[dict[str, Any]] = []
    current_day: dict[str, Any] | None = None
    missing: list[str] = []

    for line in lines:
        day_match = re.match(r"^Day\s*(\d+)\s*[：:]\s*(.+)$", line, flags=re.IGNORECASE)
        if day_match:
            day_num = int(day_match.group(1))
            day_date = start_date + dt.timedelta(days=day_num - 1)
            current_day = {
                "day": day_num,
                "date": day_date.isoformat(),
                "summary": day_match.group(2).strip(),
                "meeting_time": None,
                "meeting_point": "",
                "cautions": "",
                "stops": [],
            }
            days.append(current_day)
            continue

        if not line.startswith("-"):
            continue

        if current_day is None:
            missing.append(f"{line}: 缺少所属 Day 标题")
            continue
        try:
            current_day["stops"].append(_parse_coordinate_stop(line, current_day["day"]))
        except ParseNeedInput as exc:
            missing.extend(exc.questions)

    if not days:
        raise ParseNeedInput(
            "没有识别到 Day 行程段。",
            ["请按 `Day 1：当天摘要` 的格式添加每天行程。"],
        )
    empty_days = [day["day"] for day in days if not day["stops"]]
    if empty_days:
        missing.append(f"Day {empty_days[0]} 缺少地点条目。")
    if missing:
        raise ParseNeedInput("坐标化行程信息不完整，无法生成地图。", missing[:4])

    inferred_end = start_date + dt.timedelta(days=max(day["day"] for day in days) - 1)
    end_date = max(end_date, inferred_end)
    return {
        "schema_version": "1.0",
        "trip_title": title,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "travelers": ["traveler"],
        "budget_cny": None,
        "transport": transport,
        "style_theme": "pastel-pixel",
        "lang": "zh-CN",
        "days": days,
    }


def _metadata_value(lines: list[str], keys: list[str]) -> str | None:
    for line in lines:
        for key in keys:
            if re.match(rf"^{re.escape(key)}\s*[：:]", line, flags=re.IGNORECASE):
                return re.split(r"[：:]", line, maxsplit=1)[1].strip()
    return None


def _parse_date_range(value: str | None) -> tuple[dt.date, dt.date]:
    if not value:
        today = dt.date.today()
        return today, today
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", value)
    if not dates:
        raise ParseNeedInput(
            "日期格式无法识别。",
            ["请使用 `日期：2026-07-01 到 2026-07-03` 的格式。"],
        )
    start = dt.date.fromisoformat(dates[0])
    end = dt.date.fromisoformat(dates[-1])
    return start, max(start, end)


def _parse_coordinate_stop(line: str, day_num: int) -> dict[str, Any]:
    match = re.match(r"^-\s*(.*?)\s*[（(](.*?)[）)]\s*$", line)
    if not match:
        raise ParseNeedInput(
            "地点条目格式无法识别。",
            [f"{line}: 请使用 `- 地点名 (lat:..., lon:..., city:..., country:..., category:..., duration:...)`。"],
        )
    name = match.group(1).strip()
    fields = _parse_field_list(match.group(2))
    required = ["lat", "lon", "city", "country", "category", "duration"]
    missing = [field for field in required if not fields.get(field)]
    if missing:
        raise ParseNeedInput(
            "地点条目缺少必要字段。",
            [f"{name}: 缺少 {', '.join(missing)}。"],
        )

    category = fields["category"]
    if category not in VALID_CATEGORIES:
        raise ParseNeedInput(
            "地点 category 不在支持范围内。",
            [f"{name}: category 请使用 {', '.join(sorted(VALID_CATEGORIES))} 之一。"],
        )

    try:
        lat = float(fields["lat"])
        lon = float(fields["lon"])
        duration = int(float(fields["duration"]))
    except ValueError as exc:
        raise ParseNeedInput(
            "地点坐标或停留时间格式不正确。",
            [f"{name}: lat/lon 需要是数字，duration 需要是分钟数。"],
        ) from exc

    info_missing = fields.get("info_missing", "false").lower() == "true"
    source = "info_missing" if info_missing else fields.get("source", "user_coordinate_input")
    reservation_required = fields.get("reservation", "false").lower() in {
        "true",
        "yes",
        "required",
        "1",
        "需要",
        "是",
    }
    buffer_value = fields.get("buffer", fields.get("transit_buffer", "20"))
    try:
        transit_buffer_min = max(0, min(360, int(float(buffer_value))))
    except ValueError:
        transit_buffer_min = 20

    return {
        "id": _slugify(f"day-{day_num}-{name}"),
        "name": name,
        "name_en": fields.get("name_en"),
        "city": fields["city"],
        "country": fields["country"],
        "lat": lat,
        "lon": lon,
        "crs": fields.get("crs", "wgs84"),
        "category": category,
        "duration_min": duration,
        "arrival_time": fields.get("arrival") or fields.get("arrival_time"),
        "reservation_required": reservation_required,
        "reservation_time": fields.get("reservation_time"),
        "reservation_reference": fields.get("reservation_reference", ""),
        "transit_buffer_min": transit_buffer_min,
        "cautions": fields.get("cautions", fields.get("caution", "")),
        "description": fields.get("description"),
        "notes": fields.get("notes", "用户输入坐标地点。"),
        "source": source,
        "source_url": fields.get("source_url"),
        "official_url": fields.get("official_url"),
        "navigation_url": fields.get("navigation_url"),
        "info_missing": info_missing,
    }


def _parse_field_list(value: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in re.split(r"\s*[,，]\s*", value.strip()):
        if not part or ":" not in part:
            continue
        key, field_value = part.split(":", 1)
        fields[key.strip().lower()] = field_value.strip()
    return fields


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    suffix = hashlib.sha1(value.encode("utf-8")).hexdigest()[:6]
    return f"{slug or 'stop'}-{suffix}"
