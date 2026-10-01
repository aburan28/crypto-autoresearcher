"""Controls on graphs (AMD-20260926-a7d25d C-6).

* configuration-model rewire: the stub list of the observed multigraph (a
  self-loop contributes two stubs at its vertex) is shuffled by a SHA256
  Fisher-Yates and paired consecutively; self-loops and parallel edges are
  kept (pure configuration model). Degrees, |V| and |E| are preserved.
* Erdos-Renyi G(|V|, |E|): |E| distinct unordered vertex pairs (no loops)
  drawn uniformly by rejection; infeasible when |E| > C(|V|, 2).
* planted-dense known positive: on the observed vertex set, a random
  spanning tree (vertex i >= 1 in a shuffled order attaches to a uniform
  earlier vertex) plus ceil(|V|^{1.5}) extra uniform non-loop edges, so the
  cycle rank is exactly ceil(|V|^{1.5}).
"""

from __future__ import annotations

import math

import labels


class Draws:
    """Deterministic uniform draws from '<prefix>|<counter>'."""

    def __init__(self, prefix: str):
        self.prefix, self.i = prefix, 0

    def uniform(self, n: int) -> int:
        v = labels.uniform(f"{self.prefix}|{self.i}", n)
        self.i += 1
        return v


def _shuffle(xs: list, dr: Draws) -> list:
    xs = list(xs)
    for i in range(len(xs) - 1, 0, -1):
        j = dr.uniform(i + 1)
        xs[i], xs[j] = xs[j], xs[i]
    return xs


def ctx(bits, seed, budget) -> str:
    return f"{bits}|{seed}|{budget}"


def rewire(g: dict, ns: str, i: int, context: str) -> dict:
    stubs = []
    for u, v in g["edges"]:
        stubs.extend((u, v))
    dr = Draws(f"{labels.rewire_label(ns, i)}|{context}")
    s = _shuffle(stubs, dr)
    edges = [(s[2 * t], s[2 * t + 1]) for t in range(len(s) // 2)]
    return {"n": g["n"], "edges": edges}


def erdos_renyi(n: int, m: int, ns: str, i: int, context: str) -> dict | None:
    if n < 2 or m > n * (n - 1) // 2:
        return None
    dr = Draws(labels.lab(ns, "er", i, context))
    chosen, edges = set(), []
    while len(edges) < m:
        u, v = dr.uniform(n), dr.uniform(n)
        if u == v:
            continue
        key = (min(u, v), max(u, v))
        if key in chosen:
            continue
        chosen.add(key)
        edges.append(key)
    return {"n": n, "edges": edges}


def planted_dense(n: int, ns: str, context: str) -> dict | None:
    if n < 2:
        return None
    dr = Draws(labels.lab(ns, "planted", context))
    order = _shuffle(list(range(n)), dr)
    edges = [(order[i], order[dr.uniform(i)]) for i in range(1, n)]
    extra = math.ceil(n ** 1.5)
    for _ in range(extra):
        u = dr.uniform(n)
        v = dr.uniform(n - 1)
        edges.append((u, v if v < u else v + 1))
    return {"n": n, "edges": edges, "planted_cycle_rank": extra}


def degree_sequence(g: dict) -> list[int]:
    d = [0] * g["n"]
    for u, v in g["edges"]:
        d[u] += 1
        d[v] += 1
    return d
