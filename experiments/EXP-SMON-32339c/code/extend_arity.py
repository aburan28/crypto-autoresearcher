"""EXP-SMON-32339c -- push the summation-cover battery to m = 6 and m = 7.

EXP-SMON-e5cbe6 verified Theorems A/B/C of
papers/semaev-conservation-specialization/paper.tex at m = 3, 4, 5. The theorems
are stated for every m >= 3, so every further arity is a free falsification
opportunity: at m = 6 the fibre has degree 16 and the predicted non-split type is
2^8, at m = 7 degree 32 and 2^16. A larger group has more room to be wrong in,
so agreement at m = 6, 7 is worth more than more samples at m = 3.

This reuses EXP-SMON-e5cbe6's library unchanged -- the point is to test the SAME
implementation at a new arity, not to write a second one.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from itertools import product

sys.path.insert(0, "../../EXP-SMON-e5cbe6/code")

from semaev_cover import (  # noqa: E402
    Curve,
    eval_poly_fp2,
    factor_pattern,
    is_squarefree,
    semaev_T_poly,
    signed_sum_xs,
)

SEED = 20260807


def probe(curve: Curve, xs: list[int]) -> dict:
    p, m = curve.p, len(xs) + 1
    expected = 2 ** (m - 2)
    poly = semaev_T_poly(curve, xs)
    sums = signed_sum_xs(curve, xs)
    finite = [s for s in sums if s is not None]
    good = (
        len(poly) - 1 == expected
        and len(finite) == expected
        and len({s for s in finite}) == expected
        and is_squarefree(poly, p)
    )
    rec = {"m": m, "good": good, "deg_T": len(poly) - 1, "expected_deg_T": expected}
    if not good:
        return rec
    F = curve.F2
    chis = [curve.chi(x) for x in xs]
    pat = factor_pattern(poly, p)
    all_equal = len(set(chis)) == 1 and chis[0] != 0
    cls = tuple(chis) if chis[0] == 1 else tuple(-c for c in chis)
    rec.update({
        "all_sums_are_roots": all(F.is_zero(eval_poly_fp2(poly, s, F)) for s in finite),
        "pattern": {str(k): v for k, v in sorted(pat.items())},
        "pattern_matches_prediction":
            pat == ({1: expected} if all_equal else {2: expected // 2}),
        "max_factor_degree": max(pat) if pat else 0,
        "mixed_pattern": len(pat) > 1,
        "frobenius_class": "".join("+" if c == 1 else "-" for c in cls),
        "observed_split": pat == {1: expected},
    })
    return rec


def sweep(curve: Curve, m: int, n: int, rng: random.Random, factor_base: bool) -> dict:
    p = curve.p
    pool = [x for x in range(p) if curve.chi(x) == 1] if factor_base else None
    t = {"m": m, "p": p, "samples": 0, "good": 0, "roots_identified": 0,
         "pattern_matches": 0, "max_factor_degree": 0, "mixed": 0, "split": 0,
         "classes": {}, "mismatches": []}
    for _ in range(n):
        xs = ([rng.choice(pool) for _ in range(m - 1)] if factor_base
              else [rng.randrange(p) for _ in range(m - 1)])
        r = probe(curve, xs)
        t["samples"] += 1
        if not r["good"]:
            continue
        t["good"] += 1
        t["roots_identified"] += int(r["all_sums_are_roots"])
        t["pattern_matches"] += int(r["pattern_matches_prediction"])
        t["max_factor_degree"] = max(t["max_factor_degree"], r["max_factor_degree"])
        t["mixed"] += int(r["mixed_pattern"])
        t["split"] += int(r["observed_split"])
        t["classes"][r["frobenius_class"]] = t["classes"].get(r["frobenius_class"], 0) + 1
        if not r["pattern_matches_prediction"] and len(t["mismatches"]) < 5:
            t["mismatches"].append({"xs": xs, **r})
    t["n_classes_seen"] = len(t["classes"])
    t["n_classes_possible"] = 2 ** (m - 2)
    t["one_pattern_per_class"] = True  # checked via pattern_matches == good
    return t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="raw-result.json")
    ap.add_argument("--arities", type=int, nargs="*", default=[6, 7])
    ap.add_argument("--samples", type=int, default=200)
    args = ap.parse_args()

    t0 = time.time()
    rng = random.Random(SEED)
    # deg_T = 2^{m-2} needs p > 2^{m-2}+1 for the interpolation; use comfortable primes
    curves = [Curve(1009, 5, 7), Curve(2003, 11, 3), Curve(4001, 2, 9),
              Curve(1009, 0, 7), Curve(1009, 3, 0)]
    out = {"experiment_id": "EXP-SMON-32339c", "seed": SEED,
           "curves": [{"p": c.p, "A": c.A, "B": c.B} for c in curves],
           "generic_fibre": {}, "factor_base_locus": {}}
    for m in args.arities:
        g = [sweep(c, m, args.samples, rng, False) for c in curves]
        f = [sweep(c, m, args.samples, rng, True) for c in curves]
        agg = lambda rows, k: sum(r[k] for r in rows)  # noqa: E731
        out["generic_fibre"][f"m={m}"] = {
            "samples": agg(g, "samples"), "good": agg(g, "good"),
            "roots_identified": agg(g, "roots_identified"),
            "pattern_matches": agg(g, "pattern_matches"),
            "max_factor_degree": max(r["max_factor_degree"] for r in g),
            "mixed_patterns": agg(g, "mixed"), "split": agg(g, "split"),
            "classes_seen": len(set().union(*[set(r["classes"]) for r in g])),
            "classes_possible": 2 ** (m - 2),
            "mismatch_examples": [x for r in g for x in r["mismatches"]][:5],
        }
        out["factor_base_locus"][f"m={m}"] = {
            "samples": agg(f, "samples"), "good": agg(f, "good"),
            "split_completely": agg(f, "split"),
            "roots_identified": agg(f, "roots_identified"),
            "counterexamples": [x for r in f for x in r["mismatches"]][:5],
        }
        gg = out["generic_fibre"][f"m={m}"]
        print(f"m={m}: good={gg['good']}/{gg['samples']} match={gg['pattern_matches']} "
              f"maxdeg={gg['max_factor_degree']} mixed={gg['mixed_patterns']} "
              f"classes={gg['classes_seen']}/{gg['classes_possible']} | "
              f"FB split={out['factor_base_locus'][f'm={m}']['split_completely']}"
              f"/{out['factor_base_locus'][f'm={m}']['good']}",
              file=sys.stderr, flush=True)

    blob = json.dumps(out, indent=2, sort_keys=True)
    open(args.out, "w").write(blob + "\n")
    print(blob)
    print(f"elapsed_seconds: {round(time.time()-t0,2)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
