#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM PROBE 3 -- COULD P-GRAM HAVE BEEN SATISFIED BY ANY EXACT ROUTE,
AND IS PREREG-2 2.9's DERIVATION RIGHT?

TASK-20260813-85e343 / BATCH-6b6e78 / GOAL-MLKEM-005.  Role: red-team.
CLAIM TIER TOY.  Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost or on any cost model.

THIS IS A PROBE ON THE RED TEAM'S OWN FRAMES.  Not pre-registered.  It rescores
NO frozen verdict: P-GRAM is FALSIFIED and FC-1 FIRED on the committed record
and nothing here changes that.  It measures two different things.

  (A) REACHABILITY.  P-GRAM asks one exact value to reproduce BOTH committed
      float64 routes RQ and RG to 1e-10 absolute.  Two numbers that differ by
      D cannot both be matched to within D/2 by any single third number, so the
      SMALLEST tolerance any exact route could have met is max|RQ - RG| / 2,
      whatever that exact route is.  That quantity is computed here from the
      frozen bases, independently of the lead's implementation.

  (B) THE DERIVATION.  PREREG-2 2.9 claims X_gso_k = (1/(2k)) log det(I_k+A A^T)
      on the frozen families.  This probe checks it TWICE and the second check
      does not use the determinant identity at all:
        exact-det : multi-modular integer determinant of I_k + A A^T (my own
                    CRT implementation, not the lead's), log through decimal;
        exact-GSO : exact RATIONAL Gram-Schmidt of the first k rows, ||b*_j||^2
                    as a Fraction, logs summed -- no determinant anywhere.
      Agreement of the two is a check of the DERIVATION; agreement with RQ or
      RG is a check of the float routes.

RE-EXECUTABLE from the repository root:
    PYTHONDONTWRITEBYTECODE=1 python3 -B <this file> --out <this dir>/probe_pgram_reach_output.json

WRITES exactly one file: the --out path.  No git write, no commit.
"""

import argparse
import decimal
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import OrderedDict
from fractions import Fraction

sys.dont_write_bytecode = True
import numpy as np

T0 = time.time()
TASK_ID = "TASK-20260813-85e343"
GSO_RATIONAL_MAX_D = 40          # exact rational GSO only where it is cheap
PGRAM_TOL = 1e-10                # the frozen PREREG-2 2.9 tolerance


def _repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        return subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return os.path.abspath(".")


REPO = _repo_root()
G5 = "coordination/goals/GOAL-MLKEM-005"
P_MG = os.path.join(REPO, G5, "batches/BATCH-4ed139/tasks/"
                              "TASK-20260812-56b9da/measure_gvar2.py")
P_MF = os.path.join(REPO, G5, "batches/BATCH-4ed139/tasks/"
                              "TASK-20260812-4b8ede/measure_falserefusal.py")
P_A1 = os.path.join(REPO, G5, "batches/BATCH-6b6e78/tasks/"
                              "TASK-20260813-2ce014/results_a1.json")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


MG = load_module(P_MG, "committed_measure_gvar2")
MF = load_module(P_MF, "committed_measure_falserefusal")
Q = MG.Q
N_BASES = MG.N_BASES
LATTICES = MG.LATTICES


def build_basis_F0(d, k, i):
    """The frozen scored family F0 (seed prefix 1), PREREG-2 2.3."""
    A = MG.make_A_seed(d, k, Q, i, 1).copy()
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = np.diag(MG.moduli(d, k, i, "const_q"))
    return B, A


# ----------------------------------------------- exact integer determinant
def _is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def primes_below(start, count):
    out, n = [], start
    while len(out) < count:
        if _is_prime(n):
            out.append(n)
        n -= 2
    return out


def det_mod_p(M, p):
    """det of an integer matrix mod p by elimination with partial pivoting."""
    A = (M % p).astype(np.int64)
    n = A.shape[0]
    det = 1
    for c in range(n):
        piv = -1
        for r in range(c, n):
            if A[r, c] % p:
                piv = r
                break
        if piv < 0:
            return 0
        if piv != c:
            A[[c, piv]] = A[[piv, c]]
            det = (-det) % p
        pv = int(A[c, c]) % p
        det = det * pv % p
        inv = pow(pv, p - 2, p)
        row = (A[c] * inv) % p
        A[c] = row
        if c + 1 < n:
            f = A[c + 1:, c].copy()
            A[c + 1:] = (A[c + 1:] - f[:, None] * row[None, :]) % p
    return det % p


def exact_det(M):
    """Multi-modular determinant with CRT, sized by the Hadamard bound."""
    n = M.shape[0]
    logb = 0.0
    for r in range(n):
        row = M[r].astype(np.float64)
        logb += 0.5 * float(np.log2(max(1.0, float(np.dot(row, row)))))
    need = int(logb) + 4
    ps = primes_below(2 ** 30 - 1, max(2, need // 29 + 2))
    res, mod = 0, 1
    for p in ps:
        r = det_mod_p(M, p)
        # CRT: combine (res mod mod) with (r mod p)
        g = pow(mod % p, p - 2, p)
        t = ((r - res) % p) * g % p
        res = res + mod * t
        mod *= p
    if res > mod // 2:
        res -= mod
    return res, len(ps), logb


def exact_gso_rational(B, k):
    """EXACT rational Gram-Schmidt of the first k rows.  NO determinant is used
    anywhere, so this is independent of PREREG-2 2.9's identity."""
    rows = [[Fraction(int(x)) for x in B[j]] for j in range(k)]
    bstar, norms = [], []
    for j in range(k):
        v = list(rows[j])
        for t in range(j):
            num = sum(a * b for a, b in zip(rows[j], bstar[t]))
            mu = num / norms[t]
            v = [a - mu * b for a, b in zip(v, bstar[t])]
        nn = sum(a * a for a in v)
        bstar.append(v)
        norms.append(nn)
    return norms                       # ||b*_j||^2 as exact Fractions


def ln_fraction(fr, ctx):
    with decimal.localcontext(ctx):
        return decimal.Decimal(fr.numerator).ln() - decimal.Decimal(
            fr.denominator).ln()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    ctx = decimal.Context(prec=60)

    R = OrderedDict()
    R["probe"] = "probe_pgram_reach"
    R["task_id"] = TASK_ID
    R["batch_id"] = "BATCH-6b6e78"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["role"] = "red-team"
    R["claim_tier"] = "toy"
    R["status_of_this_measurement"] = (
        "A PROBE ON THE RED TEAM'S OWN FRAMES. Not pre-registered. It rescores "
        "NO frozen verdict: P-GRAM is FALSIFIED and FC-1 FIRED on the "
        "committed record and nothing here changes that. Nothing here bears on "
        "ML-KEM security, on any FIPS 203 parameter set, on any attack cost or "
        "on any cost model.")
    R["environment"] = OrderedDict([("python", sys.version.split()[0]),
                                    ("numpy", np.__version__)])
    R["inputs_sha256"] = OrderedDict([
        ("measure_gvar2.py (committed lead, BATCH-4ed139)", sha256_file(P_MG)),
        ("measure_falserefusal.py (committed rider ii, BATCH-4ed139)",
         sha256_file(P_MF)),
        ("results_a1.json (committed lead, BATCH-6b6e78)", sha256_file(P_A1))])

    per = OrderedDict()
    worst_gap = 0.0
    worst_cell = None
    print("[A] RQ against RG at binary64, on the frozen F0 bases, and the "
          "exact route computed twice")
    for lat, (d, k) in LATTICES.items():
        t_lat = time.time()
        gaps, dq, dg, agree_det_gso = [], [], [], []
        n_primes = None
        for i in range(N_BASES):
            B, A = build_basis_F0(d, k, i)
            rq, _ = MF.x_gso_k_RQ(B, k)
            rg, _ = MF.x_gso_k_RG(B, k)
            gaps.append(abs(rq - rg))
            # exact via the 2.9 identity, my own multi-modular determinant
            M = np.eye(k, dtype=np.int64) + A @ A.T
            det, np_used, _lb = exact_det(M)
            n_primes = np_used
            with decimal.localcontext(ctx):
                x_det = (decimal.Decimal(det).ln()
                         / (decimal.Decimal(2) * decimal.Decimal(k)))
            dq.append(abs(float(x_det) - rq))
            dg.append(abs(float(x_det) - rg))
            # exact via rational Gram-Schmidt -- no determinant used
            if d <= GSO_RATIONAL_MAX_D and i == 0:
                norms = exact_gso_rational(B, k)
                with decimal.localcontext(ctx):
                    tot = sum((ln_fraction(n2, ctx) for n2 in norms),
                              decimal.Decimal(0))
                    x_gso = tot / (decimal.Decimal(2) * decimal.Decimal(k))
                agree_det_gso.append(float(abs(x_gso - x_det)))
        mg = max(gaps)
        if mg > worst_gap:
            worst_gap, worst_cell = mg, lat
        per[lat] = OrderedDict([
            ("d", d), ("k", k),
            ("max_abs_RQ_minus_RG_over_8_bases", mg),
            ("smallest_tolerance_ANY_single_value_could_meet_for_both",
             mg / 2.0),
            ("frozen_P_GRAM_tolerance", PGRAM_TOL),
            ("P_GRAM_reachable_at_this_lattice", bool(mg / 2.0 <= PGRAM_TOL)),
            ("max_abs_exact_minus_RQ", max(dq)),
            ("max_abs_exact_minus_RG", max(dg)),
            ("n_CRT_primes_used", n_primes),
            ("exact_det_route_vs_exact_rational_GSO_max_abs_diff",
             (max(agree_det_gso) if agree_det_gso else None)),
            ("exact_rational_GSO_run", bool(agree_det_gso)),
            ("wall_clock_seconds", round(time.time() - t_lat, 3))])
        print("    %-4s (d=%3d,k=%3d) max|RQ-RG| = %.4e   min feasible tol = "
              "%.4e   reachable at 1e-10: %-5s   |exact-RQ| = %.3e   "
              "|exact-RG| = %.3e   det-vs-rationalGSO = %s"
              % (lat, d, k, mg, mg / 2.0, mg / 2.0 <= PGRAM_TOL,
                 max(dq), max(dg),
                 ("%.3e" % max(agree_det_gso)) if agree_det_gso else "n/a"))
    R["A_per_lattice"] = per
    R["A_reachability"] = OrderedDict([
        ("frozen_tolerance", PGRAM_TOL),
        ("max_over_lattices_of_abs_RQ_minus_RG", worst_gap),
        ("worst_lattice", worst_cell),
        ("smallest_tolerance_any_exact_route_could_have_met", worst_gap / 2.0),
        ("factor_by_which_the_frozen_bar_is_unreachable",
         (worst_gap / 2.0) / PGRAM_TOL),
        ("n_lattices_where_the_frozen_bar_is_reachable",
         sum(1 for v in per.values()
             if v["P_GRAM_reachable_at_this_lattice"])),
        ("n_lattices_total", len(per)),
        ("argument",
         "P-GRAM requires ONE exact value to sit within 1e-10 of BOTH RQ and "
         "RG. If |RQ - RG| = D then no single value is within D/2 of both, so "
         "no exact route whatever -- correct or incorrect -- can satisfy the "
         "clause where D/2 > 1e-10.")])

    R["B_derivation_check"] = OrderedDict([
        ("claim", "PREREG-2 2.9: X_gso_k = (1/(2k)) log det(I_k + A A^T)"),
        ("check_1", "multi-modular exact integer determinant, my own CRT "
                    "implementation, log through decimal at 60 digits"),
        ("check_2", "exact RATIONAL Gram-Schmidt of the first k rows; "
                    "||b*_j||^2 as Fractions; no determinant used anywhere"),
        ("check_2_scope", "run at d <= %d, basis index 0" % GSO_RATIONAL_MAX_D),
        ("max_abs_disagreement_between_the_two_exact_computations",
         max([v["exact_det_route_vs_exact_rational_GSO_max_abs_diff"]
              for v in per.values()
              if v["exact_det_route_vs_exact_rational_GSO_max_abs_diff"]
              is not None] or [None]))])

    R["wall_clock_seconds"] = round(time.time() - T0, 3)
    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=1, default=str)
        fh.write("\n")
    print("\nwrote %s in %.1f s" % (args.out, R["wall_clock_seconds"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
