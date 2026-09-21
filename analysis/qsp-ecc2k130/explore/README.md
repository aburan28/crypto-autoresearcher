# Exploring the four RQ-QSP-f9bbdb proposals: pre-compute audits (2026-09-17)

**Status: analysis note, not evidence.** Everything here is arithmetic in
GF(2)[X] run by `qsp_explore.py` (Python) and `gf2rc.c` (a word-level root
counter, compiled locally; binary not committed). No curve was touched, no
experiment contract exists, no ledger status changes. It is a section-8
pre-compute audit (`docs/inventor-protocol.md`) of the four proposals filed
by `TASK-20260916-a93a2a`, run so that the Coordinator's ranking of them
rests on computed facts. Promotion of any statement below to evidence needs
the ordinary `/design-experiment` → `/run` → `/review-evidence` chain.

Reproduce: `gcc -O2 -o gf2rc gf2rc.c && python3 qsp_explore.py --json explore.json`
(about an hour; `--skip-slow` runs the first six audits in two minutes and
writes `explore_fast.json`). Seed 20260917 for the random fixtures.

## What was checked, per proposal

### IDEA-20260916-3f7a1c (existence census without the 2^33 gcd)

The reduction: for `lambda in F_2[X]`, `L = X^{2^n'} + lambda`, `n = qn' + r`,
every root `x in F_{2^n}` satisfies `y := x^{2^r}` with
`H(y) = y^{2^{n'-r}} + lambda^{o(q+1)}(y) = 0`, so `N_K(L) <= max(2^{n'-r}, d^{q+1})`.

| audit | result |
|---|---|
| Stage 0 hand check, n = 4, n' = 3 | `X^2+X+1`: brute 1 = injection 1; `X^3+1`: brute 0 = injection 0 (H has 2 roots, both fail the closing test: slack 2) |
| Stage 1 toy fixtures, all 252 `lambda` of degree 2..7 at (n, n') = (11,6), (13,7), (7,3), (11,4), (13,5) | injection count = direct gcd count on every candidate (0 mismatches in 1260); every fifth candidate at (11,6) also matched by enumerating all 2048 field elements; `N/bound` at most 0.52, 0.56, 1.00, 0.25, 0.25 |
| bound attained | at (7,3) by `X^2+X` (Type 2) and `X^2+X+1`, both with 8 = 2^3 roots |
| proves-too-much | Type 2 at n = 7: 8; Type 2 at n = 31 (`X^{2^15}+X^{2^7}+X^{2^3}+X^2+X`): 32768; subfield n = 12, n' = 6: 64; Theorem 1 equality `X^4+X^2+X` over F_8: 4. All as forced. |
| **Stage 2, the census at n = 131** | see table below |
| Stage 3 as written | **cannot be run as designed**: at n' = 11 and 12 the injection polynomial has degree d^12 and d^11, far above deg L, so the bound is vacuous there and there is nothing to compare. What was done instead: the two brute instruments (Python gcd, C gcd) agree on a subset at n' in {11, 12}; and at n' = 22 (q = 5, H of degree 729 at d = 3) the injection count equals the C brute count at degree 2^22 (111 s per candidate) on two candidates. |

Census at n = 131, every non-linearized `lambda in F_2[X]` of degree 3..7
(244 candidates per n'; affine degree-4 lambda included since the 2026-09-17 fix below), exact `N_K(L)` by the injection method with the
per-orbit closing test:

| n' | q | r | max N | bound d^{q+1} at d = 7 | needed for the table row | histogram of N |
|---|---|---|---|---|---|---|
| 33 | 3 | 32 | **132** | 2401 | 2^32 | 0: 62, 1: 118, 2: 60, 132: 4 |
| 44 | 2 | 43 | 2 | 343 | 2^43 | 0: 62, 1: 122, 2: 60 |
| 66 | 1 | 65 | 2 | 49 | 2^65 | 0: 62, 1: 122, 2: 60 |

The four candidates with one full Frobenius orbit at n' = 33 are all of
degree 7: `X^7+X^2`, `X^7+X^5+1`, `X^7+X^6+X^3+X^2`, `X^7+X^6+X^5+X^4+X^3+X+1`
(N = 131 + 1 each; slack 0, i.e. every root of H is a root of L there). Under
the Poisson(1/131)-orbit null of the proposal's H1, 244 candidates give 1.9
expected orbits; observing 4 has probability about 0.1 and is not evidence of
structure. At n' in {11, 12} (brute, degree 2^11 and 2^12): max N = 2.

**Outcome 1 of the proposal's own (D) is what happened**: item (i) of
`RQ-QSP-f9bbdb` closes for `lambda in F_2[X]`, `3 <= deg lambda <= 7`,
`n' in {33, 44, 66}`, with an exact count per candidate, 20 bits or more
below what the table row needs. The certificate files (explicit root
orbits) are not written here; the run reproduces them from the seed-free
arithmetic in seconds.

### IDEA-20260916-5c9d6e (the general bound and its beta corollary)

The twisted derivation was re-derived by hand in this session: with
`Lambda_{k+1} = Lambda_k^{(n')} o lambda` (coefficients raised to `2^{n'}`),
a root satisfies `x^{2^{(k+1)n'}} = Lambda_{k+1}(x)`, and for `x in K`,
`x^{2^{(q+1)n'}} = x^{2^{n'-r}}`, so `x` is a root of
`Lambda_{q+1}(Y) - Y^{2^{n'-r}}`, degree `max(d^{q+1}, 2^{n'-r})` when that
polynomial is nonzero. The twists change nothing about degrees. The
degenerate case (the polynomial vanishing identically) forces
`Lambda_{q+1}` to be the monomial `Y^{2^{n'-r}}`, which at prime n cannot
split completely (the multiplicative census of the parent note). So the
bound holds for every `lambda in F_{2^n}[X]`, and complete splitting
(`N = 2^{n'}`) with `r >= 1` forces `d^{q+1} >= 2^{n'} - 2^{n'-r}`, i.e.
`beta >= n(n'-1)/(n'(n+n'-r))`, asymptotically `n/(n+n'-r) > 1/2`.

| audit | result |
|---|---|
| K-coefficient fixture, random `lambda in F_{2^11}[X]`: (n', d) = (6, 3) 60 draws, (6, 5) 40 draws, (4, 3) 40 draws | max N = 5, 4, 4 against bounds 9, 25, 27; bound holds on every draw |
| bound table at n = 131 | `beta >= 131/(131 + n' - r)`: 0.992 at every n' with 131 = -1 mod n', minimum 0.504 at n' = 130; Prop. 8 exponent at the bound >= 0.898, i.e. >= 2^117.7 at every n'; `alpha_beta > 1` would need `kappa < 0.992` |
| complete-splitting sweep, prime n in {7..31}, n' <= 15, 2 <= d <= min(8, 2^n' - 1), n' not dividing n | 356 candidates with N >= 2^{n'-1}, 65 complete (N = 2^n'), **0 violations** of beta >= n(n'-1)/(n'(n+n'-r)); complete splittings occur only at (n, n') = (7, 3) [36, tight: X^2+X at beta = 7/9 = bound], (7, 4) [3, tight], (31, 5) [24, min beta 2.48 vs bound 0.886], (31, 6) [2, min beta 1.72 vs 0.861]; the largest n' with any complete splitting at prime n <= 31 and d <= 8 is 6 |

The corollary inverts premise (4) of `RQ-QSP-f9bbdb` (already recorded in
`CORR-20260916-8d0b81` for F_2 coefficients; the K-coefficient form is this
proposal's and is unverified beyond the fixture above). Consequence for the
question: under the paper's own cost model, no quasi-subfield factor base
of the form `{x : x^{2^n'} = lambda(x)}` beats generic algorithms at n = 131
for any coefficient field, and beating rho's 2^60.9 would need a solver
constant `kappa < 1`, five times better than Rojas' 4.876. This is a
derivation-tier closure of the polynomial-lambda QSP line at prime n; it
needs an independent review before it can be promoted.

### IDEA-20260916-b84e2d (measuring the chain system)

Not run. Its Stage 0 engine check fails in this container: no Macaulay2,
Singular, msolve, Sage or Magma is installed (only sympy 1.14), so neither
Groebner route exists here and the resultant route for m <= 3 would have to
be written from scratch. The proposal itself ranks this low, for the right
reason: once 3f7a1c voids the factor base and 5c9d6e bounds beta, the chain
system's per-attempt cost changes no conclusion at n = 131; its remaining
value is calibrating the successor object's cost model (a17f43). If it is
ever designed, the engine impediment must be recorded first.

### IDEA-20260916-a17f43 (the conjugate-degree-2 successor object)

Two audits, one re-derived and one run.

- **Bezout arithmetic re-derived by hand**: with 4 layers, four summation
  equations of total degree 32 (assumed: S_5 has degree 8 in each of 4
  variables) and twelve links of bidegree (d0, 2), the coefficient of
  `z0^4 z1^4 z2^4 z3^4` is `32^4 * 4*6*4 * 2^6 * d0^6 = 32^4 * 6144 * d0^6`,
  matching the record. The total-degree assumption for S_5 on the ECC2K-130
  curve was not checked; a lower total degree lowers this count.
- **Toy census of the shape** `L_R = X^{2^{a+1}} + c(X) X^{2^a} + e(X)`,
  `c, e in F_2[X]` of degree <= d0, at prime n in {23, 29, 31} and the
  admissible a (r <= q), with the Type 2 fixtures: **run, and it returned the
  outcome the record calls the surprise** (its falsification condition 4). See
  the slow-stage table.

## Slow stages

Fixtures through the same instrument: Type 2 at n = 7 gives 8, Type 2 at
n = 31 (a = 14, d0 = 128) gives 32768. Both as forced.

Census of `L_R = X^{2^{a+1}} + c(X) X^{2^a} + e(X)`, `c, e in F_2[X]` of degree
<= d0, the linearized-trinomial slice (c constant, e linearized) excluded
because Proposition 2 decides it; `needed` is 2^a (half the shape's 2^{a+1}
roots), `bound` is the record's correspondence bound `d0^{q+1} + 2^{q+1} 2^{a-r}`:

| n | a | q | r | d0 | candidates | max N | needed 2^a | bound | holds |
|---|---|---|---|---|---|---|---|---|---|
| 23 | 11 | 2 | 1 | 2 | 56 | 2 | 2048 | 8200 | yes |
| 23 | 7 | 3 | 2 | 3 | 248 | 24 | 128 | 593 | yes |
| 23 | 5 | 4 | 3 | 3 | 248 | 24 | 32 | 371 | yes |
| 23 | 4 | 5 | 3 | 3 | 248 | 25 | 16 | 857 | yes |
| 23 | 3 | 7 | 2 | 3 | 248 | 2 | 8 | 7073 | yes |
| 29 | 14 | 2 | 1 | 2 | 56 | 2 | 16384 | 65544 | yes |
| 29 | 9 | 3 | 2 | 2 | 56 | 2 | 512 | 2064 | yes |
| 29 | 7 | 4 | 1 | 3 | 248 | 30 | 128 | 2291 | yes |
| 29 | 5 | 5 | 4 | 3 | 248 | **58** | 32 | 857 | yes |
| 29 | 4 | 7 | 1 | 3 | 248 | 30 | 16 | 8609 | yes |
| 31 | 15 | 2 | 1 | 2 | 56 | 2 | 32768 | 131080 | yes |
| 31 | 10 | 3 | 1 | 2 | 56 | 2 | 1024 | 8208 | yes |
| 31 | 7 | 4 | 3 | 3 | 248 | **64** | 128 | 755 | yes |
| 31 | 6 | 5 | 1 | 3 | 248 | 33 | 64 | 2777 | yes |
| 31 | 5 | 6 | 1 | 3 | 248 | **64** | 32 | 4235 | yes |

The three bold cells exceed the record's "controlled null" prediction of at
most 2n + 2 (two Frobenius orbits): at n = 31, a = 5, d0 = 3 the candidate
`c = X^2 + X`, `e = X^3 + X^2 + X`, i.e.
`L_R = X^64 + X^34 + X^33 + X^3 + X^2 + X`, has all 64 of its roots in
F_{2^31} (a non-linearized, completely splitting polynomial of the shape
with d0 = 3 at prime n, which the sweep above could not see because its
degree 34 exceeds the sweep's d <= 8); the same (c, e) at a = 7 gives 64 of
128; at n = 29, a = 5 the candidate `c = X^2 + X + 1`, `e = X^3 + X^2 + 1`
has 58 roots (two full orbits) against 32 needed. Whether these are
instances of a family (both positives sit at a = 5 with d0 = 3; 31 is a
Mersenne prime, 29 is not) was not investigated here. By the record's own
falsification condition 4, the n = 131 census at the admissible a is now
mandatory; its feasible part (a in {11, 13, 14, 16, 18} at d0 <= 3, a = 21
at d0 <= 2, via the O(deg^2) gcd) is `shape_census_131.py`, results in
`shape_census_131.json` when complete. The cells that matter most for the
cost surface (a = 32, i.e. n' = 33) need a sub-quadratic GF(2)[x] gcd at
degree 2^33 and are out of reach of this helper.

Important caveat on relevance: existence at a = 32 would make the cell
`(n' = 33, m = 4)` "alive on the factor base" but not on cost. The record's
own m-homogeneous Bezout floor for its layered decomposition system is
2^38.6 at d0 = 2 and 2^42.1 at d0 = 3 per attempt against a 2^31.3 budget,
and no mixed-volume routine exists in this container to lower it. The
positive existence outcome moves the question from "does the shape exist
at small d0" (yes, at toy n) to "what does its decomposition system cost",
which is exactly what b84e2d-style measurement would price and cannot be
priced here without an engine.

## What this changes in the ranking of the four proposals

- 3f7a1c: its Stage 2 has now effectively been executed as an analysis; as
  an experiment it would add only the certificate files and the null-object
  arm. Its Stage 3 must be redesigned (toy-n cross-check, not n' = 11/22).
- 5c9d6e: the mathematics is the load-bearing item and it survived every
  numerical check here. The next step is a validator/red-team review of the
  derivation, not compute.
- b84e2d: blocked by tooling and no longer load-bearing.
- a17f43: **promoted by its own audit.** The toy census found small-d0
  members of the shape that split completely at prime n, which the record
  predicted would not happen; its Stage 3 (the n = 131 census) is therefore
  mandatory by its own terms, and the feasible part is running. The cost
  half (mixed volume at (33, 4) against the 2^31.3 budget) remains the
  binding question and needs an engine this container lacks. This is the
  one proposal of the four whose ECDLP relevance is not yet settled by
  arithmetic, and it should be the next `/design-experiment`.

## Corrections 2026-09-17 (after the first merge of this note)

- **Parser overflow in `gf2rc.c`, found and fixed by a Cursor agent
  (commit `eedbc6e09`, restored by merge `e7bf63c6b` after a lease push had
  overwritten it).** The helper read each input line into a 64 KiB buffer
  and the hex string into a 32 KiB buffer; the a >= 18 cells of
  `shape_census_131.py` produce lines of 65536+ hex digits, so the a = 18
  cell committed in `2fa3b19e9` ("max N = 2, 218 candidates") was computed
  on truncated inputs and is **invalid**. It is superseded by the rerun
  below. Cells with a <= 16 (lines under 16400 digits) and every audit in
  `explore.json` (largest input: the Type 2 fixture at n = 31, 33 digits;
  the toy census at a = 15, 16386 digits) were unaffected.
- The same commit made the toy census enumerate constant coefficients
  c, e in {0, 1} (the first version enumerated only 0 at degree 0), and
  stopped classifying affine polynomials as linearized. `explore.json` and
  the tables above were regenerated: the n = 131 census has 244 candidates
  per n' (affine degree-4 lambda now included; same maxima 132 / 2 / 2), the
  toy census has 248 or 56 candidates per cell (same maxima and the same
  three positive cells), the sweep is unchanged (356 rows, 65 complete,
  0 violations).
- The rerun of `shape_census_131.py` with the fixed parser reproduces
  a = 11, 13, 14, 16 exactly (max N = 2, 2, 133, 131) and completes the two
  remaining cells: **a = 18, d0 <= 3: 248 candidates, max N = 2 (994 s)**;
  **a = 21, d0 <= 2: 56 candidates, max N = 2 (9242 s, about 165 s per
  candidate at degree 2^22)**. Reading of the whole n = 131 census of the
  conjugate-degree-2 shape with F_2 coefficients: at a = 14 two candidates
  and at a = 16 four candidates carry exactly one Frobenius orbit (N = 133
  and 131), which is what the Poisson(1/131) null predicts for 248 draws
  (about 1.9 orbit-carrying candidates per cell); every other candidate at
  every admissible a in {11, 13, 14, 16, 18, 21} has N <= 2. So no small-d0
  member of the shape with F_2 coefficients has more than one orbit of roots
  in F_{2^131} at any a this helper can reach; the toy positives at n = 29
  and 31 (a = 5) did not reappear at n = 131 for a <= 21. The cells a in
  {26, 32, 43, 65} (degree 2^27 to 2^66) remain out of reach of an O(deg^2)
  gcd and are the honest open remainder of this audit.
