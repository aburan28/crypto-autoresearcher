#!/usr/bin/env python3
"""Exploratory exact Frobenius splitting screen for the 21 seed classes.

This is a structural predicate, not an isogeny-map construction or ECDLP test.
The input uses assessed.json's eleven seed-level rows, rather than the fourteen
raw P-224 sign models in traits.json.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from math import isqrt
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent.parent / "nist_seed_skipped_curves_20261016"
ASSESSED = STUDY / "assessed.json"
TRAITS = STUDY / "traits.json"
LIMIT = 10_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def odd_primes(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for x in range(2, isqrt(limit) + 1):
        if sieve[x]:
            sieve[x * x : limit + 1 : x] = b"\x00" * ((limit - x * x) // x + 1)
    return [x for x in range(3, limit + 1, 2) if sieve[x]]


def load_rows() -> list[dict]:
    assessed = json.loads(ASSESSED.read_text())
    traits = json.loads(TRAITS.read_text())
    rows = []
    for x in assessed["candidate_rows"]:
        rows.append({
            "label": "omitted",
            "name": f"skip-{x['n_bits']}-{x['seed_ordinal_one_based']}",
            "field_bits": x["n_bits"],
            "ordinal": x["seed_ordinal_one_based"],
            "curve_uid": x["identity"]["curve_uid"],
            "p_hex": x["p_hex"],
            "n_hex": x["n_hex"],
        })
    for name, x in traits["published_controls"].items():
        rows.append({
            "label": "published",
            "name": name,
            "field_bits": x["n_bits"],
            "ordinal": x["seed_ordinal_one_based"],
            "curve_uid": x["identity"]["curve_uid"],
            "p_hex": x["p_hex"],
            "n_hex": x["n_hex"],
        })
    assert len(rows) == 21
    assert sum(r["label"] == "omitted" for r in rows) == 11
    assert len({r["curve_uid"] for r in rows}) == 21
    return sorted(rows, key=lambda r: (r["field_bits"], r["ordinal"]))


def frobenius_sign(delta: int, ell: int) -> str:
    # Euler's criterion: +1 split, 0 repeated root, -1 inert.
    residue = pow(delta % ell, (ell - 1) // 2, ell)
    assert residue in (0, 1, ell - 1)
    return "R" if residue == 0 else "E" if residue == 1 else "A"


def conditional_allocation_diagnostic(rows: list[dict], prime_count: int) -> dict:
    """Enumerate the 4,480 label allocations with observed field counts.

    This is an exact descriptive rank of the observed labels in a finite
    allocation set, not a model of how the original standards group acted.
    """
    groups = []
    for bits in (192, 224, 239, 256):
        indices = [i for i, row in enumerate(rows) if row["field_bits"] == bits]
        omitted_count = sum(rows[i]["label"] == "omitted" for i in indices)
        groups.append([
            sum(1 << i for i in choice)
            for choice in itertools.combinations(indices, omitted_count)
        ])
    full = (1 << len(rows)) - 1
    inert_masks = [
        sum(1 << i for i, row in enumerate(rows) if row["signature"][j] == "A")
        for j in range(prime_count)
    ]
    observed_mask = sum(1 << i for i, row in enumerate(rows) if row["label"] == "omitted")
    observed_all_inert = sum((mask & observed_mask) == observed_mask for mask in inert_masks)
    all_inert_histogram = Counter()
    perfect_histogram = Counter()
    for choice in itertools.product(*groups):
        omitted_mask = choice[0] | choice[1] | choice[2] | choice[3]
        all_inert_histogram[sum((mask & omitted_mask) == omitted_mask for mask in inert_masks)] += 1
        perfect_histogram[sum(mask in (omitted_mask, full ^ omitted_mask) for mask in inert_masks)] += 1
    allocations = sum(all_inert_histogram.values())
    assert allocations == 4480
    return {
        "allocation_count": allocations,
        "observed_all_omitted_inert_prime_count": observed_all_inert,
        "all_inert_prime_count_histogram": dict(sorted(all_inert_histogram.items())),
        "tail_at_least_observed_numerator": sum(
            count for score, count in all_inert_histogram.items() if score >= observed_all_inert
        ),
        "tail_denominator": allocations,
        "perfect_separator_count_histogram": dict(sorted(perfect_histogram.items())),
        "interpretation": "Conditional label-allocation diagnostic only; not a historical probability",
    }


def render_bars(rows: list[dict], prime_count: int) -> str:
    width, height = 1150, 795
    x0, x1 = 310, 955
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#16253e}.title{font-size:20px;font-weight:700}.small{font-size:12px}.label{font-size:13px}.tick{font-size:11px;fill:#59677e}</style>',
        '<text x="42" y="37" class="title">Rational prime-degree isogenies, degrees 3–10,000</text>',
        f'<text x="42" y="58" class="small">Exact fraction among {prime_count} odd primes; 11 omitted and 10 published seed classes</text>',
    ]
    for pct in (40, 45, 50, 55, 60):
        x = x0 + (pct - 40) / 20 * (x1 - x0)
        out.append(f'<line x1="{x:.1f}" y1="82" x2="{x:.1f}" y2="735" stroke="#dfe5ef"/>')
        out.append(f'<text x="{x:.1f}" y="755" text-anchor="middle" class="tick">{pct}%</text>')
    for i, r in enumerate(rows):
        y = 94 + 30 * i
        pct = 100 * r["isogeny_count"] / prime_count
        x = x0 + (pct - 40) / 20 * (x1 - x0)
        color = "#d97828" if r["label"] == "omitted" else "#2864a4"
        out.append(f'<text x="42" y="{y+12}" class="label">{r["name"]}</text>')
        out.append(f'<rect x="{x0}" y="{y}" width="{x-x0:.1f}" height="17" fill="{color}"/>')
        out.append(f'<text x="{x+8:.1f}" y="{y+13}" class="small">{r["isogeny_count"]}/{prime_count} ({pct:.1f}%)</text>')
    out.extend([
        '<rect x="42" y="774" width="12" height="12" fill="#d97828"/><text x="61" y="785" class="small">omitted</text>',
        '<rect x="155" y="774" width="12" height="12" fill="#2864a4"/><text x="174" y="785" class="small">published</text>',
        '<text x="1060" y="785" text-anchor="end" class="small">Deterministic screen; no sampling error</text>',
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def main() -> None:
    primes = odd_primes(LIMIT)
    rows = load_rows()
    for r in rows:
        p, n = int(r["p_hex"], 16), int(r["n_hex"], 16)
        t = p + 1 - n
        delta = t * t - 4 * p
        assert delta < 0 and all(ell != p for ell in primes)
        r["trace_hex_signed"] = hex(t)
        r["delta_hex_signed"] = hex(delta)
        r["signature"] = "".join(frobenius_sign(delta, ell) for ell in primes)
        r["isogeny_count"] = r["signature"].count("E") + r["signature"].count("R")
        r["ramified_count"] = r["signature"].count("R")

    perfect = []
    all_omitted_with = []
    all_omitted_without = []
    for j, ell in enumerate(primes):
        omitted = [r["signature"][j] != "A" for r in rows if r["label"] == "omitted"]
        published = [r["signature"][j] != "A" for r in rows if r["label"] == "published"]
        if all(omitted) and not any(published) or not any(omitted) and all(published):
            perfect.append(ell)
        if all(omitted):
            all_omitted_with.append({"ell": ell, "published_with": sum(published)})
        if not any(omitted):
            all_omitted_without.append({"ell": ell, "published_without": len(published)-sum(published)})

    result = {
        "schema": "nist-seed-rational-isogeny-screen/v1",
        "scope": "Exploratory 21-class screen, not a historical-program replay or weakness test",
        "inputs_sha256": {"assessed.json": sha256(ASSESSED), "traits.json": sha256(TRAITS)},
        "prime_degree_limit_inclusive": LIMIT,
        "odd_prime_degrees": primes,
        "legend": {"E": "Delta nonzero square mod ell", "R": "Delta zero mod ell", "A": "Delta nonsquare mod ell"},
        "rows": rows,
        "comparison": {
            "perfect_single_degree_separators": perfect,
            "all_omitted_with_isogeny": all_omitted_with,
            "all_omitted_without_isogeny": all_omitted_without,
            "conditional_allocation_diagnostic": conditional_allocation_diagnostic(rows, len(primes)),
        },
    }
    (HERE / "analysis.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (HERE / "availability.svg").write_text(render_bars(rows, len(primes)))
    print(json.dumps({
        "rows": len(rows),
        "omitted": sum(r["label"] == "omitted" for r in rows),
        "prime_degrees": len(primes),
        "perfect_separators": perfect,
        "all_omitted_with_count": len(all_omitted_with),
        "all_omitted_without": all_omitted_without,
        "allocation_tail": result["comparison"]["conditional_allocation_diagnostic"]["tail_at_least_observed_numerator"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
