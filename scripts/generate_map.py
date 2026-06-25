from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pixel_travel_map.parser import ParseNeedInput, load_trip_from_json, parse_travel_text
from pixel_travel_map.quality import validate_trip
from pixel_travel_map.renderer import write_trip_html, write_trip_poster_svg


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a PixelTravelMap HTML artifact.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=Path, help="Natural-language trip description text file.")
    group.add_argument("--trip-json", type=Path, help="Validated itinerary JSON file.")
    parser.add_argument("--output", type=Path, required=True, help="Output HTML path.")
    parser.add_argument("--dump-json", type=Path, help="Optional path to save parsed itinerary JSON.")
    parser.add_argument("--poster-svg", type=Path, help="Optional path to save one-page SVG poster.")
    args = parser.parse_args()

    try:
        if args.trip_json:
            trip = load_trip_from_json(args.trip_json)
        else:
            text = args.input.read_text(encoding="utf-8")
            trip = parse_travel_text(text)
    except ParseNeedInput as exc:
        print(f"PARSE_NEEDS_INPUT: {exc.message}", file=sys.stderr)
        for question in exc.questions:
            print(f"- {question}", file=sys.stderr)
        return 2

    errors = validate_trip(trip)
    if errors:
        print("TRIP_VALIDATION_FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.dump_json:
        args.dump_json.parent.mkdir(parents=True, exist_ok=True)
        args.dump_json.write_text(
            json.dumps(trip, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
        )

    write_trip_html(trip, args.output)
    print(f"Wrote {args.output}")
    if args.poster_svg:
        write_trip_poster_svg(trip, args.poster_svg)
        print(f"Wrote {args.poster_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
