"""Render itinerary JSON into offline PixelTravelMap artifacts."""

from __future__ import annotations

import html
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAP_W = 1040
MAP_H = 620
POSTER_W = 1600
POSTER_H = 1130
GRID = 8


@dataclass(frozen=True)
class MapView:
    key: str
    label: str
    stops: list[dict[str, Any]]
    context_stops: list[dict[str, Any]]
    points: dict[str, tuple[int, int]]
    scale_km: int
    scale_px: int


def flatten_stops(trip: dict[str, Any]) -> list[dict[str, Any]]:
    stops: list[dict[str, Any]] = []
    ordinal = 1
    for day in trip["days"]:
        for stop in day["stops"]:
            item = dict(stop)
            item["day"] = day["day"]
            item["date"] = day["date"]
            item["day_summary"] = day.get("summary", "")
            item["ordinal"] = ordinal
            stops.append(item)
            ordinal += 1
    return stops


def haversine_km(a: dict[str, Any], b: dict[str, Any]) -> float:
    radius = 6371.0
    lat1, lon1 = math.radians(a["lat"]), math.radians(a["lon"])
    lat2, lon2 = math.radians(b["lat"]), math.radians(b["lon"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(h))


def total_route_km(stops: list[dict[str, Any]]) -> int:
    if len(stops) < 2:
        return 0
    return round(sum(haversine_km(a, b) for a, b in zip(stops, stops[1:])))


def _route_segments(stops: list[dict[str, Any]]) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    for start, end in zip(stops, stops[1:]):
        segments.append(
            {
                "start": start,
                "end": end,
                "distance_km": max(1, round(haversine_km(start, end))),
            }
        )
    return segments


def _nice_scale(max_km: float) -> int:
    if max_km <= 5:
        return 1
    for candidate in [2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]:
        if candidate <= max_km:
            scale = candidate
        else:
            break
    return scale


def _projection(
    stops: list[dict[str, Any]],
    width: int = MAP_W,
    height: int = MAP_H,
    padding: int = 72,
) -> tuple[dict[str, tuple[int, int]], int, int]:
    lats = [stop["lat"] for stop in stops]
    lons = [stop["lon"] for stop in stops]
    mean_lat = sum(lats) / len(lats)
    cos_lat = max(math.cos(math.radians(mean_lat)), 0.18)
    xs = [lon * cos_lat for lon in lons]
    ys = lats
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    x_span = max(max_x - min_x, 0.08)
    y_span = max(max_y - min_y, 0.08)

    draw_w = width - padding * 2
    draw_h = height - padding * 2
    fit = min(draw_w / x_span, draw_h / y_span)
    used_w = x_span * fit
    used_h = y_span * fit
    left = (width - used_w) / 2
    top = (height - used_h) / 2

    points: dict[str, tuple[int, int]] = {}
    occupied: dict[tuple[int, int], int] = {}
    for stop, x_value, y_value in zip(stops, xs, ys):
        raw_x = left + (x_value - min_x) * fit
        raw_y = top + (max_y - y_value) * fit
        x = int(round(raw_x / GRID) * GRID)
        y = int(round(raw_y / GRID) * GRID)
        key = (x, y)
        hit = occupied.get(key, 0)
        occupied[key] = hit + 1
        if hit:
            x += ((hit % 3) - 1) * 26
            y += (hit // 3 + 1) * 22
        x = min(max(x, 44), width - 44)
        y = min(max(y, 44), height - 44)
        points[stop["id"]] = (x, y)

    km_per_lon_degree = 111.32 * cos_lat
    km_per_px = x_span * km_per_lon_degree / max(used_w, 1)
    target_px = min(180, max(90, int(draw_w * 0.18)))
    scale_km = _nice_scale(km_per_px * target_px)
    scale_px = max(56, int(round(scale_km / max(km_per_px, 0.001))))
    return points, scale_km, scale_px


def _context_for_city(stops: list[dict[str, Any]], city: str) -> list[dict[str, Any]]:
    indices = [index for index, stop in enumerate(stops) if stop["city"] == city]
    selected: dict[str, dict[str, Any]] = {}
    for index in indices:
        for neighbor in [index - 1, index, index + 1]:
            if 0 <= neighbor < len(stops):
                selected[stops[neighbor]["id"]] = stops[neighbor]
    return list(selected.values())


def build_map_views(stops: list[dict[str, Any]]) -> list[MapView]:
    overview_points, overview_scale_km, overview_scale_px = _projection(stops)
    views = [
        MapView(
            key="overview",
            label="总览地图",
            stops=stops,
            context_stops=stops,
            points=overview_points,
            scale_km=overview_scale_km,
            scale_px=overview_scale_px,
        )
    ]
    for city in sorted({stop["city"] for stop in stops}):
        city_stops = [stop for stop in stops if stop["city"] == city]
        context_stops = _context_for_city(stops, city)
        projected_stops = city_stops if len(city_stops) > 1 else context_stops
        points, scale_km, scale_px = _projection(projected_stops)
        views.append(
            MapView(
                key=city,
                label=f"{city} detail view",
                stops=city_stops,
                context_stops=context_stops,
                points=points,
                scale_km=scale_km,
                scale_px=scale_px,
            )
        )
    return views


def render_trip_html(trip: dict[str, Any]) -> str:
    stops = flatten_stops(trip)
    views = build_map_views(stops)
    cities = [view.key for view in views[1:]]
    route_km = total_route_km(stops)
    stats = {
        "days": len(trip["days"]),
        "cities": len(cities),
        "stops": len(stops),
        "route_km": route_km,
        "budget_cny": trip.get("budget_cny"),
    }

    trip_json = json.dumps(trip, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )

    return f"""<!doctype html>
<html lang="{html.escape(trip.get("lang", "zh-CN"))}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(trip["trip_title"])} | PixelTravelMap</title>
  <style>
{_css()}
  </style>
</head>
<body>
  <script id="trip-data" type="application/json">{trip_json}</script>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">PixelTravelMap Atlas</p>
        <h1>{html.escape(trip["trip_title"])}</h1>
        <p class="atlas-note">方位和距离基于 POI 经纬度计算，路线距离为直线近似值，不等同于实际驾车或步行距离。</p>
      </div>
      <div class="toolbar">
        <button class="icon-button" id="overview-button" type="button" title="返回总览" aria-label="返回总览">↩</button>
        <button class="text-button" id="download-html" type="button">保存 HTML</button>
      </div>
    </header>

    <main class="workspace">
      <section class="map-stage" aria-label="经纬度旅行地图">
        <div class="map-toolbar">
          <span id="view-label">总览地图</span>
          <div class="city-pills" aria-label="城市 detail view">
            {_render_city_buttons(cities)}
          </div>
        </div>
        {_render_map_svg(views)}
        <div class="stats-bar">
          {_render_stats(stats)}
        </div>
      </section>

      <aside class="side-panel">
        <section class="panel-section">
          <h2>完整行程</h2>
          <div id="itinerary-list" class="itinerary-list">
            {_render_itinerary(trip)}
          </div>
        </section>
        <section class="panel-section">
          <h2>地标详情</h2>
          <article id="poi-card" class="poi-card" aria-live="polite">
            <p class="empty-state">点击地图编号或日程项查看详情。</p>
          </article>
        </section>
      </aside>
    </main>
  </div>
  <script>
{_js()}
  </script>
</body>
</html>
"""


def write_trip_html(trip: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_trip_html(trip), encoding="utf-8", newline="\n")


def render_trip_poster_svg(trip: dict[str, Any]) -> str:
    stops = flatten_stops(trip)
    overview = build_map_views(stops)[0]
    title = _trim(trip["trip_title"], 32)
    date_range = f"{trip['start_date']} - {trip['end_date']}"
    route_km = total_route_km(stops)
    cities = sorted({stop["city"] for stop in stops})
    stats = f"{len(trip['days'])} days · {len(cities)} cities · {len(stops)} stops · {route_km} km straight-line route"

    map_svg = _render_static_map_view(
        overview,
        all_stops=stops,
        width=1320,
        height=560,
        x=140,
        y=150,
        include_interactions=False,
    )
    itinerary = _render_poster_itinerary(trip, x=120, y=790, width=1360)

    return f"""<svg id="pixel-travel-poster" xmlns="http://www.w3.org/2000/svg" width="{POSTER_W}" height="{POSTER_H}" viewBox="0 0 {POSTER_W} {POSTER_H}" role="img" aria-label="{html.escape(title)} poster">
  <defs>
    <pattern id="atlas-grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(49,61,76,0.12)" stroke-width="1"/>
    </pattern>
    <marker id="route-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" class="arrow-head"/>
    </marker>
  </defs>
  <style>{_poster_css()}</style>
  <rect width="{POSTER_W}" height="{POSTER_H}" class="poster-bg"/>
  <rect x="64" y="56" width="1472" height="1018" class="poster-frame"/>
  <text x="120" y="112" class="poster-kicker">PixelTravelMap · offline atlas poster</text>
  <text x="120" y="154" class="poster-title">{html.escape(title)}</text>
  <text x="120" y="194" class="poster-meta">{html.escape(date_range)} · {html.escape(stats)}</text>
  {map_svg}
  <text x="120" y="752" class="section-title">完整行程</text>
  <text x="1460" y="752" class="distance-note" text-anchor="end">距离为经纬度直线近似值</text>
  {itinerary}
</svg>
"""


def write_trip_poster_svg(trip: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_trip_poster_svg(trip), encoding="utf-8", newline="\n")


def _render_city_buttons(cities: list[str]) -> str:
    buttons = ['<button class="city-pill active" type="button" data-view="overview">总览</button>']
    for city in cities:
        safe_city = html.escape(city)
        buttons.append(
            f'<button class="city-pill" type="button" data-view="{safe_city}">{safe_city}</button>'
        )
    return "\n".join(buttons)


def _render_map_svg(views: list[MapView]) -> str:
    groups = []
    stops = views[0].stops
    for view in views:
        groups.append(_render_static_map_view(view, all_stops=stops, include_interactions=True))
    return f"""
        <svg id="pixel-map" class="pixel-map" viewBox="0 0 {MAP_W} {MAP_H}" role="img" aria-label="Latitude longitude travel atlas">
          <defs>
            <pattern id="atlas-grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(49,61,76,0.12)" stroke-width="1"/>
            </pattern>
            <marker id="route-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" class="arrow-head"/>
            </marker>
          </defs>
          {"".join(groups)}
        </svg>
"""


def _render_static_map_view(
    view: MapView,
    all_stops: list[dict[str, Any]],
    width: int = MAP_W,
    height: int = MAP_H,
    x: int = 0,
    y: int = 0,
    include_interactions: bool = True,
) -> str:
    active_ids = {stop["id"] for stop in view.stops}
    context_ids = {stop["id"] for stop in view.context_stops}
    view_stops = [stop for stop in all_stops if stop["id"] in context_ids and stop["id"] in view.points]
    route_points = " ".join(
        f"{view.points[stop['id']][0]},{view.points[stop['id']][1]}" for stop in view_stops
    )
    display = "" if view.key == "overview" else ' style="display:none"'
    interaction_attrs = f' class="map-view" data-view="{html.escape(view.key)}"{display}' if include_interactions else ' class="poster-map-view"'

    segments = []
    for segment in _route_segments(view_stops):
        start = segment["start"]
        end = segment["end"]
        if start["id"] not in view.points or end["id"] not in view.points:
            continue
        x1, y1 = view.points[start["id"]]
        x2, y2 = view.points[end["id"]]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        segments.append(
            f'<text class="distance-label" x="{mx:.0f}" y="{my - 10:.0f}" text-anchor="middle">{segment["distance_km"]} km</text>'
        )

    city_labels = []
    city_groups: dict[str, list[dict[str, Any]]] = {}
    for stop in view_stops:
        city_groups.setdefault(stop["city"], []).append(stop)
    for city, city_stops in city_groups.items():
        xs = [view.points[stop["id"]][0] for stop in city_stops]
        ys = [view.points[stop["id"]][1] for stop in city_stops]
        label = f"{city} · {city_stops[0]['country']}"
        city_labels.append(
            f'<text class="city-label" x="{sum(xs) / len(xs):.0f}" y="{max(min(ys) - 32, 30):.0f}" text-anchor="middle">{html.escape(label)}</text>'
        )

    markers = []
    for stop in view_stops:
        sx, sy = view.points[stop["id"]]
        dim = " context" if stop["id"] not in active_ids else ""
        data = (
            f' data-stop-index="{stop["ordinal"] - 1}" tabindex="0" role="button"'
            if include_interactions and stop["id"] in active_ids
            else ""
        )
        markers.append(
            f"""
            <g class="marker marker-{html.escape(stop["category"])}{dim}"{data} aria-label="{html.escape(stop["name"])}">
              <circle class="marker-halo" cx="{sx}" cy="{sy}" r="18"/>
              <rect class="marker-box" x="{sx - 15}" y="{sy - 15}" width="30" height="30" rx="2"/>
              <text class="marker-num" x="{sx}" y="{sy + 5}" text-anchor="middle">{stop["ordinal"]}</text>
              <text class="poi-label" x="{sx + 24}" y="{sy - 8}">{html.escape(_trim(stop["name"], 14))}</text>
              <text class="poi-day" x="{sx + 24}" y="{sy + 10}">Day {stop["day"]} · {html.escape(stop["city"])}</text>
            </g>
            """
        )

    return f"""
  <g transform="translate({x},{y})">
    <g{interaction_attrs}>
      <rect width="{width}" height="{height}" class="atlas-water"/>
      <rect width="{width}" height="{height}" fill="url(#atlas-grid)"/>
      <rect x="28" y="28" width="{width - 56}" height="{height - 56}" class="atlas-frame-inner"/>
      <text x="48" y="56" class="map-title">{html.escape(view.label)}</text>
      <text x="{width - 48}" y="56" class="north" text-anchor="end">N ↑</text>
      <polyline class="route" points="{route_points}" marker-mid="url(#route-arrow)" marker-end="url(#route-arrow)"/>
      {"".join(segments)}
      {"".join(city_labels)}
      <g class="marker-layer" data-view="{html.escape(view.key)}">
        {"".join(markers)}
      </g>
      {_render_scale_bar(view, width, height)}
    </g>
  </g>
"""


def _render_scale_bar(view: MapView, width: int, height: int) -> str:
    x = 48
    y = height - 48
    scale_px = min(view.scale_px, width - 160)
    return f"""
      <g class="scale-bar">
        <line x1="{x}" y1="{y}" x2="{x + scale_px}" y2="{y}" />
        <line x1="{x}" y1="{y - 8}" x2="{x}" y2="{y + 8}" />
        <line x1="{x + scale_px}" y1="{y - 8}" x2="{x + scale_px}" y2="{y + 8}" />
        <text x="{x + scale_px / 2:.0f}" y="{y - 14:.0f}" text-anchor="middle">≈ {view.scale_km} km</text>
      </g>
"""


def _render_itinerary(trip: dict[str, Any]) -> str:
    chunks: list[str] = []
    index = 0
    for day in trip["days"]:
        chunks.append(
            f'<div class="day-block"><h3>Day {day["day"]} <span>{html.escape(day["date"])}</span></h3>'
        )
        if day.get("summary"):
            chunks.append(f'<p class="day-summary">{html.escape(day["summary"])}</p>')
        for stop in day["stops"]:
            chunks.append(
                f"""
                <button class="schedule-item" type="button" data-stop-index="{index}" data-city="{html.escape(stop["city"])}">
                  <span class="schedule-index">{index + 1}</span>
                  <span>
                    <strong>{html.escape(stop["name"])}</strong>
                    <small>{html.escape(stop["city"])} · Day {day["day"]} · {stop["duration_min"]} min</small>
                  </span>
                </button>
                """
            )
            index += 1
        chunks.append("</div>")
    return "\n".join(chunks)


def _render_poster_itinerary(trip: dict[str, Any], x: int, y: int, width: int) -> str:
    rows = []
    row_h = min(58, max(42, int(310 / max(len(trip["days"]), 1))))
    for offset, day in enumerate(trip["days"]):
        row_y = y + offset * row_h
        title_y = 18 if row_h < 50 else 24
        stops_y = row_h - 8 if row_h < 50 else row_h - 18
        stop_text = " · ".join(
            f"{stop['name']} ({stop['city']}, {stop['duration_min']}m)" for stop in day["stops"]
        )
        summary = _trim(day.get("summary", ""), 28)
        stops = _trim(stop_text, 78)
        rows.append(
            f"""
  <g class="poster-day" transform="translate({x},{row_y})">
    <rect width="{width}" height="{row_h - 8}" rx="4"/>
    <text x="20" y="{title_y}" class="poster-day-num">Day {day["day"]}</text>
    <text x="112" y="{title_y}" class="poster-day-title">{html.escape(day["date"])} · {html.escape(summary)}</text>
    <text x="112" y="{stops_y}" class="poster-day-stops">{html.escape(stops)}</text>
  </g>
"""
        )
    return "".join(rows)


def _render_stats(stats: dict[str, Any]) -> str:
    budget = stats["budget_cny"]
    budget_label = "未填写预算" if budget is None else f"¥{budget:,}"
    items = [
        ("天数", f"{stats['days']}"),
        ("城市", f"{stats['cities']}"),
        ("地点", f"{stats['stops']}"),
        ("直线路线", f"{stats['route_km']} km"),
        ("预算", budget_label),
    ]
    return "\n".join(
        f'<div class="stat-item"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></div>'
        for label, value in items
    )


def _trim(value: Any, limit: int) -> str:
    text = str(value or "")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _css() -> str:
    return """
    :root {
      --paper: #f6ecd9;
      --paper-2: #fffaf0;
      --ink: #26313d;
      --muted: #697386;
      --water: #d9edf0;
      --grid: rgba(38,49,61,0.12);
      --route: #d64f3f;
      --route-soft: #f2a35f;
      --marker: #1f7a8c;
      --marker-2: #f5c542;
      --panel: #fffdf7;
      --line: #313d4c;
      --focus: #7a3e9d;
      --shadow: rgba(38, 49, 61, 0.22);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(38,49,61,0.04) 1px, transparent 1px),
        linear-gradient(rgba(38,49,61,0.04) 1px, transparent 1px),
        var(--paper);
      background-size: 18px 18px;
      font-family: "Courier New", ui-monospace, monospace;
      letter-spacing: 0;
    }
    button, a { font: inherit; }
    .app-shell { width: min(1480px, 100%); margin: 0 auto; padding: 18px; }
    .topbar {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      padding: 10px 0 18px;
    }
    .eyebrow {
      margin: 0 0 4px;
      color: var(--focus);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }
    h1, h2, h3, p { margin-top: 0; }
    h1 { margin-bottom: 6px; font-size: clamp(24px, 4vw, 40px); line-height: 1.1; }
    h2 { margin-bottom: 12px; font-size: 18px; }
    h3 { margin-bottom: 6px; font-size: 15px; }
    h3 span { color: var(--muted); font-size: 12px; font-weight: 400; }
    .atlas-note { max-width: 760px; margin-bottom: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
    .toolbar { display: flex; gap: 8px; align-items: center; }
    .icon-button, .text-button, .city-pill {
      border: 2px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      cursor: pointer;
      box-shadow: 3px 3px 0 var(--line);
    }
    .icon-button { width: 42px; height: 38px; font-size: 20px; }
    .text-button { min-height: 38px; padding: 0 14px; font-weight: 700; }
    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 380px;
      gap: 18px;
      align-items: start;
    }
    .map-stage, .side-panel {
      border: 3px solid var(--line);
      background: var(--paper-2);
      box-shadow: 6px 6px 0 var(--shadow);
    }
    .map-stage { min-width: 0; overflow: hidden; }
    .map-toolbar {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      padding: 12px;
      border-bottom: 3px solid var(--line);
      background: #ebd78f;
      font-weight: 700;
    }
    .city-pills { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; }
    .city-pill {
      min-height: 30px;
      padding: 0 10px;
      box-shadow: 2px 2px 0 var(--line);
      font-size: 12px;
    }
    .city-pill.active { background: var(--ink); color: var(--paper-2); }
    .pixel-map {
      display: block;
      width: 100%;
      height: auto;
      max-height: calc(100vh - 230px);
      min-height: 400px;
      shape-rendering: geometricPrecision;
    }
    .atlas-water { fill: var(--water); }
    .atlas-frame-inner { fill: rgba(255,255,255,0.24); stroke: var(--line); stroke-width: 2; }
    .map-title { fill: var(--ink); font-size: 18px; font-weight: 700; }
    .north { fill: var(--line); font-size: 18px; font-weight: 700; }
    .route {
      fill: none;
      stroke: var(--route);
      stroke-width: 4;
      stroke-linejoin: round;
      stroke-linecap: round;
      stroke-dasharray: 12 7;
    }
    .arrow-head { fill: var(--route); }
    .distance-label {
      paint-order: stroke;
      stroke: var(--paper-2);
      stroke-width: 5;
      fill: var(--line);
      font-size: 13px;
      font-weight: 700;
    }
    .city-label {
      paint-order: stroke;
      stroke: var(--paper-2);
      stroke-width: 6;
      fill: var(--focus);
      font-size: 17px;
      font-weight: 700;
    }
    .marker { cursor: pointer; outline: none; }
    .marker.context { opacity: 0.45; }
    .marker-halo { fill: rgba(31, 122, 140, 0.14); }
    .marker-box { fill: var(--marker); stroke: var(--line); stroke-width: 2; }
    .marker-num { fill: #fffaf0; font-size: 16px; font-weight: 700; pointer-events: none; }
    .poi-label {
      paint-order: stroke;
      stroke: var(--paper-2);
      stroke-width: 5;
      fill: var(--ink);
      font-size: 15px;
      font-weight: 700;
    }
    .poi-day {
      paint-order: stroke;
      stroke: var(--paper-2);
      stroke-width: 4;
      fill: var(--muted);
      font-size: 11px;
      font-weight: 700;
    }
    .marker.active .marker-box,
    .marker:focus .marker-box { fill: var(--marker-2); }
    .marker.active .marker-num,
    .marker:focus .marker-num { fill: var(--ink); }
    .scale-bar line { stroke: var(--line); stroke-width: 3; }
    .scale-bar text { fill: var(--line); font-size: 13px; font-weight: 700; }
    .stats-bar {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      border-top: 3px solid var(--line);
      background: var(--panel);
    }
    .stat-item { padding: 10px; border-right: 2px solid var(--line); }
    .stat-item:last-child { border-right: 0; }
    .stat-item span { display: block; color: var(--muted); font-size: 11px; }
    .stat-item strong { display: block; margin-top: 4px; font-size: 15px; }
    .side-panel { display: grid; gap: 0; }
    .panel-section { padding: 14px; border-bottom: 3px solid var(--line); }
    .panel-section:last-child { border-bottom: 0; }
    .itinerary-list { display: grid; gap: 12px; max-height: 46vh; overflow: auto; padding-right: 4px; }
    .day-block { border-left: 4px solid var(--focus); padding-left: 10px; }
    .day-summary { margin-bottom: 8px; color: var(--muted); font-size: 12px; }
    .schedule-item {
      width: 100%;
      display: grid;
      grid-template-columns: 28px 1fr;
      gap: 8px;
      align-items: start;
      margin: 6px 0;
      padding: 8px;
      border: 2px solid var(--line);
      background: #fff;
      color: var(--ink);
      text-align: left;
      cursor: pointer;
    }
    .schedule-item.active { background: #e9f6f9; border-color: var(--focus); }
    .schedule-item.focus-city:not(.in-city) { opacity: 0.45; }
    .schedule-index {
      display: grid;
      place-items: center;
      width: 24px;
      height: 24px;
      background: var(--marker);
      color: #fff;
      border: 2px solid var(--line);
      font-weight: 700;
    }
    .schedule-item small { display: block; margin-top: 2px; color: var(--muted); }
    .poi-card { min-height: 190px; }
    .poi-card h3 { margin-bottom: 8px; font-size: 20px; }
    .poi-meta { color: var(--muted); font-size: 12px; }
    .poi-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .poi-actions a {
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      padding: 0 10px;
      border: 2px solid var(--line);
      background: var(--paper);
      color: var(--ink);
      text-decoration: none;
      box-shadow: 2px 2px 0 var(--line);
    }
    .source-note {
      margin-top: 12px;
      padding: 8px;
      background: #f4f0ff;
      border: 2px dashed var(--line);
      font-size: 12px;
    }
    .empty-state { color: var(--muted); }
    @media (max-width: 980px) {
      .app-shell { padding: 12px; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .workspace { grid-template-columns: 1fr; }
      .pixel-map { min-height: 320px; max-height: none; }
      .side-panel { grid-template-columns: 1fr; }
      .itinerary-list { max-height: none; }
      .stats-bar { grid-template-columns: repeat(2, 1fr); }
      .stat-item { border-bottom: 2px solid var(--line); }
      .map-toolbar { align-items: flex-start; flex-direction: column; }
      .city-pills { justify-content: flex-start; }
    }
    @media (max-width: 560px) {
      .toolbar { width: 100%; }
      .text-button { flex: 1; }
      .stats-bar { grid-template-columns: 1fr; }
      .stat-item { border-right: 0; }
    }
"""


def _poster_css() -> str:
    return """
    .poster-bg { fill: #f6ecd9; }
    .poster-frame { fill: #fffaf0; stroke: #313d4c; stroke-width: 4; }
    .poster-kicker { fill: #7a3e9d; font: 700 22px "Courier New", monospace; }
    .poster-title { fill: #26313d; font: 700 42px "Courier New", monospace; }
    .poster-meta { fill: #697386; font: 700 20px "Courier New", monospace; }
    .section-title { fill: #26313d; font: 700 28px "Courier New", monospace; }
    .distance-note { fill: #697386; font: 700 16px "Courier New", monospace; }
    .atlas-water { fill: #d9edf0; }
    .atlas-frame-inner { fill: rgba(255,255,255,0.25); stroke: #313d4c; stroke-width: 2; }
    .map-title, .north { fill: #26313d; font: 700 18px "Courier New", monospace; }
    .route { fill: none; stroke: #d64f3f; stroke-width: 4; stroke-linejoin: round; stroke-linecap: round; stroke-dasharray: 12 7; }
    .arrow-head { fill: #d64f3f; }
    .distance-label { paint-order: stroke; stroke: #fffaf0; stroke-width: 5; fill: #313d4c; font: 700 13px "Courier New", monospace; }
    .city-label { paint-order: stroke; stroke: #fffaf0; stroke-width: 6; fill: #7a3e9d; font: 700 17px "Courier New", monospace; }
    .marker-halo { fill: rgba(31,122,140,0.14); }
    .marker-box { fill: #1f7a8c; stroke: #313d4c; stroke-width: 2; }
    .marker-num { fill: #fffaf0; font: 700 16px "Courier New", monospace; }
    .poi-label { paint-order: stroke; stroke: #fffaf0; stroke-width: 5; fill: #26313d; font: 700 15px "Courier New", monospace; }
    .poi-day { paint-order: stroke; stroke: #fffaf0; stroke-width: 4; fill: #697386; font: 700 11px "Courier New", monospace; }
    .scale-bar line { stroke: #313d4c; stroke-width: 3; }
    .scale-bar text { fill: #313d4c; font: 700 13px "Courier New", monospace; }
    .poster-day rect { fill: #ffffff; stroke: #313d4c; stroke-width: 2; }
    .poster-day-num { fill: #1f7a8c; font: 700 20px "Courier New", monospace; }
    .poster-day-title { fill: #26313d; font: 700 18px "Courier New", monospace; }
    .poster-day-stops { fill: #697386; font: 700 16px "Courier New", monospace; }
"""


def _js() -> str:
    return r"""
    const trip = JSON.parse(document.getElementById("trip-data").textContent);
    const stops = trip.days.flatMap(day => day.stops.map(stop => ({
      ...stop,
      day: day.day,
      date: day.date,
      day_summary: day.summary || ""
    })));
    const card = document.getElementById("poi-card");
    const viewLabel = document.getElementById("view-label");
    const mapViews = Array.from(document.querySelectorAll(".map-view"));
    const scheduleItems = Array.from(document.querySelectorAll(".schedule-item"));
    const cityButtons = Array.from(document.querySelectorAll(".city-pill"));

    function esc(value) {
      return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }[ch]));
    }

    function markers() {
      return Array.from(document.querySelectorAll(".marker[data-stop-index]"));
    }

    function mapsUrl(stop) {
      if (stop.navigation_url) return stop.navigation_url;
      return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(stop.lat + "," + stop.lon)}`;
    }

    function linkHtml(url, label) {
      if (!url) return "";
      return `<a href="${esc(url)}" target="_blank" rel="noreferrer">${esc(label)}</a>`;
    }

    function showCard(index) {
      const stop = stops[index];
      markers().forEach(marker => marker.classList.toggle("active", Number(marker.dataset.stopIndex) === index));
      scheduleItems.forEach(item => item.classList.toggle("active", Number(item.dataset.stopIndex) === index));
      const missing = stop.info_missing ? "信息暂缺，建议实地查证。" : esc(stop.description || "暂无补充描述。");
      const source = stop.info_missing ? "信息暂缺" : esc(stop.source);
      card.innerHTML = `
        <p class="poi-meta">Day ${esc(stop.day)} · ${esc(stop.city)} · ${esc(stop.category)} · ${esc(stop.duration_min)} min · ${esc(stop.lat)}, ${esc(stop.lon)}</p>
        <h3>${esc(stop.name)}</h3>
        <p>${missing}</p>
        <p><strong>备注：</strong>${esc(stop.notes)}</p>
        <div class="poi-actions">
          ${linkHtml(stop.source_url, "来源")}
          ${linkHtml(stop.official_url, "官网")}
          ${linkHtml(mapsUrl(stop), "导航")}
        </div>
        <div class="source-note">来源：${source}。地图方位与距离由 POI 经纬度计算；营业时间、票价和预约信息请以官网为准。</div>
      `;
    }

    function bindMarkers() {
      markers().forEach(marker => {
        if (marker.dataset.bound === "true") return;
        marker.dataset.bound = "true";
        marker.addEventListener("click", () => showCard(Number(marker.dataset.stopIndex)));
        marker.addEventListener("keydown", event => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            showCard(Number(marker.dataset.stopIndex));
          }
        });
      });
    }

    function showView(view) {
      const isOverview = view === "overview";
      mapViews.forEach(group => {
        group.style.display = group.dataset.view === view ? "block" : "none";
      });
      viewLabel.textContent = isOverview ? "总览地图" : `${view} detail view`;
      cityButtons.forEach(button => button.classList.toggle("active", button.dataset.view === view));
      scheduleItems.forEach(item => {
        item.classList.toggle("focus-city", !isOverview);
        item.classList.toggle("in-city", !isOverview && item.dataset.city === view);
      });
      if (!isOverview) {
        const first = scheduleItems.find(item => item.dataset.city === view);
        if (first) showCard(Number(first.dataset.stopIndex));
      }
      bindMarkers();
    }

    scheduleItems.forEach(item => {
      item.addEventListener("click", () => {
        showView(item.dataset.city);
        showCard(Number(item.dataset.stopIndex));
      });
    });
    cityButtons.forEach(button => {
      button.addEventListener("click", () => showView(button.dataset.view));
    });
    document.getElementById("overview-button").addEventListener("click", () => showView("overview"));
    document.getElementById("download-html").addEventListener("click", () => {
      const html = "<!doctype html>\n" + document.documentElement.outerHTML;
      const blob = new Blob([html], { type: "text/html;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `${trip.trip_title || "pixel-travel-map"}.html`;
      document.body.appendChild(a);
      a.click();
      URL.revokeObjectURL(a.href);
      a.remove();
    });
    bindMarkers();
    if (stops.length) showCard(0);
"""
