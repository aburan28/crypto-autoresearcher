#!/usr/bin/env python3
"""Borderline-sample probes for J2 / tail checks (TASK-20261022-282b02).

1. Identify, per seed, the degenerate rows the recorded degenerate_* metrics drop
   (vQ < vP) and keep-as-failure (vQ > vP), by curve / class / section.
2. Small-p residual-excess tail check: degenerate success vs 1/p per curve for
   p <= 41, and pooled over p <= 19 (the spec's pilot d = +-1 concern).
3. J3 cross-tab: producer curve list vs sealed blind list; producer canonical
   valuation histogram vs blind.
Usage: probe_borderline.py <blind_output.json> <run_dir> [<run_dir> ...]
"""
import json
import math
import sys
from collections import Counter, defaultdict


def main():
    blind = json.load(open(sys.argv[1]))
    out = {}
    blind_list = sorted([[int(D), p] for D, ps in blind["anomalous_primes_by_D_norm_equation"].items() for p in ps],
                        key=lambda t: ([-3, -11, -19, -43, -67, -163].index(t[0]), t[1]))
    for rd in sys.argv[2:]:
        raw = json.load(open(f"{rd}/raw-result.json"))
        dropped = Counter()
        kept_fail = Counter()
        small = defaultdict(lambda: [0, 0, 0.0])
        for c in raw["raw"]["curves"]:
            p = c["p"]
            for r in c["rows"]:
                if r["vP"] >= 2:
                    if r["vQ"] < r["vP"]:
                        dropped[(c["D"], p, r["class"], r["section"])] += 1
                    elif r["vQ"] > r["vP"]:
                        kept_fail[(c["D"], p, r["class"], r["section"])] += 1
                    if r["ratio_defined"] and p <= 41:
                        s = small[(c["D"], p)]
                        s[0] += 1
                        s[1] += int(r["success"])
                        s[2] += 1 / p
        pooled19 = [sum(v[i] for k, v in small.items() if k[1] <= 19) for i in range(3)]
        n, k, ex = pooled19
        var = sum(v[0] * (1 / kk[1]) * (1 - 1 / kk[1]) for kk, v in small.items() if kk[1] <= 19)
        out[rd.rstrip("/").split("/")[-1]] = {
            "dropped_vQ_lt_vP_total": sum(dropped.values()),
            "dropped_by_class": dict(Counter({k2: v for k2, v in
                                              Counter(kk[2] for kk in dropped.elements()).items()})),
            "dropped_by_curve": dict(Counter(f"{kk[0]}:{kk[1]}" for kk in dropped.elements())),
            "kept_as_failure_vQ_gt_vP_total": sum(kept_fail.values()),
            "kept_as_failure_by_curve": dict(Counter(f"{kk[0]}:{kk[1]}" for kk in kept_fail.elements())),
            "small_p_degenerate_success": {f"{kk[0]}:{kk[1]}": {"n": v[0], "succ": v[1], "expected": round(v[2], 3)}
                                           for kk, v in sorted(small.items(), key=lambda t: t[0][1])},
            "pooled_p_le_19": {"n": n, "succ": k, "expected": round(ex, 3),
                               "z_hetero": round((k - ex) / math.sqrt(var), 3)},
            "curve_list_equals_blind": [list(x) for x in raw["metrics"]["curve_list"]] == blind_list,
        }
    out["blind_curve_list"] = blind_list
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
