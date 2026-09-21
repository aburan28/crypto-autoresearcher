"""Battery member constructions: N1, N2, N2-twin, N3, N4, N5.

N1's Frobenius-permutation logic is a direct, disclosed generalisation of
EXP-MONO-4c7479's `arm_a.py` (same base construction: (e1,e2) -> D -> t1,t2
-> f(t_i) -> y1,y2 -> labelled points {P1,-P1,P2,-P2} -> Frobenius
permutation -> D_4-conjugacy-class bucket), with:
  - `fp_common.Fp2`/`Fp4` (ad hoc towers over literal F_p) REPLACED by this
    contract's own `tower.Level1`/`Level2` built over the ladder step's own
    generic base field F0 = fieldext.FpK(p,k) (NOT F_p when k>1);
  - Frobenius realised as THIS ladder step's Frob_p^k (identity on level 0,
    `Level1.conj` on level 1, `Level2.frob` on level 2) rather than the
    single absolute Frobenius x->x^p arm_a.py used (which is the k=1
    special case).
"""
from __future__ import annotations

import fieldext as fe
import fieldpoly as fp
import tower

STRATUM_NONE = "none"
STRATUM_I = "i"
STRATUM_II = "ii"


# ---------------------------------------------------------------------
# Generic level-crossing helpers (within ONE ladder step's own tower;
# NEVER crosses between different ladder levels k).
# ---------------------------------------------------------------------

def embed(val, from_level, to_level, F0, L1, L2):
    if from_level == to_level:
        return val
    if from_level == 0 and to_level == 1:
        return L1.from_level0(val)
    if from_level == 0 and to_level == 2:
        return L2.from_level1(L1.from_level0(val))
    if from_level == 1 and to_level == 2:
        return L2.from_level1(val)
    raise ValueError((from_level, to_level))


def neg_val(val, level, F0, L1, L2):
    if level == 0:
        return F0.neg(val)
    if level == 1:
        return L1.neg(val)
    if level == 2:
        return L2.neg(val)
    raise ValueError(level)


def eq_val(a, b, level, F0, L1, L2):
    if level == 0:
        return F0.eq(a, b)
    if level == 1:
        return L1.eq(a, b)
    if level == 2:
        return L2.eq(a, b)
    raise ValueError(level)


def frob_val(val, level, F0, L1, L2):
    """Frob_p^k of THIS ladder step, restricted to `level`."""
    if level == 0:
        return val  # identity: level-0 elements already lie in F_{p^k}
    if level == 1:
        return L1.conj(val)
    if level == 2:
        return L2.frob(val)
    raise ValueError(level)


def is_zero_val(val, level, F0, L1, L2):
    if level == 0:
        return F0.is_zero(val)
    if level == 1:
        return L1.is_zero(val)
    if level == 2:
        return L2.is_zero(val)
    raise ValueError(level)


class Towers:
    """Cache of Level1/Level2 towers keyed by the base field F0 (a single
    ladder step's own F_{p^k})."""

    def __init__(self, F0: fe.FpK):
        self.F0 = F0
        self._L1 = None
        self._L2 = None

    def L1(self) -> tower.Level1:
        if self._L1 is None:
            self._L1 = tower.Level1(self.F0)
        return self._L1

    def L2(self) -> tower.Level2:
        if self._L2 is None:
            self._L2 = tower.Level2(self.L1())
        return self._L2


# ---------------------------------------------------------------------
# N1: m=3 Semaev symmetric-base cover, curve (A,B)=(1,1).
# ---------------------------------------------------------------------

def _f_of(level, t, A_elt, B_elt, F0, L1, L2):
    if level == 0:
        t2 = F0.mul(t, t)
        t3 = F0.mul(t2, t)
        return F0.add(F0.add(t3, F0.mul(A_elt, t)), B_elt)
    if level == 1:
        A1 = L1.from_level0(A_elt)
        B1 = L1.from_level0(B_elt)
        t2 = L1.mul(t, t)
        t3 = L1.mul(t2, t)
        return L1.add(L1.add(t3, L1.mul(A1, t)), B1)
    raise ValueError(level)


def _lift_y(level, f_val, F0, L1, L2, reverse=False):
    """Returns (y_level, y_val); mirrors arm_a.lift_y exactly, generalised."""
    if level == 0:
        if F0.is_zero(f_val):
            return 0, F0.zero()
        if F0.is_square(f_val):
            return 0, F0.sqrt(f_val, reverse=reverse)
        v = L1.sqrt(L1.from_level0(f_val), reverse=reverse)
        return 1, v
    if level == 1:
        if L1.is_zero(f_val):
            return 1, L1.zero()
        if L1.is_square(f_val):
            return 1, L1.sqrt(f_val, reverse=reverse)
        v = L2.sqrt_of_level1_nonsquare(f_val, reverse=reverse)
        return 2, v
    raise ValueError(level)


def classify_permutation(perm) -> str:
    """Identical combinatorics to arm_a.classify_permutation (pure
    permutation-group logic, no field arithmetic)."""
    block_of = {0: 0, 1: 0, 2: 1, 3: 1}
    blocks_swapped = any(block_of[perm[i]] != block_of[i] for i in range(4))
    if perm == (0, 1, 2, 3):
        return "identity"
    if not blocks_swapped:
        swap1 = perm[0] != 0
        swap2 = perm[2] != 2
        if swap1 and swap2:
            return "sigma1_sigma2"
        return "sigma_i"
    perm2 = tuple(perm[perm[i]] for i in range(4))
    if perm2 == (0, 1, 2, 3):
        return "block_swap_involution"
    return "four_cycle"


def n1_classify_point(F0: fe.FpK, tw: Towers, A: int, B: int, e1, e2, reverse=False):
    """Classify one N1 base point (e1,e2), each a level-0 element (a
    k-tuple of F0). Returns dict with regime/stratum/class/perm."""
    p = F0.p
    inv2 = F0.inv(F0.from_int(2))
    D = F0.sub(F0.mul(e1, e1), F0.mul(F0.from_int(4), e2))
    if F0.is_zero(D):
        return {"regime": "ramified", "stratum": STRATUM_I, "class": None, "perm": None}
    A_elt = F0.from_int(A)
    B_elt = F0.from_int(B)
    if F0.is_square(D):
        regime = "split"
        sqrtD = F0.sqrt(D, reverse=reverse)
        t1 = F0.mul(F0.add(e1, sqrtD), inv2)
        t2 = F0.mul(F0.sub(e1, sqrtD), inv2)
        t_level = 0
    else:
        regime = "inert"
        L1 = tw.L1()
        delta = L1.sqrt(L1.from_level0(D), reverse=reverse)
        base = L1.from_level0(F0.mul(inv2, e1))
        t1 = L1.add(base, delta)
        t2 = L1.sub(base, delta)
        t_level = 1

    L1 = tw.L1()
    L2 = tw.L2()

    f1 = _f_of(t_level, t1, A_elt, B_elt, F0, L1, L2)
    f2 = _f_of(t_level, t2, A_elt, B_elt, F0, L1, L2)
    z1 = is_zero_val(f1, t_level, F0, L1, L2)
    z2 = is_zero_val(f2, t_level, F0, L1, L2)
    if z1 or z2:
        return {"regime": regime, "stratum": STRATUM_II, "class": None, "perm": None}

    y1_level, y1 = _lift_y(t_level, f1, F0, L1, L2, reverse=reverse)
    y2_level, y2 = _lift_y(t_level, f2, F0, L1, L2, reverse=reverse)
    lvl = max(t_level, y1_level, y2_level)

    tx1 = embed(t1, t_level, lvl, F0, L1, L2)
    tx2 = embed(t2, t_level, lvl, F0, L1, L2)
    yy1 = embed(y1, y1_level, lvl, F0, L1, L2)
    yy2 = embed(y2, y2_level, lvl, F0, L1, L2)

    pts = [
        (tx1, yy1),
        (tx1, neg_val(yy1, lvl, F0, L1, L2)),
        (tx2, yy2),
        (tx2, neg_val(yy2, lvl, F0, L1, L2)),
    ]

    def frob_point(pt):
        x, y = pt
        return (frob_val(x, lvl, F0, L1, L2), frob_val(y, lvl, F0, L1, L2))

    perm = []
    for i in range(4):
        img = frob_point(pts[i])
        match = None
        for j in range(4):
            if eq_val(img[0], pts[j][0], lvl, F0, L1, L2) and eq_val(img[1], pts[j][1], lvl, F0, L1, L2):
                match = j
                break
        if match is None:
            raise RuntimeError(f"N1: Frobenius image of point {i} matched no labelled point "
                                f"(e1={e1}, e2={e2}, k={F0.k})")
        perm.append(match)
    perm = tuple(perm)
    cls = classify_permutation(perm)
    return {"regime": regime, "stratum": STRATUM_NONE, "class": cls, "perm": perm}


# ---------------------------------------------------------------------
# N2 / N2-twin: h_sep-shaped bi-quadratics, base variable e.
# ---------------------------------------------------------------------

def n2_classify_point(F0: fe.FpK, tw: Towers, e, a_coeff_fn, b_coeff_fn, reverse=False):
    """a_coeff_fn(e)->a(e) elt of F0; b_coeff_fn(e)->b(e) elt of F0.
    Fibre: P1=+sqrt(a(e)) (level depends), -P1, P2=+sqrt(b(e)), -P2.
    Returns dict with stratum/class/perm, using the SAME 4-point labelled
    convention and D_4-class-name vocabulary as N1 (restricted to the
    (Z/2)^2 subgroup actually realizable)."""
    a_val = a_coeff_fn(e)
    b_val = b_coeff_fn(e)
    if F0.is_zero(a_val) or F0.is_zero(b_val):
        return {"stratum": STRATUM_II, "class": None, "perm": None}

    L1 = tw.L1()
    L2 = tw.L2()

    def lift_sqrt(level, val):
        if level == 0:
            if F0.is_square(val):
                return 0, F0.sqrt(val, reverse=reverse)
            return 1, L1.sqrt(L1.from_level0(val), reverse=reverse)
        raise ValueError(level)

    y1_level, y1 = lift_sqrt(0, a_val)
    y2_level, y2 = lift_sqrt(0, b_val)
    lvl = max(y1_level, y2_level)
    yy1 = embed(y1, y1_level, lvl, F0, L1, L2)
    yy2 = embed(y2, y2_level, lvl, F0, L1, L2)

    pts = [yy1, neg_val(yy1, lvl, F0, L1, L2), yy2, neg_val(yy2, lvl, F0, L1, L2)]

    def frob_pt(v):
        return frob_val(v, lvl, F0, L1, L2)

    perm = []
    for i in range(4):
        img = frob_pt(pts[i])
        match = None
        for j in range(4):
            if eq_val(img, pts[j], lvl, F0, L1, L2):
                match = j
                break
        if match is None:
            raise RuntimeError(f"N2-shape: Frobenius image of point {i} matched no labelled point (e={e}, k={F0.k})")
        perm.append(match)
    perm = tuple(perm)
    cls = classify_permutation(perm)
    return {"stratum": STRATUM_NONE, "class": cls, "perm": perm}


# ---------------------------------------------------------------------
# Subgroup generation (orbit/Schreier-style closure) for N1/N2/N2-twin/N4.
# ---------------------------------------------------------------------

def subgroup_closure(generators, n: int):
    """Given a set of permutations of {0,...,n-1} (as tuples), return the
    subgroup of S_n they generate, as a sorted list of tuples."""
    identity = tuple(range(n))

    def compose(a, b):
        return tuple(a[b[i]] for i in range(n))

    group = {identity}
    frontier = set(generators) | {identity}
    group |= frontier
    changed = True
    while changed:
        changed = False
        new_elems = set()
        for g in group:
            for h in generators:
                c1 = compose(g, h)
                c2 = compose(h, g)
                for c in (c1, c2):
                    if c not in group and c not in new_elems:
                        new_elems.add(c)
        if new_elems:
            group |= new_elems
            changed = True
    return sorted(group)


# ---------------------------------------------------------------------
# N3 / N5: random monic polynomial density controls.
# ---------------------------------------------------------------------

def classify_random_poly_shape(F0: fe.FpK, coeffs):
    """coeffs: ascending-degree list of F0 elements, monic (leading coeff
    F0.one()), for a squarefree polynomial. Returns the distinct-degree
    factorization shape (sorted list of (degree, multiplicity))."""
    return fp.distinct_degree_shape(coeffs, F0, F0.q)


def shape_to_partition_label(shape, degree: int) -> str:
    degrees = []
    for d, mult in shape:
        degrees.extend([d] * mult)
    degrees.sort()
    key = tuple(degrees)
    if degree == 4:
        table = {
            (1, 1, 1, 1): "1^4",
            (1, 1, 2): "2.1.1",
            (2, 2): "2^2",
            (1, 3): "3+1",
            (4,): "4",
        }
    elif degree == 5:
        table = {
            (1, 1, 1, 1, 1): "1^5",
            (1, 1, 1, 2): "2.1^3",
            (1, 2, 2): "2^2.1",
            (1, 1, 3): "3.1^2",
            (2, 3): "3.2",
            (1, 4): "4.1",
            (5,): "5",
        }
    else:
        raise ValueError(degree)
    return table.get(key, f"other:{key}")
