"""EXP-PFDR-011cd0 G4-D: disjoint re-verification of solve certificates (NA-8).

    <PY> experiments/EXP-PFDR-011cd0/verify_solves.py RUN_DIR/solve-certs.jsonl.gz \
        --out RUN_DIR/solve-verify.json

Standard library only.  Shares no code with the solver: its own Miller-Rabin
primality test, its own modular inversion (extended Euclid), its own short
Weierstrass arithmetic in Jacobian coordinates.  For every record
{key, p, a, b, N, P, Q, k} it checks:

  p and N are prime (deterministic Miller-Rabin bases for n < 3.3e24), p > 3,
  4a^3 + 27b^2 != 0 mod p, |N - (p + 1)| <= 2 sqrt(p) (Hasse),
  P and Q lie on y^2 = x^3 + a x + b, P is not the identity,
  N * P is the identity (so P has prime order N),
  0 <= k < N and k * P == Q.

A record passes only if every check holds.  The report lists every failure.
Exit status 0 iff every record passes (and the file holds at least one record
or --allow-empty is given).  Nothing here interprets a result.
"""
from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import json
import math
import sys

DECLARED_IMPORTS = ("argparse", "ast", "gzip", "hashlib", "json", "math", "sys")

# -- arithmetic (independent of crypto_autoresearcher) --------------------------------------

_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for q in _MR_BASES:
        if n % q == 0:
            return n == q
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in _MR_BASES:
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


def inv_mod(x: int, m: int) -> int:
    """Inverse of x mod m by the extended Euclidean algorithm."""
    a, b = x % m, m
    u0, u1 = 1, 0
    while b:
        q = a // b
        a, b = b, a - q * b
        u0, u1 = u1, u0 - q * u1
    if a != 1:
        raise ZeroDivisionError("not invertible")
    return u0 % m


class W:
    """y^2 = x^3 + a x + b over F_p; Jacobian (X, Y, Z), Z = 0 the identity."""

    def __init__(self, p: int, a: int, b: int) -> None:
        self.p, self.a, self.b = p, a % p, b % p

    def on_curve(self, P) -> bool:
        x, y = P
        p = self.p
        return 0 <= x < p and 0 <= y < p and (y * y - (x * x * x + self.a * x + self.b)) % p == 0

    def dbl(self, J):
        X, Y, Z = J
        p = self.p
        if Z == 0 or Y == 0:
            return (1, 1, 0)
        YY = Y * Y % p
        S = 4 * X * YY % p
        ZZ = Z * Z % p
        M = (3 * X * X + self.a * ZZ * ZZ) % p
        X3 = (M * M - 2 * S) % p
        Y3 = (M * (S - X3) - 8 * YY * YY) % p
        Z3 = 2 * Y * Z % p
        return (X3, Y3, Z3)

    def add(self, J1, J2):
        X1, Y1, Z1 = J1
        X2, Y2, Z2 = J2
        p = self.p
        if Z1 == 0:
            return J2
        if Z2 == 0:
            return J1
        Z1Z1 = Z1 * Z1 % p
        Z2Z2 = Z2 * Z2 % p
        U1 = X1 * Z2Z2 % p
        U2 = X2 * Z1Z1 % p
        S1 = Y1 * Z2 * Z2Z2 % p
        S2 = Y2 * Z1 * Z1Z1 % p
        if U1 == U2:
            if S1 != S2:
                return (1, 1, 0)
            return self.dbl(J1)
        H = (U2 - U1) % p
        R = (S2 - S1) % p
        HH = H * H % p
        HHH = H * HH % p
        V = U1 * HH % p
        X3 = (R * R - HHH - 2 * V) % p
        Y3 = (R * (V - X3) - S1 * HHH) % p
        Z3 = H * Z1 * Z2 % p
        return (X3, Y3, Z3)

    def mul(self, k: int, P):
        R = (1, 1, 0)
        A = (P[0], P[1], 1)
        if k < 0:
            k = -k
            A = (P[0], (-P[1]) % self.p, 1)
        while k:
            if k & 1:
                R = self.add(R, A)
            A = self.dbl(A)
            k >>= 1
        return R

    def affine(self, J):
        X, Y, Z = J
        if Z % self.p == 0:
            return None
        p = self.p
        zi = inv_mod(Z, p)
        zi2 = zi * zi % p
        return (X * zi2 % p, Y * zi2 * zi % p)


def verify_record(r: dict) -> list[str]:
    bad = []
    try:
        p, a, b, N, k = (int(r[f]) for f in ("p", "a", "b", "N", "k"))
        P, Q = tuple(r["P"]), tuple(r["Q"])
    except Exception as exc:  # malformed record
        return [f"malformed: {type(exc).__name__}: {exc}"]
    if p <= 3 or not is_prime(p):
        bad.append("p not a prime > 3")
    if not is_prime(N):
        bad.append("N not prime")
    if (4 * a ** 3 + 27 * b ** 2) % p == 0:
        bad.append("singular curve")
    if (N - (p + 1)) ** 2 > 4 * p:
        bad.append("N outside the Hasse interval")
    E = W(p, a, b)
    if not E.on_curve(P):
        bad.append("P not on curve")
    if not E.on_curve(Q):
        bad.append("Q not on curve")
    if bad:
        return bad
    if E.affine(E.mul(N, P)) is not None:
        bad.append("N * P != O")
    if not 0 <= k < N:
        bad.append("k outside [0, N)")
    if E.affine(E.mul(k, P)) != Q:
        bad.append("k * P != Q")
    return bad


def own_imports() -> list[str]:
    tree = ast.parse(open(__file__).read())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            mods.add((node.module or "").split(".")[0])
    mods.discard("__future__")
    return sorted(mods)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("certs", help="solve-certs JSONL (.gz allowed)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-empty", action="store_true",
                    help="a file with no record passes (a run that claims no solve)")
    a = ap.parse_args(argv)
    op = gzip.open if a.certs.endswith(".gz") else open
    records, failures, keys = 0, [], {}
    with op(a.certs, "rt") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            records += 1
            kk = json.dumps(r.get("key"), sort_keys=True)
            keys[kk] = keys.get(kk, 0) + 1
            bad = verify_record(r)
            if bad:
                failures.append({"key": r.get("key"), "reasons": bad})
    imports = own_imports()
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    imports_ok = set(imports) <= set(DECLARED_IMPORTS) and (not stdlib or set(imports) <= stdlib)
    dup = sorted(k for k, v in keys.items() if v > 1)
    ok = (not failures and imports_ok and not dup and (records > 0 or a.allow_empty))
    rep = {"gate": "G4-D", "pass": ok, "certificates_file": a.certs,
           "certificates_sha256": sha256_file(a.certs), "records": records,
           "verified": records - len(failures), "failed": len(failures),
           "failures": failures[:1000], "duplicate_keys": dup[:100],
           "duplicate_key_count": len(dup),
           "verifier": "experiments/EXP-PFDR-011cd0/verify_solves.py",
           "verifier_sha256": sha256_file(__file__),
           "imports": imports, "declared_imports": list(DECLARED_IMPORTS),
           "imports_subset_of_declared_and_stdlib": imports_ok,
           "checks": ["p, N prime (Miller-Rabin, bases 2..41)", "nonsingular", "Hasse",
                      "P, Q on curve", "N*P == O", "0 <= k < N", "k*P == Q"]}
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=2)
    print(json.dumps({k: rep[k] for k in ("gate", "pass", "records", "verified", "failed")}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
