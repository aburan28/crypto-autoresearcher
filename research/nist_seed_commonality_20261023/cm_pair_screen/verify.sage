#!/usr/bin/env sage -python
"""Independent Sage check of the exact CM-field pair screen."""

from collections import Counter
from itertools import combinations
import hashlib
import json
from pathlib import Path

from sage.all import ZZ, fundamental_discriminant, gcd
from sage.version import version as sage_version


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / "nist_seed_skipped_curves_20261016"
ASSESSED = SOURCE / "assessed.json"
TRAITS = SOURCE / "traits.json"
ANALYSIS = HERE / "analysis.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(label, name, record):
    p = ZZ(int(record["p_hex"], 0))
    n = ZZ(int(record["n_hex"], 0))
    t = p + 1 - n
    delta = t * t - 4 * p
    assert p > 3 and t != 0 and delta < 0
    assert delta == ZZ(int(record["delta_pi_hex_signed"], 0))
    return {
        "label": label,
        "name": name,
        "uid": record["identity"]["curve_uid"],
        "ordinal": record["seed_ordinal_one_based"],
        "p": p,
        "n": n,
        "t": t,
        "delta": delta,
        "j": record["j_hex"],
    }


def main():
    assessed = json.loads(ASSESSED.read_text())
    traits = json.loads(TRAITS.read_text())
    analysis = json.loads(ANALYSIS.read_text())
    assert analysis["inputs_sha256"] == {
        "assessed.json": digest(ASSESSED),
        "traits.json": digest(TRAITS),
    }
    rows = [
        row("omitted", f"skip-{x['n_bits']}-{x['seed_ordinal_one_based']}", x)
        for x in assessed["candidate_rows"]
    ] + [
        row("published", name, x)
        for name, x in traits["published_controls"].items()
    ]
    assert len(rows) == 21 and len({r["uid"] for r in rows}) == 21
    assert sum(r["label"] == "omitted" for r in rows) == 11
    rows.sort(key=lambda r: (r["p"].nbits(), r["ordinal"]))
    assert [r["uid"] for r in rows] == [r["curve_uid"] for r in analysis["rows"]]
    for source, recorded in zip(rows, analysis["rows"]):
        assert source["p"] == ZZ(int(recorded["p_hex"], 0))
        assert source["n"] == ZZ(int(recorded["n_hex"], 0))
        assert source["t"] == ZZ(int(recorded["trace_hex_signed"], 0))
        assert source["delta"] == ZZ(int(recorded["delta_hex_signed"], 0))

    calc = {}
    hist = Counter()
    same_p_count = 0
    same_cm_count = 0
    same_order_count = 0
    opposite_trace_count = 0
    same_j_count = 0
    max_gcd = 0
    for a, b in combinations(rows, 2):
        g = gcd(abs(a["delta"]), abs(b["delta"]))
        same_cm = bool((a["delta"] * b["delta"]).is_square())
        same_p = a["p"] == b["p"]
        same_order = same_p and a["n"] == b["n"]
        opposite_trace = same_p and a["t"] == -b["t"]
        same_j = same_p and a["j"] == b["j"]
        calc[(a["uid"], b["uid"])] = (int(g), same_cm, same_p,
            same_order, opposite_trace, same_j)
        if a["label"] == b["label"] == "omitted":
            hist[int(g)] += 1
        same_p_count += int(same_p)
        same_cm_count += int(same_cm)
        same_order_count += int(same_order)
        opposite_trace_count += int(opposite_trace)
        same_j_count += int(same_j)
        max_gcd = max(max_gcd, int(g))
    assert len(calc) == 210 and len(analysis["pairs"]) == 210
    for pair in analysis["pairs"]:
        key = pair["a_uid"], pair["b_uid"]
        assert key in calc
        expected = calc.pop(key)
        actual = (pair["delta_gcd"], pair["same_cm_field"], pair["same_p"],
            pair["same_order_if_same_p"], pair["opposite_trace_if_same_p"],
            pair["same_j_if_same_p"])
        assert actual == expected, key
    assert not calc
    assert dict(hist) == {1: 40, 3: 6, 5: 5, 13: 3, 55: 1}
    assert same_cm_count == same_order_count == opposite_trace_count == same_j_count == 0
    assert same_p_count == 45 and max_gcd == 1705

    raw_p224 = [x for x in traits["unpublished_candidates"] if x["n_bits"] == 224]
    positive = 0
    for ordinal in (777, 1485, 5736):
        pair = [x for x in raw_p224 if x["seed_ordinal_one_based"] == ordinal]
        assert len(pair) == 2
        a = row("control", f"p224-{ordinal}-a", pair[0])
        b = row("control", f"p224-{ordinal}-b", pair[1])
        assert pair[0]["b_hex"] != pair[1]["b_hex"]
        assert a["p"] == b["p"] and a["n"] == b["n"]
        assert a["delta"] == b["delta"] and a["j"] == b["j"]
        assert (a["delta"] * b["delta"]).is_square()
        positive += 1
    witness = analysis["bezout_witness"]
    wa = ZZ(int(witness["abs_delta_a_hex"], 0))
    wb = ZZ(int(witness["abs_delta_b_hex"], 0))
    u = ZZ(int(witness["u_hex_signed"], 0))
    v = ZZ(int(witness["v_hex_signed"], 0))
    assert u * wa + v * wb == 1 and gcd(wa, wb) == 1
    assert {witness["a_uid"], witness["b_uid"]} <= {r["uid"] for r in rows if r["label"] == "omitted"}

    small_cm = analysis["small_cm_screen"]
    bound = small_cm["maximum_absolute_fundamental_discriminant_tested"]
    assert bound == 1_000_000
    ds = [d for d in range(-3, -bound - 1, -1)
          if int(fundamental_discriminant(d)) == d]
    assert len(ds) == small_cm["fundamental_discriminants_tested"] == 303_968
    assert all(int(fundamental_discriminant(d)) == d for d in (-3, -4, -7, -8, -11, -15, -19, -20))
    assert int(fundamental_discriminant(-12)) == -3
    small_cm_hits = []
    for source in rows:
        for d in ds:
            if source["delta"] % d == 0 and (source["delta"] // d).is_square():
                small_cm_hits.append((source["uid"], d))
    assert small_cm_hits == small_cm["matches"] == []
    assert small_cm["curve_comparisons"] == len(rows) * len(ds)

    receipt = {
        "schema": "nist-seed-cm-pair-sage-verification/v1",
        "status": "PASS",
        "sage_version": sage_version,
        "inputs_sha256": {"assessed.json": digest(ASSESSED), "traits.json": digest(TRAITS)},
        "analysis_sha256": digest(ANALYSIS),
        "rows_checked": 21,
        "pairs_checked": 210,
        "omitted_pairs_checked": 55,
        "same_field_pairs_checked": same_p_count,
        "same_cm_field_pairs": same_cm_count,
        "same_order_same_field_pairs": same_order_count,
        "opposite_trace_same_field_pairs": opposite_trace_count,
        "same_j_same_field_pairs": same_j_count,
        "max_pair_delta_gcd": max_gcd,
        "omitted_pair_gcd_histogram": dict(sorted(hist.items())),
        "positive_controls_checked": positive,
        "bezout_witness_verified": True,
        "small_cm_discriminants_checked_to": bound,
        "small_cm_discriminants_count": len(ds),
        "small_cm_curve_comparisons": len(rows) * len(ds),
        "small_cm_matches": len(small_cm_hits),
        "small_cm_synthetic_controls_checked": 9,
    }
    (HERE / "sage_verification.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
