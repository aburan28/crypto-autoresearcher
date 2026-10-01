# Blind re-derivation: TASK-20260928-4e5c26 (GOAL-SEMBIN-5078bc)

Role: Validator, blind re-derivation (not a validation). Written on 2026-09-30
against repository HEAD `980abd8feec6429d1e7abb17618fe37bd10bd8a0` (clean tree).

## 0. Blindness record (what was read before this file was saved)

Read: `AGENTS.md`, `agents/validator.md`, CLAUDE.md (injected), the dispatch
prompt. Directory listings (names only) of `coordination/goals/GOAL-SEMBIN-5078bc/`
and `experiments/EXP-SEMBIN-04ec3c/` (showed `code/`, `runs/`, `specification.yaml`;
none opened).

NOT opened: everything on the blind list (`experiments/EXP-SEMBIN-04ec3c/code/`,
`RESULTS.md`, `runs/`, `DEC-20260928-7c3d91`, `TASK-20260928-e4f7b2`, the
`coordinator_amendments_pre_approval` section, `H-SEMBIN-8e7ae3`, PR descriptions,
git log messages). Also deliberately not opened, although not on the list, to
keep the derivation independent: the whole of `specification.yaml`, every file
under `coordination/goals/GOAL-SEMBIN-5078bc/batches/` (earlier SEMBIN reviews and
rederivations), the knowledge corpus/KB, and the two sibling review directories
`reviews/TASK-20260928-a1c7e5/` and `reviews/TASK-20260928-d8b371/`, which appeared
while I was working (seen as directory names only).

No number from the producer was seen. The only number in this file that came from
outside is 60.8090, which was in the prompt (Section 6 identifies where it comes from).

Script: `blind_rederive.py` (this directory). Outputs: `blind_rederived.json` (all
cells, all variants), `blind_rederived_primary_cells.csv` (primary model, one row per
(n, m)), `blind_rederive.stdout.txt`, `blind_rederive_mext.txt` (m > 16 side check).
Interpreter: `/usr/local/bin/python3` = CPython 3.11.15, mpmath 1.3.0 (60 digits).

## 1. The model, term by term

Unit: every cost is log2 of **elementary operations**. One elementary operation is
one elliptic-curve group operation, one hash-table probe, or one multiply-add mod r.
The rho baseline is in group operations (iterations), so this unit is **optimistic
for index calculus**: a table probe at 2^100+ entries and a 130-bit modular
multiply-add each count as one group operation. Memory is counted in **entries**.

Group size N: `N = r` for n = 131 (`log2 r = 129.000000…`, r exceeds 2^129 by a
relative 8e-21), and `N = 2^n` otherwise, as the dispatch prompt directs.

**Baseline.** `B = log2(0.886 * sqrt(N)) = N_bits/2 - 0.174621`. Note that
0.886 is sqrt(pi/4) = 0.886227 rounded, i.e. rho with the negation map.
- n = 131: B = 64.325379.
- Otherwise: B = n/2 - 0.174621.

**Factor base.** F = {P in E : x(P) in V}, with V an F_2-subspace of F_{2^n} of
dimension d. Each x in V gives two points or none, with probability 1/2 each, so
|F| ≈ 2^d points. F is closed under negation.

**Relations needed.** Because log(-P) = -log(P), there are K = |F|/2 = 2^(d-1)
unknowns. We need about K independent relations; the +1 for log Q and a few spares
are negligible. Primary convention: K = |F|/2. Sensitivity V1 uses the textbook
count K = |F|.

**Decomposition probability.** There are about |F|^m/m! unordered m-multisets from F.
Under the random-sum heuristic their sums are uniform on the group. So the expected
number of decompositions of a uniformly random target is `lambda = |F|^m / (m! N)`.
The sign choices are already inside F, because F is closed under negation.
Cross-check through x-coordinates: there are (|F|/2)^m/m! x-tuples, each hitting
2^(m-1) values of x(R), out of N/2 possible values. That gives the same lambda.

**Trials per relation.** Primary: `1/lambda` (expected-yield reading, uncapped).
Justification: an oracle with time |F|^(m-s) and store |F|^s is the meet-in-the-middle
search. It enumerates (m-s)-sums and probes a table of s-sums, so it returns *every*
decomposition of the target, and its enumeration can be stopped as soon as enough
relations are in hand. Under this reading the expected yield per unit of oracle work
is lambda/|F|^(m-s), including when lambda > 1. The strict-probability reading,
`P = 1 - exp(-lambda)` with one relation per call, is variant V2 (Section 5). Under V2
nothing is ever below rho.

**Oracle cost.** |F|^(m-s) per trial and store |F|^s, as given, with integer
0 <= s <= floor(m/2). Primary does **not** charge the |F|^s cost of building the
store, because the oracle is specified by its TIME/STORE pair. V3 charges it, and
then nothing is below rho.

**Relation collection.**
`RC = K * (1/lambda) * |F|^(m-s) = K * m! * N / |F|^s`.
The |F|^m cancels exactly, so m enters RC only through m!. I apply a floor of one
operation per relation (`RC = K * max(m! N / |F|^s, 1)`), which binds only when
|F|^s > m! N, i.e. never at a minimum-store cell.

**Sparse linear algebra.** A K x K system over Z/rZ with m nonzeros per row.
Lanczos/Wiedemann needs about K matrix-vector products, each costing m*K, so
`LA = m * K^2`. The real constant is 2–3 (V6 uses 3). Target generation (one double
scalar multiplication per target, and K/lambda << 1 targets here) and relation
bookkeeping (O(mK)) are both negligible and omitted.

**Total** = RC + LA (log-sum, not max). A cell (n, m, d, s) is *feasible* iff
total < B strictly. Its store is d*s bits. d runs over integers 1..n-1, s over
integers 0..floor(m/2).

## 2. Two structural identities, which decide the qualitative answer

(I1) `RC * store = K * m! * N`, which is at least N. So whenever RC < B, the
store satisfies store > K * m! * N / 2^B > K * m! * sqrt(N). In bits:
**the minimum store always exceeds the baseline's total work by more than
log2(K) + log2(m!)**. This holds in every uncapped model. In V4 (Section 5) the
bound is log2(K) + log2(s!).

(I2) Consequences:
- **Build charged (V3).** total >= max(RC, store) >= sqrt(K m! N) > sqrt(N) > 2^B.
  **No cell is feasible, for any n, m, d, s.**
- **Strict probability (V2).**
  - For lambda <= 1: RC ≈ K m! N / |F|^s, and d <= (N_bits + log2 m!)/m. Then
    |F|^(s-1) <= (m! N)^(1/2 - 1/m) < m! sqrt(N), so RC > sqrt(N).
  - For lambda >= 1: RC = K |F|^(m-s) >= (m! N)^(1/2 + 1/m) / 2 > sqrt(N).
  - **No cell is feasible, for any n, m, d, s.** (The script confirms both.)
- **Primary.** s <= 1 is never feasible: RC >= m! N / 2. s = 2 or 3 is never
  feasible either. With s = 3, RC * LA = (m/8) m! N, so the total is at least
  2 sqrt((m/8) m! N) = sqrt(m m!/2) sqrt(N) > 2^B for m >= 6. With s = 2, LA forces d < N_bits/4, but RC then needs
  d > N_bits/2. **Feasibility therefore needs s >= 4, i.e. m >= 8.** This is why
  m = 2..7 are empty in every row below.
- **Closed form (primary, LA negligible, m even, s = m/2).**
  d_min = smallest integer with d(s-1) > N_bits/2 + log2(m!) - 1 + 0.174621,
  and store = s * d_min.

## 3. Primary results (requested table)

Requested quantity: over m in 2..16, the minimum over (d, s) of the store d*s subject
to total < B.

| n | B = rho (bits) | minimising m | min store (log2 entries) | cell (m, d, s) | total at cell (bits) | RC / LA (bits) | margin below B | store excess over B (bits) |
|---|---|---|---|---|---|---|---|---|
| 97 | 48.325379 | 8 | 88 | (8, 22, 4) | 46.1573 | 45.2992 / 45.0000 | 2.1680 | 39.6746 |
| 109 | 54.325379 | 8 | 92 | (8, 23, 4) | 54.3083 | 54.2992 / 47.0000 | 0.0170 | 37.6746 |
| 131 | 64.325379 | 8 | 108 | (8, 27, 4) | 62.3083 | 62.2992 / 55.0000 | 2.0170 | 43.6746 |
| 163 | 81.325379 | 8 | 128 | (8, 32, 4) | 81.2992 | 81.2992 / 65.0000 | 0.0262 | 46.6746 |
| 191 | 95.325379 | 8 | 148 | (8, 37, 4) | 94.2992 | 94.2992 / 75.0000 | 1.0262 | 52.6746 |
| 233 | 116.325379 | 12 | 174 | (12, 29, 6) | 115.8355 | 115.8355 / 59.5850 | 0.4899 | 57.6746 |
| 239 | 119.325379 | **tie: 8, 10, 11, 12** | 180 | (10, 36, 5)* | 115.7911* | 115.7911 / 73.3219 | 3.5343 | 60.6746 |
| 283 | 141.325379 | 12 | 204 | (12, 34, 6) | 140.8355 | 140.8355 / 69.5850 | 0.4899 | 62.6746 |
| 409 | 204.325379 | 12 | 282 | (12, 47, 6) | 201.8355 | 201.8355 / 95.5850 | 2.4899 | 77.6746 |
| 571 | 285.325379 | 16 | 376 | (16, 47, 8) | 285.2501 | 285.2501 / 96.0000 | 0.0752 | 90.6746 |

\* n = 239 has four tied cells at store 180:
- (8, 45, 4), total 118.2992
- (10, 36, 5), total 115.7911
- (11, 36, 5), total 119.2505
- (12, 30, 6), total 116.8355

The row shows the tied cell with the lowest total.

Minimum store per (n, m), log2 entries ("-" = no feasible d, s):

| n | m=2 | m=3 | m=4 | m=5 | m=6 | m=7 | m=8 | m=9 | m=10 | m=11 | m=12 | m=13 | m=14 | m=15 | m=16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 97 | - | - | - | - | - | - | 88 | 92 | 90 | 95 | 96 | 102 | 102 | 105 | 112 |
| 109 | - | - | - | - | - | - | 92 | 100 | 95 | 100 | 102 | 108 | 112 | 112 | 112 |
| 131 | - | - | - | - | - | - | 108 | 112 | 110 | 115 | 114 | 120 | 119 | 126 | 126 |
| 163 | - | - | - | - | - | - | 128 | 136 | 130 | 135 | 132 | 138 | 140 | 147 | 144 |
| 191 | - | - | - | - | - | - | 148 | 152 | 150 | 150 | 150 | 156 | 154 | 161 | 160 |
| 233 | - | - | - | - | - | - | 176 | 180 | 175 | 180 | 174 | 180 | 182 | 182 | 184 |
| 239 | - | - | - | - | - | - | 180 | 184 | 180 | 180 | 180 | 186 | 182 | 189 | 192 |
| 283 | - | - | - | - | - | - | 208 | 216 | 205 | 210 | 204 | 210 | 210 | 217 | 216 |
| 409 | - | - | - | - | - | - | 292 | 300 | 285 | 290 | 282 | 288 | 287 | 287 | 288 |
| 571 | - | - | - | - | - | - | 400 | 408 | 385 | 390 | 378 | 384 | 378 | 385 | 376 |

Every cell's d, s, RC, LA, margin, lambda and number of full oracle calls is in
`blind_rederived_primary_cells.csv`. Extending to m = 17..24 never lowers the
minimum for any n (`blind_rederive_mext.txt`), so the m <= 16 edge is not binding.

**Integer-d artifacts.** The minimising m is sensitive to rounding d up to an
integer. With d real (s still an integer), the infimum store and argmin m are:

| n | 97 | 109 | 131 | 163 | 191 | 233 | 239 | 283 | 409 | 571 |
|---|---|---|---|---|---|---|---|---|---|---|
| infimum store | 84.01 | 91.98 | 105.30 | 127.97 | 145.58 | 171.83 | 175.58 | 203.08 | 279.01 | 374.52 |
| argmin m | 8 | 8 | 8 | 8 | 10 | 10 | 10 | 10 | 12 | 14 |

So a producer using real d or a different tie-break can legitimately report a
different m for n >= 191. The store differs from the integer answer by at most
about 4.4 bits.

**Qualitative answer.** For every n, the smallest store that lets this
index-calculus model beat rho exceeds rho's *entire* work by 2^37.7 (n = 109) to
2^90.7 (n = 571). The excess grows roughly like
N_bits/(2(s-1)) + (s/(s-1)) log2(m!). Its floor (identity I1) is
log2(K) + log2(m!) + 0.35.

## 4. The n = 131 questions

**(a) Store unconstrained: smallest m strictly below 60.8090 bits.**
Primary: **m = 8**, minimum total **59.2064** bits at d = 29, s = 4 (store 116 bits,
below N). Margin 1.60 bits.

Minimum total over (d, s) by m, primary:

| m | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| min total | 129.000 | 130.585 | 89.322 | 91.129 | 70.109 | 71.576 | 59.206 | 60.327 | 51.751 | 53.535 | 47.342 | 47.991 | 43.840 | 44.304 | 40.673 |

From m = 11 up, the unconstrained optimum has a store larger than N (flagged in the
JSON), so those rows lie outside the regime where the lookup formula is literal.

Sensitivity of answer (a):
- V1 (K = |F|): still m = 8, at **60.7912** bits. That is only 0.018 bits below
  60.8090, and m = 9 (61.86) is above.
- V5 (lambda over #E = 4r): m = 8 at 59.69.
- V6 (LA x 3): m = 8 at 59.99.
- V7 (K = |F| and LA x 3): m = 8 gives 61.45, so the answer becomes **m = 10**
  (54.99).
- V2 and V3: no m at all.

**The answer "m = 8" is fragile.** It depends on the relation-count convention and
the linear-algebra constant to within about 0.6 bits.

**(b) Total cost at m = 3 as a function of d.** With s = 1, the better of the two
allowed s values for every d:

```
primary (K = |F|/2):  total(d) = 3 * (N + 4^(d-1))        [s = 1]
                      total(d) = 3 * N * 2^d + 3 * 4^(d-1) [s = 0, always worse]
V1 (K = |F|):         total(d) = 3 * (2N + 4^d)            [s = 1]
```

RC = K * 3! * N / |F| does not depend on d. At n = 131 (N = r):

| d | 1–50 | 60 | 62 | 63 | 64 | 65 | 66 | 70 | 80 | 100 | 130 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| total | 130.5850 | 130.5857 | 130.5962 | 130.6294 | 130.7549 | 131.1699 | 132.1699 | 139.5878 | 159.5850 | 199.5850 | 259.5850 |

The curve is flat at `log2(3r) = 130.585` bits until LA takes over near d = 65.5,
where 4^(d-1) = r; from there it rises as 2d - 2 + log2 3. It is never below
exhaustive search (log2 r = 129).

Under the strict-probability reading (V2) the curve matches primary for
d <= ~40 (lambda << 1). It then rises as 3d - 1 once lambda > 1 (d >= 44):
d = 43 → 130.70, d = 44 → 131.44, d = 45 → 134.0, d = 60 → 179.0.
m = 2 is similar: total = N + 2 * 4^(d-1), flat at 129 bits.

## 5. Variants (each changes one thing relative to primary)

| variant | change | min store by n (97, 109, 131, 163, 191, 233, 239, 283, 409, 571) | n=131 (a) |
|---|---|---|---|
| PRIMARY | — | 88, 92, 108, 128, 148, 174, 180, 204, 282, 376 | m=8 (59.21) |
| V1_K_eq_F | K = \|F\| | 88, 96, 108, 130, 148, 175, 180, 205, 282, 378 | m=8 (60.79) |
| V2_prob_capped | trials = 1/(1 - e^-lambda) | **none feasible, any n** | none |
| V3_build_charged | + \|F\|^s build | **none feasible, any n** (identity I1) | none |
| V4_truncated | RC = K s! N/\|F\|^s (distinct hits of a truncated MITM) | 70, 77, 90, 110, 126, 152, 154, 182, 252, 344 | m=8 (55.00) |
| V5_fullgroup131 | lambda uses #E = 4r at n = 131 | same as primary; n=131 total 64.3015 at the same cell | m=8 (59.69) |
| V6_LA3 | LA x 3 | 88, 95, 108, 128, 148, 174, 180, 204, 282, 376 | m=8 (59.99) |
| V7_K_eq_F_LA3 | V1 + V6 | 90, 96, 108, 130, 148, 175, 180, 205, 282, 378 | **m=10** (54.99) |

The argmin m for each variant is in `blind_rederive.stdout.txt`.

V4 matters for interpretation. In a full MITM pass each unordered decomposition is
found m!/s! times, so the stated "trials per relation x oracle cost" model overcharges
a truncated enumeration by log2(m!/s!). That is 10.7 bits at m = 8. Correcting it
lowers the minimum store by 15–32 bits, depending on n. The store still exceeds the
baseline by 21.7 to 58.7 bits.

V4 also shows the (m, s) oracle family is dominated. Probing a table of s-sums
directly with random targets (m = s) costs the same as V4 with no enumeration at all.
The constraint s <= floor(m/2) is what forbids that choice.

## 6. Where 60.8090 comes from

log2(sqrt(pi r / 4) / sqrt(131)) = **60.80904**. That is the ECC2K-130 rho cost with
both the negation map and Frobenius acceleration (a factor sqrt(131)), using the exact
sqrt(pi/4). With 0.886 instead the figure is 60.80867. So the 60.8090 threshold gives
rho a Frobenius speedup that the index-calculus model here does not exploit. A
Frobenius-stable factor base would divide K by about n. That is outside this quantity
and is a limitation, not an error.

## 7. Regime caveats that bear on any agreement

1. **Fractional oracle calls.** Every primary minimum-store cell has lambda >> 1
   (log2 lambda from +59.21 to +328.53 across all (n, m) cells). Every feasible cell
   has lambda > 1, since RC < B with s <= m/2 forces log2 lambda > log2(m!) - 1.66.
   Each cell needs K/lambda full oracle calls, which is 2^-37.7 to 2^-227.5 of *one*
   call. A single full call costs |F|^(m-s), at least
   2^88 and always at least the store. So the primary number is achievable only by
   truncating the meet-in-the-middle enumeration. An atomic black-box oracle can
   never beat rho (V2).
2. **Store not built.** The primary model never pays for the store. Since the store
   exceeds the baseline in every feasible cell, a rho-beating total exists only if
   the store is supplied for free (identity I1). This should be read as "the
   comparison needs a free precomputation larger than rho", not as "index calculus
   is faster".
3. **Scale.** n = 131 uses r as directed. The others use 2^n, which ignores the
   cofactors of the standard curves (2 or 4, i.e. 0.5–1 bit on B and up to 2 bits on
   lambda). V5 shows the 131 answers survive the #E = 4r correction.
4. **Unit.** All costs are unit-cost elementary operations, optimistic for index
   calculus (table probes into 2^88–2^376 entry stores at unit cost), and memory is
   reported beside time. Nothing here was measured. This is a cost model only, with
   no run, no sampling and no heuristic validation.
