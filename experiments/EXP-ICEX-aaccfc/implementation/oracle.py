"""Exact m-membership oracle (uncharged, verifier arithmetic only): the set of
all sums of m signed factor-base points with repetition. Used for B0
agreement checks in smoke, tests and the accounting audit."""

from __future__ import annotations

from verify import O, VCurve


class MembershipOracle:
    def __init__(self, fx, points, m: int):
        vc = VCurve(fx["p"], fx["a"], fx["b"])
        signed = []
        for P in points:
            signed.append(P)
            signed.append(vc.neg(P))
        self.m = m
        sums = set()

        def rec(depth, start, acc):
            if depth == m:
                sums.add("INF" if acc is O else acc)
                return
            for i in range(start, len(signed)):
                rec(depth + 1, i, vc.add(acc, signed[i]))

        rec(0, 0, O)
        self.sums = sums

    def member(self, R) -> bool:
        return ("INF" if R is O else R) in self.sums
