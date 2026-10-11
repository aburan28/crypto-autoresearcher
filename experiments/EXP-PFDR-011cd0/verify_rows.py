"""EXP-PFDR-011cd0 G4-R: disjoint re-verification of the retained harvest rows of every
sampled instance (curve % 10 == 0) from its bases file.

    <PY> experiments/EXP-PFDR-011cd0/verify_rows.py --run-dir RUN_DIR --out RUN_DIR/row-verify.json

Standard library only; shares no code with the solver, the harvester or verify_solves.py
(its own Jacobian arithmetic and inversion).  Inputs are the run root's merge-report.json
(bases_map: (bits, curve, m, arm) -> bases file; harvest_rows_map: instance key -> harvest
rows file) and rows.jsonl.gz.  For every sampled instance it checks that every base point,
P and Q lie on y^2 = x^3 + a x + b and that every retained row satisfies

    sum_i c_i F_i + kcoef Q == rhs P.

The report lists every failure; exit status 0 iff all pass.  Nothing is interpreted.
"""
from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import json
import os
import sys
from collections import defaultdict

REPO = "/home/user/crypto-autoresearcher"
DECLARED_IMPORTS = ("argparse", "ast", "collections", "gzip", "hashlib", "json", "os", "sys")


def egcd_inv(x: int, m: int) -> int:
    a, b, u0, u1 = x % m, m, 1, 0
    while b:
        q = a // b
        a, b = b, a - q * b
        u0, u1 = u1, u0 - q * u1
    if a != 1:
        raise ZeroDivisionError
    return u0 % m


class Jac:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p, self.a, self.b = p, a % p, b % p
        self.O = (1, 1, 0)

    def on_curve(self, P) -> bool:
        x, y = P
        p = self.p
        return 0 <= x < p and 0 <= y < p and (y * y - x * x * x - self.a * x - self.b) % p == 0

    def double(self, J):
        X, Y, Z = J
        p = self.p
        if Z == 0 or Y == 0:
            return self.O
        Y2 = Y * Y % p
        S = 4 * X * Y2 % p
        Z2 = Z * Z % p
        M = (3 * X * X + self.a * Z2 * Z2) % p
        X3 = (M * M - 2 * S) % p
        return (X3, (M * (S - X3) - 8 * Y2 * Y2) % p, 2 * Y * Z % p)

    def plus(self, A, B):
        X1, Y1, Z1 = A
        X2, Y2, Z2 = B
        p = self.p
        if Z1 == 0:
            return B
        if Z2 == 0:
            return A
        Z1s, Z2s = Z1 * Z1 % p, Z2 * Z2 % p
        U1, U2 = X1 * Z2s % p, X2 * Z1s % p
        S1, S2 = Y1 * Z2 * Z2s % p, Y2 * Z1 * Z1s % p
        if U1 == U2:
            return self.double(A) if S1 == S2 else self.O
        H, R = (U2 - U1) % p, (S2 - S1) % p
        H2 = H * H % p
        H3 = H * H2 % p
        V = U1 * H2 % p
        X3 = (R * R - H3 - 2 * V) % p
        return (X3, (R * (V - X3) - S1 * H3) % p, H * Z1 * Z2 % p)

    def scal(self, k: int, P):
        if k < 0:
            k, P = -k, (P[0], (-P[1]) % self.p)
        R, A = self.O, (P[0], P[1], 1)
        while k:
            if k & 1:
                R = self.plus(R, A)
            A = self.double(A)
            k >>= 1
        return R

    def is_identity(self, J) -> bool:
        return J[2] % self.p == 0

    def equal(self, A, B) -> bool:
        if self.is_identity(A) or self.is_identity(B):
            return self.is_identity(A) and self.is_identity(B)
        p = self.p
        Z1s, Z2s = A[2] * A[2] % p, B[2] * B[2] % p
        return (A[0] * Z2s - B[0] * Z1s) % p == 0 and \
            (A[1] * Z2s * B[2] - B[1] * Z1s * A[2]) % p == 0


def read_jsonl(path: str):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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


def absp(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(REPO, p)


def row_m(r: dict):
    """m of a census row (its `method` is ic_m<m>; harvest rows and bases carry m)."""
    if r.get("m") is not None:
        return r["m"]
    meth = str(r.get("method", ""))
    return int(meth[4:]) if meth.startswith("ic_m") else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sample-mod", type=int, default=10)
    a = ap.parse_args(argv)
    rd = absp(a.run_dir)
    mr = json.load(open(os.path.join(rd, "merge-report.json")))
    rows = list(read_jsonl(os.path.join(rd, "rows.jsonl.gz")))
    sampled = [r for r in rows if r.get("curve") is not None and r["curve"] % a.sample_mod == 0]
    bases: dict = {}
    for f in sorted({v["bases_file"] for v in mr["bases_map"].values()}):
        for b in read_jsonl(absp(f)):
            bases[(b["bits"], b["curve"], b["m"], b["arm"])] = b
    need = defaultdict(set)
    for r in sampled:
        k = json.dumps([r["bits"], r["curve"], row_m(r), r["arm"], r["mode"]])
        ent = mr["harvest_rows_map"].get(k)
        if ent and ent.get("harvest_rows_file"):
            need[ent["harvest_rows_file"]].add(k)
    failures, inst_report = [], {}
    base_checked = set()
    rows_checked = 0
    for r in sampled:
        bk = (r["bits"], r["curve"], row_m(r), r["arm"])
        k = json.dumps([*bk, r["mode"]])
        b = bases.get(bk)
        if b is None:
            failures.append({"key": json.loads(k), "reason": "no bases record for a sampled instance"})
            continue
        if bk not in base_checked:
            E = Jac(b["p"], b["a"], b["b"])
            bad = [i for i, Pt in enumerate(b["points"]) if not E.on_curve(Pt)]
            if bad or not E.on_curve(b["P"]) or not E.on_curve(b["Q"]):
                failures.append({"key": list(bk), "reason": f"point off curve (base indices {bad[:10]})"})
            if "p" in r and (r["p"], r["a"], r["b"], r["N"]) != (b["p"], b["a"], b["b"], b["N"]):
                failures.append({"key": list(bk), "reason": "bases record curve differs from the row's"})
            base_checked.add(bk)
        inst_report[k] = {"rows_checked": 0, "failed": 0}
    by_inst = defaultdict(list)
    for f, keyset in need.items():
        for h in read_jsonl(absp(f)):
            k = json.dumps([h["bits"], h["curve"], h["m"], h["arm"], h["mode"]])
            if k in keyset:
                by_inst[k].append(h)
    for k, hs in by_inst.items():
        bits, c, m, arm, mode = json.loads(k)
        b = bases.get((bits, c, m, arm))
        if b is None:
            continue
        E = Jac(b["p"], b["a"], b["b"])
        F, P, Q = b["points"], b["P"], b["Q"]
        for h in hs:
            S = E.O
            try:
                for i, cc in h["coeffs"]:
                    S = E.plus(S, E.scal(cc, F[i]))
                S = E.plus(S, E.scal(h["kcoef"], Q))
                ok = E.equal(S, E.scal(h["rhs"], P))
            except (IndexError, ZeroDivisionError):
                ok = False
            rows_checked += 1
            inst_report[k]["rows_checked"] += 1
            if not ok:
                inst_report[k]["failed"] += 1
                failures.append({"key": [bits, c, m, arm, mode], "reason": "row identity fails",
                                 "class": h["class"], "attempt": h.get("attempt")})
    imports = own_imports()
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    imports_ok = set(imports) <= set(DECLARED_IMPORTS) and (not stdlib or set(imports) <= stdlib)
    ok = not failures and imports_ok
    rep = {"gate": "G4-R", "pass": ok, "run_dir": os.path.relpath(rd, REPO),
           "sample_rule": f"curve % {a.sample_mod} == 0", "sampled_instances": len(sampled),
           "bases_records_checked": len(base_checked), "rows_checked": rows_checked,
           "failures": failures[:1000], "failure_count": len(failures),
           "per_instance": inst_report,
           "harvest_files_sha256": {f: sha256_file(absp(f)) for f in need},
           "verifier": "experiments/EXP-PFDR-011cd0/verify_rows.py",
           "verifier_sha256": sha256_file(__file__), "imports": imports,
           "imports_subset_of_declared_and_stdlib": imports_ok}
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({k: rep[k] for k in ("gate", "pass", "sampled_instances", "bases_records_checked",
                                          "rows_checked", "failure_count")}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
