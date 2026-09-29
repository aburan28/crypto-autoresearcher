#!/usr/bin/env python3
"""proves_too_much control (TASK-20260904-0d66e3).

Run the (S2)-(S3)/"Koszul-only" ARGUMENT, unchanged, against objects on which its
conclusion (deficit 0 at every D <= 8) is KNOWN FALSE, and look for the declared
failure signature.

OBJECT 1  the committed binary chained fixture at n = 12 (deficit known nonzero:
          graded 1 at D = 3, 31 at D = 4; cumulative 32).  Re-measured here with
          the same meter under the same cumulative convention.
          EXTENSION (red team): the same fixture restricted to generator SUBSETS,
          which isolates whether "2 generators" alone forces deficit 0 at p = 2.

OBJECT 2  the prime-field planted-syzygy systems of r2_sensitivity.py.  Here we
          check whether they satisfy the (S2)-(S3) PREMISES verbatim:
            (S2)  no affine P with >= 2 variables is idempotent   [depends on p only]
            (S3i) f^2 - f = 2 a_1 a_2 != 0                        [depends on p only]
            (S3ii) no subset-sum c_1 E_1 + c_2 E_2 degenerates in degree
                   <=> the degree-4 parts are linearly independent
          If the premises hold and the deficit is nonzero, the argument does not
          imply its conclusion, and the step where the implication would have to
          come from is named.

OBJECT 3  the twin itself at p = 2, in two readings:
          3a  verbatim construction in the MIXED ring (free u) at p = 2;
          3b  the pure Boolean reading (u replaced by one Boolean variable, so the
              ring is pure squarefree and f^2 = f holds for every f), which is the
              reading under which the plan's "Frobenius family reappears" is
              testable.
"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "/home/user/crypto-autoresearcher")
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3")

from harness.macaulay_fp import (Ring, analyze_degrees, analyze_layer, deficit_profile,  # noqa: E402
                                 frobenius_count, koszul_pair_count)
from twin_build import s3, leaf, twin_generators  # noqa: E402

FIX = "/home/user/crypto-autoresearcher/harness/macaulay_fp/fixtures/chained_gf2_n12_t3_seed2026.json"


def prof(ring, gens, lo, hi, frobenius=None):
    L = analyze_degrees(ring, gens, lo, hi, convention="cumulative", frobenius=frobenius)
    d = deficit_profile(L).as_dict()
    return {k: d[k] for k in ("degrees", "rows", "cols", "rank", "pred", "koszul_pairwise",
                              "koszul_series", "deficit_pairwise", "deficit_cumulative",
                              "deficit_graded", "syzygy_dim")} | {
        "frobenius_factor": d["frobenius_factor"],
        "zero_product_rows": [l.zero_product_rows for l in L]}


def top_forms_independent(ring, E1, E2):
    """deg(c1 E1 + c2 E2) = max deg for every (c1,c2) != 0  <=>  the top forms are
    linearly independent AND of equal degree."""
    d1, d2 = ring.degree(E1), ring.degree(E2)
    if d1 != d2:
        return {"equal_degree": False, "d1": d1, "d2": d2, "independent": True,
                "note": "unequal degrees: no subset-sum can degenerate below max(d1,d2)"}
    t1, t2 = ring.top_form(E1), ring.top_form(E2)
    # dependent iff t2 = lambda t1
    dep = False
    lam = None
    m0 = next(iter(t1))
    if m0 in t2:
        lam = t2[m0] * pow(t1[m0], -1, ring.p) % ring.p
        dep = ring.sub(t2, ring.scale(t1, lam)) == {}
    return {"equal_degree": True, "d": d1, "independent": not dep, "lambda_if_dependent": lam if dep else None,
            "supports_disjoint": not (set(t1) & set(t2))}


def main() -> int:
    out = {}

    # ---------------- OBJECT 1: binary fixture ----------------------------
    data = json.load(open(FIX))
    ring2 = Ring(2, data["nb"], 0)
    gens = [{(sum(1 << v for v in m), ()): 1 for m in f} for f in data["generators"]]
    degs = [ring2.degree(g) for g in gens]
    quad = [i for i, d in enumerate(degs) if d == 2]
    cub = [i for i, d in enumerate(degs) if d == 3]
    full = prof(ring2, gens, 2, 4)
    out["object1_binary_fixture_full"] = full | {"n_generators": len(gens), "degrees_hist": {2: len(quad), 3: len(cub)},
                                                 "nb": data["nb"], "k": data["k"], "n": data["n"]}

    subsets = {
        "2_gens_quadric_pair": quad[:2],
        "2_gens_one_quadric_one_cubic": [quad[0], cub[0]],
        "2_gens_cubic_pair": cub[:2],
        "4_gens": quad[:2] + cub[:2],
        "8_gens": quad[:4] + cub[:4],
        "12_quadrics_only": quad,
        "12_cubics_only": cub,
        "16_gens": quad[:8] + cub[:8],
        "24_gens_full": list(range(len(gens))),
    }
    sub_out = {}
    for name, idx in subsets.items():
        rows = {}
        for D in (2, 3, 4):
            r = analyze_layer(ring2, gens, D, convention="cumulative", generator_subset=idx)
            rows[str(D)] = {"rows": r.row_count, "rank": r.full_rank, "koszul_pairwise": r.koszul_pairwise,
                            "deficit_pairwise": r.row_count - r.full_rank - r.koszul_pairwise,
                            "zero_product_rows": r.zero_product_rows}
        cum = [rows[str(D)]["deficit_pairwise"] for D in (2, 3, 4)]
        sub_out[name] = {"n_generators": len(idx), "per_degree": rows,
                         "deficit_cumulative_D2_D4": cum,
                         "deficit_graded_D2_D4": [cum[0], cum[1] - cum[0], cum[2] - cum[1]]}
    out["object1_generator_subset_ladder"] = sub_out

    # ---------------- OBJECT 2: planted prime-field systems ---------------
    r2 = json.load(open("/home/user/crypto-autoresearcher/coordination/reviews/"
                        "pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/r2-sensitivity.json"))
    # rebuild the same objects to test the premises (same seeds as r2_sensitivity.py)
    import random
    P, S = 4099, 3
    ring, G = twin_generators(P, S, 2975, 3349, 2292)

    def rand_poly(rg, deg, rng, density=0.6):
        while True:
            f = {}
            for m in rg.monomials_upto(deg):
                if rng.random() < density:
                    f[m] = rng.randrange(1, rg.p)
            f = rg.reduce(f)
            if rg.degree(f) == deg:
                return f

    premises = {}
    # (S2)/(S3i) depend on p only
    f = ring.add({ring.sq_var(0): 1}, {ring.sq_var(1): 1})
    f2mf = ring.sub(ring.mul(f, f), f)
    s2 = {"f_eq_a0_plus_a1": ring.to_string(f), "f2_minus_f": ring.to_string(f2mf),
          "idempotent_law_fails": f2mf != {}}
    for g in (1, 2, 3):
        rng = random.Random(20260904 + g)
        for _ in range(40):
            h = rand_poly(ring, g, rng); q1 = rand_poly(ring, 4 - g, rng); q2 = rand_poly(ring, 4 - g, rng)
            E1p, E2p = ring.mul(h, q1), ring.mul(h, q2)
            if ring.degree(E1p) == 4 and ring.degree(E2p) == 4 and E1p != E2p:
                break
        premises[f"A{g}_common_factor_deg{g}"] = {
            "S2_and_S3i": s2,
            "S3ii_no_degenerate_subset_sum": top_forms_independent(ring, E1p, E2p),
            "measured_deficit_D5_D8": r2["objects"][f"A{g}_common_factor_deg{g}"]["deficit_pairwise"],
            "has_nonzero_constant_term": [ring.one() in E1p, ring.one() in E2p],
        }
    rng = random.Random(777)
    a0 = {ring.sq_var(0): 1}
    for _ in range(40):
        q1 = rand_poly(ring, 3, rng); q2 = rand_poly(ring, 3, rng)
        E1p, E2p = ring.mul(a0, q1), ring.mul(a0, q2)
        if ring.degree(E1p) == 4 and ring.degree(E2p) == 4:
            break
    premises["D1_idempotent_factor_a0"] = {
        "S2_and_S3i": s2,
        "S3ii_no_degenerate_subset_sum": top_forms_independent(ring, E1p, E2p),
        "measured_deficit_D5_D8": r2["objects"]["D1_idempotent_factor_a0"]["deficit_pairwise"],
        "has_nonzero_constant_term": [ring.one() in E1p, ring.one() in E2p],
    }
    premises["T0_twin"] = {
        "S2_and_S3i": s2,
        "S3ii_no_degenerate_subset_sum": top_forms_independent(ring, G[0], G[1]),
        "measured_deficit_D5_D8": r2["objects"]["T0_twin_seed4101_target1"]["deficit_pairwise"],
        "has_nonzero_constant_term": [ring.one() in G[0], ring.one() in G[1]],
    }
    out["object2_premises_vs_conclusion"] = premises

    # ---------------- OBJECT 3: the twin at p = 2 -------------------------
    o3 = {}
    for (A, B, xR) in [(1, 1, 0), (1, 1, 1), (0, 1, 1), (1, 0, 1)]:
        try:
            r2ring, G2 = twin_generators(2, S, A, B, xR)
        except Exception as e:            # pragma: no cover
            o3[f"3a_mixed_p2_A{A}_B{B}_xR{xR}"] = {"error": repr(e)}
            continue
        rec = {"gen_degrees": [r2ring.degree(g) for g in G2],
               "gen_terms": [len(g) for g in G2],
               "gen_rendered": [r2ring.to_string(g, free_names=["u"])[:220] for g in G2],
               "S1_degree_4_claim_holds": [r2ring.degree(g) == 4 for g in G2],
               "frobenius_count_default_D8": frobenius_count(r2ring, [r2ring.degree(g) for g in G2], 8, "cumulative"),
               "frobenius_count_forced_D8": frobenius_count(r2ring, [r2ring.degree(g) for g in G2], 8, "cumulative", frobenius=True),
               "generator_is_idempotent": [r2ring.mul(g, g) == g for g in G2]}
        if all(r2ring.degree(g) >= 0 for g in G2):
            rec["profile_D5_D8"] = prof(r2ring, G2, 5, 8)
            lo = min(r2ring.degree(g) for g in G2)
            rec["profile_from_min_degree"] = prof(r2ring, G2, max(lo, 2), 8)
        o3[f"3a_mixed_p2_A{A}_B{B}_xR{xR}"] = rec

    # 3b: pure Boolean reading, u -> one Boolean variable v (index 3s)
    for (A, B, xR) in [(1, 1, 0), (1, 1, 1)]:
        rb = Ring(2, 3 * S + 1, 0)
        v = {rb.sq_var(3 * S): 1}
        x1, x2, x3 = (leaf(rb, k, S) for k in (1, 2, 3))
        E1 = s3(rb, x1, x2, v, A, B)
        E2 = s3(rb, v, x3, rb.constant(xR), A, B)
        gens_b = [E1, E2]
        dd = [rb.degree(g) for g in gens_b]
        rec = {"gen_degrees": dd, "gen_terms": [len(g) for g in gens_b],
               "S1_degree_4_claim_holds": [d == 4 for d in dd],
               "every_generator_is_idempotent_f2_eq_f": [rb.mul(g, g) == g for g in gens_b],
               "affine_P_idempotent_exists": None,
               "frobenius_count_default_D8": frobenius_count(rb, dd, 8, "cumulative"),
               "koszul_pair_count_D8": koszul_pair_count(rb, dd, 8, "cumulative")}
        # (S2) explicitly: is there an affine P with >= 2 variables and P^2 = P?
        Pf = rb.add({rb.sq_var(0): 1}, {rb.sq_var(1): 1})
        rec["affine_P_idempotent_exists"] = rb.sub(rb.mul(Pf, Pf), Pf) == {}
        lo = max(2, min(dd))
        rec["profile"] = prof(rb, gens_b, lo, 8)
        rec["profile_frobenius_forced"] = prof(rb, gens_b, lo, 8, frobenius=True)
        o3[f"3b_pure_boolean_p2_A{A}_B{B}_xR{xR}"] = rec
    out["object3_twin_at_p2"] = o3

    print(json.dumps(out, indent=1, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
