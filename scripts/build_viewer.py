from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the generic PixelTravelMap share viewer."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dist" / "viewer.html",
        help="Output viewer HTML path.",
    )
    args = parser.parse_args()

    builder_path = ROOT / "dist" / "index.html"
    if not builder_path.exists():
        raise SystemExit("dist/index.html is missing; run scripts/build_builder.py first")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "node",
            str(ROOT / "scripts" / "render_viewer_from_builder.mjs"),
            str(builder_path),
            str(args.output),
        ],
        check=True,
    )
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
