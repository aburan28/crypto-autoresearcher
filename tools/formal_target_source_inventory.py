#!/usr/bin/env python3
"""Inventory formal target source links from one exact Git tree.

This records path and lexical links only. It does not run Lean or authenticate
experiment execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import PurePosixPath

import yaml


EXP_ID = re.compile(r"(?<![A-Za-z0-9_-])EXP-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*(?![A-Za-z0-9_-])")
RUN_ID = re.compile(r"(?<![A-Za-z0-9_-])RUN-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*(?![A-Za-z0-9_-])")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def blob(rev: str, path: str) -> bytes:
    return git("show", f"{rev}:{path}")


def ids(pattern: re.Pattern[str], data: bytes) -> list[str]:
    return sorted(set(pattern.findall(data.decode("utf-8", "replace"))))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision")
    parser.add_argument("output")
    args = parser.parse_args()
    rev = git("rev-parse", f"{args.revision}^{{commit}}").decode().strip()
    paths = {p.decode("utf-8", "surrogateescape") for p in git("ls-tree", "-r", "-z", "--name-only", rev).split(b"\0") if p}
    target_paths = sorted(p for p in paths if p.startswith("formal/targets/") and p.endswith(".yaml"))
    exp_dirs = {p.split("/")[1] for p in paths if p.startswith("experiments/EXP-")}
    run_dirs = {part for p in paths if p.startswith("experiments/")
                for part in p.split("/")[:-1] if part.startswith("RUN-")}
    source_cache: dict[str, bytes] = {}
    rows = []
    for target in target_paths:
        raw = blob(rev, target)
        spec = yaml.safe_load(raw)
        if not isinstance(spec, dict) or spec.get("schema") != "crypto.autoresearch.formal_task.v1":
            raise ValueError(f"unexpected formal target schema: {target}")
        source = spec["source"]
        workspace = spec["workspace"]
        theorem_file = spec["theorem_file"]
        theorem_name = spec["theorem_name"]
        module = str(PurePosixPath(workspace) / theorem_file)
        if source not in paths or module not in paths:
            raise ValueError(f"missing tracked source or module: {target}")
        if source not in source_cache:
            source_cache[source] = blob(rev, source)
        source_raw = source_cache[source]
        source_parts = PurePosixPath(source).parts
        direct_exp = source_parts[1] if len(source_parts) > 2 and source_parts[0] == "experiments" and source_parts[1].startswith("EXP-") else None
        direct_run = next((part for part in source_parts[2:-1] if part.startswith("RUN-")), None) if direct_exp else None
        literal_exp = ids(EXP_ID, source_raw)
        literal_run = ids(RUN_ID, source_raw)
        rows.append({
            "target": target,
            "target_sha256": hashlib.sha256(raw).hexdigest(),
            "claim_id": spec.get("claim_id"),
            "source_status": spec.get("source_status"),
            "theorem_name": theorem_name,
            "module": module,
            "module_sha256": hashlib.sha256(blob(rev, module)).hexdigest(),
            "source": source,
            "source_sha256": hashlib.sha256(source_raw).hexdigest(),
            "direct_experiment_id": direct_exp,
            "direct_run_id": direct_run,
            "literal_experiment_ids": literal_exp,
            "literal_run_ids": literal_run,
            "literal_experiment_ids_with_tracked_directory": [x for x in literal_exp if x in exp_dirs],
            "literal_run_ids_with_tracked_directory": [x for x in literal_run if x in run_dirs],
        })
    stats = {
        "targets": len(rows),
        "unique_sources": len(source_cache),
        "direct_experiment_path_targets": sum(x["direct_experiment_id"] is not None for x in rows),
        "direct_run_path_targets": sum(x["direct_run_id"] is not None for x in rows),
        "targets_with_literal_experiment_id_in_source": sum(bool(x["literal_experiment_ids"]) for x in rows),
        "targets_with_literal_run_id_in_source": sum(bool(x["literal_run_ids"]) for x in rows),
        "unique_literal_experiment_ids": len({v for x in rows for v in x["literal_experiment_ids"]}),
        "unique_literal_run_ids": len({v for x in rows for v in x["literal_run_ids"]}),
    }
    result = {"schema": "crypto.validation.formal-target-source-links/v1", "revision": rev,
              "method": "Exact tracked target/source/module blobs; path and lexical IDs only, no theorem or run validation.",
              "statistics": stats, "rows": rows}
    with open(args.output, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(stats, sort_keys=True))


if __name__ == "__main__":
    main()
