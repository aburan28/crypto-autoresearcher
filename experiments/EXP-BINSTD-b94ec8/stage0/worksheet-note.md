# Stage-0 worksheet — EXP-BINSTD-b94ec8

Zero-compute HOLD-X1/HOLD-T worksheet. Frozen before any Stage-1 metric.

## Counting identity (A)
On a Frobenius-stable V the orbit system Omega=(V^m/S_m)x Z/n has |Omega|=n |V^m/S_m|. Free C_n action (t,j)->(sigma t, j+1) cancels the per-instance divisor n exactly; gauge-fixed single-instance search size is |V^m/S_m|=2^{ml}/m! (multiset form also recorded). Hence |G|=m! on every curve shape; no per-instance Frobenius divisor remains (Proposition Sigma / 9c5694).

## ord_n(2) and stable lattices
- n=17: ord_n(2)=8, stable dims=[0, 1, 8, 9, 16, 17]
- n=23: ord_n(2)=11, stable dims=[0, 1, 11, 12, 22, 23]
- n=29: ord_n(2)=28, stable dims=[0, 1, 28, 29]
- n=31: ord_n(2)=5, stable dims=[0, 1, 5, 6, 10, 11, 15, 16, 20, 21, 25, 26, 30, 31]
- n=37: ord_n(2)=36, stable dims=[0, 1, 36, 37]
- n=41: ord_n(2)=20, stable dims=[0, 1, 20, 21, 40, 41]

## m=4 admissibility screen
- expected: [[31, 5], [31, 6]]
- computed: [[31, 5], [31, 6]]
- match: True

## Search sizes
- l=5: 2^{ml}/m!=43690.666666666664, multiset=52360
- l=6: 2^{ml}/m!=699050.6666666666, multiset=766480

## Claim-(D) D3/rho
- D3 bits=11.01; gap above D3=116.405 bits
- matched rho bits=60.809
A per-instance factor 131 (~7.03 bits) would not close the ~116.4-bit gap above D3 and does not exist after (A).

worksheet_ok=True; dual_routes_ok=True
Amazon Bedrock: NOT_USED
