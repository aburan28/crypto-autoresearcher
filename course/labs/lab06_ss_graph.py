#!/usr/bin/env python3
"""
Lab 06 — The supersingular 2-isogeny graph over F_{p^2}.

Companion to course module 10 (capstone lab). Run directly:

    python3 lab06_ss_graph.py            # build + verify graphs
    python3 lab06_ss_graph.py --export   # also write JSON for the
                                         # interactive explorer

Everything in this course converges here. For a prime p, the graph G_2(p):

  * vertices: supersingular j-invariants over F_{p^2}
              (there are floor(p/12) + {0,1,1,2} of them, all in F_{p^2});
  * edges:    2-isogenies. Every curve has E[2] = (Z/2)^2, hence three
              order-2 subgroups, hence three outgoing edges: the graph is
              3-regular and, remarkably, Ramanujan (an optimal expander).

Construction, using only this course's own tools:

  1. start from a known supersingular curve (j = 1728 if p = 3 mod 4,
     j = 0 if p = 2 mod 3);
  2. find its three 2-torsion x-coordinates = roots of x^3 + a x + b over
     F_{p^2}, via x^q mod f and equal-degree splitting (module 05's
     Frobenius at work: the polynomial x^q - x is exactly the product of
     all linear polynomials over F_q);
  3. push through Velu's formulas (lab 05) to get the three neighbours;
  4. breadth-first search until the component closes up.

Verification: vertex count matches the mass-formula count, every vertex
has out-degree 3, every edge (j1, j2) is a root of the classical modular
polynomial Phi_2, and every vertex passes a randomized supersingularity
test ([p+1]P = O or [p-1]P = O, depending on the twist we happen to hit).
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

from lab02_finite_fields import Fp2
from lab03_elliptic_curves import EllipticCurve, Point
from lab05_isogenies import Isogeny

# The classical modular polynomial Phi_2(X, Y): its roots pair up exactly
# the 2-isogenous j-invariants. (Yes, the coefficients really are this
# big — for Phi_3 they are much worse, which is why nobody computes these
# by hand and Velu-based navigation is preferred.)
PHI2 = [
    ((3, 0), 1), ((0, 3), 1), ((2, 2), -1),
    ((2, 1), 1488), ((1, 2), 1488),
    ((2, 0), -162000), ((0, 2), -162000),
    ((1, 1), 40773375),
    ((1, 0), 8748000000), ((0, 1), 8748000000),
    ((0, 0), -157464000000000),
]


def phi2_value(j1: Fp2, j2: Fp2) -> Fp2:
    total = j1.zero()
    for (e1, e2), c in PHI2:
        total = total + j1 ** e1 * j2 ** e2 * c
    return total


# ----------------------------------------------------------------------
# Polynomial arithmetic over a lab-02 field (coefficient lists, low
# degree first) — just enough to find roots of cubics over F_{p^2}
# ----------------------------------------------------------------------

def _trim(f: list) -> list:
    while len(f) > 1 and f[-1].is_zero():
        f.pop()
    return f


def poly_sub(f: list, g: list) -> list:
    n = max(len(f), len(g))
    zero = (f[0] if f else g[0]).zero()
    out = []
    for i in range(n):
        a = f[i] if i < len(f) else zero
        b = g[i] if i < len(g) else zero
        out.append(a - b)
    return _trim(out)


def poly_mul(f: list, g: list) -> list:
    zero = f[0].zero()
    out = [zero] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        if a.is_zero():
            continue
        for jx, b in enumerate(g):
            out[i + jx] = out[i + jx] + a * b
    return _trim(out)


def poly_divmod(f: list, g: list) -> tuple[list, list]:
    zero = f[0].zero()
    g = _trim(list(g))
    inv_lead = g[-1].inverse()
    r = list(f)
    q = [zero] * max(1, len(f) - len(g) + 1)
    while len(r) >= len(g) and not (len(r) == 1 and r[0].is_zero()):
        shift = len(r) - len(g)
        coef = r[-1] * inv_lead
        q[shift] = q[shift] + coef
        for i, gc in enumerate(g):
            r[shift + i] = r[shift + i] - coef * gc
        r = _trim(r)
        if len(r) < len(g):
            break
    return _trim(q), _trim(r)


def poly_monic(f: list) -> list:
    inv = f[-1].inverse()
    return [c * inv for c in f]


def poly_gcd(f: list, g: list) -> list:
    f, g = _trim(list(f)), _trim(list(g))
    while not (len(g) == 1 and g[0].is_zero()):
        _, r = poly_divmod(f, g)
        f, g = g, r
    return poly_monic(f) if not f[-1].is_zero() else f


def poly_mulmod(f: list, g: list, m: list) -> list:
    _, r = poly_divmod(poly_mul(f, g), m)
    return r


def poly_powmod(f: list, e: int, m: list) -> list:
    one = f[0].one()
    result = [one]
    base = poly_divmod(f, m)[1]
    while e:
        if e & 1:
            result = poly_mulmod(result, base, m)
        base = poly_mulmod(base, base, m)
        e >>= 1
    return result


def roots_in_field(f: list, q: int, rng: random.Random) -> list:
    """All roots of f (assumed squarefree) lying in the field F_q of its
    coefficients.

    x^q - x is the product of (x - c) over ALL c in F_q, so
    gcd(f, x^q - x) collects precisely the linear factors of f; the
    equal-degree splitting step gcd(f, (x+r)^((q-1)/2) - 1) then cuts the
    product apart because a random shift makes some roots squares and
    others not (Cantor-Zassenhaus).
    """
    zero, one = f[0].zero(), f[0].one()
    x = [zero, one]
    xq = poly_powmod(x, q, f)
    g = poly_gcd(poly_sub(xq, x), f)

    roots: list = []

    def split(g: list) -> None:
        if len(g) == 1:
            return
        if len(g) == 2:  # monic linear: x + c -> root -c
            roots.append(-g[0])
            return
        while True:
            r = one.random(rng)
            h = poly_powmod([r, one], (q - 1) // 2, g)
            d = poly_gcd(poly_sub(h, [one]), g)
            if 1 < len(d) < len(g):
                split(d)
                split(poly_divmod(g, d)[0])
                return

    split(g)
    return roots


# ----------------------------------------------------------------------
# Supersingular graph machinery
# ----------------------------------------------------------------------

def curve_from_j(j: Fp2) -> EllipticCurve:
    """Some curve with the given j-invariant (either twist will do:
    2-isogeny neighbours in j-terms don't depend on the twist)."""
    zero, one = j.zero(), j.one()
    if j.is_zero():
        return EllipticCurve(zero, one)                # y^2 = x^3 + 1
    if j == one * 1728:
        return EllipticCurve(one, zero)                # y^2 = x^3 + x
    c = j * (one * 1728 - j)
    # a = 3 j (1728 - j),  b = 2 j (1728 - j)^2: one checks j(E) = j.
    return EllipticCurve(c * 3, c * (one * 1728 - j) * 2)


def two_isogeny_neighbours(j: Fp2, rng: random.Random) -> list[Fp2]:
    """The three j-invariants 2-isogenous to j (with multiplicity)."""
    E = curve_from_j(j)
    q = j.p * j.p
    f = [E.b, E.a, j.zero(), j.one()]                  # x^3 + a x + b
    xs = roots_in_field(f, q, rng)
    assert len(xs) == 3, "supersingular curves have full 2-torsion in F_{p^2}"
    out = []
    for x0 in xs:
        phi = Isogeny(E, Point(E, x0, x0.zero()), 2)
        out.append(phi.codomain.j_invariant())
    return out


def expected_vertex_count(p: int) -> int:
    """Eichler-Deuring mass formula, made exact: floor(p/12) plus a
    correction 0/1/1/2 for p = 1/5/7/11 mod 12."""
    return p // 12 + {1: 0, 5: 1, 7: 1, 11: 2}[p % 12]


def starting_j(p: int) -> Fp2:
    if p % 4 == 3:
        return Fp2(p, 1728)     # y^2 = x^3 + x is supersingular
    if p % 3 == 2:
        return Fp2(p, 0)        # y^2 = x^3 + 1 is supersingular
    raise ValueError("for p = 1 mod 12 a CM construction (Broker's "
                     "algorithm) is needed for the starting curve; "
                     "pick another prime for this lab")


def is_supersingular_probably(E: EllipticCurve, rng: random.Random,
                              tries: int = 5) -> bool:
    """Over F_{p^2} a supersingular curve has (p+1)^2 or (p-1)^2 points
    (Frobenius trace +/-2p), so every point is killed by p+1 or p-1.
    Ordinary curves fail this for random points with overwhelming
    probability."""
    p = E.a.p
    for _ in range(tries):
        P = E.random_point(rng)
        if not ((p + 1) * P).is_zero() and not ((p - 1) * P).is_zero():
            return False
    return True


def build_graph(p: int, rng: random.Random | None = None):
    """BFS the supersingular 2-isogeny graph. Returns (js, adjacency):
    js[i] is the i-th discovered j-invariant, adjacency[i] a list of three
    node indices (with multiplicity: loops and double edges are real
    features of these graphs, not bugs)."""
    rng = rng or random.Random(0x515)
    j0 = starting_j(p)
    js: list[Fp2] = [j0]
    index = {j0: 0}
    adjacency: list[list[int]] = []
    queue = [0]
    while queue:
        i = queue.pop(0)
        while len(adjacency) <= i:
            adjacency.append([])
        for jn in two_isogeny_neighbours(js[i], rng):
            if jn not in index:
                index[jn] = len(js)
                js.append(jn)
                queue.append(index[jn])
            adjacency[i].append(index[jn])
    return js, adjacency


# ----------------------------------------------------------------------
# Verification, export, demo
# ----------------------------------------------------------------------

def verify_graph(p: int, js: list[Fp2], adjacency: list[list[int]],
                 rng: random.Random) -> None:
    n = expected_vertex_count(p)
    assert len(js) == n, f"found {len(js)} vertices, expected {n}"
    assert all(len(nbrs) == 3 for nbrs in adjacency), "graph must be 3-regular"
    for i, nbrs in enumerate(adjacency):
        for k in nbrs:
            assert phi2_value(js[i], js[k]).is_zero(), \
                "edge not a root of the modular polynomial Phi_2"
    for j in js:
        assert is_supersingular_probably(curve_from_j(j), rng), \
            f"vertex j={j} failed the supersingularity test"
    # Away from the special vertices j=0 and j=1728 (extra automorphisms),
    # the graph is undirected: each edge appears in both directions.
    special = {i for i, j in enumerate(js)
               if j.is_zero() or j == js[0].one() * 1728}
    for i, nbrs in enumerate(adjacency):
        if i in special:
            continue
        for k in set(nbrs):
            if k in special:
                continue
            assert adjacency[k].count(i) == nbrs.count(k), \
                "edge multiplicities must match in both directions"


def graph_json(p: int, js: list[Fp2], adjacency: list[list[int]]) -> dict:
    ns = js[0].ns
    nodes = []
    for i, j in enumerate(js):
        special = None
        if j.is_zero():
            special = 0
        elif j == js[0].one() * 1728:
            special = 1728
        nodes.append({"id": i, "label": repr(j), "a": j.a, "b": j.b,
                      "special": special})
    edges = [[i, k] for i, nbrs in enumerate(adjacency) for k in nbrs]
    return {"p": p, "nonresidue": ns, "count": len(js),
            "nodes": nodes, "edges": edges}


def _selfcheck() -> tuple[dict, ...]:
    rng = random.Random(9)
    results = []
    for p in (83, 431, 1013):
        js, adjacency = build_graph(p)
        verify_graph(p, js, adjacency, rng)
        results.append(graph_json(p, js, adjacency))
        print(f"lab06: p={p:>5}: {len(js):>3} supersingular j-invariants, "
              f"3-regular, Phi_2 + supersingularity checks passed")
    print("lab06: all self-checks passed")
    return tuple(results)


def _demo(results) -> None:
    p = 83
    data = results[0]
    print(f"\n-- demo: the full supersingular 2-isogeny graph for p = {p} --")
    print(f"vertex count: floor({p}/12) + 2 = {expected_vertex_count(p)} "
          f"(p = 11 mod 12)")
    for node in data["nodes"]:
        nbrs = [data["nodes"][k]["label"]
                for i, k in data["edges"] if i == node["id"]]
        tag = f"  <- j = {node['special']}" if node["special"] is not None else ""
        print(f"   j = {node['label']:>12}  ->  {', '.join(nbrs)}{tag}")
    print("Note the loops/multi-edges near j = 0 and j = 1728 — the extra")
    print("automorphisms there fold isogenies together (module 10).")
    # EXERCISE 6.1: adapt the lab to the 3-isogeny graph (kernels are the
    #   four order-3 subgroups of E[3]; use Isogeny(..., order=3) on
    #   points found by clearing cofactors over F_{p^2} — you will need
    #   the quartic division polynomial or random torsion hunting).
    # EXERCISE 6.2: measure mixing: from j0, do many random walks of
    #   length L and chi-square the endpoint distribution against uniform
    #   as L grows. Compare with the Ramanujan bound's prediction.
    # EXERCISE 6.3: for p = 431, find the shortest path between two given
    #   j-invariants by BFS — then estimate how the path-finding cost
    #   scales with p, and compare with the birthday bound sqrt(#vertices).


def _export(results) -> None:
    out = Path(__file__).resolve().parent.parent / "interactive" / \
        "ssgraph_data.js"
    out.write_text("window.SS_GRAPHS = " +
                   json.dumps(list(results), separators=(",", ":")) +
                   ";\n")
    print(f"exported: {out}")


if __name__ == "__main__":
    results = _selfcheck()
    _demo(results)
    if "--export" in sys.argv:
        _export(results)
