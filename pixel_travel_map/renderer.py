"""Render itinerary JSON into a self-contained pixel travel map HTML file."""

from __future__ import annotations

import html
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


MAP_W = 920
MAP_H = 540
PADDING = 72
GRID = 8


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


def project_points(stops: list[dict[str, Any]]) -> dict[str, tuple[int, int]]:
    min_lon = min(stop["lon"] for stop in stops)
    max_lon = max(stop["lon"] for stop in stops)
    min_lat = min(stop["lat"] for stop in stops)
    max_lat = max(stop["lat"] for stop in stops)
    lon_span = max(max_lon - min_lon, 0.2)
    lat_span = max(max_lat - min_lat, 0.2)

    points: dict[str, tuple[int, int]] = {}
    collisions: dict[tuple[int, int], int] = defaultdict(int)
    for stop in stops:
        raw_x = PADDING + ((stop["lon"] - min_lon) / lon_span) * (MAP_W - PADDING * 2)
        raw_y = PADDING + ((max_lat - stop["lat"]) / lat_span) * (MAP_H - PADDING * 2)
        x = int(round(raw_x / GRID) * GRID)
        y = int(round(raw_y / GRID) * GRID)
        hit = collisions[(x, y)]
        collisions[(x, y)] += 1
        if hit:
            x += ((hit % 3) - 1) * 18
            y += (hit // 3 + 1) * 18
        x = min(max(x, 32), MAP_W - 32)
        y = min(max(y, 32), MAP_H - 32)
        points[stop["id"]] = (x, y)
    return points


def render_trip_html(trip: dict[str, Any]) -> str:
    stops = flatten_stops(trip)
    points = project_points(stops)
    cities = sorted({stop["city"] for stop in stops})
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
        <p class="eyebrow">PixelTravelMap MVP</p>
        <h1>{html.escape(trip["trip_title"])}</h1>
      </div>
      <div class="toolbar">
        <button class="icon-button" id="overview-button" type="button" title="返回总览" aria-label="返回总览">↩</button>
        <button class="text-button" id="download-html" type="button">保存 HTML</button>
      </div>
    </header>

    <main class="workspace">
      <section class="map-stage" aria-label="像素旅行地图">
        <div class="map-toolbar">
          <span id="view-label">总览地图</span>
          <div class="city-pills" aria-label="城市筛选">
            {_render_city_buttons(cities)}
          </div>
        </div>
        {_render_svg(stops, points)}
        <div class="stats-bar">
          {_render_stats(stats)}
        </div>
      </section>

      <aside class="side-panel">
        <section class="panel-section">
          <h2>日程</h2>
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
    output_path.write_text(render_trip_html(trip), encoding="utf-8")


def _render_city_buttons(cities: list[str]) -> str:
    buttons = ['<button class="city-pill active" type="button" data-city="">总览</button>']
    for city in cities:
        safe_city = html.escape(city)
        buttons.append(
            f'<button class="city-pill" type="button" data-city="{safe_city}">{safe_city}</button>'
        )
    return "\n".join(buttons)


def _render_svg(stops: list[dict[str, Any]], points: dict[str, tuple[int, int]]) -> str:
    route_points = " ".join(f"{points[stop['id']][0]},{points[stop['id']][1]}" for stop in stops)
    city_routes = []
    for city in sorted({stop["city"] for stop in stops}):
        city_stops = [stop for stop in stops if stop["city"] == city]
        if len(city_stops) > 1:
            city_points = " ".join(
                f"{points[stop['id']][0]},{points[stop['id']][1]}" for stop in city_stops
            )
            city_routes.append(
                f'<polyline class="route city-route" data-city="{html.escape(city)}" '
                f'points="{city_points}" />'
            )

    marker_nodes = []
    for index, stop in enumerate(stops):
        x, y = points[stop["id"]]
        marker_nodes.append(
            f"""
            <g class="marker marker-{html.escape(stop["category"])}" data-stop-index="{index}" data-city="{html.escape(stop["city"])}" tabindex="0" role="button" aria-label="{html.escape(stop["name"])}">
              <rect class="marker-shadow" x="{x - 12}" y="{y - 6}" width="30" height="30" />
              <rect class="marker-box" x="{x - 14}" y="{y - 18}" width="28" height="28" />
              <text x="{x}" y="{y + 2}" text-anchor="middle">{stop["ordinal"]}</text>
            </g>
            """
        )

    return f"""
        <svg id="pixel-map" class="pixel-map" viewBox="0 0 {MAP_W} {MAP_H}" role="img" aria-label="Pixel route map">
          <defs>
            <pattern id="pixel-grid" width="16" height="16" patternUnits="userSpaceOnUse">
              <path d="M 16 0 L 0 0 0 16" fill="none" stroke="rgba(58,58,58,0.08)" stroke-width="1"/>
            </pattern>
          </defs>
          <rect width="{MAP_W}" height="{MAP_H}" class="water" />
          <rect width="{MAP_W}" height="{MAP_H}" fill="url(#pixel-grid)" />
          <path class="land land-a" d="M72 362 L160 288 L264 310 L344 218 L520 238 L616 176 L802 214 L850 334 L736 438 L536 426 L418 474 L260 424 Z" />
          <path class="land land-b" d="M106 134 L236 82 L384 118 L466 84 L616 112 L752 78 L854 150 L792 236 L628 218 L520 266 L384 218 L210 232 Z" />
          <path class="mountains" d="M188 318 L226 270 L264 318 M526 250 L562 202 L604 250 M688 224 L726 174 L764 224" />
          <polyline id="route-overview" class="route" points="{route_points}" />
          {"".join(city_routes)}
          <g id="marker-layer">
            {"".join(marker_nodes)}
          </g>
        </svg>
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
                    <small>{html.escape(stop["city"])} · {stop["duration_min"]} min</small>
                  </span>
                </button>
                """
            )
            index += 1
        chunks.append("</div>")
    return "\n".join(chunks)


def _render_stats(stats: dict[str, Any]) -> str:
    budget = stats["budget_cny"]
    budget_label = "未填写预算" if budget is None else f"¥{budget:,}"
    items = [
        ("天数", f"{stats['days']}"),
        ("城市", f"{stats['cities']}"),
        ("地点", f"{stats['stops']}"),
        ("路线", f"{stats['route_km']} km"),
        ("预算", budget_label),
    ]
    return "\n".join(
        f'<div class="stat-item"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></div>'
        for label, value in items
    )


def _css() -> str:
    return """
    :root {
      --paper: #f7ead7;
      --paper-2: #fff8e8;
      --ink: #2f3542;
      --muted: #697386;
      --water: #9fd3e6;
      --land: #b7d88a;
      --land-2: #d6c07a;
      --mountain: #7b6d63;
      --route: #e86f51;
      --marker: #d83f45;
      --marker-2: #ffd166;
      --panel: #fffdf4;
      --line: #3c4250;
      --focus: #1f7a8c;
      --shadow: rgba(47, 53, 66, 0.24);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(47,53,66,0.05) 1px, transparent 1px),
        linear-gradient(rgba(47,53,66,0.05) 1px, transparent 1px),
        var(--paper);
      background-size: 18px 18px;
      font-family: "Courier New", ui-monospace, monospace;
      letter-spacing: 0;
    }
    button, a { font: inherit; }
    .app-shell { width: min(1440px, 100%); margin: 0 auto; padding: 18px; }
    .topbar {
      display: flex;
      align-items: center;
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
    h1 { margin-bottom: 0; font-size: clamp(24px, 4vw, 40px); line-height: 1.1; }
    h2 { margin-bottom: 12px; font-size: 18px; }
    h3 { margin-bottom: 6px; font-size: 15px; }
    h3 span { color: var(--muted); font-size: 12px; font-weight: 400; }
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
      grid-template-columns: minmax(0, 1fr) 360px;
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
      background: #f2d38b;
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
      max-height: calc(100vh - 210px);
      min-height: 360px;
      shape-rendering: crispEdges;
      image-rendering: pixelated;
    }
    .water { fill: var(--water); }
    .land { stroke: var(--line); stroke-width: 3; }
    .land-a { fill: var(--land); }
    .land-b { fill: var(--land-2); opacity: 0.94; }
    .mountains {
      fill: none;
      stroke: var(--mountain);
      stroke-width: 5;
      stroke-linejoin: bevel;
    }
    .route {
      fill: none;
      stroke: var(--route);
      stroke-width: 5;
      stroke-linejoin: bevel;
      stroke-linecap: square;
      stroke-dasharray: 10 8;
    }
    .city-route { display: none; stroke: var(--focus); }
    .marker { cursor: pointer; outline: none; }
    .marker-shadow { fill: rgba(47, 53, 66, 0.25); }
    .marker-box { fill: var(--marker); stroke: var(--line); stroke-width: 3; }
    .marker text { fill: #fff8e8; font-size: 16px; font-weight: 700; pointer-events: none; }
    .marker.active .marker-box,
    .marker:focus .marker-box { fill: var(--marker-2); }
    .marker.active text,
    .marker:focus text { fill: var(--ink); }
    .marker.hidden, .schedule-item.hidden { display: none; }
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
    @media (max-width: 900px) {
      .app-shell { padding: 12px; }
      .topbar { align-items: flex-start; }
      .workspace { grid-template-columns: 1fr; }
      .pixel-map { min-height: 300px; max-height: none; }
      .side-panel { grid-template-columns: 1fr; }
      .itinerary-list { max-height: none; }
      .stats-bar { grid-template-columns: repeat(2, 1fr); }
      .stat-item { border-bottom: 2px solid var(--line); }
      .map-toolbar { align-items: flex-start; flex-direction: column; }
      .city-pills { justify-content: flex-start; }
    }
    @media (max-width: 520px) {
      .topbar { flex-direction: column; }
      .toolbar { width: 100%; }
      .text-button { flex: 1; }
      .stats-bar { grid-template-columns: 1fr; }
      .stat-item { border-right: 0; }
    }
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
    const markers = Array.from(document.querySelectorAll(".marker"));
    const scheduleItems = Array.from(document.querySelectorAll(".schedule-item"));
    const cityButtons = Array.from(document.querySelectorAll(".city-pill"));
    const overviewRoute = document.getElementById("route-overview");
    const cityRoutes = Array.from(document.querySelectorAll(".city-route"));

    function esc(value) {
      return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }[ch]));
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
      markers.forEach(marker => marker.classList.toggle("active", Number(marker.dataset.stopIndex) === index));
      scheduleItems.forEach(item => item.classList.toggle("active", Number(item.dataset.stopIndex) === index));
      const missing = stop.info_missing ? "信息暂缺，建议实地查证。" : esc(stop.description || "暂无补充描述。");
      const source = stop.info_missing ? "信息暂缺" : esc(stop.source);
      card.innerHTML = `
        <p class="poi-meta">Day ${esc(stop.day)} · ${esc(stop.city)} · ${esc(stop.category)} · ${esc(stop.duration_min)} min</p>
        <h3>${esc(stop.name)}</h3>
        <p>${missing}</p>
        <p><strong>备注：</strong>${esc(stop.notes)}</p>
        <div class="poi-actions">
          ${linkHtml(stop.source_url, "来源")}
          ${linkHtml(stop.official_url, "官网")}
          ${linkHtml(mapsUrl(stop), "导航")}
        </div>
        <div class="source-note">来源：${source}。营业时间、票价和预约信息请以官网为准；本地图用于旅行展示，不作为精准导航。</div>
      `;
    }

    function showCity(city) {
      const isOverview = !city;
      viewLabel.textContent = isOverview ? "总览地图" : `${city} 子地图`;
      cityButtons.forEach(button => button.classList.toggle("active", button.dataset.city === city));
      markers.forEach(marker => marker.classList.toggle("hidden", !isOverview && marker.dataset.city !== city));
      scheduleItems.forEach(item => item.classList.toggle("hidden", !isOverview && item.dataset.city !== city));
      overviewRoute.style.display = isOverview ? "block" : "none";
      cityRoutes.forEach(route => {
        route.style.display = !isOverview && route.dataset.city === city ? "block" : "none";
      });
      if (!isOverview) {
        const first = scheduleItems.find(item => item.dataset.city === city);
        if (first) showCard(Number(first.dataset.stopIndex));
      }
    }

    markers.forEach(marker => {
      marker.addEventListener("click", () => showCard(Number(marker.dataset.stopIndex)));
      marker.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          showCard(Number(marker.dataset.stopIndex));
        }
      });
    });
    scheduleItems.forEach(item => {
      item.addEventListener("click", () => {
        showCity(item.dataset.city);
        showCard(Number(item.dataset.stopIndex));
      });
    });
    cityButtons.forEach(button => {
      button.addEventListener("click", () => showCity(button.dataset.city));
    });
    document.getElementById("overview-button").addEventListener("click", () => showCity(""));
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
    if (stops.length) showCard(0);
"""
