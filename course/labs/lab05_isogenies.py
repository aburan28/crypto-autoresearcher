#!/usr/bin/env python3
"""
Lab 05 — Isogenies and Velu's formulas.

Companion to course module 09. Run directly:

    python3 lab05_isogenies.py

An isogeny is a nonconstant algebraic map E -> E' sending O to O; it is
automatically a group homomorphism, and a separable isogeny is determined
(up to isomorphism of the target) by its kernel, a finite subgroup.
Velu (1971) turned that abstract fact into explicit formulas: given the
kernel points, write down E' and the rational map.

This lab implements Velu for a cyclic kernel <T> of order 2 or odd L, in
the "normalized" form where the y-coordinate map is y * X'(x) — the
invariant-differential trick explained in module 09:

  for each kernel x-coordinate x_Q (one representative per pair {Q, -Q}):
      g_Q = 3 x_Q^2 + a,   u_Q = (2 y_Q)^2
      t_Q = g_Q            if Q has order 2 (y_Q = 0)
            2 g_Q          otherwise
  t = sum t_Q,   w = sum (u_Q + x_Q t_Q)
  E' : y^2 = x^3 + (a - 5t) x + (b - 7w)
  X(x) = x + sum [ t_Q/(x - x_Q) + u_Q/(x - x_Q)^2 ]
  Y(x,y) = y * X'(x)

Everything is verified numerically: image points land on E', the map is a
homomorphism, the kernel maps to O, and composing a 2-isogeny with its
dual gives multiplication by 2.
"""

from __future__ import annotations

import random

from lab02_finite_fields import Fp, Fp2
from lab03_elliptic_curves import (EllipticCurve, Point, count_points_Fp,
                                   point_order)


class Isogeny:
    """A separable isogeny E -> E' with cyclic kernel <T>, via Velu."""

    def __init__(self, E: EllipticCurve, T: Point, order: int):
        """T must be a point of exact order `order` (2 or an odd prime
        power works; any odd order is accepted)."""
        if T.is_zero() or not (order * T).is_zero():
            raise ValueError("T must have the stated finite order")
        if order != 2 and order % 2 == 0:
            raise ValueError("kernel order must be 2 or odd (compose steps "
                             "for other degrees)")
        self.domain = E
        self.degree = order

        # Full kernel x-coordinate set (for detecting kernel inputs) and
        # one representative per {Q, -Q} pair for the sums.
        kernel = []
        Q = T
        while not Q.is_zero():
            kernel.append(Q)
            Q = Q + T
        self.kernel_x = {Q.x for Q in kernel}
        reps = kernel[: (order - 1) // 2] if order != 2 else [T]

        a, b = E.a, E.b
        t = a.zero()
        w = a.zero()
        self._terms = []  # (x_Q, t_Q, u_Q) for the rational map
        for Q in reps:
            g = Q.x * Q.x * 3 + a
            u = (Q.y * 2) ** 2
            tQ = g if Q.y.is_zero() else g * 2
            t = t + tQ
            w = w + u + Q.x * tQ
            self._terms.append((Q.x, tQ, u))
        self.codomain = EllipticCurve(a - t * 5, b - w * 7)

    def __call__(self, P: Point) -> Point:
        if P.curve != self.domain:
            raise ValueError("point not on the domain curve")
        if P.is_zero() or P.x in self.kernel_x:
            return self.codomain.zero()
        X = P.x
        dX = P.x.one()
        for xQ, tQ, uQ in self._terms:
            inv = (P.x - xQ).inverse()
            inv2 = inv * inv
            X = X + tQ * inv + uQ * inv2
            dX = dX - tQ * inv2 - uQ * 2 * inv2 * inv
        return Point(self.codomain, X, P.y * dX)

    def __repr__(self):
        return (f"Isogeny of degree {self.degree}: j={self.domain.j_invariant()}"
                f" -> j={self.codomain.j_invariant()}")


def two_isogenies(E: EllipticCurve) -> list[Isogeny]:
    """All 2-isogenies from E defined over the base field: one per
    rational 2-torsion point, i.e. per root of x^3 + a x + b."""
    isos = []
    p = E.a.p
    # Only used over F_p in this lab (lab 06 finds roots over F_{p^2}).
    for x in range(p):
        xe = Fp(p, x)
        if (xe ** 3 + E.a * xe + E.b).is_zero():
            T = Point(E, xe, xe.zero())
            isos.append(Isogeny(E, T, 2))
    return isos


def torsion_point(E: EllipticCurve, n_curve: int, L: int,
                  rng: random.Random) -> Point:
    """A point of exact order L. Compute a random point's exact order o
    and return (o/L)*P when L | o. (The naive "cofactor trick"
    (#E/L)*P silently fails on non-cyclic groups whose exponent divides
    #E/L — computing the exact order first is always safe.)"""
    if n_curve % L != 0:
        raise ValueError(f"{L} does not divide #E = {n_curve}")
    while True:
        P = E.random_point(rng)
        o = point_order(P, n_curve)
        if o % L == 0:
            return (o // L) * P


# ----------------------------------------------------------------------
# Self-checks and demo
# ----------------------------------------------------------------------

def _check_isogeny(phi: Isogeny, rng: random.Random, samples: int = 30):
    E, E2 = phi.domain, phi.codomain
    for _ in range(samples):
        P = E.random_point(rng)
        Q = E.random_point(rng)
        assert E2.contains(phi(P)), "image point off the codomain"
        assert phi(P + Q) == phi(P) + phi(Q), "not a homomorphism"
        assert phi(-P) == -phi(P)


def _selfcheck() -> None:
    rng = random.Random(7)

    # ---- 2-isogeny over F_p with full rational 2-torsion ----
    # y^2 = x(x-1)(x+2) = x^3 + x^2 - 2x is not short Weierstrass; instead
    # pick p and search for a curve with three rational 2-torsion points.
    p = 431
    E = None
    for bval in range(1, p):
        try:
            cand = EllipticCurve(Fp(p, p - 4), Fp(p, bval))  # a = -4, vary b
        except ValueError:
            continue
        if len([x for x in range(p)
                if (Fp(p, x) ** 3 + cand.a * Fp(p, x) + cand.b).is_zero()]) == 3:
            E = cand
            break
    assert E is not None
    isos = two_isogenies(E)
    assert len(isos) == 3
    for phi in isos:
        assert phi.codomain.discriminant().is_zero() is False
        _check_isogeny(phi, rng)
        # kernel maps to O
        for xk in phi.kernel_x:
            T = Point(E, xk, xk.zero())
            assert phi(T).is_zero()

    # Dual: some 2-isogeny psi from E' has psi . phi = iota . [2] where
    # iota: E -> psi.codomain is an isomorphism (x, y) -> (u^2 x, u^3 y).
    # Velu's normalized formulas never return to the exact starting model,
    # only to an isomorphic one, so we must recover u^2 from the curve
    # coefficients (a'' = u^4 a, b'' = u^6 b => u^2 = (b''/b)/(a''/a))
    # and compare x-coordinates through it.
    phi = isos[0]
    found_dual = False
    E2 = phi.codomain
    for x in range(p):
        xe = Fp(p, x)
        if not (xe ** 3 + E2.a * xe + E2.b).is_zero():
            continue
        psi = Isogeny(E2, Point(E2, xe, xe.zero()), 2)
        E3 = psi.codomain
        if E3.j_invariant() != E.j_invariant():
            continue  # cyclic 4-isogeny, not the dual
        u4, u6 = E3.a / E.a, E3.b / E.b
        if u4 ** 3 != u6 ** 2:
            continue
        u2 = u6 / u4                      # the unique u^2 with iota as above
        ok = True
        for _ in range(10):
            P = E.random_point(rng)
            R, D = psi(phi(P)), 2 * P
            if R.is_zero() != D.is_zero() or \
                    (not R.is_zero() and R.x != u2 * D.x):
                ok = False
                break
        if ok:
            found_dual = True
            break
    assert found_dual, "no dual 2-isogeny found"

    # ---- odd-degree isogeny over F_p ----
    # Find a small curve with 3-torsion and 5-torsion to exercise L > 2.
    for L in (3, 5, 7):
        found = False
        for p2 in (431, 1013, 2003):
            for bval in range(1, 40):
                try:
                    E3 = EllipticCurve(Fp(p2, 1), Fp(p2, bval))
                except ValueError:
                    continue
                N = count_points_Fp(E3)
                if N % L == 0:
                    T = torsion_point(E3, N, L, rng)
                    phi = Isogeny(E3, T, L)
                    _check_isogeny(phi, rng)
                    assert phi(T).is_zero()
                    # isogenous curves over F_p have the same point count
                    assert count_points_Fp(phi.codomain) == N
                    found = True
                    break
            if found:
                break
        assert found, f"no curve with {L}-torsion found"

    # ---- 2-isogeny over F_{p^2} (the setting of lab 06) ----
    p = 23
    one = Fp2(p, 1)
    Ess = EllipticCurve(one, one.zero())          # y^2 = x^3 + x, j = 1728
    # 2-torsion x-coords are roots of x^3 + x = x(x-i)(x+i) with i^2 = -1.
    for xk in (one.zero(), Fp2(p, 0, 1), Fp2(p, 0, p - 1)):
        T = Point(Ess, xk, xk.zero())
        phi = Isogeny(Ess, T, 2)
        _check_isogeny(phi, rng, samples=15)
    print("lab05: all self-checks passed")


def _demo() -> None:
    rng = random.Random(8)
    p = 431
    print(f"\n-- demo: isogenies of degree 2, 3, 5 over F_{p} --")
    for L in (2, 3, 5):
        # find a curve whose group order is divisible by L
        for bval in range(1, p):
            try:
                E = EllipticCurve(Fp(p, 1), Fp(p, bval))
            except ValueError:
                continue
            N = count_points_Fp(E)
            if N % L == 0:
                break
        phi = Isogeny(E, torsion_point(E, N, L, rng), L)
        print(f"E: y^2 = x^3 + x + {bval}  (#E = {N}):  {phi}")
        P = E.random_point(rng)
        print(f"   sample: phi({P}) = {phi(P)}")
    # EXERCISE 5.1: show deg(phi_2 . phi_3) = 6 by composing a 2- and a
    #   3-isogeny and counting the kernel of the composite on a curve with
    #   6 | #E.
    # EXERCISE 5.2: verify that the number of points of E' equals that of E
    #   for every isogeny you can build here (Tate's isogeny theorem).
    # EXERCISE 5.3 (harder): implement the dual of an odd-degree isogeny by
    #   finding the kernel of psi with psi . phi = [L] via phi(E[L]).


if __name__ == "__main__":
    _selfcheck()
    _demo()
