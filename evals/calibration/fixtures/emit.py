"""Deterministic stand-in command for calibration task cards.

Frozen: calibration items bind this file by sha256, so editing it invalidates every suite
built against it (rebuild with evals/calibration/build.py).

    emit.py print TEXT          print TEXT, exit 0
    emit.py write PATH TEXT     write TEXT to PATH (repository-relative), exit 0
    emit.py exit CODE           print a line, exit CODE
    emit.py sleep SECONDS       sleep, then exit 0
"""
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def main(argv: list[str]) -> int:
    mode, args = argv[0], argv[1:]
    if mode == "print":
        print(" ".join(args))
        return 0
    if mode == "write":
        path = REPO / args[0]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(" ".join(args[1:]) + "\n", encoding="utf-8")
        print(f"wrote {args[0]}")
        return 0
    if mode == "exit":
        print(f"exiting with status {args[0]}")
        return int(args[0])
    if mode == "sleep":
        time.sleep(float(args[0]))
        return 0
    print(f"unknown mode {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
