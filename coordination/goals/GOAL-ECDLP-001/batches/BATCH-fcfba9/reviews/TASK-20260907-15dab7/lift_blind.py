"""Blind re-derivation of the canonical order-n prime-to-p lift.

Derived only from:
  coordination/goals/GOAL-ECDLP-001/batches/BATCH-fcfba9/review_plan.yaml
  experiments/EXP-ECDLP-a98ea9/specification.yaml

Construction (specification / review_plan.blind_rederivation):
  gcd(n, p) = 1 is required (else refuse).
  Hensel-lift the Weierstrass equation (point lift with x held at its
  F_p representative; Newton on y^2 - x^3 - A x - B).
  Apply [p] exactly (r-1) times.
  Multiply by (p^{r-1})^{-1} mod n.

Quantity: ordinary base-p digits of affine x of
  (1) [k] of the canonical order-n lift of S
  versus
  (2) the canonical order-n lift of [k]S
at precision r = 4.

Arithmetic over Z/p^r uses the Renes–Costello–Batina complete
homogeneous-projective addition formulas (ePrint 2015/1060, Algorithm 1:
x = X/Z, y = Y/Z) so residue-class collisions remain well-defined.
Affine conversion guards a non-unit Z.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

# Parameters copied from review_plan.blind_rederivation.parameters.
# Not looked up from any run receipt.
SEEDS = [3, 5, 7, 11, 13, 17, 19, 23]
MIN_SAMPLES_PER_INSTANCE = 50
PRECISION = 4
INSTANCES = [
    {"p": 47237, "A": 31367, "B": 41141, "n": 47057, "S": [2, 97]},
    {"p": 128629, "A": 119056, "B": 83257, "n": 42667, "S": [87124, 110926]},
    {"p": 234527, "A": 185876, "B": 26302, "n": 58453, "S": [159550, 198939]},
    {"p": 325411, "A": 259076, "B": 82146, "n": 162611, "S": [255196, 53661]},
    {"p": 949423, "A": 610648, "B": 188380, "n": 39503, "S": [377953, 722598]},
    {"p": 1422461, "A": 1184784, "B": 515035, "n": 79043, "S": [616886, 329503]},
]


def _mod(x: int, m: int) -> int:
    return x % m


@dataclass(frozen=True)
class Jac:
    """Homogeneous point (X : Y : Z) on y^2 = x^3 + A x + B over Z/m.

    Affine meaning: x = X/Z, y = Y/Z when Z is a unit. Named Jac only
    as the file-level handle; coordinates are NOT Jacobian.
    """

    X: int
    Y: int
    Z: int
    m: int
    A: int
    B: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "X", _mod(self.X, self.m))
        object.__setattr__(self, "Y", _mod(self.Y, self.m))
        object.__setattr__(self, "Z", _mod(self.Z, self.m))
        object.__setattr__(self, "A", _mod(self.A, self.m))
        object.__setattr__(self, "B", _mod(self.B, self.m))


def infinity(m: int, A: int, B: int) -> Jac:
    return Jac(0, 1, 0, m, A, B)


def is_infinity(P: Jac) -> bool:
    return P.Z == 0


def affine_to_jac(x: int, y: int, m: int, A: int, B: int) -> Jac:
    return Jac(x, y, 1, m, A, B)


def jac_neg(P: Jac) -> Jac:
    return Jac(P.X, -P.Y, P.Z, P.m, P.A, P.B)


def on_curve_affine(x: int, y: int, A: int, B: int, m: int) -> bool:
    return _mod(y * y - (x * x * x + A * x + B), m) == 0


def jac_to_affine(P: Jac, p: int) -> tuple[int, int]:
    """Return affine (x, y) = (X/Z, Y/Z). Raises if Z is not a unit mod p."""
    if is_infinity(P):
        raise ValueError("point at infinity: no affine coordinates")
    if math.gcd(P.Z, p) != 1:
        raise ValueError("non-unit projective Z (denominator not a unit)")
    inv_z = pow(P.Z, -1, P.m)
    x = (P.X * inv_z) % P.m
    y = (P.Y * inv_z) % P.m
    return x, y


def rcb_add(P: Jac, Q: Jac) -> Jac:
    """Renes–Costello–Batina complete addition (homogeneous, short Weierstrass).

    Algorithm 1 of IACR ePrint 2015/1060, with b3 = 3B. Coordinates satisfy
    x = X/Z, y = Y/Z. Polynomial identities over Z; valid on Z/p^r for p > 3.
    """
    if P.m != Q.m or P.A != Q.A or P.B != Q.B:
        raise ValueError("point ring / curve mismatch")
    m = P.m
    a = P.A
    b3 = (3 * P.B) % m

    X1, Y1, Z1 = P.X, P.Y, P.Z
    X2, Y2, Z2 = Q.X, Q.Y, Q.Z

    t0 = (X1 * X2) % m
    t1 = (Y1 * Y2) % m
    t2 = (Z1 * Z2) % m
    t3 = (X1 + Y1) % m
    t4 = (X2 + Y2) % m
    t3 = (t3 * t4) % m
    t4 = (t0 + t1) % m
    t3 = (t3 - t4) % m
    t4 = (X1 + Z1) % m
    t5 = (X2 + Z2) % m
    t4 = (t4 * t5) % m
    t5 = (t0 + t2) % m
    t4 = (t4 - t5) % m
    t5 = (Y1 + Z1) % m
    X3 = (Y2 + Z2) % m
    t5 = (t5 * X3) % m
    X3 = (t1 + t2) % m
    t5 = (t5 - X3) % m
    Z3 = (a * t4) % m
    X3 = (b3 * t2) % m
    Z3 = (X3 + Z3) % m
    X3 = (t1 - Z3) % m
    Z3 = (t1 + Z3) % m
    Y3 = (X3 * Z3) % m
    t1 = (t0 + t0) % m
    t1 = (t1 + t0) % m
    t2 = (a * t2) % m
    t4 = (b3 * t4) % m
    t1 = (t1 + t2) % m
    t2 = (t0 - t2) % m
    t2 = (a * t2) % m
    t4 = (t4 + t2) % m
    t0 = (t1 * t4) % m
    Y3 = (Y3 + t0) % m
    t0 = (t5 * t4) % m
    X3 = (t3 * X3) % m
    X3 = (X3 - t0) % m
    t0 = (t3 * t1) % m
    Z3 = (t5 * Z3) % m
    Z3 = (Z3 + t0) % m
    return Jac(X3, Y3, Z3, m, P.A, P.B)


def scale(k: int, P: Jac) -> Jac:
    """Double-and-add using complete addition for both double and add."""
    if k < 0:
        return scale(-k, jac_neg(P))
    R = infinity(P.m, P.A, P.B)
    if k == 0:
        return R
    for bit in bin(k)[2:]:
        R = rcb_add(R, R)
        if bit == "1":
            R = rcb_add(R, P)
    return R


def hensel_lift_point(
    x0: int, y0: int, A: int, B: int, p: int, r: int
) -> tuple[int, int]:
    """Hensel-lift (x0, y0) on E(F_p) to E(Z/p^r) with x held at x0 mod p.

    Newton on f(y) = y^2 - x^3 - A x - B, incrementing valuation one step
    at a time. Requires 2y to be a unit (non-2-torsion reduction).
    """
    if r < 1:
        raise ValueError("precision r must be >= 1")
    x = int(x0) % p
    y = int(y0) % p
    if not on_curve_affine(x, y, A, B, p):
        raise ValueError("input is not on E(F_p)")
    if math.gcd(2 * y, p) != 1:
        raise ValueError("non-unit 2y: cannot Hensel-lift this reduction")
    for i in range(1, r):
        mod = p ** (i + 1)
        fval = y * y - x * x * x - A * x - B
        two_y = (2 * y) % mod
        if math.gcd(two_y, p) != 1:
            raise ValueError("non-unit 2y during Hensel lift")
        y = (y - fval * pow(two_y, -1, mod)) % mod
    m = p**r
    x = x % m
    y = y % m
    if not on_curve_affine(x, y, A, B, m):
        raise ValueError("Hensel lift failed Weierstrass equation")
    return x, y


def canonical_order_n_lift(
    x_fp: int, y_fp: int, A: int, B: int, p: int, n: int, r: int
) -> Jac:
    """k-free canonical order-n prime-to-p lift of an F_p point.

    Hensel-lift the Weierstrass equation, apply [p] exactly (r-1) times,
    multiply by (p^{r-1})^{-1} mod n. Refuses gcd(n, p) != 1.
    """
    if math.gcd(n, p) != 1:
        raise ValueError("gcd(n, p) != 1: canonical order-n lift does not exist")
    if r < 1:
        raise ValueError("precision r must be >= 1")
    m = p**r
    A_m = A % m
    B_m = B % m
    x_h, y_h = hensel_lift_point(x_fp, y_fp, A_m, B_m, p, r)
    P = affine_to_jac(x_h, y_h, m, A_m, B_m)
    for _ in range(r - 1):
        P = scale(p, P)
    if r == 1:
        inv = 1
    else:
        inv = pow(pow(p, r - 1, n), -1, n)
    P = scale(inv, P)
    return P


def ordinary_base_p_digits(x: int, p: int, r: int) -> tuple[int, ...]:
    """Ordinary base-p digits of the unique representative in [0, p^r)."""
    m = p**r
    v = x % m
    digits = []
    for _ in range(r):
        digits.append(v % p)
        v //= p
    return tuple(digits)


def fp_neg(y: int, p: int) -> int:
    return (-y) % p


def fp_add(
    P: tuple[int, int] | None,
    Q: tuple[int, int] | None,
    A: int,
    p: int,
) -> tuple[int, int] | None:
    """Affine addition over the field F_p. None is the identity."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        # doubling
        denom = (2 * y1) % p
        if denom == 0:
            raise ValueError("non-unit 2y in F_p doubling")
        lam = ((3 * x1 * x1 + A) * pow(denom, -1, p)) % p
    else:
        denom = (x2 - x1) % p
        lam = ((y2 - y1) * pow(denom, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def fp_scale(
    k: int, P: tuple[int, int] | None, A: int, p: int
) -> tuple[int, int] | None:
    if k < 0:
        if P is None:
            return None
        return fp_scale(-k, (P[0], fp_neg(P[1], p)), A, p)
    R: tuple[int, int] | None = None
    if k == 0:
        return None
    acc = P
    kk = k
    while kk:
        if kk & 1:
            R = fp_add(R, acc, A, p)
        acc = fp_add(acc, acc, A, p)
        kk >>= 1
    return R


def sample_ks(n: int, seeds: list[int], min_samples: int) -> list[int]:
    """Split at least min_samples draws of k in 1..n-1 across the seeds."""
    n_seeds = len(seeds)
    per = (min_samples + n_seeds - 1) // n_seeds
    ks: list[int] = []
    for seed in seeds:
        rng = random.Random(seed)
        seen: set[int] = set()
        while len(seen) < per:
            k = rng.randrange(1, n)
            if k not in seen:
                seen.add(k)
                ks.append(k)
    return ks


def sanity_instance(inst: dict) -> dict:
    p, A, B, n = inst["p"], inst["A"], inst["B"], inst["n"]
    Sx, Sy = inst["S"]
    notes = {}
    notes["gcd_n_p"] = math.gcd(n, p)
    notes["on_curve_fp"] = on_curve_affine(Sx, Sy, A, B, p)
    nS = fp_scale(n, (Sx, Sy), A, p)
    notes["nS_is_infinity"] = nS is None
    twoS = fp_scale(2, (Sx, Sy), A, p)
    notes["S_not_2_torsion"] = twoS is not None
    return notes


def run_instance(inst: dict, seeds: list[int], min_samples: int, r: int) -> dict:
    p, A, B, n = inst["p"], inst["A"], inst["B"], inst["n"]
    Sx, Sy = inst["S"]
    sanity = sanity_instance(inst)
    if sanity["gcd_n_p"] != 1:
        raise ValueError(f"gcd(n, p) = {sanity['gcd_n_p']} != 1")
    if not sanity["on_curve_fp"]:
        raise ValueError("S is not on E(F_p)")
    if not sanity["nS_is_infinity"]:
        raise ValueError("[n]S is not infinity over F_p")

    # Cache the canonical lift of S (path 1 base point).
    S_hat = canonical_order_n_lift(Sx, Sy, A, B, p, n, r)
    sx, sy = jac_to_affine(S_hat, p)
    if (sx % p, sy % p) != (Sx % p, Sy % p) and (
        sx % p,
        (-sy) % p,
    ) != (Sx % p, Sy % p):
        # Must reduce to ±S; the construction should reduce to S itself.
        if (sx % p, sy % p) != (Sx % p, Sy % p):
            raise ValueError("canonical lift of S does not reduce to S")
    if (sx % p, sy % p) != (Sx % p, Sy % p):
        raise ValueError("canonical lift of S does not reduce to S")

    n_hat = scale(n, S_hat)
    if not is_infinity(n_hat):
        # Over Z/p^r a true order-n point must be O after [n].
        raise ValueError("[n] of the constructed lift of S is not infinity")

    ks = sample_ks(n, seeds, min_samples)
    compared = 0
    agree = 0
    first_disagreement = None
    skipped = []

    for k in ks:
        Q_fp = fp_scale(k, (Sx, Sy), A, p)
        if Q_fp is None:
            skipped.append({"k": k, "reason": "[k]S is infinity over F_p"})
            continue
        try:
            k_Shat = scale(k, S_hat)
            x1, y1 = jac_to_affine(k_Shat, p)
        except ValueError as exc:
            skipped.append({"k": k, "reason": f"path1: {exc}"})
            continue
        try:
            Q_hat = canonical_order_n_lift(Q_fp[0], Q_fp[1], A, B, p, n, r)
            x2, y2 = jac_to_affine(Q_hat, p)
        except ValueError as exc:
            skipped.append({"k": k, "reason": f"path2: {exc}"})
            continue

        d1 = ordinary_base_p_digits(x1, p, r)
        d2 = ordinary_base_p_digits(x2, p, r)
        compared += 1
        if d1 == d2:
            agree += 1
        elif first_disagreement is None:
            first_disagreement = {
                "k": k,
                "path1_digits": list(d1),
                "path2_digits": list(d2),
                "path1_x": x1,
                "path2_x": x2,
            }

    return {
        "p": p,
        "A": A,
        "B": B,
        "n": n,
        "S": [Sx, Sy],
        "r": r,
        "sanity": sanity,
        "n_k_sampled": len(ks),
        "compared": compared,
        "agree": agree,
        "first_disagreement": first_disagreement,
        "skipped": skipped,
        "ks": ks,
    }


def _self_check_rcb() -> None:
    """Tiny field check: complete formulas recover affine addition over F_p."""
    p, A, B = 17, 2, 2
    # y^2 = x^3 + 2x + 2 over F_17; (5, 1) is on the curve.
    assert on_curve_affine(5, 1, A, B, p)
    P = affine_to_jac(5, 1, p, A, B)
    O = infinity(p, A, B)
    PplusO = rcb_add(P, O)
    x, y = jac_to_affine(PplusO, p)
    assert (x, y) == (5, 1), (x, y)
    PplusNeg = rcb_add(P, jac_neg(P))
    assert is_infinity(PplusNeg)
    twoP = rcb_add(P, P)
    x2, y2 = jac_to_affine(twoP, p)
    aff2 = fp_add((5, 1), (5, 1), A, p)
    assert aff2 == (x2, y2), ((x2, y2), aff2)


def main() -> None:
    _self_check_rcb()
    out_dir = Path(__file__).resolve().parent
    results = []
    for inst in INSTANCES:
        rec = run_instance(inst, SEEDS, MIN_SAMPLES_PER_INSTANCE, PRECISION)
        results.append(rec)
        print(
            f"p={rec['p']} n={rec['n']} compared={rec['compared']} "
            f"agree={rec['agree']} skipped={len(rec['skipped'])} "
            f"first_disagreement={rec['first_disagreement']}"
        )
    payload = {
        "seeds": SEEDS,
        "min_samples_per_instance": MIN_SAMPLES_PER_INSTANCE,
        "precision": PRECISION,
        "instances": results,
    }
    out_path = out_dir / "blind_raw.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
