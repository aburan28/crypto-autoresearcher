"""Semaev polynomials S3/S4/S5 for one fixture, charged specialization, and
the C-3 identity checker (S_m == 0 iff the last x is an x-coordinate of a
signed sum of the others, checked by independent point arithmetic)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import labels
from fparith import Fp
from verify import O, VCurve

HERE = Path(__file__).resolve().parent
POLY_FILE = HERE / "semaev_polys.json"


def load_terms(path: Path = POLY_FILE) -> dict:
    return json.loads(Path(path).read_text())


def s3_value(p: int, a: int, b: int, v: int, u: int, x: int) -> int:
    """P1480's S3 formula, verbatim from C-3 (uncharged helper)."""
    return ((u - v) ** 2 * x ** 2 - 2 * ((u + v) * (u * v + a) + 2 * b) * x
            + (u * v - a) ** 2 - 4 * b * (u + v)) % p


def s3_value_charged(F: Fp, a: int, b: int, v: int, u: int, x: int) -> int:
    p = F.p
    d = (u - v) % p
    uv = F.mul(u, v)
    t1 = F.mul(F.sqr(d), F.sqr(x))
    t2 = F.mul(2 * (F.mul((u + v) % p, (uv + a) % p) + 2 * b) % p, x)
    t3 = F.sqr((uv - a) % p)
    t4 = F.mul(4 * b % p, (u + v) % p)
    return (t1 - t2 + t3 - t4) % p


class SemaevFp:
    """Dense coefficient arrays of S4, S5 over F_p for a fixture (a, b)."""

    def __init__(self, p: int, a: int, b: int, terms: dict | None = None):
        terms = terms if terms is not None else load_terms()
        self.p, self.a, self.b = p, a % p, b % p
        self.S4 = self._dense(terms["S4"], 4, terms["degrees"]["S4"])
        self.S5 = self._dense(terms["S5"], 5, terms["degrees"]["S5"])
        self.nonzero = {"S4": int(np.count_nonzero(self.S4)),
                        "S5": int(np.count_nonzero(self.S5))}

    def _dense(self, tl, n, degs):
        p = self.p
        arr = np.zeros(tuple(d + 1 for d in degs), dtype=np.int64)
        apow, bpow = {}, {}
        for t in tl:
            ea, eb = t[0], t[1]
            es = tuple(t[2:2 + n])
            c = t[2 + n]
            if ea not in apow:
                apow[ea] = pow(self.a, ea, p)
            if eb not in bpow:
                bpow[eb] = pow(self.b, eb, p)
            arr[es] = (int(arr[es]) + c % p * apow[ea] % p * bpow[eb]) % p
        return arr

    # -- charged Horner specialization of the LAST axis -------------------
    def spec_last(self, F: Fp, arr: np.ndarray, x: int) -> np.ndarray:
        d = arr.shape[-1] - 1
        p = self.p
        out = arr[..., d].copy()
        for e in range(d - 1, -1, -1):
            out = (out * x + arr[..., e]) % p
        F.count_mul(int(out.size) * d)
        return out

    # -- uncharged exact evaluation (verification only) ------------------
    def eval_full(self, arr: np.ndarray, xs) -> int:
        p = self.p
        cur = arr
        for x in reversed(xs):
            d = cur.shape[-1] - 1
            out = cur[..., d].copy()
            for e in range(d - 1, -1, -1):
                out = (out * x + cur[..., e]) % p
            cur = out
        return int(cur) % p


def identity_check(fx: dict, sem: SemaevFp, ns: str, n_tuples: int = 1000) -> dict:
    """C-3: check S3, S4, S5 against point arithmetic on n_tuples tuples.

    Tuple i draws four liftable points P1..P4 (labels ``identity``). Even i:
    the last coordinate is x(P1 + s2 P2 + ...) for label-drawn signs (a true
    relation); odd i: a uniform x in F_p. The check is the exact iff:
    S_m(x1..x_{m-1}, t) == 0  <=>  t in {x(P1 +- P2 +- ... )} (finite sums).
    """
    p, a, b = fx["p"], fx["a"], fx["b"]
    L, seed = fx["L"], fx["seed"]
    vc = VCurve(p, a, b)
    fails = []
    counts = {"S3": [0, 0], "S4": [0, 0], "S5": [0, 0]}  # [zero, nonzero] observed
    for i in range(n_tuples):
        pts = []
        for k in range(4):
            j = 0
            while True:
                x = labels.uniform(labels.cell_lab(ns, "identity", L, seed, i, f"P{k}r{j}"), p)
                j += 1
                if vc.liftable(x):
                    pts.append(vc.lift(x))
                    break
        for m, poly in ((3, None), (4, sem.S4), (5, sem.S5)):
            base = pts[: m - 1]
            cands = set()
            for mask in range(1 << (m - 2)):
                signs = [1] + [(-1 if (mask >> t) & 1 else 1) for t in range(m - 2)]
                S = vc.sum_signed(list(zip(base, signs)))
                if S is not O:
                    cands.add(S[0])
            if i % 2 == 0:
                mask = labels.uniform(labels.cell_lab(ns, "identity", L, seed, i, f"sign{m}"),
                                      1 << (m - 2))
                signs = [1] + [(-1 if (mask >> t) & 1 else 1) for t in range(m - 2)]
                S = vc.sum_signed(list(zip(base, signs)))
                t_val = S[0] if S is not O else labels.uniform(
                    labels.cell_lab(ns, "identity", L, seed, i, f"x{m}"), p)
            else:
                t_val = labels.uniform(labels.cell_lab(ns, "identity", L, seed, i, f"x{m}"), p)
            xs = [P[0] for P in base] + [t_val]
            if m == 3:
                val = s3_value(p, a, b, xs[0], xs[1], xs[2])
            else:
                val = sem.eval_full(poly, xs)
            is_zero = val == 0
            counts[f"S{m}"][0 if is_zero else 1] += 1
            if is_zero != (t_val in cands):
                fails.append({"tuple": i, "m": m, "xs": xs, "value": val,
                              "t_in_sums": t_val in cands})
    return {"n_tuples": n_tuples, "namespace": ns, "failures": len(fails),
            "failure_examples": fails[:10], "zero_nonzero_counts": counts,
            "passed": not fails}
