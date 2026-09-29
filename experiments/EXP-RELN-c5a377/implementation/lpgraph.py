"""LP graph, cycle rank, GF(2) cross-check and Horton minimum cycle basis
(AMD-20260926-a7d25d C-3, C-4).

Graph: vertex 0 is the root; vertices 1..n-1 are the LP x-classes incident to
at least one LP edge, in increasing x order. Each 2-LP relation is an edge
between its two LP vertices (a self-loop when both are the same x-class);
each 1-LP relation is an edge from its LP vertex to the root. Multigraph:
parallel edges and self-loops are kept, one edge per relation.
"""

from __future__ import annotations

import math
from collections import deque


def build(relations: list[dict], B: int) -> dict:
    lp_xs = set()
    for r in relations:
        if r["kind"] in ("lp1", "lp2"):
            x1, _, x2, _ = r["rel"]
            lp_xs.update(x for x in (x1, x2) if x >= B)
    order = sorted(lp_xs)
    vid = {x: i + 1 for i, x in enumerate(order)}
    edges = []
    for r in relations:
        x1, _, x2, _ = r["rel"]
        if r["kind"] == "lp1":
            edges.append((vid[x1 if x1 >= B else x2], 0))
        elif r["kind"] == "lp2":
            edges.append((vid[x1], vid[x2]))
    return {"n": len(order) + 1, "edges": edges, "lp_x": order}


def components(n: int, edges) -> list[list[int]]:
    parent = list(range(n))

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    comp = {}
    for u in range(n):
        comp.setdefault(find(u), []).append(u)
    return list(comp.values())


def gf2_incidence_rank(n: int, edges) -> int:
    """Rank over GF(2) of the vertex-edge incidence matrix (independent of
    union-find); cycle-space dimension = |E| - rank."""
    basis = {}  # leading bit -> vector
    rank = 0
    for u, v in edges:
        vec = (1 << u) ^ (1 << v)
        while vec:
            lead = vec.bit_length() - 1
            if lead in basis:
                vec ^= basis[lead]
            else:
                basis[lead] = vec
                rank += 1
                break
    return rank


def metrics(g: dict, L: int) -> dict:
    n, edges = g["n"], g["edges"]
    m = len(edges)
    comps = components(n, edges)
    c = len(comps)
    cr = m - n + c
    rank = gf2_incidence_rank(n, edges)
    comp_of = {}
    for i, cc in enumerate(comps):
        for u in cc:
            comp_of[u] = i
    e_in = [0] * c
    for u, _ in edges:
        e_in[comp_of[u]] += 1
    cyclic = sum(1 for i, cc in enumerate(comps) if e_in[i] - len(cc) + 1 > 0)
    giant = max(len(cc) for cc in comps) if comps else 0
    out = {"V": n, "E": m, "components": c, "cycle_rank": cr,
           "cycle_rank_gf2": m - rank, "cycle_rank_identity_ok": (m - rank) == cr,
           "components_with_cycle": cyclic, "giant_component_size": giant,
           "giant_component_fraction": giant / n if n else None,
           "root_component_size": len(comps[comp_of[0]]) if n else 0,
           "E_over_V": m / n if n else None,
           "self_loops": sum(1 for u, v in edges if u == v), "L": L}
    out.update(deltas(cr, m, L))
    return out


def deltas(cr: int, m: int, L: int) -> dict:
    """delta_proof := log_L(cycle_rank) - 1 ; delta_ratio := log_L(cycle_rank / |E|).
    Undefined (null, with reason) when L < 2 or cycle_rank = 0."""
    if L < 2:
        why = f"L = {L} < 2: log_L undefined"
        return {"delta_proof": None, "delta_ratio": None, "delta_undefined_reason": why}
    if cr <= 0:
        why = "cycle_rank = 0: log undefined (-inf)"
        return {"delta_proof": None, "delta_ratio": None, "delta_undefined_reason": why}
    lnL = math.log(L)
    return {"delta_proof": math.log(cr) / lnL - 1, "delta_ratio": math.log(cr / m) / lnL,
            "delta_undefined_reason": None}


# ------------------------------------------------------------------ Horton
def _bfs_tree(n, adj, v):
    """Deterministic BFS from v: dist, parent edge id, branch (child of v)."""
    dist = [-1] * n
    pmask = [0] * n
    branch = [-1] * n
    dist[v] = 0
    dq = deque([v])
    while dq:
        u = dq.popleft()
        for w, eid in adj[u]:
            if dist[w] < 0:
                dist[w] = dist[u] + 1
                pmask[w] = pmask[u] | (1 << eid)
                branch[w] = w if u == v else branch[u]
                dq.append(w)
    return dist, pmask, branch


def horton_mcb(g: dict, max_candidates: int | None = None) -> dict:
    """Horton's minimum cycle basis (unit weights) of a multigraph.

    Candidates: every self-loop, and for every vertex v and edge e = (x, y)
    with x, y reachable, the cycle P(v,x) + e + P(y,v) when the two BFS-tree
    paths meet only at v and e lies on neither. Sorted by (length, edge set);
    kept greedily when GF(2)-independent of those already kept.
    """
    n, edges = g["n"], g["edges"]
    m = len(edges)
    adj = [[] for _ in range(n)]
    for eid, (u, v) in enumerate(edges):
        if u != v:
            adj[u].append((v, eid))
            adj[v].append((u, eid))
    for a in adj:
        a.sort()
    cand = set()
    for eid, (u, v) in enumerate(edges):
        if u == v:
            cand.add(1 << eid)
    for s in range(n):
        dist, pmask, branch = _bfs_tree(n, adj, s)
        for eid, (x, y) in enumerate(edges):
            if x == y or dist[x] < 0 or dist[y] < 0:
                continue
            bit = 1 << eid
            if (pmask[x] | pmask[y]) & bit:
                continue
            if x != s and y != s and branch[x] == branch[y]:
                continue
            cand.add(pmask[x] | pmask[y] | bit)
            if max_candidates and len(cand) > max_candidates:
                raise MemoryError(f"Horton candidate set exceeds {max_candidates}")
    ordered = sorted(cand, key=lambda c: (bin(c).count("1"), c))
    target = m - n + len(components(n, edges))
    red = {}  # lead bit -> reduced vector
    basis = []
    for c in ordered:
        if len(basis) == target:
            break
        vec = c
        while vec:
            lead = vec.bit_length() - 1
            if lead in red:
                vec ^= red[lead]
            else:
                red[lead] = vec
                basis.append(c)
                break
    lengths = [bin(c).count("1") for c in basis]
    ok_cycles = all(_is_cycle_space_element(c, edges, n) for c in basis)
    hist = {}
    for ln in lengths:
        hist[ln] = hist.get(ln, 0) + 1
    return {"basis_size": len(basis), "cycle_rank": target,
            "size_identity_ok": len(basis) == target, "all_even_degree": ok_cycles,
            "total_weight": sum(lengths), "max_length": max(lengths) if lengths else 0,
            "mean_length": (sum(lengths) / len(lengths)) if lengths else None,
            "length_histogram": {str(k): hist[k] for k in sorted(hist)},
            "n_candidates": len(cand), "basis": basis}


def _is_cycle_space_element(mask: int, edges, n: int) -> bool:
    deg = [0] * n
    eid = 0
    while mask:
        if mask & 1:
            u, v = edges[eid]
            deg[u] += 1
            deg[v] += 1
        mask >>= 1
        eid += 1
    return all(d % 2 == 0 for d in deg)
