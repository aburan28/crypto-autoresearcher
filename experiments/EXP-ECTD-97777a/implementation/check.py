"""Independent exact replay of the frozen F_89 coordinate-pair census."""

from __future__ import annotations

import json
import sys
from pathlib import Path

MODULUS = 89


def group_sum(left, right):
    if left is None:
        return right
    if right is None:
        return left
    a, b = left
    c, d = right
    if a == c and (b + d) % MODULUS == 0:
        return None
    if left == right:
        numerator, denominator = 3 * a * a + 1, 2 * b
    else:
        numerator, denominator = d - b, c - a
    gradient = numerator * pow(denominator % MODULUS, MODULUS - 2, MODULUS) % MODULUS
    x = (gradient * gradient - a - c) % MODULUS
    return (x, (gradient * (a - x) - b) % MODULUS)


def expected():
    affine = []
    for x in range(MODULUS):
        rhs = (x * x * x + x + 1) % MODULUS
        affine.extend((x, y) for y in range(MODULUS) if y * y % MODULUS == rhs)
    labels = list(range(MODULUS))
    state = 5140517
    for i in reversed(range(1, MODULUS)):
        state = (1103515245 * state + 12345) & ((1 << 31) - 1)
        j = state % (i + 1)
        labels[j], labels[i] = labels[i], labels[j]
    eligible = 0
    hits, null_hits = [], []
    nonscored = 0
    excluded = {"zero_y": 0, "opposite": 0, "infinite_sum": 0}
    excluded_roundtrip = None
    for i in range(len(affine)):
        u = affine[i]
        for v in affine[i + 1:]:
            if not u[1] or not v[1]:
                excluded["zero_y"] += 1
                reason = "zero_y"
            elif u[0] == v[0] and (u[1] + v[1]) % MODULUS == 0:
                excluded["opposite"] += 1
                reason = "opposite"
            else:
                reason = None
            if reason is not None:
                if excluded_roundtrip is None:
                    sum_excluded = group_sum(u, v)
                    if sum_excluded is not None:
                        excluded_roundtrip = {"pair": [list(u), list(v)], "reason": reason,
                                              "pass": group_sum(sum_excluded, (v[0], -v[1] % MODULUS)) == u}
                continue
            w = group_sum(u, v)
            if w is None:
                excluded["infinite_sum"] += 1
                continue
            if group_sum(w, (v[0], -v[1] % MODULUS)) != u:
                raise AssertionError("group-law round trip failed")
            eligible += 1
            triple = [list(u), list(v), list(w)]
            if w[0] == (u[0] + v[0]) % MODULUS:
                hits.append(triple)
            else:
                nonscored += 1
            if labels[w[0]] == (labels[u[0]] + labels[v[0]]) % MODULUS:
                null_hits.append(triple)
    order = len(affine) + 1
    controls = {"prime": all(MODULUS % d for d in range(2, 10)),
                "nonsingular": (-16 * (4 + 27)) % MODULUS != 0,
                "ordinary": order != MODULUS + 1,
                "hasse_interval": 72 <= order <= 108,
                "roundtrip_all_eligible": True,
                "roundtrip_nonscored": nonscored > 0 or eligible == len(hits),
                "roundtrip_first_excluded": excluded_roundtrip is None or excluded_roundtrip["pass"],
                "pair_partition": eligible + sum(excluded.values()) == len(affine) * (len(affine) - 1) // 2,
                "permutation_bijective": sorted(labels) == list(range(MODULUS))}
    return {"parameters": {"p": 89, "a": 1, "b": 1, "seed": 5140517},
            "point_count": order, "discriminant_mod_p": (-16 * 31) % MODULUS,
            "affine_points": len(affine), "candidate_pairs": len(affine) * (len(affine) - 1) // 2,
            "eligible_pairs": eligible, "exclusion_counts": excluded,
            "first_excluded_roundtrip": excluded_roundtrip,
            "W": len(hits), "permuted_label_count": len(null_hits),
            "hits": hits, "permuted_label_hits": null_hits,
            "permutation": labels, "controls": controls, "valid": all(controls.values())}


def check(run_dir):
    actual = json.loads((run_dir / "raw-result.json").read_text())
    manifest = json.loads((run_dir / "manifest.yaml").read_text())["run"]
    reference = expected()
    for key, value in reference.items():
        if actual.get(key) != value:
            raise AssertionError(f"raw-result mismatch: {key}")
    if not actual["valid"]:
        raise AssertionError("instrument controls failed")
    if manifest["id"] != "RUN-ECTD-63f478" or manifest["experiment_id"] != "EXP-ECTD-97777a":
        raise AssertionError("run binding mismatch")
    for key in ("W", "point_count", "permuted_label_count"):
        if manifest["result"]["metrics"][key] != reference[key]:
            raise AssertionError(f"manifest metric mismatch: {key}")
    print(json.dumps({"valid": True, "W": reference["W"],
                      "permuted_label_count": reference["permuted_label_count"],
                      "point_count": reference["point_count"]}, sort_keys=True))


if __name__ == "__main__":
    check(Path(sys.argv[1]))
