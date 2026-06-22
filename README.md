# PixelTravelMap

PixelTravelMap is a portfolio MVP for an AI travel artifact generator. It turns
a natural-language trip description into validated itinerary JSON, then renders
a self-contained offline HTML pixel map with clickable POIs, city filters,
source notes, and a downloadable single-file artifact.

The project is intentionally small: no API keys, no backend, no map tile
provider, and no third-party runtime dependencies. The point is to show the
schema-first AI workflow and the deterministic artifact pipeline that would sit
behind a larger travel planning product.

## What To Open First

- Demo artifacts: `dist/italy_france_switzerland_demo.html`,
  `dist/japan_kansai_demo.html`, and `dist/beijing_family_demo.html`.
- Architecture and tradeoffs: [`docs/interview_narrative.md`](docs/interview_narrative.md).
- Publishing checklist: [`docs/publishing.md`](docs/publishing.md).

After GitHub Pages is enabled, the checked-in demo HTML files can be linked
directly from a resume or portfolio.

## Recruiter Snapshot

- **Problem:** turn a loose trip idea into a polished, shareable travel map.
- **Approach:** parse text into a stable itinerary schema, validate before
  rendering, then generate one offline HTML artifact.
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
  -> self-contained HTML artifact
  -> scripts/check_artifact.py
```

The generated HTML includes inline CSS, inline JavaScript, inline SVG, and the
trip JSON payload. It is designed to open directly from disk and to work without
network access.

## Quickstart

Requirements:

- Python 3.10 or newer
- No third-party Python packages

From the repository root:

```powershell
python scripts/validate_trip.py examples/expected/italy_france_switzerland_self_drive.json
python scripts/generate_map.py --input examples/inputs/italy_france_switzerland_self_drive.txt --output dist/italy_france_switzerland_demo.html --dump-json dist/italy_france_switzerland_demo.json
python scripts/check_artifact.py dist/italy_france_switzerland_demo.html
python scripts/check_project.py
```

Then open the generated file in a browser:

```text
dist/italy_france_switzerland_demo.html
```

## Included Demo Scenarios

| Scenario | Natural-language input | Expected JSON | HTML artifact |
| --- | --- | --- | --- |
| Italy, France, Switzerland self-drive | `examples/inputs/italy_france_switzerland_self_drive.txt` | `examples/expected/italy_france_switzerland_self_drive.json` | `dist/italy_france_switzerland_demo.html` |
| Japan Kansai city trip | `examples/inputs/japan_kansai_city_trip.txt` | `examples/expected/japan_kansai_city_trip.json` | `dist/japan_kansai_demo.html` |
| Beijing family trip | `examples/inputs/beijing_family_trip.txt` | `examples/expected/beijing_family_trip.json` | `dist/beijing_family_demo.html` |

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
python scripts/check_artifact.py dist/japan_kansai_demo.html
python scripts/check_artifact.py dist/beijing_family_demo.html
```

The artifact checker rejects external scripts, external stylesheets, `fetch`,
`XMLHttpRequest`, dynamic imports, missing required DOM nodes, and oversized
HTML files.

## Repository Structure

```text
PixelTravelMap/
  .github/workflows/ci.yml      # GitHub Actions quality gate
  dist/                         # Checked-in offline demo artifacts
  docs/                         # Interview narrative, plan, publishing notes
  examples/
    inputs/                     # Natural-language demo prompts
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
- Small checked-in `dist/` HTML/JSON demos for GitHub Pages and portfolio links
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
- Offline HTML renderer with inline SVG map, route, markers, city filters,
  itinerary panel, POI detail card, citations, and download button
- Artifact quality checks for offline constraints

Deferred intentionally:

- Production LLM integration
- Accounts, cloud storage, collaboration, and hosted backend services
- Live POI fetching, real map tiles, and precise navigation
- PNG/PDF export and multiple visual themes

## Resume One-Liner

Built a local PixelTravelMap MVP that converts natural-language trip plans into
validated itinerary JSON and renders a self-contained interactive pixel-map HTML
artifact with clickable POIs, citations, itinerary panels, and artifact quality
checks.
