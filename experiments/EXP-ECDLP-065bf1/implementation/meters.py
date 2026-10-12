"""Twin structural meters: primal-graph width and Jacobian rank over F_p.

Path A and path B implement the same greedy min-fill width and the same
Gaussian elimination independently. Disagreement is O-ARTIFACT, not science.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


Term = tuple[int, dict[str, int]]  # (coeff, exponents)


def eval_poly(terms: list[Term], wit: dict[str, int], p: int) -> int:
    s = 0
    for c, exps in terms:
        m = c % p
        for v, e in exps.items():
            if e:
                m = (m * pow(wit[v], e, p)) % p
        s = (s + m) % p
    return s


def poly_degree(terms: list[Term]) -> int:
    d = 0
    for _c, exps in terms:
        d = max(d, sum(exps.values()) if exps else 0)
    return d


def constraint_vars(terms: list[Term]) -> set[str]:
    vs: set[str] = set()
    for _c, exps in terms:
        vs.update(exps)
    return vs


def primal_graph(variables: list[str], constraints: list[dict[str, Any]]) -> dict[str, set[str]]:
    adj = {v: set() for v in variables}
    for con in constraints:
        vs = sorted(constraint_vars(con["terms"]))
        for i, a in enumerate(vs):
            for b in vs[i + 1 :]:
                adj[a].add(b)
                adj[b].add(a)
    return adj


def greedy_width_a(adj_in: dict[str, set[str]]) -> int:
    adj = {v: set(n) for v, n in adj_in.items()}
    remaining = set(adj)
    width = 0
    while remaining:
        v = min(remaining, key=lambda x: (len(adj[x] & remaining), x))
        bag = (adj[v] & remaining) | {v}
        width = max(width, max(0, len(bag) - 1))
        neigh = [u for u in remaining if u in adj[v] and u != v]
        remaining.remove(v)
        for i, a in enumerate(neigh):
            for b in neigh[i + 1 :]:
                adj[a].add(b)
                adj[b].add(a)
    return width


def greedy_width_b(adj_in: dict[str, set[str]]) -> int:
    # Independent copy: degree-then-name selection via explicit scan.
    adj = {v: set(n) for v, n in adj_in.items()}
    remaining = set(adj)
    width = 0
    while remaining:
        best = None
        best_key = None
        for x in remaining:
            key = (len(adj[x] & remaining), x)
            if best_key is None or key < best_key:
                best_key = key
                best = x
        assert best is not None
        v = best
        bag = (adj[v] & remaining) | {v}
        width = max(width, max(0, len(bag) - 1))
        neigh = [u for u in remaining if u in adj[v] and u != v]
        remaining.remove(v)
        for i in range(len(neigh)):
            for j in range(i + 1, len(neigh)):
                a, b = neigh[i], neigh[j]
                adj[a].add(b)
                adj[b].add(a)
    return width


def width_both(adj: dict[str, set[str]]) -> dict[str, Any]:
    wa = greedy_width_a(adj)
    wb = greedy_width_b(adj)
    return {"width_a": wa, "width_b": wb, "agree": wa == wb, "width": wa if wa == wb else None}


def jacobian_rows(
    variables: list[str], constraints: list[dict[str, Any]], wit: dict[str, int], p: int
) -> list[list[int]]:
    rows: list[list[int]] = []
    for con in constraints:
        row = []
        for v in variables:
            deriv = 0
            for c, exps in con["terms"]:
                e = exps.get(v, 0)
                if e == 0:
                    continue
                m = (c * e) % p
                for u, eu in exps.items():
                    if u == v:
                        if e - 1 > 0:
                            m = (m * pow(wit[u], e - 1, p)) % p
                    elif eu:
                        m = (m * pow(wit[u], eu, p)) % p
                deriv = (deriv + m) % p
            row.append(deriv)
        rows.append(row)
    return rows


def gaussian_rank_a(mat: list[list[int]], p: int) -> int:
    a = [row[:] for row in mat]
    n = len(a)
    m = len(a[0]) if a else 0
    r = 0
    c = 0
    while r < n and c < m:
        piv = None
        for i in range(r, n):
            if a[i][c] % p:
                piv = i
                break
        if piv is None:
            c += 1
            continue
        a[r], a[piv] = a[piv], a[r]
        inv = pow(a[r][c] % p, -1, p)
        a[r] = [(x * inv) % p for x in a[r]]
        for i in range(n):
            if i == r:
                continue
            f = a[i][c] % p
            if f:
                a[i] = [(a[i][j] - f * a[r][j]) % p for j in range(m)]
        r += 1
        c += 1
    return r


def gaussian_rank_b(mat: list[list[int]], p: int) -> int:
    # Column-major hunt with last-row pivot preference; rank is invariant.
    a = [row[:] for row in mat]
    n = len(a)
    m = len(a[0]) if a else 0
    used_rows = set()
    rank = 0
    for c in range(m):
        piv = None
        for i in range(n - 1, -1, -1):
            if i in used_rows:
                continue
            if a[i][c] % p:
                piv = i
                break
        if piv is None:
            continue
        inv = pow(a[piv][c] % p, -1, p)
        a[piv] = [(x * inv) % p for x in a[piv]]
        for i in range(n):
            if i == piv:
                continue
            f = a[i][c] % p
            if f:
                a[i] = [(a[i][j] - f * a[piv][j]) % p for j in range(m)]
        used_rows.add(piv)
        rank += 1
    return rank


def rank_both(mat: list[list[int]], p: int) -> dict[str, Any]:
    ra = gaussian_rank_a(mat, p)
    rb = gaussian_rank_b(mat, p)
    return {"rank_a": ra, "rank_b": rb, "agree": ra == rb, "rank": ra if ra == rb else None}


def permute_presentation(
    variables: list[str], constraints: list[dict[str, Any]], wit: dict[str, int]
) -> tuple[list[str], list[dict[str, Any]], dict[str, int]]:
    """Reverse variable names; graph invariants must be preserved."""
    mapping = {v: f"u{len(variables) - 1 - i}" for i, v in enumerate(variables)}
    new_vars = [mapping[v] for v in reversed(variables)]
    new_cons = []
    for con in constraints:
        terms = []
        for c, exps in con["terms"]:
            terms.append((c, {mapping[k]: e for k, e in exps.items()}))
        new_cons.append({"name": con["name"] + "_perm", "terms": terms})
    new_wit = {mapping[k]: val for k, val in wit.items()}
    return new_vars, new_cons, new_wit


def random_coeff_clone(
    constraints: list[dict[str, Any]], seed: int, p: int
) -> list[dict[str, Any]]:
    """Same incidence, different coefficients (null-object control)."""
    rng_state = seed
    out = []
    for con in constraints:
        terms = []
        for _c, exps in con["terms"]:
            rng_state = (1103515245 * rng_state + 12345) % (1 << 31)
            coeff = (rng_state % (p - 1)) + 1
            terms.append((coeff, dict(exps)))
        out.append({"name": con["name"] + "_rnd", "terms": terms})
    return out


def presentation_stats(
    variables: list[str],
    constraints: list[dict[str, Any]],
    wit: dict[str, int],
    p: int,
) -> dict[str, Any]:
    residuals = [eval_poly(c["terms"], wit, p) for c in constraints]
    witness_ok = all(r == 0 for r in residuals)
    adj = primal_graph(variables, constraints)
    w = width_both(adj)
    mat = jacobian_rows(variables, constraints, wit, p)
    rk = rank_both(mat, p)
    n_edges = sum(len(n) for n in adj.values()) // 2
    max_deg = max((poly_degree(c["terms"]) for c in constraints), default=0)
    n_aux = sum(1 for v in variables if v.startswith("lam") or v.startswith("Z") or v.startswith("aux"))
    return {
        "n_vars": len(variables),
        "n_constraints": len(constraints),
        "n_aux": n_aux,
        "n_edges": n_edges,
        "max_degree": max_deg,
        "width": w["width"],
        "width_a": w["width_a"],
        "width_b": w["width_b"],
        "width_agree": w["agree"],
        "rank": rk["rank"],
        "rank_a": rk["rank_a"],
        "rank_b": rk["rank_b"],
        "rank_agree": rk["agree"],
        "matrix_rows": len(mat),
        "matrix_cols": len(mat[0]) if mat else 0,
        "witness_ok": witness_ok,
        "twin_ok": bool(w["agree"] and rk["agree"] and witness_ok),
        "residuals": residuals,
    }


def clone_cons(constraints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return deepcopy(constraints)
