#!/usr/bin/env python3
"""R2 (TASK-20260904-ed0e8f, red team): the exactness / Wilson dependence.

Independent computation of the rank of multiplication by ell^e on the
squarefree TOP-FORM algebra A = F_p[a_1..a_s]/(a_i^2) from degree j to j + e,
for ell = sum_i 2^i a_i (digit) and ell = sum_i a_i (unit).

Three questions the producer's H-WIL table (s <= 8, e = 2, p in {4099, 65537},
112 cells, all full rank) cannot answer:

 (Q1) DYNAMIC RANGE.  Does the rank EVER drop?  A control that can only pass
      is not a control.  The parameter that should destroy it is p: sweep
      p from 2 upward and find the cells where the rank is below
      min(C(s,j), C(s,j+e)).
 (Q2) The reason given in H-PFDR-4148b8 (D4) for full rank under p > s is
      "every binom(k-i, t-i) is a positive integer BELOW p".  Is that true?
      Find (s, j, e, p) with p > s and a diagonal entry binom(r+e, e) >= p,
      and check whether the rank is nevertheless full (which would show the
      stated reason is wrong and the conclusion right, by Kummer/Lucas:
      r + e <= s < p implies p does not divide binom(r+e, e)).
 (Q3) e = 4 (m = 3).  The producer's table is e = 2 only.
"""
import json
import sys
from math import comb
from itertools import combinations

sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/"
                   "pfdr-battery-20260904/reviews/TASK-20260904-ed0e8f")
from rt_meter import rank_mod_p, monomials_of_degree


def amul(f, g, p):
    """product in A = F_p[a]/(a_i^2): overlapping monomials die."""
    out = {}
    for m1, c1 in f.items():
        for m2, c2 in g.items():
            if m1 & m2:
                continue
            m = m1 | m2
            v = (out.get(m, 0) + c1 * c2) % p
            if v:
                out[m] = v
            elif m in out:
                del out[m]
    return out


def ell_pow(s, e, p, kind):
    f = {}
    for i in range(s):
        f[1 << i] = pow(2, i, p) if kind == "digit" else 1
    r = {0: 1}
    for _ in range(e):
        r = amul(r, f, p)
    return r


def rank_mult(s, j, e, p, kind):
    L = ell_pow(s, e, p, kind)
    rows = []
    for mu in monomials_of_degree(s, j):
        rows.append(amul({mu: 1}, L, p))
    return rank_mod_p(rows, p)


def main():
    out = {"Q1_dynamic_range": [], "Q2_entry_above_p": [], "Q3_e4": [],
           "reproduce_producer_table": []}

    # Q1: sweep p including p <= s, e = 2
    for s in range(2, 11):
        for j in range(0, s - 1):
            exp = min(comb(s, j), comb(s, j + 2))
            for p in (2, 3, 5, 7, 11, 13, 4099):
                r = rank_mult(s, j, 2, p, "unit")
                if r != exp:
                    out["Q1_dynamic_range"].append(
                        {"s": s, "j": j, "e": 2, "p": p, "rank": r,
                         "expected": exp, "p_gt_s": p > s,
                         "diag_entries": [comb(rr + 2, 2) for rr in range(j + 1)]})

    # Q2: p > s but some diagonal entry binom(r+e, e) >= p
    for (s, j, e, p) in [(10, 4, 2, 11), (10, 4, 2, 13), (9, 3, 2, 11),
                         (10, 3, 2, 11), (8, 3, 2, 11), (10, 4, 2, 17)]:
        entries = [comb(r + e, e) for r in range(j + 1)]
        exp = min(comb(s, j), comb(s, j + e))
        for kind in ("unit", "digit"):
            r = rank_mult(s, j, e, p, kind)
            out["Q2_entry_above_p"].append(
                {"s": s, "j": j, "e": e, "p": p, "ell": kind, "rank": r,
                 "expected": exp, "full": r == exp,
                 "diag_entries": entries,
                 "max_entry_ge_p": max(entries) >= p,
                 "p_divides_some_entry": any(x % p == 0 for x in entries)})

    # Q3: e = 4 (the m = 3 exponent), never checked by the producer
    for s in range(4, 11):
        for j in range(0, s - 3):
            exp = min(comb(s, j), comb(s, j + 4))
            for p in (5, 7, 11, 13, 65537):
                for kind in ("unit", "digit"):
                    r = rank_mult(s, j, 4, p, kind)
                    if r != exp or p == 65537:
                        out["Q3_e4"].append(
                            {"s": s, "j": j, "e": 4, "p": p, "ell": kind,
                             "rank": r, "expected": exp, "full": r == exp,
                             "p_gt_s": p > s,
                             "e_factorial_mod_p": 24 % p,
                             "diag_entries": [comb(rr + 4, 4) for rr in range(j + 1)]})

    # reproduce the producer's 112-cell table independently
    for p in (4099, 65537):
        for s in range(2, 9):
            for j in range(0, s - 1):
                for kind in ("digit", "unit"):
                    exp = min(comb(s, j), comb(s, j + 2))
                    r = rank_mult(s, j, 2, p, kind)
                    out["reproduce_producer_table"].append(
                        {"p": p, "s": s, "j": j, "ell": kind, "rank": r,
                         "expected": exp, "full": r == exp})
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
