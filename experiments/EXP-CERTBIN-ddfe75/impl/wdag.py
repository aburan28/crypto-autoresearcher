"""wdag-v1 extractor for W_D refutations (specification object.certificate_format).

`WDagClosure` subclasses the engine's closure.Closure (imported, not copied)
and re-runs the documented W_D iteration (EXP-CERTBIN-e94b27 object
mutant_closure_W_D) with the engine's kernels.* primitives (column_pass,
products, backtrace), keeping the op log of every iteration up to the first
one whose row space contains 1. Its iteration dimensions are compared with the
engine's own w_closure record by the driver (C-WDAG).

Structure used (the specification's recommended construction):
  stack_0 = M_D;  stack_l = [basis_{l-1} ; v_j * newfallen_{l-1} (j-major)].
A set T of final-state rows of level l is backtraced through log_l to rows of
stack_l. Rows of M_D become (mu, k) pairs of the node; basis rows of level
l-1 are expanded INLINE into the same node (they are again final-state rows
of level l-1); the fallen rows used with v_j form ONE child node per j at
level l-1 (its polynomial is a sum of reduced rows whose leading monomial has
degree <= D-1, so the polynomial has degree <= D-1), with a prods entry
(j, child). Every node's polynomial is a sum of final-state rows of its level
(degree <= D). Node ids are assigned children-first, the output last.
"""
from __future__ import annotations

import numpy as np

from crypto_autoresearcher.gf2 import closure, kernels


class WDagClosure(closure.Closure):

    def iterate(self, eqs):
        """Run the W_D iteration to the fixpoint; keep op logs up to the first
        iteration containing 1. -> (dims, one_first, levels)."""
        D = self.D
        M = self.build_M(eqs)
        log = kernels.column_pass(M, self.C, keep_ops=True)
        levels = [{"log": log, "origin": None, "nrows": int(M.shape[0])}]
        ps, cs = log.ps.astype(np.int64), log.cs.astype(np.int64)
        dims = [int(ps.size)]
        one_first = 0 if self.const_col in set(cs.tolist()) else None
        prev_low = set()
        it = 0
        while True:
            order = np.argsort(cs, kind="stable")
            prow = ps[order]
            leads = cs[order]
            basis = M[prow]
            low = self.col_deg[leads] <= D - 1
            lowidx = np.flatnonzero(low)
            new = np.array([t for t in lowidx if int(leads[t]) not in prev_low], dtype=np.int64)
            prev_low = set(int(x) for x in leads[low])
            P = self.products(basis[new])
            M = np.concatenate([basis, P])
            del P
            keep = one_first is None
            log2 = kernels.column_pass(M, self.C, keep_ops=keep)
            ps2, cs2 = log2.ps.astype(np.int64), log2.cs.astype(np.int64)
            if keep:
                levels.append({"log": log2, "nrows": int(M.shape[0]),
                               "origin": {"nb": int(prow.size), "prow": prow,
                                          "newrows": prow[new], "nnew": int(new.size)}})
            if ps2.size == dims[-1]:
                break
            it += 1
            dims.append(int(ps2.size))
            if one_first is None and self.const_col in set(cs2.tolist()):
                one_first = it
            ps, cs = ps2, cs2
        if one_first is not None:
            levels = levels[:one_first + 1]
        else:
            levels = None
        return dims, one_first, levels

    def extract(self, levels):
        """-> wdag-v1 dict for the refutation at depth len(levels)-1."""
        Lv = len(levels) - 1
        top = levels[Lv]["log"]
        cs = top.cs
        k1 = int(np.flatnonzero(cs == self.const_col)[0])
        pstar = int(top.ps[k1])
        nodes = []  # creation order; each {"rows": {(mu,k): 1}, "prods": [(j, node_idx)]}
        nodes.append({"rows": {}, "prods": []})
        items = [(0, [pstar])]  # (node index, list of final-state rows at this level)
        for lev in range(Lv, -1, -1):
            if not items:
                break
            L = levels[lev]
            ntag = len(items)
            nw = (ntag + 63) // 64
            S = np.zeros((L["nrows"], nw), dtype=np.uint64)
            for t, (_, rows) in enumerate(items):
                w, b = t >> 6, np.uint64(1 << (t & 63))
                for r in rows:
                    S[r, w] ^= b
            kernels.backtrace(L["log"], S)
            nz = np.flatnonzero(S.any(axis=1))
            per_tag = [[] for _ in range(ntag)]
            Sn = S[nz]
            for t in range(ntag):
                w, b = t >> 6, np.uint64(1 << (t & 63))
                sel = (Sn[:, w] & b) != 0
                per_tag[t] = nz[sel].tolist()
            nxt = []
            org = L["origin"]
            for t, (nd, _) in enumerate(items):
                orig = per_tag[t]
                if org is None:
                    rd = nodes[nd]["rows"]
                    for r in orig:
                        mu, k = self.row_pair(r)
                        key = (mu, k)
                        if key in rd:
                            del rd[key]
                        else:
                            rd[key] = 1
                    continue
                nb, nnew = org["nb"], org["nnew"]
                basis_rows = []
                byj = {}
                for r in orig:
                    if r < nb:
                        basis_rows.append(int(org["prow"][r]))
                    else:
                        j, f = divmod(r - nb, nnew)
                        byj.setdefault(j, []).append(int(org["newrows"][f]))
                if basis_rows:
                    nxt.append((nd, basis_rows))
                for j in sorted(byj):
                    ci = len(nodes)
                    nodes.append({"rows": {}, "prods": []})
                    nodes[nd]["prods"].append((j, ci))
                    nxt.append((ci, byj[j]))
            items = nxt
        # ids: children first -> id = N-1-creation index
        N = len(nodes)
        out_nodes = []
        for cidx in range(N - 1, -1, -1):
            nd = nodes[cidx]
            rows = sorted(([_mask_list(mu), k] for (mu, k) in nd["rows"]),
                          key=lambda x: (x[0], x[1]))
            prods = [[j, N - 1 - c] for (j, c) in nd["prods"]]
            out_nodes.append({"id": N - 1 - cidx, "rows": rows, "prods": prods})
        return {"D": self.D, "nv": self.nv, "nodes": out_nodes, "output": N - 1}


def _mask_list(m):
    out = []
    i = 0
    while m:
        if m & 1:
            out.append(i)
        m >>= 1
        i += 1
    return out
