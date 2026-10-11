"""J3 (1): the validator's OWN literal, slow W_D (TASK-20260926-42be88).

Independent of the pinned engine AND of impl/literal.py:
  * own E_hex codec (j2-population/gf219.py), own monomial indexing;
  * polynomials are Python ints over a DIFFERENT degree-compatible order
    (bit position increases with degree; ties broken by the complemented mask),
    so the lead (most significant bit) is a highest-degree monomial;
  * elimination is incremental reduce-by-pivot-dict on Python ints (not a column pass);
  * products v_j * b by explicit monomial map with XOR (parity) accumulation.

Literal rule (EXP-CERTBIN-e94b27 object.mutant_closure_W_D, nv = 20 here):
  W^(0) = rowspace(M_D); W^(i+1) = W^(i) + span{v_j * b : b in a basis of W^(i) cap B_{<=D-1},
  j = 0..nv-1}: EVERY basis element, at EVERY iteration; the whole stack is re-eliminated from
  scratch each iteration; stop at the first i with dim W^(i+1) = dim W^(i).
Intrinsic records: dims per iteration, fixpoint index, first iteration containing 1,
dim(W cap B_{<=d}) for d = 0..D, and rank / dims_by_deg of M_3 and M_4.
"""
import os
import sys
import time
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "j2-population"))
import gf219 as G  # noqa: E402


def popcount(x):
    return bin(x).count("1")


class Lit:
    def __init__(self, nv, D):
        self.nv, self.D = nv, D
        mons = [sum(1 << i for i in c) for d in range(D + 1) for c in combinations(range(nv), d)]
        full = (1 << nv) - 1
        mons.sort(key=lambda m: (popcount(m), m ^ full))  # own order: position 0 = constant
        self.mons = mons
        self.C = len(mons)
        self.pos = {m: p for p, m in enumerate(mons)}
        self.deg = np.array([popcount(m) for m in mons], dtype=np.int64)
        # degree boundaries: positions with deg <= d are exactly [0, cnt_le[d])
        self.cnt_le = [int((self.deg <= d).sum()) for d in range(D + 1)]
        for d in range(D + 1):
            assert (self.deg[: self.cnt_le[d]] <= d).all() and (self.deg[self.cnt_le[d]:] > d).all()
        # product map: PM[j][p] = position of v_j * mono(p) for deg(p) <= D-1
        low = self.cnt_le[D - 1]
        self.low = low
        self.PM = np.zeros((nv, low), dtype=np.int64)
        for j in range(nv):
            for p in range(low):
                self.PM[j, p] = self.pos[mons[p] | (1 << j)]
        self.nbytes = (self.C + 7) // 8

    # ---- conversions
    def poly_from_masks(self, masks):
        x = 0
        for m in masks:
            x ^= 1 << self.pos[m]
        return x

    def bits_of(self, x):
        b = np.frombuffer(x.to_bytes(self.nbytes, "little"), dtype=np.uint8)
        return np.flatnonzero(np.unpackbits(b, bitorder="little")[: self.C])

    def int_from_positions_parity(self, tgt):
        cnt = np.bincount(tgt, minlength=self.C) & 1
        pk = np.packbits(cnt.astype(np.uint8), bitorder="little")
        return int.from_bytes(pk.tobytes(), "little")

    def times_vj(self, x, j):
        p = self.bits_of(x)
        assert p.size == 0 or p.max() < self.low, "product of a degree-D element requested"
        return self.int_from_positions_parity(self.PM[j, p])

    # ---- Macaulay rows mu * f_k, mu of degree <= D-2, multilinear reduction with parity
    def macaulay_rows(self, eqs):
        rows = []
        mus = [sum(1 << i for i in c) for d in range(self.D - 1) for c in combinations(range(self.nv), d)]
        for mu in mus:
            for f in eqs:
                acc = {}
                for m in f:
                    y = mu | m
                    acc[y] = acc.get(y, 0) ^ 1
                x = 0
                for y, par in acc.items():
                    if par:
                        x ^= 1 << self.pos[y]
                rows.append(x)
        return rows

    # ---- elimination: fresh pivot dict, rows inserted one by one
    @staticmethod
    def span(rows):
        piv = {}
        for x in rows:
            while x:
                l = x.bit_length() - 1
                p = piv.get(l)
                if p is None:
                    piv[l] = x
                    break
                x ^= p
        return piv

    def dims_by_deg(self, piv):
        leads = np.fromiter(piv.keys(), dtype=np.int64, count=len(piv))
        return [int((self.deg[leads] <= d).sum()) for d in range(self.D + 1)]

    def w_closure(self, eqs, log=None):
        t0 = time.time()
        M = self.macaulay_rows(eqs)
        piv = self.span(M)
        mrec = {"rank": len(piv), "one": 0 in piv, "dims_by_deg": self.dims_by_deg(piv), "rows": len(M)}
        dims = [len(piv)]
        one_first = 0 if 0 in piv else None
        i = 0
        per_iter = []
        while True:
            basis = list(piv.values())
            lowb = [x for l, x in piv.items() if l < self.low]  # rows whose lead has degree <= D-1
            prods = [self.times_vj(x, j) for x in lowb for j in range(self.nv)]
            stack = basis + prods
            piv2 = self.span(stack)  # full re-elimination from scratch
            per_iter.append({"basis": len(basis), "low_basis": len(lowb), "stack_rows": len(stack),
                             "dim_next": len(piv2), "seconds": round(time.time() - t0, 1)})
            if log:
                log(per_iter[-1])
            if len(piv2) == dims[-1]:
                break
            i += 1
            dims.append(len(piv2))
            if one_first is None and 0 in piv2:
                one_first = i
            piv = piv2
        rec = {"iterations_to_fixpoint": i, "dims": dims, "final_dim": dims[-1], "one": one_first is not None,
               "one_first_iteration": one_first, "dims_by_deg": self.dims_by_deg(piv)}
        return mrec, rec, per_iter, piv


def eqs_from_E(E):
    """19 x 211 matrix (columns mu_order(2,20)) -> 19 lists of monomial masks."""
    masks = [sum(1 << i for i in mono) for mono in G.MONO2]
    return [[masks[c] for c in np.flatnonzero(E[k])] for k in range(E.shape[0])]


def macaulay_only(nv, D, eqs):
    L = Lit(nv, D)
    piv = L.span(L.macaulay_rows(eqs))
    return {"rank": len(piv), "one": 0 in piv, "dims_by_deg": L.dims_by_deg(piv)}
