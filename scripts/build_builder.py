from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pixel_travel_map.builder import write_builder_html


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the PixelTravelMap browser builder.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional single output path. By default writes dist/index.html and dist/builder.html.",
    )
    args = parser.parse_args()

    outputs = [args.output] if args.output else [
        ROOT / "dist" / "index.html",
        ROOT / "dist" / "builder.html",
    ]
    for output in outputs:
        write_builder_html(output)
        print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
