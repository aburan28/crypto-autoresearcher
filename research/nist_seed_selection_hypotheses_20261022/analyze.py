#!/usr/bin/env python3
"""Exploratory, source-bound feature comparison for the 21 recorded seed slots.

This is a derived comparison of archived curves, not a historical acceptance
model or a scan of the generator orbit. It writes no source records.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "nist_seed_skipped_curves_20261016" / "traits.json"
FIELDS_WITH_BOTH_LABELS = (192, 224, 239, 256)


def rank(values: list[int]) -> list[float]:
    """Ascending midranks, including ties."""
    return [1 + sum(x < v for x in values) + (sum(x == v for x in values) - 1) / 2 for v in values]


def main() -> None:
    raw = SOURCE.read_bytes()
    archive = json.loads(raw)
    rows = []
    for name, item in archive["published_controls"].items():
        rows.append((name, "published", item))
    seen = set()
    for item in archive["unpublished_candidates"]:
        key = (item["timestamp"], item["seed_ordinal_one_based"])
        if key not in seen:
            seen.add(key)
            rows.append((f"#{key[1]}", "passed_over", item))
    assert len(rows) == 21 and len(seen) == 11

    derived = []
    for name, label, item in rows:
        p = int(item["p_hex"], 16)
        b = int(item["b_hex"], 16)
        bits = p.bit_length()
        alternative = (-b) % p
        derived.append({
            "field_bits": bits,
            "name": name,
            "label": label,
            "ordinal": item["seed_ordinal_one_based"],
            "curve_uid": item["identity"]["curve_uid"],
            "b_popcount": b.bit_count(),
            "b_sign_invariant_popcount": min(b.bit_count(), alternative.bit_count()) if bits == 224 else b.bit_count(),
            "seed_popcount": int(item["seed_hex"], 16).bit_count(),
            "c_popcount": int(item["ansi_c_hex"], 16).bit_count(),
            "n_popcount": int(item["n_hex"], 16).bit_count(),
        })

    comparisons = {}
    for feature in ("b_popcount", "b_sign_invariant_popcount", "seed_popcount", "c_popcount", "n_popcount"):
        observed = 0.0
        possible_by_field = []
        within_field_pairs = 0
        published_lower_pairs = 0
        for bits in FIELDS_WITH_BOTH_LABELS:
            group = [row for row in derived if row["field_bits"] == bits]
            values = [row[feature] for row in group]
            ranks = rank(values)
            n_published = sum(row["label"] == "published" for row in group)
            observed += sum(ranks[i] for i, row in enumerate(group) if row["label"] == "published")
            possible_by_field.append([
                sum(ranks[i] for i in choice)
                for choice in itertools.combinations(range(len(group)), n_published)
            ])
            pub_values = [row[feature] for row in group if row["label"] == "published"]
            skip_values = [row[feature] for row in group if row["label"] == "passed_over"]
            within_field_pairs += len(pub_values) * len(skip_values)
            published_lower_pairs += sum(p < s for p in pub_values for s in skip_values)
        scores = [sum(x) for x in itertools.product(*possible_by_field)]
        comparisons[feature] = {
            "observed_rank_sum": observed,
            "label_allocations": len(scores),
            "allocations_at_or_below_observed": sum(x <= observed + 1e-9 for x in scores),
            "within_field_published_vs_passed_over_pairs": within_field_pairs,
            "pairs_with_published_lower": published_lower_pairs,
            "interpretation": "Exploratory conditional label permutation; not a historical randomization test or a corrected significance claim.",
        }

    out = {
        "status": "derived_exploratory",
        "source": str(SOURCE.relative_to(HERE.parent.parent)),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "scope": "21 named seed blocks; 19 rows in four fields with both labels for comparisons; no historical execution trace",
        "rows": sorted(derived, key=lambda r: (r["field_bits"], r["ordinal"], r["label"])),
        "comparisons": comparisons,
    }
    (HERE / "analysis.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    render_scatter(out)
    render_fork()


def render_scatter(out: dict) -> None:
    selected = [r for r in out["rows"] if r["field_bits"] in FIELDS_WITH_BOTH_LABELS]
    left, top, right, bottom = 100, 55, 1020, 555
    xs = {192: 210, 224: 435, 239: 660, 256: 885}
    y0, y1 = 40.0, 56.0

    def y_for(r: dict) -> float:
        pct = 100 * r["b_sign_invariant_popcount"] / r["field_bits"]
        return bottom - (pct - y0) * (bottom - top) / (y1 - y0)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 640">',
        '<rect width="1100" height="640" fill="white"/>',
        '<text x="550" y="28" text-anchor="middle" font-size="20" font-family="sans-serif">Coefficient b bit weight in the 19 labeled comparison curves</text>',
    ]
    for pct in (40, 44, 48, 52, 56):
        yy = bottom - (pct - y0) * (bottom - top) / (y1 - y0)
        parts += [
            f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="#e1e5e9"/>',
            f'<text x="{left-12}" y="{yy+5:.1f}" text-anchor="end" font-size="14" font-family="sans-serif">{pct}%</text>',
        ]
    for bits, xx in xs.items():
        parts.append(f'<text x="{xx}" y="585" text-anchor="middle" font-size="16" font-family="sans-serif">{bits}-bit field</text>')
    occurrence = {}
    for r in selected:
        key = (r["field_bits"], r["label"], r["b_sign_invariant_popcount"])
        offset = occurrence.get(key, 0)
        occurrence[key] = offset + 1
        xx = xs[r["field_bits"]] + (-32 if r["label"] == "published" else 32) + offset * 12
        yy = y_for(r)
        color = "#2067a4" if r["label"] == "published" else "#d47a1c"
        parts.append(f'<circle cx="{xx}" cy="{yy:.1f}" r="8" fill="{color}" stroke="white" stroke-width="1"/>')
    parts += [
        '<circle cx="330" cy="615" r="6" fill="#2067a4"/><text x="345" y="620" font-size="14" font-family="sans-serif">Published (n=8)</text>',
        '<circle cx="560" cy="615" r="6" fill="#d47a1c"/><text x="575" y="620" font-size="14" font-family="sans-serif">Passed over (n=11)</text>',
        '</svg>',
    ]
    (HERE / "b_weight.svg").write_text("\n".join(parts) + "\n")


def render_fork() -> None:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 390">
<rect width="1100" height="390" fill="white"/>
<text x="550" y="32" text-anchor="middle" font-family="sans-serif" font-size="20">What could explain a qualifying block absent from publication?</text>
<rect x="365" y="55" width="370" height="48" rx="8" fill="#eaf0f5" stroke="#506576"/>
<text x="550" y="85" text-anchor="middle" font-family="sans-serif" font-size="15">Block appears in reconstructed lrand48 stream</text>
<line x1="550" y1="103" x2="550" y2="135" stroke="#506576" stroke-width="2"/>
<rect x="372" y="135" width="356" height="48" rx="8" fill="#eaf0f5" stroke="#506576"/>
<text x="550" y="165" text-anchor="middle" font-family="sans-serif" font-size="15">Did original code evaluate this block?</text>
<path d="M 470 183 L 200 215" stroke="#506576" stroke-width="2" fill="none"/>
<path d="M 550 183 L 555 215" stroke="#506576" stroke-width="2" fill="none"/>
<path d="M 630 183 L 900 215" stroke="#506576" stroke-width="2" fill="none"/>
<text x="325" y="202" font-family="sans-serif" font-size="13">Not evaluated</text>
<text x="527" y="202" font-family="sans-serif" font-size="13">Failed</text>
<text x="735" y="202" font-family="sans-serif" font-size="13">Passed</text>
<rect x="35" y="215" width="330" height="105" rx="8" fill="#fff2e3" stroke="#bd761e"/>
<text x="200" y="246" text-anchor="middle" font-family="sans-serif" font-size="15">Stream calls consumed elsewhere,</text>
<text x="200" y="269" text-anchor="middle" font-family="sans-serif" font-size="15">or candidate windows not visited</text>
<text x="200" y="299" text-anchor="middle" font-family="sans-serif" font-size="12">Needs original call trace</text>
<rect x="390" y="215" width="330" height="105" rx="8" fill="#edf4fa" stroke="#426f9b"/>
<text x="555" y="246" text-anchor="middle" font-family="sans-serif" font-size="15">Historical arithmetic, primality,</text>
<text x="555" y="269" text-anchor="middle" font-family="sans-serif" font-size="15">or certification rejected it</text>
<text x="555" y="299" text-anchor="middle" font-family="sans-serif" font-size="12">Needs historical software replay</text>
<rect x="745" y="215" width="330" height="105" rx="8" fill="#f0ecf7" stroke="#745a9a"/>
<text x="910" y="246" text-anchor="middle" font-family="sans-serif" font-size="15">Extra property or manual choice</text>
<text x="910" y="269" text-anchor="middle" font-family="sans-serif" font-size="15">selected another curve</text>
<text x="910" y="299" text-anchor="middle" font-family="sans-serif" font-size="12">Needs a predictive criterion or record</text>
<text x="550" y="362" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#49545d">The published parameters alone do not choose among these branches.</text>
</svg>'''
    (HERE / "selection_fork.svg").write_text(svg + "\n")


if __name__ == "__main__":
    main()
