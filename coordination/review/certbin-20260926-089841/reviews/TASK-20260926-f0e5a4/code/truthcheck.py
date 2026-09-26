"""Second, semantic verification route (truth tables), own code.

B = F_2[v_0..v_17]/(v_i^2 + v_i) is isomorphic to the ring of functions
{0,1}^18 -> F_2 (evaluation map; multilinear polynomials <-> truth tables).
So sum mu*f_k = 1 in B iff it equals 1 at all 2^18 assignments, and the degree
of an element is the maximum weight of its algebraic normal form (Moebius
transform of its truth table). This route uses no monomial product or
multilinear reduction code: it ANDs and XORs packed truth tables.
Imports nothing from this repository.
"""
import numpy as np

import evaluator as EV

NV = 18
NA = 1 << NV
NW = NA // 64
_U = np.arange(NA, dtype=np.int64)
_POP = np.array([bin(i).count("1") for i in range(NA)], dtype=np.int64)
ALL_ONES = np.full(NW, np.uint64(0xFFFFFFFFFFFFFFFF), dtype=np.uint64)
_mon_cache = {}


def mon_truth(m):
    t = _mon_cache.get(m)
    if t is None:
        t = np.packbits((_U & m) == m, bitorder="little").view("<u8").copy()
        _mon_cache[m] = t
    return t


def system_truth(rows):
    return [EV.row_truth(r) for r in rows]


def degree_of_truth(t):
    bits = np.unpackbits(t.view(np.uint8), bitorder="little").astype(np.uint8)
    a = bits
    for i in range(NV):
        step = 1 << i
        v = a.reshape(-1, 2 * step)
        v[:, step:] ^= v[:, :step]
    nz = np.flatnonzero(a)
    if nz.size == 0:
        return -1
    return int(_POP[nz].max())


def flat_identity(body, FT):
    acc = np.zeros(NW, dtype=np.uint64)
    for mu, k in body:
        m = 0
        for i in mu:
            m |= 1 << i
        acc ^= mon_truth(m) & FT[k]
    return bool(np.array_equal(acc, ALL_ONES))


def wdag_semantic(body, FT, D=4):
    """Identity and degree bounds by truth tables, in dependency order.
    Returns dict: evaluated, output_is_1, max node degree, max child degree,
    rule_c_ok, rule_d_ok."""
    byid = {nd["id"]: nd for nd in body["nodes"]}
    order = []
    state = {}
    cyc = [False]

    def visit(x):
        if state.get(x) == 2:
            return
        if state.get(x) == 1:
            cyc[0] = True
            return
        state[x] = 1
        for _, c in byid[x].get("prods", []):
            visit(c)
        state[x] = 2
        order.append(x)

    for x in sorted(byid):
        visit(x)
    if cyc[0]:
        return {"evaluated": False}
    T = {}
    deg = {}
    children = set()
    for i in order:
        nd = byid[i]
        acc = np.zeros(NW, dtype=np.uint64)
        for mu, k in nd.get("rows", []):
            m = 0
            for x in mu:
                m |= 1 << x
            acc ^= mon_truth(m) & FT[k]
        for j, c in nd.get("prods", []):
            children.add(c)
            acc ^= mon_truth(1 << j) & T[c]
        T[i] = acc
        deg[i] = degree_of_truth(acc)
    mcd = max([deg[c] for c in children], default=-1)
    return {"evaluated": True,
            "output_is_1": bool(np.array_equal(T[body["output"]], ALL_ONES)),
            "node_degrees": [deg[i] for i in sorted(deg)] if len(deg) <= 64 else None,
            "max_node_degree": max(deg.values()),
            "max_child_degree": mcd,
            "rule_c_ok": all(deg[c] <= D - 1 for c in children),
            "rule_d_ok": all(d <= D for d in deg.values())}
