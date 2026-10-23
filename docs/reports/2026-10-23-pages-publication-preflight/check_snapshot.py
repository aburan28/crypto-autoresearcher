#!/usr/bin/env python3
"""Check one local Pages snapshot against its source commit and pinned rows."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True).stdout


def main():
    if not __debug__:
        raise RuntimeError("validation assertions require normal Python mode")
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--site", type=Path, required=True)
    ap.add_argument("--source-repo", type=Path, required=True)
    ap.add_argument("--build-report", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    repo = args.repo.resolve()
    site = args.site.resolve()
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    assert git(repo, "rev-parse", "--is-shallow-repository").strip() == b"false"

    meta_path = site / "data/meta.json"
    comparisons_path = site / "data/comparisons.json"
    integrity_path = site / "data/integrity.json"
    meta = json.loads(meta_path.read_text())
    comparisons = json.loads(comparisons_path.read_text())
    integrity = json.loads(integrity_path.read_text())
    report = json.loads(args.build_report.read_text())
    bundle_bytes = git(repo, "show", f"{head}:ui/benchmarks/cryptanalysis-primary.json")
    bundle = json.loads(bundle_bytes)

    assert meta["commit"] == report["commit"] == head
    assert meta["git"]["available"] is True and meta["git"]["paths"] > 0
    assert meta["git"]["commits"] > 1
    assert meta["records"] == report["records"] >= 100
    assert report["bytes"] < 900_000_000
    assert len(comparisons["receipts"]) == len(bundle["rows"]) == 9
    assert comparisons.get("error") is None
    assert integrity["unparseable_state"] == "complete"
    assert len(integrity["unparseable"]) == report["unparseable"]

    source_commit = bundle["source_commit"]
    for path, pin in bundle["sources"].items():
        assert path == pin["path"]
        source = git(args.source_repo, "show", f"{source_commit}:{path}")
        assert digest(source) == pin["sha256"], path

    primary_path = "experiments/ic-bench/baseline/primary.jsonl"
    primary = git(args.source_repo, "show", f"{source_commit}:{primary_path}")
    source_rows = [json.loads(line) for line in primary.splitlines() if line]
    assert len(source_rows) == 9

    fields = ("run_id", "candidate_id", "workload_id", "status",
              "total_operations", "wall_ns", "operation_unit")
    source_field_checks = 0
    payload_field_checks = 0
    for ordinal, (row, receipt) in enumerate(zip(bundle["rows"], comparisons["receipts"]), 1):
        assert row["source_line"] == ordinal
        source_row = source_rows[ordinal - 1]
        for field in fields:
            assert row[field] == source_row[field], (ordinal, field)
            source_field_checks += 1
        for field in ("ic_online_ns", "rho_online_ns"):
            assert row[field] == source_row["online"][field], (ordinal, field)
            source_field_checks += 1
        assert row["targets_verified"] == source_row["counts"]["targets_verified"]
        source_field_checks += 1

        for field in ("candidate_id", "workload_id", "curve_uid", "curve_id",
                      "operation_unit", "status", "scope"):
            assert receipt[field] == row[field], (ordinal, field)
            payload_field_checks += 1
        for field in ("total_operations", "ic_online_ns", "rho_online_ns", "targets_verified"):
            assert receipt["metrics"][field] == row[field], (ordinal, field)
            payload_field_checks += 1
        assert receipt["metrics"]["total_wall_seconds"] == row["wall_ns"] / 1e9
        payload_field_checks += 1
        assert receipt["timing_boundary"] == row["online_boundary"]
        payload_field_checks += 1
        assert {v["path"]: v["sha256"] for v in receipt["sources"].values()} == {
            p: bundle["sources"][p]["sha256"] for p in row["sources"]}
        payload_field_checks += len(row["sources"])

    output = {
        "schema": "pages-fullhistory-preflight-v1",
        "status": "pass",
        "scope": "local snapshot and pinned archive consistency; no live deployment or scientific replay",
        "repo_commit": head,
        "bundle_sha256": digest(bundle_bytes),
        "source_repository": bundle["source_repository"],
        "source_commit": source_commit,
        "source_files_sha256_checked": len(bundle["sources"]),
        "source_field_checks": source_field_checks,
        "payload_field_checks": payload_field_checks,
        "comparison_rows": len(comparisons["receipts"]),
        "comparison_error": comparisons.get("error"),
        "comparison_sha256": digest(comparisons_path.read_bytes()),
        "integrity_sha256": digest(integrity_path.read_bytes()),
        "unparseable": len(integrity["unparseable"]),
        "duplicate_ids": len(integrity["duplicate_ids"]),
        "id_path_mismatch": len(integrity["id_path_mismatch"]),
        "dangling_refs": integrity["dangling_refs_total"],
        "git_dates_available": True,
        "git_paths": meta["git"]["paths"],
        "git_commits": meta["git"]["commits"],
        "records": meta["records"],
        "files": report["files"],
        "bytes": report["bytes"],
        "built_at": meta["built_at"],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
