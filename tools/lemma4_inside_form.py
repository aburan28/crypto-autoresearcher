"""Standing refutation of the INSIDE form of Nagao 2015/984's Lemma 4.

WHY THIS LIVES IN tools/ AND NOT IN A TASK DIRECTORY
----------------------------------------------------
`EXP-SEMBIN-4fa22c` records `d_F <= d'_F` -- Lemma 4 -- as a DEPENDENCY of its
central inference, and the run's own S-1 protection is phrased in terms of it.
The inequality is false. A refutation that load-bearing must be re-runnable by
any later reader without depending on a session, a task directory, or an
archive, so it is checked in beside the tools and pinned by
`tools/test_lemma4_inside_form.py`.

WHAT IS CLAIMED, AND AT WHAT TIER
---------------------------------
Claimed: the universally quantified statement `d_F(F u S_fe) <= d'_F(F u S_fe)`
is FALSE over `F_2`, with an explicit three-variable witness, and it fails on a
substantial fraction of random multilinear pairs at `N = 3`.

NOT claimed: anything about Nagao's Proposition 5, which may well be true by
another route; anything about descended summation-polynomial systems at
`n in [7,12]`, which this does not touch; and anything about the `>=` reading of
2015/984's Definitions 5-6, under which the lemma is true and empty (see
`degenerate_under_ge_reading` below). A counterexample refutes a universally
quantified statement and says nothing about a typical instance.

PROVENANCE OF THE WITNESS
-------------------------
The polynomial pair was first reported by a blind source read of Nagao 2013/549
(`TASK-20260916-9da6e0`) whose artifacts were LOST UNCOMMITTED when the session
holding them ended (`CORR-20260921-942a62`). That report cannot be cited: no
reviewer can read it. What survives is this file -- an independent
implementation written from the definitions, which does not read that reader's
code and which reproduces the witness from scratch. The witness is a pair of
polynomials, and a pair of polynomials needs no provenance to be checkable: run
this file.

CONVENTION
----------
Everything below is under the EQUALITY reading of condition (1), which is what
`experiments/EXP-SEMBIN-4fa22c/specification.yaml` declares and what 2013/549's
own Definition 1 prints. Under the literal `>=` printed in 2015/984 the
quantities degenerate; that is measured here rather than argued.

The ring is `F_2[X_1..X_N]`, NOT the Boolean quotient. That is the whole point:
the field equations are GENERATORS of the system, not relations of the ring.
"""

from __future__ import annotations

import itertools
import random

N_DEFAULT = 3


# --------------------------------------------------------------------------
# Polynomials over F_2 as frozensets of exponent tuples; addition is symmetric
# difference. Small and slow, chosen because it is obviously correct: the whole
# computation is a few thousand set operations.
# --------------------------------------------------------------------------
def deg_mono(m: tuple[int, ...]) -> int:
    return sum(m)


def deg(p) -> int:
    return max((deg_mono(m) for m in p), default=-1)


def poly_add(p, q):
    return frozenset(p) ^ frozenset(q)


def poly_mul_mono(p, m):
    return frozenset(tuple(a + b for a, b in zip(u, m)) for u in p)


def reduce_fe(p):
    """Reduce modulo `S_fe = {X_i^2 - X_i}` over `F_2`: clamp every exponent."""
    out: set = set()
    for m in p:
        out ^= {tuple(min(e, 1) for e in m)}
    return frozenset(out)


def field_equations(n: int = N_DEFAULT):
    """`S_fe = {X_i^2 + X_i}`, as GENERATORS of the system."""
    eqs = []
    for i in range(n):
        sq = tuple(2 if j == i else 0 for j in range(n))
        lin = tuple(1 if j == i else 0 for j in range(n))
        eqs.append(frozenset({sq, lin}))
    return eqs


def monomials_up_to(d: int, n: int = N_DEFAULT, multilinear: bool = False):
    hi = 2 if multilinear else d + 1
    for exps in itertools.product(range(hi), repeat=n):
        if sum(exps) <= d:
            yield exps


def _vectorise(rows):
    monos = sorted({m for r in rows for m in r})
    index = {m: i for i, m in enumerate(monos)}
    vecs = []
    for r in rows:
        v = 0
        for m in r:
            v |= 1 << index[m]
        vecs.append(v)
    return monos, vecs


def _reduce_into(basis: dict[int, int], vec: int) -> int:
    """Reduce `vec` against `basis`, inserting it if it survives. Returns residue."""
    while vec:
        pivot = vec.bit_length() - 1
        if pivot not in basis:
            basis[pivot] = vec
            return 0
        vec ^= basis[pivot]
    return 0


def _in_span(basis: dict[int, int], vec: int) -> bool:
    while vec:
        pivot = vec.bit_length() - 1
        if pivot not in basis:
            return False
        vec ^= basis[pivot]
    return True


def _fall_exists_at(products_at_D, products_below, D: int) -> bool:
    """Does a first fall at exactly degree `D` exist?

    A fall at `D` needs cofactors with (a) every product of degree `<= D`,
    (b) max product degree EXACTLY `D`, (c) sum nonzero, (d) sum of degree `< D`.

    Condition (b) is the one a naive eliminator drops, and dropping it is wrong
    rather than conservative: for `f_1 = f_2 = X_1X_2` over `F_2` in two
    variables every product is `X_1X_2`, so no `D` admits a witness at all and
    the quantity is undefined -- but an eliminator that only looks for a
    low-degree element in the span happily reports a fall at `D = 3`, where
    nothing of degree 3 exists to be the maximum. That mismatch is what the
    enumeration oracle caught.

    Write `A` for the span of the products of degree `< D` and `K` for the
    degree-`< D` part of the span of ALL admissible products. Then a fall at `D`
    exists exactly when `K != {0}` and either

      * `K` is not contained in `A` -- some low-degree element needs a degree-`D`
        product to be expressed at all, so its every representation attains `D`; or
      * some nonempty subset of the degree-`D` products sums into `A` -- then any
        `s` in `K` is `(s + p) + p` with `s + p` in `A` and `p` attaining `D`.
    """
    if not products_at_D:
        return False
    monos, vecs = _vectorise(products_at_D + products_below)
    n_at_D = len(products_at_D)
    at_D, below = vecs[:n_at_D], vecs[n_at_D:]

    low_mask = 0
    for i, m in enumerate(monos):
        if deg_mono(m) < D:
            low_mask |= 1 << i

    # A = span of the low products
    basis_A: dict[int, int] = {}
    for v in below:
        _reduce_into(basis_A, v)

    # K = degree-<D part of span(all products): eliminate the high block first
    basis_high: dict[int, int] = {}
    residues = []
    for v in at_D + below:
        vec = v
        while vec & ~low_mask:
            pivot = (vec & ~low_mask).bit_length() - 1
            if pivot not in basis_high:
                basis_high[pivot] = vec
                vec = 0
                break
            vec ^= basis_high[pivot]
        if vec:
            residues.append(vec)
    if not residues:
        return False

    # K not contained in A?
    for r in residues:
        if not _in_span(basis_A, r):
            return True

    # Otherwise: is some NONEMPTY subset of the degree-D products inside A?
    # Equivalently, are their images in the quotient by A linearly dependent --
    # which includes the case of an image that is zero, i.e. a single product
    # already lying in A. Dependence is a rank comparison.
    combined = dict(basis_A)
    rank_of_images = 0
    for v in at_D:
        before = len(combined)
        _reduce_into(combined, v)
        if len(combined) > before:
            rank_of_images += 1
    return rank_of_images < len(at_D)


def first_fall_degree(gens, fake: bool, n: int = N_DEFAULT, dmax: int = 8):
    """`d_F` when `fake` is false, `d'_F` when it is true.

    `fake=True` takes every degree modulo `S_fe`, which is 2015/984's
    Definition 6. A generator that reduces to zero then contributes nothing,
    which is why the field equations drop out of the fake quantity -- and that
    asymmetry is exactly what the counterexample exploits.
    """
    prep = reduce_fe if fake else (lambda p: p)
    gens = [g for g in (prep(g) for g in gens) if g]
    if not gens:
        return None
    for D in range(1, dmax + 1):
        at_D, below = [], []
        for g in gens:
            for m in monomials_up_to(D, n, multilinear=fake):
                prod = prep(poly_mul_mono(g, m))
                if not prod:
                    continue
                d = deg(prod)
                if d == D:
                    at_D.append(prod)
                elif d < D:
                    below.append(prod)
        if _fall_exists_at(at_D, below, D):
            return D
    return None


# --------------------------------------------------------------------------
# The witness
# --------------------------------------------------------------------------
X1, X2, X3 = (1, 0, 0), (0, 1, 0), (0, 0, 1)
X1X2, X1X3 = (1, 1, 0), (1, 0, 1)

WITNESS_F1 = frozenset({X1X2, X3})   # X_1 X_2 + X_3
WITNESS_F2 = frozenset({X1X3, X2})   # X_1 X_3 + X_2


def witness_system():
    """`{f_1, f_2} u S_fe`, the system the inside form quantifies over."""
    return [WITNESS_F1, WITNESS_F2] + field_equations(3)


def check_witness() -> dict:
    """Verify the refutation. Returns every number a reader would want to see."""
    system = witness_system()
    d_true = first_fall_degree(system, fake=False)
    d_fake = first_fall_degree(system, fake=True)

    # The stated d'_F witness: g_1 = 1, g_2 = X_1 + 1.
    g2f2 = poly_add(poly_mul_mono(WITNESS_F2, X1), WITNESS_F2)
    combination = poly_add(reduce_fe(WITNESS_F1), reduce_fe(g2f2))

    # Exhaustive: at D = 2 every generator has degree exactly 2, so every
    # cofactor is a scalar and there are only 31 nonzero choices. This is the
    # whole of the `d_F >= 3` half, checkable by hand.
    falls_at_two = []
    for bits in range(1, 1 << len(system)):
        comb = frozenset()
        for i, g in enumerate(system):
            if bits >> i & 1:
                comb = poly_add(comb, g)
        if comb and deg(comb) < 2:
            falls_at_two.append(bits)

    # d_F <= 3, by exhibiting it: 1*f_1 + (X_1+1)*f_2 + X_3*(X_1^2+X_1).
    fe1 = field_equations(3)[0]                      # X_1^2 + X_1
    products = [WITNESS_F1, g2f2, poly_mul_mono(fe1, X3)]
    total = frozenset()
    for p in products:
        total = poly_add(total, p)
    upper_witness = {
        "products": ["1*f_1", "(X_1+1)*f_2", "X_3*(X_1^2+X_1)"],
        "max_product_degree": max(deg(p) for p in products),
        "sum": sorted(total),
        "sum_degree": deg(total),
        "sum_nonzero": bool(total),
        "is_a_fall_at_3": (max(deg(p) for p in products) == 3
                           and bool(total) and deg(total) < 3),
    }

    # d'_F >= 2: no admissible product has degree <= 1, so no witness at D = 1.
    degree_one_products = [
        (i, m) for i, g in enumerate([WITNESS_F1, WITNESS_F2])
        for m in monomials_up_to(1, 3, multilinear=True)
        if (pr := reduce_fe(poly_mul_mono(g, m))) and deg(pr) <= 1
    ]

    return {
        "d_F_inside": d_true,
        "d_prime_F": d_fake,
        "inside_form_holds": d_true <= d_fake,
        # --- the refutation, standing on explicit witnesses alone ---
        # These four facts settle it without using first_fall_degree at all,
        # which matters because the general routine is the fragile part of this
        # file and was wrong twice before the oracle pinned it.
        "d_prime_F_at_most_2_witness": {
            "cofactors": "g_1 = 1, g_2 = X_1 + 1",
            "products_mod_fe_degrees": [deg(reduce_fe(WITNESS_F1)), deg(reduce_fe(g2f2))],
            "sum_mod_fe": sorted(combination),
            "sum_mod_fe_degree": deg(combination),
            "sum_mod_fe_nonzero": bool(combination),
        },
        "d_prime_F_at_least_2_because": "no admissible product has reduced degree <= 1",
        "degree_one_products_found": degree_one_products,
        "d_F_at_least_3_because": (
            "at D = 2 every generator has degree exactly 2, so every cofactor is a "
            "scalar; all 31 nonzero scalar combinations were enumerated and none "
            "falls below degree 2"
        ),
        "scalar_combinations_tested_at_D2": (1 << len(system)) - 1,
        "falls_found_at_D2": falls_at_two,
        "d_F_at_most_3_witness": upper_witness,
        "refutation_stands_without_general_routine": (
            not degree_one_products
            and not falls_at_two
            and upper_witness["is_a_fall_at_3"]
            and bool(combination)
            and deg(combination) < 2
        ),
    }


def least_degree_in_ideal(gens, fake: bool, n: int = N_DEFAULT,
                          cofactor_degree_bound: int = 4) -> int | None:
    """Least degree of a nonzero element of the span of `{m * g}`.

    Cofactors are bounded by `cofactor_degree_bound` rather than unbounded, so
    this is an UPPER bound on the true least degree: a longer search can only
    find something smaller. Stated because an upper bound reported as an exact
    value is the kind of quiet overclaim this file exists to catch.
    """
    prep = reduce_fe if fake else (lambda p: p)
    gens = [g for g in (prep(g) for g in gens) if g]
    rows = []
    for g in gens:
        for m in monomials_up_to(cofactor_degree_bound, n, multilinear=fake):
            prod = prep(poly_mul_mono(g, m))
            if prod:
                rows.append(prod)
    if not rows:
        return None
    monos, vecs = _vectorise(rows)
    max_degree = max(deg_mono(m) for m in monos)
    # For each target degree, eliminate using ONLY the monomials above it as
    # pivots: anything that survives is a nonzero element of degree <= target.
    # Reducing basis-first and reading off degrees does NOT work -- a reduced
    # basis need not contain a minimal-degree element even when the span does.
    for target in range(0, max_degree + 1):
        high_mask = 0
        for i, m in enumerate(monos):
            if deg_mono(m) > target:
                high_mask |= 1 << i
        basis: dict[int, int] = {}
        for v in vecs:
            vec = v
            while vec & high_mask:
                pivot = (vec & high_mask).bit_length() - 1
                if pivot not in basis:
                    basis[pivot] = vec
                    vec = 0
                    break
                vec ^= basis[pivot]
            if vec:
                return target
    return None


def degenerate_under_ge_reading() -> dict:
    """Measure the `>=` reading, under which the lemma is true and empty.

    Koszul padding (`g_1 += m f_2`, `g_2 += m f_1`) raises
    `max_i deg(g_i f_i)` without touching the sum, so a literal `>=` in
    condition (1) is free: the quantity stops depending on the products at all
    and collapses to `1 + (least degree of a nonzero element of the ideal)`.
    Reported because a refutation silent about the reading under which its
    target is TRUE is not honest about its own scope.
    """
    system = witness_system()
    least_true = least_degree_in_ideal(system, fake=False)
    least_fake = least_degree_in_ideal(system, fake=True)
    return {
        "least_degree_nonzero_ideal_element_true": least_true,
        "least_degree_nonzero_ideal_element_fake": least_fake,
        "ge_reading_d_F": None if least_true is None else least_true + 1,
        "ge_reading_d_prime_F": None if least_fake is None else least_fake + 1,
        "collapses_to_same_value": least_true == least_fake,
        "these_are_upper_bounds": "cofactors searched to degree 4, not unbounded",
        "note": "Under >= the inside form HOLDS here, for a reason having nothing "
                "to do with any upstream lemma. It is not the declared convention, "
                "and under it 2015/984's own Assumption 1 would be false.",
    }


def first_fall_degree_by_enumeration(gens, fake: bool, n: int = N_DEFAULT,
                                     dmax: int = 4):
    """`first_fall_degree` again, by LITERAL ENUMERATION of every cofactor tuple.

    An independent oracle, not an optimisation: it is exponential and usable
    only on tiny systems. It exists because the fast path is a hand-rolled `F_2`
    eliminator with a pivot mask, the single most error-prone object in this
    file, and because two separate implementations of this quantity -- the
    original reader's and the first draft of this one -- were each wrong on the
    first attempt in a way that still produced plausible integers.

    Agreement between the two is evidence about the QUANTITY. Disagreement
    localises to one of two named implementations, which is the whole reason to
    pay for it.
    """
    prep = reduce_fe if fake else (lambda p: p)
    prepped = [prep(g) for g in gens]
    live = [(i, g) for i, g in enumerate(prepped) if g]
    if not live:
        return None
    for D in range(1, dmax + 1):
        # every cofactor that keeps its product at degree <= D, per generator
        choices = []
        for _, g in live:
            ok = [frozenset()]
            for m in monomials_up_to(D, n, multilinear=fake):
                prod = prep(poly_mul_mono(g, m))
                if prod and deg(prod) <= D:
                    ok.append(frozenset({m}))
            choices.append(ok)
        # cofactors are SUMS of admissible monomials; enumerate subsets of them
        per_gen = []
        for (idx, g), ok in zip(live, choices):
            monos = [next(iter(c)) for c in ok if c]
            subsets = []
            for r in range(len(monos) + 1):
                for combo in itertools.combinations(monos, r):
                    cof = frozenset(combo)
                    prod = frozenset()
                    for m in cof:
                        prod = poly_add(prod, poly_mul_mono(g, m))
                    prod = prep(prod)
                    if deg(prod) <= D:
                        subsets.append((cof, prod))
            per_gen.append(subsets)
        if any(not s for s in per_gen):
            continue
        for tup in itertools.product(*per_gen):
            total = frozenset()
            for _, prod in tup:
                total = poly_add(total, prod)
            if not total or deg(total) >= D:
                continue
            if max(deg(prod) for _, prod in tup) == D:
                return D
    return None


def cross_check_eliminator(trials: int = 40, seed: int = 902126) -> dict:
    """Run both implementations on random tiny systems and compare."""
    rng = random.Random(seed)
    pool = [m for m in monomials_up_to(2, 2, multilinear=True) if sum(m) > 0]
    agree = disagree = 0
    mismatches = []
    for _ in range(trials):
        fs = [frozenset(rng.sample(pool, rng.randint(1, len(pool))))
              for _ in range(2)]
        system = fs + field_equations(2)
        for fake in (False, True):
            fast = first_fall_degree(system, fake=fake, n=2, dmax=4)
            slow = first_fall_degree_by_enumeration(system, fake=fake, n=2, dmax=4)
            if fast == slow:
                agree += 1
            else:
                disagree += 1
                mismatches.append({"system": [sorted(f) for f in fs],
                                   "fake": fake, "fast": fast, "slow": slow})
    return {"decisions": agree + disagree, "agree": agree,
            "disagree": disagree, "mismatches": mismatches[:5]}


def survey_random_multilinear_pairs(trials: int = 400, seed: int = 20260916) -> dict:
    """How often does the inside form fail on random multilinear pairs at N=3?

    This is the part the original read did not measure, and it changes the
    finding's character: a lone counterexample invites the response "pathological
    instance", and a failure rate near a fifth does not.
    """
    rng = random.Random(seed)
    pool = [m for m in monomials_up_to(3, multilinear=True) if sum(m) > 0]
    violated = equal = below = skipped = 0
    for _ in range(trials):
        fs = [frozenset(rng.sample(pool, rng.randint(1, min(4, len(pool)))))
              for _ in range(2)]
        system = fs + field_equations(3)
        a = first_fall_degree(system, fake=False)
        b = first_fall_degree(system, fake=True)
        if a is None or b is None:
            skipped += 1
        elif a > b:
            violated += 1
        elif a == b:
            equal += 1
        else:
            below += 1
    return {
        "trials": trials,
        "seed": seed,
        "d_F_exceeds_d_prime_F": violated,
        "equal": equal,
        "d_F_below_d_prime_F": below,
        "undetermined": skipped,
    }


def main() -> int:
    import json

    result = check_witness()
    print("=== INSIDE form of Lemma 4: d_F(F u S_fe) <= d'_F(F u S_fe) ===")
    print("    f_1 = X_1 X_2 + X_3 ,  f_2 = X_1 X_3 + X_2   over F_2, N = 3")
    print(json.dumps(result, indent=1))
    if result["inside_form_holds"]:
        print("\nUNEXPECTED: the inside form HELD. The refutation does not reproduce.")
        return 1
    print(f"\n  REFUTED: d_F = {result['d_F_inside']} > {result['d_prime_F']} = d'_F")

    print("\n=== oracle: fast eliminator vs literal enumeration ===")
    cross = cross_check_eliminator()
    print(json.dumps(cross, indent=1))
    if cross["disagree"]:
        print("\nThe two implementations DISAGREE. Trust neither number above.")
        return 1

    print("\n=== the >= reading, under which the lemma is true and empty ===")
    print(json.dumps(degenerate_under_ge_reading(), indent=1))

    print("\n=== is the failure pathological? random multilinear pairs, N = 3 ===")
    print(json.dumps(survey_random_multilinear_pairs(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
