# EXP-SEMBIN-35bf67 Stage 0 size worksheet

Computed by `implementation/sizes.py` (pure arithmetic, no RNG); machine-readable copy
`stage0/sizes.json`. Written before any Stage-1 code exists or runs.

System shape (Semaev 2015 eq. (5), Weil descent): N = n(t-2) + kt Boolean unknowns;
n(t-2) cubic + n quadratic equations (t = 3) or n quadratic equations (t = 2).
`M_le4` = squarefree monomials of degree <= 4 in N variables. `rows0` = initial degree-4
Macaulay rows (multiples m*f with deg m <= 4 - deg f). `init GiB` = rows0 x M_le4 dense
(the figure IDEA-20260913-9ba7fc quotes). `square GiB` = M_le4^2 dense. `compact GiB` =
M_le4^2/4 bits, the peak of an RREF stored on non-pivot columns only (r(M-r) <= M^2/4),
which is the storage both rank arms use. `prod UB` = rows0 + N * M_le3, an upper bound on
the rows the closure can generate.

IMPORTANT size note (observation from arithmetic, not a result): SOLV4 holds iff
dim R_4 = M_le4 - s, so on a cell where SOLV4 holds the closure's echelon basis is
(M_le4 - s) x M_le4, i.e. essentially square. The IDEA's GiB figures are for the
INITIAL Macaulay matrix only; the closure fixpoint is bounded by the square/compact
columns below. With compact storage every Stage-2 and off-diagonal cell is under the
8 GiB per-process cap; time, not memory, is the binding resource.

## Stage 2 decisive cells (run order)

| (n,m,t,k) | N | excess n(t-1)-N | M_le4 | rows0 | init GiB | square GiB | compact GiB | prod UB |
|---|---|---|---|---|---|---|---|---|
| (30,2,2,15) | 30 | 0 | 31,931 | 13,980 | 0.052 | 0.119 | 0.030 | 149,760 |
| (40,2,2,20) | 40 | 0 | 102,091 | 32,840 | 0.390 | 1.213 | 0.303 | 460,880 |
| (21,3,3,7) | 42 | 0 | 124,314 | 19,887 | 0.288 | 1.799 | 0.450 | 540,015 |
| (45,2,2,23) | 46 | -1 | 179,447 | 48,690 | 1.017 | 3.749 | 0.937 | 796,742 |
| (25,3,3,9) | 52 | -2 | 294,204 | 35,800 | 1.226 | 10.076 | 2.519 | 1,256,708 |
| (50,2,2,25) | 50 | 0 | 251,176 | 63,800 | 1.866 | 7.345 | 1.836 | 1,107,600 |

## Stage 3 off-diagonal gate

| (n,m,t,k) | N | excess | M_le4 | rows0 | init GiB | square GiB | compact GiB | prod UB |
|---|---|---|---|---|---|---|---|---|
| (40,2,2,21) | 42 | -2 | 124,314 | 36,160 | 0.523 | 1.799 | 0.450 | 556,288 |
| (40,2,2,22) | 44 | -4 | 149,986 | 39,640 | 0.692 | 2.619 | 0.655 | 665,980 |
| (25,3,3,10) | 55 | -5 | 368,831 | 39,925 | 1.714 | 15.837 | 3.959 | 1,567,605 |

## Stage 3 fixed-k ladders (sizes only; schedule status BLOCKED, see cell-schedule.json)

The frozen specification does not state (m, t) for the k=4 and k=7 ladders. Sizes are
listed for the readings that the inputs suggest, for information only:
k=4 at m=t=3 (N = n+12; M_le4 15,276 .. 102,091 for n = 13..28; all < 0.31 GiB compact);
k=4 at m=t=4 (Semaev's Table 1/2 k=4 rows are m=t=4; N = 2n+16; compact > 8 GiB from
n = 23; M_le4 = 1,091,059 at n = 28) -- but m = 4 is outside the frozen independent-variable
levels arity_m in {2,3};
k=7 at m=t=3 (N = n+21; M_le4 102,091 .. 272,052 for n = 19..30; <= 2.2 GiB compact).
Full rows in `stage0/sizes.json`.

## Stage 1 DREG anchors (EXP-DREG-001, t = m = 3, D = 5, seed 2026, ti = 0)

| n | k | N | Macaulay rows (D=5) | C(N, <=5) | recorded rank | recorded ncols (support) |
|---|---|---|---|---|---|---|
| 15 | 5 | 30 | 74,880 | 174,437 | 69,073 | 143,421 |
| 18 | 6 | 36 | 152,532 | 443,704 | 143,882 | 358,678 |

Row counts reproduce the recorded nrows exactly (74,880 and 152,532), which fixes the
multiplier rule of the DREG matrix as deg m <= 5 - deg f.

## Degree 5 (declared out of budget; C3)

Not computed here beyond the IDEA's figures (731,790 x 1,550,201, ~132 GiB at n=45 m=2).
No degree-5 computation is scheduled.
