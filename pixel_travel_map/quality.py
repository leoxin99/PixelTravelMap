"""Validation and artifact checks for PixelTravelMap."""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


TOP_LEVEL_REQUIRED = [
    "schema_version",
    "trip_title",
    "start_date",
    "end_date",
    "travelers",
    "transport",
    "style_theme",
    "lang",
    "days",
]

STOP_REQUIRED = [
    "id",
    "name",
    "city",
    "country",
    "lat",
    "lon",
    "crs",
    "category",
    "duration_min",
    "notes",
    "source",
    "info_missing",
]

TRANSPORT_VALUES = {"self-drive", "train", "public-transit", "walk", "mixed", "unknown"}
THEME_VALUES = {
    "pastel-pixel",
    "cyberpunk-neon",
    "vintage-parchment",
    "monochrome-ink",
    "forest-ghibli",
}
LANG_VALUES = {"zh-CN", "en-US"}
CRS_VALUES = {"wgs84", "gcj02"}
CATEGORY_VALUES = {
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


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _is_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def validate_trip(trip: dict[str, Any]) -> list[str]:
    """Return validation errors for the MVP schema contract.

    The repository also includes a JSON Schema file. This lightweight validator
    keeps the local demo dependency-free while checking the fields that matter
    most for generation and interview discussion.
    """

    errors: list[str] = []
    for field in TOP_LEVEL_REQUIRED:
        if field not in trip:
            errors.append(f"missing top-level field: {field}")

    if errors:
        return errors

    if trip["schema_version"] != "1.0":
        errors.append("schema_version must be '1.0'")
    if not isinstance(trip["trip_title"], str) or not trip["trip_title"].strip():
        errors.append("trip_title must be a non-empty string")
    if not _is_date(trip["start_date"]):
        errors.append("start_date must be YYYY-MM-DD")
    if not _is_date(trip["end_date"]):
        errors.append("end_date must be YYYY-MM-DD")
    if trip["transport"] not in TRANSPORT_VALUES:
        errors.append(f"transport must be one of {sorted(TRANSPORT_VALUES)}")
    if trip["style_theme"] not in THEME_VALUES:
        errors.append(f"style_theme must be one of {sorted(THEME_VALUES)}")
    if trip["lang"] not in LANG_VALUES:
        errors.append(f"lang must be one of {sorted(LANG_VALUES)}")
    if not isinstance(trip["travelers"], list) or not trip["travelers"]:
        errors.append("travelers must be a non-empty array")
    if not isinstance(trip["days"], list) or not trip["days"]:
        errors.append("days must be a non-empty array")

    stop_ids: set[str] = set()
    for day_index, day in enumerate(trip.get("days", []), 1):
        prefix = f"days[{day_index}]"
        if not isinstance(day, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ["day", "date", "stops"]:
            if field not in day:
                errors.append(f"{prefix} missing field: {field}")
        if not isinstance(day.get("day"), int) or day.get("day", 0) < 1:
            errors.append(f"{prefix}.day must be a positive integer")
        if not _is_date(day.get("date")):
            errors.append(f"{prefix}.date must be YYYY-MM-DD")
        if not isinstance(day.get("stops"), list) or not day.get("stops"):
            errors.append(f"{prefix}.stops must be a non-empty array")
            continue
        for stop_index, stop in enumerate(day["stops"], 1):
            stop_prefix = f"{prefix}.stops[{stop_index}]"
            if not isinstance(stop, dict):
                errors.append(f"{stop_prefix} must be an object")
                continue
            for field in STOP_REQUIRED:
                if field not in stop:
                    errors.append(f"{stop_prefix} missing field: {field}")
            stop_id = stop.get("id")
            if isinstance(stop_id, str):
                if stop_id in stop_ids:
                    errors.append(f"{stop_prefix}.id duplicates '{stop_id}'")
                stop_ids.add(stop_id)
                if not re.match(r"^[a-z0-9][a-z0-9_-]*$", stop_id):
                    errors.append(f"{stop_prefix}.id must be slug-like")
            else:
                errors.append(f"{stop_prefix}.id must be a string")

            _validate_stop_values(stop, stop_prefix, errors)

    return errors


def _validate_stop_values(stop: dict[str, Any], prefix: str, errors: list[str]) -> None:
    for field in ["name", "city", "country", "notes", "source"]:
        if not isinstance(stop.get(field), str) or not stop.get(field, "").strip():
            errors.append(f"{prefix}.{field} must be a non-empty string")

    lat = stop.get("lat")
    lon = stop.get("lon")
    if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
        errors.append(f"{prefix}.lat must be a number in [-90, 90]")
    if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
        errors.append(f"{prefix}.lon must be a number in [-180, 180]")
    if stop.get("crs") not in CRS_VALUES:
        errors.append(f"{prefix}.crs must be one of {sorted(CRS_VALUES)}")
    if stop.get("category") not in CATEGORY_VALUES:
        errors.append(f"{prefix}.category must be one of {sorted(CATEGORY_VALUES)}")
    if not isinstance(stop.get("duration_min"), int) or stop["duration_min"] < 0:
        errors.append(f"{prefix}.duration_min must be a non-negative integer")
    if not isinstance(stop.get("info_missing"), bool):
        errors.append(f"{prefix}.info_missing must be boolean")
    if stop.get("info_missing") and stop.get("source") != "info_missing":
        errors.append(f"{prefix}.source should be 'info_missing' when info_missing=true")
    if not stop.get("info_missing") and not stop.get("source"):
        errors.append(f"{prefix} must include a source or mark info_missing=true")


def check_artifact(html_path: Path, max_bytes: int = 2_000_000) -> list[str]:
    """Check that an HTML artifact is self-contained enough for phase 1."""

    errors: list[str] = []
    if not html_path.exists():
        return [f"missing artifact: {html_path}"]

    size = html_path.stat().st_size
    if size > max_bytes:
        errors.append(f"artifact is {size} bytes, expected <= {max_bytes}")

    html = html_path.read_text(encoding="utf-8")
    forbidden_patterns = {
        r"<script[^>]+src=": "external script tag",
        r"<link[^>]+rel=[\"']?stylesheet": "external stylesheet link",
        r"\bfetch\s*\(": "fetch call",
        r"\bXMLHttpRequest\b": "XMLHttpRequest usage",
        r"\bimport\s*\(": "dynamic import",
    }
    for pattern, label in forbidden_patterns.items():
        if re.search(pattern, html, flags=re.IGNORECASE):
            errors.append(f"artifact contains forbidden {label}")

    required_snippets = [
        'id="trip-data"',
        'id="pixel-map"',
        'id="itinerary-list"',
        'id="poi-card"',
        'id="download-html"',
        'id="download-overview-poster"',
        'id="download-day-poster"',
        'id="download-record-poster"',
        'id="trip-note"',
        'id="day-note"',
        'id="stop-note"',
        'name="viewport"',
        "data-stop-index",
    ]
    for snippet in required_snippets:
        if snippet not in html:
            errors.append(f"artifact missing required snippet: {snippet}")

    return errors


def check_builder_artifact(html_path: Path, max_bytes: int = 2_500_000) -> list[str]:
    """Check that the browser builder is static and has the expected controls."""

    errors: list[str] = []
    if not html_path.exists():
        return [f"missing artifact: {html_path}"]

    size = html_path.stat().st_size
    if size > max_bytes:
        errors.append(f"artifact is {size} bytes, expected <= {max_bytes}")

    html = html_path.read_text(encoding="utf-8")
    forbidden_patterns = {
        r"<script[^>]+src=": "external script tag",
        r"<link[^>]+rel=[\"']?stylesheet": "external stylesheet link",
        r"\bfetch\s*\(": "fetch call",
        r"\bXMLHttpRequest\b": "XMLHttpRequest usage",
        r"\bimport\s*\(": "dynamic import",
        r"@import": "CSS import",
        r"\burl\([\"']?https?://": "remote CSS url",
    }
    for pattern, label in forbidden_patterns.items():
        if re.search(pattern, html, flags=re.IGNORECASE):
            errors.append(f"builder contains forbidden {label}")

    required_snippets = [
        'id="docx-input"',
        'id="builder-data-input"',
        'id="parse-input"',
        'id="draft-table"',
        'id="build-preview"',
        'id="map-preview"',
        'id="download-json"',
        'id="download-map-html"',
        'id="download-overview-poster"',
        'id="download-day-poster"',
        'id="download-record-poster"',
        "DecompressionStream",
        "word/document.xml",
        "lat",
        "lon",
    ]
    for snippet in required_snippets:
        if snippet not in html:
            errors.append(f"builder missing required snippet: {snippet}")

    return errors


def check_svg_artifact(svg_path: Path, max_bytes: int = 2_000_000) -> list[str]:
    """Check that a poster SVG is offline and contains the expected sections."""

    errors: list[str] = []
    if not svg_path.exists():
        return [f"missing artifact: {svg_path}"]

    size = svg_path.stat().st_size
    if size > max_bytes:
        errors.append(f"artifact is {size} bytes, expected <= {max_bytes}")

    svg = svg_path.read_text(encoding="utf-8")
    forbidden_patterns = {
        r"<script\b": "script tag",
        r"\bhref=[\"']https?://": "remote href",
        r"\bxlink:href=[\"']https?://": "remote xlink href",
        r"@import": "CSS import",
        r"\burl\([\"']?https?://": "remote CSS url",
        r"\bfetch\s*\(": "fetch call",
        r"\bXMLHttpRequest\b": "XMLHttpRequest usage",
    }
    for pattern, label in forbidden_patterns.items():
        if re.search(pattern, svg, flags=re.IGNORECASE):
            errors.append(f"artifact contains forbidden {label}")

    required_snippets = [
        'id="pixel-travel-poster"',
        "PixelTravelMap",
        "完整行程",
        "atlas-grid",
        "scale-bar",
        "poster-day",
        "route-arrow",
    ]
    for snippet in required_snippets:
        if snippet not in svg:
            errors.append(f"artifact missing required snippet: {snippet}")

    return errors
