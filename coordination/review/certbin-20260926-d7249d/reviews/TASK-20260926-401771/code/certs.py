"""Boolean-ring arithmetic and certificate checkers for the J1 verifier.

B = F_2[v_0..v_19]/(v_i^2 + v_i). A polynomial is a dense uint8 array of
length 2^20 indexed by monomial mask (1 = coefficient 1). Multilinear
reduction is built in: the product of monomials a, b is the monomial a | b.
Every degree is the maximum popcount over the support AFTER reduction
(deg 0-polynomial = -1).

Formats (EXP-CERTBIN-060020 specification certificate_format):
  flat-v1: C = sorted list of (mu, k); claim sum mu*f_k = 1 in B.
  wdag-v1: nodes with rows [[mu, k]] and prods [[j, c]];
           poly(i) = sum mu*f_k + sum v_j * poly(c); rules (a)-(e).
  ann-v1:  L_hex functionals on B_{<=4} in ann_order(4, 20); (A1)-(A3).
"""
import numpy as np

import kern
import layout as LY

NPT = 1 << LY.NV


class System:
    """A system f_0..f_18 given as its 19 x 211 E matrix."""

    def __init__(self, E):
        self.E = E
        self.supp = LY.rows_as_masks(E)  # per k: int64 monomial masks
        self._m4 = None

    # ---------------------------------------------------------- ring ops
    def rows_poly(self, rows):
        """sum over (mu_mask, k) of mu * f_k, as a dense parity array."""
        parts = [self.supp[k] | mu for (mu, k) in rows if self.supp[k].size]
        if not parts:
            return np.zeros(NPT, dtype=np.uint8)
        idx = np.concatenate(parts)
        return (np.bincount(idx, minlength=NPT) & 1).astype(np.uint8)

    def m4_packed(self):
        """M_4: rows mu*f_k, mu over mu_order(2, 20) (211 monomials), row index
        mu_index * 19 + k (EXP-CERTBIN-4e92d7 convention), zero rows retained;
        columns in ann_order(4, 20). Returns packed uint64 (4009 x 97)."""
        if self._m4 is None:
            mus = [LY.mask_of(t) for t in LY.mu_order(2, LY.NV)]
            dense = np.zeros((len(mus) * LY.NEQ, LY.NCOL4), dtype=np.uint8)
            for a, mu in enumerate(mus):
                for k in range(LY.NEQ):
                    if self.supp[k].size == 0:
                        continue
                    cols = LY.ANN_COL_OF_MASK[self.supp[k] | mu]
                    assert (cols >= 0).all()
                    par = np.bincount(cols, minlength=LY.NCOL4) & 1
                    dense[a * LY.NEQ + k] = par
            self._m4 = kern.pack_rows(dense, LY.WORDS4)
        return self._m4


def times_vj(poly, j):
    nz = np.flatnonzero(poly)
    if nz.size == 0:
        return np.zeros(NPT, dtype=np.uint8)
    return (np.bincount(nz | (1 << j), minlength=NPT) & 1).astype(np.uint8)


def degree(poly):
    nz = np.flatnonzero(poly)
    return int(LY.POP[nz].max()) if nz.size else -1


def is_one(poly):
    nz = np.flatnonzero(poly)
    return nz.size == 1 and nz[0] == 0


def residual_summary(poly, target_one=True):
    """Residual = poly + 1 (if the target is 1): its size and 5 monomials."""
    r = poly.copy()
    if target_one:
        r[0] ^= 1
    nz = np.flatnonzero(r)
    mons = [sorted(i for i in range(LY.NV) if (int(m) >> i) & 1) for m in nz[:5]]
    return {"residual_size": int(nz.size), "residual_monomials_first5": mons}


def _mu_ok(mu):
    return (isinstance(mu, list) and all(isinstance(i, int) for i in mu)
            and all(0 <= i < LY.NV for i in mu) and all(mu[a] < mu[a + 1] for a in range(len(mu) - 1)))


# ------------------------------------------------------------------ flat-v1
def check_flat(sys, body):
    """Returns dict with identity verdict and counting admissibility."""
    out = {"format": "flat-v1"}
    C = body.get("C") if isinstance(body, dict) else None
    if not isinstance(C, list):
        out.update(verified=False, first_violated="format", note="no C list")
        return out
    fmt_err = []
    rows = []
    maxmu = -1
    for e in C:
        if not (isinstance(e, list) and len(e) == 2 and _mu_ok(e[0]) and isinstance(e[1], int)):
            fmt_err.append("malformed entry")
            continue
        mu, k = e
        if not (0 <= k < LY.NEQ):
            fmt_err.append("k out of range")
            continue
        maxmu = max(maxmu, len(mu))
        rows.append((LY.mask_of(mu), k))
    keyed = [(tuple(e[0]), e[1]) for e in C if isinstance(e, list) and len(e) == 2 and isinstance(e[0], list)]
    sorted_ok = keyed == sorted(keyed)
    dup = len(set(keyed)) != len(keyed)
    out["n_terms"] = len(C)
    out["max_mu"] = maxmu
    out["sorted"] = bool(sorted_ok)
    out["duplicates"] = bool(dup)
    if fmt_err:
        out.update(verified=False, first_violated="format", note=sorted(set(fmt_err)))
        return out
    p = sys.rows_poly(rows)
    ok = is_one(p)
    out["identity_holds"] = bool(ok)
    out["verified"] = bool(ok and not dup)
    if not ok:
        out["first_violated"] = "identity (sum != 1)"
        out.update(residual_summary(p))
    elif dup:
        out["first_violated"] = "format (duplicate pair)"
    out["counts_toward_M4"] = bool(out["verified"] and maxmu <= 2)
    out["counts_toward_W4"] = bool(out["verified"] and maxmu <= 2)
    return out


def check_flat_as_M4(sys, body):
    """A flat-v1 submitted as an M_4 refutation: must verify AND max|mu| <= 2."""
    r = check_flat(sys, body)
    acc = bool(r.get("verified") and r.get("max_mu", 99) <= 2)
    r["accepted_as_M4"] = acc
    if r.get("verified") and not acc:
        r["first_violated"] = "M_4 degree discipline (max |mu| > 2)"
    return r


# ------------------------------------------------------------------ wdag-v1
def check_wdag(sys, body, D=4, nv=20, neq=19):
    out = {"format": "wdag-v1"}
    viol = []
    if not isinstance(body, dict):
        return dict(out, verified=False, first_violated="format", violated=["format"])
    if body.get("D") != D or body.get("nv") != nv or body.get("neq") != neq:
        viol.append("header (D, nv, neq)")
    nodes = body.get("nodes")
    outp = body.get("output")
    if not isinstance(nodes, list) or not nodes or not isinstance(outp, int):
        return dict(out, verified=False, first_violated="format", violated=["format"])
    n = len(nodes)
    ids_ok = all(isinstance(nd, dict) and nd.get("id") == i for i, nd in enumerate(nodes))
    if not ids_ok:
        viol.append("format (node ids are not 0..n-1 in order)")
    polys = []
    degs = []
    depth = []
    maxmu = -1
    rule = {"a": [], "b": [], "c": [], "d": [], "e": []}
    for i, nd in enumerate(nodes):
        rows = []
        for e in nd.get("rows", []):
            if not (isinstance(e, list) and len(e) == 2 and _mu_ok(e[0]) and isinstance(e[1], int)):
                rule["b"].append((i, "malformed row"))
                continue
            mu, k = e
            maxmu = max(maxmu, len(mu))
            if len(mu) > 2:
                rule["b"].append((i, "|mu| = %d" % len(mu)))
            if not (0 <= k < neq):
                rule["b"].append((i, "k = %d" % k))
                continue
            rows.append((LY.mask_of(mu), k))
        p = sys.rows_poly(rows)
        dep = 0
        for e in nd.get("prods", []):
            if not (isinstance(e, list) and len(e) == 2 and all(isinstance(x, int) for x in e)):
                rule["a"].append((i, "malformed prod"))
                continue
            j, c = e
            if not (0 <= j < nv):
                rule["b"].append((i, "j = %d" % j))
                continue
            if not (0 <= c < i):
                rule["a"].append((i, "child %d not < %d" % (c, i)))
                continue
            if degs[c] > 3:
                rule["c"].append((i, "child %d has degree %d" % (c, degs[c])))
            p ^= times_vj(polys[c], j)
            dep = max(dep, depth[c] + 1)
        d = degree(p)
        if d > 4:
            rule["d"].append((i, "degree %d" % d))
        polys.append(p)
        degs.append(d)
        depth.append(dep)
    if not (0 <= outp < n):
        rule["e"].append(("output", "output id %s out of range" % outp))
        final = None
    else:
        final = polys[outp]
        if not is_one(final):
            rule["e"].append(("output", "poly(output) != 1"))
    violated = [r for r in "abcde" if rule[r]]
    fmt = [v for v in viol]
    out.update(
        n_nodes=n,
        max_prods_depth=int(max(depth) if depth else 0),
        max_node_degree=int(max(degs) if degs else -1),
        max_mu=maxmu,
        node_degrees=degs,
        violated=fmt + ["(%s)" % r for r in violated],
        verified=(not violated and not fmt),
    )
    if violated or fmt:
        out["first_violated"] = (fmt + ["(%s)" % r for r in violated])[0]
        out["rule_details"] = {r: [str(x) for x in rule[r][:5]] for r in violated}
        if final is not None and not is_one(final):
            out.update(residual_summary(final))
    return out


# ------------------------------------------------------------------ ann-v1
def lam_packed(L_hex):
    """L_hex -> packed uint64 (nL x 97), coordinate c at bit c (LSB first)."""
    nL = len(L_hex)
    buf = np.zeros((nL, LY.WORDS4 * 8), dtype=np.uint8)
    for i, h in enumerate(L_hex):
        v = int(h, 16)
        if v >> LY.NCOL4:
            raise ValueError("functional %d has a bit beyond coordinate 6195" % i)
        buf[i] = np.frombuffer(v.to_bytes(LY.WORDS4 * 8, "little"), dtype=np.uint8)
    return np.ascontiguousarray(buf.view(np.uint64))


def packed_to_hex(row_u64):
    return format(int.from_bytes(row_u64.tobytes(), "little"), "x")


def basis_S_deg3(Lp):
    """Basis K of S cap B_{<=3}, S = {g : lambda(g) = 0 for all lambda}, by own
    elimination on the restriction of L to the 1351 degree <= 3 coordinates.
    Returns (K packed in 6196-coordinates, rank of the restriction)."""
    dense = kern.unpack_rows(Lp, LY.NCOL4)[:, LY.DEG3_START:]
    n3 = dense.shape[1]  # 1351
    w3 = (n3 + 63) // 64
    R, r, piv = kern.rref(kern.pack_rows(dense, w3), n3)
    Rd = kern.unpack_rows(R[:r], n3)
    free = np.setdiff1d(np.arange(n3), piv)
    K = np.zeros((free.size, n3), dtype=np.uint8)
    K[np.arange(free.size), free] = 1
    if r:
        K[:, piv] = Rd[:, free].T
    full = np.zeros((free.size, LY.NCOL4), dtype=np.uint8)
    full[:, LY.DEG3_START:] = K
    return kern.pack_rows(full, LY.WORDS4), r


def check_ann(sys, body):
    out = {"format": "ann-v1"}
    if not isinstance(body, dict) or body.get("D") != 4 or body.get("nv") != 20 or body.get("neq") != 19:
        return dict(out, verified=False, first_violated="header")
    L_hex = body.get("L_hex")
    if not isinstance(L_hex, list) or not L_hex:
        return dict(out, verified=False, first_violated="format (empty L)")
    Lp = lam_packed(L_hex)
    out["size_L"] = int(Lp.shape[0])
    # (A1) every M_4 row in S
    M4 = sys.m4_packed()
    n1, first1, _ = kern.parity_check(Lp, M4)
    out["A1"] = {"pass": n1 == 0, "violations": int(n1),
                 "first_violation_row_functional": list(first1) if n1 else None}
    # dim S
    _, rankL, _ = kern.rref(Lp, LY.NCOL4)
    out["rank_L"] = int(rankL)
    out["dim_S"] = int(LY.NCOL4 - rankL)
    # (A2)
    Kp, r3 = basis_S_deg3(Lp)
    nchk, _, _ = kern.parity_check(Lp, Kp)  # sanity: K lies in S
    n2, first2, ovf = kern.closure_check(Lp, Kp, LY.NCOL4, LY.NV, LY.ANN_MASK_OF_COL, LY.ANN_COL_OF_MASK)
    out["dim_S_cap_B3"] = int(Kp.shape[0])
    out["A2"] = {"pass": n2 == 0 and ovf == 0 and nchk == 0, "violations": int(n2), "overflow": ovf,
                 "basis_sanity_violations": int(nchk),
                 "first_violation_basis_j_functional": list(first2) if n2 else None}
    # (A3)
    const_bits = [(int(h, 16) >> LY.CONST_COL) & 1 for h in L_hex]
    out["A3"] = {"pass": any(const_bits), "n_functionals_with_lambda1": int(sum(const_bits))}
    out["verified"] = bool(out["A1"]["pass"] and out["A2"]["pass"] and out["A3"]["pass"])
    if not out["verified"]:
        out["first_violated"] = [a for a in ("A1", "A2", "A3") if not out[a]["pass"]][0]
    return out
