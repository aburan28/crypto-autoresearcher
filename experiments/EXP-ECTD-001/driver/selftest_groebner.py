"""
selftest_groebner.py -- validate the from-scratch Buchberger implementation via the
decisive "ideal membership" property: every element of a Groebner basis computed
from generators that vanish at a known point must ALSO vanish at that point (since
Groebner basis computation only takes F_p-linear combinations of the generators
multiplied by monomials -- it changes the *generating set*, never the *ideal* /
*variety*). This is checked over many random systems, not asserted from theory alone.
Run: python3 -m driver.selftest_groebner
"""
import random
from . import mvpoly, groebner


def random_poly_with_root(nvars, p, root, max_deg, nterms, rng):
    """Build a random polynomial of the given shape that vanishes at `root`, by
    generating random terms and then adjusting the constant term to force f(root)=0."""
    terms = {}
    for _ in range(nterms):
        exps = tuple(rng.randrange(0, max_deg + 1) for _ in range(nvars))
        if sum(exps) > max_deg:
            continue
        c = rng.randrange(1, p)
        terms[exps] = (terms.get(exps, 0) + c) % p
    f = mvpoly.MPoly(terms, nvars, p)
    val = f.evaluate(root)
    const_key = (0,) * nvars
    cur_const = f.terms.get(const_key, 0)
    new_const = (cur_const - val) % p
    new_terms = dict(f.terms)
    if new_const == 0:
        new_terms.pop(const_key, None)
    else:
        new_terms[const_key] = new_const
    f2 = mvpoly.MPoly(new_terms, nvars, p)
    assert f2.evaluate(root) == 0
    return f2


def run():
    print("=== selftest_groebner ===")
    p = 10007
    rng = random.Random(3)
    n_systems = 30
    for trial in range(n_systems):
        nvars = 2
        root = tuple(rng.randrange(p) for _ in range(nvars))
        gens = [random_poly_with_root(nvars, p, root, max_deg=4, nterms=6, rng=rng)
                for _ in range(3)]
        G, stats = groebner.buchberger(gens, p, nvars, max_pairs=2000, max_degree=40,
                                        wall_seconds=20.0)
        assert not stats["timed_out"], f"trial {trial}: unexpected timeout, stats={stats}"
        for g in G:
            val = g.evaluate(root)
            assert val == 0, (
                f"trial {trial}: GB element does not vanish at planted common root "
                f"{root}: val={val}, stats={stats}"
            )
    print(f"  {n_systems} random systems (each with a planted common root): "
          f"every computed GB element vanishes at the root. OK")

    # a hand-checkable tiny case: f1 = x^2 - 1, f2 = y - x  (root set {(1,1),(-1,-1)})
    p2 = 97
    x = mvpoly.MPoly.var(0, 2, p2)
    y = mvpoly.MPoly.var(1, 2, p2)
    one = mvpoly.MPoly.constant(1, 2, p2)
    f1 = x.mul(x).sub(one)
    f2 = y.sub(x)
    G, stats = groebner.buchberger([f1, f2], p2, 2, max_pairs=200, max_degree=20, wall_seconds=5.0)
    for root in [(1, 1), (p2 - 1, p2 - 1)]:
        for g in G:
            assert g.evaluate(root) == 0
    print(f"  hand-checkable case (x^2-1, y-x): GB vanishes at both known roots. OK, "
          f"solving_degree={stats['max_spoly_degree']}")
    print("ALL GROEBNER SELFTESTS PASSED")


if __name__ == "__main__":
    run()
