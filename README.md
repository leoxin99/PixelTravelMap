# PixelTravelMap

PixelTravelMap is a portfolio MVP for an AI travel artifact generator. It turns
a natural-language trip description into validated itinerary JSON, then renders
self-contained offline artifacts: an interactive HTML atlas and a one-page SVG
poster with the map and full itinerary.

The project is intentionally small: no API keys, no backend, no map tile
provider, and no third-party runtime dependencies. The point is to show the
schema-first AI workflow and the deterministic artifact pipeline that would sit
behind a larger travel planning product.

## What To Open First

- Demo artifacts: `dist/italy_france_switzerland_demo.html`,
  `dist/italy_france_switzerland_demo_poster.svg`,
  `dist/japan_kansai_demo.html`, and `dist/beijing_family_demo.html`.
- Architecture and tradeoffs: [`docs/interview_narrative.md`](docs/interview_narrative.md).
- Publishing checklist: [`docs/publishing.md`](docs/publishing.md).

After GitHub Pages is enabled, the checked-in demo HTML files can be linked
directly from a resume or portfolio.

## Recruiter Snapshot

- **Problem:** turn a loose trip idea into a polished, shareable travel map.
- **Approach:** parse text into a stable itinerary schema, validate before
  rendering, then generate offline HTML and SVG artifacts.
- **AI engineering angle:** the local parser is a no-key fixture parser today,
  but it uses the same boundary an LLM structured-output adapter would use.
- **Quality bar:** schema validation, source coverage checks, offline artifact
  checks, and deterministic rendering.

## Demo Workflow

```text
natural-language trip text
  -> pixel_travel_map/parser.py
  -> itinerary JSON
  -> pixel_travel_map/quality.py
  -> pixel_travel_map/renderer.py
  -> self-contained HTML atlas + one-page SVG poster
  -> artifact checks
```

The generated HTML includes inline CSS, inline JavaScript, inline SVG, and the
trip JSON payload. The poster SVG is a single image file. Both are designed to
open directly from disk and work without network access.

## Quickstart

Requirements:

- Python 3.10 or newer
- No third-party Python packages

From the repository root:

```powershell
python scripts/validate_trip.py examples/expected/italy_france_switzerland_self_drive.json
python scripts/generate_map.py --input examples/inputs/italy_france_switzerland_self_drive.txt --output dist/italy_france_switzerland_demo.html --dump-json dist/italy_france_switzerland_demo.json --poster-svg dist/italy_france_switzerland_demo_poster.svg
python scripts/check_artifact.py dist/italy_france_switzerland_demo.html
python scripts/check_artifact.py dist/italy_france_switzerland_demo_poster.svg
python scripts/check_project.py
```

Then open the generated file in a browser:

```text
dist/italy_france_switzerland_demo.html
dist/italy_france_switzerland_demo_poster.svg
```

## Included Demo Scenarios

| Scenario | Natural-language input | Expected JSON | HTML artifact | SVG poster |
| --- | --- | --- | --- | --- |
| Italy, France, Switzerland self-drive | `examples/inputs/italy_france_switzerland_self_drive.txt` | `examples/expected/italy_france_switzerland_self_drive.json` | `dist/italy_france_switzerland_demo.html` | `dist/italy_france_switzerland_demo_poster.svg` |
| Japan Kansai city trip | `examples/inputs/japan_kansai_city_trip.txt` | `examples/expected/japan_kansai_city_trip.json` | `dist/japan_kansai_demo.html` | `dist/japan_kansai_demo_poster.svg` |
| Beijing family trip | `examples/inputs/beijing_family_trip.txt` | `examples/expected/beijing_family_trip.json` | `dist/beijing_family_demo.html` | `dist/beijing_family_demo_poster.svg` |

## Quality Gates

Run these before publishing or after changing the schema, parser, renderer, or
example data:

```powershell
python scripts/check_project.py
```

For one-off checks while developing:

```powershell
python scripts/validate_trip.py examples/expected/italy_france_switzerland_self_drive.json
python scripts/validate_trip.py examples/expected/japan_kansai_city_trip.json
python scripts/validate_trip.py examples/expected/beijing_family_trip.json
python scripts/check_artifact.py dist/italy_france_switzerland_demo.html
python scripts/check_artifact.py dist/italy_france_switzerland_demo_poster.svg
python scripts/check_artifact.py dist/japan_kansai_demo.html
python scripts/check_artifact.py dist/japan_kansai_demo_poster.svg
python scripts/check_artifact.py dist/beijing_family_demo.html
python scripts/check_artifact.py dist/beijing_family_demo_poster.svg
```

The artifact checkers reject external scripts, external stylesheets, remote SVG
resources, `fetch`, `XMLHttpRequest`, dynamic imports, missing required DOM
nodes, missing poster sections, and oversized files.

## Generate Your Own Map

For reusable custom trips, write natural-language input with explicit POI
coordinates. PixelTravelMap does not geocode place names online and does not
guess coordinates.

```text
标题：日本东京 3 日亲子游
日期：2026-07-01 到 2026-07-03
交通：public-transit

Day 1：东京塔和城市观景
- 东京塔 (lat:35.6586, lon:139.7454, city:Tokyo, country:JP, category:landmark, duration:90)
- 六本木之丘 (lat:35.6605, lon:139.7292, city:Tokyo, country:JP, category:viewpoint, duration:120)
```

Required fields for each stop: `lat`, `lon`, `city`, `country`, `category`, and
`duration`. Supported categories are `landmark`, `museum`, `food`, `hotel`,
`nature`, `transit`, `shopping`, `experience`, and `viewpoint`.

Generate HTML, JSON, and SVG from the sample custom input:

```powershell
python scripts/generate_map.py --input examples/inputs/tokyo_coordinate_trip.txt --output dist/tokyo_coordinate_demo.html --dump-json dist/tokyo_coordinate_demo.json --poster-svg dist/tokyo_coordinate_demo_poster.svg
```

The map uses latitude/longitude to preserve relative direction and approximate
straight-line distance. It is suitable for itinerary communication, not precise
road navigation.

## Repository Structure

```text
PixelTravelMap/
  .github/workflows/ci.yml      # GitHub Actions quality gate
  dist/                         # Checked-in offline HTML and SVG demo artifacts
  docs/                         # Interview narrative, plan, publishing notes
  examples/
    inputs/                     # Natural-language demo and coordinate prompts
    expected/                   # Validated itinerary JSON fixtures
  pixel_travel_map/             # Parser, validation, renderer modules
  schemas/trip.schema.json      # Public schema contract
  scripts/                      # CLI helpers for generation and checks
  pyproject.toml                # Minimal Python package metadata
  README.md
```

## Include And Exclude Policy

Included for the public repository:

- Source code in `pixel_travel_map/` and `scripts/`
- Package metadata in `pyproject.toml`
- Schema and fixture data in `schemas/` and `examples/`
- Small checked-in `dist/` HTML/JSON/SVG demos for GitHub Pages and portfolio links
- Documentation in `README.md` and `docs/`

Excluded from git:

- `__pycache__/`, `*.pyc`, local virtual environments, editor metadata, logs,
  coverage output, and local cache directories
- Ad hoc generated artifacts matching `dist/ambiguous*` or
  `dist/*_from_json_demo.*`
- Any future API keys, secrets, private trip notes, or unpublished user data

## Scope

Built in phase 1:

- Heuristic parser for three curated demo prompts
- Stable itinerary JSON schema and dependency-free validator
- Offline HTML atlas with coordinate-projected route, POI labels, city detail
  views, scale bar, segment distances, itinerary panel, citations, and download button
- One-page SVG poster containing the map and full itinerary
- Artifact quality checks for offline HTML and SVG constraints

Deferred intentionally:

- Production LLM integration
- Accounts, cloud storage, collaboration, and hosted backend services
- Live POI fetching, real map tiles, and precise navigation
- PNG/PDF export and multiple visual themes

## Resume One-Liner

Built a local PixelTravelMap MVP that converts natural-language trip plans into
validated itinerary JSON and renders offline HTML atlas plus one-page SVG poster
artifacts with coordinate-projected POIs, route distances, citations, itinerary
panels, and artifact quality checks.
