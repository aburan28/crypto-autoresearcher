"""Certificate construction (TASK-20260926-f0736e).

wdag-v1 (1 in W_4) and ann-v1 (1 not in W_4) in the frozen formats of
EXP-CERTBIN-060020 object.certificate_format.  Construction is free ("obtain
them however you like"); validity is decided by checkers.py, which shares no
code with this module or with algebra.py.

wdag-v1 construction ("collapse per variable"):
  Level 0 is rowspace(M_4) with every echelon row tagged by the M_4 rows it is
  a sum of.  Level i >= 1 is rebuilt from the generators
      M_4 rows  and  v_j * b  (b in B_{i-1}, j = 0..19),
  where B_{i-1} is the set of level-(i-1) echelon rows with leading degree
  <= 3 (a basis of W^(i-1) cap B_{<=3}).  Its span is W^(i) (checked against
  the literal iteration's dims).  Tags are carried over the INDEPENDENT
  generators only (found by an untagged first pass), so they stay <= 6196 +
  4009 bits.  The constant 1 is reduced against level L (the first iteration
  containing 1): 1 = sum(M_4 rows) + sum_j v_j a_j with a_j in span(B_{L-1}).
  Each a_j becomes one node, expressed the same way one level down, and so on
  to level 0 (rows only).  All node polynomials have degree <= 3 except the
  output, which is 1.
"""
from collections import defaultdict

import numpy as np

import algebra as G


def _bits(tag):
    u = np.unpackbits(np.ascontiguousarray(tag).view(np.uint8), bitorder="little")
    return np.flatnonzero(u)


def build_levels(M4, cols, L, wdims, nv=G.NV, D=4):
    """Tagged levels 0..L.  Returns list of dicts with keys bas (tagged
    Basis), low (row indices with lead deg <= 3), gens (list: tag bit ->
    ('row', r) or ('prod', j, position-in-low-of-previous-level))."""
    nrows = M4.shape[0]
    lev0 = G.Basis(cols, tagbits=nrows)
    res0 = lev0.insert(M4, tagidx=np.arange(nrows, dtype=np.int32))
    if lev0.rank != wdims[0]:
        raise AssertionError("level 0 rank %d != literal dim %d" % (lev0.rank, wdims[0]))
    indep_rows = np.flatnonzero(res0 >= 0)
    untagged0 = G.Basis(cols)
    untagged0.insert(M4[indep_rows])
    levels = [{"bas": lev0, "low": lev0.low_rows(D - 1), "gens": None}]
    for i in range(1, L + 1):
        prev = levels[-1]
        Bprev = prev["bas"].rows[prev["low"]]
        nb = Bprev.shape[0]
        prods = np.concatenate([G.mul_var_packed(Bprev, cols, cols, j) for j in range(nv)], axis=0)
        prod_ids = [(j, p) for j in range(nv) for p in range(nb)]
        U = untagged0.copy()
        r = U.insert(prods)
        if U.rank != wdims[i]:
            raise AssertionError("level %d rank %d != literal dim %d" % (i, U.rank, wdims[i]))
        indep = np.flatnonzero(r >= 0)
        T = G.Basis(cols, tagbits=nrows + len(indep))
        T.insert(M4[indep_rows], tagidx=indep_rows.astype(np.int32))
        T.insert(prods[indep], tagidx=(nrows + np.arange(len(indep))).astype(np.int32))
        if T.rank != U.rank:
            raise AssertionError("tagged level %d rank mismatch" % i)
        gens = {nrows + q: ("prod",) + prod_ids[int(p)] for q, p in enumerate(indep)}
        levels.append({"bas": T, "low": T.low_rows(D - 1), "gens": gens})
    return levels


def build_wdag(label, eqs, M4, row_labels, cols, wrec, nv=G.NV, neq=G.NEQ, D=4):
    L = wrec["one_first_iteration"]
    if L is None:
        raise ValueError("not refuted")
    levels = build_levels(M4, cols, L, wrec["dims"], nv, D)
    nrows = M4.shape[0]
    one = np.zeros((1, cols.nw), dtype=np.uint64)
    c = cols.const_col
    one[0, c >> 6] = np.uint64(1) << np.uint64(c & 63)
    top = levels[L]["bas"]
    rem, lead, T = top.reduce(one, with_tags=True)
    if lead[0] != -1:
        raise AssertionError("1 not in level %d" % L)
    nodes = []
    memo = {}

    def node_for(level, tag):
        key = (level, np.ascontiguousarray(tag).tobytes())
        if key in memo:
            return memo[key]
        bits = _bits(tag)
        rows = []
        groups = defaultdict(list)
        for b in bits:
            b = int(b)
            if b < nrows:
                mu, k = row_labels[b]
                rows.append([G.mask_to_tuple(mu), int(k)])
            else:
                g = levels[level]["gens"][b]
                _, j, p = g
                groups[j].append(p)
        prods = []
        if groups:
            prev = levels[level - 1]
            for j in sorted(groups):
                ridx = prev["low"][np.array(groups[j], dtype=np.int64)]
                ctag = np.bitwise_xor.reduce(prev["bas"].tags[ridx], axis=0)
                cid = node_for(level - 1, ctag)
                prods.append([int(j), int(cid)])
        nid = len(nodes)
        nodes.append({"id": nid, "rows": rows, "prods": prods})
        memo[key] = nid
        return nid

    out = node_for(L, T[0])
    cert = {"label": label, "D": D, "nv": nv, "neq": neq, "nodes": nodes, "output": out}
    stats = {"nodes": len(nodes), "row_entries": sum(len(n["rows"]) for n in nodes),
             "prod_entries": sum(len(n["prods"]) for n in nodes), "depth": L}
    return cert, stats


def annihilator(basW):
    """Basis of the annihilator of the row space: for the RREF with pivot set
    P and free set Fr, lambda_f = e_f + sum_{p} R[p, f] e_p."""
    b = basW.copy()
    b.full_reduce()
    n = b.cols.n
    rank = b.rank
    R = G.unpack_rows(b.rows[:rank], n)
    piv = b.lead[:rank].astype(np.int64)
    free = np.setdiff1d(np.arange(n), piv)
    Lm = np.zeros((free.size, n), dtype=np.uint8)
    Lm[np.arange(free.size), free] = 1
    Lm[:, piv] = R[:, free].T
    return Lm


def hex_rows(Lm):
    out = []
    n = Lm.shape[1]
    nb = (n + 7) // 8
    pad = np.zeros((Lm.shape[0], nb * 8), dtype=np.uint8)
    pad[:, :n] = Lm
    by = np.packbits(pad, axis=1, bitorder="little")
    for row in by:
        out.append(format(int.from_bytes(row.tobytes(), "little"), "x"))
    return out


def build_ann(label, basW, nv=G.NV, neq=G.NEQ):
    Lm = annihilator(basW)
    cert = {"label": label, "D": 4, "nv": nv, "neq": neq, "L_hex": hex_rows(Lm)}
    stats = {"functionals": int(Lm.shape[0]), "density": float(Lm.mean()) if Lm.size else 0.0}
    return cert, stats, Lm
