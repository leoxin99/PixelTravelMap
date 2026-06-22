# PixelTravelMap Phase 1 Plan

## Goal

Build a local, demonstrable MVP:

```text
travel description -> structured itinerary JSON -> offline pixel map HTML
```

The goal is not to build a large SaaS. The goal is to show AI application
engineering judgment: schema design, structured output constraints, front-end
artifact rendering, error handling, and eval-minded delivery.

## MVP Boundary

P0:

- Natural-language input for curated demo scenarios.
- Stable itinerary schema.
- JSON validation before rendering.
- Self-contained HTML artifact.
- Inline SVG map with route, markers, itinerary panel, POI card, source notes, city drill-down/filter.
- Local quality checks.

Out of scope for phase 1:

- User accounts.
- Cloud save/share links.
- Online Mapbox/Gaode tiles.
- Live POI APIs.
- PDF/screenshot/multimodal import.
- PNG export.
- Collaboration.

## Technical Route

1. Define `trip.schema.json` as the stable contract.
2. Keep `parser.py` replaceable:
   - phase 1: heuristic parser for demos;
   - next: LLM structured output with retry/repair against the same schema.
3. Validate before render:
   - required fields;
   - lat/lon ranges;
   - unique stop ids;
   - source coverage.
4. Render artifact with no runtime network dependency:
   - inline CSS;
   - inline JS;
   - inline SVG;
   - inline trip JSON.
5. Check artifact:
   - no external scripts/styles;
   - no fetch/XHR/import;
   - required interactive DOM nodes exist;
   - file size stays below target.

## Phase 1 Tasks

1. Schema and examples
   - Create `schemas/trip.schema.json`.
   - Create 3 inputs and expected JSON files.
   - Validate examples.

2. Renderer
   - Flatten itinerary stops.
   - Project coordinates into pixel-grid SVG.
   - Draw route, markers, city routes, and stats.
   - Add marker and itinerary click interactions.
   - Add city filter/drill-down and return overview.
   - Add download button.

3. Quality checks
   - Validate itinerary JSON.
   - Check HTML artifact constraints.
   - Generate one demo artifact in `dist/`.

4. Documentation
   - README quickstart.
   - Interview narrative.
   - Explicit MVP tradeoffs.

## Acceptance Criteria

- `python scripts/validate_trip.py examples/expected/italy_france_switzerland_self_drive.json` returns `OK`.
- `python scripts/generate_map.py --input examples/inputs/italy_france_switzerland_self_drive.txt --output dist/italy_france_switzerland_demo.html` writes an HTML file.
- `python scripts/check_artifact.py dist/italy_france_switzerland_demo.html` returns `OK`.
- Generated HTML opens locally and contains clickable markers, itinerary items, detail card, city filters, and source notes.

## Next Phase

- Add an LLM parser adapter with strict JSON schema, repair retry, and fixture-based eval.
- Add static POI cache and source normalization.
- Add browser-based visual checks at 375px, 768px, and 1440px.
- Add PNG export after the HTML artifact is stable.
