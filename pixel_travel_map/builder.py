"""Render the standalone PixelTravelMap trip builder artifact."""

from __future__ import annotations

from pathlib import Path


def render_builder_html() -> str:
    return r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PixelTravelMap 创建器</title>
  <style>
    :root {
      --paper: #f6ecd9;
      --paper-2: #fffaf0;
      --ink: #26313d;
      --muted: #697386;
      --water: #d9edf0;
      --route: #d64f3f;
      --marker: #1f7a8c;
      --line: #313d4c;
      --focus: #7a3e9d;
      --panel: #fffdf7;
      --warn: #b42318;
      --ok: #1f7a4d;
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
    button, input, select, textarea { font: inherit; }
    .app-shell { width: min(1480px, 100%); margin: 0 auto; padding: 18px; }
    .topbar {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
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
    h1 { margin-bottom: 6px; font-size: clamp(26px, 4vw, 42px); line-height: 1.1; }
    h2 { margin-bottom: 12px; font-size: 18px; }
    h3 { margin-bottom: 8px; font-size: 15px; }
    .atlas-note { max-width: 820px; margin-bottom: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
    .builder-layout {
      display: grid;
      grid-template-columns: minmax(320px, 0.78fr) minmax(0, 1.22fr);
      gap: 16px;
      align-items: start;
    }
    .panel {
      border: 2px solid var(--line);
      background: var(--panel);
      box-shadow: 6px 6px 0 var(--line);
      padding: 16px;
    }
    .stack { display: grid; gap: 16px; }
    .field-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    label { display: grid; gap: 6px; color: var(--muted); font-size: 12px; font-weight: 700; }
    input, select, textarea {
      width: 100%;
      border: 2px solid var(--line);
      border-radius: 4px;
      background: #fffaf0;
      color: var(--ink);
      padding: 9px 10px;
      min-width: 0;
    }
    textarea { min-height: 250px; resize: vertical; line-height: 1.45; }
    input:focus, select:focus, textarea:focus, button:focus-visible {
      outline: 3px solid rgba(122,62,157,0.28);
      outline-offset: 2px;
    }
    .button-row, .download-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }
    .text-button {
      border: 2px solid var(--line);
      border-radius: 4px;
      background: var(--paper-2);
      color: var(--ink);
      cursor: pointer;
      box-shadow: 3px 3px 0 var(--line);
      padding: 9px 12px;
      font-weight: 700;
    }
    .text-button.primary { background: #f5c542; }
    .text-button:active { transform: translate(2px, 2px); box-shadow: 1px 1px 0 var(--line); }
    .text-button:disabled { opacity: 0.48; cursor: not-allowed; transform: none; }
    .status {
      margin: 10px 0 0;
      min-height: 20px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }
    .status.error { color: var(--warn); }
    .status.ok { color: var(--ok); }
    .draft-days { display: grid; gap: 12px; }
    .day-editor {
      border: 2px solid rgba(49,61,76,0.35);
      background: #fffaf0;
      padding: 12px;
    }
    .day-head {
      display: grid;
      grid-template-columns: 90px minmax(110px, 160px) minmax(0, 1fr) auto;
      gap: 8px;
      align-items: end;
      margin-bottom: 10px;
    }
    .table-wrap { overflow-x: auto; border: 2px solid var(--line); background: #fff; }
    table { width: 100%; border-collapse: collapse; min-width: 920px; }
    th, td { border-bottom: 1px solid rgba(49,61,76,0.22); padding: 7px; vertical-align: top; }
    th { text-align: left; color: var(--muted); font-size: 12px; background: #f8efd9; }
    td input, td select { padding: 7px 8px; }
    .row-actions { width: 62px; }
    .mini-button {
      border: 2px solid var(--line);
      border-radius: 4px;
      background: #fffaf0;
      cursor: pointer;
      padding: 5px 8px;
      font-weight: 700;
    }
    .missing input, .missing select { border-color: var(--warn); background: #fff1ed; }
    .preview-box {
      display: grid;
      gap: 12px;
    }
    .preview-map {
      min-height: 320px;
      border: 2px solid var(--line);
      background: #d9edf0;
      overflow: hidden;
    }
    .preview-map .empty {
      display: grid;
      min-height: 320px;
      place-items: center;
      color: var(--muted);
      font-weight: 700;
      text-align: center;
      padding: 24px;
    }
    .pixel-map { display: block; width: 100%; height: auto; background: var(--water); }
    .atlas-water { fill: var(--water); }
    .atlas-frame-inner { fill: rgba(255,255,255,0.22); stroke: var(--line); stroke-width: 2; }
    .map-title, .north { fill: var(--ink); font: 700 18px "Courier New", monospace; }
    .route {
      fill: none;
      stroke: var(--route);
      stroke-width: 4;
      stroke-linecap: round;
      stroke-linejoin: round;
      stroke-dasharray: 12 7;
    }
    .arrow-head { fill: var(--route); }
    .distance-label {
      paint-order: stroke;
      stroke: var(--paper-2);
      stroke-width: 5;
      fill: var(--line);
      font: 700 13px "Courier New", monospace;
    }
    .city-label {
      paint-order: stroke;
      stroke: var(--paper-2);
      stroke-width: 6;
      fill: var(--focus);
      font: 700 16px "Courier New", monospace;
    }
    .marker-halo { fill: rgba(255,250,240,0.82); stroke: rgba(49,61,76,0.3); stroke-width: 1; }
    .marker-box { fill: var(--marker); stroke: var(--line); stroke-width: 2; }
    .marker-num { fill: var(--paper-2); font: 700 16px "Courier New", monospace; }
    .poi-label {
      paint-order: stroke;
      stroke: var(--paper-2);
      stroke-width: 5;
      fill: var(--ink);
      font: 700 14px "Courier New", monospace;
    }
    .poi-day {
      paint-order: stroke;
      stroke: var(--paper-2);
      stroke-width: 4;
      fill: var(--muted);
      font: 700 11px "Courier New", monospace;
    }
    .scale-bar line { stroke: var(--line); stroke-width: 3; }
    .scale-bar text { fill: var(--line); font: 700 13px "Courier New", monospace; }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
    }
    .stat-item {
      border: 2px solid var(--line);
      background: var(--paper-2);
      padding: 10px;
    }
    .stat-item span { display: block; color: var(--muted); font-size: 11px; }
    .stat-item strong { display: block; margin-top: 5px; font-size: 18px; }
    .preview-itinerary {
      border: 2px solid rgba(49,61,76,0.35);
      background: #fffaf0;
      padding: 12px;
      max-height: 360px;
      overflow: auto;
    }
    .preview-itinerary h3 { margin-bottom: 4px; }
    .preview-itinerary p { margin-bottom: 8px; color: var(--muted); font-size: 12px; }
    .preview-itinerary ol { margin: 0 0 14px 22px; padding: 0; line-height: 1.5; }
    .download-panel { display: grid; gap: 10px; }
    .download-grid select { width: auto; min-width: 150px; }
    .help-text { color: var(--muted); font-size: 12px; line-height: 1.45; }
    @media (max-width: 1060px) {
      .builder-layout { grid-template-columns: 1fr; }
      .day-head { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 680px) {
      .app-shell { padding: 12px; }
      .topbar { display: block; }
      .field-grid, .summary-grid { grid-template-columns: 1fr; }
      .day-head { grid-template-columns: 1fr; }
      textarea { min-height: 220px; }
    }
  </style>
</head>
<body>
  <script id="sample-trip-text" type="text/plain">标题：东京 2 日城市旅行
日期：2026-07-01 到 2026-07-02
交通：public-transit

Day 1：东京塔和六本木夜景
- 09:30 东京塔 (lat:35.6586, lon:139.7454, city:Tokyo, country:JP, category:landmark, duration:90)
- 13:00 麻布台之丘 (lat:35.6602, lon:139.7404, city:Tokyo, country:JP, category:viewpoint, duration:120)
- 17:00 六本木之丘 (lat:35.6605, lon:139.7292, city:Tokyo, country:JP, category:viewpoint, duration:120)

Day 2：浅草和上野
- 浅草寺 (city:Tokyo, country:JP, duration:90)
- 上野公园 (city:Tokyo, country:JP, category:nature, duration:120)</script>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">PixelTravelMap Builder</p>
        <h1>行程导入创建器</h1>
        <p class="atlas-note">上传 .docx 或粘贴自然语言行程，补齐地点坐标后生成离线 HTML 地图、JSON 和 SVG poster。坐标不会自动猜测，也不会上传到服务器。</p>
      </div>
    </header>

    <main class="builder-layout">
      <div class="stack">
        <section class="panel">
          <h2>导入行程</h2>
          <label for="docx-input">Word 文档（.docx）
            <input id="docx-input" type="file" accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document">
          </label>
          <p id="docx-status" class="status">旧版 .doc、PDF 和扫描图片暂不支持。</p>
          <label for="builder-data-input">自然语言行程
            <textarea id="builder-data-input" placeholder="粘贴传统旅行行程，或写 Day 1 / 第1天 / D1 格式的简要计划。"></textarea>
          </label>
          <div class="button-row">
            <button class="text-button" id="load-sample" type="button">填入示例</button>
            <button class="text-button primary" id="parse-input" type="button">解析行程</button>
          </div>
          <p id="parse-status" class="status">解析后会进入可编辑草稿；缺失坐标的地点需要手动补齐。</p>
        </section>

        <section class="panel">
          <h2>行程信息</h2>
          <div class="field-grid">
            <label for="trip-title">标题
              <input id="trip-title" type="text">
            </label>
            <label for="trip-transport">交通方式
              <select id="trip-transport">
                <option value="mixed">mixed</option>
                <option value="public-transit">public-transit</option>
                <option value="self-drive">self-drive</option>
                <option value="train">train</option>
                <option value="walk">walk</option>
                <option value="unknown">unknown</option>
              </select>
            </label>
            <label for="trip-start">开始日期
              <input id="trip-start" type="date">
            </label>
            <label for="trip-end">结束日期
              <input id="trip-end" type="date">
            </label>
          </div>
        </section>
      </div>

      <div class="stack">
        <section class="panel">
          <h2>待补全草稿</h2>
          <div id="draft-table" class="draft-days"></div>
          <div class="button-row">
            <button class="text-button" id="add-day" type="button">增加 Day</button>
            <button class="text-button primary" id="build-preview" type="button">生成预览</button>
          </div>
          <p id="validation-status" class="status">至少需要 1 个地点；每个地点必须填写 name、city、country、lat、lon。</p>
        </section>

        <section class="panel preview-box">
          <h2>地图预览</h2>
          <div id="map-preview" class="preview-map"><div class="empty">生成预览后显示经纬度路线地图。</div></div>
          <div id="summary-grid" class="summary-grid"></div>
          <div id="preview-itinerary" class="preview-itinerary"></div>
        </section>

        <section class="panel download-panel">
          <h2>下载 artifact</h2>
          <div class="download-grid">
            <button class="text-button" id="download-json" type="button" disabled>下载 JSON</button>
            <button class="text-button" id="download-map-html" type="button" disabled>下载 HTML 地图</button>
            <button class="text-button" id="download-overview-poster" type="button" disabled>总行程 poster</button>
            <select id="poster-day-select" disabled></select>
            <button class="text-button" id="download-day-poster" type="button" disabled>每日 poster</button>
            <button class="text-button" id="download-record-poster" type="button" disabled>旅行记录 poster</button>
          </div>
          <p class="help-text">下载后的 HTML 是独立离线文件，包含地图、详情、备注区和 poster 工具。</p>
        </section>
      </div>
    </main>
  </div>

  <script>
    const MAP_W = 1040;
    const MAP_H = 620;
    const CATEGORY_VALUES = ["landmark", "museum", "food", "hotel", "nature", "transit", "shopping", "experience", "viewpoint"];
    const TRANSPORT_VALUES = ["self-drive", "train", "public-transit", "walk", "mixed", "unknown"];
    const draftTable = document.getElementById("draft-table");
    const titleInput = document.getElementById("trip-title");
    const transportInput = document.getElementById("trip-transport");
    const startInput = document.getElementById("trip-start");
    const endInput = document.getElementById("trip-end");
    const textInput = document.getElementById("builder-data-input");
    const parseStatus = document.getElementById("parse-status");
    const docxStatus = document.getElementById("docx-status");
    const validationStatus = document.getElementById("validation-status");
    const mapPreview = document.getElementById("map-preview");
    const summaryGrid = document.getElementById("summary-grid");
    const previewItinerary = document.getElementById("preview-itinerary");
    const posterDaySelect = document.getElementById("poster-day-select");
    let draft = emptyDraft();
    let activeTrip = null;

    function emptyDraft() {
      const today = new Date().toISOString().slice(0, 10);
      return {
        trip_title: "自定义 PixelTravelMap 行程",
        start_date: today,
        end_date: today,
        transport: "mixed",
        days: [{ day: 1, date: today, summary: "待补全行程", stops: [] }]
      };
    }

    function esc(value) {
      return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }[ch]));
    }

    function text(value, fallback = "") {
      const raw = String(value ?? "").trim();
      return raw || fallback;
    }

    function trimText(value, limit) {
      const raw = text(value);
      return raw.length <= limit ? raw : raw.slice(0, limit - 1) + "…";
    }

    function fileSafe(value) {
      return text(value, "pixel-travel-map").replace(/[\\/:*?"<>|]+/g, "-").replace(/\s+/g, "-");
    }

    function addDays(dateText, offset) {
      const date = new Date(dateText + "T00:00:00");
      if (Number.isNaN(date.getTime())) return dateText;
      date.setDate(date.getDate() + offset);
      return date.toISOString().slice(0, 10);
    }

    function syncMetaToDraft() {
      draft.trip_title = titleInput.value.trim() || "自定义 PixelTravelMap 行程";
      draft.transport = TRANSPORT_VALUES.includes(transportInput.value) ? transportInput.value : "mixed";
      draft.start_date = startInput.value || new Date().toISOString().slice(0, 10);
      draft.end_date = endInput.value || draft.start_date;
    }

    function syncMetaFromDraft() {
      titleInput.value = draft.trip_title;
      transportInput.value = draft.transport;
      startInput.value = draft.start_date;
      endInput.value = draft.end_date;
    }

    function setStatus(element, message, kind = "") {
      element.textContent = message;
      element.className = "status" + (kind ? " " + kind : "");
    }

    function parseDraftFromText(rawText) {
      const raw = rawText.trim();
      if (!raw) throw new Error("请输入行程文本或上传 .docx。");
      const lines = raw.split(/\r?\n/).map(line => line.trim()).filter(Boolean);
      const dates = raw.match(/\d{4}-\d{2}-\d{2}/g) || [];
      const startDate = dates[0] || new Date().toISOString().slice(0, 10);
      const endDate = dates[dates.length - 1] || startDate;
      const metadataTitle = metadataValue(lines, ["标题", "title"]);
      const transport = metadataValue(lines, ["交通", "transport"]) || "mixed";
      const firstContent = lines.find(line => !isMetadataLine(line) && !parseDayHeading(line) && !isStopLike(line));
      const parsed = {
        trip_title: metadataTitle || firstContent || "自定义 PixelTravelMap 行程",
        start_date: startDate,
        end_date: endDate < startDate ? startDate : endDate,
        transport: TRANSPORT_VALUES.includes(transport) ? transport : "mixed",
        days: []
      };
      let currentDay = null;
      for (const line of lines) {
        if (isMetadataLine(line)) continue;
        const heading = parseDayHeading(line);
        if (heading) {
          currentDay = {
            day: heading.day,
            date: addDays(startDate, heading.day - 1),
            summary: heading.summary || "待补全行程",
            stops: []
          };
          parsed.days.push(currentDay);
          continue;
        }
        const stop = parseStopLine(line);
        if (!stop) continue;
        if (!currentDay) {
          currentDay = {
            day: 1,
            date: startDate,
            summary: "待补全行程",
            stops: []
          };
          parsed.days.push(currentDay);
        }
        currentDay.stops.push(stop);
      }
      if (!parsed.days.length) {
        parsed.days.push({ day: 1, date: startDate, summary: "待补全行程", stops: [] });
      }
      const maxDay = Math.max(...parsed.days.map(day => day.day));
      parsed.end_date = parsed.end_date < addDays(startDate, maxDay - 1) ? addDays(startDate, maxDay - 1) : parsed.end_date;
      return parsed;
    }

    function metadataValue(lines, keys) {
      for (const line of lines) {
        for (const key of keys) {
          const match = line.match(new RegExp("^" + key + "\\s*[：:](.+)$", "i"));
          if (match) return match[1].trim();
        }
      }
      return "";
    }

    function isMetadataLine(line) {
      return /^(标题|title|日期|date|dates|交通|transport)\s*[：:]/i.test(line);
    }

    function chineseNumber(value) {
      const map = { 一: 1, 二: 2, 两: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9, 十: 10 };
      if (/^\d+$/.test(value)) return Number(value);
      if (value === "十") return 10;
      if (value.includes("十")) {
        const parts = value.split("十");
        const tens = parts[0] ? map[parts[0]] : 1;
        const ones = parts[1] ? map[parts[1]] : 0;
        return tens * 10 + ones;
      }
      return map[value] || 1;
    }

    function parseDayHeading(line) {
      let match = line.match(/^(?:Day|D)\s*(\d+)\s*[：:.\-、]?\s*(.*)$/i);
      if (match) return { day: Number(match[1]), summary: match[2].trim() };
      match = line.match(/^第\s*([一二两三四五六七八九十\d]+)\s*天\s*[：:.\-、]?\s*(.*)$/);
      if (match) return { day: chineseNumber(match[1]), summary: match[2].trim() };
      return null;
    }

    function isStopLike(line) {
      return /^[\-•*]\s+/.test(line) || /^\d+[.)、]\s+/.test(line) || /^\d{1,2}[:：]\d{2}/.test(line);
    }

    function parseStopLine(line) {
      const original = line;
      let value = line.replace(/^[\-•*]\s*/, "").replace(/^\d+[.)、]\s*/, "").trim();
      const timeRange = value.match(/(\d{1,2})[:：](\d{2})(?:\s*[-–—到至]\s*(\d{1,2})[:：](\d{2}))?/);
      let duration = 90;
      if (timeRange && timeRange[3]) {
        const start = Number(timeRange[1]) * 60 + Number(timeRange[2]);
        const end = Number(timeRange[3]) * 60 + Number(timeRange[4]);
        if (end > start) duration = end - start;
      }
      value = value.replace(/^\d{1,2}[:：]\d{2}(?:\s*[-–—到至]\s*\d{1,2}[:：]\d{2})?\s*/, "").trim();
      const fields = parseInlineFields(value);
      if (fields.duration) duration = Number(fields.duration) || duration;
      const fieldBlockPattern = /[（(][^()（）]*(?:lat|lon|city|country|category|duration|notes|source)[^()（）]*[）)]/ig;
      let name = value.replace(fieldBlockPattern, "").trim();
      name = name.replace(/^[:：,\-—、\s]+/, "").replace(/\s+/g, " ");
      if (!name && !isStopLike(original)) return null;
      if (!name) name = "待命名地点";
      return {
        name,
        city: fields.city || "",
        country: fields.country || "",
        lat: fields.lat || "",
        lon: fields.lon || "",
        category: CATEGORY_VALUES.includes(fields.category) ? fields.category : "landmark",
        duration_min: String(Math.max(0, Math.round(duration))),
        notes: fields.notes || "由创建器导入，建议补充实际注意事项。"
      };
    }

    function parseInlineFields(value) {
      const fields = {};
      for (const match of value.matchAll(/([a-zA-Z_]+)\s*[：:]\s*([^,，)）]+)/g)) {
        fields[match[1].trim().toLowerCase()] = match[2].trim();
      }
      return fields;
    }

    function renderDraft() {
      syncMetaFromDraft();
      draftTable.innerHTML = draft.days.map((day, dayIndex) => `
        <section class="day-editor" data-day-index="${dayIndex}">
          <div class="day-head">
            <label>Day
              <input type="number" min="1" value="${esc(day.day)}" data-kind="day" data-field="day">
            </label>
            <label>日期
              <input type="date" value="${esc(day.date)}" data-kind="day" data-field="date">
            </label>
            <label>摘要
              <input type="text" value="${esc(day.summary || "")}" data-kind="day" data-field="summary">
            </label>
            <button class="text-button" type="button" data-action="add-stop" data-day-index="${dayIndex}">增加地点</button>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>地点</th><th>城市</th><th>国家</th><th>lat</th><th>lon</th><th>类型</th><th>停留</th><th>备注</th><th class="row-actions"></th>
                </tr>
              </thead>
              <tbody>
                ${day.stops.map((stop, stopIndex) => renderStopRow(stop, dayIndex, stopIndex)).join("") || `<tr><td colspan="9" class="help-text">此 Day 还没有地点。</td></tr>`}
              </tbody>
            </table>
          </div>
        </section>
      `).join("");
    }

    function renderStopRow(stop, dayIndex, stopIndex) {
      const missing = ["name", "city", "country", "lat", "lon"].some(field => !String(stop[field] ?? "").trim());
      return `
        <tr class="${missing ? "missing" : ""}" data-day-index="${dayIndex}" data-stop-index="${stopIndex}">
          <td><input type="text" value="${esc(stop.name)}" data-kind="stop" data-field="name"></td>
          <td><input type="text" value="${esc(stop.city)}" data-kind="stop" data-field="city"></td>
          <td><input type="text" value="${esc(stop.country)}" data-kind="stop" data-field="country"></td>
          <td><input type="number" step="0.0001" value="${esc(stop.lat)}" data-kind="stop" data-field="lat"></td>
          <td><input type="number" step="0.0001" value="${esc(stop.lon)}" data-kind="stop" data-field="lon"></td>
          <td>
            <select data-kind="stop" data-field="category">
              ${CATEGORY_VALUES.map(category => `<option value="${category}" ${stop.category === category ? "selected" : ""}>${category}</option>`).join("")}
            </select>
          </td>
          <td><input type="number" min="0" step="5" value="${esc(stop.duration_min)}" data-kind="stop" data-field="duration_min"></td>
          <td><input type="text" value="${esc(stop.notes)}" data-kind="stop" data-field="notes"></td>
          <td><button class="mini-button" type="button" data-action="remove-stop" data-day-index="${dayIndex}" data-stop-index="${stopIndex}">删</button></td>
        </tr>
      `;
    }

    function addStop(dayIndex) {
      draft.days[dayIndex].stops.push({
        name: "待命名地点",
        city: "",
        country: "",
        lat: "",
        lon: "",
        category: "landmark",
        duration_min: "90",
        notes: "由创建器导入，建议补充实际注意事项。"
      });
      renderDraft();
    }

    function slugify(value) {
      const ascii = value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
      let hash = 0;
      for (let index = 0; index < value.length; index += 1) {
        hash = ((hash << 5) - hash + value.charCodeAt(index)) | 0;
      }
      const suffix = Math.abs(hash).toString(16).slice(0, 6).padStart(6, "0");
      return (ascii || "stop") + "-" + suffix;
    }

    function buildTripFromDraft() {
      syncMetaToDraft();
      const errors = [];
      const days = draft.days
        .map((day, dayIndex) => ({
          day: Number(day.day) || dayIndex + 1,
          date: day.date || addDays(draft.start_date, dayIndex),
          summary: day.summary || "每日行程",
          stops: day.stops.map((stop, stopIndex) => normalizeStop(stop, day, dayIndex, stopIndex, errors))
        }))
        .filter(day => day.stops.length);
      if (!draft.trip_title.trim()) errors.push("请填写标题。");
      if (!days.length) errors.push("至少需要 1 个地点。");
      if (!draft.start_date || !draft.end_date) errors.push("请填写开始和结束日期。");
      if (draft.end_date < draft.start_date) errors.push("结束日期不能早于开始日期。");
      if (errors.length) throw new Error(errors.slice(0, 6).join(" "));
      return {
        schema_version: "1.0",
        trip_title: draft.trip_title.trim(),
        start_date: draft.start_date,
        end_date: draft.end_date,
        travelers: ["traveler"],
        budget_cny: null,
        transport: draft.transport,
        style_theme: "pastel-pixel",
        lang: "zh-CN",
        days
      };
    }

    function normalizeStop(stop, day, dayIndex, stopIndex, errors) {
      const prefix = `Day ${day.day || dayIndex + 1} 第 ${stopIndex + 1} 个地点`;
      const latRaw = String(stop.lat ?? "").trim();
      const lonRaw = String(stop.lon ?? "").trim();
      const lat = Number(latRaw);
      const lon = Number(lonRaw);
      const duration = Number(stop.duration_min);
      if (!text(stop.name)) errors.push(`${prefix} 缺少地点名。`);
      if (!text(stop.city)) errors.push(`${prefix} 缺少 city。`);
      if (!text(stop.country)) errors.push(`${prefix} 缺少 country。`);
      if (!latRaw || !Number.isFinite(lat) || lat < -90 || lat > 90) errors.push(`${prefix} lat 不正确。`);
      if (!lonRaw || !Number.isFinite(lon) || lon < -180 || lon > 180) errors.push(`${prefix} lon 不正确。`);
      return {
        id: slugify(`day-${day.day || dayIndex + 1}-${stop.name}-${stopIndex + 1}`),
        name: text(stop.name),
        name_en: null,
        city: text(stop.city),
        country: text(stop.country),
        lat,
        lon,
        crs: "wgs84",
        category: CATEGORY_VALUES.includes(stop.category) ? stop.category : "landmark",
        duration_min: Number.isFinite(duration) ? Math.max(0, Math.round(duration)) : 90,
        description: null,
        notes: text(stop.notes, "由创建器导入，建议补充实际注意事项。"),
        source: "user_builder_input",
        source_url: null,
        official_url: null,
        navigation_url: null,
        info_missing: false
      };
    }

    function flattenStops(trip) {
      const stops = [];
      let ordinal = 1;
      trip.days.forEach(day => {
        day.stops.forEach(stop => {
          stops.push({
            ...stop,
            day: day.day,
            date: day.date,
            day_summary: day.summary || "",
            ordinal
          });
          ordinal += 1;
        });
      });
      return stops;
    }

    function stopKey(stop) {
      return stop.id || `${stop.day}-${stop.name}-${stop.city}`;
    }

    function haversineKm(a, b) {
      const radius = 6371;
      const toRad = value => value * Math.PI / 180;
      const lat1 = toRad(a.lat);
      const lat2 = toRad(b.lat);
      const dlat = lat2 - lat1;
      const dlon = toRad(b.lon - a.lon);
      const h = Math.sin(dlat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2;
      return 2 * radius * Math.asin(Math.sqrt(h));
    }

    function totalKm(items) {
      return Math.round(items.slice(1).reduce((sum, stop, index) => sum + haversineKm(items[index], stop), 0));
    }

    function niceScale(maxKm) {
      if (maxKm <= 5) return 1;
      let scale = 1;
      [2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000].forEach(candidate => {
        if (candidate <= maxKm) scale = candidate;
      });
      return scale;
    }

    function projectStops(items, width = MAP_W, height = MAP_H, padding = 72) {
      const meanLat = items.reduce((sum, stop) => sum + stop.lat, 0) / Math.max(items.length, 1);
      const cosLat = Math.max(Math.cos(meanLat * Math.PI / 180), 0.18);
      const values = items.map(stop => ({ stop, x: stop.lon * cosLat, y: stop.lat }));
      const xs = values.map(item => item.x);
      const ys = values.map(item => item.y);
      const minX = Math.min(...xs);
      const maxX = Math.max(...xs);
      const minY = Math.min(...ys);
      const maxY = Math.max(...ys);
      const xSpan = Math.max(maxX - minX, 0.08);
      const ySpan = Math.max(maxY - minY, 0.08);
      const drawW = width - padding * 2;
      const drawH = height - padding * 2;
      const fit = Math.min(drawW / xSpan, drawH / ySpan);
      const usedW = xSpan * fit;
      const left = (width - usedW) / 2;
      const top = (height - ySpan * fit) / 2;
      const points = {};
      const occupied = {};
      values.forEach(({ stop, x, y }) => {
        let px = Math.round((left + (x - minX) * fit) / 8) * 8;
        let py = Math.round((top + (maxY - y) * fit) / 8) * 8;
        const key = `${px},${py}`;
        const hit = occupied[key] || 0;
        occupied[key] = hit + 1;
        if (hit) {
          px += ((hit % 3) - 1) * 26;
          py += (Math.floor(hit / 3) + 1) * 22;
        }
        points[stopKey(stop)] = [
          Math.min(Math.max(px, 44), width - 44),
          Math.min(Math.max(py, 44), height - 44)
        ];
      });
      const kmPerPx = xSpan * 111.32 * cosLat / Math.max(usedW, 1);
      const targetPx = Math.min(180, Math.max(90, drawW * 0.18));
      const scaleKm = niceScale(kmPerPx * targetPx);
      const scalePx = Math.min(Math.max(56, Math.round(scaleKm / Math.max(kmPerPx, 0.001))), width - 160);
      return { points, scaleKm, scalePx };
    }

    function contextForCity(stops, city) {
      const selected = {};
      stops.forEach((stop, index) => {
        if (stop.city !== city) return;
        [index - 1, index, index + 1].forEach(neighbor => {
          if (stops[neighbor]) selected[stops[neighbor].id] = stops[neighbor];
        });
      });
      return Object.values(selected);
    }

    function buildMapViews(stops) {
      const overviewProjection = projectStops(stops);
      const views = [{
        key: "overview",
        label: "总览地图",
        stops,
        contextStops: stops,
        ...overviewProjection
      }];
      [...new Set(stops.map(stop => stop.city))].sort().forEach(city => {
        const cityStops = stops.filter(stop => stop.city === city);
        const contextStops = contextForCity(stops, city);
        const projected = cityStops.length > 1 ? cityStops : contextStops;
        views.push({
          key: city,
          label: `${city} detail view`,
          stops: cityStops,
          contextStops,
          ...projectStops(projected)
        });
      });
      return views;
    }

    function renderMapSvg(trip, interactive = false) {
      const stops = flattenStops(trip);
      const views = buildMapViews(stops);
      return `
        <svg id="pixel-map" class="pixel-map" viewBox="0 0 ${MAP_W} ${MAP_H}" role="img" aria-label="Latitude longitude travel atlas">
          <defs>
            <pattern id="atlas-grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(49,61,76,0.12)" stroke-width="1"/>
            </pattern>
            <marker id="route-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" class="arrow-head"/>
            </marker>
          </defs>
          ${views.map(view => renderMapView(view, stops, interactive)).join("")}
        </svg>
      `;
    }

    function renderMapView(view, allStops, interactive) {
      const activeIds = new Set(view.stops.map(stop => stop.id));
      const contextIds = new Set(view.contextStops.map(stop => stop.id));
      const viewStops = allStops.filter(stop => contextIds.has(stop.id) && view.points[stopKey(stop)]);
      const routePoints = viewStops.map(stop => view.points[stopKey(stop)].join(",")).join(" ");
      const segments = viewStops.slice(1).map((stop, index) => {
        const start = viewStops[index];
        const p1 = view.points[stopKey(start)];
        const p2 = view.points[stopKey(stop)];
        const km = Math.max(1, Math.round(haversineKm(start, stop)));
        return `<text class="distance-label" x="${(p1[0] + p2[0]) / 2}" y="${(p1[1] + p2[1]) / 2 - 10}" text-anchor="middle">${km} km</text>`;
      }).join("");
      const cityLabels = [...new Set(viewStops.map(stop => `${stop.city} · ${stop.country}`))].map(label => {
        const cityStops = viewStops.filter(stop => `${stop.city} · ${stop.country}` === label);
        const points = cityStops.map(stop => view.points[stopKey(stop)]);
        const x = points.reduce((sum, point) => sum + point[0], 0) / points.length;
        const y = Math.max(Math.min(...points.map(point => point[1])) - 32, 30);
        return `<text class="city-label" x="${x}" y="${y}" text-anchor="middle">${esc(label)}</text>`;
      }).join("");
      const markers = viewStops.map(stop => {
        const point = view.points[stopKey(stop)];
        const isActive = activeIds.has(stop.id);
        const data = interactive && isActive ? ` data-stop-index="${stop.ordinal - 1}" tabindex="0" role="button"` : "";
        const dim = isActive ? "" : " context";
        return `
          <g class="marker marker-${esc(stop.category)}${dim}"${data} aria-label="${esc(stop.name)}">
            <circle class="marker-halo" cx="${point[0]}" cy="${point[1]}" r="18"/>
            <rect class="marker-box" x="${point[0] - 15}" y="${point[1] - 15}" width="30" height="30" rx="2"/>
            <text class="marker-num" x="${point[0]}" y="${point[1] + 5}" text-anchor="middle">${stop.ordinal}</text>
            <text class="poi-label" x="${point[0] + 24}" y="${point[1] - 8}">${esc(trimText(stop.name, 14))}</text>
            <text class="poi-day" x="${point[0] + 24}" y="${point[1] + 10}">Day ${stop.day} · ${esc(stop.city)}</text>
          </g>
        `;
      }).join("");
      return `
        <g class="map-view" data-view="${esc(view.key)}" style="${view.key === "overview" ? "" : "display:none"}">
          <rect width="${MAP_W}" height="${MAP_H}" class="atlas-water"/>
          <rect width="${MAP_W}" height="${MAP_H}" fill="url(#atlas-grid)"/>
          <rect x="28" y="28" width="${MAP_W - 56}" height="${MAP_H - 56}" class="atlas-frame-inner"/>
          <text x="48" y="56" class="map-title">${esc(view.label)}</text>
          <text x="${MAP_W - 48}" y="56" class="north" text-anchor="end">N ↑</text>
          <polyline class="route" points="${routePoints}" marker-mid="url(#route-arrow)" marker-end="url(#route-arrow)"/>
          ${segments}
          ${cityLabels}
          <g class="marker-layer" data-view="${esc(view.key)}">${markers}</g>
          ${renderScaleBar(view)}
        </g>
      `;
    }

    function renderScaleBar(view) {
      const x = 48;
      const y = MAP_H - 48;
      return `
        <g class="scale-bar">
          <line x1="${x}" y1="${y}" x2="${x + view.scalePx}" y2="${y}" />
          <line x1="${x}" y1="${y - 8}" x2="${x}" y2="${y + 8}" />
          <line x1="${x + view.scalePx}" y1="${y - 8}" x2="${x + view.scalePx}" y2="${y + 8}" />
          <text x="${x + view.scalePx / 2}" y="${y - 14}" text-anchor="middle">≈ ${view.scaleKm} km</text>
        </g>
      `;
    }

    function renderStatsHtml(trip) {
      const stops = flattenStops(trip);
      const cities = new Set(stops.map(stop => stop.city));
      const items = [
        ["天数", String(trip.days.length)],
        ["城市", String(cities.size)],
        ["地点", String(stops.length)],
        ["直线路线", `${totalKm(stops)} km`]
      ];
      return items.map(([label, value]) => `<div class="stat-item"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join("");
    }

    function renderPreviewItinerary(trip) {
      return trip.days.map(day => `
        <section>
          <h3>Day ${day.day} <span>${esc(day.date)}</span></h3>
          <p>${esc(day.summary || "每日行程")}</p>
          <ol>${day.stops.map(stop => `<li>${esc(stop.name)} · ${esc(stop.city)} · ${esc(stop.duration_min)} min</li>`).join("")}</ol>
        </section>
      `).join("");
    }

    function renderItineraryHtml(trip) {
      let index = 0;
      return trip.days.map(day => {
        const stopsHtml = day.stops.map(stop => {
          const currentIndex = index;
          index += 1;
          return `
            <button class="schedule-item" type="button" data-stop-index="${currentIndex}" data-city="${esc(stop.city)}">
              <span class="schedule-index">${currentIndex + 1}</span>
              <span>
                <strong>${esc(stop.name)}</strong>
                <small>${esc(stop.city)} · Day ${day.day} · ${stop.duration_min} min</small>
              </span>
            </button>
          `;
        }).join("");
        return `
          <div class="day-block">
            <h3>Day ${day.day} <span>${esc(day.date)}</span></h3>
            <p class="day-summary">${esc(day.summary || "每日行程")}</p>
            ${stopsHtml}
          </div>
        `;
      }).join("");
    }

    function renderPoiCardHtml(stop) {
      const mapUrl = stop.navigation_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(stop.lat + "," + stop.lon)}`;
      const link = (url, label) => url ? `<a href="${esc(url)}" target="_blank" rel="noreferrer">${esc(label)}</a>` : "";
      return `
        <p class="poi-meta">Day ${esc(stop.day)} · ${esc(stop.city)} · ${esc(stop.category)} · ${esc(stop.duration_min)} min · ${esc(stop.lat)}, ${esc(stop.lon)}</p>
        <h3>${esc(stop.name)}</h3>
        <p>${esc(stop.description || "暂无补充描述。")}</p>
        <p><strong>备注：</strong>${esc(stop.notes)}</p>
        <div class="poi-actions">
          ${link(stop.source_url, "来源")}
          ${link(stop.official_url, "官网")}
          ${link(mapUrl, "导航")}
        </div>
        <div class="source-note">来源：${esc(stop.source)}。地图方位与距离由 POI 经纬度计算；营业时间、票价和预约信息请以官网为准。</div>
      `;
    }

    function posterCss() {
      return `
        .bg{fill:#f6ecd9}.frame{fill:#fffaf0;stroke:#313d4c;stroke-width:4}
        .kicker{fill:#7a3e9d;font:700 22px Courier New,monospace}.title{fill:#26313d;font:700 42px Courier New,monospace}
        .meta,.small{fill:#697386;font:700 18px Courier New,monospace}.section{fill:#26313d;font:700 28px Courier New,monospace}
        .map-bg{fill:#d9edf0}.map-frame{fill:rgba(255,255,255,.25);stroke:#313d4c;stroke-width:2}
        .route{fill:none;stroke:#d64f3f;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:12 7}.arrow{fill:#d64f3f}
        .label{paint-order:stroke;stroke:#fffaf0;stroke-width:5;fill:#26313d;font:700 15px Courier New,monospace}
        .muted-label{paint-order:stroke;stroke:#fffaf0;stroke-width:4;fill:#697386;font:700 12px Courier New,monospace}
        .city{paint-order:stroke;stroke:#fffaf0;stroke-width:6;fill:#7a3e9d;font:700 17px Courier New,monospace}
        .distance{paint-order:stroke;stroke:#fffaf0;stroke-width:5;fill:#313d4c;font:700 13px Courier New,monospace}
        .marker-box{fill:#1f7a8c;stroke:#313d4c;stroke-width:2}.marker-num{fill:#fffaf0;font:700 16px Courier New,monospace}
        .row{fill:#fff;stroke:#313d4c;stroke-width:2}.row-title{fill:#26313d;font:700 18px Courier New,monospace}
        .row-text{fill:#697386;font:700 15px Courier New,monospace}.note{fill:#fff7d6;stroke:#313d4c;stroke-width:2;stroke-dasharray:8 6}
        .note-text{fill:#26313d;font:700 16px Courier New,monospace}.scale line{stroke:#313d4c;stroke-width:3}.scale text{fill:#313d4c;font:700 13px Courier New,monospace}
      `;
    }

    function posterDefs() {
      return `
        <defs>
          <pattern id="poster-grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(49,61,76,0.12)" stroke-width="1"/>
          </pattern>
          <marker id="poster-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0 0 L10 5 L0 10z" class="arrow"/>
          </marker>
        </defs>
      `;
    }

    function routeMapSvg(items, x, y, width, height, title) {
      const mapStops = items.length ? items : [];
      const projection = projectStops(mapStops, width, height);
      const routePoints = mapStops.map(stop => projection.points[stopKey(stop)].join(",")).join(" ");
      const segments = mapStops.slice(1).map((stop, index) => {
        const a = mapStops[index];
        const p1 = projection.points[stopKey(a)];
        const p2 = projection.points[stopKey(stop)];
        const km = Math.max(1, Math.round(haversineKm(a, stop)));
        return `<text class="distance" x="${(p1[0] + p2[0]) / 2}" y="${(p1[1] + p2[1]) / 2 - 10}" text-anchor="middle">${km} km</text>`;
      }).join("");
      const cities = [...new Set(mapStops.map(stop => `${stop.city} · ${stop.country}`))].map(cityLabel => {
        const cityStops = mapStops.filter(stop => `${stop.city} · ${stop.country}` === cityLabel);
        const pts = cityStops.map(stop => projection.points[stopKey(stop)]);
        const cx = pts.reduce((sum, point) => sum + point[0], 0) / pts.length;
        const cy = Math.max(Math.min(...pts.map(point => point[1])) - 30, 28);
        return `<text class="city" x="${cx}" y="${cy}" text-anchor="middle">${esc(cityLabel)}</text>`;
      }).join("");
      const markersSvg = mapStops.map(stop => {
        const point = projection.points[stopKey(stop)];
        return `
          <g>
            <rect class="marker-box" x="${point[0] - 15}" y="${point[1] - 15}" width="30" height="30" rx="2"/>
            <text class="marker-num" x="${point[0]}" y="${point[1] + 5}" text-anchor="middle">${stop.ordinal}</text>
            <text class="label" x="${point[0] + 24}" y="${point[1] - 8}">${esc(trimText(stop.name, 14))}</text>
            <text class="muted-label" x="${point[0] + 24}" y="${point[1] + 10}">Day ${stop.day} · ${esc(stop.city)}</text>
          </g>`;
      }).join("");
      return `
        <g transform="translate(${x},${y})">
          <rect width="${width}" height="${height}" class="map-bg"/>
          <rect width="${width}" height="${height}" fill="url(#poster-grid)"/>
          <rect x="28" y="28" width="${width - 56}" height="${height - 56}" class="map-frame"/>
          <text x="48" y="56" class="row-title">${esc(title)}</text>
          <text x="${width - 48}" y="56" class="row-title" text-anchor="end">N ↑</text>
          <polyline class="route" points="${routePoints}" marker-mid="url(#poster-arrow)" marker-end="url(#poster-arrow)"/>
          ${segments}${cities}${markersSvg}
          <g class="scale">
            <line x1="48" y1="${height - 48}" x2="${48 + projection.scalePx}" y2="${height - 48}"/>
            <line x1="48" y1="${height - 56}" x2="48" y2="${height - 40}"/>
            <line x1="${48 + projection.scalePx}" y1="${height - 56}" x2="${48 + projection.scalePx}" y2="${height - 40}"/>
            <text x="${48 + projection.scalePx / 2}" y="${height - 62}" text-anchor="middle">≈ ${projection.scaleKm} km</text>
          </g>
        </g>`;
    }

    function posterShell(title, subtitle, body) {
      return `<svg id="pixel-travel-dynamic-poster" xmlns="http://www.w3.org/2000/svg" width="1600" height="1130" viewBox="0 0 1600 1130" role="img" aria-label="${esc(title)}">
        ${posterDefs()}
        <style>${posterCss()}</style>
        <rect width="1600" height="1130" class="bg"/>
        <rect x="64" y="56" width="1472" height="1018" class="frame"/>
        <text x="120" y="112" class="kicker">PixelTravelMap · offline share poster</text>
        <text x="120" y="154" class="title">${esc(trimText(title, 34))}</text>
        <text x="120" y="194" class="meta">${esc(subtitle)}</text>
        ${body}
      </svg>`;
    }

    function itineraryRows(items, x, y, width, rowHeight, limit) {
      return items.slice(0, limit).map((item, index) => {
        const rowY = y + index * rowHeight;
        return `<g transform="translate(${x},${rowY})">
          <rect width="${width}" height="${rowHeight - 8}" rx="4" class="row"/>
          <text x="20" y="25" class="row-title">${esc(item.title)}</text>
          <text x="20" y="${rowHeight - 18}" class="row-text">${esc(trimText(item.body, 105))}</text>
        </g>`;
      }).join("");
    }

    function noteBox(label, note, x, y, width, height) {
      const content = text(note) || "暂无补充备注。";
      return `<g transform="translate(${x},${y})">
        <rect width="${width}" height="${height}" rx="4" class="note"/>
        <text x="20" y="28" class="row-title">${esc(label)}</text>
        <text x="20" y="58" class="note-text">${esc(trimText(content, 96))}</text>
      </g>`;
    }

    function renderOverviewPosterSvgForTrip(trip) {
      const stops = flattenStops(trip);
      const rows = trip.days.map(day => ({
        title: `Day ${day.day} · ${day.date}`,
        body: `${day.summary || "行程"}：${day.stops.map(stop => `${stop.name}(${stop.city}, ${stop.duration_min}m)`).join(" · ")}`
      }));
      const subtitle = `${trip.start_date} - ${trip.end_date} · ${trip.days.length} days · ${new Set(stops.map(stop => stop.city)).size} cities · ${stops.length} stops · ${totalKm(stops)} km straight-line route`;
      const body = `
        ${routeMapSvg(stops, 120, 220, 1360, 500, "总行程路线")}
        <text x="120" y="760" class="section">完整行程</text>
        ${itineraryRows(rows, 120, 790, 1360, Math.min(58, Math.max(42, Math.floor(300 / trip.days.length))), trip.days.length)}
      `;
      return posterShell(`${trip.trip_title} · 总行程介绍`, subtitle, body);
    }

    function renderDayPosterSvgForTrip(trip, dayNumber, notes = {}) {
      const stops = flattenStops(trip);
      const day = trip.days.find(item => item.day === Number(dayNumber)) || trip.days[0];
      const dayStops = stops.filter(stop => stop.day === day.day);
      const rows = dayStops.map(stop => ({
        title: `${stop.ordinal}. ${stop.name} · ${stop.city}`,
        body: `${stop.category} · 预计停留 ${stop.duration_min} min · ${stop.notes || "按现场情况调整"}`
      }));
      const note = (notes.days && notes.days[day.day]) || day.summary || "";
      const body = `
        ${routeMapSvg(dayStops, 120, 220, 1360, 420, `Day ${day.day} 明日路线`)}
        <text x="120" y="690" class="section">明日具体行程</text>
        ${itineraryRows(rows, 120, 720, 1360, 58, 6)}
        ${noteBox("同行提醒 / 注意事项", note, 120, 1010, 1360, 70)}
      `;
      return posterShell(`${trip.trip_title} · Day ${day.day} 简报`, `${day.date} · ${day.summary || "每日行程"} · ${dayStops.length} stops · ${totalKm(dayStops)} km straight-line route`, body);
    }

    function renderRecordPosterSvgForTrip(trip, notes = {}) {
      const stops = flattenStops(trip);
      const rows = trip.days.map(day => {
        const dayStops = stops.filter(stop => stop.day === day.day);
        const dayRemark = text(notes.days && notes.days[day.day]) || day.summary || "暂无当天记录";
        const stopRemark = dayStops.map(stop => text(notes.stops && notes.stops[stopKey(stop)])).filter(Boolean).join("；");
        return {
          title: `Day ${day.day} · ${day.date}`,
          body: stopRemark ? `${dayRemark}｜${stopRemark}` : dayRemark
        };
      });
      const body = `
        ${routeMapSvg(stops, 120, 220, 1360, 450, "旅行记录路线")}
        ${noteBox("全程总结", notes.trip || "", 120, 700, 1360, 86)}
        <text x="120" y="830" class="section">每日记录</text>
        ${itineraryRows(rows, 120, 860, 1360, Math.min(54, Math.max(40, Math.floor(205 / trip.days.length))), trip.days.length)}
      `;
      return posterShell(`${trip.trip_title} · 旅行记录`, `${trip.start_date} - ${trip.end_date} · 记录来自当前浏览器备注`, body);
    }

    function downloadText(filename, content, type) {
      const blob = new Blob([content], { type });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      URL.revokeObjectURL(a.href);
      a.remove();
    }

    function downloadSvg(filename, svgText) {
      downloadText(filename, svgText, "image/svg+xml;charset=utf-8");
    }

    function renderViewerHtml(trip) {
      const json = JSON.stringify(trip).replace(/<\//g, "<\\/");
      const closeScript = "</" + "script>";
      const runtime = viewerRuntimeSource();
      return `<!doctype html>
<html lang="${esc(trip.lang || "zh-CN")}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${esc(trip.trip_title)} | PixelTravelMap</title>
  <style>${viewerCss()}</style>
</head>
<body>
  <script id="trip-data" type="application/json">${json}${closeScript}
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">PixelTravelMap Atlas</p>
        <h1>${esc(trip.trip_title)}</h1>
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
          <div class="city-pills" id="city-pills" aria-label="城市 detail view"></div>
        </div>
        <div id="map-container"><svg id="pixel-map" class="pixel-map" viewBox="0 0 ${MAP_W} ${MAP_H}"></svg></div>
        <div class="stats-bar" id="stats-bar"></div>
      </section>
      <aside class="side-panel">
        <section class="panel-section">
          <h2>完整行程</h2>
          <div id="itinerary-list" class="itinerary-list"><!-- data-stop-index hydrated by runtime --></div>
        </section>
        <section class="panel-section">
          <h2>地标详情</h2>
          <article id="poi-card" class="poi-card" aria-live="polite">
            <p class="empty-state">点击地图编号或日程项查看详情。</p>
          </article>
        </section>
        <section class="panel-section poster-tools">
          <h2>Poster 工具</h2>
          <div class="poster-controls">
            <button class="text-button compact" id="download-overview-poster" type="button">下载总行程 poster</button>
            <label class="field-label" for="poster-day-select">每日简报</label>
            <div class="inline-controls">
              <select id="poster-day-select"></select>
              <button class="text-button compact" id="download-day-poster" type="button">下载每日 poster</button>
            </div>
            <button class="text-button compact" id="download-record-poster" type="button">下载旅行记录 poster</button>
          </div>
          <div class="notes-editor">
            <label class="field-label" for="trip-note">全程备注 / 结束总结</label>
            <textarea id="trip-note" rows="3" placeholder="旅行前可写整体提醒；旅行后可写总结。"></textarea>
            <label class="field-label" for="day-note">当前 Day 备注</label>
            <textarea id="day-note" rows="3" placeholder="写给同行朋友的明日注意事项，或当天记录。"></textarea>
            <label class="field-label" for="stop-note">当前地点备注</label>
            <textarea id="stop-note" rows="3" placeholder="记录某个地点的临时变化、体验或提醒。"></textarea>
            <button class="text-button compact danger" id="clear-notes" type="button">清空备注</button>
          </div>
        </section>
      </aside>
    </main>
  </div>
  <script>${runtime}
initViewer();${closeScript}
</body>
</html>`;
    }

    function viewerRuntimeSource() {
      const functions = [
        esc,
        text,
        trimText,
        fileSafe,
        flattenStops,
        stopKey,
        haversineKm,
        totalKm,
        niceScale,
        projectStops,
        contextForCity,
        buildMapViews,
        renderMapSvg,
        renderMapView,
        renderScaleBar,
        renderStatsHtml,
        renderItineraryHtml,
        renderPoiCardHtml,
        posterCss,
        posterDefs,
        routeMapSvg,
        posterShell,
        itineraryRows,
        noteBox,
        renderOverviewPosterSvgForTrip,
        renderDayPosterSvgForTrip,
        renderRecordPosterSvgForTrip,
        downloadText,
        downloadSvg,
        viewerCss,
        initViewer
      ];
      return `const MAP_W = ${MAP_W};\nconst MAP_H = ${MAP_H};\n` + functions.map(fn => fn.toString()).join("\n\n");
    }

    function viewerCss() {
      return `
        :root{--paper:#f6ecd9;--paper-2:#fffaf0;--ink:#26313d;--muted:#697386;--water:#d9edf0;--grid:rgba(38,49,61,.12);--route:#d64f3f;--marker:#1f7a8c;--panel:#fffdf7;--line:#313d4c;--focus:#7a3e9d;--shadow:rgba(38,49,61,.22)}
        *{box-sizing:border-box}body{margin:0;min-height:100vh;color:var(--ink);background:linear-gradient(90deg,rgba(38,49,61,.04) 1px,transparent 1px),linear-gradient(rgba(38,49,61,.04) 1px,transparent 1px),var(--paper);background-size:18px 18px;font-family:"Courier New",ui-monospace,monospace;letter-spacing:0}
        button,a,select,textarea{font:inherit}.app-shell{width:min(1480px,100%);margin:0 auto;padding:18px}.topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;padding:10px 0 18px}.eyebrow{margin:0 0 4px;color:var(--focus);font-size:12px;font-weight:700;text-transform:uppercase}h1,h2,h3,p{margin-top:0}h1{margin-bottom:6px;font-size:clamp(24px,4vw,40px);line-height:1.1}h2{margin-bottom:12px;font-size:18px}h3{margin-bottom:6px;font-size:15px}.atlas-note{max-width:760px;margin-bottom:0;color:var(--muted);font-size:13px;line-height:1.5}.toolbar{display:flex;gap:8px;align-items:center}
        .icon-button,.text-button,.city-pill{border:2px solid var(--line);background:var(--panel);color:var(--ink);cursor:pointer;box-shadow:3px 3px 0 var(--line);font-weight:700}.icon-button{width:40px;height:38px}.text-button,.city-pill{padding:9px 12px;border-radius:4px}.compact{padding:8px 10px;font-size:12px}.danger{color:#b42318}.icon-button:active,.text-button:active,.city-pill:active{transform:translate(2px,2px);box-shadow:1px 1px 0 var(--line)}
        .workspace{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:16px;align-items:start}.map-stage,.side-panel,.panel-section{border:2px solid var(--line);background:var(--panel);box-shadow:6px 6px 0 var(--line)}.map-stage{overflow:hidden}.map-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 14px;border-bottom:2px solid var(--line);font-weight:700}.city-pills{display:flex;flex-wrap:wrap;gap:8px}.city-pill.active{background:#f5c542}.pixel-map{display:block;width:100%;height:auto;background:var(--water)}.atlas-water{fill:var(--water)}.atlas-frame-inner{fill:rgba(255,255,255,.22);stroke:var(--line);stroke-width:2}.map-title,.north{fill:var(--ink);font:700 18px "Courier New",monospace}.route{fill:none;stroke:var(--route);stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:12 7}.arrow-head{fill:var(--route)}.distance-label{paint-order:stroke;stroke:var(--paper-2);stroke-width:5;fill:var(--line);font:700 13px "Courier New",monospace}.city-label{paint-order:stroke;stroke:var(--paper-2);stroke-width:6;fill:var(--focus);font:700 16px "Courier New",monospace}.marker{cursor:pointer}.marker.context{opacity:.45}.marker.active .marker-box{fill:#f5c542}.marker-halo{fill:rgba(255,250,240,.82);stroke:rgba(49,61,76,.3);stroke-width:1}.marker-box{fill:var(--marker);stroke:var(--line);stroke-width:2}.marker-num{fill:var(--paper-2);font:700 16px "Courier New",monospace}.poi-label{paint-order:stroke;stroke:var(--paper-2);stroke-width:5;fill:var(--ink);font:700 14px "Courier New",monospace}.poi-day{paint-order:stroke;stroke:var(--paper-2);stroke-width:4;fill:var(--muted);font:700 11px "Courier New",monospace}.scale-bar line{stroke:var(--line);stroke-width:3}.scale-bar text{fill:var(--line);font:700 13px "Courier New",monospace}
        .stats-bar{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid var(--line)}.stat-item{padding:12px;border-right:2px solid var(--line);background:var(--paper-2)}.stat-item:last-child{border-right:0}.stat-item span{display:block;color:var(--muted);font-size:11px}.stat-item strong{display:block;margin-top:5px;font-size:18px}.side-panel{display:grid;gap:0}.panel-section{box-shadow:none;border-width:0 0 2px 0;padding:14px}.panel-section:last-child{border-bottom:0}.itinerary-list{display:grid;gap:12px}.day-block{display:grid;gap:6px}.day-summary{color:var(--muted);font-size:12px;line-height:1.4}.schedule-item{width:100%;display:grid;grid-template-columns:28px 1fr;gap:10px;text-align:left;border:2px solid var(--line);background:var(--paper-2);padding:8px;cursor:pointer}.schedule-item.active{background:#f5c542}.schedule-item.focus-city{opacity:.45}.schedule-item.in-city{opacity:1}.schedule-index{display:grid;place-items:center;width:26px;height:26px;background:var(--marker);color:var(--paper-2);border:2px solid var(--line);font-weight:700}.schedule-item strong{display:block;font-size:13px}.schedule-item small{display:block;color:var(--muted);font-size:11px;margin-top:3px}.poi-card{display:grid;gap:8px}.empty-state{color:var(--muted);font-size:13px}.poi-meta{margin:0;color:var(--muted);font-size:12px}.poi-actions{display:flex;gap:8px;flex-wrap:wrap}.poi-actions a{border:2px solid var(--line);background:#fffaf0;color:var(--ink);padding:6px 8px;text-decoration:none;font-weight:700}.source-note{color:var(--muted);font-size:11px;line-height:1.45}.poster-tools{display:grid;gap:14px}.poster-controls,.notes-editor{display:grid;gap:10px}.inline-controls{display:grid;grid-template-columns:minmax(0,1fr) 150px;gap:8px}.field-label{display:grid;gap:6px;color:var(--muted);font-size:12px;font-weight:700}select,textarea{width:100%;border:2px solid var(--line);border-radius:4px;background:#fffaf0;color:var(--ink);padding:8px}textarea{min-height:72px;resize:vertical}.poster-bg{fill:#f6ecd9}.poster-frame{fill:#fffaf0;stroke:#313d4c;stroke-width:4}.poster-kicker{fill:#7a3e9d;font:700 22px "Courier New",monospace}.poster-title{fill:#26313d;font:700 42px "Courier New",monospace}.poster-meta{fill:#697386;font:700 20px "Courier New",monospace}
        @media(max-width:1000px){.workspace{grid-template-columns:1fr}.side-panel{grid-template-columns:1fr}.stats-bar{grid-template-columns:repeat(2,1fr)}}@media(max-width:620px){.app-shell{padding:12px}.topbar{display:block}.map-toolbar{display:block}.city-pills{margin-top:10px}.stats-bar{grid-template-columns:1fr}.inline-controls{grid-template-columns:1fr}}
      `;
    }

    function initViewer() {
      const trip = JSON.parse(document.getElementById("trip-data").textContent);
      const stops = flattenStops(trip);
      const storageKey = `PixelTravelMap:${trip.trip_title}:${trip.start_date}:${trip.end_date}`;
      let currentStopIndex = 0;
      let tripNotes = loadTripNotes();
      const cityPills = document.getElementById("city-pills");
      cityPills.innerHTML = `<button class="city-pill active" type="button" data-view="overview">总览</button>` + [...new Set(stops.map(stop => stop.city))].sort().map(city => `<button class="city-pill" type="button" data-view="${esc(city)}">${esc(city)}</button>`).join("");
      document.getElementById("map-container").innerHTML = renderMapSvg(trip, true);
      document.getElementById("stats-bar").innerHTML = renderStatsHtml(trip);
      document.getElementById("itinerary-list").innerHTML = renderItineraryHtml(trip);
      const daySelect = document.getElementById("poster-day-select");
      daySelect.innerHTML = trip.days.map(day => `<option value="${day.day}">Day ${day.day} · ${esc(day.date)}</option>`).join("");
      const tripNote = document.getElementById("trip-note");
      const dayNote = document.getElementById("day-note");
      const stopNote = document.getElementById("stop-note");
      const card = document.getElementById("poi-card");
      const viewLabel = document.getElementById("view-label");
      function markers() { return Array.from(document.querySelectorAll(".marker[data-stop-index]")); }
      function scheduleItems() { return Array.from(document.querySelectorAll(".schedule-item")); }
      function cityButtons() { return Array.from(document.querySelectorAll(".city-pill")); }
      function loadTripNotes() {
        try {
          const parsed = JSON.parse(localStorage.getItem(storageKey) || "{}");
          return { trip: parsed.trip || "", days: parsed.days || {}, stops: parsed.stops || {} };
        } catch {
          return { trip: "", days: {}, stops: {} };
        }
      }
      function saveTripNotes() { localStorage.setItem(storageKey, JSON.stringify(tripNotes)); }
      function selectedDayNumber() { return Number(daySelect.value || trip.days[0].day); }
      function syncNoteFields() {
        tripNote.value = tripNotes.trip || "";
        dayNote.value = tripNotes.days[selectedDayNumber()] || "";
        const stop = stops[currentStopIndex];
        stopNote.value = stop ? (tripNotes.stops[stopKey(stop)] || "") : "";
      }
      function showCard(index) {
        const stop = stops[index];
        currentStopIndex = index;
        if (daySelect) daySelect.value = String(stop.day);
        markers().forEach(marker => marker.classList.toggle("active", Number(marker.dataset.stopIndex) === index));
        scheduleItems().forEach(item => item.classList.toggle("active", Number(item.dataset.stopIndex) === index));
        card.innerHTML = renderPoiCardHtml(stop);
        syncNoteFields();
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
        document.querySelectorAll(".map-view").forEach(group => {
          group.style.display = group.dataset.view === view ? "block" : "none";
        });
        viewLabel.textContent = isOverview ? "总览地图" : `${view} detail view`;
        cityButtons().forEach(button => button.classList.toggle("active", button.dataset.view === view));
        scheduleItems().forEach(item => {
          item.classList.toggle("focus-city", !isOverview);
          item.classList.toggle("in-city", !isOverview && item.dataset.city === view);
        });
        if (!isOverview) {
          const first = scheduleItems().find(item => item.dataset.city === view);
          if (first) showCard(Number(first.dataset.stopIndex));
        }
        bindMarkers();
      }
      scheduleItems().forEach(item => {
        item.addEventListener("click", () => {
          showView(item.dataset.city);
          showCard(Number(item.dataset.stopIndex));
        });
      });
      cityButtons().forEach(button => button.addEventListener("click", () => showView(button.dataset.view)));
      document.getElementById("overview-button").addEventListener("click", () => showView("overview"));
      document.getElementById("download-html").addEventListener("click", () => {
        downloadText(`${fileSafe(trip.trip_title)}.html`, "<!doctype html>\n" + document.documentElement.outerHTML, "text/html;charset=utf-8");
      });
      tripNote.addEventListener("input", () => { tripNotes.trip = tripNote.value; saveTripNotes(); });
      dayNote.addEventListener("input", () => { tripNotes.days[selectedDayNumber()] = dayNote.value; saveTripNotes(); });
      stopNote.addEventListener("input", () => {
        const stop = stops[currentStopIndex];
        if (stop) {
          tripNotes.stops[stopKey(stop)] = stopNote.value;
          saveTripNotes();
        }
      });
      daySelect.addEventListener("change", syncNoteFields);
      document.getElementById("clear-notes").addEventListener("click", () => {
        if (!confirm("清空当前浏览器保存的旅行备注？")) return;
        tripNotes = { trip: "", days: {}, stops: {} };
        localStorage.removeItem(storageKey);
        syncNoteFields();
      });
      document.getElementById("download-overview-poster").addEventListener("click", () => {
        downloadSvg(`${fileSafe(trip.trip_title)}-overview-poster.svg`, renderOverviewPosterSvgForTrip(trip));
      });
      document.getElementById("download-day-poster").addEventListener("click", () => {
        downloadSvg(`${fileSafe(trip.trip_title)}-day-${selectedDayNumber()}-briefing.svg`, renderDayPosterSvgForTrip(trip, selectedDayNumber(), tripNotes));
      });
      document.getElementById("download-record-poster").addEventListener("click", () => {
        downloadSvg(`${fileSafe(trip.trip_title)}-travel-record-poster.svg`, renderRecordPosterSvgForTrip(trip, tripNotes));
      });
      bindMarkers();
      if (stops.length) showCard(0);
      syncNoteFields();
    }

    function updateDownloads(enabled) {
      ["download-json", "download-map-html", "download-overview-poster", "download-day-poster", "download-record-poster"].forEach(id => {
        document.getElementById(id).disabled = !enabled;
      });
      posterDaySelect.disabled = !enabled;
    }

    function renderActivePreview() {
      if (!activeTrip) return;
      mapPreview.innerHTML = renderMapSvg(activeTrip, false);
      summaryGrid.innerHTML = renderStatsHtml(activeTrip);
      previewItinerary.innerHTML = renderPreviewItinerary(activeTrip);
      posterDaySelect.innerHTML = activeTrip.days.map(day => `<option value="${day.day}">Day ${day.day} · ${esc(day.date)}</option>`).join("");
      updateDownloads(true);
    }

    async function readDocxText(file) {
      if (!file.name.toLowerCase().endsWith(".docx")) {
        throw new Error("只支持 .docx 文件。");
      }
      const buffer = await file.arrayBuffer();
      const entry = findZipEntry(buffer, "word/document.xml");
      if (!entry) throw new Error("没有在 .docx 中找到正文 XML。");
      const bytes = await inflateZipEntry(entry);
      const xml = new TextDecoder("utf-8").decode(bytes);
      return documentXmlToText(xml);
    }

    function findZipEntry(buffer, wantedName) {
      const view = new DataView(buffer);
      let eocd = -1;
      for (let offset = view.byteLength - 22; offset >= Math.max(0, view.byteLength - 66000); offset -= 1) {
        if (view.getUint32(offset, true) === 0x06054b50) {
          eocd = offset;
          break;
        }
      }
      if (eocd < 0) throw new Error("无法识别 .docx zip 结构。");
      const entries = view.getUint16(eocd + 10, true);
      let offset = view.getUint32(eocd + 16, true);
      for (let index = 0; index < entries; index += 1) {
        if (view.getUint32(offset, true) !== 0x02014b50) break;
        const method = view.getUint16(offset + 10, true);
        const compressedSize = view.getUint32(offset + 20, true);
        const nameLength = view.getUint16(offset + 28, true);
        const extraLength = view.getUint16(offset + 30, true);
        const commentLength = view.getUint16(offset + 32, true);
        const localHeaderOffset = view.getUint32(offset + 42, true);
        const name = new TextDecoder("utf-8").decode(new Uint8Array(buffer, offset + 46, nameLength));
        if (name === wantedName) {
          if (view.getUint32(localHeaderOffset, true) !== 0x04034b50) throw new Error("正文文件头损坏。");
          const localNameLength = view.getUint16(localHeaderOffset + 26, true);
          const localExtraLength = view.getUint16(localHeaderOffset + 28, true);
          const dataStart = localHeaderOffset + 30 + localNameLength + localExtraLength;
          return {
            method,
            compressed: buffer.slice(dataStart, dataStart + compressedSize)
          };
        }
        offset += 46 + nameLength + extraLength + commentLength;
      }
      return null;
    }

    async function inflateZipEntry(entry) {
      if (entry.method === 0) return new Uint8Array(entry.compressed);
      if (entry.method !== 8) throw new Error("暂不支持此 .docx 压缩方式。");
      if (!("DecompressionStream" in window)) {
        throw new Error("当前浏览器不支持直接解析 .docx，请复制 Word 正文到文本框。");
      }
      const compressed = new Uint8Array(entry.compressed);
      try {
        return await inflateWithFormat(compressed, "deflate-raw");
      } catch {
        return await inflateWithFormat(compressed, "deflate");
      }
    }

    async function inflateWithFormat(bytes, format) {
      const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream(format));
      return new Uint8Array(await new Response(stream).arrayBuffer());
    }

    function documentXmlToText(xml) {
      const withBreaks = xml
        .replace(/<w:tab\/>/g, "\t")
        .replace(/<w:br\/>/g, "\n")
        .replace(/<\/w:p>/g, "\n")
        .replace(/<[^>]+>/g, "");
      const textarea = document.createElement("textarea");
      textarea.innerHTML = withBreaks;
      return textarea.value.replace(/\n{3,}/g, "\n\n").trim();
    }

    document.getElementById("load-sample").addEventListener("click", () => {
      textInput.value = document.getElementById("sample-trip-text").textContent.trim();
      setStatus(parseStatus, "已填入示例；其中第 2 天仍缺少坐标，可体验补全流程。", "ok");
    });

    document.getElementById("parse-input").addEventListener("click", () => {
      try {
        draft = parseDraftFromText(textInput.value);
        renderDraft();
        activeTrip = null;
        updateDownloads(false);
        mapPreview.innerHTML = `<div class="empty">草稿已生成，补齐坐标后点击“生成预览”。</div>`;
        summaryGrid.innerHTML = "";
        previewItinerary.innerHTML = "";
        const stopCount = draft.days.reduce((sum, day) => sum + day.stops.length, 0);
        setStatus(parseStatus, `已解析 ${draft.days.length} 天、${stopCount} 个地点。`, "ok");
      } catch (error) {
        setStatus(parseStatus, error.message, "error");
      }
    });

    document.getElementById("docx-input").addEventListener("change", async event => {
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      try {
        setStatus(docxStatus, "正在读取 Word 正文...");
        const text = await readDocxText(file);
        textInput.value = text;
        setStatus(docxStatus, `已读取 ${file.name}，可继续解析。`, "ok");
      } catch (error) {
        setStatus(docxStatus, error.message, "error");
      }
    });

    draftTable.addEventListener("input", event => {
      const target = event.target;
      const dayEditor = target.closest("[data-day-index]");
      if (!dayEditor || !target.dataset.kind) return;
      const dayIndex = Number(dayEditor.dataset.dayIndex);
      if (target.dataset.kind === "day") {
        const field = target.dataset.field;
        draft.days[dayIndex][field] = field === "day" ? Number(target.value) : target.value;
      } else {
        const row = target.closest("[data-stop-index]");
        const stopIndex = Number(row.dataset.stopIndex);
        draft.days[dayIndex].stops[stopIndex][target.dataset.field] = target.value;
      }
      activeTrip = null;
      updateDownloads(false);
    });

    draftTable.addEventListener("click", event => {
      const action = event.target.dataset.action;
      if (!action) return;
      const dayIndex = Number(event.target.dataset.dayIndex);
      if (action === "add-stop") addStop(dayIndex);
      if (action === "remove-stop") {
        const stopIndex = Number(event.target.dataset.stopIndex);
        draft.days[dayIndex].stops.splice(stopIndex, 1);
        renderDraft();
      }
    });

    [titleInput, transportInput, startInput, endInput].forEach(input => {
      input.addEventListener("input", () => {
        syncMetaToDraft();
        activeTrip = null;
        updateDownloads(false);
      });
    });

    document.getElementById("add-day").addEventListener("click", () => {
      syncMetaToDraft();
      const nextDay = draft.days.length ? Math.max(...draft.days.map(day => Number(day.day) || 1)) + 1 : 1;
      draft.days.push({
        day: nextDay,
        date: addDays(draft.start_date, nextDay - 1),
        summary: "待补全行程",
        stops: []
      });
      renderDraft();
    });

    document.getElementById("build-preview").addEventListener("click", () => {
      try {
        activeTrip = buildTripFromDraft();
        renderActivePreview();
        setStatus(validationStatus, "校验通过，可以下载 artifact。", "ok");
      } catch (error) {
        setStatus(validationStatus, error.message, "error");
        activeTrip = null;
        updateDownloads(false);
      }
    });

    document.getElementById("download-json").addEventListener("click", () => {
      if (!activeTrip) return;
      downloadText(`${fileSafe(activeTrip.trip_title)}.json`, JSON.stringify(activeTrip, null, 2), "application/json;charset=utf-8");
    });

    document.getElementById("download-map-html").addEventListener("click", () => {
      if (!activeTrip) return;
      downloadText(`${fileSafe(activeTrip.trip_title)}.html`, renderViewerHtml(activeTrip), "text/html;charset=utf-8");
    });

    document.getElementById("download-overview-poster").addEventListener("click", () => {
      if (!activeTrip) return;
      downloadSvg(`${fileSafe(activeTrip.trip_title)}-overview-poster.svg`, renderOverviewPosterSvgForTrip(activeTrip));
    });

    document.getElementById("download-day-poster").addEventListener("click", () => {
      if (!activeTrip) return;
      downloadSvg(`${fileSafe(activeTrip.trip_title)}-day-${posterDaySelect.value}-briefing.svg`, renderDayPosterSvgForTrip(activeTrip, Number(posterDaySelect.value)));
    });

    document.getElementById("download-record-poster").addEventListener("click", () => {
      if (!activeTrip) return;
      downloadSvg(`${fileSafe(activeTrip.trip_title)}-travel-record-poster.svg`, renderRecordPosterSvgForTrip(activeTrip));
    });

    renderDraft();
    updateDownloads(false);
  </script>
</body>
</html>
"""


def write_builder_html(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_builder_html(), encoding="utf-8", newline="\n")
