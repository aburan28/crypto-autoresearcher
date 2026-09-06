#!/usr/bin/env python3
"""R1 (TASK-20260904-ed0e8f, red team): the fall_dim identity and the
boundary-cell block-factored-null anomaly.

Computations, all with the independent meter rt_meter.py (no producer code):

 (1) Reproduce the HOMOGENEOUS block-factored null at the two boundary cells
     (2,2,2) and (3,2,4) and at two strict-early-fall cells (2,2,3), (3,2,5).
 (2) Build an INHOMOGENEOUS block-factored null (same homogeneous top part,
     plus random sub-top terms in the same block variables, no curve, no
     target, no x_R) and measure (d_ff, fall_dim) at the same four cells,
     at three sub-top densities.
 (3) FORCING controls (the question the plan does not ask): at the boundary
     cells, is d_ff forced for EVERY generator of that degree?  Measure a
     random dense inhomogeneous polynomial of top degree n = ms whose top
     part is the unique top monomial, with no block structure at all.
 (4) Row-independence diagnostic: rank of the D = d_ff row set (full_rank)
     against the row count, per object.

RNG: python random, seed recorded below.  Producer null seeds (7,11,13,17,19)
are deliberately NOT reused.
"""
import json
import random
import sys
from itertools import combinations

sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/"
                   "pfdr-battery-20260904/reviews/TASK-20260904-ed0e8f")
from rt_meter import (pmul, padd, pscal, deg, top_part, layer_profile,
                      first_fall, monomials_of_degree, rank_mod_p,
                      digit_forms, S3)

SEED = 20260904
CELLS = [(2, 2, 4, 6), (2, 3, 4, 7), (3, 4, 12, 14), (3, 5, 12, 14)]
#         m  s  delta Dmax   delta = m * 2^(m-1) is the generator degree;
#                            Dmax is one past the predicted first fall.
# (v1 of this script passed d_ff in the delta slot for the m = 2 cells, which
#  let add_subtop() write degree-4 terms and so destroyed the block top form at
#  (2,2,3); that object is kept below under the honest name
#  "generic_homogeneous_top" and is a useful extra null.)
PRIMES = [4099, 65537]


def block_form(m, s, e, p, rng):
    """prod_k q_k with q_k a uniformly random homogeneous degree-e form in
    block k's s digit variables (reduced in B = same as in A for a single
    squarefree monomial basis)."""
    g = {0: 1}
    for k in range(m):
        q = {}
        for combo in combinations(range(k * s, (k + 1) * s), e):
            mask = 0
            for i in combo:
                mask |= 1 << i
            q[mask] = rng.randrange(1, p)
        g = pmul(g, q, p)
    return g


def add_subtop(g, n, delta, p, rng, density):
    """add random terms of degree < delta on all n variables (density = the
    fraction of sub-top monomials given a nonzero coefficient)."""
    out = dict(g)
    for d in range(0, delta):
        for mu in monomials_of_degree(n, d):
            if rng.random() < density:
                c = rng.randrange(1, p)
                v = (out.get(mu, 0) + c) % p
                if v:
                    out[mu] = v
                elif mu in out:
                    del out[mu]
    return out


def dense_random_with_top_monomial(n, delta, p, rng):
    """A generator with NO block structure: coefficient on every monomial of
    degree <= delta, with the top part forced nonzero."""
    out = {}
    for d in range(0, delta + 1):
        for mu in monomials_of_degree(n, d):
            out[mu] = rng.randrange(1, p)
    return out


def report(tag, g, n, p, Dmax):
    prof = layer_profile(g, n, p, Dmax)
    dff, fd = first_fall(prof)
    tp = top_part(g)
    return {"object": tag, "p": p, "gen_degree": deg(g), "gen_terms": len(g),
            "top_terms": len(tp), "profile": prof, "d_ff": dff, "fall_dim": fd,
            "rows_at_d_ff": next((r for (D, r, f, t, x) in prof if D == dff), None),
            "full_rank_at_d_ff": next((f for (D, r, f, t, x) in prof if D == dff), None),
            "rows_independent_at_d_ff": next(
                (f == r for (D, r, f, t, x) in prof if D == dff), None)}


def main():
    rng = random.Random(SEED)
    res = []
    for (m, s, delta, Dmax) in CELLS:
        n = m * s
        e = 2 ** (m - 1)
        for p in (PRIMES if m == 2 else [65537]):
            # Semaev arm, for reference (frozen-fixture-like instance)
            if m == 2:
                a, b, xR = 527, 72, 2374
                ells = digit_forms(2, s, p if p == 4099 else 65537)
                if p == 65537:
                    a, b, xR = 5623, 46432, 42063
                g = S3(ells[0], ells[1], {0: xR}, a, b, p)
                res.append(dict(cell=(m, 2, s), **report("semaev", g, n, p, Dmax)))
            # homogeneous block-factored null (the producer's NULL-2 shape)
            for rep in range(2):
                g = block_form(m, s, e, p, rng)
                res.append(dict(cell=(m, 2, s), rep=rep,
                                **report("null2_homogeneous", g, n, p, Dmax)))
            # inhomogeneous block-factored null, three sub-top densities
            for density in (1.0, 0.25, 0.05):
                for rep in range(2):
                    g0 = block_form(m, s, e, p, rng)
                    g = add_subtop(g0, n, delta, p, rng, density)
                    res.append(dict(cell=(m, 2, s), density=density, rep=rep,
                                    **report("null2_inhomogeneous", g, n, p, Dmax)))
            # generic (non-block) homogeneous top form of the same degree
            for rep in range(2):
                gh = {}
                for mu in monomials_of_degree(n, delta):
                    gh[mu] = rng.randrange(1, p)
                g = add_subtop(gh, n, delta, p, rng, 1.0)
                res.append(dict(cell=(m, 2, s), rep=rep,
                                **report("generic_homogeneous_top", g, n, p, Dmax)))
            # forcing control: dense random, no block structure, top degree delta
            if s == e:  # boundary cells only: delta = n, unique top monomial
                for rep in range(2):
                    g = dense_random_with_top_monomial(n, delta, p, rng)
                    res.append(dict(cell=(m, 2, s), rep=rep,
                                    **report("dense_random_no_block", g, n, p, Dmax)))
    json.dump({"seed": SEED, "results": res}, sys.stdout, indent=1, default=str)


if __name__ == "__main__":
    main()
