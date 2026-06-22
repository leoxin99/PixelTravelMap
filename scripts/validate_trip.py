from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pixel_travel_map.quality import load_json, validate_trip


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a PixelTravelMap itinerary JSON file.")
    parser.add_argument("trip_json", type=Path)
    args = parser.parse_args()

    trip = load_json(args.trip_json)
    errors = validate_trip(trip)
    if errors:
        print("FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
