import fs from "node:fs";
import vm from "node:vm";

const [, , sourcePath, outputPath] = process.argv;
if (!sourcePath || !outputPath) {
  throw new Error("Usage: node render_viewer_from_builder.mjs <builder-html> <viewer-html>");
}

const sourceHtml = fs.readFileSync(sourcePath, "utf8");
const scripts = [...sourceHtml.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(match => match[1]);
const runtime = scripts.sort((a, b) => b.length - a.length)[0];
if (!runtime) throw new Error("Builder runtime not found.");

const elements = new Map();
function makeElement(id) {
  const element = {
    id,
    value: "",
    textContent: "",
    innerHTML: "",
    hidden: false,
    disabled: false,
    checked: false,
    open: false,
    dataset: {},
    options: [],
    files: [],
    classList: { toggle() {}, add() {}, remove() {} },
    addEventListener() {},
    querySelectorAll() { return []; },
    querySelector() { return makeElement(`${id}-child`); },
    closest() { return null; },
    scrollIntoView() {},
    focus() {},
    appendChild() {},
    remove() {},
    click() {}
  };
  return element;
}

globalThis.document = {
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, makeElement(id));
    return elements.get(id);
  },
  querySelector() { return makeElement("query"); },
  querySelectorAll() { return []; },
  createElement(id) { return makeElement(id); },
  body: makeElement("body"),
  documentElement: { outerHTML: "<html></html>" },
  title: ""
};
globalThis.localStorage = {
  getItem() { return null; },
  setItem() {},
  removeItem() {}
};
globalThis.location = { hash: "", href: "file:///index.html" };
globalThis.history = { replaceState(_a, _b, hash) { location.hash = hash; } };
globalThis.window = { addEventListener() {} };
globalThis.confirm = () => true;

vm.runInThisContext(runtime, { filename: sourcePath });

const placeholder = {
  schema_version: "1.0",
  trip_title: "PixelTravelMap 分享查看器",
  start_date: "2026-01-01",
  end_date: "2026-01-01",
  travelers: ["traveler"],
  budget_cny: null,
  transport: "unknown",
  style_theme: "ancient-atlas",
  lang: "zh-CN",
  days: [{
    day: 1,
    date: "2026-01-01",
    summary: "请通过 PixelTravelMap 生成的分享链接打开此页面。",
    meeting_time: null,
    meeting_point: "",
    cautions: "",
    stops: [{
      id: "share-viewer-placeholder",
      name: "等待分享数据",
      name_en: null,
      city: "PixelTravelMap",
      country: "WEB",
      lat: 0,
      lon: 0,
      crs: "wgs84",
      category: "transit",
      duration_min: 0,
      arrival_time: null,
      reservation_required: false,
      reservation_time: null,
      reservation_reference: "",
      transit_buffer_min: 0,
      cautions: "",
      description: "此页面需要分享链接中的行程数据。",
      notes: "请让行程组织者重新复制分享链接。",
      source: "PixelTravelMap",
      source_url: null,
      official_url: null,
      navigation_url: null,
      info_missing: false
    }]
  }]
};

const viewerHtml = globalThis.renderViewerHtml(placeholder);
fs.writeFileSync(outputPath, viewerHtml, "utf8");
