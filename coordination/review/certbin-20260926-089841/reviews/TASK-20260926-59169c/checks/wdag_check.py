#!/usr/bin/env python3
"""TASK-20260926-59169c -- own minimal wdag-v1 / flat-v1 checker (CP-3).

Written from EXP-CERTBIN-ddfe75 specification.yaml object.certificate_format
and object.E_layout ONLY, before reading any code of TASK-20260926-83cebf,
TASK-20260926-f0e5a4, impl/, verifier/ or src/crypto_autoresearcher/.
Standard library only.

Ring B = F_2[v_0..v_17]/(v_i^2 + v_i). A multilinear monomial is an int bitmask
(bit i = v_i present); a polynomial is a Python set of such masks (the monomials
with coefficient 1). Addition is symmetric difference; the product of two
monomials is the bitwise OR (v^2 = v).

wdag-v1: {"D": 4, "nv": 18, "nodes": [{"id": i, "rows": [[mu, k], ...],
"prods": [[j, c], ...]}, ...], "output": o}
poly(i) = sum_{(mu,k) in rows} mu*f_k + sum_{(j,c) in prods} v_j * poly(c).
VALID iff (a) every child c < i; (b) every |mu| <= D-2 = 2 and every k in 0..16;
(c) every child c used in prods has deg poly(c) <= D-1 = 3; (d) every node has
deg poly(i) <= D; (e) poly(output) == 1.
Structural preconditions checked first and reported as rule "(fmt)": D == 4,
nv == 18, node ids are 0..N-1 in list order (or at least unique), every mu is a
list of distinct ints in 0..17, every j in 0..17, every child id exists, output
exists.
"""
import itertools

NV = 18
NEQ = 17


def mu_order2():
    """Columns of E_layout: mu_order(2, 18): degree ascending, then ascending
    sorted index tuple. col 0 = (), 1..18 = (i,), 19..171 = (i, j), i < j."""
    cols = [()]
    cols += [(i,) for i in range(NV)]
    cols += list(itertools.combinations(range(NV), 2))
    assert len(cols) == 172
    return cols


COLS = mu_order2()
COL_MASK = [sum(1 << i for i in c) for c in COLS]


def decode_E_hex_row(h):
    """E_hex row: hex integer, bit j (LSB first) = column j."""
    x = int(h, 16) if isinstance(h, str) else int(h)
    if x >> 172:
        raise ValueError("row has bits beyond column 171")
    out = set()
    j = 0
    while x:
        if x & 1:
            out.add(COL_MASK[j])
        x >>= 1
        j += 1
    return out


def system_from_hex(rows):
    assert len(rows) == NEQ
    return [decode_E_hex_row(h) for h in rows]


def system_from_monomial_lists(eqs):
    """blind-inputs.json: each equation is a list of monomials, each an
    ascending list of variable indices ([] = 1). Repeated monomials cancel."""
    assert len(eqs) == NEQ
    F = []
    for eq in eqs:
        s = set()
        for mono in eq:
            m = 0
            for i in mono:
                assert 0 <= i < NV
                m |= 1 << i
            s ^= {m}
        F.append(s)
    return F


def system_to_colbits(F):
    """Back to E_layout ints (for decoded-matrix comparison)."""
    idx = {m: j for j, m in enumerate(COL_MASK)}
    out = []
    for s in F:
        x = 0
        for m in s:
            if m not in idx:
                raise ValueError("monomial of degree > 2 in a system")
            x |= 1 << idx[m]
        out.append(x)
    return out


def deg(p):
    return max((bin(m).count("1") for m in p), default=-1)  # deg 0 = -1


def mu_mask(mu):
    m = 0
    for i in mu:
        m |= 1 << i
    return m


def _toggle_into(acc, it):
    for x in it:
        if x in acc:
            acc.remove(x)
        else:
            acc.add(x)


def check_wdag(cert, F, D_expected=4):
    """Return (status, detail). status in {'valid', 'invalid'}; detail names the
    first violated rule in the order (fmt), (a), (b), (c), (d), (e) as they are
    met while evaluating nodes in list order; (e) last."""
    if cert.get("D") != D_expected:
        return "invalid", {"rule": "(fmt)", "why": "D != %d" % D_expected}
    if cert.get("nv") != NV:
        return "invalid", {"rule": "(fmt)", "why": "nv != 18"}
    D = D_expected
    nodes = cert.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return "invalid", {"rule": "(fmt)", "why": "no nodes"}
    ids = [nd.get("id") for nd in nodes]
    if len(set(ids)) != len(ids):
        return "invalid", {"rule": "(fmt)", "why": "duplicate node id"}
    ids_in_order = ids == list(range(len(nodes)))
    polys = {}
    degs = {}
    max_child_deg = -1
    max_mu = 0
    n_rows = 0
    n_prods = 0
    for nd in nodes:
        i = nd["id"]
        rows = nd.get("rows", [])
        prods = nd.get("prods", [])
        # (a) topological order
        for pr in prods:
            if len(pr) != 2:
                return "invalid", {"rule": "(fmt)", "why": "prod not [j, c]", "node": i}
            j, c = pr
            if not isinstance(c, int) or c not in set(ids):
                return "invalid", {"rule": "(fmt)", "why": "unknown child", "node": i}
            if not (c < i):
                return "invalid", {"rule": "(a)", "node": i, "child": c}
            if c not in polys:
                # child id smaller but not yet evaluated (list order differs from id order)
                return "invalid", {"rule": "(a)", "node": i, "child": c, "why": "child not earlier in list"}
            if not (isinstance(j, int) and 0 <= j < NV):
                return "invalid", {"rule": "(fmt)", "why": "bad j", "node": i}
        # (b) rows
        acc = set()
        for rw in rows:
            if len(rw) != 2:
                return "invalid", {"rule": "(fmt)", "why": "row not [mu, k]", "node": i}
            mu, k = rw
            if not isinstance(mu, list) or any((not isinstance(t, int)) or t < 0 or t >= NV for t in mu) or len(set(mu)) != len(mu):
                return "invalid", {"rule": "(fmt)", "why": "bad mu", "node": i}
            if len(mu) > D - 2:
                return "invalid", {"rule": "(b)", "node": i, "why": "|mu| = %d" % len(mu)}
            if not (isinstance(k, int) and 0 <= k < NEQ):
                return "invalid", {"rule": "(b)", "node": i, "why": "k = %r" % (k,)}
            max_mu = max(max_mu, len(mu))
            mm = mu_mask(mu)
            _toggle_into(acc, (m | mm for m in F[k]))
            n_rows += 1
        # (c) children degree, then products
        for j, c in prods:
            if degs[c] > D - 1:
                return "invalid", {"rule": "(c)", "node": i, "child": c, "child_deg": degs[c]}
            max_child_deg = max(max_child_deg, degs[c])
            vj = 1 << j
            _toggle_into(acc, (m | vj for m in polys[c]))
            n_prods += 1
        di = deg(acc)
        # (d) node degree
        if di > D:
            return "invalid", {"rule": "(d)", "node": i, "deg": di}
        polys[i] = acc
        degs[i] = di
    o = cert.get("output")
    if o not in polys:
        return "invalid", {"rule": "(fmt)", "why": "output id missing"}
    # (e)
    if polys[o] != {0}:
        p = polys[o]
        return "invalid", {"rule": "(e)", "residual_terms": len(p ^ {0}), "residual_deg": deg(p ^ {0})}
    return "valid", {"nodes": len(nodes), "ids_in_list_order": ids_in_order, "rows": n_rows,
                     "prods": n_prods, "max_mu": max_mu, "max_child_deg": max_child_deg,
                     "max_node_deg": max(degs.values())}


def check_flat(C, F):
    """flat-v1: C = list of [mu, k]; claim sum mu*f_k = 1. Returns (verified, max|mu|)."""
    acc = set()
    mx = 0
    for mu, k in C:
        mx = max(mx, len(mu))
        mm = mu_mask(mu)
        _toggle_into(acc, (m | mm for m in F[k]))
    return acc == {0}, mx


def eval_system(F, x):
    """Evaluate all f_k at an 18-bit assignment x (bit i = v_i). Returns list of bits."""
    return [sum(1 for m in fk if (m & x) == m) & 1 for fk in F]


# ---------------------------------------------------------------- self-test
def _selftest():
    import random
    rnd = random.Random(59169)
    # random quadratic system with a planted solution x0 -> build a sum that is
    # NOT 1; and a trivially refutable system f_0 = 1 to test (e) positive.
    F = [set() for _ in range(NEQ)]
    F[0] = {0}  # f_0 = 1
    for k in range(1, NEQ):
        F[k] = {COL_MASK[rnd.randrange(172)] for _ in range(20)}
    ok = check_wdag({"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[], 0]], "prods": []}], "output": 0}, F)
    assert ok[0] == "valid", ok
    # two-node: node0 = v_3*f_0 = v_3 ; node1 = f_0 + v_3*node0 + v_3*node0 -> 1 (prods cancel)
    c = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[3], 0]], "prods": []},
                                     {"id": 1, "rows": [[[], 0]], "prods": [[3, 0], [3, 0]]}], "output": 1}
    assert check_wdag(c, F)[0] == "valid"
    # (a) violation
    c2 = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[], 0]], "prods": [[1, 1]]},
                                      {"id": 1, "rows": [[[], 0]], "prods": []}], "output": 0}
    assert check_wdag(c2, F)[1]["rule"] in ("(a)",), check_wdag(c2, F)
    # (b) violation
    c3 = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[1, 2, 3], 0], [[1, 2, 3], 0], [[], 0]], "prods": []}], "output": 0}
    assert check_wdag(c3, F)[1]["rule"] == "(b)"
    c3b = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[], 17]], "prods": []}], "output": 0}
    assert check_wdag(c3b, F)[1]["rule"] == "(b)"
    # (c) violation: child of degree 4 used in a prod (v1v2v3v4 * f_0 via two deg-2 rows impossible
    # under (b); build child = v1v2*F[k] could be deg 4)
    k4 = next(k for k in range(1, NEQ) if deg(F[k]) == 2)
    mono2 = next(m for m in F[k4] if bin(m).count("1") == 2)
    a, b = [i for i in range(NV) if mono2 >> i & 1]
    others = [i for i in range(NV) if i not in (a, b)][:2]
    child = {"id": 0, "rows": [[others, k4]], "prods": []}
    # child degree is 4 unless cancellation; find one that is deg 4
    c4 = {"D": 4, "nv": 18, "nodes": [child, {"id": 1, "rows": [[[], 0]], "prods": [[5, 0]]}], "output": 1}
    r4 = check_wdag(c4, F)
    assert r4[0] == "invalid" and r4[1]["rule"] == "(c)", r4
    # (d) violation: node of degree 5 = v_j * (deg-4 poly) with j outside -> caught by (c) first;
    # construct (d) directly: impossible with (b),(c) and D=4 (deg <= max(4, 1+3) = 4). So (d) is
    # implied by (b)+(c) for these inputs; tested by D=3 variant.
    c5 = {"D": 3, "nv": 18, "nodes": [child], "output": 0}
    r5 = check_wdag(c5, F, D_expected=3)
    assert r5[0] == "invalid" and r5[1]["rule"] in ("(b)", "(d)"), r5
    # (e) violation
    c6 = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[], 1]], "prods": []}], "output": 0}
    assert check_wdag(c6, F)[1]["rule"] == "(e)"
    # decode round trip
    for _ in range(50):
        rows = [format(rnd.getrandbits(172), "x") for _ in range(NEQ)]
        G = system_from_hex(rows)
        assert [format(x, "x") for x in system_to_colbits(G)] == rows
    # eval: f_0 = 1 never vanishes
    assert eval_system(F, 0)[0] == 1
    return True


if __name__ == "__main__":
    print("selftest", _selftest())
