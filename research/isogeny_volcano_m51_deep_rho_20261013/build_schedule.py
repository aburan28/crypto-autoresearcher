#!/usr/bin/env python3
"""Regenerate and verify the exact endpoint-independent crossover schedule."""

from __future__ import annotations

import argparse
import hashlib
import io
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEDULE_SEED = 202610136106


def load_local_design() -> object:
    path = HERE / "design.py"
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("design.py must be a regular file")
    source = path.read_bytes()
    digest = hashlib.sha256(source).digest()
    module = types.ModuleType("m51_schedule_design")
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    if hashlib.sha256(path.read_bytes()).digest() != digest:
        raise RuntimeError("design.py changed while loading")
    return module


_design = load_local_design()
generate_schedule = _design.generate_schedule
read_schedule = _design.read_schedule
write_schedule = _design.write_schedule


def render() -> str:
    output = io.StringIO()
    write_schedule(generate_schedule(SCHEDULE_SEED), output)
    return output.getvalue()


def main() -> int:
    if sys.flags.isolated != 1 or sys.flags.dont_write_bytecode != 1:
        raise SystemExit("schedule verification requires Python -I -B")
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    expected = render()
    path = HERE / "schedule.csv"
    if args.stdout:
        sys.stdout.write(expected)
        return 0
    if args.check:
        actual = path.read_text()
        if actual != expected:
            raise SystemExit("schedule.csv differs from deterministic regeneration")
        read_schedule(path)
        print("schedule ok: 4096 blocks; exact crossover and conjugate balances verified")
        return 0
    raise SystemExit("use --check or --stdout; this program never overwrites schedule.csv")


if __name__ == "__main__":
    raise SystemExit(main())
