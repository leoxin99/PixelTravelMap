# PixelTravelMap Interview Narrative

## 30-Second Version

PixelTravelMap is a portfolio MVP for an AI travel artifact generator. The user
describes a trip in natural language, the system turns it into structured
itinerary JSON, validates the schema, and renders offline artifacts: an
interactive HTML atlas plus a one-page SVG poster with coordinate-projected
POIs, route distance labels, itinerary panels, source notes, and artifact
quality checks.

The HTML artifact also works as a lightweight trip companion: before the trip,
it can generate an overall poster and per-day briefing posters for companions;
during the trip, notes are saved locally in the browser; after the trip, those
notes can be turned into a travel record poster.

## Why Start With an HTML Artifact

I intentionally did not start with a full SaaS. The risky assumption is whether
the output itself is valuable: can a user get a beautiful, shareable, offline
travel artifact from one description? HTML and SVG files validate that core
loop quickly without accounts, databases, deployment, billing, or map-provider
licensing.

This is also a good fit for AI application engineering because the boundary is
clear:

```text
unstructured input -> structured JSON -> deterministic renderer -> evaluable artifact
```

## How To Keep LLM Output Stable

The project treats schema as the contract, not the prompt as the contract.

- Define required fields and value ranges in `trip.schema.json`.
- Ask the LLM for structured output only.
- Validate JSON before rendering.
- Reject or repair invalid output with structured error messages.
- Mark missing POI facts as `info_missing=true` instead of inventing facts.
- Keep renderer deterministic so layout bugs are separate from model mistakes.

In phase 1, the parser is local and heuristic so the project is runnable without
API keys. The same parser boundary can later be replaced by OpenAI/Claude
structured output.

## How To Evaluate Usefulness

The MVP can be evaluated without subjective vibes:

- JSON validity rate.
- Required-field completion rate.
- POI source coverage.
- Artifact open rate for HTML and SVG.
- Offline compliance: no external scripts/styles/fetch.
- Interaction success: marker click, itinerary click, city detail view, download.
- Poster success: overall trip, daily briefing, and travel record posters download from the HTML artifact.
- Note persistence: browser-local trip/day/POI notes survive refresh and appear in the record poster.
- Map readability: POI labels, relative direction, scale bar, and segment distance labels are legible.
- Human review: does the itinerary map communicate the trip clearly?

## Product Tradeoffs

Chose:

- local CLI before web app;
- static/demo POI before live APIs;
- offline coordinate-projected SVG/HTML artifacts before precise navigation;
- validation and quality checks before extra themes.

Deferred:

- accounts and collaboration;
- real-time maps;
- official POI fetching;
- PNG export;
- PDF/screenshot import.

## Resume Description

English:

Built a local PixelTravelMap MVP that converts natural-language trip plans into
validated itinerary JSON and renders offline HTML atlas and SVG poster artifacts
with coordinate-projected POIs, route distances, citations, itinerary panels, and artifact quality checks.

Chinese:

完成 PixelTravelMap 本地 MVP，将自然语言旅行描述转化为可校验 itinerary JSON，并生成离线可用的 HTML atlas 和一页式 SVG 海报，支持坐标投影 POI、路线距离、来源标注、日程面板和 artifact 质量检查。
