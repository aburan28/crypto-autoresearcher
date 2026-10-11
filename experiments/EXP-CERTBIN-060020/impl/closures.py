"""Closures on the pinned engine (crypto_autoresearcher.gf2, imported, never
copied or edited) plus the n = 19-specific extractors:

* WdagClosure: a subclass of closure.Closure whose ``_extract`` hook also
  records the iteration structure and (on request) builds a general wdag-v1
  certificate by level-wise back-tracing, keeping v_j * (fallen row) products
  as DAG nodes instead of collapsing them into flat (mu, k) pairs. The W_D
  iteration itself (``_w_closure``) is the engine's, inherited unchanged.
* ell_route / ell-route wdag-v1: 1 in rowspace(M_4) + ell * B_{<=3}, with the
  prefix-shared chain construction v_{j1}(v_{j2}(v_{j3} ell)).
* ann-v1: a basis of the annihilator of the final W_4 basis (own RREF).
* rc_b: the ell-substituted closures R'_3, R'_4 (and W'_4).
"""
from __future__ import annotations

import threading

import numpy as np

import common  # noqa: F401  (puts src/ on sys.path)
from crypto_autoresearcher.gf2 import closure as gclosure
from crypto_autoresearcher.gf2 import kernels


def popcount(x):
    return bin(x).count("1")


def mask_to_list(m):
    out = []
    i = 0
    while m:
        if m & 1:
            out.append(i)
        m >>= 1
        i += 1
    return out


# ---------------------------------------------------------------------------
# general wdag-v1 via the engine's own iteration
# ---------------------------------------------------------------------------
class WdagClosure(gclosure.Closure):
    """closure.Closure with an extraction hook (engine iteration unchanged)."""

    want_general_wdag = True

    def _extract(self, itl, pstar):
        flat = super()._extract(itl, pstar)
        info = {"depth": len(itl) - 1,
                "nb_per_level": [None] + [int(it["origin"]["nb"]) for it in itl[1:]]}
        wd = None
        if len(itl) > 1 and self.want_general_wdag:
            wd = self._wdag(itl, pstar)
        self._last_extract = {"info": info, "wdag": wd}
        return flat

    def _wdag(self, itl, pstar):
        """Grouped construction (specification certificate_format, recommended
        construction): an element of W^(i) is (basis rows of iteration i-1)
        + sum_j v_j * (sum of the fallen basis rows of iteration i-1 used with
        j); each group sum_j is ONE node (degree <= D-1, as a sum of rows with
        degree-<=D-1 leads) and is expanded recursively; the basis part of a
        node is expanded into the same node. Level 0 gives Macaulay rows."""
        top = len(itl) - 1
        nodes = {}
        OUT = ("out",)
        seq = [0]

        def new_node(key, level):
            nodes[key] = {"level": level, "seq": seq[0], "rows": {}, "prods": {}}
            seq[0] += 1

        new_node(OUT, top)
        pending = {top: {OUT: {int(pstar)}}}
        for level in range(top, -1, -1):
            tg = pending.pop(level, {})
            tg = {k: v for k, v in tg.items() if v}
            if not tg:
                continue
            keys = list(tg)
            nt = len(keys)
            nw = (nt + 63) // 64
            nrows = self._nrows(itl, level)
            S = np.zeros((nrows, nw), dtype=np.uint64)
            for t, key in enumerate(keys):
                for r in tg[key]:
                    S[r, t >> 6] ^= np.uint64(1 << (t & 63))
            kernels.backtrace(itl[level]["log"], S)
            org = itl[level]["origin"]
            nxt = pending.setdefault(level - 1, {}) if level > 0 else None
            for r in np.flatnonzero(S.any(axis=1)).tolist():
                for w in range(nw):
                    word = int(S[r, w])
                    while word:
                        b = (word & -word).bit_length() - 1
                        word &= word - 1
                        key = keys[w * 64 + b]
                        node = nodes[key]
                        if org is None:
                            mu, k = self.row_pair(r)
                            pk = (mu, k)
                            node["rows"][pk] = node["rows"].get(pk, 0) ^ 1
                        elif r < org["nb"]:
                            pr = int(org["prow"][r])
                            s = nxt.setdefault(key, set())
                            s ^= {pr}
                        else:
                            j, f = divmod(r - org["nb"], org["nnew"])
                            x = int(org["newrows"][f])
                            ck = ("g", key, j, level - 1)
                            if ck not in nodes:
                                new_node(ck, level - 1)
                                node["prods"][(j, ck)] = 1
                            nxt.setdefault(ck, set()).symmetric_difference_update({x})
        order = sorted((k for k in nodes if k != OUT), key=lambda k: (nodes[k]["level"], nodes[k]["seq"]))
        order.append(OUT)
        ids = {k: i for i, k in enumerate(order)}
        out_nodes = []
        for k in order:
            nd = nodes[k]
            rows = sorted([mask_to_list(mu), kk] for (mu, kk), p in nd["rows"].items() if p)
            prods = sorted([j, ids[c]] for (j, c), p in nd["prods"].items() if p)
            out_nodes.append({"id": ids[k], "rows": rows, "prods": prods})
        return {"D": self.D, "nv": self.nv, "neq": self.neq, "nodes": out_nodes,
                "output": ids[OUT]}


# ---------------------------------------------------------------------------
# per-thread closure objects (Closure keeps per-call state in self._final)
# ---------------------------------------------------------------------------
_tls = threading.local()


def get_closure(nv, D, neq, wdag=False):
    cache = getattr(_tls, "cache", None)
    if cache is None:
        cache = _tls.cache = {}
    key = (nv, D, neq, wdag)
    if key not in cache:
        cache[key] = (WdagClosure if wdag else gclosure.Closure)(nv, D, neq)
    return cache[key]


def flat_to_json(cert):
    return gclosure.cert_to_json(cert)


def flat_maxdeg(cert):
    return max((popcount(mu) for mu, k in cert), default=0)


# ---------------------------------------------------------------------------
# ell route
# ---------------------------------------------------------------------------
def ell_masks_from_row(ell_row, masks):
    return [int(masks[c]) for c in np.flatnonzero(ell_row)]


def ell_route(cl, eqs, ell_masks, cvec, want_cert=True):
    """Is 1 in rowspace(M_4) + ell * B_{<=3}? cl: Closure(nv, 4, neq).
    Returns (bool, wdag-v1 or None). cvec: int bitmask with ell = sum c_k f_k."""
    M4 = cl.build_M(eqs)
    low_cols = np.flatnonzero(cl.col_deg <= cl.D - 1)
    low_masks = cl.col_mask[low_cols]
    nlow = len(low_cols)
    ext = np.zeros((nlow, cl.W), dtype=np.uint64)
    em = np.asarray(ell_masks, dtype=np.int64)
    rr = np.repeat(np.arange(nlow), len(em))
    cc = cl.mask2col[(low_masks[:, None] | em[None, :]).ravel()]
    assert np.all(cc >= 0)
    np.bitwise_xor.at(ext, (rr, cc >> 6), np.left_shift(np.uint64(1), (cc & 63).astype(np.uint64)))
    Mst = np.ascontiguousarray(np.concatenate([M4, ext]))
    log = kernels.column_pass(Mst, cl.C, keep_ops=want_cert)
    cs = log.cs
    hit = np.flatnonzero(cs == cl.const_col)
    if not hit.size:
        return False, None
    if not want_cert:
        return True, None
    pstar = int(log.ps[hit[0]])
    S = np.zeros((Mst.shape[0], 1), dtype=np.uint64)
    S[pstar, 0] = np.uint64(1)
    kernels.backtrace(log, S)
    used = np.flatnonzero(S[:, 0]).tolist()
    flat = {}
    ell_mons = []
    for r in used:
        if r < cl.R:
            mu, k = cl.row_pair(r)
            flat[(mu, k)] = flat.get((mu, k), 0) ^ 1
        else:
            ell_mons.append(int(low_masks[r - cl.R]))
    return True, _ell_wdag(cl, flat, ell_mons, cvec)


def _ell_wdag(cl, flat, ell_mons, cvec):
    nodes = []
    ell_rows = [[[], k] for k in range(cl.neq) if (cvec >> k) & 1]
    nodes.append({"id": 0, "rows": ell_rows, "prods": []})
    single, pair = {}, {}
    out_prods = {}
    out_rows = dict(flat)
    for m in ell_mons:
        vs = mask_to_list(m)
        if len(vs) == 0:
            for k in range(cl.neq):
                if (cvec >> k) & 1:
                    out_rows[(0, k)] = out_rows.get((0, k), 0) ^ 1
            continue
        if len(vs) == 1:
            pk = (vs[0], ("ell",))
        elif len(vs) == 2:
            single.setdefault(vs[1], None)
            pk = (vs[0], ("s", vs[1]))
        else:
            single.setdefault(vs[2], None)
            pair.setdefault((vs[1], vs[2]), None)
            pk = (vs[0], ("p", vs[1], vs[2]))
        out_prods[pk] = out_prods.get(pk, 0) ^ 1
    ids = {("ell",): 0}
    for j3 in sorted(single):
        ids[("s", j3)] = len(nodes)
        nodes.append({"id": len(nodes), "rows": [], "prods": [[j3, 0]]})
    for (j2, j3) in sorted(pair):
        ids[("p", j2, j3)] = len(nodes)
        nodes.append({"id": len(nodes), "rows": [], "prods": [[j2, ids[("s", j3)]]]})
    rows = sorted([mask_to_list(mu), k] for (mu, k), p in out_rows.items() if p)
    prods = sorted([j, ids[c]] for (j, c), p in out_prods.items() if p)
    oid = len(nodes)
    nodes.append({"id": oid, "rows": rows, "prods": prods})
    return {"D": cl.D, "nv": cl.nv, "neq": cl.neq, "nodes": nodes, "output": oid}


def flat_as_wdag(cl, cert):
    """A flat certificate with max |mu| <= D - 2 as a one-node wdag-v1."""
    rows = sorted([mask_to_list(mu), k] for mu, k in cert)
    return {"D": cl.D, "nv": cl.nv, "neq": cl.neq,
            "nodes": [{"id": 0, "rows": rows, "prods": []}], "output": 0}


# ---------------------------------------------------------------------------
# ann-v1: annihilator of the final W_D basis (own RREF)
# ---------------------------------------------------------------------------
def rref_from_echelon(basis, leads, C):
    """basis (n x W uint64) in echelon form with distinct leads (lowest set
    column = lead). Returns a fully reduced copy (own back-substitution)."""
    R = basis.copy()
    leads = np.asarray(leads, dtype=np.int64)
    order = np.argsort(-leads, kind="stable")  # descending lead column
    for t in order.tolist():
        c = int(leads[t])
        w, b = c >> 6, np.uint64(c & 63)
        col = (R[:, w] >> b) & np.uint64(1)
        col[t] = 0
        hit = np.flatnonzero(col)
        if hit.size:
            R[hit] ^= R[t]
    return R


def annihilator(basis, leads, C):
    """Basis of {lambda : lambda(g) = 0 for g in rowspace(basis)} as a list of
    hex strings (bit c = value on column c)."""
    R = rref_from_echelon(basis, leads, C)
    W = R.shape[1]
    b = R.view(np.uint8).reshape(R.shape[0], W * 8)
    Ru = np.unpackbits(b, axis=1, bitorder="little")[:, :C]
    leads = np.asarray(leads, dtype=np.int64)
    piv = np.zeros(C, dtype=bool)
    piv[leads] = True
    free = np.flatnonzero(~piv)
    Lu = np.zeros((free.size, C), dtype=np.uint8)
    Lu[np.arange(free.size), free] = 1
    Lu[:, leads] = Ru[:, free].T
    pad = W * 64 - C
    if pad:
        Lu = np.concatenate([Lu, np.zeros((Lu.shape[0], pad), np.uint8)], axis=1)
    packed = np.packbits(Lu, axis=1, bitorder="little")
    return [format(int.from_bytes(row.tobytes(), "little"), "x") for row in packed]


# ---------------------------------------------------------------------------
# convenience: all closures of one system
# ---------------------------------------------------------------------------
def macaulay(nv, D, neq, eqs, want_cert=True):
    cl = get_closure(nv, D, neq)
    return cl.macaulay_closure(eqs, want_cert=want_cert)


def w_closure(nv, D, neq, eqs, want_cert=True, general_wdag=True):
    cl = get_closure(nv, D, neq, wdag=True)
    cl._last_extract = None
    cl.want_general_wdag = general_wdag
    rec, flat = cl.w_closure(eqs, want_cert=want_cert)
    ext = cl._last_extract
    final = cl._final
    return rec, flat, ext, final, cl
