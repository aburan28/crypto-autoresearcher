#!/usr/bin/env python3
"""Independent PS0' certificate verifier for EXP-CERTBIN-3f06d1 (C-PROPS PS0').

Imports NOTHING from experiments/EXP-CERTBIN-3f06d1/impl/ (only the Python
standard library). It rebuilds the descended equations f_k with its own
F_{2^17} arithmetic and its own multilinear polynomial code, and checks that
each certificate -- a set of Macaulay rows (mu, k), deg mu <= D - 2 -- XORs to
the constant polynomial 1:

    sum over certificate rows of  ML(mu * f_k)  ==  1      (over F_2),

where ML is the multilinear reduction v^2 = v. Such a combination is an
algebraic proof that the Boolean system {f_k = 0} (with the field equations)
has no solution, i.e. that the target is unsatisfiable.

Conventions are read from cells.json (field modulus, the cell's curve B and V
basis): Boolean variables v_0..v_17, x_1 = sum_{j<9} v_j b_j,
x_2 = sum_{j<9} v_{9+j} b_j, S_3 = (x_1x_2 + x_1x_R + x_2x_R)^2 + x_1x_2x_R + B,
f_k = the coefficient of t^k.

  python3 experiments/EXP-CERTBIN-3f06d1/verifier/verify_cert.py \
      --certs .../ps0prime-certificates.jsonl.gz --cells .../cells.json \
      --out .../ps0prime-verification.json
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import sys
import time


# ---------------------------------------------------------------------------
# own GF(2^n) arithmetic (carry-less multiply + reduction)
# ---------------------------------------------------------------------------
class GF2n:
    def __init__(self, modulus):
        self.mod = modulus
        self.n = modulus.bit_length() - 1

    def mul(self, a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> self.n:
                a ^= self.mod
        return r


def irreducible(mod):
    """Brute-force check: no polynomial of degree 1..n//2 divides mod."""
    n = mod.bit_length() - 1

    def pdivmod_rem(a, m):
        dm = m.bit_length() - 1
        while a and a.bit_length() - 1 >= dm:
            a ^= m << (a.bit_length() - 1 - dm)
        return a

    for d in range(1, n // 2 + 1):
        for g in range(1 << d, 1 << (d + 1)):
            if pdivmod_rem(mod, g) == 0:
                return False
    return True


# ---------------------------------------------------------------------------
# multilinear polynomials: dict {variable bitmask: coefficient}
# ---------------------------------------------------------------------------
def padd(P, Q, field_add=lambda a, b: a ^ b):
    R = dict(P)
    for m, c in Q.items():
        v = field_add(R.get(m, 0), c)
        if v:
            R[m] = v
        else:
            R.pop(m, None)
    return R


def pmul(K, P, Q):
    R = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            m = m1 | m2  # multilinear: v^2 = v
            v = R.get(m, 0) ^ K.mul(c1, c2)
            if v:
                R[m] = v
            else:
                R.pop(m, None)
    return R


def descended_equations(K, B, xR, basis):
    """Returns f_0..f_{n-1}, each a set of variable bitmasks (Boolean
    polynomial over F_2)."""
    X1 = {1 << j: b for j, b in enumerate(basis) if b}
    X2 = {1 << (9 + j): b for j, b in enumerate(basis) if b}
    XR = {0: xR} if xR else {}
    Bc = {0: B} if B else {}
    e1 = padd(padd(pmul(K, X1, X2), pmul(K, X1, XR)), pmul(K, X2, XR))
    S = padd(padd(pmul(K, e1, e1), pmul(K, pmul(K, X1, X2), XR)), Bc)
    f = [set() for _ in range(K.n)]
    for m, c in S.items():
        for k in range(K.n):
            if (c >> k) & 1:
                f[k] ^= {m}
    return f


def verify_one(cert, cell, K):
    D = cert["D"]
    B = cell["curve"]["B"]
    basis = cell["V"]["basis_b0_to_b8"]
    f = descended_equations(K, B, cert["x_R"], basis)
    acc = set()
    problems = []
    seen = set()
    for mu, k in cert["rows_mu_k"]:
        if not (0 <= k < K.n):
            problems.append(f"equation index {k} out of range")
            continue
        if len(mu) > D - 2 or len(set(mu)) != len(mu) or any(not (0 <= i < 18) for i in mu):
            problems.append(f"multiplier {mu} not a multilinear monomial of degree <= {D - 2}")
            continue
        key = (tuple(sorted(mu)), k)
        if key in seen:
            problems.append(f"row {key} repeated")
        seen.add(key)
        mm = 0
        for i in mu:
            mm |= 1 << i
        row = set()
        for m in f[k]:
            row ^= {m | mm}
        acc ^= row
    ok = (acc == {0}) and not problems
    return {"cell": cert["cell"], "idx": cert["idx"], "x_R": cert["x_R"], "D": D, "n_rows": len(cert["rows_mu_k"]),
            "xor_is_constant_1": acc == {0}, "residual_monomials": len(acc ^ {0}) if acc != {0} else 0,
            "problems": problems, "pass": ok}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


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
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cells = json.load(open(args.cells))
    mod = cells["field"]["modulus_int"]
    K = GF2n(mod)
    mod_ok = irreducible(mod) and mod == (1 << 17) | (1 << 3) | 1
    certs = []
    with gzip.open(args.certs, "rt") as fh:
        for line in fh:
            certs.append(json.loads(line))
    results = [verify_one(c, cells["cells"][c["cell"]], K) for c in certs]
    per_cell = {}
    for r in results:
        pc = per_cell.setdefault(r["cell"], {"certificates": 0, "passed": 0, "failed_idx": []})
        pc["certificates"] += 1
        pc["passed"] += r["pass"]
        if not r["pass"]:
            pc["failed_idx"].append(r["idx"])
    impl_loaded = sorted(m for m, mod_ in sys.modules.items()
                         if getattr(mod_, "__file__", None) and "EXP-CERTBIN-3f06d1/impl" in str(mod_.__file__))
    out = {
        "control": "C-PROPS PS0'", "verifier": "experiments/EXP-CERTBIN-3f06d1/verifier/verify_cert.py",
        "verifier_sha256": sha256_file(os.path.abspath(__file__)),
        "independence": {"imports_from_impl": impl_loaded,
                         "note": "standard library only; own GF(2^17) arithmetic and own multilinear expansion"},
        "inputs": {"certs": args.certs, "certs_sha256": sha256_file(args.certs),
                   "cells": args.cells, "cells_sha256": sha256_file(args.cells)},
        "modulus_irreducible_brute_force": mod_ok,
        "n_certificates": len(results), "n_passed": sum(r["pass"] for r in results),
        "all_pass": mod_ok and bool(results) and all(r["pass"] for r in results),
        "per_cell": per_cell, "results": results,
        "process": {"pid": os.getpid(), "ppid": os.getppid(), "argv": sys.argv, "python": sys.version},
        "started_at": started, "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "wall_seconds": time.time() - t0,
    }
    tmp = args.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(out, fh, indent=1)
    os.replace(tmp, args.out)
    print(json.dumps({"ps0prime_all_pass": out["all_pass"], "n": len(results), "passed": out["n_passed"]}))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
