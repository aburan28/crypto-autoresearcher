"""Exact A5 oracle (C-5): exhaustive enumeration of all 5-multisets of signed
factor-base points, once per (fixture, deck), with independent verifier
arithmetic. Membership of R is then a bitmap lookup (x-indexed, one bit per
y-parity; y and p - y have opposite parity for odd p). Uncharged."""

from __future__ import annotations

from math import comb

import numpy as np

from verify import O, VCurve


class A5Oracle:
    def __init__(self, fx, deck):
        p = fx["p"]
        self.p = p
        vc = VCurve(p, fx["a"], fx["b"])
        S = []
        for P in deck.points:
            S.append(P)
            S.append(vc.neg(P))
        m = len(S)
        self.n_signed = m
        self.expected_multisets = comb(m + 4, 5)
        flags = np.zeros(p, dtype=np.uint8)
        self.has_O = False
        J = [vc._to_j(P) for P in S]
        jadd = vc._jadd
        frm = vc._from_j
        count = 0
        zero = (1, 1, 0)
        for i1 in range(m):
            A1 = jadd(zero, J[i1])
            for i2 in range(i1, m):
                A2 = jadd(A1, J[i2])
                for i3 in range(i2, m):
                    A3 = jadd(A2, J[i3])
                    for i4 in range(i3, m):
                        A4 = jadd(A3, J[i4])
                        for i5 in range(i4, m):
                            Pt = frm(jadd(A4, J[i5]))
                            count += 1
                            if Pt is O:
                                self.has_O = True
                            else:
                                flags[Pt[0]] |= 1 << (Pt[1] & 1)
        assert count == self.expected_multisets, (count, self.expected_multisets)
        self.enumerated = count
        self.flags = flags
        self.distinct_members = int(np.count_nonzero(flags & 1)) + int(np.count_nonzero(flags & 2)) \
            + int(self.has_O)

    def member(self, R) -> bool:
        if R is O:
            return self.has_O
        return bool(self.flags[R[0]] & (1 << (R[1] & 1)))
