#!/usr/bin/env python3
"""INDEPENDENT verifier of PS0' certificates for EXP-CERTBIN-a58c63 (C-PROPS).

Imports NOTHING from impl/. Rebuilds every certified row from the frozen
object definitions with its own arithmetic (schoolbook carry-less multiply and
reduction; L_V by direct polynomial multiplication of prod_{v in V}(X - v); the
Weil descent of S_3 by its own multilinear expansion) and checks that the
certified combination of rows is EXACTLY the constant polynomial 1:
  regime A: the XOR of the rows mu * f_k (multilinear, D = 3 or 4) is 1;
  regime B: sum_i coef_i * row_i = 1 in F_{2^n}[x_1, x_2].
It also re-checks that the target is unsatisfiable by exhaustive evaluation of
S_3 on V x V with its own arithmetic.

Usage: verify_cert.py --certs <ps0prime-certificates.jsonl.gz> --cells <cells.json> --out <json>
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import sys
import time
from itertools import combinations


def clmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


class GF:
    def __init__(self, n, mod):
        self.n, self.mod = n, mod

    def red(self, a):
        n, m = self.n, self.mod
        while a >> n:
            a ^= m << (a.bit_length() - 1 - n)
        return a

    def mul(self, a, b):
        return self.red(clmul(a, b))


def s3(F, B, x1, x2, x3):
    e = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    return F.mul(e, e) ^ F.mul(F.mul(x1, x2), x3) ^ B


def unsat_by_enumeration(F, B, xR, l):
    for x1 in range(1 << l):
        for x2 in range(1 << l):
            if s3(F, B, x1, x2, xR) == 0:
                return False
    return True


# ---------------- regime B
def LV_product(F, l):
    poly = [1]
    for v in range(1 << l):
        new = [0] * (len(poly) + 1)
        for e, c in enumerate(poly):
            new[e + 1] ^= c
            new[e] ^= F.mul(c, v)
        poly = new
    return {e: c for e, c in enumerate(poly) if c}


def monos_block(d):
    out = []
    for e in range(d + 1):
        for a in range(e, -1, -1):
            out.append((a, e - a))
    return out


def rowsB(F, l, D, g0):
    """All rows of M_D as polynomials {(a, b): coeff}, in the frozen row order."""
    LV = LV_product(F, l)
    rows = []
    for (a, b) in monos_block(D - 4):
        rows.append({(a + i, b + j): c for (i, j), c in g0.items() if c})
    nus = monos_block(D - (1 << l))
    for (a, b) in nus:
        rows.append({(a + e, b): c for e, c in LV.items()})
    for (a, b) in nus:
        rows.append({(a, b + e): c for e, c in LV.items()})
    return rows


def verify_B(cert, cell, F):
    l, D = cell["l"], 66
    B, xR = cell["B"], cert["x_R"]
    xR2 = F.mul(xR, xR)
    g0 = {(2, 2): 1, (2, 0): xR2, (0, 2): xR2, (1, 1): xR, (0, 0): B}
    rows = rowsB(F, l, D, g0)
    acc = {}
    for i, cf in zip(cert["rows"], cert["coeffs"]):
        if i < 0 or i >= len(rows):
            return False, "row index out of range"
        for m, c in rows[i].items():
            v = acc.get(m, 0) ^ F.mul(c, cf)
            if v:
                acc[m] = v
            else:
                acc.pop(m, None)
    ok = acc == {(0, 0): 1}
    return ok, (None if ok else f"combination != 1 ({len(acc)} monomials remain)")


# ---------------- regime A
def descend(F, B, xR, l, n):
    """Equations f_k (k < n) of S_3(x_1, x_2, x_R) after Weil descent, as sets of
    multilinear monomials (sorted index tuples), v_j (j < l) for x_1, v_{l+j} for x_2."""
    # S_3 = (x1x2 + x1xR + x2xR)^2 + x1x2xR + B, expanded over F in Boolean v
    def mono_mul(m1, m2):
        return tuple(sorted(set(m1) | set(m2)))

    def pmul(P, Q):
        out = {}
        for m1, c1 in P.items():
            for m2, c2 in Q.items():
                m = mono_mul(m1, m2)
                out[m] = out.get(m, 0) ^ F.mul(c1, c2)
        return {m: c for m, c in out.items() if c}

    def padd(*Ps):
        out = {}
        for P in Ps:
            for m, c in P.items():
                out[m] = out.get(m, 0) ^ c
        return {m: c for m, c in out.items() if c}

    def scal(P, c):
        return {m: F.mul(v, c) for m, v in P.items() if F.mul(v, c)}

    X1 = {(j,): 1 << j for j in range(l)}
    X2 = {(l + j,): 1 << j for j in range(l)}
    s12 = pmul(X1, X2)
    e = padd(s12, scal(X1, xR), scal(X2, xR))
    sq = pmul(e, e)   # multilinear square (v^2 = v via set union)
    S = padd(sq, scal(s12, xR), {(): B})
    eqs = []
    for k in range(n):
        eqs.append({m for m, c in S.items() if (c >> k) & 1})
    return eqs


def verify_A(cert, cell, F):
    l, n, D = cell["l"], cell["n"], cert["D"]
    eqs = descend(F, cell["B"], cert["x_R"], l, n)
    nv = 2 * l
    mus = []
    for d in range(D - 1):
        mus.extend(combinations(range(nv), d))
    acc = set()
    for i, lab in zip(cert["rows"], cert["row_labels"]):
        a, k = divmod(i, n)
        mu = tuple(mus[a])
        if list(mu) != list(lab[0]) or k != lab[1]:
            return False, f"row {i} label mismatch"
        row = set()
        for m in eqs[k]:
            p = tuple(sorted(set(mu) | set(m)))
            row ^= {p}
        acc ^= row
    ok = acc == {()}
    return ok, (None if ok else f"XOR != 1 ({len(acc)} monomials remain)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certs", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if os.path.exists(args.out):
        print(f"refusing to overwrite {args.out}", file=sys.stderr)
        return 2
    t0 = time.time()
    cells = json.load(open(args.cells))["cells"]
    res = []
    with gzip.open(args.certs, "rt") as f:
        for line in f:
            c = json.loads(line)
            cell = cells[c["cell"]]
            F = GF(cell["n"], cell["modulus_int"])
            unsat = unsat_by_enumeration(F, cell["B"], c["x_R"], cell["l"])
            if c["regime"] == "B":
                ok, why = verify_B(c, cell, F)
            else:
                ok, why = verify_A(c, cell, F)
            res.append({"cell": c["cell"], "regime": c["regime"], "D": c["D"], "idx": c["idx"], "x_R": c["x_R"],
                        "n_rows": len(c["rows"]), "combination_is_one": ok, "target_unsat_by_enumeration": unsat,
                        "pass": bool(ok and unsat), "reason": why})
    out = {"verifier": "verifier/verify_cert.py (imports nothing from impl/)",
           "verifier_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
           "argv": sys.argv, "pid": os.getpid(), "ppid": os.getppid(),
           "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "wall_seconds": time.time() - t0, "n_certificates": len(res),
           "n_pass": sum(r["pass"] for r in res), "all_pass": all(r["pass"] for r in res) and len(res) > 0,
           "imported_modules": sorted(m for m in sys.modules if not m.startswith("_") and "." not in m),
           "results": res}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"n": len(res), "n_pass": out["n_pass"], "all_pass": out["all_pass"]}))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
