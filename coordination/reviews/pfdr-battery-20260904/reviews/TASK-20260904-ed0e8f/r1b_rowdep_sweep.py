#!/usr/bin/env python3
"""R1b (TASK-20260904-ed0e8f, red team): does anything in the hypothesis's OWN
declared quantifier range destroy the fall_dim value?

H-PFDR-4148b8 quantifies: FOR ALL p > 3, FOR ALL s with 2^{m-1} <= s and
2^s <= p, FOR ALL non-singular E/F_p, FOR ALL affine targets x_R,
d_ff = m e + a_0 AND fall_dim(d_ff) = m [C(s,a_0) - C(s,a_0+e)].

The experiment tested p in {4099, 65537} and generic-j planted targets only.
The derivation note (r1_derivation.md) shows fall_dim(d_ff) equals the
top-form kernel dimension only when the rows {x^mu S~} are independent in B,
which fails exactly when some nonzero combination of the degree-(d_ff - delta)
squarefree monomials vanishes on supp(S~) = {omega : S~(omega) != 0}.  That is
an IDEAL-LEVEL (solution-set) quantity, so it is the one channel by which the
curve and the target can reach the meter.

This script sweeps the SMALLEST primes allowed by the hypothesis's own
constraint 2^s <= p, exhaustively over all non-singular curves and all affine
targets, at m = 2 and s in {2, 3}, and reports every (p, a, b, x_R) whose
fall_dim differs from the frozen value.  Exhaustive: no seeds, no sampling.
"""
import json
import sys

sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/"
                   "pfdr-battery-20260904/reviews/TASK-20260904-ed0e8f")
from rt_meter import (deg, top_part, layer_profile, first_fall, digit_forms,
                      S3, pmul)


def sweep(p, s, require_generic_j=False):
    m, e = 2, 2
    n = m * s
    delta = 4
    a0 = (s - e) // 2 + 1
    d_ff_pred = 4 + a0
    from math import comb
    fall_pred = m * (comb(s, a0) - comb(s, a0 + e))
    ells = digit_forms(m, s, p)
    hits = []
    total = 0
    for a in range(p):
        for b in range(p):
            if (4 * a ** 3 + 27 * b ** 2) % p == 0:
                continue
            if require_generic_j and (a % p == 0 or b % p == 0):
                continue
            for xR in range(p):
                g = S3(ells[0], ells[1], {0: xR}, a, b, p)
                total += 1
                if not g:
                    hits.append({"p": p, "s": s, "a": a, "b": b, "x_R": xR,
                                 "d_ff": None, "fall_dim": None,
                                 "note": "generator is identically zero in B"})
                    continue
                prof = layer_profile(g, n, p, d_ff_pred)
                dff, fd = first_fall(prof)
                if dff != d_ff_pred or fd != fall_pred:
                    nsol = sum(1 for w in range(1 << n)
                               if evaluate(g, w, p) == 0)
                    hits.append({"p": p, "s": s, "a": a, "b": b, "x_R": xR,
                                 "d_ff": dff, "fall_dim": fd, "N_sol": nsol,
                                 "gen_degree": deg(g), "profile": prof})
    return {"p": p, "s": s, "instances": total, "d_ff_pred": d_ff_pred,
            "fall_pred": fall_pred, "n_deviating": len(hits),
            "deviating": hits[:40], "generic_j_only": require_generic_j}


def evaluate(f, omega, p):
    """value of f (dict mask->coeff) at the 0/1 point omega (bitmask)."""
    tot = 0
    for mask, c in f.items():
        if mask & ~omega == 0:
            tot += c
    return tot % p


def main():
    out = []
    for p in (5, 7, 11, 13, 17, 19, 23):
        out.append(sweep(p, 2))
    for p in (11, 13, 17):
        out.append(sweep(p, 3))
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
