#!/usr/bin/env python3
"""Classify current-main malformed ledger YAML against the existing repair policy.

This is a read-only replay of the dashboard's exact ledger parse sweep. A
registered schema replacement is counted only after independent path, digest,
parse and identity checks, and agreement with the repository merge gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

import yaml

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("evidence.json")


def source_path(value: str) -> Path:
    part = PurePosixPath(value)
    if part.is_absolute() or ".." in part.parts:
        raise ValueError(f"unsafe registry path: {value!r}")
    result = (ROOT / value).resolve()
    if not result.is_relative_to(ROOT):
        raise ValueError(f"registry path leaves repository: {value!r}")
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def registry_records() -> dict[str, list[dict[str, str]]]:
    path = ROOT / "tools/schema_supersession_registry.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("schema") != "schema-supersession-registry-v1":
        raise ValueError("unknown schema supersession registry")
    result: dict[str, list[dict[str, str]]] = {}
    for row in data["records"]:
        result.setdefault(row["superseded_path"], []).append(row)
    return result


def verified_replacement(original: Path, rows: list[dict[str, str]]) -> str | None:
    if len(rows) != 1:
        return None
    row = rows[0]
    try:
        replacement = source_path(row["superseding_path"])
        if sha256(original) != row["superseded_sha256"]:
            return None
        if sha256(replacement) != row["superseding_sha256"]:
            return None
        parsed = yaml.safe_load(replacement.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            return None
        bodies = [parsed] + [v for v in parsed.values() if isinstance(v, dict)]
        if not any(body.get("id") == original.stem for body in bodies):
            return None
        return row["superseding_path"]
    except (KeyError, OSError, UnicodeError, ValueError, yaml.YAMLError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="create a separate new replay JSON; default: stdout")
    args = parser.parse_args()
    if args.output is not None and args.output.resolve() == OUT.resolve():
        parser.error("the committed evidence path is reserved; choose a new output")

    sys.path.insert(0, str(ROOT))
    from tools.check_merge_hygiene import _baseline, _retired_by_supersession

    baseline = _baseline()
    gate_retired = _retired_by_supersession()
    registry = registry_records()
    rows = []
    for path in sorted((ROOT / "ledger").rglob("*.yaml")):
        try:
            yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
            continue
        except yaml.YAMLError as exc:
            error = str(exc).splitlines()[0][:200]
        rel = path.relative_to(ROOT).as_posix()
        replacement = verified_replacement(path, registry.get(rel, []))
        if replacement is not None and gate_retired.get(rel) != replacement:
            raise AssertionError(f"independent and merge-gate routing differ: {rel}")
        if replacement is None and rel in gate_retired:
            raise AssertionError(f"merge gate accepted an independently invalid replacement: {rel}")
        disposition = ("verified_schema_replacement" if replacement is not None
                       else "legacy_parse_baseline" if rel in baseline
                       else "unresolved")
        row = {"path": rel, "error": error, "original_sha256": sha256(path),
               "disposition": disposition}
        if replacement is not None:
            row["replacement_path"] = replacement
        rows.append(row)

    counts = {status: sum(row["disposition"] == status for row in rows)
              for status in ("verified_schema_replacement", "legacy_parse_baseline",
                             "unresolved")}
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                     text=True).strip()
    result = {"schema": "ledger-parse-audit/v1", "source_commit": commit,
              "method": "PyYAML exact ledger sweep; independent SHA/parse/ID check; merge-gate cross-check",
              "scope": "tracked and materialized ledger/**/*.yaml in the exact-main checkout",
              "baseline_entries_all_paths": len(baseline), "counts": counts,
              "malformed_originals": rows}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(text)
    else:
        try:
            # Exclusive creation protects earlier replays and symlink targets.
            with args.output.open("x", encoding="utf-8") as output:
                output.write(text)
        except OSError as exc:
            parser.error(f"cannot create new replay output: {exc}")
        print(commit, len(rows), counts, file=sys.stderr)


if __name__ == "__main__":
    main()
