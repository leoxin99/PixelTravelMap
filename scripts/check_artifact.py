from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pixel_travel_map.quality import check_artifact, check_svg_artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a generated PixelTravelMap HTML or SVG artifact.")
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()

    if args.artifact.suffix.lower() == ".svg":
        errors = check_svg_artifact(args.artifact)
    else:
        errors = check_artifact(args.artifact)
    if errors:
        print("FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
