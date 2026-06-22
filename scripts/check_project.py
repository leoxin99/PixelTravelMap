from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pixel_travel_map.quality import check_artifact, load_json, validate_trip


PYTHON_FILES = [
    ROOT / "pixel_travel_map" / "__init__.py",
    ROOT / "pixel_travel_map" / "parser.py",
    ROOT / "pixel_travel_map" / "quality.py",
    ROOT / "pixel_travel_map" / "renderer.py",
    ROOT / "scripts" / "check_artifact.py",
    ROOT / "scripts" / "check_project.py",
    ROOT / "scripts" / "generate_map.py",
    ROOT / "scripts" / "render_map.py",
    ROOT / "scripts" / "validate_trip.py",
]

FIXTURES = [
    ROOT / "examples" / "expected" / "italy_france_switzerland_self_drive.json",
    ROOT / "examples" / "expected" / "japan_kansai_city_trip.json",
    ROOT / "examples" / "expected" / "beijing_family_trip.json",
]

ARTIFACTS = [
    ROOT / "dist" / "italy_france_switzerland_demo.html",
    ROOT / "dist" / "japan_kansai_demo.html",
    ROOT / "dist" / "beijing_family_demo.html",
]


def main() -> int:
    failures: list[str] = []

    for path in PYTHON_FILES:
        try:
            compile(path.read_text(encoding="utf-8"), str(path.relative_to(ROOT)), "exec")
        except SyntaxError as exc:
            failures.append(
                f"{path.relative_to(ROOT)}:{exc.lineno}:{exc.offset}: {exc.msg}"
            )

    for path in FIXTURES:
        for error in validate_trip(load_json(path)):
            failures.append(f"{path.relative_to(ROOT)}: {error}")

    for path in ARTIFACTS:
        for error in check_artifact(path):
            failures.append(f"{path.relative_to(ROOT)}: {error}")

    if failures:
        print("FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
