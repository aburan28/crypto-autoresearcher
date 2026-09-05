---
id: KN-FIND-0618ab
type: internal_finding
title: >-
  The degree column of the d=2 digit presentation - the substituted summation
  generator has reduced total degree m*2^(m-1), not 2m, so any bounded-D_0
  Macaulay cost model at m>=3 prices a matrix with ZERO rows; and at m=2 the
  measured solving degree is D_0(s) = d_lf = d_ff = 4 + floor(s/2), a growing
  function of s
tags: [semaev, summation-polynomial, digit-presentation, generator-degree, macaulay, first-fall-degree, last-fall-degree, solving-degree, index-calculus, cost-model, negative-result, proven-boundary, ecdlp, prime-field]
confidence: reported
internal_refs: [EV-PFDR-f71d7f, EV-PFDR-99c699, EV-PFDR-1394a4, DEC-20260904-d47cd2, H-PFDR-06fd60, EXP-PFDR-c04716, EXP-PFDR-5726af, EXP-PFDR-cbdefb]
proof_status: derivation
proof_refs:
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da/derivation-R1-generator-degree.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da/derivation-R2-row-count.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da/rt_degree_probe.py
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da/rt_semaev_control.py
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da/rt_support_size.py
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da/proves-too-much-table.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5/derivation-r3-single-fall.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5/r3_single_fall_check.json
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-42b33a/rederivation.yaml
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5/rederivation.yaml
  - experiments/EXP-PFDR-5726af/stage0-htop.md
  - knowledge/techniques/KN-TECH-002.md
claim_tier: toy
added: 2026-09-04
superseded_by: null
---

## Finding

Two halves of one quantity — the **degree column** that any cost model of the
base-2 digit presentation must supply and, until this round, did not.

### 1. The generator-degree floor: `delta = m * 2^(m-1)`, not `2m`

The digit-substituted summation generator `S~` has reduced total degree

`delta = m * min(2^(m-1), s)`, which is `m * 2^(m-1)` = **4 / 12 / 32 / 80** at
`m = 2 / 3 / 4 / 5`.

The per-variable degree of `S_n` is `2^(n-2)` (this program's own KN-TECH-002),
giving `m * 2^(m-1)` in `m` unknowns, and the digit substitution followed by
multilinear reduction preserves it (a block-multigrading argument, checked
directly at `(m, s) = (2,2), (2,3), (2,5), (3,4)` by Möbius inversion over the
Boolean cube). The value `2m` — "degree 2 in each `x_k`" — is correct **only at
`m = 2`**.

Consequences, each independent of any heuristic:

- **A Macaulay matrix at any bounded degree `D_0 < delta` has NO ROWS.**
  `rows(D_0) = Ncols(n, D_0 − delta) = 0`. In the one cost table this program has
  built, that is 0 rows at **all 54 cells** and at **every `D_0 = 2` threshold
  row**, including the four cells reported as beating Pollard rho.
- **Any `D_0` that could bound a fall is at least `delta + 1`.** A degree fall
  needs a multiplier of degree ≥ 1, so `d_lf >= d_ff >= delta + 1` =
  5 / 13 / 33 / 81 at `m = 2 / 3 / 4 / 5`. This is *measured* at the two arities
  where it can be: EXP-PFDR-cbdefb records `d_ff = delta + 1` exactly at its
  boundary cells (5 at `(m 2, s 2)`, 7 at `(m 3, s 2)`).
- **The plain row count cannot determine the solutions at any fixed `D_0`.** The
  deficiency `Ncols(n, D) − Ncols(n, D − delta)` does not fall to `O(1)` until
  `D >= n + delta − 1` (348 at `n = 269`, `delta = 80`), so a bounded solve is
  available only through a closure, whose degree is `d_lf`.
- **Independently of all of the above, the generator cannot be written down at
  large `m`.** Its top-degree part alone has `binom(s, 2^(m-1))^m` nonzero terms
  = `2^221.3` at a 256-bit, `m = 5` parameter set, exceeding that set's entire
  claimed total cost of `2^108.76`.
- **Scope wider than one experiment:** the degree is a property of `S_{m+1}`, so
  the floor applies to **every presentation keeping `S_{m+1}` as a generator, at
  every base `d`**, not only at `d = 2`.

### 2. The measured solving degree at `m = 2`: `D_0(s) = 4 + floor(s/2)`

Under the frozen Huang–Kosters–Yeo closure convention, at `m = 2`, `d = 2`,
`s ∈ {2,3,4,5}`, `p ∈ {4099, 16411, 65537}`, 8 curves × 5 planted targets per
cell:

`(d_ff, d_lf) = (5,5), (5,5), (6,6), (6,6)` — on **480 of 480** Semaev draws,
with **zero** within-cell variance and **zero** between-prime variance at fixed
`s`, and residual 0 against the closed form `4 + floor(s/2)`.

Every fallen system has **exactly one** fall degree, and at that degree the
closure has already computed the entire degree-`≤ d_ff` part of the vanishing
ideal `I(Z)`. That identity is **derived, not fitted**, on 3660 of the package's
3752 fallen systems: if `V_{F,D0} = I ∩ B_{<=D0}` for some `D0 >= e(Z) + 1` then
no fall occurs above `D0` at any degree, and the recorded per-draw diagnostic
`V_complete_at_D` is true at the first fall on all 3752.

**So `D_0` is not a constant — it is a growing function of `s`.** A cost model
that treats it as a parameter must substitute the function. The one such table
this program has built requires `D_0 <= 6` at 256 bits with `omega = 2`; the
`m = 2` law exceeds that from `s = 6` on, and at `m >= 3` the floor `m*2^(m-1)`
puts it out of reach by an order of magnitude.

**The cost consequence, computed:** at the measured solving degree the reduced
column count `N_D = sum_{j<=D} binom(2s, j)` gives `log_B N_D` = 1.99, 1.95,
1.95 at `s = 3, 4, 5`, tending to `2H(1/4) = 1.6226`; the linear-algebra cost is
then about `B^3.9` at `s = 4, 5` and tends to `B^3.245` at `omega = 2`, against
`B^1` for exhaustive enumeration of one digit block and `O(sqrt(N))` for Pollard
rho. **σ > 1 by a wide margin at every tested `s`**: at its own measured solving
degree the algebraic route is dominated by brute-force enumeration of the digit
cube, and by rho on both time and memory.

## Scope and limitations

- **NOT AN IMPOSSIBILITY RESULT.** It does **not** follow that a bounded last
  fall degree is impossible for the digit presentation: a `D_0 = m*2^(m-1) +
  O(1)` constant in `s` is excluded by nothing here. Nor does it follow that the
  digit presentation is worse than the direct one — its floor `m*2^(m-1)` does
  **not** grow with the factor base, unlike the direct presentation's proven
  floor `d_lf >= B`, which is a real structural gain. And no universal
  impossibility about index calculus over prime fields is claimed.
- **THE m = 2 LAW IS NOT A STATEMENT ABOUT ELLIPTIC CURVES.** A singular
  non-curve nodal cubic reproduces the same `(d_ff, d_lf)` pair and censoring
  status at every one of the 15 cells on 600 draws, and a curve-free
  block-factored null reproduces the first-fall value at every strict cell. It
  is a statement about a degree-4 multilinear generator in `2s` squarefree digit
  variables whose top form is the tensor square of the digit linear forms.
- Toy scale: `p <= 2^16`, `s <= 6`, `m ∈ {2,3}`, at most a few thousand columns.
  Four points on the `s`-axis at resolution 0.25. **No growth-RATE statement is
  supported**: on the four independent `s`-levels the OLS slope's 95 % interval
  is `[−0.2085, 1.0085]`, containing 0, 0.25, 0.5 and 1. The reported per-draw
  interval `[0.382, 0.418]` is pseudoreplicated (four integers each repeated 120
  times) and it *excludes* the asymptotic slope 1/2 of the step law the data
  reproduce with residual 0.
- The `m = 2` half's conditions travel with it: the `d_ff` closed form is
  `H-PFDR-4148b8`'s (status `analyzed`), conditional on H-TOP at `m = 2` and on
  Wilson's rank theorem for exactness beyond the directly computed range — and
  that record's own `fall_dim` clause was refuted by counterexample in the same
  round. `H-TOP` is checked at `m = 2, 3, 4` and **open at `m >= 5`**
  (`KN-OPEN-02200b`).
- The `m = 2` ladder **cannot be lengthened** under the frozen instrument: at
  `s = 6` the ring has 4096 monomials against a 1024-column certificate limit,
  so every draw is right-censored by declaration.
- The receipt supporting the `m = 2` half is **incomplete**: all three blocking
  instrument controls of EXP-PFDR-cbdefb pin a `closure.py` version retained in
  no reachable commit and cannot be re-run. The 20 measurement runs are pinned
  to a retained version and are unaffected; a replication of the three controls
  is a required next action of `DEC-20260904-d4a554`.
- **Basis.** The generator-degree half is backed by a **counterexample
  certificate** in `EV-PFDR-f71d7f` (`S_4` has total degree 12, not 6). This
  finding nevertheless declares `proof_status: derivation`, the WEAKER of its
  two evidence records' bases, because half of it rests on `EV-PFDR-99c699`,
  whose basis is a derivation. A finding never claims a stronger basis than the
  evidence it rests on.

## Evidence

- `EV-PFDR-f71d7f` / `DEC-20260904-d47cd2` (`reject_scoped` of the `m >= 3`
  cells and all `D_0 = 2` rows of the conditional cost table).
- `EV-PFDR-99c699` / `DEC-20260904-d4a554` and `EV-PFDR-1394a4` /
  `DEC-20260904-1e27a2` for the `m = 2` law and the boundary-cell `delta + 1`
  measurements.
- Run records: EXP-PFDR-cbdefb's twelve `m2-s2..s5` ladder cells (480 Semaev
  draws), EXP-PFDR-5726af's `m2-s2-gate` through `m3-s5` (the `d_ff` ladder and
  the `S_4` symbolic top form), EXP-PFDR-c04716's zero-run STATIC-001 package
  (the 54-cell grid whose rows are counted).
- Independent reproduction: the degree by a validated standard-library probe
  with a known-answer control and by two other experiments' symbolic runs at
  `m = 3` and `m = 4`; the `m = 2` pair by two BLIND re-derivations (48 systems
  and 12 instances) sharing no code with the producers, and by a second engine
  (the graded-rank meter) agreeing on 24 of 24 rows.
