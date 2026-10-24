#!/usr/bin/env python3
"""Phase-2 independent replay for EXP-CZLIFT-7c8d73 (validator TASK-20261022-d7d57f).

Producer code is used ONLY to regenerate the seeded sample inputs (lift coefficients
from run.lift_classes, the F_p point from czlift.random_point, the Hensel x-digit eps),
consuming the RNG in the same order as run.measure_curve.  Everything downstream is
the validator's own:
  * p-adic numbers with explicit absolute precision (class Qp below),
  * affine chord-tangent arithmetic on y^2 = x^3 + A x + B over Q_p,
  * the formal-group series w, log_F, exp_F from the SEALED blind module
    (reports/validation-20261022/blind/blind_formal_log.py), correct to z^25,
  * j(E^) exactly over Q, v_p(j - j_cm) capped at 8,
  * the p-torsion construction P~ = P^ - exp_F(log_F(z([p]P^))/p) and its verification
    by computing [p]P~ at high precision.

Outputs per seed: agreement of every row's v_log, v_dj, split, predicted_split,
constructed, verified, reduces with raw-result.json; the size of the producer's series
defect (lambda_true - z mod p^6); the identity-series construction diagnostic; PTM-1.

Run with:  python3 -B independent_replay.py <run_dir> [<run_dir> ...]
"""
from __future__ import annotations

import importlib.util
import json
import os
import random
import sys
from collections import Counter
from fractions import Fraction

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments", "EXP-CZLIFT-7c8d73", "implementation"))

# sealed blind module (series), imported without writing bytecode
_spec = importlib.util.spec_from_file_location("blind_formal_log", os.path.join(HERE, "blind", "blind_formal_log.py"))
blind = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(blind)

# producer code: sampling inputs only
import run as producer_run  # noqa: E402
from harness import czlift as producer_czlift  # noqa: E402
from harness.toycurve import EllipticCurve as ProducerFp  # noqa: E402

NPREC = 40          # absolute p-adic precision of the replay
K = 6               # specification precision
VER_PREC = 5        # hypothesis: [p]P~ = O at precision 5


# ---------------------------------------------------------------------------
# p-adic numbers with absolute precision
# ---------------------------------------------------------------------------
class Qp:
    __slots__ = ("p", "n", "e", "ap")

    def __init__(self, p, n, e, ap):
        self.p = p
        if ap <= e:
            self.n, self.e, self.ap = 0, ap, ap
            return
        m = p ** (ap - e)
        n %= m
        if n == 0:
            self.n, self.e, self.ap = 0, ap, ap
            return
        while n % p == 0:
            n //= p
            e += 1
        self.n, self.e, self.ap = n, e, ap

    @classmethod
    def of(cls, p, x, ap=NPREC):
        x = Fraction(x)
        if x == 0:
            return cls(p, 0, ap, ap)
        num, den = x.numerator, x.denominator
        e = 0
        while num % p == 0:
            num //= p
            e += 1
        while den % p == 0:
            den //= p
            e -= 1
        rel = ap - e
        if rel <= 0:
            return cls(p, 0, ap, ap)
        m = p ** rel
        return cls(p, num * pow(den, -1, m), e, ap)

    def iszero(self):
        return self.n == 0

    def val(self):
        return self.e  # equals ap when zero to precision ("at least ap")

    def __add__(self, o):
        if not isinstance(o, Qp):
            o = Qp.of(self.p, o, self.ap)
        e = min(self.e, o.e)
        ap = min(self.ap, o.ap)
        n = self.n * self.p ** (self.e - e) + o.n * self.p ** (o.e - e)
        return Qp(self.p, n, e, ap)

    __radd__ = __add__

    def __neg__(self):
        return Qp(self.p, -self.n, self.e, self.ap)

    def __sub__(self, o):
        if not isinstance(o, Qp):
            o = Qp.of(self.p, o, self.ap)
        return self + (-o)

    def __rsub__(self, o):
        return Qp.of(self.p, o, self.ap) - self

    def __mul__(self, o):
        if not isinstance(o, Qp):
            o = Qp.of(self.p, o, self.ap + 60)
        e = self.e + o.e
        ap = min(self.ap + o.e, o.ap + self.e)
        return Qp(self.p, self.n * o.n, e, ap)

    __rmul__ = __mul__

    def inv(self):
        if self.n == 0:
            raise ZeroDivisionError("inverse of p-adic zero (to precision)")
        rel = self.ap - self.e
        return Qp(self.p, pow(self.n, -1, self.p ** rel), -self.e, -self.e + rel)

    def __truediv__(self, o):
        if not isinstance(o, Qp):
            o = Qp.of(self.p, o, self.ap + 60)
        return self * o.inv()

    def mod(self, k):
        """integer representative mod p^k (requires e >= 0 and ap >= k)."""
        assert self.ap >= k, (self.ap, k)
        if self.n == 0 or self.e >= k:
            return 0
        assert self.e >= 0
        return (self.n * self.p ** self.e) % self.p ** k


class InfPoint:
    """O to available precision: z-valuation at least `bound`."""

    def __init__(self, bound):
        self.bound = bound


def ec_add(P, Q, A):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    dx = x2 - x1
    if dx.iszero():
        s = y1 + y2
        if s.iszero():
            return InfPoint(min(dx.ap, s.ap))
        raise ArithmeticError("doubling via add")
    lam = (y2 - y1) / dx
    x3 = lam * lam - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return (x3, y3)


def ec_dbl(P, A):
    x, y = P
    lam = (3 * x * x + A) / (2 * y)
    x3 = lam * lam - 2 * x
    y3 = lam * (x - x3) - y
    return (x3, y3)


def ec_neg(P):
    return (P[0], -P[1])


def ec_mul(n, P, A):
    """MSB double-and-add; for n = p only the last addition lands in E1."""
    bits = bin(n)[3:]
    R = P
    for b in bits:
        R = ec_dbl(R, A)
        if b == "1":
            R = ec_add(R, P, A)
            if isinstance(R, InfPoint):
                return R
    return R


def zval_of(T):
    """(v_p(z), z) of a point in E1; for InfPoint returns (bound, None)."""
    if isinstance(T, InfPoint):
        return T.bound, None
    x, y = T
    z = -(x / y)
    return z.val(), z


def series_at(ser, A, B, p, ap):
    return [Qp.of(p, blind.peval(c, A, B), ap) if c else None for c in ser]


def eval_ser(coeffs, z):
    acc = Qp.of(z.p, 0, z.ap)
    zp = z
    for i, c in enumerate(coeffs):
        if i == 0:
            continue
        if c is not None:
            acc = acc + c * zp
        zp = zp * z
    return acc


def j_exact(A, B):
    A, B = Fraction(A), Fraction(B)
    return 1728 * 4 * A ** 3 / (4 * A ** 3 + 27 * B ** 2)


def vcap(x, p, cap):
    v = blind.vp(x, p)
    return cap if v == float("inf") or v >= cap else v


def main():
    W = blind.formal_w()
    OM = blind.invariant_differential(W)
    LG = blind.integrate(OM)
    EX = blind.reversion(LG)

    report = {}
    for run_dir in sys.argv[1:]:
        raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
        man_seed = raw["metrics"]["seed"]
        curves = raw["raw"]["curves"]
        mism = Counter()
        mism_rows = []
        defect_hist = Counter()          # v_p(lambda_true - z) mod p^6 on rows where it is < 6
        defect_rows_lt6 = 0
        identity_construction_zval = Counter()
        true_construction_zval_min = None
        ptm = {"pert_p_rows": 0, "pert_p_nonsplit_by_rule": 0, "pert_p_nonsplit_with_v_z_eq_1": 0,
               "pert_p_nonsplit_constructed_recorded": 0, "pert_p_split_by_rule_rows": [],
               "pert_p_split_lifts": []}
        nrows = 0
        for c in curves:
            D, p, A, B, j_cm = c["D"], c["p"], c["A"], c["B"], c["j_cm"]
            e = c["e"]
            rng = random.Random(man_seed * 999_983 + p)
            Efp = ProducerFp(p, A % p, B % p)
            lifts = producer_run.lift_classes(p, A, B, j_cm, rng, 2)
            ri = 0
            for li, (cls, A2, B2) in enumerate(lifts):
                v_dj = vcap(j_exact(A2, B2) - j_cm, p, 8)
                predicted = v_dj >= 2 * e
                Aq = Qp.of(p, A2, NPREC)
                lg = series_at(LG, A2, B2, p, NPREC)
                ex = series_at(EX, A2, B2, p, NPREC)
                ww = series_at(W, A2, B2, p, NPREC)
                if cls == "pert_p" and predicted:
                    ptm["pert_p_split_lifts"].append({"p": p, "D": D, "lift_index": li, "A2": A2, "B2": B2,
                                                      "v_p(j-j_cm)": v_dj, "e": e})
                for s in range(8):
                    P = producer_czlift.random_point(Efp, rng)
                    eps = rng.randrange(p)
                    row = c["rows"][ri]
                    ri += 1
                    nrows += 1
                    # own Hensel lift at precision NPREC
                    x = Qp.of(p, P[0] + p * eps, NPREC)
                    f = x * x * x + Aq * x + B2
                    y = Qp.of(p, P[1], NPREC)
                    for _ in range(8):
                        y = y - (y * y - f) / (2 * y)
                    assert (y * y - f).val() >= NPREC - 1
                    Ph = (x, y)
                    T = ec_mul(p, Ph, Aq)
                    vz, z = zval_of(T)
                    lam = eval_ser(lg, z)
                    v_lam = min(lam.val(), K)
                    split = v_lam >= 2
                    # producer's lambda equals z mod p^6 (its log_F is the identity mod z^7)
                    d = (lam - z)
                    if d.val() < K:
                        defect_rows_lt6 += 1
                        defect_hist[d.val()] += 1
                    constructed = split
                    verified = reduces = False
                    if split:
                        mu = lam / p
                        zU = eval_ser(ex, mu)
                        wU = eval_ser(ww, zU)
                        U = (zU / wU, -(Qp.of(p, 1, NPREC) / wU))
                        Pt = ec_add(Ph, ec_neg(U), Aq)
                        R = ec_mul(p, Pt, Aq)
                        vR, _ = zval_of(R)
                        verified = vR >= VER_PREC
                        true_construction_zval_min = vR if true_construction_zval_min is None else min(
                            true_construction_zval_min, vR)
                        reduces = (Pt[0].mod(1), Pt[1].mod(1)) == (P[0] % p, P[1] % p)
                        # diagnostic: the identity-series construction (what the producer's series reduces to)
                        mu_id = z / p
                        wI = eval_ser(ww, mu_id)
                        UI = (mu_id / wI, -(Qp.of(p, 1, NPREC) / wI))
                        RI = ec_mul(p, ec_add(Ph, ec_neg(UI), Aq), Aq)
                        identity_construction_zval[(e, A2 % p != 0, zval_of(RI)[0])] += 1
                    mine = {"v_dj": v_dj, "predicted_split": predicted, "v_log": v_lam, "split": split,
                            "constructed": constructed, "verified": verified, "reduces": reduces,
                            "class": cls}
                    for k, v in mine.items():
                        if row[k] != v:
                            mism[k] += 1
                            if len(mism_rows) < 20:
                                mism_rows.append({"p": p, "D": D, "row": ri - 1, "key": k, "recorded": row[k],
                                                  "replayed": v})
                    if cls == "pert_p":
                        ptm["pert_p_rows"] += 1
                        if not predicted:
                            ptm["pert_p_nonsplit_by_rule"] += 1
                            ptm["pert_p_nonsplit_with_v_z_eq_1"] += (vz == 1)
                            ptm["pert_p_nonsplit_constructed_recorded"] += row["constructed"]
                        else:
                            ptm["pert_p_split_by_rule_rows"].append(
                                {"p": p, "D": D, "row": ri - 1, "v_z": vz, "v_lambda": v_lam,
                                 "own_construction_[p]P~_zval": vR if split else None,
                                 "recorded": {k: row[k] for k in ("v_dj", "v_log", "verified", "reduces")}})
        report[os.path.basename(run_dir.rstrip("/"))] = {
            "seed": man_seed,
            "rows_replayed": nrows,
            "field_mismatches": dict(mism),
            "mismatch_examples": mism_rows,
            "producer_series_defect": {
                "rows_where_lambda_true_ne_z_mod_p6": defect_rows_lt6,
                "valuation_hist_of(lambda_true - z)": {str(k): v for k, v in sorted(defect_hist.items())},
            },
            "own_true_series_construction_min_zval_of_[p]P~": true_construction_zval_min,
            "identity_series_construction_zval_hist[(e, A_unit, v_z([p]P~))]": {
                str(k): v for k, v in sorted(identity_construction_zval.items())},
            "PTM-1": ptm,
        }
    json.dump(report, sys.stdout, indent=1, default=str)
    print()


if __name__ == "__main__":
    main()
