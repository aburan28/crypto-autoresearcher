#!/usr/bin/env python3
"""Independent re-derivation of the decomposition counts, before any cell runs.

WHY THIS FILE IS THE LOAD-BEARING ONE. `yield_core.py` computes every number in
EXP-SEMBIN-354a75 through one clever identification: that the y-values outside
F_q are the F_q-points of the quadratic twist, so the whole count can be taken
in F_q arithmetic on two curves. If that identification or its bookkeeping is
wrong, the error is a systematic multiplicative bias on the yield -- which is
indistinguishable from the quantity the experiment exists to measure. So the
counts are re-derived here by routes that share no code with it:

  ROUTE A  Brute force in F_{q^2}. Build the flat factor base -- every point of
           E(F_{q^2}) with x in V -- enumerate every t-multiset of it, add the
           points with binary_field's slow verified group law over
           F_q[u]/(u^2+u+delta), and test the sum against -R directly. No
           twist, no log tables, no numpy, and no case analysis: the count is
           one pass of combinations_with_replacement whose length is asserted
           to be C(P+t-1, t).
  ROUTE B  The paper's printed polynomial. For t = 2 the single presentation is
           literally S_3(x_1, x_2, R_X) = 0 with
           S_3 = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B, so the count is a
           polynomial evaluation and involves no group law at all.
  ROUTE C  Root sets of the chain equations. For t = 3 the chain is one
           auxiliary variable: S_3(u, x_1, x_2) = 0 = S_3(u, x_3, R_X). Solving
           both quadratics in u and intersecting their root sets gives the
           CHAINED count when the intersection is taken in F_q and the SINGLE
           count when it is taken in F_{q^2}. That is Lemma 2's conditional
           equivalence as an executable statement, and it tests the chain walk
           and the single count at once.
  ROUTE D  The inherited t!-permutation chain search against the subset-lattice
           rewrite that replaced it.
  ROUTE E  The histogram enumeration (one pass over all C(L+t-1, t) multisets)
           against the per-R lookup path, which are two different algorithms
           for the usable-relation count.
  ROUTE F  The Lemma-2 instrument: the side condition against the brute
           force's own lower-i counts, s = 1 never occurring, and -- where the
           side condition holds -- H equal to the 2-torsion point and chained
           equal to single. This is the one route that checks the counter
           against the PAPER rather than against another enumeration.

Exit status 0 on success, 1 on the first disagreement, with the case printed.
Nothing here writes into the run directory.
"""
from __future__ import annotations

import itertools
import random
import sys
from math import comb, factorial

import numpy as np

from binary_field import BinaryCurve, GF2m, QuadraticExtension, INFINITY
from fastfield import FastCurve, FastField, twist_a
from yield_core import (CellContext, build_subspace, count_multiset_sums,
                        ordered_orbit, span_of, validate_subspace,
                        validate_target)

U32 = np.uint32


def check(name: str, ok: bool) -> None:
    if not ok:
        print(f"FAIL: {name}")
        raise SystemExit(1)
    print(f"ok: {name}")


# --------------------------------------------------------------------------
# ROUTE A: brute force in F_{q^2}
# --------------------------------------------------------------------------
class BruteForce:
    """Every count of interest, computed in F_{q^2} with the slow arithmetic."""

    def __init__(self, n: int, a: int, b: int, V: list[int]) -> None:
        self.f = GF2m(n)
        self.ext = QuadraticExtension(self.f)
        self.a, self.b, self.V = a, b, V
        self.curve = BinaryCurve(self.ext, self.ext.embed(a), self.ext.embed(b))
        self.lifts = {x: self._lifts(x) for x in V}
        # The flat factor base: every point of E(F_{q^2}) whose x lies in V,
        # with its x and whether its y is F_q-rational. Enumerating multisets
        # of THIS list is what makes the brute force exhaustive with no
        # bookkeeping: a decomposition is a t-multiset of factor-base points,
        # so it is one entry of combinations_with_replacement, counted once.
        # (Enumerating x-multisets and then lifting each coordinate
        # independently is NOT the same count -- it orders the lifts inside a
        # group of equal x, which double-counts every decomposition that uses
        # both lifts of one x. That error is why this list exists.)
        self.points = [(p, rat, x) for x in V for p, rat in self.lifts[x]]

    def _lifts(self, x: int):
        """Both points of E(F_{q^2}) over x, with a flag for y in F_q."""
        f, ext = self.f, self.ext
        if x == 0:
            y = f.sqrt(self.b)
            return [((ext.embed(0), ext.embed(y)), True)]
        c = f.add(f.add(x, self.a), f.div(self.b, f.sqr(x)))
        out = []
        for z in ext.solve_quadratic_over_base(c):
            y = ext.mul(ext.embed(x), z)
            p = (ext.embed(x), y)
            assert self.curve.is_on_curve(p), "brute-force lift left the curve"
            out.append((p, ext.in_base(y)))
        return out

    def embed_point(self, R, side: str):
        """A target on E (side E) or on the twist (side T) as a point of E(F_{q^2})."""
        ext = self.ext
        x, y = R
        if side == "E":
            return (ext.embed(x), ext.embed(y))
        # psi(x, y) = (x, y + x u): the twist isomorphism into E(F_{q^2}).
        img = (ext.embed(x), ext.add(ext.embed(y), ext.mul(ext.embed(x), (0, 1))))
        assert self.curve.is_on_curve(img), "psi(twist point) left the curve"
        return img

    def summarise(self, R, t: int, side: str = "E") -> dict:
        target = self.curve.negate(self.embed_point(R, side))
        x_multisets, chained, with_rat, with_out = set(), set(), set(), set()
        usable_pm = outside_pm = 0
        max_s = 0
        visited = 0
        s_counts: dict[int, int] = {}
        tau_counts = {"O": 0, "T2": 0}
        t2_ext = (self.ext.embed(0), self.ext.embed(self.f.sqrt(self.b)))
        for combo in itertools.combinations_with_replacement(self.points, t):
            visited += 1
            total = INFINITY
            for p, _rat, _x in combo:
                total = self.curve.add(total, p)
            if total != target:
                continue
            xs = tuple(sorted(x for _p, _rat, x in combo))
            s = sum(1 for _p, rat, _x in combo if not rat)
            x_multisets.add(xs)
            s_counts[s] = s_counts.get(s, 0) + 1
            if s == 0:
                usable_pm += 1
                with_rat.add(xs)
            else:
                outside_pm += 1
                with_out.add(xs)
                max_s = max(max_s, s)
                # tau: the sum of the points on the side OPPOSITE the target.
                # For a target in E(F_q) this is Lemma 2's H, the sum of the
                # points with y outside F_q, and the lemma says it has order
                # exactly 2. For a target on the twist the roles swap -- the
                # proof's step "H = -R - G in E(F_q)" needs R in E(F_q) -- and
                # it is the RATIONAL part that must collapse to {O, T2}.
                # Either way it is computed here from the points themselves,
                # with no twist bookkeeping.
                opposite = INFINITY
                for p, rat, _x in combo:
                    if rat == (side == "T"):
                        opposite = self.curve.add(opposite, p)
                if opposite is INFINITY:
                    tau_counts["O"] += 1
                elif opposite == t2_ext:
                    tau_counts["T2"] += 1
                else:
                    check(f"the side-opposite sum {opposite} is neither "
                          f"infinity nor the 2-torsion point, so the "
                          f"decomposition could not have closed", False)
            if xs not in chained and self._chain(combo, t):
                chained.add(xs)
        assert visited == comb(len(self.points) + t - 1, t), (
            f"brute force visited {visited} multisets, expected "
            f"{comb(len(self.points) + t - 1, t)}")
        return {
            "point_multiset_total": usable_pm + outside_pm,
            "usable_point_multiset": usable_pm,
            "outside_fq_point_multiset": outside_pm,
            "max_y_outside_fq": max_s,
            "s_counts": {str(s): c for s, c in sorted(s_counts.items())},
            "tau_counts_for_s_positive": dict(tau_counts),
            "single_x_multiset": len(x_multisets),
            "chained_x_multiset": len(chained),
            "single_x_ordered": sum(ordered_orbit(x, t) for x in x_multisets),
            "chained_x_ordered": sum(ordered_orbit(x, t) for x in chained),
            "x_multiset_outside_only": len(with_out - with_rat),
            "x_multiset_both_kinds": len(with_out & with_rat),
        }

    def _chain(self, combo, t: int) -> bool:
        """Chain condition read straight off its definition, in F_{q^2}.

        u_1..u_{t-2} are the x-coordinates of the running partial sums, they
        live in F_q, and a partial sum of infinity has no x-coordinate at all.
        """
        if t <= 2:
            return True
        for order in itertools.permutations(range(t)):
            total, ok = INFINITY, True
            for pos, i in enumerate(order):
                total = self.curve.add(total, combo[i][0])
                step = pos + 1
                if 2 <= step <= t - 1:
                    if total is INFINITY or not self.ext.in_base(total[0]):
                        ok = False
                        break
            if ok:
                return True
        return False


# --------------------------------------------------------------------------
# ROUTE B: the printed summation polynomial S_3
# --------------------------------------------------------------------------
def s3(f: GF2m, b: int, x1: int, x2: int, x3: int) -> int:
    """(x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B, the paper's Section 2 formula."""
    e2 = f.add(f.add(f.mul(x1, x2), f.mul(x1, x3)), f.mul(x2, x3))
    return f.add(f.add(f.sqr(e2), f.mul(f.mul(x1, x2), x3)), b)


def s3_count(f: GF2m, b: int, V: list[int], z: int) -> tuple[int, int]:
    """(x-multisets, ordered tuples) in V^2 with S_3(x1, x2, z) = 0."""
    cls = [xs for xs in itertools.combinations_with_replacement(V, 2)
           if s3(f, b, xs[0], xs[1], z) == 0]
    return len(cls), sum(ordered_orbit(xs, 2) for xs in cls)


# --------------------------------------------------------------------------
# ROUTE C: root sets of the chain equations, for t = 3
# --------------------------------------------------------------------------
def s3_roots(f: GF2m, ext: QuadraticExtension, b: int, x1: int, x2: int):
    """Roots in u of S_3(u, x1, x2) = 0, split by whether they lie in F_q.

    S_3(u, x1, x2) = u^2 (x1+x2)^2 + u x1x2 + ((x1x2)^2 + B), read off the
    printed polynomial. Returns (roots in F_q, roots in F_{q^2} as pairs).
    """
    lead = f.sqr(f.add(x1, x2))
    mid = f.mul(x1, x2)
    const = f.add(f.sqr(mid), b)
    if lead == 0:                       # x1 == x2: the equation is linear in u
        if mid == 0:                    # x1 == x2 == 0: constant B != 0
            return [], []
        return [f.div(const, mid)], []
    beta = f.div(mid, lead)
    gamma = f.div(const, lead)
    if beta == 0:                       # u^2 = gamma, one root, always in F_q
        return [f.sqrt(gamma)], []
    c = f.div(gamma, f.sqr(beta))       # u = beta w, w^2 + w = c
    if f.trace(c) == 0:
        w = f.solve_quadratic(c)
        return [f.mul(beta, w), f.mul(beta, f.add(w, 1))], []
    roots = [ext.mul(ext.embed(beta), w)
             for w in ext.solve_quadratic_over_base(c)]
    return [], roots


def route_c(f: GF2m, ext: QuadraticExtension, b: int, V: list[int], z: int):
    """(single, chained) x-multiset counts at t = 3 by intersecting root sets."""
    single, chained = set(), set()
    for xs in itertools.combinations_with_replacement(V, 3):
        hit_single = hit_chain = False
        for pick in range(3):
            rest = [xs[i] for i in range(3) if i != pick]
            base_q, base_e = s3_roots(f, ext, b, rest[0], rest[1])
            tail_q, tail_e = s3_roots(f, ext, b, xs[pick], z)
            if set(base_q) & set(tail_q):
                hit_chain = hit_single = True
                break
            if set(base_e) & set(tail_e):
                hit_single = True
        if hit_single:
            single.add(xs)
        if hit_chain:
            chained.add(xs)
    return len(single), len(chained)


# --------------------------------------------------------------------------
# Target drawing shared with the driver's convention
# --------------------------------------------------------------------------
def draw_targets(ctx: CellContext, side: str, count: int, rng: random.Random):
    """Uniform affine points of the chosen curve whose x lies outside V."""
    pts = ctx.e_pts if side == "E" else ctx.t_pts
    curve = ctx.curve if side == "E" else ctx.twist
    out, Vset = [], set(ctx.V)
    field = ctx.field
    while len(out) < count:
        x = rng.randrange(1, field.q)
        if x in Vset:
            continue
        ys = curve.ys_for_x_scalar(x)
        if not ys:
            continue
        out.append((x, ys[rng.randrange(len(ys))]))
    return out


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------
def route_a_agreement(n: int, k: int, t: int, b: int, rng: random.Random,
                      targets: int = 6) -> None:
    V, _basis = build_subspace(FastField.get(n), k, "low_degree_polynomial",
                              np.random.default_rng(1))
    ctx = CellContext(n, 0, b, V)
    bf = BruteForce(n, 0, b, V)
    for side in ("E", "T"):
        if (side == "T" and ctx.t_pts.n == 0) or (side == "E" and ctx.e_pts.n == 0):
            continue
        for R in draw_targets(ctx, side, targets, rng):
            fast = ctx.solve_for_target(R, t, side=side)
            slow = bf.summarise(R, t, side=side)
            if fast != slow:
                print(f"  n={n} k={k} t={t} b={b} side={side} R={R}")
                print(f"  fast={fast}")
                print(f"  slow={slow}")
                check("route A agreement", False)
    check(f"n={n} k={k} t={t} b={b}: every count agrees with brute force in "
          f"F_(q^2) on {targets} targets per side (both presentations, the "
          f"Lemma-2 split and both granularities)", True)


def route_b_agreement(n: int, k: int, b: int, rng: random.Random,
                      targets: int = 8, variant: str = "low_degree_polynomial") -> None:
    ff = FastField.get(n)
    sf = GF2m(n)
    V, _basis = build_subspace(ff, k, variant, np.random.default_rng(7))
    ctx = CellContext(n, 0, b, V)
    for side in ("E", "T"):
        for R in draw_targets(ctx, side, targets, rng):
            got = ctx.solve_for_target(R, 2, side=side)
            cls, ordered = s3_count(sf, b, V, R[0])
            if (cls, ordered) != (got["single_x_multiset"], got["single_x_ordered"]):
                print(f"  n={n} k={k} b={b} side={side} R={R}: "
                      f"S_3 says {(cls, ordered)}, counter says "
                      f"{(got['single_x_multiset'], got['single_x_ordered'])}")
                check("route B agreement", False)
            if got["chained_x_multiset"] != got["single_x_multiset"]:
                check("t=2 chained must equal single (one equation, no u_i)",
                      False)
    check(f"n={n} k={k} b={b} V={variant}: t=2 single count equals the zero "
          f"count of the PRINTED S_3 on {targets} targets per side, and "
          f"chained = single at t = 2 as the paper states", True)


def route_c_agreement(n: int, k: int, b: int, rng: random.Random,
                      targets: int = 4) -> None:
    sf = GF2m(n)
    ext = QuadraticExtension(sf)
    V, _basis = build_subspace(FastField.get(n), k, "low_degree_polynomial",
                               np.random.default_rng(3))
    ctx = CellContext(n, 0, b, V)
    for side in ("E", "T"):
        for R in draw_targets(ctx, side, targets, rng):
            got = ctx.solve_for_target(R, 3, side=side)
            single, chained = route_c(sf, ext, b, V, R[0])
            if (single, chained) != (got["single_x_multiset"],
                                     got["chained_x_multiset"]):
                print(f"  n={n} k={k} b={b} side={side} R={R}: roots say "
                      f"{(single, chained)}, counter says "
                      f"{(got['single_x_multiset'], got['chained_x_multiset'])}")
                check("route C agreement", False)
    check(f"n={n} k={k} b={b}: at t=3 both presentations agree with the "
          f"F_q-versus-F_(q^2) root-set intersection of the chain equations "
          f"on {targets} targets per side", True)


def route_d_agreement(n: int, k: int, t: int, b: int, rng: random.Random,
                      targets: int = 10) -> None:
    V, _basis = build_subspace(FastField.get(n), k, "low_degree_polynomial",
                               np.random.default_rng(5))
    ctx = CellContext(n, 0, b, V)
    compared = 0
    for side in ("E", "T"):
        for R in draw_targets(ctx, side, targets, rng):
            validate_target(R)
            if side == "E":
                side_pts, other_pts = ctx.e_pts, ctx.t_pts
                scalar, other_tag, sk, ok_ = ctx.scalar_e, "T", "E", "T"
            else:
                side_pts, other_pts = ctx.t_pts, ctx.e_pts
                scalar, other_tag, sk, ok_ = ctx.scalar_t, "E", "T", "E"
            minus_r = scalar.neg(R)
            for j, rows in ctx.torsion_parts(other_pts, t, other_tag).items():
                for tau_name in ("O", "T2"):
                    other_rows = [tw for nm, tw in rows if nm == tau_name]
                    if not other_rows:
                        continue
                    tgt = (minus_r if tau_name == "O"
                           else scalar.add(minus_r, ctx.t2))
                    for srow in side_pts.solutions(t - j, tgt):
                        base = [(sk, int(v)) for v in srow]
                        for other in other_rows:
                            items = base + [(ok_, int(v)) for v in other]
                            a = ctx.chain_satisfiable(items, t)
                            c = ctx.chain_satisfiable_permutations(items, t)
                            if a != c:
                                print(f"  items={items} lattice={a} perms={c}")
                                check("route D agreement", False)
                            compared += 1
    check(f"n={n} k={k} t={t}: subset-lattice chain search agrees with the "
          f"t!-permutation search on {compared} witnesses", True)


def route_d_random(n: int, k: int, t: int, b: int, rng: random.Random,
                   trials: int = 4000) -> None:
    """The same two chain searches on RANDOM item lists, not only on solutions.

    Solution witnesses are scarce -- a whole cell can yield three -- so agreeing
    on them says little about a rewrite that changed the search from t!
    orderings to 2^t subsets. Random item lists exercise the branch that
    matters: mixed E/twist multisets whose partial sums hit infinity and the
    2-torsion point far more often than a solution set does.
    """
    V, _basis = build_subspace(FastField.get(n), k, "low_degree_polynomial",
                               np.random.default_rng(13))
    ctx = CellContext(n, 0, b, V)
    pool = ([("E", i) for i in range(ctx.e_pts.n)]
            + [("T", i) for i in range(ctx.t_pts.n)])
    if not pool:
        return
    agree = sat = 0
    for _ in range(trials):
        items = [pool[rng.randrange(len(pool))] for _ in range(t)]
        a = ctx.chain_satisfiable(items, t)
        c = ctx.chain_satisfiable_permutations(items, t)
        if a != c:
            print(f"  items={items} lattice={a} perms={c}")
            check("route D random agreement", False)
        agree += 1
        sat += int(a)
    check(f"n={n} k={k} t={t}: the two chain searches agree on {agree} random "
          f"item lists ({sat} satisfiable, {agree - sat} not), so the "
          f"subset-lattice rewrite is exercised on both branches",
          0 < sat < agree)


def route_e_agreement(n: int, k: int, t: int, b: int, rng: random.Random,
                      targets: int = 40) -> None:
    """Histogram enumeration against the per-R lookup, and order independence."""
    V, _basis = build_subspace(FastField.get(n), k, "low_degree_polynomial",
                               np.random.default_rng(11))
    ctx = CellContext(n, 0, b, V)
    Rs = draw_targets(ctx, "E", targets, rng)
    per_r = np.array([ctx.solve_for_target(R, t)["usable_point_multiset"]
                      for R in Rs], dtype=np.int64)
    keys = ctx.curve.key(
        np.array([R[0] for R in Rs], dtype=U32),
        np.array([R[1] ^ R[0] for R in Rs], dtype=U32),   # -R
        np.zeros(len(Rs), dtype=bool))
    hist, states = count_multiset_sums(ctx.curve, ctx.e_pts.X, ctx.e_pts.Y, t,
                                       keys, state_cap=400_000)
    check(f"n={n} k={k} t={t}: histogram visited all C(L+t-1,t) = "
          f"{comb(ctx.e_pts.n + t - 1, t)} multisets",
          states == comb(ctx.e_pts.n + t - 1, t))
    if not np.array_equal(hist, per_r):
        print(f"  histogram={hist[:12]} per_r={per_r[:12]}")
        check("route E agreement", False)
    perm = np.random.default_rng(99).permutation(ctx.e_pts.n)
    hist2, _s = count_multiset_sums(ctx.curve, ctx.e_pts.X, ctx.e_pts.Y, t,
                                    keys, perm=perm, state_cap=400_000)
    check(f"n={n} k={k} t={t}: per-R usable-relation counts agree between the "
          f"histogram and the lookup path, and are unchanged under a permuted "
          f"enumeration order", bool(np.array_equal(hist, hist2)))


def route_f_lemma2(n: int, k: int, t: int, b: int, rng: random.Random,
                   targets: int = 12) -> None:
    """The Lemma-2 instrument: side condition, s = 0 or s >= 2, and ord(H) = 2.

    Checks three separate things, because they fail separately:
      - `lemma2_side_condition` agrees with the brute force's own lower-i
        single counts;
      - s = 1 never occurs (Lemma 2 part 1's conclusion);
      - where the side condition HOLDS, every s > 0 solution has H = T2 and
        none has H = infinity, which is the sharp form of part 1. Where it
        FAILS the lemma predicts nothing, so H = infinity is allowed and is
        counted rather than treated as an error.
    """
    V, _basis = build_subspace(FastField.get(n), k, "low_degree_polynomial",
                               np.random.default_rng(17))
    ctx = CellContext(n, 0, b, V)
    bf = BruteForce(n, 0, b, V)
    held = failed = s_pos = 0
    for side in ("E", "T"):
        for R in draw_targets(ctx, side, targets, rng):
            cond = ctx.lemma2_side_condition(R, t, side=side)
            for i in range(2, t):
                want = bf.summarise(R, i, side=side)["single_x_multiset"]
                if cond["lower_i_single_counts"][str(i)] != want:
                    check(f"side condition at i={i}: core says "
                          f"{cond['lower_i_single_counts'][str(i)]}, brute "
                          f"force says {want}", False)
            got = ctx.solve_for_target(R, t, side=side)
            if "1" in got["s_counts"]:
                check(f"s = 1 occurred at R={R}, contradicting Lemma 2 part 1",
                      False)
            s_pos += sum(c for s, c in got["s_counts"].items() if int(s) > 0)
            if side == "T":
                # Lemma 2's proof needs R in E(F_q): H = -R - G is in E(F_q)
                # only then. On the twist side the lower-i counts are still
                # checked above, but parts 1 and 2 are simply not in scope.
                continue
            if cond["holds"]:
                held += 1
                if got["tau_counts_for_s_positive"]["O"] != 0:
                    check(f"side condition holds at R={R} but H = infinity "
                          f"occurred, contradicting Lemma 2 part 1", False)
                if got["chained_x_multiset"] != got["single_x_multiset"]:
                    check(f"side condition holds at R={R} but chained "
                          f"{got['chained_x_multiset']} != single "
                          f"{got['single_x_multiset']}, contradicting Lemma 2 "
                          f"part 2", False)
            else:
                failed += 1
    check(f"n={n} k={k} t={t} b={b}: Lemma 2 verified on {held} targets where "
          f"the side condition holds and {failed} where it fails -- lower-i "
          f"counts match brute force, s = 1 never occurs ({s_pos} solutions "
          f"with s > 0 seen), and where it holds chained = single and H = T2",
          True)


def orbit_and_guard_checks() -> None:
    for t in (2, 3, 4, 6):
        for xs in itertools.combinations_with_replacement(range(3), t):
            want = len(set(itertools.permutations(xs)))
            if ordered_orbit(tuple(sorted(xs)), t) != want:
                check(f"ordered_orbit wrong at {xs}", False)
    check("ordered_orbit equals the number of distinct permutations for every "
          "multiset over 3 symbols at t in {2,3,4,6}", True)
    try:
        validate_target(None)
    except ValueError:
        pass
    else:
        check("R = infinity must be rejected", False)
    bad = [0, 1, 2, 4]                     # closed under nothing: 1^2 = 3 absent
    try:
        validate_subspace(bad, 2)
    except ValueError:
        pass
    else:
        check("a V that is not F_2-closed must be rejected", False)
    validate_subspace(span_of([1, 2]), 2)
    check("invalid_input control: R = infinity and a non-subspace V are both "
          "rejected, and a genuine subspace is accepted", True)


def main() -> int:
    rng = random.Random(20260913203)
    orbit_and_guard_checks()
    # Brute force in F_{q^2} on small instances, both b values, t = 2..4,
    # plus the contract's own smallest cell shape (k = 2, t = 6).
    for (n, k, t) in ((9, 2, 2), (9, 2, 3), (10, 3, 2), (10, 3, 3),
                      (11, 2, 4), (12, 2, 6)):
        for b in (1, 5):
            route_a_agreement(n, k, t, b, rng)
    for (n, k) in ((12, 2), (13, 4), (15, 3), (17, 6)):
        for b in (1, 11):
            route_b_agreement(n, k, b, rng)
    route_b_agreement(17, 6, 1, rng, variant="random_k_dimensional")
    for (n, k) in ((12, 2), (15, 3), (17, 6)):
        route_c_agreement(n, k, 1, rng)
    route_c_agreement(15, 3, 7, rng)
    for (n, k, t) in ((11, 3, 3), (12, 2, 6), (13, 4, 4)):
        route_d_agreement(n, k, t, 1, rng, targets=4)
    for (n, k, t) in ((12, 2, 3), (12, 2, 6), (13, 4, 4), (17, 6, 3)):
        route_d_random(n, k, t, 1, rng)
    for (n, k, t) in ((13, 4, 4), (15, 3, 3), (17, 6, 3), (12, 2, 6)):
        route_e_agreement(n, k, t, 1, rng)
    for (n, k, t) in ((9, 2, 3), (10, 3, 3), (11, 2, 4), (12, 2, 6)):
        for b in (1, 5):
            route_f_lemma2(n, k, t, b, rng)
    print("\nALL YIELD-CORE CROSS-CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
