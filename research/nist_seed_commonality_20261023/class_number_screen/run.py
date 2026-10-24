"""Run the frozen GMP comparison and retain raw output plus a receipt."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_LIST_HASH = "07100ea3589ab2b490122fa69b438cd5393bdcd2e547dfc29bb3b5c86f9f24c0"
EXPECTED_LIST_ROWS = 16_453_493


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: run.py EXTERNAL_LIST.txt COMPILED_SCAN")
    external_list, binary = map(lambda s: Path(s).resolve(), sys.argv[1:])
    raw_out, raw_err = HERE / "raw_stdout.tsv", HERE / "raw_stderr.log"
    receipt_path, analysis_path = HERE / "run_receipt.json", HERE / "analysis.json"
    for path in (raw_out, raw_err, receipt_path, analysis_path):
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path}")
    list_hash = sha256(external_list)
    if list_hash != EXPECTED_LIST_HASH:
        raise SystemExit(f"external list SHA-256 mismatch: {list_hash}")
    inputs = json.loads((HERE / "inputs.json").read_text())
    assert sha256(HERE / "curves.tsv") == inputs["curves_tsv_sha256"]
    cmd = [str(binary), str(external_list), str(HERE / "curves.tsv")]
    started, tic = utc_now(), time.monotonic()
    exit_code = None
    error = None
    try:
        with raw_out.open("wb") as stdout, raw_err.open("wb") as stderr:
            exit_code = subprocess.run(cmd, stdout=stdout, stderr=stderr, timeout=245, check=False).returncode
    except subprocess.TimeoutExpired as exc:
        error = f"timeout: {exc}"
    elapsed = time.monotonic() - tic
    receipt = {
        "status": "complete" if exit_code == 0 else "censored",
        "error": error,
        "command": cmd,
        "exit_code": exit_code,
        "started_utc": started,
        "ended_utc": utc_now(),
        "elapsed_wall_seconds": elapsed,
        "max_child_rss_bytes_macos": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "host": platform.platform(),
        "python": sys.version,
        "binary_sha256": sha256(binary),
        "scan_cpp_sha256": sha256(HERE / "scan.cpp"),
        "curves_tsv_sha256": sha256(HERE / "curves.tsv"),
        "external_list_url": "https://raw.githubusercontent.com/iwaokimura/cln-imq-2k/e451afc/lists/imq_h2000.txt.xz",
        "external_list_uncompressed_sha256": list_hash,
        "external_list_uncompressed_bytes": external_list.stat().st_size,
        "raw_stdout_sha256": sha256(raw_out),
        "raw_stderr_sha256": sha256(raw_err),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if exit_code != 0:
        raise SystemExit(f"comparison censored; inspect {receipt_path}")
    with raw_out.open(newline="") as file:
        parsed = list(csv.DictReader(file, delimiter="\t"))
    summaries = {row["label"]: row for row in parsed if row["kind"] == "summary"}
    hits = [row for row in parsed if row["kind"] == "hit"]
    if len(summaries) != 24 or len(hits) != sum(int(r["hits"]) for r in summaries.values()):
        raise SystemExit("output row-count validation failed")
    controls = {
        "control_d3": {"D": 3, "h": 1, "conductor": 17},
        "control_d4": {"D": 4, "h": 1, "conductor": 19},
    }
    for label, expected in controls.items():
        matches = [r for r in hits if r["label"] == label]
        if len(matches) != 1 or {k: int(matches[0][k]) for k in expected} != expected:
            raise SystemExit(f"synthetic positive control failed: {label}")
    if int(summaries["control_nohit"]["hits"]) != 0:
        raise SystemExit("synthetic negative control failed")
    by_curve = []
    for row in inputs["rows"]:
        raw = summaries[row["label"]]
        by_curve.append({**row, "listed_discriminants_dividing_delta": int(raw["divisors"]),
                         "cm_field_hits_h_at_most_2000": int(raw["hits"])})
    analysis = {
        "status": "complete",
        "external_completeness_assumption": "Kimura arXiv:2610.21511v2 Theorem 2 and released list v1.2",
        "external_list_rows": EXPECTED_LIST_ROWS,
        "tested_pairs": EXPECTED_LIST_ROWS * 21,
        "input_assessed_sha256": inputs["assessed_sha256"],
        "input_traits_sha256": inputs["traits_sha256"],
        "run_receipt_sha256": sha256(receipt_path),
        "synthetic_controls": {k: int(summaries[k]["hits"]) for k in (*controls, "control_nohit")},
        "hit_rows": hits,
        "curves": by_curve,
    }
    analysis_path.write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "complete", "hit_counts": {
        "omitted": sum(r["cm_field_hits_h_at_most_2000"] for r in by_curve if r["group"] == "omitted"),
        "published": sum(r["cm_field_hits_h_at_most_2000"] for r in by_curve if r["group"] == "published"),
    }, "elapsed_seconds": round(elapsed, 3)}))


if __name__ == "__main__":
    main()
