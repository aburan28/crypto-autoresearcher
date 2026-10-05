# Task report: RUN-SEMBIN-9bb990 (EXP-SEMBIN-7e1371, handoff TASK-20260917-b2bf32)

Executor report. Measurement only: no hypothesis status is changed here, no evidence
record is written here, and nothing below is a claim about any deployed curve.

## VALIDITY NOTICE (read before any table below)

This run's manifest status is `completed_invalid`. The closure and single-level
rows below were produced with M4RI 0.0.20200125, whose eliminations leave the
row space at this scale (`NOTES-deviations-and-limitations.md`, sections "STOP"
and "N = 44 verdict on a fixed M4RI"). One recorded closure verdict, cell
(43,2,2,22) draw 0, is contradicted by exact enumeration and by direct
substitution of both solutions; every other closure and single-level row is
UNVERIFIED, and a `sufficient` or `insufficient` label below is not a result.
The exact solution counts (`|V(I)|`) are cross-checked by two independent
counters and are not affected by that defect. The closure and single-level
measurements for the m = t = 2 window are re-measured on a fixed library in
RUN-SEMBIN-5ed13e. Nothing in this report is an evidence decision.

## What was measured

The degree-4 Macaulay certificate of Semaev's eq. (5) chained-S_3 Boolean systems
(ePrint 2015/310, frozen at `inputs/SEMAEV-2015-310/`), in two readings:

- **single-level block** -- all products of the generators by monomials up to total
  degree 4, with its rank and its rank deficiency against `sum_{d<=4} C(N,d)`. This is
  the contract's literal certificate.
- **degree-capped closure** -- the same block iterated to saturation inside degree 4.
  Its standard-monomial count against the exact `|V(I)|` is the sufficiency verdict.

`|V(I)|` is measured exactly, by enumeration, not by a Groebner engine: every equation
of the chain is F_2-affine in the one unknown it is solved for, so the solution set is
walked in `|V|^(t-1)` field-linear solves (`count_chain.c`; `count_m2.c` is a second,
independent program for `t = 2` and the two agree wherever both apply). This is what
makes a verdict possible at cells where no F4 run completes on this host.

## The m = t = 2 window (growth in n)

| cell (n,m,t,k) | N | deg-4 columns | instances | exact \|V(I)\| | closure verdict at D=4 | standard monomials | closure_D |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (40, 2, 2, 20) | 40 | 102,091 | 40 | [0, 2, 4] | {'sufficient': 1} | [0] | [4] |
| (41, 2, 2, 21) | 42 | 124,314 | 40 | [0, 2, 4, 6, 8] | {'sufficient': 1} | [0] | [4] |
| (42, 2, 2, 21) | 42 | 124,314 | 40 | [0, 2, 4, 6, 8] | {'sufficient': 1} | [] | [2] |
| (43, 2, 2, 22) | 44 | 149,986 | 40 | [0, 2, 4, 6, 8] | {'sufficient': 1} | [0] | [4] |
| (44, 2, 2, 22) | 44 | 149,986 | 40 | [0, 2, 4, 6] | {'sufficient': 1} | [] | [2] |
| (45, 2, 2, 23) | 46 | 179,447 | 40 | [0, 2, 4, 6] | {} | [] | [] |

Per decided instance, which is where the verdict actually lives. A cell decided
below degree 4 stops the closure loop there (sufficiency is monotone upward in D,
so a decision at D <= 4 forces degree 4), and the rank/columns/standard-monomials
shown are the block that was actually built -- the deciding D, not literally D=4.

| instance | \|V(I)\| | source | decided D | rank / columns | standard monomials | verdict | wall s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ch_n40_m2_t2_k20_low_B_ran_s20260913101_d0` | 0 | exhaustive_count_over_V | 4 | 101931 / 102091 | 0 | **sufficient** | 941 |
| `ch_n41_m2_t2_k21_low_B_ran_s20260913101_d0` | 0 | exhaustive_count_chain | 4 | 124314 / 124314 | 0 | **sufficient** | 1569 |
| `ch_n42_m2_t2_k21_low_B_ran_s20260913101_d0` | 0 | exhaustive_count_chain | 2 | 904 / 904 | 0 | **sufficient** | 0 |
| `ch_n43_m2_t2_k22_low_B_ran_s20260913101_d0` | 2 | exhaustive_count_chain | 4 | 149986 / 149986 | 0 | **sufficient** | 3038 |
| `ch_n44_m2_t2_k22_low_B_ran_s20260913101_d0` | 0 | exhaustive_count_chain | 2 | 991 / 991 | 0 | **sufficient** | 0 |

## Off-diagonal k sweeps (the monotonicity probe)

| cell (n,m,t,k) | N | deg-4 columns | exact \|V(I)\| | closure verdict at D=4 | standard monomials | single-level D4 rank | deficiency vs columns |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (12, 6, 6, 2) | 60 | 523,686 | [0] | {'None': 1} | [] | [24553, 24555] | [499131, 499133] |
| (12, 6, 6, 3) | 66 | 768,692 | [0] | {'None': 1} | [] | [] | [] |
| (12, 6, 6, 4) | 72 | 1,091,059 | [0] | {'None': 1} | [] | [] | [] |
| (13, 4, 4, 4) | 42 | 124,314 | [24] | {'sufficient': 1} | [24] | [12728] | [111586] |
| (13, 4, 4, 5) | 46 | 179,447 | [] | {} | [] | [15143] | [164304] |
| (13, 4, 4, 6) | 50 | 251,176 | [1814] | {'None': 1} | [] | [17766] | [233410] |
| (17, 3, 3, 6) | 35 | 59,536 | [0, 6] | {'sufficient': 2} | [0, 6] | [11140] | [48396] |
| (17, 3, 3, 7) | 38 | 82,993 | [42] | {'sufficient': 1} | [42] | [13076] | [69917] |
| (17, 3, 3, 8) | 41 | 112,792 | [] | {} | [] | [15165] | [97627] |
| (17, 3, 3, 9) | 44 | 149,986 | [] | {} | [] | [17407] | [132579] |
| (19, 3, 3, 7) | 40 | 102,091 | [0, 15] | {'sufficient': 2} | [0, 15] | [16136] | [85955] |
| (19, 3, 3, 8) | 43 | 136,698 | [] | {} | [] | [18585] | [118113] |
| (19, 3, 3, 9) | 46 | 179,447 | [] | {} | [] | [21205] | [158242] |
| (19, 3, 3, 10) | 49 | 231,526 | [2154] | {'None': 1} | [] | [23996] | [207530] |
| (21, 3, 3, 7) | 42 | 124,314 | [] | {} | [] | [19600] | [104714] |
| (21, 3, 3, 8) | 45 | 164,221 | [] | {} | [] | [22433] | [141788] |
| (21, 3, 3, 9) | 48 | 213,053 | [90] | {'None': 1} | [] | [25455] | [187598] |
| (21, 3, 3, 10) | 51 | 272,052 | [555] | {'None': 1} | [] | [28666] | [243386] |

## Against what the paper publishes

`d_F4` values transcribed from Tables 1 and 2 of the frozen source, for the cells
this run measures. A cell the paper never published is new territory, not a
disagreement, and is marked as such.

| cell (n,m,t,k) | paper's d_F4 | this run's degree-4 verdict |
| --- | --- | --- |
| (40, 2, 2, 20) | [4] | {'sufficient': 1} |
| (41, 2, 2, 21) | *not published* | {'sufficient': 1} |
| (42, 2, 2, 21) | *not published* | {'sufficient': 1} |
| (43, 2, 2, 22) | *not published* | {'sufficient': 1} |
| (44, 2, 2, 22) | *not published* | {'sufficient': 1} |
| (45, 2, 2, 23) | *not published* | *not reached in this run* |
| (12, 6, 6, 2) | [4] | {'None': 1} |
| (12, 6, 6, 3) | *not published* | {'None': 1} |
| (12, 6, 6, 4) | *not published* | {'None': 1} |
| (13, 4, 4, 4) | [4] | {'sufficient': 1} |
| (13, 4, 4, 5) | *not published* | *not reached in this run* |
| (13, 4, 4, 6) | *not published* | {'None': 1} |
| (17, 3, 3, 6) | [4] | {'sufficient': 2} |
| (17, 3, 3, 7) | *not published* | {'sufficient': 1} |
| (17, 3, 3, 8) | *not published* | *not reached in this run* |
| (17, 3, 3, 9) | *not published* | *not reached in this run* |
| (19, 3, 3, 7) | [4] | {'sufficient': 2} |
| (19, 3, 3, 8) | *not published* | *not reached in this run* |
| (19, 3, 3, 9) | *not published* | *not reached in this run* |
| (19, 3, 3, 10) | *not published* | {'None': 1} |
| (21, 3, 3, 7) | [4] | *not reached in this run* |
| (21, 3, 3, 8) | *not published* | *not reached in this run* |
| (21, 3, 3, 9) | *not published* | {'None': 1} |
| (21, 3, 3, 10) | *not published* | {'None': 1} |

6 of the 24 chained cells measured here carry a published `d_F4`; the other
18 are cells the paper never reports -- every off-diagonal `k > ceil(n/m)`
cell, and every `m = 2` cell above `n = 40`.

## Controls

- **invalid_input** (controls): passed = `True`
- **known_false** (controls): passed = `True`
- **summation_polynomial_identity** (controls): passed = `True`
- **nearby_object (eq. (4))**: at `m = 3` the descended single summation polynomial has
  Boolean degree 6 (the paper's own bound `m(m-1)`), so no product of its generators
  fits in the degree-4 block at all: the block is empty, rank 0, and the certificate
  cannot report sufficiency. At `m = 2` eq. (4) IS eq. (5) at `t = 2` -- the same
  system, byte for byte -- which is recorded rather than counted as a second control.
- **matched_null**: a shape-matched random Boolean system; its verdict is reported as
  measured. `|V(I)|` is not available for it (no structure to enumerate), so where the
  closure does not reach `1 in W_D` its verdict is `undetermined`, which is not
  sufficiency and does not trip the contract's stopping rule.

## Cells not reached, with their sizes

| cell | family | instrument | D | columns | why |
| --- | --- | --- | --- | --- | --- |
| (12, 6, 6, 2) | chained_S3_eq5 | closure | 4 | 523686 | column count 523686 exceeds --closure-max-cols 200000 |
| (12, 6, 6, 3) | chained_S3_eq5 | closure | 4 | 768692 | N = 66 exceeds the 64-bit monomial mask both M4RI instruments use (closure_cert._csr); not |
| (12, 6, 6, 3) | chained_S3_eq5 | single_level | 4 | 768692 | N = 66 exceeds the 64-bit monomial mask both M4RI instruments use (closure_cert._csr); not |
| (12, 6, 6, 4) | chained_S3_eq5 | closure | 4 | 1091059 | N = 72 exceeds the 64-bit monomial mask both M4RI instruments use (closure_cert._csr); not |
| (12, 6, 6, 4) | chained_S3_eq5 | single_level | 4 | 1091059 | N = 72 exceeds the 64-bit monomial mask both M4RI instruments use (closure_cert._csr); not |
| (13, 4, 4, 6) | chained_S3_eq5 | closure | 4 | 251176 | column count 251176 exceeds --closure-max-cols 200000 |
| (19, 3, 3, 10) | chained_S3_eq5 | closure | 4 | 231526 | column count 231526 exceeds --closure-max-cols 200000 |
| (21, 3, 3, 9) | chained_S3_eq5 | closure | 4 | 213053 | column count 213053 exceeds --closure-max-cols 200000 |
| (21, 3, 3, 10) | chained_S3_eq5 | closure | 4 | 272052 | column count 272052 exceeds --closure-max-cols 200000 |

An unreached cell is **not** an insufficient one. Under AGENTS.md rule 3 and the
contract's invalidation rule 5, a cap is never negative mathematical evidence; the
column count is recorded so a later session with more memory can price the same cell.

## Distance to cryptographic scale

`crypto-scale-arithmetic.json` is arithmetic on the paper's own formulas, not a
measurement and not an extrapolation of one.

| n | m | k | N | deg-4 columns | log2 |
| --- | --- | --- | --- | --- | --- |
| 163 | 7 | 24 | 983 | 3.883e+10 | 2^35.18 |
| 233 | 9 | 26 | 1865 | 5.035e+11 | 2^38.87 |
| 283 | 9 | 32 | 2269 | 1.103e+12 | 2^40.01 |
| 409 | 11 | 38 | 4099 | 1.176e+13 | 2^43.42 |
| 571 | 12 | 48 | 6286 | 6.504e+13 | 2^45.89 |

Crossover with Pollard rho, minimising over m at each n:

| reading of the per-system Groebner cost | omega=2.376 | omega=2.807 | omega=3.0 |
| --- | --- | --- | --- |
| `n^{4w}` -- Table 3's own column (block-structured solver, never implemented) | n = 241 | n = 283 | n = 302 |
| `[n(m-1)]^{4w}` -- what Section 4.5.2 derives for F4 itself | n = 324 | n = 382 | n = 408 |
| `(#degree-<=4 monomials in N)^w` | n = 291 | n = 343 | n = 367 |

Time only. Stage 2 must also store `Theta(2^k)` relations, which none of these columns
charges (`KN-OPEN-86e7e1`).

## Scope

Everything above is scoped to the tested cells, the tested solver and the tested
budget. The largest n measured here is on the m = 2 diagonal; the paper's conclusion
needs n = 409 and 571 at m = 11, 12, which is roughly a 13-fold extrapolation in n and
a 6-fold one in m, untouched by this run. No transfer is claimed, and nothing here is
a statement about the security of any deployed curve in either direction.

