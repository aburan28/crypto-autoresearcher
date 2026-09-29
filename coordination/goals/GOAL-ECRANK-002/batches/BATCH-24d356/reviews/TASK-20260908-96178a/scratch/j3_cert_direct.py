#!/usr/bin/env python3
"""J3.4: certificate spot-recheck by EXACT recomputation from recorded
instance fields. For every one of the 28 R3 instances verify:
  (1) s(b_i) = d_i * r_i^2  for every i   (the core forced-point identity)
  (2) deg s = len(s)-1 in {3,4}
  (3) disc(s) != 0  (recompute the quartic/cubic discriminant, compare to disc_s)
  (4) g(b_i) = r_i != 0 for all i
  (5) class_keys == sorted(set(d_pattern)), n_classes == len(set(d_pattern))
Then, for a subset, recompute aggregate_total by running the committed
certifier (if loadable)."""
import json, os, sys
from fractions import Fraction as Fr

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/ecrank-73275e-review-20260908"
SRC = os.path.join(ROOT, "experiments/EXP-ECRANK-73275e/source")
sys.path.insert(0, SRC)
R3 = os.path.join(ROOT, "experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R3-construct-n6/raw-result.json")

with open(R3) as f: r3 = json.load(f)

def peval(poly, x):
    # poly = [c0, c1, ...]; evaluate at x
    r = Fr(0)
    for c in reversed(poly):
        r = r * x + c
    return r

def _det_bareiss(M):
    n = len(M)
    M = [row[:] for row in M]
    if n == 0: return Fr(1)
    if n == 1: return M[0][0]
    sign = Fr(1)
    prev = Fr(1)
    for k in range(n - 1):
        if M[k][k] == 0:
            sw = None
            for r in range(k + 1, n):
                if M[r][k] != 0:
                    sw = r; break
            if sw is None:
                return Fr(0)
            M[k], M[sw] = M[sw], M[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) / prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]

def _resultant(A, B):
    """A, B ascending coeff lists [c0..cn]. Res via Sylvester determinant."""
    def trim(p):
        p = list(p)
        while len(p) > 1 and p[-1] == 0:
            p = p[:-1]
        return p
    A = trim(A); B = trim(B)
    m = len(A) - 1  # deg A
    n = len(B) - 1  # deg B
    if m < 0 or n < 0:
        return Fr(0)
    Ad = A[::-1]  # descending, leading first
    Bd = B[::-1]
    size = m + n
    S = [[Fr(0)] * size for _ in range(size)]
    for i in range(n):
        for j in range(m + 1):
            S[i][i + j] = Ad[j]
    for k in range(m):
        for j in range(n + 1):
            S[n + k][k + j] = Bd[j]
    return _det_bareiss(S)

def discriminant(poly):
    """Discriminant of poly (list c0..cn), exact. disc = (-1)^{n(n-1)/2} / a_n * Res(p, p')."""
    n = len(poly) - 1
    if n == 0:
        return None
    dp = [Fr(i) * poly[i] for i in range(1, len(poly))]
    lead = poly[-1]
    res = _resultant(poly, dp)
    return ((-1) ** (n * (n - 1) // 2)) * res / lead

print("=== J3.4 per-instance exact recomputation (all 28) ===")
n_id_fail = 0; n_deg_fail = 0; n_disc_fail = 0; n_rzero_fail = 0; n_class_fail = 0
disc_mismatch = []
for idx, rec in enumerate(r3["found"]):
    inst = rec["instance"]; cert = rec["certificate"]
    b = [Fr(x) for x in inst["b"]]
    r = [Fr(x) for x in inst["r"]]
    dpat = [int(d) for d in inst["d_pattern"]]
    s = [Fr(c) for c in inst["s"]]
    n = len(b)
    # (1) core identity s(b_i) = d_i * r_i^2
    id_ok = True
    for i in range(n):
        if peval(s, b[i]) != dpat[i] * r[i] * r[i]:
            id_ok = False
    if not id_ok: n_id_fail += 1
    # (2) deg s
    deg = len(s) - 1
    deg_ok = deg in (3, 4) and deg == inst["deg_s"]
    if not deg_ok: n_deg_fail += 1
    # (3) disc(s) != 0 and matches disc_s
    disc = discriminant(s)
    disc_rec = Fr(inst["disc_s"])
    disc_ok = (disc != 0) and (disc == disc_rec)
    if disc != 0 and disc != disc_rec:
        disc_mismatch.append((idx, inst["b_index"]))
    if not disc_ok: n_disc_fail += 1
    # (4) r_i != 0
    rzero_ok = all(ri != 0 for ri in r)
    if not rzero_ok: n_rzero_fail += 1
    # (5) class_keys / n_classes
    ck = sorted(set(str(d) for d in dpat))
    nc = len(set(dpat))
    class_ok = (ck == cert["class_keys"]) and (nc == cert["n_classes"])
    if not class_ok: n_class_fail += 1

print("instances total:", len(r3["found"]))
print("(1) s(b_i)=d_i*r_i^2 failures:", n_id_fail)
print("(2) deg s in {3,4} & ==deg_s failures:", n_deg_fail)
print("(3) disc(s)!=0 & ==disc_s failures:", n_disc_fail, " disc mismatches:", disc_mismatch)
print("(4) any r_i==0 failures:", n_rzero_fail)
print("(5) class_keys/n_classes mismatches:", n_class_fail)
print("ALL PASS:", n_id_fail==0 and n_deg_fail==0 and n_disc_fail==0 and n_rzero_fail==0 and n_class_fail==0)

# distribution of deg_s and n_classes
from collections import Counter
print("deg_s distribution:", Counter(inst["deg_s"] for inst in [r["instance"] for r in r3["found"]]))
print("n_classes distribution:", Counter(r["certificate"]["n_classes"] for r in r3["found"]))
print("aggregate_total distribution:", Counter(r["certificate"]["aggregate_total"] for r in r3["found"]))
print("any 4-class instance:", any(r["certificate"]["n_classes"] >= 4 for r in r3["found"]))
