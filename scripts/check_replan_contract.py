from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _function_source(script: str, name: str) -> str:
    match = re.search(rf"\bfunction\s+{re.escape(name)}\s*\(", script)
    if not match:
        raise ValueError(f"missing JavaScript function: {name}")
    start = match.start()
    brace = script.find("{", match.end())
    depth = 0
    quote: str | None = None
    escaped = False
    template_depth = 0
    for index in range(brace, len(script)):
        char = script[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif quote == "`" and char == "$" and script[index + 1 : index + 2] == "{":
                template_depth += 1
            elif char == quote and template_depth == 0:
                quote = None
            elif quote == "`" and char == "}" and template_depth:
                template_depth -= 1
            continue
        if char in "\"'`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return script[start : index + 1]
    raise ValueError(f"unterminated JavaScript function: {name}")


def check_replan_contract(html_path: Path) -> list[str]:
    if not html_path.exists():
        return [f"missing artifact: {html_path}"]
    html = html_path.read_text(encoding="utf-8")
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, flags=re.DOTALL)
    if not scripts:
        return ["builder has no inline JavaScript"]
    script = max(scripts, key=len)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".js", encoding="utf-8", delete=False
    ) as handle:
        handle.write(script)
        syntax_path = Path(handle.name)
    try:
        syntax = subprocess.run(
            ["node", "--check", str(syntax_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
            check=False,
        )
    finally:
        syntax_path.unlink(missing_ok=True)
    if syntax.returncode:
        return [line for line in (syntax.stderr or syntax.stdout).splitlines() if line]

    sample_match = re.search(
        r'<script id="sample-trip-text" type="text/plain">(.*?)</script>',
        html,
        flags=re.DOTALL,
    )
    if not sample_match:
        return ["builder has no embedded demo text"]
    sample_json = json.dumps(sample_match.group(1).strip(), ensure_ascii=False)
    smoke_prelude = f"""
const elements = new Map();
function makeElement(id) {{
  const handlers = {{}};
  const element = {{
    id, handlers, value: "", textContent: id === "sample-trip-text" ? {sample_json} : "",
    innerHTML: "", hidden: false, disabled: false, checked: false, open: false,
    dataset: {{}}, options: [], files: [],
    classList: {{ toggle() {{}}, add() {{}}, remove() {{}} }},
    addEventListener(type, callback) {{ (handlers[type] ||= []).push(callback); }},
    querySelectorAll() {{ return []; }},
    querySelector() {{ return makeElement(id + "-child"); }},
    closest() {{ return null; }},
    scrollIntoView() {{}},
    focus() {{}},
    appendChild() {{}},
    remove() {{}},
    click() {{}}
  }};
  return element;
}}
globalThis.document = {{
  getElementById(id) {{
    if (!elements.has(id)) elements.set(id, makeElement(id));
    return elements.get(id);
  }},
  querySelector() {{ return makeElement("query"); }},
  querySelectorAll() {{ return []; }},
  createElement(id) {{ return makeElement(id); }},
  body: makeElement("body"),
  documentElement: {{ outerHTML: "<html></html>" }},
  title: ""
}};
const storage = new Map();
globalThis.localStorage = {{
  getItem(key) {{ return storage.has(key) ? storage.get(key) : null; }},
  setItem(key, value) {{ storage.set(key, String(value)); }},
  removeItem(key) {{ storage.delete(key); }}
}};
globalThis.location = {{ hash: "", href: "file:///index.html" }};
globalThis.history = {{ replaceState(_a, _b, hash) {{ location.hash = hash; }} }};
globalThis.window = {{ addEventListener() {{}} }};
globalThis.confirm = () => true;
"""
    smoke_postlude = """
function clickHandler(id) {
  const handlers = elements.get(id)?.handlers?.click || [];
  if (handlers.length !== 1) throw new Error(`expected one click handler for ${id}, got ${handlers.length}`);
  handlers[0]({ target: elements.get(id) });
}
const migratedLegacy = migrateStoredTripCopy({
  trip_title: "川北九寨与重庆 7 日旅行（脱敏演示）",
  days: [{ stops: [{ source: "sanitized_demo_itinerary" }] }]
});
if (migratedLegacy.trip_title.includes("脱敏") || migratedLegacy.days[0].stops[0].source !== "curated_demo_itinerary") {
  throw new Error("legacy stored demo state was not migrated");
}
clickHandler("load-sample");
if (!activeTrip || activeTrip.days.length !== 7) throw new Error("demo did not create a seven-day active trip");
if (!activeTrip.trip_title.includes("川北九寨与重庆")) throw new Error("demo title was overwritten by the initial form state");
if (!flattenStops(activeTrip).some(stop => stop.name === "乐山大佛")) throw new Error("demo route should initially contain Leshan");
const initialStops = flattenStops(activeTrip);
const initialViews = buildMapViews(initialStops);
if (initialViews[0].stops.length !== new Set(initialStops.map(stop => stop.city)).size) {
  throw new Error("overview map should render one hub per city");
}
if (!initialViews.some(view => view.key === "day-6")) throw new Error("daily map view is missing");
for (const view of initialViews) {
  const labels = Object.values(layoutMapLabels(view.contextStops, view.points, MAP_W, MAP_H, view.mode));
  for (let i = 0; i < labels.length; i += 1) {
    for (let j = i + 1; j < labels.length; j += 1) {
      if (boxesOverlap(labels[i], labels[j], 0)) {
        throw new Error(`map labels overlap in ${view.key}`);
      }
    }
  }
}
clickHandler("open-disruption");
if (!pendingProposal) throw new Error("demo disruption did not produce a proposal: " + elements.get("replan-status").textContent);
clickHandler("apply-replan");
if (flattenStops(activeTrip).some(stop => stop.name === "乐山大佛")) throw new Error("applied route should skip Leshan");
if (!flattenStops(activeTrip).some(stop => stop.name === "成都东站前往重庆" && stop.reservation_required)) {
  throw new Error("fixed Day 6 train was not preserved");
}
if (elements.get("map-preview").innerHTML.includes("乐山大佛")) throw new Error("map preview did not refresh from activeTrip");
if (renderViewerHtml(activeTrip).includes("乐山大佛")) throw new Error("downloaded viewer did not use activeTrip");
const overviewPoster = renderOverviewPosterSvgForTrip(activeTrip);
const dayPoster = renderDayPosterSvgForTrip(activeTrip, 5);
if (!overviewPoster.includes("poster-paper-pattern") || !overviewPoster.includes("城市方位经视觉优化")) {
  throw new Error("overview poster did not use the ancient atlas layout");
}
const compactRows = [...overviewPoster.matchAll(/class="compact-row" transform="translate\\(120,(\\d+)\\)">\\s*<rect width="1360" height="(\\d+)"/g)]
  .map(match => ({ y: Number(match[1]), height: Number(match[2]) }));
if (compactRows.length !== activeTrip.days.length) throw new Error("overview poster is missing compact itinerary rows");
for (let index = 1; index < compactRows.length; index += 1) {
  if (compactRows[index - 1].y + compactRows[index - 1].height >= compactRows[index].y) {
    throw new Error("overview poster itinerary rows overlap");
  }
}
if (compactRows.at(-1).y + compactRows.at(-1).height > 1065) throw new Error("overview poster itinerary exceeds the page");
if (dayPoster.includes("乐山大佛")) throw new Error("daily briefing did not use activeTrip");
if (!dayPoster.includes("当天地点独立放大")) throw new Error("daily poster did not use an independent map layout");
clickHandler("map-view-button");
if (location.hash !== "#map") throw new Error("map view hash was not updated");
clickHandler("plan-view-button");
if (location.hash !== "#plan") throw new Error("applied result should stay in the plan view");
if (!localStorage.getItem(REPLAN_LAST_KEY)) throw new Error("active trip state was not persisted");
clickHandler("undo-replan");
if (!flattenStops(activeTrip).some(stop => stop.name === "乐山大佛")) throw new Error("single-step undo did not restore Leshan");
console.log("RUNTIME_OK");
"""
    smoke_source = f"{smoke_prelude}\n{script}\n{smoke_postlude}"
    with tempfile.NamedTemporaryFile(
        "w", suffix=".js", encoding="utf-8", delete=False
    ) as handle:
        handle.write(smoke_source)
        smoke_path = Path(handle.name)
    try:
        smoke = subprocess.run(
            ["node", str(smoke_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
            check=False,
        )
    finally:
        smoke_path.unlink(missing_ok=True)
    if smoke.returncode:
        return [line for line in (smoke.stderr or smoke.stdout).splitlines() if line]

    names = [
        "clone",
        "minutesFromTime",
        "timeFromMinutes",
        "flattenStops",
        "checkedLockIds",
        "proposalItem",
        "buildReplanProposal",
    ]
    try:
        functions = "\n\n".join(_function_source(script, name) for name in names)
    except ValueError as exc:
        return [str(exc)]

    fixture = {
        "schema_version": "1.0",
        "trip_title": "replan-test",
        "start_date": "2026-10-16",
        "end_date": "2026-10-17",
        "travelers": ["traveler"],
        "transport": "mixed",
        "style_theme": "pastel-pixel",
        "lang": "zh-CN",
        "days": [
            {
                "day": 5,
                "date": "2026-10-16",
                "summary": "茂县经乐山前往成都",
                "cautions": "",
                "stops": [
                    {
                        "id": "maoxian",
                        "name": "茂县出发点",
                        "arrival_time": "08:00",
                        "duration_min": 30,
                        "transit_buffer_min": 30,
                        "reservation_required": False,
                    },
                    {
                        "id": "leshan",
                        "name": "乐山大佛",
                        "arrival_time": "13:00",
                        "duration_min": 180,
                        "transit_buffer_min": 40,
                        "reservation_required": False,
                    },
                    {
                        "id": "chengdu",
                        "name": "成都抵达点",
                        "arrival_time": "18:30",
                        "duration_min": 30,
                        "transit_buffer_min": 30,
                        "reservation_required": False,
                    },
                ],
            },
            {
                "day": 6,
                "date": "2026-10-17",
                "summary": "成都前往重庆",
                "cautions": "",
                "stops": [
                    {
                        "id": "train",
                        "name": "成都东站前往重庆",
                        "arrival_time": "15:00",
                        "duration_min": 120,
                        "transit_buffer_min": 45,
                        "reservation_required": True,
                        "reservation_time": "15:00",
                    },
                    {
                        "id": "chongqing",
                        "name": "重庆夜游",
                        "arrival_time": "18:00",
                        "duration_min": 90,
                        "transit_buffer_min": 20,
                        "reservation_required": False,
                    },
                ],
            },
        ],
    }
    harness = f"""
{functions}
let activeTrip = {json.dumps(fixture, ensure_ascii=False)};
let lockIds = ["train"];
const lockList = {{ querySelectorAll: () => lockIds.map(value => ({{ value }})) }};
const disruptionType = {{ value: "delay" }};
const disruptionDay = {{ value: "5" }};
const disruptionStop = {{ value: "leshan" }};
const disruptionDelay = {{ value: "180" }};
function assert(value, message) {{ if (!value) throw new Error(message); }}

const daySixBefore = JSON.stringify(activeTrip.days[1]);
let proposal = buildReplanProposal();
assert(!proposal.trip.days[0].stops.some(stop => stop.id === "leshan"), "delay should skip Leshan");
assert(proposal.trip.days[0].stops.some(stop => stop.id === "chengdu"), "delay should keep Chengdu");
assert(JSON.stringify(proposal.trip.days[1]) === daySixBefore, "day 6 must remain unchanged");
assert(proposal.diffs.some(item => item.kind === "keep" && item.label.includes("成都东站")), "fixed train should be explained");

for (const type of ["closure", "weather"]) {{
  disruptionType.value = type;
  disruptionStop.value = "leshan";
  proposal = buildReplanProposal();
  assert(!proposal.trip.days[0].stops.some(stop => stop.id === "leshan"), type + " should skip selected stop");
}}

disruptionType.value = "fatigue";
proposal = buildReplanProposal();
assert(!proposal.trip.days[0].stops.some(stop => stop.id === "chengdu"), "fatigue should remove final flexible stop");

disruptionType.value = "closure";
disruptionDay.value = "6";
disruptionStop.value = "train";
let blocked = false;
try {{ buildReplanProposal(); }} catch (error) {{ blocked = /固定安排/.test(error.message); }}
assert(blocked, "locked stop change should block");

disruptionType.value = "delay";
disruptionDay.value = "5";
disruptionStop.value = "leshan";
disruptionDelay.value = "60";
activeTrip.days[0].stops[1].arrival_time = null;
blocked = false;
try {{ buildReplanProposal(); }} catch (error) {{ blocked = /缺少时间/.test(error.message); }}
assert(blocked, "missing time should block");
console.log("OK");
"""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".js", encoding="utf-8", delete=False
    ) as handle:
        handle.write(harness)
        temp_path = Path(handle.name)
    try:
        result = subprocess.run(
            ["node", str(temp_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
            check=False,
        )
    finally:
        temp_path.unlink(missing_ok=True)
    if result.returncode:
        return [line for line in (result.stderr or result.stdout).splitlines() if line]
    return []


def main() -> int:
    failures = check_replan_contract(ROOT / "dist" / "index.html")
    if failures:
        print("FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
