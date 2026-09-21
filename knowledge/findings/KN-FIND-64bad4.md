---
id: KN-FIND-64bad4
type: internal_finding
title: >-
  The (2,2,3) digit-presented Macaulay profile is FORCED by a parameter-free
  integer top form with sole content prime 2 and threshold p_0 = 3; the
  observable is a function of (zero set thresholded at 16/32/64, top form)
  alone and carries no curve, target or prime information
tags: [semaev, digit-presentation, macaulay, graded-rank, p-independence, content-primes, invariant-factors, specialization, null-object, controlled-null, prime-field, ecdlp, negative-scope]
confidence: reported
internal_refs: [EV-PFDR-acc71a, DEC-20260904-36b906, H-PFDR-09e1b0, EXP-PFDR-fd901a]
proof_status: derivation
proof_refs:
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-8c5f97/note-r2-forced-profile-and-content-primes.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-8c5f97/out/r2_forced_profile.json
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-8c5f97/note-r1-minor-degree-and-rank-drop-locus.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-8c5f97/out/r1_rankdrop_locus.json
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-8c5f97/note-r4-pointset-determination.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-8c5f97/out/r4_pointset_mutation.json
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-8c5f97/note-proves-too-much-table.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-4c0d7d/tables.md
  - experiments/EXP-PFDR-fd901a/stage0-derivation.md
claim_tier: toy
added: 2026-09-04
superseded_by: null
---

## Finding

For the base-2 digit presentation of the decomposition system at
`(m, d, s) = (2, 2, 3)` — six squarefree digit variables `a_{k,i}`, linear forms
`ell_k = a_{k,0} + 2 a_{k,1} + 4 a_{k,2}`, generator
`S~ = S_3(ell_1, ell_2, x_R)` reduced modulo `a_i^2 - a_i` — **the entire graded
Macaulay profile is a fixed integer, forced before any instance is drawn.**

- `top_rank(D) = sum_{j+k=D-4} r_1(j) r_2(k) = [1, 2, 1]` at `D = 4, 5, 6`,
  because the degree-4 part of `S~` is the parameter-free integer form
  `16 Q_1 Q_2`.
- The integer top blocks have **invariant factors `(16)`, `(16, 16)`, `(16)`**,
  so **2 is the only content prime** and `top_rank` is identical over every
  field of characteristic ≠ 2.
- `full_rank(D)` is the evaluation rank of the degree-`(D-4)` squarefree
  monomials on the non-vanishing set of `S~`, hence `[1, 6, 15]` **whenever
  `S~` has fewer than 16 zeros among the 64 digit points** (a drop at
  `D = 6, 5, 4` needs at least 16, 32, 64 zeros).
- Therefore the whole recorded vector — profile, `fall_dim [0,0,4,14]`,
  `syzygy_dim 0`, `d_ff 5`, deficit series — is forced for every odd `p`.
- **The threshold is `p_0 = 3`**: the fixture triple `(941, 428, 3690)` taken as
  INTEGERS and reduced modulo every prime in `{3, 5, 7, …, 199, 4099, 2^64 − 59,
  the NIST P-256 prime}` gives the reference profile at every one. The only
  deviating prime is 2. The computation costs under a second.

**The rank-drop locus is empty, not merely thin.** Exhaustively over all 4099
targets for 19 992 curves at `p = 4099` (81 947 208 curve–target pairs) the
maximum number of zeros of `S~` on the cube is **6**, against a threshold of 16.
The planted design contributes exactly 2 zeros in 120 of 120 recorded draws.

**What the observable is a function of.** `full_rank(D)` is invariant under any
rescaling of the nonzero values of `S~` on the cube, hence a function of the
zero set `Z(S~)` **alone**; `top_rank(D)` is a function of the fixed integer top
form **alone**. Two mutations separate the halves, each reproducing a recorded
arm exactly, 40/40 at `p = 4099`, `2^64 − 59` and the P-256 prime:

| mutation | what is held | what is randomised | result |
| --- | --- | --- | --- |
| M1 | the zero set and the 49-monomial support | all coefficients | the **NULL** arm's profile `[(0,0),(1,1),(6,6),(15,1)]` |
| M2 | the integer top form `16 Q_1 Q_2` | every sub-top coefficient | the **SEMAEV** arm's profile `[(0,0),(1,1),(6,2),(15,1)]`, `d_ff = 5`, `fall_dim [0,0,4,14]` |

**M2 contains no elliptic curve, no target, no planted decomposition and no
Semaev polynomial beyond its top monomial `x_1^2 x_2^2`.**

## Scope and limitations

- **THIS IS NOT A STATEMENT ABOUT SUMMATION POLYNOMIALS, ELLIPTIC CURVES OR THE
  ECDLP.** M2 reproduces the Semaev profile with no curve content, and the
  singular non-curve nodal cubic reproduces it at every prime by construction
  (identical top form, `|Z| = 2`, verified 40/40 per prime). Any downstream
  sentence of the form "the Semaev system at (2,2,3) behaves thus" must read
  "any generator with this integer top form behaves thus".
- One digit shape only. Nothing here touches the `s`-axis, the solving degree,
  yield, cost, or any attack. A graded rank profile is not a solving degree.
- **No cryptographic-scale claim.** The P-256 cells are exact ranks of a
  64-column matrix costing 3.25 s and 62 MB; the "cryptographic scale" of the
  run is field-element size only, and the value was forced before the run. Tier
  `toy` is kept deliberately against the mechanical field-size rule.
- The consequence for the experiment that produced it: criteria (3) and (5)
  could fail only by an instrument fault, and criterion (4)'s interval bounds an
  event set that is **empty** at the prime it names. The "small-p artifact
  budget" handed to sibling experiments is a **derived bound restated, not a
  measurement**, and should be replaced by the per-draw structural criterion
  `|Z(S~)| >= 16` (64 field evaluations per draw).
- **Two corrections this finding supersedes by reference** (records are
  immutable and were not edited): the maximal-minor **PRODUCT** Schwartz–Zippel
  bound in H-PFDR-09e1b0 / IDEA-20260903-26aa81 is **vacuous** at the tested
  primes (`deg(P_D) <= 4.79e15` at `D = 6` against `p = 4099`) — the usable
  constant `30/4099` is Stage 0's single-minor refinement; and
  `stage0-derivation.md` §4's **entry-content** check cannot exclude odd content
  primes, as the Wilson inclusion map `W_{1,3}` over `F_3` shows (entry content
  2, rank drops at `p = 3`). The invariant-factor computation above is the
  repair.
- `CTRL-CONFOUNDERS-NAMED (i)`'s "no ideal-level invariant appears" is false:
  four of the five reported invariants are point-set quantities. The confound is
  neutralised only by planting pinning `|Z(S~)| = 2`, far below every threshold
  that could move a rank; the exclusion should be restated as conditional on
  `|Z(S~)| < 16`.
- HEUR-001's `c_D/p` rank-drop law is **neither supported nor tested** by this
  shape: a drop needs a codimension-≥14 coincidence, so the true rate at
  `p = 4099` is 0 rather than `c/p`. Where a `c/p` law is real and measurable is
  the support-matched null's `top_rank` at `D = 5` (measured rates 0.2800,
  0.1835, 0.1035, 0.0935, 0.0130, 0.0005 at `p = 5, 7, 11, 13, 101, 4099`, 2000
  draws per rung).
- Basis is `derivation`, not `certificate`: the argument is checkable step by
  step by an independent reader and is corroborated by four independent
  implementations, but nothing here is machine-verified.

## Evidence

- `EV-PFDR-acc71a` (evidence) and `DEC-20260904-36b906` (decision, `support`).
- EXP-PFDR-fd901a run records `RUN-PFDR-fd901a-{fixture-p4099, posctrl-p4099,
  posctrl-p16411, sweep-p4099, sweep-p64, sweep-p256}`, six `completed_valid`
  runs, 722 draws.
- Independent recomputation: 245 of 245 draws by an implementation sharing no
  code with the meter (TASK-20260904-4c0d7d), and an independent tensor/symbolic
  derivation with the content-prime and one-integer-ladder computations
  (TASK-20260904-8c5f97). 276 planted certificates re-verified, 0 failures.
