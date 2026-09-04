#!/usr/bin/env python3
"""V2 SECOND PASS on fixture F2 only.  ORDER DISCLOSURE: written AFTER
cost_table.py was opened and AFTER IDEA-20260808-da1428 was read.  The first
pass (v2_recompute.py, hashed 2026-09-04T02:16Z before the script was opened)
implemented the review-plan paraphrase literally -- dense columns
binom(D+r, r) for EVERY r including r = 1 -- and got slope omega - 1.
IDEA-20260808-da1428 states a LEAF-COSTING CONTROL: 'the k=m-1 leaf must be
charged by root-finding, never by a Macaulay reduction', leaf = B^{m-1} 2^{m-1};
H-PFDR-06fd60 assumptions repeat it ('enumeration leaf charged by root-finding
plus O(1) lookup').  This pass applies that control and nothing else."""
import math

def direct_logC(m, k, B, omega):
    r = m - k
    D_S = m * 2 ** (m - 1)
    if k == m - 1:                       # da1428 LEAF-COSTING CONTROL
        return (m - 1) * math.log2(B) + (m - 1)
    D = -((-(r * (B - 1) + D_S)) // 2)
    return k * math.log2(B) + omega * math.log2(math.comb(D + r, r))

print(f"{'m':>2} {'omega':>6} {'B':>8} | {'logC k=m-2':>12} {'logC k=m-1':>12} "
      f"{'log2 ratio':>11} {'slope(bwd)':>11} {'slope(ctr)':>11} {'2w-1':>7}")
for m in (3, 4, 5):
    for omega in (2.0, 2.807):
        def lr(e):
            return direct_logC(m, m - 2, 2 ** e, omega) - direct_logC(m, m - 1, 2 ** e, omega)
        bwd = lr(20) - lr(19)
        ctr = (lr(21) - lr(19)) / 2.0
        print(f"{m:>2} {omega:>6} {'2^20':>8} | {direct_logC(m, m-2, 2**20, omega):>12.4f} "
              f"{direct_logC(m, m-1, 2**20, omega):>12.4f} {lr(20):>11.4f} "
              f"{bwd:>11.4f} {ctr:>11.4f} {2*omega-1:>7.4f}")
        # argmin over k at each grid B, 2^4..2^20
        am = {2**e: min(range(m), key=lambda k: direct_logC(m, k, 2**e, omega))
              for e in range(1, 21)}
        first_leaf = min(B for B in sorted(am) if all(am[b] == m - 1 for b in sorted(am) if b >= B))
        print(f"      argmin=m-1 at every grid B from B={first_leaf} on; "
              f"argmin at B=2: {am[2]}, B=4: {am[4]}, B=8: {am[8]}, B=16: {am[16]}")
