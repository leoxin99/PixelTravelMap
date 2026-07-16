from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pixel_travel_map.renderer import write_share_viewer_html


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

    write_share_viewer_html(args.output)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
