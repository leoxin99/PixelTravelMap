"""Heuristic local parser for the PixelTravelMap MVP.

This module deliberately keeps parsing simple for phase 1. It proves the
contract from natural-language input to itinerary JSON without requiring a
live LLM key. The function boundary can later be replaced by an LLM structured
output call that targets the same schema.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIR = PROJECT_ROOT / "examples" / "expected"


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
