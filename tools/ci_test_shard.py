#!/usr/bin/env python3
"""Split the pytest suite into balanced CI shards, by file.

`validate.yml` runs the suite as parallel matrix jobs; this picks each job's
files. Run serially it took 19 minutes, two thirds of the job's 33. Files are
packed longest-first onto the least-loaded shard (LPT) using the measured
seconds in `.github/test-durations.json`; a file with no measurement counts as
the median. Every collected file lands in exactly one shard, so the shards'
union is the whole suite, and a file that fails to collect still lands in one
(and fails there, as it would serially).

    python3 tools/ci_test_shard.py --shard 1 --of 4      # shard 1's files, one per line
    python3 tools/ci_test_shard.py --of 4 --plan         # every shard and its estimate
    python3 tools/ci_test_shard.py --update harness-tests-*.xml   # refresh durations

The unit is the file, never the test: classes share expensive fixtures
(`setUpClass` over the real ledger), and splitting one would pay for them twice.
A stale durations file only unbalances the shards; it never drops a test.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DURATIONS = REPO / ".github" / "test-durations.json"
_ERROR = re.compile(r"^ERROR (?:collecting )?(\S+?\.py)\b")


def collected_files(repo: Path = REPO) -> list[str]:
    """Test files pytest collects under the configured testpaths, sorted."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=repo, capture_output=True, text=True, check=False)
    files: set[str] = set()
    for line in proc.stdout.splitlines():
        if "::" in line:
            files.add(line.split("::", 1)[0])
        elif match := _ERROR.match(line):
            files.add(match.group(1))
    if not files:
        raise SystemExit(f"ci_test_shard: pytest collected nothing:\n{proc.stdout}{proc.stderr}")
    return sorted(files)


def load_durations(path: Path = DURATIONS) -> dict[str, float]:
    try:
        return {k: float(v) for k, v in json.loads(path.read_text())["seconds"].items()}
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def plan(files: list[str], shards: int, durations: dict[str, float]) -> list[list[str]]:
    """LPT: longest file first onto the least-loaded shard; deterministic."""
    if shards < 1:
        raise ValueError("need at least one shard")
    default = statistics.median(durations.values()) if durations else 1.0
    weight = {f: durations.get(f, default) for f in files}
    loads = [0.0] * shards
    out: list[list[str]] = [[] for _ in range(shards)]
    for f in sorted(files, key=lambda f: (-weight[f], f)):
        i = min(range(shards), key=lambda i: (loads[i], i))
        out[i].append(f)
        loads[i] += weight[f]
    return [sorted(s) for s in out]


def junit_durations(paths: list[Path], repo: Path = REPO) -> dict[str, float]:
    """Seconds per test file from pytest JUnit XML (classname is dotted path[.Class])."""
    seconds: dict[str, float] = {}
    for path in paths:
        for case in ET.parse(path).getroot().iter("testcase"):
            parts = (case.get("classname") or "").split(".")
            for i in range(len(parts), 0, -1):
                candidate = "/".join(parts[:i]) + ".py"
                if (repo / candidate).is_file():
                    seconds[candidate] = seconds.get(candidate, 0.0) + float(case.get("time") or 0)
                    break
    return seconds


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--of", type=int, help="number of shards")
    parser.add_argument("--shard", type=int, help="1-based shard to print")
    parser.add_argument("--plan", action="store_true", help="print every shard with its estimate")
    parser.add_argument("--update", nargs="+", type=Path, metavar="JUNIT",
                        help="rewrite .github/test-durations.json from JUnit XML")
    args = parser.parse_args(argv)

    if args.update:
        seconds = junit_durations(args.update)
        DURATIONS.write_text(json.dumps({
            "source": "per-file pytest seconds from CI JUnit XML; "
                      "regenerate with tools/ci_test_shard.py --update",
            "seconds": {k: round(v, 1) for k, v in sorted(seconds.items())},
        }, indent=1) + "\n")
        print(f"ci_test_shard: {len(seconds)} files, {sum(seconds.values()):.0f}s total")
        return 0
    if not args.of or args.of < 1:
        parser.error("--of N is required")
    durations = load_durations()
    shards = plan(collected_files(), args.of, durations)
    if args.plan:
        default = statistics.median(durations.values()) if durations else 1.0
        for i, files in enumerate(shards, 1):
            est = sum(durations.get(f, default) for f in files)
            print(f"shard {i}/{args.of}: {len(files)} files, ~{est:.0f}s")
        return 0
    if not args.shard or not 1 <= args.shard <= args.of:
        parser.error("--shard must be between 1 and --of")
    print("\n".join(shards[args.shard - 1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
