#!/usr/bin/env python3
"""TASK-20260813-59c321 (Validator) -- probe 3 of 5.

PREREG-2 2.9 CHECKED AS MATHEMATICS, NOT AS ARITHMETIC ON THE PRODUCER'S
NUMBERS.  The Coordinator's derivation has three steps and each is verified
separately in EXACT RATIONAL ARITHMETIC on cases this probe builds itself:

  (i)   prod_{j=1..k} ||b*_j||^2 = det Gram(b_1..b_k)
        -- verified by running Gram-Schmidt over Fraction on random integer
           row sets, including rank-deficient and near-degenerate ones.
  (ii)  for the frozen families, row i <= k of B is [e_i | A_i], hence
        Gram(b_1..b_k) = I_k + A A^T
        -- verified ENTRYWISE over Fraction on bases built from the frozen
           seeds, at every declared lattice.
  (iii) therefore X_gso_k = (1/k) sum log||b*_j|| = (1/(2k)) log det(I_k+A A^T)
        -- verified by comparing the two sides in exact rational / high
           precision decimal.

Also checked, because a derivation can be right and its ROUTE still wrong:
  (iv)  the claim "det G_k is an integer" -- verified.
  (v)   whether P-GRAM's 1e-10 tolerance is SATISFIABLE BY ANY VALUE AT ALL,
        by the triangle inequality against the disagreement between the two
        committed float64 routes it must simultaneously reproduce (OBJ-1).

Writes exactly one file: its --out path.  Imports nothing from any producer.
"""
import argparse
import json
import math
import sys
from collections import OrderedDict
from decimal import Decimal, localcontext
from fractions import Fraction

import numpy as np

Q = 3329
LATTICES = [("L1", 100, 30), ("L2", 100, 70), ("L4", 140, 40), ("L5", 140, 100),
            ("L7", 20, 6), ("L8", 20, 14), ("L9", 30, 9), ("L10", 30, 21),
            ("L11", 40, 12), ("L12", 40, 28)]


def gram_schmidt_exact(rows):
    """Exact Gram-Schmidt over Fraction.  Returns the list of ||b*_j||^2."""
    star = []
    norms = []
    for v in rows:
        w = list(v)
        for u, n2 in zip(star, norms):
            if n2 == 0:
                continue
            c = sum(a * b for a, b in zip(v, u)) / n2
            w = [wi - c * ui for wi, ui in zip(w, u)]
        n2 = sum(x * x for x in w)
        star.append(w)
        norms.append(n2)
    return norms


def det_exact(M):
    """Exact determinant over Fraction by plain elimination."""
    A = [list(r) for r in M]
    n = len(A)
    sign = Fraction(1)
    det = Fraction(1)
    for i in range(n):
        p = None
        for r in range(i, n):
            if A[r][i] != 0:
                p = r
                break
        if p is None:
            return Fraction(0)
        if p != i:
            A[i], A[p] = A[p], A[i]
            sign = -sign
        det *= A[i][i]
        inv = Fraction(1, 1) / A[i][i]
        for r in range(i + 1, n):
            f = A[r][i] * inv
            if f:
                A[r] = [a - f * b for a, b in zip(A[r], A[i])]
    return sign * det


def make_A(d, k, i, prefix):
    return np.random.default_rng([prefix, d, k, i]).integers(
        0, Q, size=(k, d - k), dtype=np.int64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = OrderedDict()
    R["probe"] = "probe_gram_derivation.py"
    R["task_id"] = "TASK-20260813-59c321"
    R["what"] = "PREREG-2 2.9 verified as mathematics in exact arithmetic"

    # ------------------------------------------------------------------ (i)
    rng = np.random.default_rng([59321, 1])
    step_i = []
    for trial in range(12):
        m = int(rng.integers(2, 7))
        n = int(rng.integers(m, m + 5))
        M = rng.integers(-9, 10, size=(m, n)).tolist()
        if trial == 5:                       # force a rank deficiency
            M[1] = [2 * x for x in M[0]]
        if trial == 9:                       # force a zero row
            M[0] = [0] * n
        rows = [[Fraction(int(x)) for x in r] for r in M]
        norms = gram_schmidt_exact(rows)
        prod = Fraction(1)
        for x in norms:
            prod *= x
        G = [[sum(a * b for a, b in zip(r1, r2)) for r2 in rows]
             for r1 in rows]
        dG = det_exact(G)
        step_i.append({"trial": trial, "shape": [m, n],
                       "prod_of_bstar_norm_squares": str(prod),
                       "det_Gram": str(dG), "equal": prod == dG,
                       "rank_deficient": prod == 0})
    R["step_i_prod_bstar_norm_sq_equals_det_Gram"] = {
        "n_trials": len(step_i), "all_equal": all(t["equal"] for t in step_i),
        "includes_rank_deficient_case":
            any(t["rank_deficient"] for t in step_i),
        "trials": step_i}

    # ----------------------------------------------------------------- (ii)
    step_ii = []
    for lat, d, k in LATTICES:
        A = make_A(d, k, 0, 2)
        B = np.zeros((d, d), dtype=np.int64)
        B[:k, :k] = np.eye(k, dtype=np.int64)
        B[:k, k:] = A
        B[k:, k:] = np.diag(np.full(d - k, Q, dtype=np.int64))
        rows = B[:k, :].astype(object)
        G = rows @ rows.T                       # exact python-int Gram
        claim = np.eye(k, dtype=object) + A.astype(object) @ A.astype(object).T
        step_ii.append({"lattice": lat, "d": d, "k": k,
                        "Gram_k_equals_I_plus_A_AT_entrywise":
                            bool(np.array_equal(G, claim))})
    R["step_ii_Gram_k_equals_I_plus_A_AT"] = {
        "all_lattices": all(s["Gram_k_equals_I_plus_A_AT_entrywise"]
                            for s in step_ii),
        "per_lattice": step_ii}

    # ---------------------------------------------------------------- (iii)
    step_iii = []
    for lat, d, k in [("L7", 20, 6), ("L9", 30, 9), ("L11", 40, 12),
                      ("L12", 40, 28)]:
        A = make_A(d, k, 0, 2)
        B = np.zeros((d, d), dtype=np.int64)
        B[:k, :k] = np.eye(k, dtype=np.int64)
        B[:k, k:] = A
        B[k:, k:] = np.diag(np.full(d - k, Q, dtype=np.int64))
        rows = [[Fraction(int(x)) for x in B[i, :]] for i in range(k)]
        norms = gram_schmidt_exact(rows)        # ||b*_j||^2, exact rationals
        with localcontext() as ctx:
            ctx.prec = 80
            lhs = sum((Decimal(x.numerator) / Decimal(x.denominator)).ln()
                      for x in norms) / (Decimal(2) * Decimal(k))
            Gk = np.eye(k, dtype=object) + A.astype(object) @ A.astype(
                object).T
            dG = det_exact([[Fraction(int(v)) for v in r] for r in Gk])
            rhs = Decimal(int(dG)).ln() / (Decimal(2) * Decimal(k))
            step_iii.append({
                "lattice": lat,
                "lhs_(1/k)sum_log_norm_bstar": str(+lhs),
                "rhs_(1/(2k))log_det(I+AAT)": str(+rhs),
                "abs_diff": str(abs(+lhs - +rhs)),
                "agree_to_1e-60": abs(+lhs - +rhs) < Decimal("1e-60"),
                "det_is_integer": int(dG) == dG})
    R["step_iii_X_gso_k_identity"] = {
        "all_agree": all(s["agree_to_1e-60"] for s in step_iii),
        "det_G_k_is_an_integer_everywhere":
            all(s["det_is_integer"] for s in step_iii),
        "per_lattice": step_iii}

    # ------------------------------------------------------------------ (v)
    # P-GRAM demands ONE value within 1e-10 of BOTH committed float64 routes.
    # By the triangle inequality that is possible only where the two routes
    # themselves differ by at most 2e-10.  Recomputed from OUR OWN float64.
    sat = OrderedDict()
    for lat, d, k in LATTICES:
        worst = 0.0
        for i in range(8):
            A = make_A(d, k, i, 1)           # family F0, seed prefix 1
            B = np.zeros((d, d), dtype=np.int64)
            B[:k, :k] = np.eye(k, dtype=np.int64)
            B[:k, k:] = A
            B[k:, k:] = np.diag(np.full(d - k, Q, dtype=np.int64))
            Rm = np.linalg.qr(B.astype(np.float64).T)[1]
            rq = float(np.sum(np.log(np.abs(np.diag(Rm))[:k])) / k)
            L = np.linalg.cholesky((B @ B.T).astype(np.float64))
            rg = float(np.sum(np.log(np.abs(np.diag(L))[:k])) / k)
            worst = max(worst, abs(rq - rg))
        sat[lat] = {"max_abs_RQ_minus_RG_over_8_bases": worst,
                    "2x_tolerance": 2e-10,
                    "SATISFIABLE_BY_ANY_VALUE": bool(worst <= 2e-10)}
    n_unsat = sum(1 for v in sat.values()
                  if not v["SATISFIABLE_BY_ANY_VALUE"])
    R["step_v_P_GRAM_satisfiability"] = OrderedDict([
        ("rule", ("|x-RQ|<=t and |x-RG|<=t implies |RQ-RG|<=2t; with "
                  "t = 1e-10 the clause is satisfiable at a basis only if the "
                  "two committed float64 routes agree there to 2e-10")),
        ("per_lattice", sat),
        ("n_lattices_where_NO_value_can_satisfy_P_GRAM", n_unsat),
        ("lattices_where_NO_value_can_satisfy_P_GRAM",
         [l for l, v in sat.items() if not v["SATISFIABLE_BY_ANY_VALUE"]]),
        ("conclusion",
         ("P-GRAM as frozen is UNSATISFIABLE at those lattices by ANY exact "
          "route and indeed by any real number whatever; its failure there is "
          "therefore not evidence about the 2.9 derivation")),
    ])

    with open(a.out, "w") as f:
        json.dump(R, f, indent=1, default=str)

    p = print
    p("== (i) prod ||b*_j||^2 == det Gram, exact rationals, %d self-built "
      "trials incl. rank-deficient: %s"
      % (len(step_i), R["step_i_prod_bstar_norm_sq_equals_det_Gram"]
         ["all_equal"]))
    p("== (ii) Gram(b_1..b_k) == I_k + A A^T entrywise at all 10 lattices: %s"
      % R["step_ii_Gram_k_equals_I_plus_A_AT"]["all_lattices"])
    p("== (iii) (1/k)sum log||b*_j|| == (1/(2k)) log det(I+AA^T): %s   "
      "det integer: %s"
      % (R["step_iii_X_gso_k_identity"]["all_agree"],
         R["step_iii_X_gso_k_identity"]["det_G_k_is_an_integer_everywhere"]))
    for s in step_iii:
        p("     %-4s lhs %s" % (s["lattice"], s["lhs_(1/k)sum_log_norm_bstar"]))
        p("          rhs %s  diff %s"
          % (s["rhs_(1/(2k))log_det(I+AAT)"], s["abs_diff"]))
    p("== (v) P-GRAM satisfiability by ANY value")
    for lat, v in sat.items():
        p("     %-4s max|RQ-RG| %.6e  satisfiable: %s"
          % (lat, v["max_abs_RQ_minus_RG_over_8_bases"],
             v["SATISFIABLE_BY_ANY_VALUE"]))
    p("     lattices where NO value can satisfy P-GRAM: %s"
      % R["step_v_P_GRAM_satisfiability"]
        ["lattices_where_NO_value_can_satisfy_P_GRAM"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
