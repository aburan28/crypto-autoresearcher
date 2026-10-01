"""Honest 2-large-prime relation generator (AMD-20260926-a7d25d C-2, C-3).

Factor base: x-classes x < B (B = ceil(p^{1/5})) that lift to the curve.
Large primes: liftable x-classes B <= x < B2 (B2 = ceil(p^{2/5})).
Scan set S: every point (both signs) with x < B2, sorted by (x, y).

Attempt j: R_j = a_j G + b_j Q. For every P1 in S compute T = R_j - P1 (one
charged group operation each, including the trivial T = O case) and record
every T != O with x(T) < B2. Distinct unordered {P1, T} are decompositions
R_j = P1 + T; the relation kept is the first in scan order (see
implementation.md for this literal reading). A point P1 = R_j (T = O) is a
single-point hit, recorded but not a two-point relation.

Every point operation is charged to the attempt's counter delta. Instance
construction (Q = kG) is counted on a separate, uncharged counter: Q is the
input handed to the attacker.
"""

from __future__ import annotations

import labels
from ecarith import O, Curve, Fp, OpCounter, scalar_mul_charge


def sign_of(y: int, p: int) -> int:
    return 1 if y <= (p - 1) // 2 else -1


def classify(x1: int, x2: int, B: int) -> str:
    n_lp = (x1 >= B) + (x2 >= B)
    return ("full", "lp1", "lp2")[n_lp]


class Generator:
    def __init__(self, fx: dict, prm: dict, ns: str):
        self.fx, self.prm, self.ns = fx, prm, ns
        self.p, self.q = fx["p"], fx["N"]
        self.B, self.B2 = prm["B"], prm["B2"]
        self.bits, self.seed = fx["bits"], fx["seed"]
        self.counter = OpCounter()
        self.F = Fp(self.p, self.counter)
        self.E = Curve(self.F, fx["a"], fx["b"])
        self.G = tuple(fx["G"])
        # instance construction: uncharged counter
        inst_ctr = OpCounter()
        inst_curve = Curve(Fp(self.p, inst_ctr), fx["a"], fx["b"])
        self.k = labels.uniform(labels.target_label(ns, self.bits, self.seed), self.q)
        self.Q = inst_curve.mul(self.k, self.G)
        self.instance_ops = inst_ctr.as_dict()
        # charged setup: enumerate liftable x < B2
        snap = self.counter.snapshot()
        S, fb, lp = [], [], []
        for x in range(self.B2):
            r = self.E.rhs(x)
            if r == 0:
                S.append((x, 0))
            elif self.F.is_square(r):
                y = self.F.sqrt(r)
                S.extend(sorted([(x, y), (x, self.p - y)]))
            else:
                continue
            (fb if x < self.B else lp).append(x)
        self.S = S
        self.fb_x, self.lp_x = fb, lp
        self.L = len(fb)
        self.setup_ops = self.counter.delta(snap)

    def attempt_coeffs(self, j: int) -> tuple[int, int]:
        lbl = labels.attempt_label(self.ns, self.bits, self.seed, j)
        return labels.uniform(lbl + "|a", self.q), labels.uniform(lbl + "|b", self.q)

    def attempt(self, j: int) -> dict:
        a, b = self.attempt_coeffs(j)
        snap = self.counter.snapshot()
        E, p, B2 = self.E, self.p, self.B2
        R = E.add(E.mul(a, self.G), E.mul(b, self.Q))
        rec = {"j": j, "a": a, "b": b}
        if R is O:
            rec.update(outcome="R_is_O", rel=None, n_decomp=0, single_point=False,
                       **_charge(self.counter.delta(snap)))
            return rec
        decomps, seen, single = [], set(), False
        for P1 in self.S:
            T = E.sub(R, P1)
            if T is O:
                single = True
            elif T[0] < B2:
                key = (P1, T) if P1 <= T else (T, P1)
                if key not in seen:
                    seen.add(key)
                    decomps.append((P1, T))
        rel = None
        if decomps:
            P1, T = decomps[0]
            (x1, y1), (x2, y2) = sorted([P1, T])
            rel = [x1, sign_of(y1, p), x2, sign_of(y2, p)]
            outcome = classify(x1, x2, self.B)
        elif single:
            outcome = "single_point_fb" if R[0] < self.B else "single_point_lp"
        else:
            outcome = "miss"
        rec.update(outcome=outcome, rel=rel, n_decomp=len(decomps), single_point=single,
                   **_charge(self.counter.delta(snap)))
        return rec

    def expected_attempt_group_ops(self, a: int, b: int, R_is_O: bool) -> int:
        """Charging formula the audit checks: scalar multiplications, one add,
        plus |S| scan operations unless R_j = O."""
        base = scalar_mul_charge(a) + scalar_mul_charge(b) + 1
        return base if R_is_O else base + len(self.S)

    def header(self) -> dict:
        return {"bits": self.bits, "seed": self.seed, "p": self.p, "q": self.q,
                "a": self.fx["a"], "b": self.fx["b"], "G": list(self.G),
                "B": self.B, "B2": self.B2, "L": self.L, "n_fb_classes": len(self.fb_x),
                "n_lp_classes_liftable": len(self.lp_x), "scan_size": len(self.S),
                "target_k": self.k, "Q": list(self.Q) if self.Q is not O else None,
                "instance_ops_uncharged": self.instance_ops, "setup_ops": self.setup_ops,
                "ns": self.ns}


def _charge(d: dict) -> dict:
    return {"group_ops": d["group_ops"], "W_field": d["W_field"]}


def relations_of(records: list[dict]) -> list[dict]:
    """Two-point relations (full / lp1 / lp2) with their attempt coefficients."""
    return [{"j": r["j"], "a": r["a"], "b": r["b"], "rel": r["rel"], "kind": r["outcome"]}
            for r in records if r["outcome"] in ("full", "lp1", "lp2")]
