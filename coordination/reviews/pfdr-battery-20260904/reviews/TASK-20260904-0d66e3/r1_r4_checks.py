#!/usr/bin/env python3
"""R1 + R4 mechanical checks (TASK-20260904-0d66e3), independent of the producer code.

R1  (S1) deg E1 = deg E2 = 4 for s >= 2 at every tested (s, p)
    (S3 ii) top(E1) has u-free digit-degree-4 monomials (C(s,2)^2 of them);
            top(E2) = u^2 x_3^2 restricted to degree 4 (C(s,2) monomials, every
            one with u-exponent exactly 2 and block-3 digits only);
            the two top forms share no monomial => linearly independent
    (S2)/(S3 i) f^2 - f = 2 a_0 a_1 != 0 for f = a_0 + a_1
    baseline: koszul_pairwise is EXACT here (two generators => no second syzygy
    to over-count); the residual claim rank = rows - koszul is the heuristic.
    Also: are there zero-product rows (a dropped syzygy)?  Is the kernel at D = 8
    exactly the Koszul line?

R4  (a) null box sizes: |box(E1)|, |box(E2)| against the realised supports
    (b) generator term counts / degree histograms across the six curves
    (c) the singular (non-curve) cubic: does A, B enter the top forms at all?
"""
from __future__ import annotations

import json
import sys
from math import comb

sys.path.insert(0, "/home/user/crypto-autoresearcher")
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3")

from harness.macaulay_fp import analyze_degrees, deficit_profile, layer_rows  # noqa: E402
from twin_build import twin_generators  # noqa: E402

PRIMES = (4099, 16411, 65537)
CURVES = {4099: [(4101, 2975, 3349), (4102, 1174, 2571), (4103, 743, 2019),
                 (4104, 1581, 2498), (4105, 181, 2138), (4106, 3669, 1241)]}


def box_size(s: int, blocks: list[int], u_max: int, total: int) -> int:
    """# monomials multilinear in the named digit blocks with per-block degree <= 2
    (the multidegree of S_3 in each argument) and u-exponent <= u_max, total <= total."""
    from itertools import product
    tot = 0
    per = [[(j, comb(s, j)) for j in range(0, min(2, s) + 1)] for _ in blocks]
    for combo in product(*per):
        dsum = sum(j for j, _ in combo)
        w = 1
        for _, c in combo:
            w *= c
        for e in range(0, u_max + 1):
            if dsum + e <= total:
                tot += w
    return tot


def main() -> int:
    out = {}

    # ---------------- R1 (S1)/(S3) at every tested (s, p) -----------------
    s1s3 = {}
    for p in PRIMES:
        for s in (3, 4, 5, 6):
            ring, (E1, E2) = twin_generators(p, s, 2975 % p, 3349 % p, 2292 % p)
            t1, t2 = ring.top_form(E1), ring.top_form(E2)
            ufree_top1 = [m for m in t1 if m[1] == (0,)]
            u2_only_block3 = all(m[1] == (2,) and (m[0] >> (2 * s)) and not (m[0] & ((1 << (2 * s)) - 1))
                                 for m in t2)
            s1s3[f"s{s}_p{p}"] = {
                "deg_E1": ring.degree(E1), "deg_E2": ring.degree(E2),
                "S1_both_degree_4": ring.degree(E1) == 4 and ring.degree(E2) == 4,
                "n_top_monomials": [len(t1), len(t2)],
                "u_free_degree4_monomials_in_top_E1": len(ufree_top1),
                "expected_C_s_2_squared": comb(s, 2) ** 2,
                "top_E2_all_u2_and_block3_only": u2_only_block3,
                "n_top_E2_expected_C_s_2": comb(s, 2),
                "tops_share_no_monomial": not (set(t1) & set(t2)),
                "E1_has_constant_term": ring.one() in E1,
                "E2_has_constant_term": ring.one() in E2,
            }
    out["R1_S1_S3_mechanical"] = s1s3

    # (S2) / (S3 i)
    ring, _ = twin_generators(4099, 3, 1, 1, 1)
    f = ring.add({ring.sq_var(0): 1}, {ring.sq_var(1): 1})
    out["R1_S2_idempotent_counterexample"] = {
        "f": ring.to_string(f), "f2_minus_f": ring.to_string(ring.sub(ring.mul(f, f), f)),
        "nonzero": ring.sub(ring.mul(f, f), f) != {},
        "note": "the digit ring still HAS idempotents (every digit monomial e satisfies e^2 = e); "
                "what fails is only that an AFFINE form in >= 2 variables is idempotent",
        "a0_is_idempotent": ring.mul({ring.sq_var(0): 1}, {ring.sq_var(0): 1}) == {ring.sq_var(0): 1},
    }

    # baseline exactness + kernel identification at D = 8, all six curves at p = 4099
    ker = {}
    raw = json.load(open("/home/user/crypto-autoresearcher/experiments/EXP-PFDR-20ee58/runs/"
                         "RUN-PFDR-20ee58-s3-p4099/raw-result.json"))
    xr = {}
    for d in raw["raw"]["draws"]:
        if d["arm"] == "semaev":
            xr.setdefault(d["curve_seed"], []).append((d["target_seed"], d["x_R"]))
    for seed, A, B in CURVES[4099]:
        for tseed, xR in xr[seed]:
            ring, G = twin_generators(4099, 3, A, B, xR)
            L = analyze_degrees(ring, G, 5, 8, convention="cumulative")
            pr = deficit_profile(L).as_dict()
            rows, prov, zp = layer_rows(ring, G, 8, convention="cumulative")
            acc = {}
            for m, c in G[1].items():
                acc = ring.add(acc, ring.mul_monomial(G[0], m, c))
            for m, c in G[0].items():
                acc = ring.sub(acc, ring.mul_monomial(G[1], m, c))
            mult = set(ring.monomials_upto(4))
            ker[f"curve{seed}_target{tseed}"] = {
                "rows": pr["rows"], "rank": pr["rank"], "koszul": pr["koszul_pairwise"],
                "deficit": pr["deficit_pairwise"], "zero_product_rows": zp,
                "kernel_dim_D8": pr["rows"][-1] - pr["rank"][-1],
                "koszul_vector_is_a_dependency": acc == {},
                "koszul_vector_rows_are_in_the_row_set": all(m in mult for m in G[0]) and all(m in mult for m in G[1]),
            }
    out["R1_kernel_at_D8_is_the_koszul_line"] = ker
    out["R1_second_syzygy_degree"] = {
        "n_generators": 2, "generator_degrees": [4, 4],
        "first_degree_at_which_koszul_pairwise_can_over_count":
            "d_i + d_j + d_k with three distinct generators; with only two generators there is none, "
            "so koszul_pairwise(D) is EXACT for every D here (contrast: on the binary fixture at p = 2 "
            "the same count over-counts and deficit_pairwise goes negative above D = 5)",
    }

    # ---------------- R4 (a) null boxes -----------------------------------
    boxes = {}
    for s in (3, 4, 5, 6):
        ring, (E1, E2) = twin_generators(4099, s, 2975, 3349, 2292)
        b1 = box_size(s, [1, 2], 2, 4)          # E1: blocks 1,2 and u
        b2 = box_size(s, [3], 2, 4)             # E2: block 3 and u
        boxes[f"s{s}"] = {"box_E1": b1, "realised_terms_E1": len(E1), "missing_E1": b1 - len(E1),
                          "box_E2": b2, "realised_terms_E2": len(E2), "missing_E2": b2 - len(E2),
                          "E2_support_is_full_box": b2 == len(E2)}
    out["R4a_null_boxes"] = boxes

    # ---------------- R4 (b) curve invariance of the template --------------
    tmpl = {}
    for seed, A, B in CURVES[4099]:
        xR = xr[seed][0][1]
        ring, G = twin_generators(4099, 3, A, B, xR)
        tmpl[str(seed)] = {"terms": [len(g) for g in G],
                           "hist": [dict(sorted(ring.degree_histogram(g).items())) for g in G]}
    out["R4b_template_across_curves"] = tmpl
    out["R4b_all_templates_identical"] = len({json.dumps(v, sort_keys=True) for v in tmpl.values()}) == 1

    # ---------------- R4 (c) do A, B enter the top forms? ------------------
    ring, (E1a, E2a) = twin_generators(4099, 3, 2975, 3349, 2292)
    _, (E1b, E2b) = twin_generators(4099, 3, 1915, 2403, 2292)   # singular cubic seed 51 coefficients
    out["R4c_top_forms_independent_of_A_B"] = {
        "top_E1_equal": ring.top_form(E1a) == ring.top_form(E1b),
        "top_E2_equal": ring.top_form(E2a) == ring.top_form(E2b),
        "note": "A and B occur only in monomials of total degree <= 3, so the nearby non-curve object "
                "differs from SEM only below the leading form",
    }

    print(json.dumps(out, indent=1, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
