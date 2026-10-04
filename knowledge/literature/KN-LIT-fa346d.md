---
id: KN-LIT-fa346d
type: literature
title: New algorithm for the discrete logarithm problem on elliptic curves
authors: [Semaev Igor]
year: 2015
venue: IACR Cryptology ePrint Archive
identifiers:
  eprint: iacr:2015/310
  doi: null
  arxiv: '1504.01175'
  url: https://eprint.iacr.org/2015/310
tags: [semaev, summation-polynomial, index-calculus, characteristic-two, binary-field,
  ecdlp, first-fall-degree, degree-of-regularity, groebner, weil-descent, chained-system,
  fips-186-4, asymptotic-complexity, contested]
confidence: reported
citation_verified: read
frozen_source: inputs/SEMAEV-2015-310/
source_record: SRC-SEMAEV-2015-310
supersedes: KN-LIT-009
added: 2026-09-13
superseded_by: null
---

## Why this record exists

`KN-LIT-009` has been this program's entry for this paper since 2026-07-19 and
says, correctly for its time, "Full paper not read." Meanwhile the program began
depending on the paper: `GOAL-DREG-001` measures the degree of regularity of the
Boolean system this paper introduces, and frozen `GOAL-RELN-001` /
`GOAL-ICEX-001` protocols carry a reference curve named `HEUR-SEMAEV-2015-4.3`
(`experiments/EXP-RELN-164ad3/specification.yaml`, `H-RELN-cfa1a2`,
`H-RELN-96e3ba`) which is this paper's Section 4.3. Under core rule 9 a recalled
citation is a pointer and supports nothing. The paper was therefore fetched and
read in full; it is frozen at `inputs/SEMAEV-2015-310/` (final revision of
2015-04-10, CC BY 4.0, retrieval receipt in `provenance.json`).

`KN-LIT-009` is not corrected or rewritten. It remains the immutable record of
what this program believed while the paper was unread, and points here.

## Contribution

Replaces the single summation-polynomial decomposition equation

    S_{t+1}(x_1, ..., x_t, R_X) = 0                                   (eq. 4)

with a **chain of `S_3` equations linked by auxiliary variables** (eq. 5):

    S_3(u_1, x_1, x_2)       = 0
    S_3(u_i, u_{i+1}, x_{i+2}) = 0     for 1 <= i <= t-3
    S_3(u_{t-2}, x_t, R_X)   = 0

Over `F_{2^n}`, with `V` an `F_2`-subspace of dimension `k = ceil(n/m)` and the
curve `Y^2 + XY = X^3 + AX^2 + B` (so
`S_3(x_1,x_2,x_3) = (x_1x_2 + x_1x_3 + x_2x_3)^2 + x_1x_2x_3 + B`), Weil descent
turns eq. (5) at `t = m` into a Boolean system of `n(t-1)` equations in
`n(t-2) + kt` variables of algebraic **degree 3**, against degree `2^{t-1}` for
eq. (4). The trade is many more variables for a far lower degree. Lemma 2
establishes the equivalence with eq. (4), conditional on the lower-`t` systems
being unsatisfiable, and handles the case where some `y_i` fall in
`F_{q^2} \ F_q` (their partial sum is then a point of order exactly 2, so
`s = 0` or `s >= 2`).

## Key claims (as the paper states them)

- **Assumption 1** (Section 4.5): `d_F4 <= 4` for the Boolean system equivalent
  to eq. (5), for every `2 <= t <= m`, where `k = ceil(n/m)` and `V` is a
  `k`-dimensional subspace. `d_F4` is defined in Section 4.4 as the maximal
  total degree of polynomials occurring before F4 finishes. The **first fall
  degree is proved to be 4**; Assumption 1 is the separate step `d_F4 <= d_ff`.
- Under Assumption 1 each decomposition costs `O[(n(m-1))^{4*omega}]`,
  `2.376 <= omega <= 3` — polynomial in `n`.
- **Section 4.3** success-probability model (eq. 11): treating
  `x_1,...,x_t -> S_{t+1}(x_1,...,x_t,z)` as a symmetric random map from `V^t`
  to `F_q` with `K ~ |V|^t / t!` classes,
  `P(n,m,t,k) = 1 - (1-1/q)^K ~ 1 - exp(-2^{tk-n}/t!)`.
- **Two-stage cost** (eqs. 15-17): stage 1 (relation collection)
  `~ m! * 2^{n/m} * 2^k * n^{4*omega} / 2^{mk}`, i.e. `m! 2^{n/m} n^{12}` at
  `omega = 3`; stage 2 (sparse linear algebra) `2^{k*omega'}` with `omega' = 2`.
  Balancing gives `m* ~ sqrt(2 ln2 * n / ln n)` and total time
  **`2^{c sqrt(n ln n)}`, `c = 2/(2 ln 2)^{1/2} ~ 1.6986`**.
- **Concrete claim** (Section 4.5.2, Table 3): the method beats Pollard rho for
  `n > 310`, so the four FIPS PUB 186-4 binary curves at `n = 409, 571` are
  "theoretically broken" — reduced to the two `n = 571` curves if the block
  structure is not exploited.
- **Assumption 2** (Section 4.6, the revision's added section): the weaker
  `d_F4 = o(sqrt(n / ln n))` suffices for the same asymptotic bound, which then
  "does not depend on any first fall degree assumption" — though the paper
  states the Table 3 concrete estimates, and hence the FIPS conclusion, do not
  generally survive under it.
- Extension to `F_{p^n}`, fixed `p > 2`, growing `n`: `p^{c sqrt(n ln n)}` with
  `c = 2/(2 ln p)^{1/2}`, via the first-fall-degree bounds of
  Hodges-Petit-Schlather. Section 2: "a similar assumption looks correct for odd
  `p` too but the computations are tedious already for `p = 5`."

## Experimental basis, exactly

Tables 1-2 (transcribed row-wise in `inputs/SEMAEV-2015-310/tables.yaml`) are
the paper's entire support for Assumption 1: MAGMA F4 on a 2.6 GHz Core i7 with
16 GB, 100 random `z` per cell, 2300 systems in total. **Every reported `d_F4`
is 4.** The parameter reach is `n <= 21` and `m <= 6` in every cell but one, plus
a single cell at `n = 40, m = t = 2, k = 20`. The FIPS conclusion needs
`n = 409, 571` at `m = 11, 12`, so the claim rests on a roughly 27-fold
extrapolation in `n` and 2-fold in `m` beyond the measured region.

Table 1's starred rows also quantify, without explaining, that the low-degree
polynomial `V` beats a random subspace of the same dimension (`11.41 s` /
`364 MB` vs `27.08 s` / `378 MB` at `n = 17, m = t = 3, k = 6`), which the paper
attributes to the Gröbner input being "simpler" and does not pursue.

## The paper's own stated boundary

End of Section 4.5.1, and load-bearing for anything built on Assumption 1:

> "the maximal degree(regularity degree) generally exceeds 4 when `k > ceil(n/m)`
> though the first fall degree is still 4."

So Assumption 1 is asserted only on the diagonal `k = ceil(n/m)`, and the paper
reports that raising the factor base off that diagonal breaks it while leaving
`d_ff` at 4 — i.e. the paper itself exhibits a regime where `d_F4 > d_ff`.

## Re-checked here (internal consistency only)

Arithmetic re-derived in the freezing session from the paper's own formulas, in
`inputs/SEMAEV-2015-310/tables.yaml` `derived_checks`:

- Section 4.3's model recovers as `P = 1 - exp(-2^{tk-n}/t!)` and reproduces
  every theoretical-probability cell of Tables 1-2 to the four printed decimals.
  **This confirms the formula that `HEUR-SEMAEV-2015-4.3` assumes**, for the
  first time in this program, against the source.
- All 36 numeric cells of Table 3 reproduce from `m! 2^{n/m} n^{12}`,
  `2^{2n/m}` and `2^{n/2}` to within 0.7%.
- Minimising the first stage over `m` puts the rho crossover at `n = 302`, so the
  paper's "`n > 310`" is internally consistent and slightly conservative.

None of this is evidence for Assumption 1 or for the FIPS conclusion.

## What the paper does not report

- **Memory anywhere in the asymptotic analysis.** Table 3 and eqs. (15)-(17) are
  time only, while stage 2 must store `Theta(2^k)` relations with `k` growing:
  `2^{31}` at `n = 310`, `2^{38}` at `n = 409`, `2^{48}` at `n = 571`. The
  comparison target, Pollard rho, has negligible memory. See `KN-OPEN-86e7e1`.
- **The direction of the Section 4.3 approximation.** The paper argues
  `P(solve one of the first t-1 systems) >= P(n,m,t,k) >= P(solve eq. 5)` and
  then assumes `P(solve eq. 5) ~ P(n,m,t,k)`. An upper bound placed in the
  denominator of relation-collection cost yields a lower bound on cost.
- **The `t < m` trade-off it identifies and declines.** Section 3 step 3: for
  `t < m` "the solving running time ... drops dramatically and the probability of
  solving is relatively lower ... the trade off may be positive, we won't pursue
  this approach in the present work as this does not affect the asymptotical
  running time estimates." Table 2 quantifies it. See `KN-OPEN-94f456`.
- **The block-structured solver.** Section 4.5.2 makes the four-curve claim
  contingent on it ("We think the same approach is applicable") and never
  implements it; without it the paper claims only two curves.

## Contested status — read with KN-LIT-e77232

`KN-LIT-e77232` is this corpus's receipt for Galbraith's ellipticnews post of
2015-04-13 and its comment thread, which is **three days after** the revision
frozen here, so it discusses this exact text. From that thread, and unreproduced
by anyone since:

- **Kosters** reports `n = 45, m = t = 2` reaching step degree **5** (126 GB) and
  `n = 25, m = t = 3` with solutions reaching step degree **5** (unfinished at
  111 GB). Semaev's own Table 2 reports `d_F4 = 4` at `n = 40, m = t = 2`. If
  both stand, the `m = 2` boundary of Assumption 1 lies between `n = 40` and
  `n = 45`.
- **Galbraith** puts dense storage at `2^{91}` bits for `n = 571, m = 12` against
  Semaev's sparse `2^{70}`; the freezing session independently recovered
  `2^{91.8}` from the paper's own parameters.
- **Semaev** replies that the method still beats Pollard at `n = 571, m = 12`
  with regularity degree up to 6 and linear-algebra constant 3.

`KN-LIT-7604` (Kosters-Yeo) and `KN-LIT-7607` (Huang-Kosters-Yeo, last fall
degree) both argue against `d_ff ~ d_reg` for summation systems generally.

## Relevance to this program

- `GOAL-SEMBIN-5078bc` audits Assumption 1's validity boundary and the
  memory-charged crossover; `GOAL-SEMBIN-cbf422` works the mechanism forward.
- `GOAL-DREG-001` has been measuring the degree of regularity of **this paper's
  Boolean system** at Macaulay degrees 5 and 6. Whether its `d_reg`/`D` is
  Semaev's `d_F4` is not established and is the first thing to settle
  (`KN-OPEN-d218ec`): if the two quantities differ, that campaign's
  measurements neither support nor contradict Assumption 1.
- `H-RELN-96e3ba` reports a `2^m`-type discrepancy between an exact law and the
  `HEUR-SEMAEV-2015-4.3` curve at `m = 2`. The curve is now confirmed to be
  eq. (11); whether eq. (11) is right for the chained system is open.

## Not verified here

The MAGMA implementation was never published and was not obtained. No timing,
memory figure or step-degree value in Tables 1-2 has been independently
reproduced by this program — that is assigned work (`EXP-SEMBIN-c2c312`), not a
claim of this record. The arXiv:1504.01175 alias is recorded as an identifier
because this repository's coordination records use it, but only the ePrint copy
was fetched, so the two texts have not been compared here.
