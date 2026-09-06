"""Per-ladder-step tower construction.

At base-change-ladder level k, the CENSUS base field is F_{p^k} itself
(an `fieldext.FpK` instance, level "0" for this step). Some base points'
fibres do not close up over F_{p^k} and need a quadratic extension
(level "1", F_{p^{2k}}) or a further quadratic extension on top of that
(level "2", F_{p^{4k}}). Finite fields of a given degree over a given base
are unique, so this is exactly analogous to the sibling contract
EXP-MONO-4c7479's Fp/Fp2/Fp4 tower -- generalised so the BASE ring is this
contract's own generic F_{p^k} (an `FpK` object) instead of literally F_p.
This is a disclosed, necessary generalisation of the tower PATTERN (not a
reversion to the ad hoc Fp2/Fp4 CLASSES themselves, which are specific to
base F_p and are not reused here); see `implementation.md`.

This never crosses between DIFFERENT ladder levels k1 != k2 (no embedding
of an F_{p^j} element into F_{p^k} coordinates is performed anywhere), only
extends the SAME base level's own field upward, exactly as
`field_arithmetic_representation.embeddings_between_levels` says is
sufficient.

Level-1 elements: (u, v) with u, v base-field (level-0) elements, meaning
u + v*w, w^2 = d (d a fixed non-residue of level 0).
Level-2 elements: (A, B) with A, B level-1 elements, meaning A + B*z,
z^2 = e (e a fixed non-square of level 1).
"""
from __future__ import annotations


class Level1:
    """Quadratic extension of a base field `F0` (an FpK, or any object
    exposing add/sub/mul/neg/eq/is_zero/pow/is_square/from_int/lex_key)."""

    def __init__(self, F0):
        self.F0 = F0
        self.q0 = F0.q
        self.d = F0.find_nonresidue()

    def zero(self):
        return (self.F0.zero(), self.F0.zero())

    def one(self):
        return (self.F0.one(), self.F0.zero())

    def from_level0(self, u):
        return (u, self.F0.zero())

    def add(self, x, y):
        F0 = self.F0
        return (F0.add(x[0], y[0]), F0.add(x[1], y[1]))

    def sub(self, x, y):
        F0 = self.F0
        return (F0.sub(x[0], y[0]), F0.sub(x[1], y[1]))

    def neg(self, x):
        F0 = self.F0
        return (F0.neg(x[0]), F0.neg(x[1]))

    def mul(self, x, y):
        F0, d = self.F0, self.d
        u1, v1 = x
        u2, v2 = y
        return (
            F0.add(F0.mul(u1, u2), F0.mul(d, F0.mul(v1, v2))),
            F0.add(F0.mul(u1, v2), F0.mul(v1, u2)),
        )

    def eq(self, x, y):
        return self.F0.eq(x[0], y[0]) and self.F0.eq(x[1], y[1])

    def is_zero(self, x):
        return self.F0.is_zero(x[0]) and self.F0.is_zero(x[1])

    def pow(self, x, n):
        result = self.one()
        base = x
        while n > 0:
            if n & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            n >>= 1
        return result

    def conj(self, x):
        """Frobenius of THIS ladder step's Frob_p^k restricted to level 1
        (the unique nontrivial automorphism fixing level 0): (u,v)->(u,-v)."""
        F0 = self.F0
        return (x[0], F0.neg(x[1]))

    def is_in_level0(self, x):
        return self.F0.is_zero(x[1])

    def lex_key(self, x):
        return (self.F0.lex_key(x[0]), self.F0.lex_key(x[1]))

    def is_square(self, x):
        if self.is_zero(x):
            return True
        return self.eq(self.pow(x, (self.q0 * self.q0 - 1) // 2), self.one())

    def sqrt(self, x, reverse: bool = False):
        """'Complex method' square root in level 1, generalising
        fp_common.Fp2.sqrt to an arbitrary base field F0. Returns the
        LEXICOGRAPHICALLY SMALLER (or, if `reverse`, larger -- the
        labelling-control convention) of the two roots, applied
        consistently at every level via Python tuple order on this
        contract's nested tower coordinate representation."""
        F0 = self.F0
        pick = max if reverse else min
        u, v = x
        if F0.is_zero(v):
            r = F0.sqrt(u, reverse=reverse)
            if r is not None:
                cand = (r, F0.zero())
                other = self.neg(cand)
                return pick(cand, other, key=self.lex_key)
            dinv = F0.inv(self.d)
            t2 = F0.mul(u, dinv)
            t = F0.sqrt(t2, reverse=reverse)
            if t is None:
                return None
            cand = (F0.zero(), t)
            other = self.neg(cand)
            return pick(cand, other, key=self.lex_key)
        norm_x = F0.sub(F0.mul(u, u), F0.mul(self.d, F0.mul(v, v)))
        m = F0.sqrt(norm_x)
        if m is None:
            return None
        inv2 = F0.inv(F0.from_int(2))
        for msign in (m, F0.neg(m)):
            s2 = F0.mul(F0.add(u, msign), inv2)
            s = F0.sqrt(s2)
            if s is None or F0.is_zero(s):
                continue
            t = F0.mul(v, F0.inv(F0.mul(F0.from_int(2), s)))
            cand = (s, t)
            if self.eq(self.mul(cand, cand), x):
                other = self.neg(cand)
                return pick(cand, other, key=self.lex_key)
        return None


class Level2:
    """Further quadratic extension, on top of a Level1 `L1`."""

    def __init__(self, L1: Level1):
        self.L1 = L1
        self.q1 = L1.q0 * L1.q0
        self.e = self._find_nonsquare()
        # sigma = Frob_p^k restricted to level 2 satisfies sigma(z) = z^{q0}
        # = (z^2)^{(q0-1)/2} * z = e^{(q0-1)/2} * z (q0 odd), q0 = L1.q0 =
        # THIS LADDER STEP'S BASE FIELD size, NOT q1 = q0^2. (Exactly
        # analogous to fp_common.Fp4's s = e^{(p-1)/2}, generalised from
        # base-field size p to base-field size q0.)
        self.s = L1.pow(self.e, (L1.q0 - 1) // 2)

    def _find_nonsquare(self):
        L1 = self.L1
        F0 = L1.F0
        # Try small combinations first (cheap), then exhaustively over F0
        # via the generator sequence (bounded, always terminates).
        for base_u in [0, 1]:
            for base_v in [1, 2, 3]:
                cand = (F0.from_int(base_u), F0.from_int(base_v))
                if not L1.is_square(cand):
                    return cand
        for cand0 in F0._gen_sequence():
            cand = (cand0, F0.one())
            if not L1.is_square(cand):
                return cand
        raise RuntimeError("no non-square found in Level1 (unexpected)")

    def zero(self):
        L1 = self.L1
        return (L1.zero(), L1.zero())

    def one(self):
        L1 = self.L1
        return (L1.one(), L1.zero())

    def from_level1(self, a):
        return (a, self.L1.zero())

    def add(self, x, y):
        L1 = self.L1
        return (L1.add(x[0], y[0]), L1.add(x[1], y[1]))

    def sub(self, x, y):
        L1 = self.L1
        return (L1.sub(x[0], y[0]), L1.sub(x[1], y[1]))

    def mul(self, x, y):
        L1, e = self.L1, self.e
        A, B = x
        C, D = y
        return (
            L1.add(L1.mul(A, C), L1.mul(e, L1.mul(B, D))),
            L1.add(L1.mul(A, D), L1.mul(B, C)),
        )

    def eq(self, x, y):
        L1 = self.L1
        return L1.eq(x[0], y[0]) and L1.eq(x[1], y[1])

    def frob(self, x):
        """Frob_p^k restricted to level 2, via the freshman's-dream
        identity, exactly generalising fp_common.Fp4.frob."""
        L1 = self.L1
        A, B = x
        return (L1.conj(A), L1.mul(L1.conj(B), self.s))

    def lex_key(self, x):
        L1 = self.L1
        return (L1.lex_key(x[0]), L1.lex_key(x[1]))

    def neg(self, x):
        L1 = self.L1
        return (L1.neg(x[0]), L1.neg(x[1]))

    def sqrt_of_level1_nonsquare(self, a, reverse: bool = False):
        """Square root, in level 2, of a level-1 element `a` that is a
        non-square in level 1 (generalising fp_common.Fp4.sqrt_of_fp2_nonsquare)."""
        L1 = self.L1
        e_inv = L1.pow(self.e, self.q1 - 2)
        a_over_e = L1.mul(a, e_inv)
        y = L1.sqrt(a_over_e, reverse=reverse)
        if y is None:
            raise ValueError("sqrt_of_level1_nonsquare: a/e unexpectedly not a level-1 square (bug)")
        return (L1.zero(), y)
