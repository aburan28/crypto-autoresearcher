#!/usr/bin/env python3
"""R2 (TASK-20260904-0d66e3): is the deficit meter, AS CONFIGURED FOR THE TWIN,
able to return a nonzero value at the twin's own shape?

Everything below lives in the twin's own ring (mixed: n_sq = 3s squarefree digit
variables, one free u), at s = 3, p = 4099, under the contract's cumulative
convention with koszul(D) = koszul_pair_count, exactly as the twin arms are
measured.  Nothing here is an experiment run; these are constructed objects.

Objects
  T0   the twin itself (curve seed 4101, target 1)                 known 0
  A(g) E1 = h*q1, E2 = h*q2 with deg h = g, deg q_i = 4-g          planted
       non-Koszul syzygy  q2*E1 - q1*E2 = 0  with multiplier degree 4-g,
       hence FIRST VISIBLE AT D = 8 - g   (g = 1, 2, 3)
  B    E1 = the Semaev E1, E2 = h*q with h | E1 forced by construction:
       E2 = q * g1 where g1 is a degree-1 factor planted into BOTH  (variant of A)
  C    E2 = c * E1 (proportional): the degenerate extreme, an upper witness
  D1   E1 = a_0 * q1, E2 = a_0 * q2: the IDEMPOTENT family; besides the A-type
       syzygy the rows m*E_i and (a_0 m)*E_i coincide, an F_p analogue of the
       Boolean duplication that exists at EVERY p in the digit ring
  N    a support-matched-style random pair of quartics (control: expect 0)

For every object: the meter's rows/cols/rank/koszul/deficit at D = 5..8, plus an
INDEPENDENT verification that the planted syzygy really is a dependency among the
rows (the polynomial identity is checked directly).
"""
from __future__ import annotations

import json
import random
import sys

sys.path.insert(0, "/home/user/crypto-autoresearcher")
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3")

from harness.macaulay_fp import Ring, analyze_degrees, deficit_profile  # noqa: E402
from twin_build import twin_generators  # noqa: E402

P, S = 4099, 3
NSQ = 3 * S
DEGS = (5, 6, 7, 8)


def rand_poly(ring: Ring, deg: int, rng: random.Random, density: float = 0.6):
    """Random polynomial of total degree EXACTLY deg (redrawn until the top part
    survives the multilinear reduction)."""
    while True:
        f = {}
        for m in ring.monomials_upto(deg):
            if rng.random() < density:
                c = rng.randrange(1, ring.p)
                f[m] = c
        f = ring.reduce(f)
        if ring.degree(f) == deg:
            return f


def profile(ring: Ring, gens):
    L = analyze_degrees(ring, gens, DEGS[0], DEGS[-1], convention="cumulative")
    d = deficit_profile(L).as_dict()
    return {"degrees": d["degrees"], "rows": d["rows"], "cols": d["cols"], "rank": d["rank"],
            "koszul_pairwise": d["koszul_pairwise"], "deficit_pairwise": d["deficit_pairwise"],
            "deficit_cumulative": d["deficit_cumulative"], "syzygy_dim": d["syzygy_dim"],
            "gen_degrees": [ring.degree(g) for g in gens],
            "gen_terms": [len(g) for g in gens],
            "zero_product_rows": [l.zero_product_rows for l in L]}


def check_syzygy(ring, q2, E1, q1, E2):
    """q2*E1 - q1*E2 == 0 as a polynomial identity in the ring."""
    return ring.sub(ring.mul(q2, E1), ring.mul(q1, E2)) == {}


def main() -> int:
    out = {"ring": {"p": P, "s": S, "n_sq": NSQ, "n_free": 1, "mode": "mixed"},
           "convention": "cumulative", "degrees": list(DEGS), "objects": {}}

    # --- T0 the twin itself ------------------------------------------------
    ring, G = twin_generators(P, S, 2975, 3349, 2292)
    out["objects"]["T0_twin_seed4101_target1"] = profile(ring, G)

    # --- A(g) planted common factor of degree g ----------------------------
    for g in (1, 2, 3):
        rng = random.Random(20260904 + g)
        for attempt in range(40):
            h = rand_poly(ring, g, rng)
            q1 = rand_poly(ring, 4 - g, rng)
            q2 = rand_poly(ring, 4 - g, rng)
            E1p, E2p = ring.mul(h, q1), ring.mul(h, q2)
            if ring.degree(E1p) == 4 and ring.degree(E2p) == 4 and E1p != E2p:
                break
        rec = profile(ring, [E1p, E2p])
        rec["planted"] = {"common_factor_degree": g, "multiplier_degree": 4 - g,
                          "syzygy_first_visible_at_D": 8 - g,
                          "identity_q2E1_minus_q1E2_is_zero": check_syzygy(ring, q2, E1p, q1, E2p)}
        out["objects"][f"A{g}_common_factor_deg{g}"] = rec

    # --- D1 idempotent common factor a_0 (degree 1, an idempotent) ---------
    rng = random.Random(777)
    a0 = {ring.sq_var(0): 1}
    for attempt in range(40):
        q1 = rand_poly(ring, 3, rng)
        q2 = rand_poly(ring, 3, rng)
        E1p, E2p = ring.mul(a0, q1), ring.mul(a0, q2)
        if ring.degree(E1p) == 4 and ring.degree(E2p) == 4:
            break
    rec = profile(ring, [E1p, E2p])
    rec["planted"] = {"common_factor": "a_0 (idempotent)", "syzygy_first_visible_at_D": 7,
                      "identity_q2E1_minus_q1E2_is_zero": check_syzygy(ring, q2, E1p, q1, E2p),
                      "duplication_rows_equal_a0f_and_f": ring.mul_monomial(E1p, ring.sq_var(0)) == E1p}
    out["objects"]["D1_idempotent_factor_a0"] = rec

    # --- C proportional pair (degenerate extreme; the practical ceiling) ---
    E1, E2 = G
    out["objects"]["C_proportional_E2_eq_7E1"] = profile(ring, [E1, ring.scale(E1, 7)])

    # --- N random quartic pair (negative control; expect the twin's answer) -
    rng = random.Random(31337)
    N1 = rand_poly(ring, 4, rng)
    N2 = rand_poly(ring, 4, rng)
    out["objects"]["N_random_quartic_pair"] = profile(ring, [N1, N2])

    # --- B  one Semaev generator + a planted partner sharing a linear factor
    # E1 kept as the true Semaev E1; E2 replaced by  L * q  where L | E1 is FALSE
    # in general, so instead: build the pair (L*E1', L*q) with E1' random cubic and
    # L a random linear form -- reported as A1 above.  Here we do the ASYMMETRIC
    # case the plan named: E2'' = w*E1 + v.  With deg w = 0 this is proportional
    # (object C).  With deg w >= 1 the degree of E2'' exceeds 4, so the plan's
    # literal construction cannot produce a quartic; recorded as a defect of the
    # plan, and the honest substitute is A(g).
    out["plan_construction_B_note"] = (
        "review_plan R2's second family (E2'' = w E1 + v with deg w <= 2 and deg E2'' = 4) "
        "is not constructible: deg(w E1) = deg w + 4 > 4 for deg w >= 1 in this ring, and "
        "deg w = 0 gives a proportional pair (object C). The A(g) family realises the same "
        "intent (a non-Koszul syzygy at a chosen degree) and is used instead.")

    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
