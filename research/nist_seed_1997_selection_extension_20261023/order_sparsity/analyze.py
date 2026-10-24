#!/usr/bin/env python3
"""Frozen 19-curve group-order sparsity comparison."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUTS = {
    "omitted": (ROOT / "research/nist_seed_skipped_curves_20261016/assessed.json",
                "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841"),
    "published": (ROOT / "research/nist_seed_skipped_curves_20261016/traits.json",
                  "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67"),
}
METRICS = ("n_binary_weight", "n_naf_weight", "gap_binary_weight", "gap_naf_weight")


def naf_weight(n: int) -> int:
    assert n > 0
    weight = 0
    while n:
        if n & 1:
            digit = 2 - (n & 3)
            n -= digit
            weight += 1
        n //= 2
    return weight


def pair_score(pub: int, omit: int) -> int:
    return 2 if pub < omit else 1 if pub == omit else 0


def main() -> None:
    sources = {}
    for key, (path, digest) in INPUTS.items():
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest, key
        sources[key] = json.loads(data)
    omitted = sources["omitted"]["candidate_rows"]
    published = sources["published"]["published_controls"]
    assert len(omitted) == 11 and len(published) == 10
    rows = []
    for label, records in (("omitted", omitted), ("published", published.values())):
        for record in records:
            n = int(record["n_hex"], 16)
            p = int(record["p_hex"], 16)
            ident = record["identity"]
            assert ident["field"]["characteristic"] == p
            assert ident["curve"]["subgroup_order"] == n
            assert ident["curve"]["cofactor"] == 1
            gap = (1 << n.bit_length()) - n
            assert gap > 0
            rows.append({
                "name": next((name for name, r in published.items() if r is record),
                             f"omitted-{record['seed_ordinal_one_based']}"),
                "label": label,
                "curve_uid": ident["curve_uid"],
                "field_bits": p.bit_length(),
                "field_hex": hex(p),
                "timestamp": record["timestamp"],
                "ordinal": record["seed_ordinal_one_based"],
                "n_hex": hex(n),
                "gap_hex": hex(gap),
                "n_binary_weight": n.bit_count(),
                "n_naf_weight": naf_weight(n),
                "gap_binary_weight": gap.bit_count(),
                "gap_naf_weight": naf_weight(gap),
            })
    assert len(rows) == 21 and len({r["curve_uid"] for r in rows}) == 21
    groups = {}
    for row in rows:
        groups.setdefault((row["field_hex"], row["timestamp"]), []).append(row)
    mixed = {key: group for key, group in groups.items()
             if {r["label"] for r in group} == {"omitted", "published"}}
    assert len(mixed) == 4 and sum(len(group) for group in mixed.values()) == 19
    pairs = []
    for group in mixed.values():
        for o, p in itertools.product((r for r in group if r["label"] == "omitted"),
                                      (r for r in group if r["label"] == "published")):
            pairs.append({"omitted_uid": o["curve_uid"], "omitted_name": o["name"],
                          "omitted_ordinal": o["ordinal"], "published_uid": p["curve_uid"],
                          "published_name": p["name"], "published_ordinal": p["ordinal"],
                          "field_bits": o["field_bits"], "earlier_omission": o["ordinal"] < p["ordinal"],
                          **{metric: {"omitted": o[metric], "published": p[metric],
                                      "published_better": p[metric] < o[metric],
                                      "tie": p[metric] == o[metric]}
                             for metric in METRICS}})
    assert len(pairs) == 25 and sum(p["earlier_omission"] for p in pairs) == 16

    allocations = []
    for group in mixed.values():
        pub_count = sum(r["label"] == "published" for r in group)
        allocations.append((group, list(itertools.combinations(range(len(group)), pub_count))))
    assert __import__("math").prod(len(arms) for _, arms in allocations) == 4480
    summary = {}
    for metric in METRICS:
        observed2 = sum(pair_score(p[metric]["published"], p[metric]["omitted"]) for p in pairs)
        all_scores2 = []
        for selected in itertools.product(*(arms for _, arms in allocations)):
            score2 = 0
            for (group, _), pub_idxs in zip(allocations, selected):
                pub_idx = set(pub_idxs)
                for i, j in itertools.product(pub_idx, set(range(len(group))) - pub_idx):
                    score2 += pair_score(group[i][metric], group[j][metric])
            all_scores2.append(score2)
        assert len(all_scores2) == 4480
        tail_count = sum(abs(score2 - 25) >= abs(observed2 - 25) for score2 in all_scores2)
        earlier = [p for p in pairs if p["earlier_omission"]]
        summary[metric] = {"published_better_all_pairs": sum(p[metric]["published_better"] for p in pairs),
                           "ties_all_pairs": sum(p[metric]["tie"] for p in pairs),
                           "published_better_earlier_omission_pairs": sum(p[metric]["published_better"] for p in earlier),
                           "ties_earlier_omission_pairs": sum(p[metric]["tie"] for p in earlier),
                           "earlier_omission_pairs": len(earlier),
                           "allocation_score_twice": observed2,
                           "two_sided_tail_count": tail_count,
                           "allocation_count": 4480}
    result = {"protocol_sha256": hashlib.sha256((HERE / "PROTOCOL.md").read_bytes()).hexdigest(),
              "input_sha256": {k: digest for k, (_, digest) in INPUTS.items()},
              "rows": rows, "pairs": pairs, "summary": summary}
    target = HERE / "analysis.json"
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if target.exists():
        assert target.read_text() == encoded, "immutable analysis.json replay mismatch"
    else:
        target.write_text(encoded)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
