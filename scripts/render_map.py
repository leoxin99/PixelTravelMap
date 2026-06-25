from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pixel_travel_map.parser import load_trip_from_json
from pixel_travel_map.quality import validate_trip
from pixel_travel_map.renderer import write_trip_html, write_trip_poster_svg


def main() -> int:
    parser = argparse.ArgumentParser(description="Render itinerary JSON to self-contained HTML.")
    parser.add_argument("--input", type=Path, required=True, help="Itinerary JSON path.")
    parser.add_argument("--output", type=Path, required=True, help="Output HTML path.")
    parser.add_argument("--poster-svg", type=Path, help="Optional path to save one-page SVG poster.")
    args = parser.parse_args()

    trip = load_trip_from_json(args.input)
    errors = validate_trip(trip)
    if errors:
        print("TRIP_VALIDATION_FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    write_trip_html(trip, args.output)
    print(f"Wrote {args.output}")
    if args.poster_svg:
        write_trip_poster_svg(trip, args.poster_svg)
        print(f"Wrote {args.poster_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
