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
        default=ROOT / "dist" / "builder.html",
        help="Output builder HTML path.",
    )
    args = parser.parse_args()

    write_builder_html(args.output)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
