"""Arm (a): INDEPENDENT PATH 1, direct group arithmetic.

Computes t1, t2 from (e1,e2), lifts to actual curve points via f(t_i), and
applies Frobenius DIRECTLY to point coordinates (never via c1, c0, or h(Y)).
Classifies the resulting permutation of the fixed labelled 4-point set
{P1, -P1, P2, -P2} into the five D_4-conjugacy-class buckets used by the
whole contract: identity, sigma_i, sigma1_sigma2, block_swap_involution,
four_cycle.

THIS MODULE NEVER COMPUTES c1, c0, OR h(Y) -- see independence_requirement.
It imports only fp_common.py (generic field arithmetic, shared with arm_b
in the same limited sense a shared `mulmod` would be, per the frozen
contract's own wording).
"""
from __future__ import annotations

import fp_common as fc

STRATUM_NONE = "none"
STRATUM_I = "i"     # e1^2-4e2=0 (t1=t2), ramified regime, excluded
STRATUM_II = "ii"   # f(t1)*f(t2)=0, excluded


def f_of(t_level, t_val, A, B, p, fp2, fp4):
    """Evaluate f(t)=t^3+A t+B at a coordinate value living at `t_level`."""
    if t_level == 0:
        return (t_val * t_val % p * t_val + A * t_val + B) % p
    if t_level == 1:
        A2 = fp2.from_fp(A)
        B2 = fp2.from_fp(B)
        t2 = fp2.mul(t_val, t_val)
        t3 = fp2.mul(t2, t_val)
        return fp2.add(fp2.add(t3, fp2.mul(A2, t_val)), B2)
    raise ValueError(t_level)


def is_zero(level, val, p):
    if level == 0:
        return val % p == 0
    if level == 1:
        return val[0] % p == 0 and val[1] % p == 0
    raise ValueError(level)


def lift_y(t_level, f_val, p, fp2, fp4):
    """Given f(t_i) at `t_level`, return (y_level, y_val).

    - f_val == 0: 2-torsion, y = 0 at t_level (caller flags stratum ii).
    - t_level == 0 (split regime), f_val a QR in Fp: y in Fp (level 0).
    - t_level == 0, f_val a non-QR in Fp: y lifts to Fp2 (level 1), pure
      w-multiple form (see fp_common.inert_delta-style derivation).
    - t_level == 1 (inert regime), f_val a square in Fp2: y in Fp2 (level 1).
    - t_level == 1, f_val a non-square in Fp2: y lifts to Fp4 (level 2).
    """
    if t_level == 0:
        if f_val % p == 0:
            return 0, 0
        if fc.is_qr(f_val, p):
            return 0, fc.sqrt_mod(f_val, p)
        # non-residue element of Fp, lift into Fp2 as pure-w form
        d = fp2.d
        t2 = (f_val * pow(d, -1, p)) % p
        root = fc.sqrt_mod(t2, p)
        return 1, (0, root)
    if t_level == 1:
        if is_zero(1, f_val, p):
            return 1, (0, 0)
        if fp2.is_square(f_val):
            return 1, fp2.sqrt(f_val)
        return 2, fp4.sqrt_of_fp2_nonsquare(f_val)
    raise ValueError(t_level)


def classify_from_t_pair(p: int, A: int, B: int, t1, t2, t_level: int,
                          fp2: fc.Fp2, fp4: fc.Fp4):
    """Core Frobenius-permutation computation given an already-determined
    (t1, t2) pair at a known field level (0=Fp, split; 1=Fp2, inert/or an
    ordered-base re-run of a split pair). Returns the same shape as
    `classify_point`'s off-stratum branch, WITHOUT re-deriving t1,t2 from
    (e1,e2) -- this is the piece reused by the matched-ordered-base control,
    which supplies an ORDERED (t1,t2) directly rather than deriving it from
    a symmetric (e1,e2)."""
    f1 = f_of(t_level, t1, A, B, p, fp2, fp4)
    f2 = f_of(t_level, t2, A, B, p, fp2, fp4)
    z1 = is_zero(t_level, f1, p)
    z2 = is_zero(t_level, f2, p)
    if z1 or z2:
        return {"stratum": STRATUM_II, "class": None, "perm": None, "f1": f1, "f2": f2}

    y1_level, y1 = lift_y(t_level, f1, p, fp2, fp4)
    y2_level, y2 = lift_y(t_level, f2, p, fp2, fp4)
    lvl = max(t_level, y1_level, y2_level)

    tx1 = fc.embed(t1, t_level, lvl)
    tx2 = fc.embed(t2, t_level, lvl)
    yy1 = fc.embed(y1, y1_level, lvl)
    yy2 = fc.embed(y2, y2_level, lvl)

    # Labelled points, fixed convention: 0=P1=(t1,y1), 1=-P1=(t1,-y1),
    # 2=P2=(t2,y2), 3=-P2=(t2,-y2).
    pts = [
        (tx1, yy1),
        (tx1, fc.neg_val(yy1, lvl, p)),
        (tx2, yy2),
        (tx2, fc.neg_val(yy2, lvl, p)),
    ]

    def frob_point(pt):
        x, y = pt
        return (fc.frob_val(x, lvl, p, fp2, fp4), fc.frob_val(y, lvl, p, fp2, fp4))

    perm = []
    for i in range(4):
        img = frob_point(pts[i])
        match = None
        for j in range(4):
            if fc.eq_val(img[0], pts[j][0], lvl, p) and fc.eq_val(img[1], pts[j][1], lvl, p):
                match = j
                break
        if match is None:
            raise RuntimeError(f"Frobenius image of point {i} did not match any labelled point "
                                f"(t1={t1}, t2={t2}, p={p}, A={A}, B={B}) -- implementation bug")
        perm.append(match)
    perm = tuple(perm)

    cls = classify_permutation(perm)
    return {"stratum": STRATUM_NONE, "class": cls, "perm": perm, "f1": f1, "f2": f2}


def classify_point(p: int, A: int, B: int, e1: int, e2: int, fp2: fc.Fp2, fp4: fc.Fp4):
    """Classify one base point (e1,e2). Returns a dict with regime, stratum,
    the observed D_4 class (or None if excluded), and the realized labelled
    permutation (tuple of 4 ints, or None if excluded)."""
    D = (e1 * e1 - 4 * e2) % p
    inv2 = pow(2, -1, p)

    if D == 0:
        return {"regime": "ramified", "stratum": STRATUM_I, "class": None, "perm": None,
                "t1": None, "t2": None, "t_level": None}

    if fc.is_qr(D, p):
        regime = "split"
        sqrtD = fc.sqrt_mod(D, p)
        t1 = (e1 + sqrtD) * inv2 % p
        t2 = (e1 - sqrtD) * inv2 % p
        t_level = 0
    else:
        regime = "inert"
        delta = fc.inert_delta(fp2, D)
        base = fp2.scal(inv2 * e1 % p, (1, 0))
        t1 = fp2.add(base, delta)
        t2 = fp2.sub(base, delta)
        t_level = 1

    core = classify_from_t_pair(p, A, B, t1, t2, t_level, fp2, fp4)
    core["regime"] = regime
    core["t1"] = t1
    core["t2"] = t2
    core["t_level"] = t_level
    return core


def classify_permutation(perm) -> str:
    """Map a permutation of labelled indices {0:P1,1:-P1,2:P2,3:-P2} to one
    of the five D_4-conjugacy-class names, resolving the cycle-type-2^2
    observation collision (sigma1_sigma2 vs block_swap_involution) using
    the block structure of the labelling itself (index 0,1 in block A;
    2,3 in block B) -- information intrinsic to arm (a)'s own permutation,
    not borrowed from the character-triple check or arm (b)."""
    block_of = {0: 0, 1: 0, 2: 1, 3: 1}
    blocks_swapped = any(block_of[perm[i]] != block_of[i] for i in range(4))
    if perm == (0, 1, 2, 3):
        return "identity"
    if not blocks_swapped:
        # within-block only: perm restricted to {0,1} and {2,3} each a
        # permutation of that pair.
        swap1 = perm[0] != 0  # 0<->1 swapped
        swap2 = perm[2] != 2  # 2<->3 swapped
        if swap1 and swap2:
            return "sigma1_sigma2"
        return "sigma_i"
    # blocks swapped: check order (involution vs order-4)
    perm2 = tuple(perm[perm[i]] for i in range(4))
    if perm2 == (0, 1, 2, 3):
        return "block_swap_involution"
    return "four_cycle"
