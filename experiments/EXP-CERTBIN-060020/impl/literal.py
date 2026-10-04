"""The executor's own LITERAL W_D (C-LIT, C-SELF (viii)/(ix)): numpy only, it
imports nothing from crypto_autoresearcher.

Literal rule (EXP-CERTBIN-e94b27 object.mutant_closure_W_D):
W^(0) = rowspace(M_D); W^(i+1) = W^(i) + span{v_j * b : b in a basis of
W^(i) cap B_{<=D-1}, j = 0..nv-1} (ALL basis elements, not only new ones);
stop at the first i with dim W^(i+1) = dim W^(i). Coordinates: all
multilinear monomials of degree <= D sorted by (-degree, bitmask); a basis of
W cap B_{<=D-1} is the set of echelon rows whose lead (lowest set coordinate
= highest monomial) has degree <= D-1.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np


class Literal:
    def __init__(self, nv, D, neq):
        self.nv, self.D, self.neq = nv, D, neq
        mons = []
        for d in range(D + 1):
            for m in combinations(range(nv), d):
                mons.append(sum(1 << i for i in m))
        mons.sort(key=lambda m: (-bin(m).count("1"), m))
        self.masks = np.array(mons, dtype=np.int64)
        self.C = len(mons)
        self.W = (self.C + 63) // 64
        self.deg = np.array([bin(m).count("1") for m in mons], dtype=np.int64)
        self.col = {m: c for c, m in enumerate(mons)}
        self.mus = [sum(1 << i for i in m) for d in range(D - 1) for m in combinations(range(nv), d)]
        low = np.flatnonzero(self.deg <= D - 1)
        self.low = low
        # mult[j][c] = coordinate of v_j * monomial c (c of degree <= D-1)
        lookup = {int(m): c for c, m in enumerate(mons)}
        self.mult = np.full((nv, self.C), -1, dtype=np.int64)
        for j in range(nv):
            for c in low.tolist():
                self.mult[j, c] = lookup[int(self.masks[c]) | (1 << j)]

    def dense_to_packed(self, Md):
        n = Md.shape[0]
        pad = self.W * 64 - self.C
        if pad:
            Md = np.concatenate([Md, np.zeros((n, pad), np.uint8)], axis=1)
        return np.packbits(Md, axis=1, bitorder="little").view(np.uint64).reshape(n, self.W).copy()

    def packed_to_dense(self, M):
        b = M.view(np.uint8).reshape(M.shape[0], self.W * 8)
        return np.unpackbits(b, axis=1, bitorder="little")[:, :self.C]

    def macaulay(self, eqs):
        rows = np.zeros((len(self.mus) * self.neq, self.C), dtype=np.uint8)
        r = 0
        for mu in self.mus:
            for f in eqs:
                acc = {}
                for m in f:
                    x = mu | m
                    acc[x] = acc.get(x, 0) ^ 1
                for x, p in acc.items():
                    if p:
                        rows[r, self.col[x]] = 1
                r += 1
        return self.dense_to_packed(rows)

    def echelon(self, M):
        """Own elimination: returns (rows, leads), leads ascending."""
        M = M.copy()
        active = np.arange(M.shape[0])
        # drop zero rows up front
        active = active[M[active].any(axis=1)]
        piv_rows, leads = [], []
        for c in range(self.C):
            if active.size == 0:
                break
            w, b = c >> 6, np.uint64(c & 63)
            bits = (M[active, w] >> b) & np.uint64(1)
            nz = np.flatnonzero(bits)
            if nz.size == 0:
                continue
            p = int(active[nz[0]])
            others = active[nz[1:]]
            if others.size:
                M[others] ^= M[p]
            piv_rows.append(p)
            leads.append(c)
            keep = np.ones(active.size, dtype=bool)
            keep[nz[0]] = False
            active = active[keep]
            if c % 64 == 63 and active.size:
                active = active[M[active].any(axis=1)]
        return M[piv_rows], np.array(leads, dtype=np.int64)

    def products(self, rows):
        """All v_j * rows (dense multilinear map), packed."""
        Md = self.packed_to_dense(rows)
        out = np.zeros((self.nv * rows.shape[0], self.C), dtype=np.uint8)
        nz_r, nz_c = np.nonzero(Md)
        for j in range(self.nv):
            tgt = self.mult[j, nz_c]
            assert np.all(tgt >= 0)
            blk = np.zeros((rows.shape[0], self.C), dtype=np.int64)
            np.add.at(blk, (nz_r, tgt), 1)
            out[j * rows.shape[0]:(j + 1) * rows.shape[0]] = (blk & 1).astype(np.uint8)
        return self.dense_to_packed(out)

    def w_closure(self, eqs):
        basis, leads = self.echelon(self.macaulay(eqs))
        const = self.C - 1
        dims = [int(len(leads))]
        one_first = 0 if const in set(leads.tolist()) else None
        i = 0
        while True:
            low = self.deg[leads] <= self.D - 1
            P = self.products(basis[low])
            nb, nl = self.echelon(np.concatenate([basis, P]))
            if len(nl) == dims[-1]:
                break
            i += 1
            dims.append(int(len(nl)))
            if one_first is None and const in set(nl.tolist()):
                one_first = i
            basis, leads = nb, nl
        return {"iterations_to_fixpoint": i, "dims": dims, "final_dim": dims[-1],
                "one": one_first is not None, "one_first_iteration": one_first,
                "dims_by_deg": [int((self.deg[leads] <= d).sum()) for d in range(self.D + 1)]}

    def macaulay_closure(self, eqs):
        basis, leads = self.echelon(self.macaulay(eqs))
        return {"rank": int(len(leads)), "one": bool((leads == self.C - 1).any()),
                "dims_by_deg": [int((self.deg[leads] <= d).sum()) for d in range(self.D + 1)]}
