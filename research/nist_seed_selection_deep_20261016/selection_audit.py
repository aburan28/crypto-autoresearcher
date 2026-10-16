"""Selection diagnostics over the frozen 21-curve NIST/ANSI seed reconstruction.

This is a comparison of reported stream slots, not a replay of the historical
generator program. The input point counts and prime certificates are inherited
from the source-bound 2026-10-16 assessment named below.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "nist_seed_skipped_curves_20261016"
ASSESSMENT = SOURCE / "assessed.json"
TRAITS = SOURCE / "traits.json"
SUPPLEMENT = SOURCE / "supplemental_checks.json"
OUT = HERE / "selection_matrix.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_signed_hex(value: str) -> int:
    return int(value, 16)


def small_twist_factors(row: dict) -> list[int]:
    return [int(p) for p, _ in row["twist_small_factors_to_10000"]]


def make_row(row: dict, label: str, name: str) -> dict:
    p = int(row["p_hex"], 16)
    n = int(row["n_hex"], 16)
    t = p + 1 - n
    assert t == parse_signed_hex(row["trace_hex_signed"])
    assert int(row["twist_order_hex"], 16) == p + 1 + t
    assert row["identity"]["curve"]["cofactor"] == 1
    assert row["anomalous"] is False
    assert n.bit_length() <= p.bit_length()
    factors = small_twist_factors(row)
    return {
        "label": label,
        "name": name,
        "field_bits": p.bit_length(),
        "timestamp": int(row["timestamp"]),
        "ordinal": int(row["seed_ordinal_one_based"]),
        "seed_hex": row["seed_hex"],
        "curve_uid": row["identity"]["curve_uid"],
        "n_bits": n.bit_length(),
        "n_gt_p": n > p,
        "trace_sign": -1 if t < 0 else 1 if t > 0 else 0,
        "trace_normalized": row["trace_normalized"],
        "twist_small_prime_factors_le_10000": factors,
        "twist_has_small_prime_factor_le_10000": bool(factors),
        "twist_residual_prime_certified": row.get("twist_residual_primality") == "proven_prime",
        "cm_discriminant_scan_gt_2000000": (
            row.get("cm_scan", {}).get("found_fundamental_discriminant") is None
            if label == "passed_over" else None
        ),
    }


def main() -> None:
    assessed, traits, supplemental = map(read_json, (ASSESSMENT, TRAITS, SUPPLEMENT))
    assert assessed["number_of_seed_candidates"] == 11
    assert supplemental["counts"] == {
        "published_controls": 10,
        "skipped_candidates": 11,
        "total": 21,
    }
    assert supplemental["embedding_degree_screen"]["all_21_greater_than_limit"] is True
    assert sha256(ASSESSMENT) == supplemental["source"]["assessed_json_sha256"]

    rows = [make_row(r, "passed_over", f"{r['identity']['curve_id']}")
            for r in assessed["candidate_rows"]]
    rows += [make_row(r, "published", name)
             for name, r in traits["published_controls"].items()]
    assert len(rows) == 21 and len({r["seed_hex"] for r in rows}) == 21
    assert len({r["curve_uid"] for r in rows}) == 21
    assert all(r["n_bits"] <= r["field_bits"] for r in rows)

    streams: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        streams[row["timestamp"]].append(row)

    stream_rows = []
    for timestamp, slots in sorted(streams.items()):
        slots.sort(key=lambda r: r["ordinal"])
        assert len({r["field_bits"] for r in slots}) == 1
        published = [r for r in slots if r["label"] == "published"]
        passed = [r for r in slots if r["label"] == "passed_over"]
        stream_rows.append({
            "timestamp": timestamp,
            "utc": datetime.fromtimestamp(timestamp, timezone.utc).isoformat(),
            "field_bits": slots[0]["field_bits"],
            "published_count": len(published),
            "passed_over_count": len(passed),
            "first_reported_qualifying_slot_published": slots[0]["label"] == "published",
            "slots": [{"ordinal": r["ordinal"], "label": r["label"],
                       "name": r["name"], "seed_prefix": r["seed_hex"][:8]}
                      for r in slots],
            "published_slot_gaps_in_drands": [
                (published[i]["ordinal"] - published[i - 1]["ordinal"]) * 20
                for i in range(1, len(published))
            ],
        })

    published = [r for r in rows if r["label"] == "published"]
    passed = [r for r in rows if r["label"] == "passed_over"]
    selector_checks = {
        "require_n_less_than_p": {
            "counterexample_published": [r["name"] for r in published if r["n_gt_p"]],
            "passed_over_with_n_less_than_p": sum(not r["n_gt_p"] for r in passed),
        },
        "require_positive_trace": {
            "counterexample_published": [r["name"] for r in published if r["trace_sign"] < 0],
            "passed_over_with_positive_trace": sum(r["trace_sign"] > 0 for r in passed),
        },
        "require_twist_without_prime_factor_le_10000": {
            "counterexample_published": [r["name"] for r in published
                                         if r["twist_has_small_prime_factor_le_10000"]],
            "passed_over_without_such_factor": [r["name"] for r in passed
                                                 if not r["twist_has_small_prime_factor_le_10000"]],
        },
        "require_prime_order_and_h_one_and_n_bits_le_field_bits": {
            "published_pass": len(published), "passed_over_pass": len(passed),
        },
        "require_embedding_degree_gt_1000000": {
            "published_pass": len(published), "passed_over_pass": len(passed),
            "basis": "inherited bounded modular screen; exact degree not computed",
        },
        "publish_first_reported_qualifying_slot_per_stream": {
            "counterexample_stream_timestamps": [s["timestamp"] for s in stream_rows
                                                  if not s["first_reported_qualifying_slot_published"]],
        },
    }
    result = {
        "meaning": "Comparison of reported qualifying slots, not original-program decisions",
        "source_sha256": {p.name: sha256(p) for p in (ASSESSMENT, TRAITS, SUPPLEMENT)},
        "counts": {"published": len(published), "passed_over": len(passed),
                   "streams": len(stream_rows)},
        "selector_checks": selector_checks,
        "streams": stream_rows,
        "rows": sorted(rows, key=lambda r: (r["timestamp"], r["ordinal"])),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"counts": result["counts"],
                      "selector_checks": selector_checks}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
