#!/usr/bin/env python3

import csv
import sys
import time
import os
import glob
import argparse


def find_csv(path: str) -> str:
    if os.path.isfile(path):
        return path
    matches = glob.glob(path)
    if matches:
        return matches[0]
    raise FileNotFoundError(f"No CSV found at: {path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Display CSV timecodes as a real-time incrementing clock."
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        help="Path to the CSV file (defaults to first .csv found in ./input/)",
    )
    parser.add_argument(
        "-newline",
        action="store_true",
        help="Print each timecode on a new line instead of updating in place.",
    )
    return parser.parse_args()


def read_timecodes(csv_path: str):
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        # Normalise header names (strip whitespace)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            try:
                day    = int(float(row["Day"]))
                hour   = int(float(row["Hour"]))
                minute = int(float(row["Minute"]))
                second = int(float(row["Second"]))
                yield (day, hour, minute, second)
            except (KeyError, ValueError):
                continue  # skip malformed rows


def format_timecode(day, hour, minute, second) -> str:
    return f"Day {day:>3d}  {hour:02d}:{minute:02d}:{second:02d}"


def main():
    args = parse_args()

    # Resolve CSV path
    if args.csv_file:
        csv_path = find_csv(args.csv_file)
    else:
        candidates = glob.glob("./input/*.csv")
        if not candidates:
            print("Error: no CSV file specified and none found in ./input/", file=sys.stderr)
            sys.exit(1)
        csv_path = candidates[0]

    print(f"Reading: {csv_path}", file=sys.stderr)
    print("Press Ctrl+C to stop.\n", file=sys.stderr)

    timecodes = list(read_timecodes(csv_path))
    if not timecodes:
        print("Error: no valid timecode rows found in the CSV.", file=sys.stderr)
        sys.exit(1)

    try:
        for i, (day, hour, minute, second) in enumerate(timecodes):
            label = format_timecode(day, hour, minute, second)

            if args.newline:
                print(label)
            else:
                # Overwrite the current line in place
                print(f"\r{label}   ", end="", flush=True)

            # Sleep 1 second, but skip the wait after the last row
            if i < len(timecodes) - 1:
                time.sleep(1)

        # Final newline so the shell prompt appears cleanly
        if not args.newline:
            print()

    except KeyboardInterrupt:
        if not args.newline:
            print()
        print("\nStopped.", file=sys.stderr)


if __name__ == "__main__":
    main()
