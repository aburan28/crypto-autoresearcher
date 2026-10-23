#!/usr/bin/env python3
"""Exact pairwise CM-field and same-field relation screen for 21 seed classes.

For ordinary curves with Frobenius discriminants D1,D2 < 0, their imaginary
quadratic CM fields coincide iff D1*D2 is a perfect square. This requires no
factorization of either discriminant. No isogeny map or attack is constructed.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
from math import gcd, isqrt
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / "nist_seed_skipped_curves_20261016"
ASSESSED = SOURCE / "assessed.json"
TRAITS = SOURCE / "traits.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xgcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t


def base_row(label: str, name: str, source: dict) -> dict:
    p = int(source["p_hex"], 16)
    n = int(source["n_hex"], 16)
    trace = p + 1 - n
    delta = trace * trace - 4 * p
    assert p > 3 and trace != 0 and delta < 0
    assert delta == int(source["delta_pi_hex_signed"], 0)
    return {
        "label": label,
        "name": name,
        "field_bits": p.bit_length(),
        "ordinal": source["seed_ordinal_one_based"],
        "curve_uid": source["identity"]["curve_uid"],
        "p_hex": hex(p),
        "n_hex": hex(n),
        "trace_hex_signed": hex(trace),
        "delta_hex_signed": hex(delta),
        "j_hex": source["j_hex"],
    }


def load_rows() -> tuple[list[dict], list[dict]]:
    assessed = json.loads(ASSESSED.read_text())
    traits = json.loads(TRAITS.read_text())
    rows = [
        base_row("omitted", f"skip-{x['n_bits']}-{x['seed_ordinal_one_based']}", x)
        for x in assessed["candidate_rows"]
    ]
    rows += [
        base_row("published", name, x)
        for name, x in traits["published_controls"].items()
    ]
    assert len(rows) == 21
    assert sum(x["label"] == "omitted" for x in rows) == 11
    assert len({x["curve_uid"] for x in rows}) == 21
    rows.sort(key=lambda x: (x["field_bits"], x["ordinal"]))
    return rows, traits["unpublished_candidates"]


def check_pair(a: dict, b: dict) -> dict:
    da = int(a["delta_hex_signed"], 0)
    db = int(b["delta_hex_signed"], 0)
    product = da * db
    assert product > 0
    pa, pb = int(a["p_hex"], 16), int(b["p_hex"], 16)
    na, nb = int(a["n_hex"], 16), int(b["n_hex"], 16)
    same_p = pa == pb
    return {
        "a_uid": a["curve_uid"],
        "b_uid": b["curve_uid"],
        "labels": [a["label"], b["label"]],
        "delta_gcd": gcd(abs(da), abs(db)),
        "same_cm_field": isqrt(product) ** 2 == product,
        "same_p": same_p,
        "same_order_if_same_p": same_p and na == nb,
        "opposite_trace_if_same_p": same_p and na + nb == 2 * (pa + 1),
        "same_j_if_same_p": same_p and a["j_hex"] == b["j_hex"],
    }


def control_pairs(raw: list[dict]) -> list[dict]:
    grouped: dict[tuple[int, int], list[dict]] = {}
    for x in raw:
        if x["n_bits"] == 224:
            grouped.setdefault((x["n_bits"], x["seed_ordinal_one_based"]), []).append(x)
    controls = []
    assert sorted(grouped) == [(224, 777), (224, 1485), (224, 5736)]
    for (bits, ordinal), records in sorted(grouped.items()):
        assert len(records) == 2
        a, b = records
        da, db = int(a["delta_pi_hex_signed"], 0), int(b["delta_pi_hex_signed"], 0)
        same_cm = isqrt(da * db) ** 2 == da * db
        assert a["b_hex"] != b["b_hex"] and da == db and same_cm
        assert a["n_hex"] == b["n_hex"] and a["j_hex"] == b["j_hex"]
        controls.append({
            "field_bits": bits,
            "ordinal": ordinal,
            "curve_uids": [a["identity"]["curve_uid"], b["identity"]["curve_uid"]],
            "different_b_models": True,
            "same_order": True,
            "same_j": True,
            "same_cm_field": same_cm,
        })
    return controls


def render_gcd_histogram(hist: dict[int, int]) -> str:
    width, height = 920, 430
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#172943}.title{font-size:21px;font-weight:700}.sub{font-size:13px}.tick{font-size:12px}</style>',
        '<text x="42" y="37" class="title">Pairwise gcd of omitted-curve Frobenius discriminants</text>',
        '<text x="42" y="60" class="sub">All 55 omitted–omitted pairs; exact integer gcd, no sampling uncertainty</text>',
    ]
    y_base = 350
    for tick in (0, 10, 20, 30, 40):
        y = y_base - tick * 6
        out.append(f'<line x1="90" y1="{y}" x2="855" y2="{y}" stroke="#dce5ef"/>')
        out.append(f'<text x="75" y="{y+4}" text-anchor="end" class="tick">{tick}</text>')
    for i, key in enumerate(sorted(hist)):
        count = hist[key]
        x = 132 + i * 150
        y = y_base - count * 6
        out.append(f'<rect x="{x}" y="{y}" width="76" height="{count*6}" fill="#356ca7"/>')
        out.append(f'<text x="{x+38}" y="{y-8}" text-anchor="middle" class="tick">{count}</text>')
        out.append(f'<text x="{x+38}" y="377" text-anchor="middle" class="tick">{key}</text>')
    out.append('<text x="470" y="410" text-anchor="middle" class="sub">gcd(|Δᵢ|, |Δⱼ|)</text>')
    out.append('</svg>')
    return "\n".join(out) + "\n"


def main() -> None:
    rows, raw = load_rows()
    pairs = [check_pair(a, b) for a, b in itertools.combinations(rows, 2)]
    omitted_pairs = [p for p in pairs if p["labels"] == ["omitted", "omitted"]]
    same_p_pairs = [p for p in pairs if p["same_p"]]
    assert len(pairs) == 210 and len(omitted_pairs) == 55 and len(same_p_pairs) == 45
    assert not any(p["same_cm_field"] for p in pairs)
    assert not any(p["same_order_if_same_p"] or p["opposite_trace_if_same_p"] or p["same_j_if_same_p"] for p in same_p_pairs)
    hist = Counter(p["delta_gcd"] for p in omitted_pairs)
    assert hist == {1: 40, 3: 6, 5: 5, 13: 3, 55: 1}
    a, b = next(
        (a, b) for a, b in itertools.combinations(rows, 2)
        if a["label"] == b["label"] == "omitted"
        and a["p_hex"] == b["p_hex"]
        and gcd(abs(int(a["delta_hex_signed"], 0)), abs(int(b["delta_hex_signed"], 0))) == 1
    )
    da, db = abs(int(a["delta_hex_signed"], 0)), abs(int(b["delta_hex_signed"], 0))
    g, u, v = xgcd(da, db)
    assert g == 1 and u * da + v * db == 1
    result = {
        "schema": "nist-seed-cm-pair-screen/v1",
        "scope": "21 exact seed classes; structural comparison only",
        "inputs_sha256": {"assessed.json": sha256(ASSESSED), "traits.json": sha256(TRAITS)},
        "rows": rows,
        "pairs": pairs,
        "positive_controls": control_pairs(raw),
        "summary": {
            "total_rows": 21,
            "omitted_rows": 11,
            "published_rows": 10,
            "total_pairs": 210,
            "omitted_omitted_pairs": 55,
            "same_cm_field_pairs": 0,
            "max_all_pair_delta_gcd": max(p["delta_gcd"] for p in pairs),
            "max_omitted_pair_delta_gcd": max(hist),
            "omitted_pair_gcd_histogram": dict(sorted(hist.items())),
            "same_field_pairs": 45,
            "same_order_same_field_pairs": 0,
            "opposite_trace_same_field_pairs": 0,
            "same_j_same_field_pairs": 0,
            "raw_p224_sign_model_positive_controls": 3,
        },
        "bezout_witness": {
            "a_uid": a["curve_uid"],
            "b_uid": b["curve_uid"],
            "abs_delta_a_hex": hex(da),
            "abs_delta_b_hex": hex(db),
            "u_hex_signed": hex(u),
            "v_hex_signed": hex(v),
            "identity": "u*abs_delta_a + v*abs_delta_b = 1",
        },
    }
    (HERE / "analysis.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (HERE / "pair_gcd.svg").write_text(render_gcd_histogram(hist))
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
