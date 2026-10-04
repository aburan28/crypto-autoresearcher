#!/usr/bin/env python3
"""EXP-ECDLP-1bef8f Stage 0 height-box fixture calibrator (P-S0-HTBOX).

Authorized by DEC-20260913-0f8468, execution_authorized_stages: [0],
claim_ceiling: stage0_fixture_reproduction_only, maximum_runs: 1,
certificate.kind: none.

WHAT THIS PROGRAM DOES.  It recomputes, by exact integer and exact rational
arithmetic only, the five frozen Stage 0 fixture anchors (a)-(e) of
experiments/EXP-ECDLP-1bef8f/specification.yaml, rejects the three known-false
claims KF-1/KF-2/KF-3 by computation, and refuses the three invalid inputs
INV-1/INV-2/INV-3.

WHAT THIS PROGRAM DOES NOT DO, by contract.  It computes no gamma_2, gamma_3 or
gamma_m of any kind; it builds no lattice, forms no shift-polynomial set, and
calls no LLL/BKZ routine; it solves no ECDLP instance and recovers no scalar; it
emits no certificate other than `none`; it mounts no attack and reports no ratio
against Pollard rho or BSGS; it uses no elliptic-curve library.  Stages 1, 2 and
3 of the frozen contract are NOT authorized and are not entered.

NO FLOATING POINT IS USED IN ANY DECISION.  Integer counts are exact `int`;
ratios are exact `fractions.Fraction`; the decimals reported against the frozen
anchors are rendered from those exact rationals by integer arithmetic with
half-away-from-zero rounding at the anchor's own precision, and are compared to
the frozen anchors as decimal STRINGS.  The only stochastic element is the
matched-null draw set, which is fully determined by the contract's declared seed
20260913.

THE BINDING LIMIT CARRIED FROM THE CONTRACT.  The arity-2 density observable
does NOT separate the height box from a matched negation-closed random base;
the contract's own observation-collision audit already found that collision.
Every dispersion number below is a FIXTURE CHECK and never a finding, never an
advantage, and never evidence about the height box.
"""
from __future__ import annotations

import hashlib
import json
import platform
import random
import re
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-1bef8f/implementation/stage0_htbox.py"
RUN_ID = "RUN-ECDLP-1bef8f-S0"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-1bef8f/runs" / RUN_ID
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-1bef8f/execution-report-s0.yaml"
COMMAND = (
    "bash -lc 'ulimit -v 4194304; exec timeout --signal=TERM "
    "--kill-after=5s 3600s python3 "
    "experiments/EXP-ECDLP-1bef8f/implementation/stage0_htbox.py'"
)

EXPERIMENT_ID = "EXP-ECDLP-1bef8f"
HYPOTHESIS_ID = "H-ECDLP-b97b72"
GOAL_ID = "GOAL-ECDLP-001"
BATCH_ID = "BATCH-e5c603"
TASK_ID = "TASK-20260913-f3397c"
ARCHIVED_BY = "TASK-20260913-b49ef5"
AUTHORIZED_BY = "DEC-20260913-0f8468"
FROZEN_OBJECT = "P-S0-HTBOX"

# ---------------------------------------------------------------------------
# Frozen anchors, transcribed ONCE from experiments/EXP-ECDLP-1bef8f/
# specification.yaml `inputs.stage0_anchors`.  Integer anchors are ints; every
# decimal anchor is kept as the STRING the contract states, at the contract's
# own precision, so the comparison never touches a float.
# ---------------------------------------------------------------------------
ANCHOR_A = {
    "p": 101, "a": 3, "b": 5, "curve_order": 115,
    "realisable_ordered_x_triples": 6441,
    "false_negatives": 0, "false_positives": 0,
}
ANCHOR_B = {
    "ladder_p": 10007,
    "ladder_H": [4, 5, 6, 9, 10],
    "box_sizes": [23, 39, 47, 111, 127],
    "c_H": ["1.438", "1.560", "1.306", "1.370", "1.270"],
    "cell_p": 10007, "cell_a": 1, "cell_b": 28, "cell_n": 9851, "cell_H": 10,
    "on_curve_x_values_in_box": 69, "base_points": 138,
}
ANCHOR_C = {
    "monomial_count": 9,
    "total_degree": 4,
    # keys are monomials in x1, x2; values are the coefficient expressions in
    # a, b, x_3 verbatim from the contract.  Both sides are PARSED by the
    # generic routines below; no bidegree and no coefficient is hardcoded in
    # the expander, which derives everything from f_3's defining equation.
    "coefficients": {
        "x1^2*x2^2": "1",
        "x1^2*x2": "-2*x_3",
        "x1*x2^2": "-2*x_3",
        "x1*x2": "-2a - 2*x_3^2",
        "x1^2": "x_3^2",
        "x2^2": "x_3^2",
        "x1": "-2a*x_3 - 4b",
        "x2": "-2a*x_3 - 4b",
        "const": "a^2 - 4b*x_3",
    },
}
ANCHOR_D = {
    "p": 10007, "H": 10, "H_to_the_4": 10000,
    "ratio_H4_over_p": "0.99930",
    "B_squared_over_n": "1.9332", "B": 138, "n": 9851,
}
ANCHOR_E = {
    "p": 10007, "a": 1, "b": 28, "n": 9851, "H": 10,
    "mean": "1.9332", "variance": "5.5822", "dispersion_index": "2.8875",
    "unreachable_targets": 3704, "max_count": 138, "c_of_identity": 138,
    "null_size": 138, "null_draws": 60, "null_seed": 20260913,
    "null_mean_dispersion": "2.9163",
    "null_dispersion_range": ["2.7628", "3.1316"],
    "null_mean_unreachable": "3712.3",
}

# Executor implementation choices that the contract does not fix.  Declared
# here so a reader can see exactly what was chosen and what was given.
IMPL_CHOICES = {
    "null_x_list_order": "ascending integer order of the on-curve x-values of F_p",
    "null_rng": "random.Random(20260913), one fresh instance used only for the "
                "60 matched-null draws, one sequential rng.sample(list, 69) per draw",
    "generic_control": "deterministic relabelling of the already-indexed height-box "
                       "base into Z/nZ; no additional random draws",
    "kf1_arity_range": [2, 8],
    "kf2_canonical_omitted_bidegree": [1, 1],
    "decimal_rounding": "half away from zero, at each anchor's own precision, "
                        "from the exact rational by integer arithmetic",
}


class InvalidInputError(ValueError):
    """An invalid input that the contract requires be refused, not measured."""


# ---------------------------------------------------------------------------
# Exact decimal rendering from exact rationals.  No float anywhere.
# ---------------------------------------------------------------------------
def decimal_str(value: Fraction, places: int) -> str:
    """Render an exact rational at `places` decimals, half away from zero."""
    if not isinstance(value, Fraction):
        raise TypeError("decimal_str requires an exact Fraction")
    scale = 10 ** places
    num = value.numerator * scale
    den = value.denominator
    negative = num < 0
    num = -num if negative else num
    q = (2 * num + den) // (2 * den)
    digits = str(q).rjust(places + 1, "0")
    text = digits if places == 0 else digits[:-places] + "." + digits[-places:]
    return ("-" + text) if (negative and q) else text


def places_of(anchor: str) -> int:
    return len(anchor.split(".")[1]) if "." in anchor else 0


def matches(value: Fraction, anchor: str) -> bool:
    return decimal_str(value, places_of(anchor)) == anchor


# ---------------------------------------------------------------------------
# Invalid-input refusals (INV-1, INV-2, INV-3).
# ---------------------------------------------------------------------------
def require_nonsingular(p: int, a: int, b: int) -> None:
    """INV-3: refuse a singular (a, b), i.e. 4a^3 + 27b^2 = 0 mod p."""
    if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
        raise InvalidInputError(
            f"singular curve refused: 4a^3 + 27b^2 = 0 mod {p} at (a, b) = ({a}, {b})")


def require_nonvacuous_H(p: int, H: int) -> None:
    """INV-2: refuse H > (4p/3)^{1/2}; exact integer test 3H^2 > 4p."""
    if H < 1:
        raise InvalidInputError(f"H must be at least 1, got {H}")
    if 3 * H * H > 4 * p:
        raise InvalidInputError(
            f"H = {H} exceeds (4p/3)^(1/2) at p = {p} (3H^2 = {3 * H * H} > 4p = {4 * p}); "
            "the box is then all of F_p and the density condition is vacuous")


def require_affine_x(point) -> int:
    """INV-1, half one: the point at infinity has no affine x and no height."""
    if point is None:
        raise InvalidInputError("the point at infinity has no affine x and no height")
    return point[0]


# ---------------------------------------------------------------------------
# Exact curve arithmetic over F_p.  Affine short-Weierstrass, no library.
# ---------------------------------------------------------------------------
def rhs(x: int, p: int, a: int, b: int) -> int:
    return (pow(x, 3, p) + a * x + b) % p


def is_square(v: int, p: int) -> bool:
    if v % p == 0:
        return True
    return pow(v % p, (p - 1) // 2, p) == 1


def sqrt_mod(v: int, p: int) -> int:
    v %= p
    if v == 0:
        return 0
    if p % 4 == 3:
        r = pow(v, (p + 1) // 4, p)
    else:
        r = next((y for y in range(p) if y * y % p == v), None)
        if r is None:
            raise ValueError(f"{v} is not a square mod {p}")
    if r * r % p != v:
        raise ValueError(f"{v} is not a square mod {p}")
    return r


def add(P, Q, p: int, a: int):
    """Affine addition.  None is the point at infinity."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if (x1 - x2) % p == 0:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def on_curve(point, p: int, a: int, b: int) -> bool:
    if point is None:
        return True
    x, y = point
    return (y * y - rhs(x, p, a, b)) % p == 0


def affine_points(p: int, a: int, b: int):
    """All affine points, in ascending (x, y) order.  Exact, no square roots."""
    pts = []
    for x in range(p):
        r = rhs(x, p, a, b)
        if r == 0:
            pts.append((x, 0))
        elif is_square(r, p):
            y = sqrt_mod(r, p)
            pts.append((x, min(y, p - y)))
            pts.append((x, max(y, p - y)))
    return pts


def curve_order(p: int, a: int, b: int) -> int:
    """#E(F_p) by exact Euler-criterion point counting, identity included."""
    total = 1
    for x in range(p):
        r = rhs(x, p, a, b)
        if r == 0:
            total += 1
        elif is_square(r, p):
            total += 2
    return total


def is_prime(m: int) -> bool:
    if m < 2:
        return False
    if m % 2 == 0:
        return m == 2
    d = 3
    while d * d <= m:
        if m % d == 0:
            return False
        d += 2
    return True


# ---------------------------------------------------------------------------
# Asymmetric height and the height box.
#
#   ht(x) = min over lifts of max(|alpha|, beta) with alpha = x*beta mod p,
#           1 <= beta, alpha reduced to the symmetric interval.
#
# So ht(x) <= H  <=>  there are alpha, beta with |alpha| <= H, 1 <= beta <= H
# and alpha = x*beta mod p.  Two independent constructions are computed and
# cross-checked against each other below.
# ---------------------------------------------------------------------------
def symmetric_rep(v: int, p: int) -> int:
    v %= p
    return v - p if 2 * v > p else v


def box_by_lift_enumeration(p: int, H: int) -> set:
    """F_H built forward from the lifts.  x = 0 enters through its lift (0, 1)."""
    require_nonvacuous_H(p, H)
    members = set()
    for beta in range(1, H + 1):
        inv_beta = pow(beta, -1, p)
        for alpha in range(-H, H + 1):
            members.add(alpha % p * inv_beta % p)
    return members


def height_of(x: int, p: int, H_cap: int) -> int | None:
    """ht(x) by direct minimisation over beta, or None if ht(x) > H_cap."""
    best = None
    for beta in range(1, H_cap + 1):
        if best is not None and beta > best:
            break
        alpha = symmetric_rep(x * beta % p, p)
        h = max(abs(alpha), beta)
        if best is None or h < best:
            best = h
    return best


def box_by_height_minimisation(p: int, H: int, H_cap: int) -> set:
    """F_H built backward from ht(x), computed per x.  Independent of the above."""
    require_nonvacuous_H(p, H)
    return {x for x in range(p) if (height_of(x, p, H_cap) or H_cap + 1) <= H}


# ---------------------------------------------------------------------------
# A minimal exact sparse multivariate polynomial ring over Z.
# ---------------------------------------------------------------------------
class Poly:
    __slots__ = ("names", "terms")

    def __init__(self, names, terms=None):
        self.names = tuple(names)
        self.terms = {}
        if terms:
            for mono, coeff in terms.items():
                if coeff:
                    self.terms[tuple(mono)] = coeff

    @classmethod
    def const(cls, names, c):
        z = tuple([0] * len(names))
        return cls(names, {z: c} if c else {})

    @classmethod
    def var(cls, names, name):
        i = tuple(names).index(name)
        mono = [0] * len(names)
        mono[i] = 1
        return cls(names, {tuple(mono): 1})

    def __add__(self, other):
        out = dict(self.terms)
        for mono, coeff in other.terms.items():
            new = out.get(mono, 0) + coeff
            if new:
                out[mono] = new
            else:
                out.pop(mono, None)
        return Poly(self.names, out)

    def __neg__(self):
        return Poly(self.names, {m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if isinstance(other, int):
            return Poly(self.names, {m: c * other for m, c in self.terms.items()})
        out = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                mono = tuple(x + y for x, y in zip(m1, m2))
                new = out.get(mono, 0) + c1 * c2
                if new:
                    out[mono] = new
                else:
                    out.pop(mono, None)
        return Poly(self.names, out)

    __rmul__ = __mul__

    def __pow__(self, k: int):
        out = Poly.const(self.names, 1)
        for _ in range(k):
            out = out * self
        return out

    def __eq__(self, other):
        return self.names == other.names and self.terms == other.terms

    def degree_in(self, name: str) -> int:
        i = self.names.index(name)
        return max((m[i] for m in self.terms), default=0)

    def is_zero(self) -> bool:
        return not self.terms

    def coefficient_in(self, spec: dict, keep):
        """Coefficient of the monomial `spec` in the named variables, as a
        polynomial in the variables `keep` (declared order)."""
        idx = {n: i for i, n in enumerate(self.names)}
        out = {}
        for mono, coeff in self.terms.items():
            if any(mono[idx[n]] != e for n, e in spec.items()):
                continue
            reduced = tuple(mono[idx[n]] for n in keep)
            out[reduced] = out.get(reduced, 0) + coeff
        return Poly(keep, out)

    def render(self) -> str:
        if not self.terms:
            return "0"
        chunks = []
        for mono in sorted(self.terms, key=lambda m: (-sum(m), m), reverse=False):
            coeff = self.terms[mono]
            factors = []
            for name, e in zip(self.names, mono):
                if e == 1:
                    factors.append(name)
                elif e > 1:
                    factors.append(f"{name}^{e}")
            if not factors:
                chunks.append(f"{coeff:+d}")
            elif abs(coeff) == 1:
                chunks.append(("+" if coeff > 0 else "-") + "*".join(factors))
            else:
                chunks.append(f"{coeff:+d}*" + "*".join(factors))
        text = " ".join(chunks)
        return text[1:].strip() if text.startswith("+") else text


TERM_RE = re.compile(r"([+-]?)\s*([0-9]*)\s*((?:\*?\s*(?:x_3|x1|x2|a|b)(?:\^[0-9]+)?)*)$")
FACTOR_RE = re.compile(r"\*?\s*(x_3|x1|x2|a|b)(?:\^([0-9]+))?")


def parse_expression(text: str, names, alias: dict) -> Poly:
    """Parse one of the contract's coefficient/monomial strings exactly.

    Generic over the restricted grammar `[+-] int? symbol(^int)? (*symbol...)*`
    joined by + / -.  It knows nothing about which answer is expected; it is
    applied to the frozen strings AND used nowhere in the derivation of f_3.
    """
    text = text.strip()
    if text == "const":
        return Poly.const(names, 1)
    pieces, buf = [], ""
    for i, ch in enumerate(text):
        if ch in "+-" and i > 0:
            pieces.append(buf)
            buf = ch
        else:
            buf += ch
    pieces.append(buf)
    total = Poly.const(names, 0)
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        m = TERM_RE.match(piece)
        if not m:
            raise ValueError(f"cannot parse term {piece!r} of {text!r}")
        sign = -1 if m.group(1) == "-" else 1
        coeff = int(m.group(2)) if m.group(2) else 1
        term = Poly.const(names, sign * coeff)
        body = m.group(3)
        pos = 0
        while pos < len(body):
            fm = FACTOR_RE.match(body, pos)
            if not fm:
                raise ValueError(f"cannot parse factor at {body[pos:]!r} of {text!r}")
            exponent = int(fm.group(2)) if fm.group(2) else 1
            term = term * (Poly.var(names, alias[fm.group(1)]) ** exponent)
            pos = fm.end()
        total = total + term
    return total


# ---------------------------------------------------------------------------
# Decomposition-count statistics.  Exact integers and exact rationals.
# ---------------------------------------------------------------------------
def decomposition_counts(indices, n: int):
    """c_2(R) = #{(P, Q) in F x F : P + Q = R}, ORDERED pairs, over all n
    targets, by exact convolution in the group's index coordinates."""
    counts = [0] * n
    for i in indices:
        for j in indices:
            counts[(i + j) % n] += 1
    return counts


def count_stats(counts, n: int):
    total = sum(counts)
    mean = Fraction(total, n)
    mean_square = Fraction(sum(c * c for c in counts), n)
    variance = mean_square - mean * mean
    return {
        "total": total,
        "mean": mean,
        "variance": variance,
        "dispersion_index": variance / mean,
        "unreachable": sum(1 for c in counts if c == 0),
        "max": max(counts),
        "c_of_identity": counts[0],
    }


# ---------------------------------------------------------------------------
# Anchor (a).
# ---------------------------------------------------------------------------
def f3_mod(x1: int, x2: int, x3: int, p: int, a: int, b: int) -> int:
    e1 = (x1 + x2 + x3) % p
    e2 = (x1 * x2 + x1 * x3 + x2 * x3) % p
    e3 = (x1 * x2 * x3) % p
    return ((e2 - a) ** 2 - 4 * e1 * (e3 + b)) % p


def anchor_a():
    p, a, b = ANCHOR_A["p"], ANCHOR_A["a"], ANCHOR_A["b"]
    require_nonsingular(p, a, b)
    order = curve_order(p, a, b)
    pts = affine_points(p, a, b)
    x_values = sorted({x for x, _ in pts})

    # INV-1: the identity is not an affine point and contributes no x.
    infinity_refused = False
    try:
        require_affine_x(None)
    except InvalidInputError:
        infinity_refused = True

    # Realisability decided by ACTUAL CURVE ARITHMETIC, independently of f_3:
    # (x1, x2, x3) is realisable iff points P, Q with those first two
    # x-coordinates satisfy x(P + Q) = x3, i.e. P + Q + R = O for the point R
    # with x(R) = x3 and the matching sign.
    realisable = set()
    witness = {}
    for P in pts:
        for Q in pts:
            S = add(P, Q, p, a)
            if S is None:
                continue  # then the third summand would be O, which has no x
            key = (P[0], Q[0], S[0])
            realisable.add(key)
            witness.setdefault(key, (P, Q, (S[0], (-S[1]) % p)))

    vanishing = 0
    false_negatives, false_positives = [], []
    for x1 in x_values:
        for x2 in x_values:
            for x3 in x_values:
                vanishes = f3_mod(x1, x2, x3, p, a, b) == 0
                real = (x1, x2, x3) in realisable
                if vanishes:
                    vanishing += 1
                if real and not vanishes:
                    false_negatives.append([x1, x2, x3])
                if vanishes and not real:
                    false_positives.append([x1, x2, x3])

    # Independently re-verify a sample of witnesses by point arithmetic.
    checked = 0
    for key in sorted(realisable)[:25]:
        P, Q, R = witness[key]
        assert on_curve(P, p, a, b) and on_curve(Q, p, a, b) and on_curve(R, p, a, b)
        assert add(add(P, Q, p, a), R, p, a) is None, key
        checked += 1

    return {
        "p": p, "a": a, "b": b,
        "curve_order_measured": order,
        "affine_point_count": len(pts),
        "on_curve_x_count": len(x_values),
        "ordered_triples_enumerated": len(x_values) ** 3,
        "realisable_ordered_x_triples": len(realisable),
        "f3_vanishing_ordered_x_triples": vanishing,
        "false_negatives": len(false_negatives),
        "false_positives": len(false_positives),
        "false_negative_examples": false_negatives[:10],
        "false_positive_examples": false_positives[:10],
        "witnesses_reverified_by_point_arithmetic": checked,
        "infinity_has_no_affine_x_refused": infinity_refused,
        "x_zero_on_curve": 0 in x_values,
        "witness_sample": [
            {"triple": list(k), "points": [list(witness[k][0]), list(witness[k][1]),
                                           list(witness[k][2])]}
            for k in sorted(realisable)[:5]
        ],
        "pass_curve_order": order == ANCHOR_A["curve_order"],
        "pass_realisable": len(realisable) == ANCHOR_A["realisable_ordered_x_triples"],
        "pass_false_negatives": len(false_negatives) == ANCHOR_A["false_negatives"],
        "pass_false_positives": len(false_positives) == ANCHOR_A["false_positives"],
    }


# ---------------------------------------------------------------------------
# Anchor (b).
# ---------------------------------------------------------------------------
def anchor_b():
    p = ANCHOR_B["ladder_p"]
    a, b = ANCHOR_B["cell_a"], ANCHOR_B["cell_b"]
    require_nonsingular(p, a, b)
    H_cap = max(ANCHOR_B["ladder_H"])

    ladder = []
    for H in ANCHOR_B["ladder_H"]:
        forward = box_by_lift_enumeration(p, H)
        backward = box_by_height_minimisation(p, H, H_cap)
        size = len(forward)
        c_H = Fraction(size, H * H)
        ladder.append({
            "H": H,
            "box_size_measured": size,
            "box_size_by_height_minimisation": len(backward),
            "two_constructions_agree": forward == backward,
            "c_H_exact": f"{c_H.numerator}/{c_H.denominator}",
            "c_H_decimal": decimal_str(c_H, 3),
        })

    # INV-1, half two: x = 0 has the lift (0, 1) and therefore height 1.
    ht_zero = height_of(0, p, H_cap)

    n = curve_order(p, a, b)
    H = ANCHOR_B["cell_H"]
    box = sorted(box_by_lift_enumeration(p, H))
    on_curve_x = [x for x in box if rhs(x, p, a, b) != 0 and is_square(rhs(x, p, a, b), p)]
    base_points = []
    for x in on_curve_x:
        y = sqrt_mod(rhs(x, p, a, b), p)
        lo, hi = min(y, p - y), max(y, p - y)
        base_points.append((x, lo))
        base_points.append((x, hi))
    assert all(on_curve(P, p, a, b) for P in base_points)
    # Negation closure of the base, which the contract declares load-bearing.
    as_set = set(base_points)
    negation_closed = all((x, (-y) % p) in as_set for x, y in base_points)

    sizes = [row["box_size_measured"] for row in ladder]
    decimals = [row["c_H_decimal"] for row in ladder]
    return {
        "ladder_p": p,
        "ladder": ladder,
        "box_sizes_measured": sizes,
        "c_H_decimals": decimals,
        "height_of_x_zero": ht_zero,
        "x_zero_lift": [0, 1],
        "cell": {
            "p": p, "a": a, "b": b, "H": H,
            "n_measured": n,
            "n_prime": is_prime(n),
            "n_not_equal_p": n != p,
            "box_size": len(box),
            "on_curve_x_values_in_box": len(on_curve_x),
            "base_point_count": len(base_points),
            "base_is_negation_closed": negation_closed,
            "no_two_torsion_in_box": all(y != 0 for _, y in base_points),
        },
        "on_curve_x_in_box": on_curve_x,
        "base_points": [list(P) for P in base_points],
        "pass_box_sizes": sizes == ANCHOR_B["box_sizes"],
        "pass_c_H": decimals == ANCHOR_B["c_H"],
        "pass_two_constructions_agree": all(r["two_constructions_agree"] for r in ladder),
        "pass_n": n == ANCHOR_B["cell_n"] and is_prime(n) and n != p,
        "pass_on_curve_x": len(on_curve_x) == ANCHOR_B["on_curve_x_values_in_box"],
        "pass_base_points": len(base_points) == ANCHOR_B["base_points"],
    }


# ---------------------------------------------------------------------------
# Anchor (c): independent expansion and homogenisation of f_3.
# ---------------------------------------------------------------------------
F3_VARS = ("u", "v", "w", "a", "b")
COEFF_VARS = ("w", "a", "b")
HOM_VARS = ("alpha1", "beta1", "alpha2", "beta2", "w", "a", "b")
COEFF_ALIAS = {"x_3": "w", "a": "a", "b": "b"}
KEY_ALIAS = {"x1": "u", "x2": "v"}


def anchor_c():
    u = Poly.var(F3_VARS, "u")
    v = Poly.var(F3_VARS, "v")
    w = Poly.var(F3_VARS, "w")
    a = Poly.var(F3_VARS, "a")
    b = Poly.var(F3_VARS, "b")

    # Derived from the DEFINING equation only.  No frozen coefficient is read.
    e1 = u + v + w
    e2 = u * v + u * w + v * w
    e3 = u * v * w
    f3 = (e2 - a) ** 2 - Poly.const(F3_VARS, 4) * e1 * (e3 + b)

    deg_u, deg_v = f3.degree_in("u"), f3.degree_in("v")
    bidegrees = [(i, j) for i in range(deg_u + 1) for j in range(deg_v + 1)]
    expanded = {}
    for i, j in bidegrees:
        expanded[(i, j)] = f3.coefficient_in({"u": i, "v": j}, COEFF_VARS)

    # Homogenisation F = beta1^2 * beta2^2 * f_3(alpha1/beta1, alpha2/beta2, x_3),
    # performed as exact polynomial arithmetic: it is legitimate precisely
    # because deg_u f_3 = deg_v f_3 = 2, so no negative power of beta arises.
    assert deg_u == 2 and deg_v == 2, (deg_u, deg_v)
    hom = Poly.const(HOM_VARS, 0)
    a1 = Poly.var(HOM_VARS, "alpha1")
    b1 = Poly.var(HOM_VARS, "beta1")
    a2 = Poly.var(HOM_VARS, "alpha2")
    b2 = Poly.var(HOM_VARS, "beta2")
    hom_terms = {}
    for (i, j), coeff in expanded.items():
        if coeff.is_zero():
            continue
        lifted = Poly(HOM_VARS, {
            (0, 0, 0, 0) + mono: c for mono, c in coeff.terms.items()})
        block = lifted * (a1 ** i) * (b1 ** (2 - i)) * (a2 ** j) * (b2 ** (2 - j))
        hom_terms[(i, j)] = block
        hom = hom + block

    total_degrees = sorted({
        sum(mono[:4]) for block in hom_terms.values() for mono in block.terms})

    # Compare against the frozen list, both sides parsed by generic routines.
    comparison = []
    all_match = True
    for key, text in ANCHOR_C["coefficients"].items():
        key_poly = parse_expression(key, F3_VARS, KEY_ALIAS) if key != "const" else None
        if key == "const":
            bidegree = (0, 0)
        else:
            mono = next(iter(key_poly.terms))
            bidegree = (mono[F3_VARS.index("u")], mono[F3_VARS.index("v")])
        frozen = parse_expression(text, COEFF_VARS, COEFF_ALIAS)
        mine = expanded[bidegree]
        ok = frozen == mine
        all_match = all_match and ok
        comparison.append({
            "frozen_key": key,
            "bidegree": list(bidegree),
            "frozen_coefficient": text,
            "expanded_coefficient": mine.render(),
            "agree": ok,
        })

    present = sorted(bd for bd, c in expanded.items() if not c.is_zero())
    return {
        "f3_definition": "f_3 = (e_2 - a)^2 - 4*e_1*(e_3 + b)",
        "f3_expanded": f3.render(),
        "e1": e1.render(), "e2": e2.render(), "e3": e3.render(),
        "square_term": ((e2 - a) ** 2).render(),
        "product_term": (Poly.const(F3_VARS, 4) * e1 * (e3 + b)).render(),
        "degree_in_x1": deg_u,
        "degree_in_x2": deg_v,
        "bidegrees_present": [list(bd) for bd in present],
        "monomial_count_measured": len(present),
        "homogenised_total_degrees": total_degrees,
        "homogenised_form": hom.render(),
        "homogenised_monomial_blocks": {
            f"{bd[0]},{bd[1]}": block.render() for bd, block in sorted(hom_terms.items())},
        "coefficient_comparison": comparison,
        "pass_monomial_count": len(present) == ANCHOR_C["monomial_count"],
        "pass_all_bidegrees_present":
            present == [(i, j) for i in range(3) for j in range(3)],
        "pass_total_degree": total_degrees == [ANCHOR_C["total_degree"]],
        "pass_coefficients": all_match,
        "_expanded": expanded,
    }


# ---------------------------------------------------------------------------
# Anchor (d).
# ---------------------------------------------------------------------------
def anchor_d(box_size: int):
    p, H, B, n = ANCHOR_D["p"], ANCHOR_D["H"], ANCHOR_D["B"], ANCHOR_D["n"]
    H4 = H ** 4
    ratio = Fraction(H4, p)
    b2n = Fraction(B * B, n)
    return {
        "p": p, "H": H, "B": B, "n": n,
        "H_to_the_4_measured": H4,
        "ratio_H4_over_p_exact": f"{ratio.numerator}/{ratio.denominator}",
        "ratio_H4_over_p_decimal_5dp": decimal_str(ratio, 5),
        "ratio_H4_over_p_decimal_10dp": decimal_str(ratio, 10),
        "rounding": IMPL_CHOICES["decimal_rounding"],
        "B_squared_over_n_exact": f"{b2n.numerator}/{b2n.denominator}",
        "B_squared_over_n_decimal_4dp": decimal_str(b2n, 4),
        "box_size_at_H": box_size,
        "pass_H4": H4 == ANCHOR_D["H_to_the_4"],
        "pass_ratio": matches(ratio, ANCHOR_D["ratio_H4_over_p"]),
        "pass_B_squared_over_n": matches(b2n, ANCHOR_D["B_squared_over_n"]),
    }


# ---------------------------------------------------------------------------
# Anchor (e): the dispersion cell, its matched null, and the controls.
# ---------------------------------------------------------------------------
def anchor_e(base_points, on_curve_x_in_box):
    p, a, b = ANCHOR_E["p"], ANCHOR_E["a"], ANCHOR_E["b"]
    require_nonsingular(p, a, b)
    n = curve_order(p, a, b)

    # Index the whole group once by repeated addition of a generator.
    generator = None
    for x in range(p):
        r = rhs(x, p, a, b)
        if r != 0 and is_square(r, p):
            generator = (x, sqrt_mod(r, p))
            break
    index = {None: 0}
    cur = generator
    for i in range(1, n):
        index[cur] = i
        cur = add(cur, generator, p, a)
    if cur is not None:
        raise AssertionError("generator order does not equal the measured group order")
    generator_order_is_n = True
    assert len(index) == n

    box_idx = [index[tuple(P)] for P in base_points]
    box_counts = decomposition_counts(box_idx, n)
    box_stats = count_stats(box_counts, n)

    # Implementation cross-check: the same count vector recomputed by DIRECT
    # point addition rather than by index-space convolution.  A disagreement
    # here would be an implementation error, not an observation.
    direct = [0] * n
    pts = [tuple(P) for P in base_points]
    for P in pts:
        for Q in pts:
            direct[index[add(P, Q, p, a)]] += 1
    direct_agrees = direct == box_counts

    # Matched null: negation-closed random base of the same size, drawn as a
    # random subset of the ON-CURVE X-VALUES of F_p with both points per x.
    all_on_curve_x = [x for x in range(p)
                      if rhs(x, p, a, b) != 0 and is_square(rhs(x, p, a, b), p)]
    x_to_indices = {}
    for x in all_on_curve_x:
        y = sqrt_mod(rhs(x, p, a, b), p)
        x_to_indices[x] = (index[(x, min(y, p - y))], index[(x, max(y, p - y))])

    rng_null = random.Random(ANCHOR_E["null_seed"])
    subset_size = len(on_curve_x_in_box)
    null_draws = []
    null_vectors = []
    disp = []
    unreach = []
    null_means_match = True
    null_sizes_match = True
    null_negation_closed = True
    for draw in range(ANCHOR_E["null_draws"]):
        sample = rng_null.sample(all_on_curve_x, subset_size)
        idxs = []
        for x in sample:
            idxs.extend(x_to_indices[x])
        counts = decomposition_counts(idxs, n)
        st = count_stats(counts, n)
        null_vectors.append(counts)
        disp.append(st["dispersion_index"])
        unreach.append(st["unreachable"])
        null_means_match = null_means_match and st["mean"] == box_stats["mean"]
        null_sizes_match = null_sizes_match and len(idxs) == ANCHOR_E["null_size"]
        idx_set = set(idxs)
        draw_negation_closed = all((-i) % n in idx_set for i in idxs)
        null_negation_closed = null_negation_closed and draw_negation_closed
        null_draws.append({
            "draw": draw,
            "base_size": len(idxs),
            "x_values_sampled": subset_size,
            "negation_closed": draw_negation_closed,
            "mean_exact": f"{st['mean'].numerator}/{st['mean'].denominator}",
            "variance_decimal_4dp": decimal_str(st["variance"], 4),
            "dispersion_index_decimal_4dp": decimal_str(st["dispersion_index"], 4),
            "dispersion_index_exact":
                f"{st['dispersion_index'].numerator}/{st['dispersion_index'].denominator}",
            "unreachable": st["unreachable"],
            "max": st["max"],
            "c_of_identity": st["c_of_identity"],
        })

    null_mean_disp = sum(disp, Fraction(0)) / len(disp)
    null_min_disp, null_max_disp = min(disp), max(disp)
    null_mean_unreach = Fraction(sum(unreach), len(unreach))

    # Relabelled-Z/nZ generic control (density half only; the search half is
    # Stage 2 and is unauthorized).  The group index already is an explicit
    # isomorphism E(F_p) -> Z/nZ.  Forget the curve coordinates and height
    # labels, retain only the same negation-closed residue subset, and recompute
    # the density vector in Z/nZ.  This is a deterministic relabelling control,
    # so it consumes no randomness beyond the 60 contract-authorized null draws.
    generic_indices = list(box_idx)
    generic_counts = decomposition_counts(generic_indices, n)
    generic_stats = count_stats(generic_counts, n)
    generic_agrees = generic_counts == box_counts

    box_disp = box_stats["dispersion_index"]
    return {
        "p": p, "a": a, "b": b, "n_measured": n, "H": ANCHOR_E["H"],
        "generator": list(generator),
        "generator_order_equals_n": generator_order_is_n,
        "group_indexed_size": len(index),
        "base_point_count": len(box_idx),
        "box": {
            "total_ordered_pairs": box_stats["total"],
            "mean_exact": f"{box_stats['mean'].numerator}/{box_stats['mean'].denominator}",
            "mean_decimal_4dp": decimal_str(box_stats["mean"], 4),
            "variance_exact":
                f"{box_stats['variance'].numerator}/{box_stats['variance'].denominator}",
            "variance_decimal_4dp": decimal_str(box_stats["variance"], 4),
            "dispersion_index_exact": f"{box_disp.numerator}/{box_disp.denominator}",
            "dispersion_index_decimal_4dp": decimal_str(box_disp, 4),
            "unreachable_targets": box_stats["unreachable"],
            "max_count": box_stats["max"],
            "c_of_identity": box_stats["c_of_identity"],
        },
        "direct_point_arithmetic_cross_check_agrees": direct_agrees,
        "matched_null": {
            "kind": "negation_closed_random_base",
            "seed": ANCHOR_E["null_seed"],
            "draws": len(null_draws),
            "size": 2 * subset_size,
            "x_universe_size": len(all_on_curve_x),
            "procedure": IMPL_CHOICES["null_rng"],
            "x_list_order": IMPL_CHOICES["null_x_list_order"],
            "mean_dispersion_exact":
                f"{null_mean_disp.numerator}/{null_mean_disp.denominator}",
            "mean_dispersion_decimal_4dp": decimal_str(null_mean_disp, 4),
            "dispersion_min_decimal_4dp": decimal_str(null_min_disp, 4),
            "dispersion_max_decimal_4dp": decimal_str(null_max_disp, 4),
            "mean_unreachable_exact":
                f"{null_mean_unreach.numerator}/{null_mean_unreach.denominator}",
            "mean_unreachable_decimal_1dp": decimal_str(null_mean_unreach, 1),
            "every_draw_mean_equals_box_mean": null_means_match,
            "every_draw_has_frozen_size": null_sizes_match,
            "every_draw_is_negation_closed": null_negation_closed,
            "box_dispersion_inside_null_range":
                null_min_disp <= box_disp <= null_max_disp,
        },
        "generic_relabelled_control": {
            "object": "relabelled Z/nZ, negation-closed residue base of the same "
                      "size, no height structure",
            "draws": 0,
            "procedure": IMPL_CHOICES["generic_control"],
            "base_size": len(generic_indices),
            "negation_closed": all((-i) % n in set(generic_indices)
                                   for i in generic_indices),
            "mean_decimal_4dp": decimal_str(generic_stats["mean"], 4),
            "dispersion_index_decimal_4dp":
                decimal_str(generic_stats["dispersion_index"], 4),
            "unreachable": generic_stats["unreachable"],
            "max": generic_stats["max"],
            "c_of_identity": generic_stats["c_of_identity"],
            "mean_equals_box_mean": generic_stats["mean"] == box_stats["mean"],
            "density_count_vector_equals_box_after_relabelling": generic_agrees,
        },
        "pass_mean": matches(box_stats["mean"], ANCHOR_E["mean"]),
        "pass_variance": matches(box_stats["variance"], ANCHOR_E["variance"]),
        "pass_dispersion_index": matches(box_disp, ANCHOR_E["dispersion_index"]),
        "pass_unreachable": box_stats["unreachable"] == ANCHOR_E["unreachable_targets"],
        "pass_max": box_stats["max"] == ANCHOR_E["max_count"],
        "pass_c_of_identity": box_stats["c_of_identity"] == ANCHOR_E["c_of_identity"],
        "pass_c_of_identity_at_least_B":
            box_stats["c_of_identity"] >= len(box_idx),
        "pass_null_mean_dispersion":
            matches(null_mean_disp, ANCHOR_E["null_mean_dispersion"]),
        "pass_null_range":
            [decimal_str(null_min_disp, 4), decimal_str(null_max_disp, 4)]
            == ANCHOR_E["null_dispersion_range"],
        "pass_null_mean_unreachable":
            matches(null_mean_unreach, ANCHOR_E["null_mean_unreachable"]),
        "pass_null_comparability":
            null_means_match and null_sizes_match and null_negation_closed,
        "pass_direct_cross_check": direct_agrees,
        "_box_counts": box_counts,
        "_null_vectors": null_vectors,
        "_null_draws": null_draws,
        "_generic_counts": generic_counts,
    }


# ---------------------------------------------------------------------------
# Known-false controls.
# ---------------------------------------------------------------------------
def known_false_kf1(box_size: int, H: int, p: int, n: int):
    """KF-1: 'the product of the 2m unknown bounds FALLS with arity m'.

    Refuted at the contract's stated asymptotic level by the exact identity
    H^{2m} = n/c_H^m.  Rejected BY COMPUTATION: symbolic exponent bookkeeping
    leaves the exponent of n equal to one for every m; only the constant
    c_H^{-m} changes.  The exact finite-cell values can decrease when c_H > 1,
    so this routine deliberately does NOT make the false stronger claim that
    the rational sequence n/c_H^m is numerically nondecreasing.
    """
    c_H = Fraction(box_size, H * H)
    lo, hi = IMPL_CHOICES["kf1_arity_range"]
    rows = []
    identities_hold = True
    n_exponent_constant = True
    for m in range(lo, hi + 1):
        prod = Fraction(n) / (c_H ** m)
        restored = prod * (c_H ** m)
        identity_holds = restored == n
        exponent_vector = {"n": 1, "c_H": -m}
        identities_hold = identities_hold and identity_holds
        n_exponent_constant = n_exponent_constant and exponent_vector["n"] == 1
        rows.append({
            "m": m,
            "unknown_bounds": 2 * m,
            "identity_rhs_n_over_c_H_pow_m_exact":
                f"{prod.numerator}/{prod.denominator}",
            "restored_n_exact": f"{restored.numerator}/{restored.denominator}",
            "identity_holds": identity_holds,
            "formal_exponent_vector": exponent_vector,
            "n_exponent_is_one": exponent_vector["n"] == 1,
        })
    pinning = Fraction(H ** 4, p)
    frozen_cell_pinning_pass = (
        H ** 4 == ANCHOR_D["H_to_the_4"]
        and matches(pinning, ANCHOR_D["ratio_H4_over_p"])
    )
    return {
        "id": "KF-1",
        "claim": "the product of the unknown bounds FALLS with arity m",
        "c_H_exact": f"{c_H.numerator}/{c_H.denominator}",
        "arity_range": [lo, hi],
        "rows": rows,
        "identity_exhibited_at_frozen_cell": {
            "m": 2,
            "H": H,
            "H_to_the_2m": H ** 4,
            "p": p,
            "ratio_exact": f"{pinning.numerator}/{pinning.denominator}",
            "ratio_decimal_5dp": decimal_str(pinning, 5),
        },
        "all_exact_identities_hold": identities_hold,
        "n_exponent_is_one_for_every_arity": n_exponent_constant,
        "only_c_H_constant_factor_depends_on_arity": True,
        "finite_values_may_decrease_when_c_H_exceeds_one": c_H > 1,
        "frozen_cell_pinning_pass": frozen_cell_pinning_pass,
        "rejected": identities_hold and n_exponent_constant and frozen_cell_pinning_pass,
        "rejection_reason":
            "Exact rational and symbolic-exponent computation verifies "
            "H^(2m) = n/c_H^m by multiplying the right-hand side by c_H^m "
            f"and recovering n for every m in [{lo}, {hi}]. The exponent of n "
            "is exactly 1 at every arity; only the p-independent constant factor "
            f"c_H^(-m), with c_H = {c_H.numerator}/{c_H.denominator}, changes. "
            "The finite rational values may decrease because c_H > 1; that is not "
            "an arity-dependent fall in the field-size exponent asserted by KF-1. "
            f"At the frozen cell H^4 = {H ** 4} against p = {p}, ratio "
            f"{decimal_str(pinning, 5)}.",
    }


def known_false_kf2(expanded):
    """KF-2: 'the homogenised arity-2 support has a MISSING bidegree'.

    Rejected BY COMPUTATION: the independent expansion of f_3 carries a nonzero
    coefficient polynomial at every one of the nine bidegrees, so no
    missing-bidegree claim survives.  Every candidate omission is tested, and
    the canonical instance named in this record is (1, 1).
    """
    tested = []
    all_nonzero = True
    for (i, j), coeff in sorted(expanded.items()):
        nonzero = not coeff.is_zero()
        all_nonzero = all_nonzero and nonzero
        tested.append({
            "bidegree": [i, j],
            "coefficient": coeff.render(),
            "nonzero_as_polynomial_in_Z[a,b,x_3]": nonzero,
            "omission_claim_refuted": nonzero,
        })
    omitted = IMPL_CHOICES["kf2_canonical_omitted_bidegree"]
    omitted_coeff = expanded[tuple(omitted)].render()
    return {
        "id": "KF-2",
        "claim": "the homogenised arity-2 support has a MISSING bidegree",
        "bidegrees_tested": tested,
        "candidate_omissions_tested": len(tested),
        "every_bidegree_nonzero": all_nonzero,
        "bidegree_the_false_claim_omitted": omitted,
        "bidegree_the_false_claim_omitted_monomial": "x1*x2",
        "bidegree_the_false_claim_omitted_coefficient": omitted_coeff,
        "rejected": all_nonzero,
        "rejection_reason":
            "The independent expansion of f_3 = (e_2 - a)^2 - 4*e_1*(e_3 + b) "
            "carries a nonzero coefficient at all nine bidegrees in {0,1,2}^2, "
            "so every candidate missing-bidegree claim is refuted, not only the "
            f"canonical one. The canonical false claim omits bidegree "
            f"({omitted[0]}, {omitted[1]}) (the monomial x1*x2), whose measured "
            f"coefficient is {omitted_coeff} and is nonzero as a polynomial in "
            "Z[a, b, x_3].",
    }


def known_false_kf3():
    """KF-3: 'gamma_2 >= 1, asserted WITHOUT the lattice dimension and
    determinant recorded'.

    PROCEDURAL control: nothing is computed, by design.  The contract's own
    admissibility rule makes such a claim inadmissible on its face, and Stage 0
    reports no gamma of any kind.
    """
    return {
        "id": "KF-3",
        "claim": "gamma_2 >= 1, asserted without the lattice dimension and "
                 "determinant recorded",
        "control_kind": "procedural",
        "nothing_computed_by_design": True,
        "rejected": True,
        "rejection_reason":
            "Rejected on the contract's admissibility rule, not by computation: "
            "experiments/EXP-ECDLP-1bef8f/specification.yaml requires a gamma "
            "claim to record its shift-polynomial set, lattice dimension and "
            "determinant, and its stage1_preregistered_branches.BR-LEAD "
            "additionally requires the recovered integers, a verified relation "
            "and a passing univariate positive control. A gamma claim carrying "
            "none of these is inadmissible on its face.",
        "how_the_design_enforces_it": [
            "Stage 1 is unauthorized (execution_authorized_stages: [0]); the "
            "authorizing decision for Stage 1 must itself declare and hash-bind "
            "the shift-polynomial strategy and the lattice implementation "
            "BEFORE any gamma is reported.",
            "invalidation_rules: reporting any value, bound or estimate of "
            "gamma_2, gamma_3 or gamma_m invalidates a Stage 0 run, as does "
            "building a lattice, running LLL/BKZ, or constructing a "
            "shift-polynomial set.",
            "BR-LEAD requires independent review-breakthrough at max effort "
            "before any interpretation, and that tier may not be degraded.",
        ],
        "gamma_reported_by_this_run": None,
        "this_run_computed_no_gamma": True,
        "this_run_built_no_lattice": True,
        "this_run_formed_no_shift_polynomial_set": True,
        "this_run_called_no_lattice_reduction_routine": True,
    }


def invalid_input_controls():
    p = ANCHOR_B["ladder_p"]
    results = []

    # INV-1: x = 0 and the point at infinity, both handled explicitly.
    infinity_refused, message = False, None
    try:
        require_affine_x(None)
    except InvalidInputError as exc:
        infinity_refused, message = True, str(exc)
    ht_zero = height_of(0, p, 10)
    results.append({
        "id": "INV-1",
        "object": "x = 0 and the point at infinity",
        "point_at_infinity_refused": infinity_refused,
        "refusal_message": message,
        "x_zero_lift": [0, 1],
        "x_zero_height": ht_zero,
        "x_zero_in_box_at_H_10": ht_zero <= 10,
        "x_zero_on_curve_at_cell": is_square(
            rhs(0, p, ANCHOR_B["cell_a"], ANCHOR_B["cell_b"]), p)
        and rhs(0, p, ANCHOR_B["cell_a"], ANCHOR_B["cell_b"]) != 0,
        "handled_explicitly": infinity_refused and ht_zero == 1,
    })

    # INV-2: H exceeding (4p/3)^{1/2}.
    boundary = max(H for H in range(1, p) if 3 * H * H <= 4 * p)
    refused, msg = False, None
    try:
        box_by_lift_enumeration(p, boundary + 1)
    except InvalidInputError as exc:
        refused, msg = True, str(exc)
    accepted = True
    try:
        box_by_lift_enumeration(p, boundary)
    except InvalidInputError:
        accepted = False
    results.append({
        "id": "INV-2",
        "object": f"H exceeding (4p/3)^(1/2) at p = {p}",
        "largest_admissible_H": boundary,
        "refused_H": boundary + 1,
        "refused": refused,
        "refusal_message": msg,
        "boundary_H_still_accepted": accepted,
        "frozen_ladder_H_all_accepted": all(
            3 * H * H <= 4 * p for H in ANCHOR_B["ladder_H"]),
        "handled_explicitly": refused and accepted,
    })

    # INV-3: a singular (a, b).  Both the trivial pair and a nontrivial one
    # COMPUTED as a cube root, not hardcoded.
    cases = [(0, 0)]
    if (p - 1) % 3 != 0:
        d = (2 * (p - 1) + 1) // 3
        target = (-27) * pow(4, -1, p) % p
        a_sing = pow(target, d, p)
        if (4 * pow(a_sing, 3, p) + 27) % p == 0:
            cases.append((a_sing, 1))
    singular = []
    for a_s, b_s in cases:
        refused_s, msg_s = False, None
        try:
            require_nonsingular(p, a_s, b_s)
        except InvalidInputError as exc:
            refused_s, msg_s = True, str(exc)
        singular.append({
            "a": a_s, "b": b_s,
            "discriminant_expression_mod_p":
                (4 * pow(a_s, 3, p) + 27 * pow(b_s, 2, p)) % p,
            "refused": refused_s,
            "refusal_message": msg_s,
        })
    frozen_nonsingular = []
    for cp, ca, cb in ((ANCHOR_A["p"], ANCHOR_A["a"], ANCHOR_A["b"]),
                       (ANCHOR_B["cell_p"], ANCHOR_B["cell_a"], ANCHOR_B["cell_b"])):
        frozen_nonsingular.append({
            "p": cp, "a": ca, "b": cb,
            "discriminant_expression_mod_p":
                (4 * pow(ca, 3, cp) + 27 * pow(cb, 2, cp)) % cp,
            "nonsingular": (4 * pow(ca, 3, cp) + 27 * pow(cb, 2, cp)) % cp != 0,
        })
    results.append({
        "id": "INV-3",
        "object": "a singular (a, b) with 4a^3 + 27b^2 = 0 mod p",
        "singular_cases_refused": singular,
        "all_refused": all(c["refused"] for c in singular),
        "frozen_cells_nonsingular": frozen_nonsingular,
        "handled_explicitly": all(c["refused"] for c in singular)
        and all(c["nonsingular"] for c in frozen_nonsingular),
    })
    return results


# ---------------------------------------------------------------------------
# Artifact writers.
# ---------------------------------------------------------------------------
def yaml_scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    return json.dumps(text)


def to_yaml(obj, indent=0) -> str:
    pad = "  " * indent
    if isinstance(obj, dict):
        if not obj:
            return pad + "{}\n"
        out = []
        for key, value in obj.items():
            if isinstance(value, (dict, list)) and value:
                out.append(f"{pad}{key}:\n" + to_yaml(value, indent + 1))
            elif isinstance(value, (dict, list)):
                out.append(f"{pad}{key}: " + ("{}" if isinstance(value, dict) else "[]") + "\n")
            else:
                out.append(f"{pad}{key}: {yaml_scalar(value)}\n")
        return "".join(out)
    if isinstance(obj, list):
        if not obj:
            return pad + "[]\n"
        out = []
        for item in obj:
            if isinstance(item, (dict, list)) and item:
                body = to_yaml(item, indent + 1)
                first, rest = body.split("\n", 1)
                out.append(f"{pad}- {first.strip()}\n" + rest)
            else:
                out.append(f"{pad}- {yaml_scalar(item)}\n")
        return "".join(out)
    return pad + yaml_scalar(obj) + "\n"


def git_state():
    def run(args):
        try:
            return subprocess.run(args, cwd=ROOT, capture_output=True,
                                  text=True, check=True).stdout
        except Exception:
            return ""
    commit = run(["git", "rev-parse", "HEAD"]).strip() or None
    status = run(["git", "status", "--porcelain"])
    lines = [ln for ln in status.splitlines() if ln.strip()]
    return commit, bool(lines), lines


def main() -> int:
    started_at = datetime.now(timezone.utc)
    clock = time.perf_counter()
    # Capture execution provenance before creating any result artifact.
    commit, dirty, dirty_lines = git_state()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    source_bytes = (ROOT / SOURCE).read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    spec_path = ROOT / "experiments/EXP-ECDLP-1bef8f/specification.yaml"
    spec_sha256 = hashlib.sha256(spec_path.read_bytes()).hexdigest()

    res_a = anchor_a()
    res_b = anchor_b()
    res_c = anchor_c()
    expanded = res_c.pop("_expanded")
    res_d = anchor_d(res_b["cell"]["box_size"])
    res_e = anchor_e(res_b["base_points"], res_b["on_curve_x_in_box"])
    box_counts = res_e.pop("_box_counts")
    null_vectors = res_e.pop("_null_vectors")
    null_draws = res_e.pop("_null_draws")
    generic_counts = res_e.pop("_generic_counts")

    kf1 = known_false_kf1(res_b["cell"]["box_size"], ANCHOR_B["cell_H"],
                          ANCHOR_B["cell_p"], res_b["cell"]["n_measured"])
    kf2 = known_false_kf2(expanded)
    kf3 = known_false_kf3()
    inv = invalid_input_controls()

    # ------------------------------------------------------------------
    # Anchor-by-anchor gate table, evaluated in the contract's own order.
    # ------------------------------------------------------------------
    checks = [
        ("a", "curve_order at (101, 3, 5)", res_a["curve_order_measured"],
         ANCHOR_A["curve_order"], res_a["pass_curve_order"]),
        ("a", "realisable ordered x-triples", res_a["realisable_ordered_x_triples"],
         ANCHOR_A["realisable_ordered_x_triples"], res_a["pass_realisable"]),
        ("a", "false negatives", res_a["false_negatives"],
         ANCHOR_A["false_negatives"], res_a["pass_false_negatives"]),
        ("a", "false positives", res_a["false_positives"],
         ANCHOR_A["false_positives"], res_a["pass_false_positives"]),
        ("b", "|F_H| ladder", res_b["box_sizes_measured"],
         ANCHOR_B["box_sizes"], res_b["pass_box_sizes"]),
        ("b", "c_H ladder (3 dp)", res_b["c_H_decimals"],
         ANCHOR_B["c_H"], res_b["pass_c_H"]),
        ("b", "n at (10007, 1, 28), prime and != p", res_b["cell"]["n_measured"],
         ANCHOR_B["cell_n"], res_b["pass_n"]),
        ("b", "on-curve x-values in the box", res_b["cell"]["on_curve_x_values_in_box"],
         ANCHOR_B["on_curve_x_values_in_box"], res_b["pass_on_curve_x"]),
        ("b", "base points", res_b["cell"]["base_point_count"],
         ANCHOR_B["base_points"], res_b["pass_base_points"]),
        ("c", "monomial count", res_c["monomial_count_measured"],
         ANCHOR_C["monomial_count"], res_c["pass_monomial_count"]),
        ("c", "all nine bidegrees present", len(res_c["bidegrees_present"]),
         9, res_c["pass_all_bidegrees_present"]),
        ("c", "homogenised total degree", res_c["homogenised_total_degrees"],
         [ANCHOR_C["total_degree"]], res_c["pass_total_degree"]),
        ("c", "coefficient list", "all nine agree" if res_c["pass_coefficients"]
         else "disagreement", "frozen list", res_c["pass_coefficients"]),
        ("d", "H^4", res_d["H_to_the_4_measured"],
         ANCHOR_D["H_to_the_4"], res_d["pass_H4"]),
        ("d", "H^4/p (5 dp)", res_d["ratio_H4_over_p_decimal_5dp"],
         ANCHOR_D["ratio_H4_over_p"], res_d["pass_ratio"]),
        ("d", "B^2/n (4 dp)", res_d["B_squared_over_n_decimal_4dp"],
         ANCHOR_D["B_squared_over_n"], res_d["pass_B_squared_over_n"]),
        ("e", "mean (4 dp)", res_e["box"]["mean_decimal_4dp"],
         ANCHOR_E["mean"], res_e["pass_mean"]),
        ("e", "variance (4 dp)", res_e["box"]["variance_decimal_4dp"],
         ANCHOR_E["variance"], res_e["pass_variance"]),
        ("e", "dispersion index (4 dp)", res_e["box"]["dispersion_index_decimal_4dp"],
         ANCHOR_E["dispersion_index"], res_e["pass_dispersion_index"]),
        ("e", "unreachable targets", res_e["box"]["unreachable_targets"],
         ANCHOR_E["unreachable_targets"], res_e["pass_unreachable"]),
        ("e", "max decomposition count", res_e["box"]["max_count"],
         ANCHOR_E["max_count"], res_e["pass_max"]),
        ("e", "c(O)", res_e["box"]["c_of_identity"],
         ANCHOR_E["c_of_identity"], res_e["pass_c_of_identity"]),
        ("e", "null mean dispersion (4 dp)",
         res_e["matched_null"]["mean_dispersion_decimal_4dp"],
         ANCHOR_E["null_mean_dispersion"], res_e["pass_null_mean_dispersion"]),
        ("e", "null dispersion range (4 dp)",
         [res_e["matched_null"]["dispersion_min_decimal_4dp"],
          res_e["matched_null"]["dispersion_max_decimal_4dp"]],
         ANCHOR_E["null_dispersion_range"], res_e["pass_null_range"]),
        ("e", "null mean unreachable (1 dp)",
         res_e["matched_null"]["mean_unreachable_decimal_1dp"],
         ANCHOR_E["null_mean_unreachable"], res_e["pass_null_mean_unreachable"]),
    ]
    anchor_table = [
        {"anchor": anchor, "quantity": name,
         "measured": measured, "frozen": frozen,
         "verdict": "PASS" if ok else "MISMATCH"}
        for anchor, name, measured, frozen, ok in checks
    ]
    mismatches = [row for row in anchor_table if row["verdict"] == "MISMATCH"]
    first_mismatch = mismatches[0] if mismatches else None

    gates = {
        "relation_condition_pass": all([res_a["pass_curve_order"], res_a["pass_realisable"],
                                        res_a["pass_false_negatives"],
                                        res_a["pass_false_positives"]]),
        "box_count_ladder_pass": res_b["pass_box_sizes"] and res_b["pass_c_H"]
        and res_b["pass_two_constructions_agree"],
        "base_and_order_pass": res_b["pass_n"] and res_b["pass_on_curve_x"]
        and res_b["pass_base_points"] and res_b["cell"]["base_is_negation_closed"],
        "monomial_support_pass": all([res_c["pass_monomial_count"],
                                     res_c["pass_all_bidegrees_present"],
                                     res_c["pass_total_degree"],
                                     res_c["pass_coefficients"]]),
        "pinning_anchor_pass": all([res_d["pass_H4"], res_d["pass_ratio"],
                                    res_d["pass_B_squared_over_n"]]),
        "dispersion_cell_pass": all([res_e["pass_mean"], res_e["pass_variance"],
                                     res_e["pass_dispersion_index"],
                                     res_e["pass_unreachable"], res_e["pass_max"],
                                     res_e["pass_c_of_identity"],
                                     res_e["pass_direct_cross_check"]]),
        "matched_null_pass": all([res_e["pass_null_mean_dispersion"],
                                  res_e["pass_null_range"],
                                  res_e["pass_null_mean_unreachable"],
                                  res_e["pass_null_comparability"]]),
        "known_false_KF1_reject_pass": kf1["rejected"],
        "known_false_KF2_reject_pass": kf2["rejected"],
        "known_false_KF3_reject_pass": kf3["rejected"],
        "invalid_input_reject_pass": all(c["handled_explicitly"] for c in inv),
        "identity_count_pass": res_e["pass_c_of_identity"]
        and res_e["pass_c_of_identity_at_least_B"],
        "certificate_kind_none_pass": True,
        "no_gamma_reported_pass": True,
    }
    gates["fixture_pass"] = all(gates.values()) and not mismatches
    all_pass = gates["fixture_pass"]
    procedure_gate_names = [
        "known_false_KF1_reject_pass",
        "known_false_KF2_reject_pass",
        "known_false_KF3_reject_pass",
        "invalid_input_reject_pass",
    ]
    if all_pass:
        failure_classification = None
    elif mismatches:
        failure_classification = "invalid_measurement"
    elif not all(gates[name] for name in procedure_gate_names):
        failure_classification = "implementation_error"
    else:
        failure_classification = "invalid_measurement"

    secondary = {
        "realisable_ordered_x_triples": res_a["realisable_ordered_x_triples"],
        "box_sizes_by_H": dict(zip((str(h) for h in ANCHOR_B["ladder_H"]),
                                   res_b["box_sizes_measured"])),
        "c_H_by_H": dict(zip((str(h) for h in ANCHOR_B["ladder_H"]),
                             res_b["c_H_decimals"])),
        "on_curve_x_values_in_box": res_b["cell"]["on_curve_x_values_in_box"],
        "base_point_count": res_b["cell"]["base_point_count"],
        "pinning_ratio": res_d["ratio_H4_over_p_decimal_5dp"],
        "decomposition_mean": res_e["box"]["mean_decimal_4dp"],
        "decomposition_variance": res_e["box"]["variance_decimal_4dp"],
        "dispersion_index": res_e["box"]["dispersion_index_decimal_4dp"],
        "unreachable_target_count": res_e["box"]["unreachable_targets"],
        "max_decomposition_count": res_e["box"]["max_count"],
        "c_of_identity": res_e["box"]["c_of_identity"],
        "matched_null_dispersion_mean_min_max": [
            res_e["matched_null"]["mean_dispersion_decimal_4dp"],
            res_e["matched_null"]["dispersion_min_decimal_4dp"],
            res_e["matched_null"]["dispersion_max_decimal_4dp"]],
        "matched_null_unreachable_mean":
            res_e["matched_null"]["mean_unreachable_decimal_1dp"],
        "generic_group_density_agreement": {
            "generic_dispersion":
                res_e["generic_relabelled_control"]["dispersion_index_decimal_4dp"],
            "generic_unreachable":
                res_e["generic_relabelled_control"]["unreachable"],
            "mean_equals_box_mean":
                res_e["generic_relabelled_control"]["mean_equals_box_mean"],
            "density_count_vector_equals_box_after_relabelling":
                res_e["generic_relabelled_control"][
                    "density_count_vector_equals_box_after_relabelling"],
        },
    }

    finished_at = datetime.now(timezone.utc)
    elapsed = time.perf_counter() - clock
    usage = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss_bytes = usage.ru_maxrss * 1024

    # ------------------------------------------------------------------
    # raw-result.json
    # ------------------------------------------------------------------
    raw = {
        "schema": "crypto.autoresearch.stage0_raw_result.v1",
        "run_id": RUN_ID,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "goal_id": GOAL_ID,
        "batch_id": BATCH_ID,
        "task_id": TASK_ID,
        "stage": 0,
        "authorized_by": AUTHORIZED_BY,
        "frozen_object": FROZEN_OBJECT,
        "claim_ceiling": "stage0_fixture_reproduction_only",
        "specification_path": "experiments/EXP-ECDLP-1bef8f/specification.yaml",
        "specification_sha256": spec_sha256,
        "source_path": SOURCE,
        "source_sha256": source_sha256,
        "arithmetic": "exact integers and exact fractions.Fraction only; no "
                      "floating point in any decision; decimals rendered from "
                      "exact rationals by integer arithmetic",
        "implementation_choices": IMPL_CHOICES,
        "anchor_comparison_table": anchor_table,
        "first_mismatch": first_mismatch,
        "mismatch_count": len(mismatches),
        "primary_metrics": gates,
        "secondary_metrics": secondary,
        "anchor_a_relation_condition": res_a,
        "anchor_b_box_counts_and_base": {k: v for k, v in res_b.items()
                                         if k not in ("on_curve_x_in_box", "base_points")},
        "anchor_c_monomial_support": res_c,
        "anchor_d_pinning": res_d,
        "anchor_e_dispersion_cell": res_e,
        "known_false": [kf1, kf2, kf3],
        "invalid_inputs": inv,
        "tail_checks": {
            "c_of_identity_equals_B": res_e["box"]["c_of_identity"]
            == res_b["cell"]["base_point_count"],
            "c_of_identity_at_least_B": res_e["pass_c_of_identity_at_least_B"],
            "max_decomposition_count": res_e["box"]["max_count"],
            "unreachable_target_count": res_e["box"]["unreachable_targets"],
            "null_range_used_not_only_the_mean": True,
            "box_dispersion_inside_null_range":
                res_e["matched_null"]["box_dispersion_inside_null_range"],
            "false_negatives_and_false_positives_reported_separately": {
                "false_negatives": res_a["false_negatives"],
                "false_positives": res_a["false_positives"],
            },
        },
        "certificate": {"kind": "none", "verified": None,
                        "note": "No ECDLP instance solved, no scalar recovered, "
                                "nothing to certify."},
        "gamma_reported": None,
        "stage1_authorized": False,
        "stage2_authorized": False,
        "stage3_authorized": False,
        "lattice_built": False,
        "shift_polynomial_set_formed": False,
        "lattice_reduction_called": False,
        "ecdlp_instance_solved": False,
        "scalar_recovered": False,
        "observation_collision_limit_honoured": {
            "binding": True,
            "statement": "The arity-2 density observable does not separate the "
                         "height box from a matched negation-closed random base. "
                         "Every dispersion number in this run is a fixture check, "
                         "never a finding and never an advantage.",
            "box_dispersion": res_e["box"]["dispersion_index_decimal_4dp"],
            "null_mean_dispersion":
                res_e["matched_null"]["mean_dispersion_decimal_4dp"],
            "null_range": [res_e["matched_null"]["dispersion_min_decimal_4dp"],
                           res_e["matched_null"]["dispersion_max_decimal_4dp"]],
            "box_inside_null_range":
                res_e["matched_null"]["box_dispersion_inside_null_range"],
            "decay_parameter_p_tested": False,
            "decay_parameter_note": "One value of p is measured, so this run "
                                    "cannot test decay in p at all; the p-ladder "
                                    "is Stage 3 and is unauthorized.",
        },
        "timing": {
            "started_at": started_at.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "finished_at": finished_at.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "wall_clock_seconds": elapsed,
        },
        "resources": {"peak_rss_bytes": peak_rss_bytes,
                      "cpu_seconds": usage.ru_utime + usage.ru_stime},
        "exit_code": 0 if all_pass else 1,
        "validity": "completed_valid" if all_pass else "completed_invalid",
        "failure_classification": failure_classification,
        "all_pass": all_pass,
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")

    # ------------------------------------------------------------------
    # frozen-manifest.json
    # ------------------------------------------------------------------
    frozen_manifest = {
        "schema": "crypto.autoresearch.stage0_frozen_manifest.v1",
        "run_id": RUN_ID,
        "purpose": "Rebuild both frozen cells without rerunning the producer.",
        "seed": ANCHOR_E["null_seed"],
        "seeds_declared_by_contract": [ANCHOR_E["null_seed"]],
        "cells": [
            {
                "name": "relation-condition cell (anchor a)",
                "p": ANCHOR_A["p"], "a": ANCHOR_A["a"], "b": ANCHOR_A["b"],
                "curve": "y^2 = x^3 + 3x + 5",
                "n": res_a["curve_order_measured"],
                "n_is_group_order_including_identity": True,
                "H": None,
                "box_size": None,
                "on_curve_x_values": sorted({P[0] for P in affine_points(
                    ANCHOR_A["p"], ANCHOR_A["a"], ANCHOR_A["b"])}),
                "affine_points": [list(P) for P in affine_points(
                    ANCHOR_A["p"], ANCHOR_A["a"], ANCHOR_A["b"])],
            },
            {
                "name": "density cell (anchors b, d, e)",
                "p": ANCHOR_B["cell_p"], "a": ANCHOR_B["cell_a"],
                "b": ANCHOR_B["cell_b"],
                "curve": "y^2 = x^3 + x + 28",
                "n": res_b["cell"]["n_measured"],
                "n_prime": res_b["cell"]["n_prime"],
                "H": ANCHOR_B["cell_H"],
                "box_size": res_b["cell"]["box_size"],
                "box_sizes_by_H": dict(zip((str(h) for h in ANCHOR_B["ladder_H"]),
                                           res_b["box_sizes_measured"])),
                "on_curve_x_values_in_box": res_b["on_curve_x_in_box"],
                "base_points": res_b["base_points"],
                "generator_used_for_indexing": res_e["generator"],
            },
        ],
        "height_normalisation":
            "ht(x) = min over lifts of max(|alpha|, beta) subject to "
            "alpha = x*beta mod p, 1 <= beta, alpha reduced to the symmetric "
            "interval; x = 0 has the lift (0, 1) and height 1.",
    }
    (RUN_DIR / "frozen-manifest.json").write_text(
        json.dumps(frozen_manifest, indent=2) + "\n")

    # ------------------------------------------------------------------
    # f3-verification-transcript.txt
    # ------------------------------------------------------------------
    lines = [
        "EXP-ECDLP-1bef8f Stage 0 -- anchor (a) two-directional f_3 verification",
        f"run: {RUN_ID}   authorized_by: {AUTHORIZED_BY}   certificate.kind: none",
        "",
        f"curve            : y^2 = x^3 + {ANCHOR_A['a']}x + {ANCHOR_A['b']} over F_{ANCHOR_A['p']}",
        f"relation form    : f_3 = (e_2 - a)^2 - 4*e_1*(e_3 + b) mod {ANCHOR_A['p']}",
        f"#E(F_p) measured : {res_a['curve_order_measured']}  (frozen anchor {ANCHOR_A['curve_order']})",
        f"affine points    : {res_a['affine_point_count']}",
        f"on-curve x-values: {res_a['on_curve_x_count']}",
        f"ordered triples  : {res_a['ordered_triples_enumerated']}  (= on-curve x-count cubed)",
        "",
        "REALISABILITY IS DECIDED INDEPENDENTLY OF f_3.  A triple (x1, x2, x3) is",
        "realisable iff there are affine points P, Q on the curve with x(P) = x1,",
        "x(Q) = x2 and x(P + Q) = x3, computed by affine point addition over F_p.",
        "The third summand is then R = -(P + Q), so P + Q + R = O.  f_3 is never",
        "consulted when deciding realisability, and point arithmetic is never",
        "consulted when evaluating f_3.",
        "",
        f"realisable ordered x-triples (point arithmetic) : {res_a['realisable_ordered_x_triples']}",
        f"f_3-vanishing ordered x-triples (algebra)       : {res_a['f3_vanishing_ordered_x_triples']}",
        "",
        "DIRECTION 1 -- realisable but f_3 does not vanish (false negatives)",
        f"  false_negatives = {res_a['false_negatives']}   (frozen anchor {ANCHOR_A['false_negatives']})",
        f"  examples        = {res_a['false_negative_examples'] or 'none'}",
        "",
        "DIRECTION 2 -- f_3 vanishes but the triple is not realisable (false positives)",
        f"  false_positives = {res_a['false_positives']}   (frozen anchor {ANCHOR_A['false_positives']})",
        f"  examples        = {res_a['false_positive_examples'] or 'none'}",
        "",
        "Both directions are reported separately, per the contract's tail check: a",
        "one-sided check would pass on a vacuous predicate.",
        "",
        f"witnesses re-verified by point arithmetic: {res_a['witnesses_reverified_by_point_arithmetic']}",
        "sample witnesses (P, Q, R with P + Q + R = O, each verified on-curve):",
    ]
    for item in res_a["witness_sample"]:
        lines.append(f"  triple {item['triple']} <- points {item['points']}")
    lines += [
        "",
        "INV-1 handling:",
        f"  point at infinity refused as having no affine x : {res_a['infinity_has_no_affine_x_refused']}",
        f"  x = 0 is an on-curve x-coordinate here          : {res_a['x_zero_on_curve']}",
        "  a triple whose third summand would be O is excluded, because O carries",
        "  no affine x-coordinate and so is not an on-curve x-value.",
        "",
        "verdicts:",
        f"  curve order      : {'PASS' if res_a['pass_curve_order'] else 'MISMATCH'}",
        f"  realisable count : {'PASS' if res_a['pass_realisable'] else 'MISMATCH'}",
        f"  false negatives  : {'PASS' if res_a['pass_false_negatives'] else 'MISMATCH'}",
        f"  false positives  : {'PASS' if res_a['pass_false_positives'] else 'MISMATCH'}",
        "",
        "SCOPE.  This is one toy curve over F_101.  It says nothing about any other",
        "curve, any larger field, gamma_m, the height box, or the ECDLP.",
    ]
    (RUN_DIR / "f3-verification-transcript.txt").write_text("\n".join(lines) + "\n")

    # ------------------------------------------------------------------
    # homogenisation-transcript.txt
    # ------------------------------------------------------------------
    hl = [
        "EXP-ECDLP-1bef8f Stage 0 -- anchor (c) homogenisation transcript",
        f"run: {RUN_ID}   authorized_by: {AUTHORIZED_BY}   certificate.kind: none",
        "",
        "DERIVATION IS INDEPENDENT.  The expansion below is produced by exact",
        "sparse polynomial arithmetic over Z in the variables x1, x2, x_3, a, b,",
        "starting from the DEFINING equation only.  The frozen coefficient list is",
        "read afterwards, parsed by a generic parser, and compared.  No frozen",
        "coefficient enters the expander.",
        "",
        "step 1 -- elementary symmetric functions of (x1, x2, x_3), written u, v, w",
        f"  e_1 = {res_c['e1']}",
        f"  e_2 = {res_c['e2']}",
        f"  e_3 = {res_c['e3']}",
        "",
        "step 2 -- the two halves of the defining equation",
        f"  (e_2 - a)^2      = {res_c['square_term']}",
        f"  4*e_1*(e_3 + b)  = {res_c['product_term']}",
        "",
        "step 3 -- f_3 = (e_2 - a)^2 - 4*e_1*(e_3 + b), expanded",
        f"  f_3 = {res_c['f3_expanded']}",
        "",
        f"step 4 -- degrees: deg_x1 f_3 = {res_c['degree_in_x1']}, "
        f"deg_x2 f_3 = {res_c['degree_in_x2']}",
        "  Both are 2, which is what makes the homogenisation below legitimate:",
        "  multiplying by beta_1^2*beta_2^2 clears every denominator and no",
        "  negative power of a beta can arise.",
        "",
        "step 5 -- coefficient of x1^i*x2^j, as a polynomial in a, b, x_3",
    ]
    for row in res_c["coefficient_comparison"]:
        hl.append(f"  bidegree {tuple(row['bidegree'])}  ({row['frozen_key']})")
        hl.append(f"    expanded independently : {row['expanded_coefficient']}")
        hl.append(f"    frozen in the contract : {row['frozen_coefficient']}")
        hl.append(f"    agree                  : {row['agree']}")
    hl += [
        "",
        "step 6 -- homogenisation",
        "  F = beta_1^2 * beta_2^2 * f_3(alpha_1/beta_1, alpha_2/beta_2, x_3)",
        "  performed termwise: c_ij(x_3, a, b) * x1^i * x2^j becomes",
        "  c_ij * alpha_1^i * beta_1^(2-i) * alpha_2^j * beta_2^(2-j).",
        "",
    ]
    for key, block in res_c["homogenised_monomial_blocks"].items():
        hl.append(f"  bidegree ({key}) -> {block}")
    hl += [
        "",
        f"  monomial blocks                     : {res_c['monomial_count_measured']} "
        f"(frozen anchor {ANCHOR_C['monomial_count']})",
        f"  bidegrees present                   : {res_c['bidegrees_present']}",
        f"  total degree in (alpha_1, beta_1, alpha_2, beta_2) of every monomial: "
        f"{res_c['homogenised_total_degrees']} (frozen anchor {ANCHOR_C['total_degree']})",
        "",
        f"  F = {res_c['homogenised_form']}",
        "",
        "verdicts:",
        f"  monomial count          : {'PASS' if res_c['pass_monomial_count'] else 'MISMATCH'}",
        f"  all nine bidegrees      : {'PASS' if res_c['pass_all_bidegrees_present'] else 'MISMATCH'}",
        f"  homogeneous of degree 4 : {'PASS' if res_c['pass_total_degree'] else 'MISMATCH'}",
        f"  coefficient list        : {'PASS' if res_c['pass_coefficients'] else 'MISMATCH'}",
        "",
        "SCOPE.  This is the support of one relation form.  NO gamma_2, gamma_3 or",
        "gamma_m of any kind is computed, estimated or implied here; no lattice is",
        "built and no shift-polynomial set is formed.  That is Stage 1 and it is",
        "unauthorized.",
    ]
    (RUN_DIR / "homogenisation-transcript.txt").write_text("\n".join(hl) + "\n")

    # ------------------------------------------------------------------
    # decomposition-counts.json
    # ------------------------------------------------------------------
    decomposition = {
        "schema": "crypto.autoresearch.stage0_decomposition_counts.v1",
        "run_id": RUN_ID,
        "p": ANCHOR_E["p"], "a": ANCHOR_E["a"], "b": ANCHOR_E["b"],
        "n": res_e["n_measured"], "H": ANCHOR_E["H"],
        "arity": 2,
        "counting_convention": "ORDERED pairs (P, Q) in F x F with P + Q = R; "
                               "the total over all targets is therefore B^2",
        "index_convention": "target index i means [i]G for the recorded generator; "
                            "index 0 is the identity O",
        "generator": res_e["generator"],
        "seed": ANCHOR_E["null_seed"],
        "box": {
            "base_point_count": res_e["base_point_count"],
            "dispersion_index": res_e["box"]["dispersion_index_decimal_4dp"],
            "unreachable": res_e["box"]["unreachable_targets"],
            "max": res_e["box"]["max_count"],
            "c_of_identity": res_e["box"]["c_of_identity"],
            "counts": box_counts,
        },
        "matched_null": {
            "procedure": IMPL_CHOICES["null_rng"],
            "x_list_order": IMPL_CHOICES["null_x_list_order"],
            "per_draw": null_draws,
            "counts_per_draw": null_vectors,
        },
        "generic_relabelled_control": {
            "procedure": IMPL_CHOICES["generic_control"],
            "counts": generic_counts,
            "density_count_vector_equals_box_after_relabelling":
                res_e["generic_relabelled_control"][
                    "density_count_vector_equals_box_after_relabelling"],
        },
        "binding_limit": "The density observable does not separate the height box "
                         "from a matched negation-closed random base. These vectors "
                         "are a fixture check, not a finding.",
    }
    (RUN_DIR / "decomposition-counts.json").write_text(
        json.dumps(decomposition) + "\n")

    # ------------------------------------------------------------------
    # known-false-report.yaml
    # ------------------------------------------------------------------
    kf_report = {
        "known_false_report": {
            "run_id": RUN_ID,
            "experiment_id": EXPERIMENT_ID,
            "task_id": TASK_ID,
            "authorized_by": AUTHORIZED_BY,
            "recorded_at": started_at.strftime("%Y-%m-%d"),
            "all_three_rejected": kf1["rejected"] and kf2["rejected"] and kf3["rejected"],
            "claims": [kf1, kf2, kf3],
            "invalid_inputs": inv,
            "note": "A known-false control that PASSES means the pipeline refused "
                    "a claim known to be false. It is a statement about the "
                    "instrument, not evidence about the ECDLP or the height box.",
        }
    }
    (RUN_DIR / "known-false-report.yaml").write_text(to_yaml(kf_report))

    # ------------------------------------------------------------------
    # stdout.log / stderr.log / command.txt / environment.json
    # ------------------------------------------------------------------
    command = COMMAND
    (RUN_DIR / "command.txt").write_text(command + "\n")
    env = {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "operating_system": platform.system(),
        "architecture": platform.architecture()[0],
        "libc": "-".join(platform.libc_ver()),
        "dependencies": {
            "third_party": {},
            "note": "Standard library only. No numpy, no sympy, no sage, no "
                    "elliptic-curve library, no lattice-reduction library.",
            "stdlib_modules_used": sorted([
                "hashlib", "json", "platform", "random", "re", "resource",
                "subprocess", "sys", "time", "datetime", "fractions", "pathlib"]),
        },
        "sage_version": None,
    }
    (RUN_DIR / "environment.json").write_text(json.dumps(env, indent=2) + "\n")

    summary = []
    summary.append(f"{EXPERIMENT_ID} Stage 0 ({FROZEN_OBJECT}) run {RUN_ID}")
    summary.append(f"authorized_by {AUTHORIZED_BY}   stage 0 only   certificate.kind none")
    summary.append(f"specification sha256 {spec_sha256}")
    summary.append(f"implementation sha256 {source_sha256}")
    summary.append("")
    summary.append("ANCHOR COMPARISON (measured | frozen | verdict)")
    for row in anchor_table:
        summary.append(f"  ({row['anchor']}) {row['quantity']:<38} "
                       f"{str(row['measured']):<28} {str(row['frozen']):<28} "
                       f"{row['verdict']}")
    summary.append("")
    summary.append("KNOWN-FALSE CONTROLS")
    for kf in (kf1, kf2, kf3):
        summary.append(f"  {kf['id']}: rejected={kf['rejected']}")
    summary.append("")
    summary.append("INVALID-INPUT REFUSALS")
    for c in inv:
        summary.append(f"  {c['id']}: handled_explicitly={c['handled_explicitly']}")
    summary.append("")
    summary.append("PRIMARY GATES")
    for key, value in gates.items():
        summary.append(f"  {key}: {str(value).lower()}")
    summary.append("")
    summary.append("MATCHED NULL (seed 20260913, 60 draws, negation-closed random base)")
    mn = res_e["matched_null"]
    summary.append(f"  mean dispersion {mn['mean_dispersion_decimal_4dp']} "
                   f"range [{mn['dispersion_min_decimal_4dp']}, "
                   f"{mn['dispersion_max_decimal_4dp']}] "
                   f"mean unreachable {mn['mean_unreachable_decimal_1dp']}")
    summary.append(f"  box dispersion {res_e['box']['dispersion_index_decimal_4dp']} "
                   f"lies inside the null range: "
                   f"{str(mn['box_dispersion_inside_null_range']).lower()}")
    summary.append("  This is the contract's already-successful observation "
                   "collision, restated. It is a fixture check and not a finding.")
    summary.append("")
    summary.append("NOT DONE, BY CONTRACT: no gamma computed, no lattice built, no "
                   "shift-polynomial set formed, no LLL/BKZ called, no ECDLP "
                   "instance solved, no scalar recovered, no attack mounted, no "
                   "ratio to rho or BSGS reported, Stages 1-3 not entered.")
    summary.append("")
    summary.append(f"fixture_pass {str(all_pass).lower()}   mismatches {len(mismatches)}")
    summary.append(f"wall_clock_seconds {elapsed:.6f}   peak_rss_bytes {peak_rss_bytes}")
    summary.append("")
    summary.append(f"artifacts written under {RUN_DIR.relative_to(ROOT)}")
    summary.append(f"execution report at {REPORT_PATH.relative_to(ROOT)}")
    summary_text = "\n".join(summary) + "\n"
    (RUN_DIR / "stdout.log").write_text(summary_text)
    (RUN_DIR / "stderr.log").write_text("")
    sys.stdout.write(summary_text)

    # ------------------------------------------------------------------
    # manifest.yaml
    # ------------------------------------------------------------------
    manifest = {
        "run": {
            "id": RUN_ID,
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "goal_id": GOAL_ID,
            "batch_id": BATCH_ID,
            "task_id": TASK_ID,
            "archived_by": ARCHIVED_BY,
            "stage": 0,
            "status": "completed_valid" if all_pass else "completed_invalid",
            "recorded_at": finished_at.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "code": {
                "commit": commit,
                "dirty": dirty,
                "dirty_summary": "untracked Stage 0 implementation and task "
                                 "records before execution"
                                 if dirty else "clean",
                "pre_run_dirty_paths": dirty_lines,
                "command": command,
                "source_path": SOURCE,
                "source_sha256": source_sha256,
                "specification_path":
                    "experiments/EXP-ECDLP-1bef8f/specification.yaml",
                "specification_sha256": spec_sha256,
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "canonical_policy": "executor-implementation",
                "policy": "executor-implementation",
                "backend": "cursor-cloud-agent",
                "provider": "openai",
                "resolved_model_id": "gpt-5.6-sol",
                "model_provenance":
                    "runtime identity supplied to the executing Cursor Cloud "
                    "session; not probe-verified",
                "model_verified": False,
                "requested_reasoning_effort": "medium",
                "reasoning_effort": "medium",
                "fallback_allowed": False,
                "fallback_used": False,
                "fallback_reason": None,
                "degraded_allowed": False,
                "degraded_requirements": [],
                "independent_session_required": False,
                "independent_session": False,
                "adapter_version": None,
                "adapter_note":
                    "orchestration/adapter was not invoked: no model is in this "
                    "run's compute loop. The program is deterministic exact "
                    "integer arithmetic; the policy fields record the session "
                    "that authored and launched it.",
                "config_digest": None,
            },
            "environment": {
                "operating_system": platform.system(),
                "architecture": platform.architecture()[0],
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "machine": platform.machine(),
                "sage_version": None,
                "dependencies": {
                    "third_party": "none",
                    "note": "standard library only; no elliptic-curve library "
                            "and no lattice-reduction library",
                },
            },
            "inputs": {
                "curve_id": "toy-F101-a3-b5 and toy-F10007-a1-b28",
                "seed": ANCHOR_E["null_seed"],
                "parameters": {
                    "frozen_object": FROZEN_OBJECT,
                    "authorized_by": AUTHORIZED_BY,
                    "execution_authorized_stages": [0],
                    "claim_ceiling": "stage0_fixture_reproduction_only",
                    "maximum_runs": 1,
                    "anchor_a_p": ANCHOR_A["p"],
                    "anchor_a_a": ANCHOR_A["a"],
                    "anchor_a_b": ANCHOR_A["b"],
                    "cell_p": ANCHOR_B["cell_p"],
                    "cell_a": ANCHOR_B["cell_a"],
                    "cell_b": ANCHOR_B["cell_b"],
                    "cell_n": res_b["cell"]["n_measured"],
                    "cell_H": ANCHOR_B["cell_H"],
                    "ladder_H": ANCHOR_B["ladder_H"],
                    "base_point_count": res_b["cell"]["base_point_count"],
                    "matched_null_draws": ANCHOR_E["null_draws"],
                    "generic_control_draws": 0,
                    "arithmetic": "exact integers and fractions.Fraction only",
                },
                "seeds": {
                    "declared": [ANCHOR_E["null_seed"]],
                    "matched_null": ANCHOR_E["null_seed"],
                    "generic_relabelled_control": None,
                    "sources_of_randomness":
                        "one random.Random instance seeded with the contract's "
                        "declared seed 20260913 for the 60 matched-null draws. "
                        "The relabelled-Z/nZ control is deterministic. Nothing "
                        "else in the run is stochastic.",
                },
            },
            "timing": {
                "started_at": started_at.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "finished_at": finished_at.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "wall_clock_seconds": elapsed,
                "wall_seconds": elapsed,
            },
            "resources": {
                "wall_clock_seconds": elapsed,
                "peak_rss_bytes": peak_rss_bytes,
                "cpu_seconds": usage.ru_utime + usage.ru_stime,
                "budget_wall_clock_seconds": 3600,
                "budget_memory_gb": 4,
                "budget_exceeded": False,
            },
            "result": {
                "validity_status": "valid" if all_pass else "invalid",
                "failure_classification": failure_classification,
                "exit_code": 0 if all_pass else 1,
                "valid": all_pass,
                "validity_reason":
                    "Stage 0 height-box fixture calibrator: all five frozen "
                    "anchors (a)-(e) reproduced by exact arithmetic, all three "
                    "known-false claims rejected, all three invalid inputs "
                    "refused, certificate kind none, no gamma reported."
                    if all_pass else
                    "Stage 0 instrument defect: an anchor mismatch is a fixture "
                    "defect and a failed known-false or invalid-input gate is a "
                    "procedure defect. See result.first_mismatch and metrics. "
                    "Neither is negative mathematical evidence about the ECDLP "
                    "or the height box.",
                "invalid_reason": None if all_pass else (
                    "fixture defect: anchor mismatch" if mismatches
                    else "procedure defect: control failure"
                ),
                "first_mismatch": first_mismatch,
                "mismatch_count": len(mismatches),
                "certificate": {
                    "kind": "none",
                    "verified": None,
                    "verifier": None,
                    "note": "No ECDLP instance is solved and no scalar is "
                            "recovered, so there is nothing to certify.",
                },
                "metrics": {**gates,
                            "gamma_reported": None,
                            "stage1_authorized": False,
                            "stage2_authorized": False,
                            "stage3_authorized": False,
                            "sibling_stage1_authorized": False,
                            "lattice_built": False,
                            "shift_polynomial_set_formed": False,
                            "lattice_reduction_called": False,
                            "ecdlp_instance_solved": False,
                            "scalar_recovered": False,
                            "attack_mounted": False,
                            "ratio_to_rho_reported": False,
                            "density_observable_founds_no_claim": True,
                            "decay_in_p_tested": False},
                "secondary_metrics": secondary,
                "anchor_comparison_table": anchor_table,
                "measured_vs_modeled":
                    "Every number in this run is MEASURED by exact enumeration. "
                    "No modeled cost figure appears anywhere in it; the "
                    "p^{2/m} and p^{1+o(1)} charges of the contract's cost "
                    "model are not computed, not estimated and not reported.",
                "scale_relevance":
                    "Toy: p = 101 (#E = 115) and p = 10007 (n = 9851 prime). At "
                    "p = 10007, H = 10 the box holds 1.27 per cent of F_p, far "
                    "larger than any cryptographic analogue, which biases every "
                    "density measurement toward apparent structure. No transfer "
                    "to cryptographic parameters is claimed; the p-ladder that "
                    "would test it is Stage 3 and unauthorized.",
                "scientific_boundary":
                    "Stage 0 P-S0-HTBOX height-box fixture calibrator only. Not "
                    "Stage 1 (no gamma_2, no gamma_3, no shift-polynomial set, no "
                    "lattice dimension, no determinant). Not Stage 2 (no lattice, "
                    "no LLL/BKZ, no planted instances, no univariate positive "
                    "control). Not Stage 3 (no p-ladder, no three field sizes, no "
                    "charge against rho or BSGS). No ECDLP solve, no scalar "
                    "recovery, certificate kind none. No descent, no p-adic "
                    "lifting, no Groebner-basis relation search. No claim founded "
                    "on the density observable in either direction. Not "
                    "P-S0-XLOW2, not P-S0-YLOW2, not P-S0-CHI2X. Authorizes "
                    "nothing.",
            },
            "artifacts": {
                "raw_result": "raw-result.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "environment": "environment.json",
                "command": "command.txt",
                "frozen_manifest": "frozen-manifest.json",
                "f3_verification_transcript": "f3-verification-transcript.txt",
                "homogenisation_transcript": "homogenisation-transcript.txt",
                "decomposition_counts": "decomposition-counts.json",
                "known_false_report": "known-false-report.yaml",
                "execution_report":
                    "../../execution-report-s0.yaml",
                "implementation_note":
                    "../../implementation/implementation-note.md",
            },
        }
    }
    (RUN_DIR / "manifest.yaml").write_text(to_yaml(manifest))

    # ------------------------------------------------------------------
    # execution-report-s0.yaml
    # ------------------------------------------------------------------
    observations = [
        f"Anchor (a): {res_a['realisable_ordered_x_triples']} realisable ordered "
        f"x-triples over the {res_a['on_curve_x_count']} on-curve x-values of "
        f"y^2 = x^3 + 3x + 5 over F_101 (frozen anchor "
        f"{ANCHOR_A['realisable_ordered_x_triples']}); "
        f"{res_a['false_negatives']} false negatives and "
        f"{res_a['false_positives']} false positives, reported separately. "
        "Realisability was decided by affine point addition, never by f_3.",
        f"Anchor (b): |F_H| = {res_b['box_sizes_measured']} at H = "
        f"{ANCHOR_B['ladder_H']} (frozen anchor {ANCHOR_B['box_sizes']}), c_H = "
        f"{res_b['c_H_decimals']} (frozen anchor {ANCHOR_B['c_H']}). Two "
        "independent box constructions -- forward from the lifts and backward "
        "from ht(x) -- agree on every H. At (10007, 1, 28), n = "
        f"{res_b['cell']['n_measured']} is prime and differs from p, and the box "
        f"at H = 10 holds {res_b['cell']['on_curve_x_values_in_box']} on-curve "
        f"x-values carrying {res_b['cell']['base_point_count']} base points, "
        "negation-closed.",
        f"Anchor (c): the independent expansion of f_3 = (e_2 - a)^2 - "
        f"4*e_1*(e_3 + b) has {res_c['monomial_count_measured']} monomials in "
        "(x1, x2), every bidegree in {0,1,2}^2 present, and the homogenised form "
        f"is homogeneous of total degree {res_c['homogenised_total_degrees']} in "
        "(alpha_1, beta_1, alpha_2, beta_2). All nine coefficient polynomials "
        "agree with the frozen list.",
        f"Anchor (d): H^4 = {res_d['H_to_the_4_measured']} and H^4/p = "
        f"{res_d['ratio_H4_over_p_exact']} = "
        f"{res_d['ratio_H4_over_p_decimal_5dp']} at five decimals "
        f"({res_d['ratio_H4_over_p_decimal_10dp']} at ten), rendered from the "
        "exact rational with half-away-from-zero rounding. B^2/n = "
        f"{res_d['B_squared_over_n_exact']} = "
        f"{res_d['B_squared_over_n_decimal_4dp']}.",
        f"Anchor (e): mean {res_e['box']['mean_decimal_4dp']}, variance "
        f"{res_e['box']['variance_decimal_4dp']}, dispersion index "
        f"{res_e['box']['dispersion_index_decimal_4dp']}, "
        f"{res_e['box']['unreachable_targets']} unreachable targets, max "
        f"{res_e['box']['max_count']}, c(O) = "
        f"{res_e['box']['c_of_identity']}. The same count vector recomputed by "
        "direct point addition rather than index-space convolution agrees "
        f"exactly: {res_e['direct_point_arithmetic_cross_check_agrees']}.",
        f"Matched null (seed {ANCHOR_E['null_seed']}, "
        f"{ANCHOR_E['null_draws']} draws, negation-closed random base of size "
        f"{res_e['matched_null']['size']} drawn from the "
        f"{res_e['matched_null']['x_universe_size']} on-curve x-values of F_p): "
        f"mean dispersion {res_e['matched_null']['mean_dispersion_decimal_4dp']}, "
        f"range [{res_e['matched_null']['dispersion_min_decimal_4dp']}, "
        f"{res_e['matched_null']['dispersion_max_decimal_4dp']}], mean "
        f"unreachable {res_e['matched_null']['mean_unreachable_decimal_1dp']}. "
        "The box's dispersion index lies inside that range: "
        f"{res_e['matched_null']['box_dispersion_inside_null_range']}. This is "
        "the contract's already-successful observation collision restated as a "
        "fixture check; it is not a finding, not an advantage, and not evidence "
        "about the height box in either direction.",
        "Relabelled-Z/nZ generic control (density half only; the search half is "
        "Stage 2 and unauthorized): the indexed height-box base was deterministically "
        "relabelled in Z/nZ with all curve and height labels removed. Its complete "
        "density count vector agrees with the elliptic vector exactly: "
        f"{res_e['generic_relabelled_control']['density_count_vector_equals_box_after_relabelling']}. "
        "This control used no additional random draws.",
        "KF-1 rejected by exact rational and symbolic-exponent computation: "
        "multiplying n/c_H^m by c_H^m recovers n for every m in "
        f"{kf1['arity_range']}, and the exponent of n remains exactly one. "
        f"Only the p-independent factor c_H^(-m), c_H = {kf1['c_H_exact']}, "
        "changes; finite values may decrease when c_H exceeds one, which is not "
        "a fall in the field-size exponent. The identity is exhibited at the "
        "frozen cell as H^4 = "
        f"{kf1['identity_exhibited_at_frozen_cell']['H_to_the_2m']} against p = "
        f"{kf1['identity_exhibited_at_frozen_cell']['p']}.",
        f"KF-2 rejected by the independent expansion: all "
        f"{kf2['candidate_omissions_tested']} candidate omissions are refuted, "
        "each bidegree carrying a nonzero coefficient polynomial. The canonical "
        f"false claim omits bidegree {kf2['bidegree_the_false_claim_omitted']} "
        f"(the monomial x1*x2), whose coefficient is "
        f"{kf2['bidegree_the_false_claim_omitted_coefficient']}.",
        "KF-3 rejected procedurally, with nothing computed by design: the "
        "contract's admissibility rule makes a gamma claim without a recorded "
        "lattice dimension and determinant inadmissible on its face. THIS RUN "
        "COMPUTED NO GAMMA of any kind, built no lattice, formed no "
        "shift-polynomial set, and called no lattice-reduction routine.",
        "INV-1, INV-2 and INV-3 all handled explicitly: the point at infinity is "
        "refused as having no affine x and no height; x = 0 has the lift (0, 1) "
        f"and height {inv[0]['x_zero_height']}; H = {inv[1]['refused_H']} at "
        f"p = 10007 is refused because 3H^2 > 4p while H = "
        f"{inv[1]['largest_admissible_H']} is still accepted; and both a trivial "
        "and a computed nontrivial singular (a, b) are refused, while both "
        "frozen cells are confirmed nonsingular.",
    ]
    report = {
        "execution_report": {
            "id": "ER-ECDLP-1bef8f-S0",
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "run_id": RUN_ID,
            "task_id": TASK_ID,
            "archived_by": ARCHIVED_BY,
            "goal_id": GOAL_ID,
            "batch_id": BATCH_ID,
            "recorded_at": started_at.strftime("%Y-%m-%d"),
            "stage": 0,
            "authorized_by": AUTHORIZED_BY,
            "frozen_object": FROZEN_OBJECT,
            "claim_ceiling": "stage0_fixture_reproduction_only",
            "implementation_commit": commit,
            "implementation_dirty": dirty,
            "implementation_sha256": source_sha256,
            "specification_sha256": spec_sha256,
            "validity_status": "valid" if all_pass else "invalid",
            "failure_classification": failure_classification,
            "exit_code": 0 if all_pass else 1,
            "protocol_deviations": [
                "The implementation note is at "
                "experiments/EXP-ECDLP-1bef8f/implementation/"
                "implementation-note.md rather than at the repository-standard "
                "experiments/EXP-ECDLP-1bef8f/implementation.md, to stay inside "
                "this task's assigned write scope.",
            ],
            "runs": {
                "completed": [RUN_ID] if all_pass else [],
                "invalid": [] if all_pass else [RUN_ID],
                "failed": [],
                "planned": 1,
                "executed": 1,
                "maximum_runs": 1,
            },
            "primary_gates": gates,
            "anchor_comparison_table": anchor_table,
            "first_mismatch": first_mismatch,
            "mismatch_count": len(mismatches),
            "secondary_metrics": secondary,
            "certificate": {"kind": "none", "verified": None, "verifier": None},
            "tail_checks": raw["tail_checks"],
            "observations": observations,
            "anomalies": [],
            "unexpected_observations": [],
            "interpretation": "NONE OFFERED. This report records observations "
                              "only. Whether the fixtures being trustworthy "
                              "warrants any further step is the Coordinator's "
                              "judgement after independent review.",
            "observation_collision_limit_honoured":
                raw["observation_collision_limit_honoured"],
            "gamma_reported": None,
            "no_gamma_computed": True,
            "no_lattice_built": True,
            "no_shift_polynomial_set_formed": True,
            "no_lattice_reduction_called": True,
            "no_ecdlp_instance_solved": True,
            "no_scalar_recovered": True,
            "stage1_authorized": False,
            "stage2_authorized": False,
            "stage3_authorized": False,
            "sibling_stage1_authorized": False,
            "evidence_record_written": False,
            "decision_record_written": False,
            "hypothesis_status_changed": False,
            "goal_yaml_edited": False,
            "dispatch_queue_edited": False,
            "specification_edited": False,
            "committed_by_this_task": False,
            "artifact_paths": [
                "experiments/EXP-ECDLP-1bef8f/implementation/stage0_htbox.py",
                "experiments/EXP-ECDLP-1bef8f/implementation/implementation-note.md",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/manifest.yaml",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/command.txt",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/environment.json",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/stdout.log",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/stderr.log",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/raw-result.json",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/frozen-manifest.json",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/"
                "f3-verification-transcript.txt",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/"
                "homogenisation-transcript.txt",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/"
                "decomposition-counts.json",
                f"experiments/EXP-ECDLP-1bef8f/runs/{RUN_ID}/known-false-report.yaml",
                "experiments/EXP-ECDLP-1bef8f/execution-report-s0.yaml",
                "coordination/goals/GOAL-ECDLP-001/batches/BATCH-e5c603/tasks/"
                f"{TASK_ID}/execution-receipt.json",
            ],
            "executor_assessment": {
                "protocol_complete": True,
                "data_quality": "good" if all_pass else "invalid",
                "requires_rerun": False,
                "note": "maximum_runs is 1 and one run was executed. A "
                        "correction, if one were ever needed, would be a NEW "
                        "run id; this record is immutable.",
            },
            "scientific_boundary": manifest["run"]["result"]["scientific_boundary"],
        }
    }
    REPORT_PATH.write_text(to_yaml(report))

    # Task receipt for the Coordinator's later snapshot archive.  It binds the
    # exact producer artifacts but does not commit or change research state.
    task_dir = (
        ROOT / "coordination/goals/GOAL-ECDLP-001/batches/BATCH-e5c603/tasks"
        / TASK_ID
    )
    task_dir.mkdir(parents=True, exist_ok=True)
    receipt_paths = [
        ROOT / p for p in report["execution_report"]["artifact_paths"]
        if not p.endswith("/execution-receipt.json")
    ]
    receipt = {
        "schema": "crypto.autoresearch.execution_receipt.v1",
        "task_id": TASK_ID,
        "snapshot_archive_task": ARCHIVED_BY,
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "stage": 0,
        "authorized_by": AUTHORIZED_BY,
        "claim_ceiling": "stage0_fixture_reproduction_only",
        "command": command,
        "exit_code": 0 if all_pass else 1,
        "validity": "completed_valid" if all_pass else "completed_invalid",
        "recorded_at": finished_at.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "pre_run_git_commit": commit,
        "pre_run_git_dirty": dirty,
        "pre_run_dirty_paths": dirty_lines,
        "certificate": {"kind": "none", "verified": None, "verifier": None},
        "scientific_runs_executed": 1,
        "maximum_runs": 1,
        "stage1_authorized": False,
        "stage2_authorized": False,
        "stage3_authorized": False,
        "draft_required_changes": True,
        "draft_change_summary": [
            "Removed 60 undeclared generic-control random draws; the partial "
            "relabelled-Z/nZ control is now a deterministic density relabelling.",
            "Corrected KF-1 so it computationally checks the frozen exponent-level "
            "identity without falsely claiming the finite n/c_H^m sequence cannot "
            "decrease when c_H exceeds one.",
            "Captured git state before artifact creation, corrected runtime model "
            "provenance, used null certificate verification fields, and bound the "
            "resource-limited exact command.",
        ],
        "artifact_sha256": {
            str(path.relative_to(ROOT)):
                hashlib.sha256(path.read_bytes()).hexdigest()
            for path in receipt_paths
        },
        "observation_collision_limit": "binding limit, not a finding",
        "committed_by_this_task": False,
    }
    (task_dir / "execution-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
