# Publishing PixelTravelMap

Use this checklist when turning `PixelTravelMap/` into a standalone public
GitHub repository for a resume or portfolio link.

## Before First Push

Keep these files and folders:

- `README.md`
- `LICENSE`
- `.gitignore`, `.gitattributes`, `.editorconfig`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `pixel_travel_map/`
- `scripts/`
- `schemas/`
- `examples/`
- `docs/`
- `dist/` demo HTML, JSON, and SVG poster artifacts

Do not commit:

- `__pycache__/` or `*.pyc`
- Local virtual environments
- Editor state
- Logs and scratch files
- Ad hoc `dist/ambiguous*` and `dist/*_from_json_demo.*` artifacts
- Locally generated custom-coordinate artifacts such as `dist/*_coordinate_demo*`
- API keys, private trip notes, or unpublished user data

## Local Verification

Run from `PixelTravelMap/`:

```powershell
python scripts/generate_map.py --input examples/inputs/italy_france_switzerland_self_drive.txt --output dist/italy_france_switzerland_demo.html --dump-json dist/italy_france_switzerland_demo.json --poster-svg dist/italy_france_switzerland_demo_poster.svg
python scripts/generate_map.py --input examples/inputs/japan_kansai_city_trip.txt --output dist/japan_kansai_demo.html --dump-json dist/japan_kansai_demo.json --poster-svg dist/japan_kansai_demo_poster.svg
python scripts/generate_map.py --input examples/inputs/beijing_family_trip.txt --output dist/beijing_family_demo.html --dump-json dist/beijing_family_demo.json --poster-svg dist/beijing_family_demo_poster.svg
python scripts/check_project.py
```

Expected result: each generation command prints `Wrote ...`, then
`python scripts/check_project.py` prints `OK`.

## Create The Standalone Repo

```powershell
cd D:\AI\PixelTravelMap
git init
git branch -M main
git add .
git status --short
git commit -m "Initial PixelTravelMap portfolio MVP"
```

Create an empty GitHub repository named `PixelTravelMap`, then connect and push:

```powershell
git remote add origin https://github.com/<your-github-username>/PixelTravelMap.git
git push -u origin main
```

## Enable Demo Links With GitHub Pages

1. Open the repository on GitHub.
2. Go to **Settings** -> **Pages**.
3. Set **Source** to **Deploy from a branch**.
4. Set **Branch** to `main` and folder to `/root`.
5. Save and wait for Pages to publish.

The public demos will use URLs like:

```text
https://<your-github-username>.github.io/PixelTravelMap/dist/italy_france_switzerland_demo.html
https://<your-github-username>.github.io/PixelTravelMap/dist/italy_france_switzerland_demo_poster.svg
https://<your-github-username>.github.io/PixelTravelMap/dist/japan_kansai_demo.html
https://<your-github-username>.github.io/PixelTravelMap/dist/beijing_family_demo.html
```

Use the Italy/France/Switzerland route as the primary resume link because it
shows the richest multi-country artifact. Keep the GitHub repository link next
to it so interviewers can inspect the schema, quality gates, and renderer.

## Suggested Portfolio Copy

```text
PixelTravelMap - schema-first AI travel artifact generator.
Built a no-key local MVP that converts natural-language trip prompts into
validated itinerary JSON and renders offline interactive HTML atlas plus SVG
poster demos.
```

## Suggested Resume Bullet

```text
Built PixelTravelMap, a local AI travel artifact MVP that transforms natural-language trip plans into validated itinerary JSON and deterministic offline HTML/SVG maps with coordinate-projected POIs, route distances, citations, city detail views, and artifact quality checks.
```

## After Publishing

- Check the GitHub Actions CI run after the first push.
- Open each GitHub Pages demo URL in a private browser window.
- Update `README.md` with the real Pages URLs if you want one-click demo links.
- Replace the license copyright holder with your name if preferred.
- Add a screenshot or short GIF to the README once you have a polished visual
  capture of the primary demo.
