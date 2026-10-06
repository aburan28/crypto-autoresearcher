"""Factor-base decks (C-2, C-8) and query targets (C-5).

A deck is a sorted list V of liftable x-coordinates; the factor base is
{P : x(P) in V}, both signs. ``points[i]`` is the canonical lift
(x, min(y, p - y)) of V[i]; the signed factor base is
[(points[i], +1), (points[i], -1)]. Deck construction is charged to its own
counter (spec v1 charging_rule "Charge FB construction"; reported with the
table cost, amortized and unamortized).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import labels
from fparith import Curve, Fp, OpCounter
from verify import O, VCurve

DECKS = ("interval_x", "subgroup_x", "random_x")
CONTROL_DECK = "progression"
N_PLANTED = 16
N_RANDOM = 16


@dataclass
class Deck:
    name: str
    V: list
    points: list
    construction_ops: dict
    notes: dict = field(default_factory=dict)

    @property
    def size(self) -> int:
        return len(self.V)


def _finish(name, V, curve, counter, snap, notes):
    V = sorted(V)
    pts = [curve.lift(x) for x in V]
    return Deck(name=name, V=V, points=pts, construction_ops=counter.delta(snap), notes=notes)


def interval_x(fx, curve: Curve) -> Deck:
    c = curve.F.c
    snap = c.snapshot()
    V, x = [], 0
    while len(V) < fx["L"]:
        if curve.is_liftable(x):
            V.append(x)
        x += 1
    return _finish("interval_x", V, curve, c, snap, {"x_scanned_to": x - 1})


def subgroup_x(fx, curve: Curve) -> Deck:
    """Liftable elements of the order-L subgroup of F_p^* (|V| may be < L)."""
    F, L, p = curve.F, fx["L"], fx["p"]
    assert (p - 1) % L == 0
    c = F.c
    snap = c.snapshot()
    primes = [r for r in range(2, L + 1) if L % r == 0 and all(r % s for s in range(2, r))]
    g, base = None, 2
    while g is None:
        cand = F.pow(base, (p - 1) // L)
        if all(F.pow(cand, L // r) != 1 for r in primes):
            g = cand
        base += 1
    elems, e = [], 1
    for _ in range(L):
        elems.append(e)
        e = F.mul(e, g)
    assert len(set(elems)) == L
    V = [x for x in elems if curve.is_liftable(x)]
    return _finish("subgroup_x", V, curve, c, snap,
                   {"subgroup_generator": g, "subgroup_size": L, "liftable": len(V)})


def random_x(fx, curve: Curve, size: int, ns: str) -> Deck:
    """|V| = size, without replacement from all liftable x, SHA256 labels
    '<ns>|random_x|L<L>|<seed>|<i>', i = attempt counter from 0."""
    c = curve.F.c
    snap = c.snapshot()
    V, seen, i, rejected = [], set(), 0, 0
    while len(V) < size:
        try:
            x = labels.uniform(labels.cell_lab(ns, "random_x", fx["L"], fx["seed"], i), fx["p"])
        except labels.RejectionFailure:
            x = None
        i += 1
        if x is None or x in seen or not curve.is_liftable(x):
            rejected += 1
            continue
        seen.add(x)
        V.append(x)
    return _finish("random_x", V, curve, c, snap, {"draws": i, "rejected": rejected})


def progression(fx, curve: Curve) -> Deck:
    """C-8 known-structure positive: V = x({k G : k = 1..L})."""
    c = curve.F.c
    snap = c.snapshot()
    G = tuple(fx["G"])
    V, P = [], G
    for k in range(1, fx["L"] + 1):
        V.append(P[0])
        P = curve.add(P, G)
    assert len(set(V)) == fx["L"]
    return _finish("progression", V, curve, c, snap, {"k_range": [1, fx["L"]]})


def build_all(fx, ns: str) -> dict:
    """All three decks plus the progression control, each with a fresh counter."""
    out = {}
    for name in DECKS + (CONTROL_DECK,):
        F = Fp(fx["p"], OpCounter())
        curve = Curve(F, fx["a"], fx["b"])
        if name == "interval_x":
            out[name] = interval_x(fx, curve)
        elif name == "subgroup_x":
            out[name] = subgroup_x(fx, curve)
        elif name == "random_x":
            out[name] = random_x(fx, curve, out["interval_x"].size, ns)
        else:
            out[name] = progression(fx, curve)
    return out


def targets(fx, deck: Deck, ns: str, n_planted: int = N_PLANTED, n_random: int = N_RANDOM):
    """C-5 queries. Planted j: 5 signed FB points, term k drawn as r in
    [0, 2|V|) from '<ns>|planted|L<L>|<seed>|<deck>|<j>|<k>', index r // 2,
    sign +1 if r even else -1. Random j: R = k G, k = SHA256('<ns>|random|
    L<L>|<seed>|<deck>|<j>') mod q. Uncharged (verifier arithmetic)."""
    L, seed, q = fx["L"], fx["seed"], fx["N"]
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    G = tuple(fx["G"])
    out = []
    n = deck.size
    for j in range(n_planted):
        terms = []
        for k in range(5):
            r = labels.uniform(labels.cell_lab(ns, "planted", L, seed, deck.name, j, k), 2 * n)
            terms.append((r // 2, 1 if r % 2 == 0 else -1))
        R = vc.sum_signed([(deck.points[i], s) for i, s in terms])
        out.append(dict(query_id=f"L{L}-s{seed}-{deck.name}-planted-{j:02d}", kind="planted",
                        j=j, R=R, planted_terms=terms))
    for j in range(n_random):
        k = labels.h(labels.cell_lab(ns, "random", L, seed, deck.name, j)) % q
        R = vc.mul(k, G)
        out.append(dict(query_id=f"L{L}-s{seed}-{deck.name}-random-{j:02d}", kind="random",
                        j=j, R=R, k=k))
    return out
