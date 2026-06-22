# PixelTravelMap Interview Narrative

## 30-Second Version

PixelTravelMap is a portfolio MVP for an AI travel artifact generator. The user
describes a trip in natural language, the system turns it into structured
itinerary JSON, validates the schema, and renders a self-contained offline HTML
pixel map with clickable POIs, itinerary panels, source notes, and artifact
quality checks.

## Why Start With an HTML Artifact

I intentionally did not start with a full SaaS. The risky assumption is whether
the output itself is valuable: can a user get a beautiful, shareable, offline
travel artifact from one description? A single HTML file validates that core
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
- Artifact open rate.
- Offline compliance: no external scripts/styles/fetch.
- Interaction success: marker click, itinerary click, city filter, download.
- Human review: does the itinerary map communicate the trip clearly?

## Product Tradeoffs

Chose:

- local CLI before web app;
- static/demo POI before live APIs;
- offline SVG artifact before precise navigation;
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
validated itinerary JSON and renders a self-contained interactive pixel-map HTML
artifact with clickable POIs, citations, itinerary panels, and artifact quality checks.

Chinese:

完成 PixelTravelMap 本地 MVP，将自然语言旅行描述转化为可校验 itinerary JSON，并生成离线可用的自包含像素风交互地图 HTML，支持可点击 POI、来源标注、日程面板和 artifact 质量检查。
