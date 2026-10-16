#!/usr/bin/env python3
"""Classify complete and censored order files without inventing missing rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scan


def materialize(i: int, meta: dict, orders: dict, p: int) -> dict:
    row = dict(meta[i])
    n, nt = orders[i]
    b = int(row["b0"], 16)
    if b == 0:
        expression = f"print(lift(sqrt(Mod({int(row['b2'], 16)},{p}))));\nquit;\n"
        b = int(subprocess.run(["gp", "-q", "-f"], input=expression, text=True, capture_output=True, check=True).stdout.strip())
    row.update(b=hex(b), n=hex(n) if n else None, twist_n=hex(nt) if nt else None,
               trace=p + 1 - n if n else None)
    row["j"] = hex((1728 * 4 * (-3) ** 3 * pow((4 * (-3) ** 3 + 27 * b * b) % p, -1, p)) % p)
    row["twist_small_factor_le_10000"] = next((q for q in range(2, 10001) if nt and nt % q == 0), None)
    return row


def summarize(run: Path) -> dict:
    manifest = json.loads((run / "prepare_manifest.json").read_text())
    protocol = json.loads((scan.HERE / "protocol.json").read_text())
    assert manifest["protocol_sha256"] == scan.digest(scan.HERE / "protocol.json")
    assert manifest["scanner_sha256"] == scan.digest(Path(scan.__file__))
    classifier_source = scan.ROOT / "research/nist_seed_provenance_20261016/classify.gp"
    summary = {"protocol_sha256": manifest["protocol_sha256"],
               "scanner_sha256": manifest["scanner_sha256"],
               "summarizer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "classifier_sha256": scan.digest(classifier_source), "streams": []}
    for stream in manifest["streams"]:
        t, p = stream["timestamp"], int(stream["p"], 16)
        meta = {row["ordinal"]: row for row in (json.loads(s) for s in (run / f"metadata_{t}.jsonl").read_text().splitlines())}
        assert scan.digest(run / f"metadata_{t}.jsonl") == stream["metadata_sha256"]
        path = run / f"orders_{t}.txt"
        lines = path.read_text().splitlines() if path.exists() else []
        orders = {}
        for line in lines:
            i, n, nt = map(int, line.split())
            assert i not in orders and i in meta and meta[i]["precheck"] == "point_count_candidate"
            if n:
                assert nt == 2 * p + 2 - n
            orders[i] = n, nt
        assert len(orders) <= stream["point_count_candidates"]
        exact_input = run / f"classifier_input_{t}.txt"
        exact_input.write_text("\n".join(lines) + ("\n" if lines else ""))
        program = f'P={p}; ORDERS="{exact_input}"; RUN="srand48({t})";\n' + classifier_source.read_text()
        result = subprocess.run(["gp", "-q", "-f"], input=program, text=True, capture_output=True, check=True)
        (run / f"classification_{t}.txt").write_text(result.stdout)
        (run / f"classification_{t}.stderr").write_text(result.stderr)
        classes = json.loads(next(s[5:] for s in result.stdout.splitlines() if s.startswith("JSON ")))
        assert classes["candidates"] == len(orders)
        receipt_path = run / f"count_receipt_{t}.json"
        receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
        if receipt is not None:
            assert receipt["output_rows"] == len(orders)
            assert receipt["orders_sha256"] == scan.digest(path)
        status = "complete" if len(orders) == stream["point_count_candidates"] and receipt and receipt["valid_output_count"] else "censored"
        row = {"timestamp": t, "field": stream["field"], "p": stream["p"],
               "first_ordinal": stream["first"], "last_ordinal": stream["last"],
               "blocks_generated": stream["total_blocks"],
               "point_count_candidates": stream["point_count_candidates"],
               "point_count_rows": len(orders), "status": status,
               "early_abort_rows": sum(n == 0 for n, _ in orders.values()),
               "accepted": [materialize(i, meta, orders, p) for i in classes["accepted"]],
               "prime_order_but_long": [materialize(i, meta, orders, p) for i in classes["n_longer_than_p"]],
               "only_twist_prime": [materialize(i, meta, orders, p) for i in classes["only_twist_prime"]],
               "orders_sha256": scan.digest(path) if path.exists() else None,
               "classification_sha256": scan.digest(run / f"classification_{t}.txt")}
        summary["streams"].append(row)
    (run / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    result = summarize(args.run)
    print(json.dumps({"streams": [{"field": s["field"], "rows": s["point_count_rows"], "planned": s["point_count_candidates"], "accepted": [r["ordinal"] for r in s["accepted"]], "status": s["status"]} for s in result["streams"]]}, indent=2))
