#!/usr/bin/env python3
"""Render a measured bound record as a cairn artifact, and prove the rendering
lossless.

cairn's canonical encoding has no float variant (`canonical::Value`, by
design: a double does not round-trip identically through every JSON
implementation, and an artifact's id is the digest of its bytes). A bound
record as ecbench writes it (`ecbench.bound/v1`, aburan28/crypto
`docs/bounds/README.md`) carries dozens of floats, so `cairn propose`,
`commit` and `score_candidate` refuse it before any verifier runs, with the
advice this tool follows: "carry a scaled integer or a decimal string
instead".

    render FILE [--out FILE]   every non-integer JSON number becomes its
                               shortest round-trip decimal string (Python's
                               `repr`, which `float()` reads back to the same
                               double); integers, strings, booleans and nulls
                               are untouched; keys are sorted. Prints the
                               artifact when --out is absent.
    check RECORD ARTIFACT      the artifact is exactly what `render` writes
                               for the record, and reading every decimal
                               string back gives the record's doubles. Exit 1
                               when either fails.

The pinned evaluator (`cairn/checkers/bound_frontier_prime_toy.py`) reads both
spellings, so `check` there runs on the record as committed and `score` on the
artifact as cairn delivers it. Nothing here changes a value: the record's
`bound_id` still names the measuring repository's bytes, and the artifact's
cairn id names these. Neither is the other, and the evidence record cites the
first.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def render_value(value: Any) -> Any:
    """Floats to decimal strings, recursively; everything else as it was."""
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("a bound record carries only finite numbers")
        return repr(value)
    if isinstance(value, list):
        return [render_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): render_value(item) for key, item in value.items()}
    raise TypeError(f"cannot render a {type(value).__name__}")


def render(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise TypeError("a bound record is a JSON object")
    return render_value(record)


def dumps(artifact: dict[str, Any]) -> str:
    return json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def restore_value(value: Any, original: Any) -> Any:
    """Read decimal strings back where the record had floats, so a rendering
    can be compared with its source value for value rather than text."""
    if isinstance(original, float) and isinstance(value, str):
        return float(value)
    if isinstance(original, list) and isinstance(value, list) and len(value) == len(original):
        return [restore_value(v, o) for v, o in zip(value, original)]
    if isinstance(original, dict) and isinstance(value, dict):
        return {key: restore_value(value.get(key), original.get(key)) for key in value}
    return value


def check(record: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    """Problems with an artifact that claims to render this record."""
    problems: list[str] = []
    expected = render(record)
    if artifact != expected:
        problems.append("the artifact is not what `render` writes for this record")
    if restore_value(artifact, record) != record:
        problems.append("a decimal string in the artifact does not read back to the record's double")
    return problems


def _load(path: str) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("render", help="write the record as a cairn artifact")
    p.add_argument("record")
    p.add_argument("--out")
    p = sub.add_parser("check", help="the artifact is the lossless rendering of the record")
    p.add_argument("record")
    p.add_argument("artifact")
    args = parser.parse_args(argv)
    try:
        if args.command == "render":
            text = dumps(render(_load(args.record)))
            if args.out:
                Path(args.out).write_text(text, encoding="utf-8")
            else:
                sys.stdout.write(text)
            return 0
        problems = check(_load(args.record), _load(args.artifact))
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1 if problems else 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
