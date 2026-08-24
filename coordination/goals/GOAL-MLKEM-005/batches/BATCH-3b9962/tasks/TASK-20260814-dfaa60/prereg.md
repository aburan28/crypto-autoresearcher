# PREREG-8 — BATCH-3b9962 PRE-REGISTRATION

    goal        GOAL-MLKEM-005
    batch       BATCH-3b9962
    task        TASK-20260814-dfaa60 (Coordinator, drafting) notarized alone
                by a separate, later Coordinator-only snapshot archive task
                (zero producer artifacts), per this goal's own established
                split-producer notarization pattern (PREREG-4 through
                PREREG-7 all used it)
    authority   ledger/goals/GOAL-MLKEM-005.yaml `next_action` (commit
                25b7f4ead), which names IDEA-20260805-3d71ca +
                IDEA-20260814-8f8f45 (required) + IDEA-20260814-137f68
                (optional, discretionary) as the exact scope of this batch
    hypothesis  H-MLKEM-7d9bcc (minted and two-scope verified by the
                orchestrating session; status `proposed` as of this
                notarization — this document's own notarization is NOT
                itself the ground for moving it to `specified`; that is a
                SEPARATE, later Coordinator act, exactly as PREREG-7 section
                0.2 records for H-MLKEM-11aabf)
    claim tier  TOY throughout (q = 3329 is a 12-bit prime; toy by the
                mechanical field-bit-size rule of
                docs/claims-and-verification.md regardless of tested BKZ
                dimension d in {256, 512}). NOT medium, NOT crypto. No
                ML-KEM break, no key recovery, is claimed anywhere in this
                document.

## Status of this document

**THIS IS THE FROZEN, NOTARIZED TEXT.** A four-agent independent review
(precedent rigor against PREREG-4 through PREREG-7; hypothesis faithfulness
to the two source ideas; NULL-3 scoping arithmetic and budget derivation;
experiment-contract and proof-architecture-audit completeness) plus a
Coordinator ruling (`approve_with_required_revisions`, twelve named
revisions) reviewed the drafting task's own output before this text was
frozen; every required revision was applied and independently re-verified by
the orchestrating session against primary sources before this notarization
(exact figures recomputed, not merely re-stated; the NULL-3 budget error,
the Stage-numbering inconsistency, the `n`/`d` symbol ambiguity, the
mismatched `beta/d` calibration point, the missing `LICENSES:` clauses, the
missing repair-bar analysis, the missing seed-determinism spec, the dropped
mechanism component, the mis-attributed C1-F1 citation, the composition
argument's category error, and the CPU-year arithmetic error are all
corrected in the text below — see this batch's own notarizing archive
receipt for the full verification record). This commit is the split-producer
notarization: zero producer artifacts accompany it, before any measuring
task is dispatched.

---

## 0. WHAT THIS BATCH DISCHARGES, WHICH HYPOTHESIS AND WHY

`ledger/goals/GOAL-MLKEM-005.yaml`'s own `next_action` (recorded in commit
`25b7f4ead`) makes an explicit portfolio decision, reasoned through at length
in that field's own text: convert `IDEA-20260805-3d71ca` — filed 2026-08-05,
unconverted for approximately nine days across an estimated thirteen to
twenty intervening batches, already stating this goal's own tracked object
almost verbatim — to a frozen `H-MLKEM-*` hypothesis via `/design-experiment`,
folding in `IDEA-20260814-8f8f45` (the order-statistic floor test) as a
REQUIRED companion extension of the SAME protocol (zero marginal reduction
cost per its own text), and admitting `IDEA-20260814-137f68` (the
GSA-profile-fidelity covariate) as OPTIONAL if it does not materially
complicate the protocol. `IDEA-20260814-10e5e1` (the census-grounded C1
`GAIN(u)` evaluation) and `IDEA-20260814-a609eb` (the C2 audit) are
DELIBERATELY OUT OF SCOPE — the former is a zero-lattice-compute arithmetic
task better dispatched as its own separate, even cheaper task; the latter is
not commissioned because C2 (the census of M) is already MET.

**THE HYPOTHESIS-STRUCTURE CHOICE.** `H-MLKEM-7d9bcc.yaml` (this batch's own
draft, see `hypothesis_draft.yaml`) converts `3d71ca` and `8f8f45` into ONE
hypothesis with two conjuncts (C1 = the tail law and its bit-savings readout;
C2 = the order-statistic floor test), not two hypotheses and not a bare
sub-claim. The reasoning is recorded in full in `hypothesis_draft.yaml`'s own
`statement` field ("Why one hypothesis, not two") and is not repeated
verbatim here; in summary, it mirrors `H-MLKEM-11aabf`'s own established
C1/C2 two-conjunct-single-hypothesis shape, and `8f8f45` itself states it
"should be commissioned as an addition to that same protocol, not as an
independent second experiment."

`IDEA-20260814-137f68` is admitted as a DISCRETIONARY, zero-marginal-cost
diagnostic analysis of Stage-1 byproduct data (§5 below), not as a third
conjunct of the hypothesis — it makes no falsifiable prediction of its own
about C1 or C2's truth (its own `interpretation_limits`: "DIAGNOSTIC ONLY").

### 0.1 `docs/inventor-protocol.md` section 8 — checked, not assumed

Both source ideas carry their own, already-populated `proof_search_map`
fields, and this IS a proof-oriented proposal in section 8's sense (C1 is a
constructive claim about a removable cost factor, with a named bottleneck,
an observation-collision search, an explicit quantifier order, and a stated
method ceiling with a nearby-object control; C2 likewise). **A
`proof_search_map` IS owed and IS carried**, transcribed and cross-checked
into `hypothesis_draft.yaml`'s own `proof_search_map` field. The full audit
— including one place where this drafting task's own review diverges from
what `3d71ca` assumed (the NULL-3 nearby-object control's literal
construction) — is in `proof_architecture_audit.md`, a required deliverable
of this same task, not folded into this section.

### 0.2 What this document does NOT do

Notarizing this document does not move `H-MLKEM-7d9bcc`'s status past
`proposed` and does not itself authorize any run of any kind — dispatching
the lead producer against this frozen protocol is a separate, later act. It
does not touch `H-MLKEM-11aabf`,
`H-MLKEM-dc51f5`, `H-MLKEM-232843`, or `H-MLKEM-34e22e`. It does not close,
pause, or complete `GOAL-MLKEM-005` or `RQ-MLKEM-001`.

---

## 1. INFRASTRUCTURE RE-VERIFICATION, TO BE PERFORMED FRESH IN THE LEAD'S OWN SESSION

**BEFORE ANY NUMBER FROM STAGE 1 OR STAGE 3 (§§3-4) IS TRUSTED**, the lead
(a separate Executor session, once this document is notarized and dispatched)
performs, in its own session:

1. Confirms `fpylll` is installed, records its exact version, and confirms
   `BKZ.reduction` (or the equivalent BKZ2.0 entry point the installed
   version exposes) is callable with an explicit `block_size` and, if the
   installed version ships one, a default strategies file. **This is the
   FIRST batch in this goal's `RQ-MLKEM-001` history to require actual
   lattice reduction** (task card TASK-20260814-dfaa60; every prior
   `RQ-MLKEM-001` measurement in this goal was either a closed-form estimator
   readout — `H-MLKEM-11aabf`/PREREG-7 — or bounded at `d <= 40` in the
   `hkz`/HKZ-independence lineage, confirmed by that lineage's own
   `EV-MLKEM-5aa471` record: "no reduction above d=40 occurred anywhere,
   independently verified by both reviews"). If `fpylll` is absent or
   non-functional, this fires `T-PROJNOISE-NODATA` (§4) for the WHOLE
   package before Stage 0 begins — no hand-rolled reduction substitute is
   commissioned.
2. Confirms the real CBD sampler (eta1 = 3, eta2 = 2) and the real FIPS 203
   `Compress_d`/`Decompress_d` definitions (`d_u = 10`, `d_v = 4`) match the
   ML-KEM-512/768 Table 2 values, independently re-derived from FIPS 203's
   own definitions (matching PREREG-7 section 1 point 3's own discipline for
   the estimator harness, applied here to the sampler/compression code
   instead).
3. Confirms the BLAS/numpy batched-Babai implementation reproduces exact
   scalar Babai nearest-plane on a handful of small, hand-checkable
   instances before any timing or comparative measurement (this protocol's
   own analogue of EXP-MLKEM-007's `CTRL-EXACT-EQUALITY`, required here for
   the identical reason: a batched and a scalar implementation disagreeing
   invalidates everything downstream of it).

**No Branch-B contingency (a hand-rolled BKZ substitute bypassing `fpylll`)
is commissioned by this document.**

---

## 2. STAGE 0 — FEASIBILITY BENCHMARK (gates the entire measurement grid;
##    runs first, cheapest possible reads first)

### 2.1 Why this stage exists and did not exist in any prior PREREG-* of this goal

Every prior `PREREG-*` in this goal's `RQ-MLKEM-001` history either ran a
closed-form estimator readout (PREREG-7, sub-second) or stayed at `d <= 40`
BKZ reduction, itself measured at well under one second per basis
(`TASK-20260813-7b3039` run manifest: `elapsed_seconds ~ 0.06`). **Neither
figure is informative for `d in {256, 512}`, `beta in {40, 55, 70}`.** This
protocol's own budget derivation (§6) is therefore explicitly built on an
ESTIMATE with wide uncertainty bounds, not a extrapolation from this goal's
own prior measured numbers, and Stage 0 exists precisely to replace that
estimate with a real number before Stage 1's full grid is committed —
matching this goal's own established "report wall-clock at increasing toy d
BEFORE committing to a specific d" convention (`8f8f45`'s own brute-force
floor control, generalized here to the BKZ stage itself).

### 2.2 What Stage 0 measures

For each of the 6 `(d, beta)` cells (`d in {256, 512}` x `beta in {40, 55,
70}`) — the SAME dimensions Stage 1 actually runs (§1, §9), so Stage 0's own
numbers are not systematically optimistic relative to what they gate —
reduce EXACTLY ONE basis (a single fresh key, single fresh `A`) and
record: wall-clock seconds, peak resident memory, number of BKZ tours to
convergence (or to `auto_abort`), and the achieved root-Hermite factor
`delta`. Each cell's reduction is capped at `PER_BASIS_FEASIBILITY_CAP =
3600` seconds (§6); a cell that does not complete within the cap is recorded
`NOT_COMPUTED: infeasible within Stage-0 cap`, not silently retried at a
different beta or dimension.

Independently, for `8f8f45`'s own exact-floor arm: sweep toy dimension
`d in {8, 12, 16, 20}` and report exhaustive-search wall-clock at each,
BEFORE committing to a specific `d` for the headline floor number — this is
`8f8f45`'s own `minimal_test` control, transcribed verbatim, not a new
requirement this document adds.

### 2.3 The Stage-0 decision rule

- A `(n, beta)` cell that COMPLETES within the cap is CLEARED for Stage 1 at
  that cell's OWN measured per-basis time, used to re-derive that cell's own
  realistic `>= 8`-draw budget (§6.2) — not the worst-case ceiling.
- A cell that does NOT complete within the cap is DROPPED from Stage 1's
  committed grid and reported `NOT_COMPUTED: infeasible within
  PER_BASIS_FEASIBILITY_CAP`. This is INFRASTRUCTURE SIGNAL for that cell
  specifically (AGENTS.md rule 5), never silently reinterpreted as a
  negative result about C1 or C2 at that cell.
- If EVERY cell is dropped, `T-PROJNOISE-NODATA` fires for the WHOLE package
  (§4); Stage 1 does not run at all.
- If AT LEAST ONE cell clears, Stage 1 proceeds on the cleared subset only,
  and the dropped cells are reported by name alongside whatever result the
  cleared cells produce — never merged, never silently omitted.
- The toy-floor `d` sweep separately selects the LARGEST `d in {8, 12, 16,
  20}` whose exhaustive search completes within
  `TOY_FLOOR_FEASIBILITY_CAP = 900` seconds; if `d = 8` itself does not
  complete, `8f8f45`'s own C2-F3 fires (HEUR-MLKEM-7d9bcc-4's own
  falsification) and C2's exact-floor arm is reported `NOT COMPUTED:
  infeasible within budget` while C2's own deceleration-statistic arm (which
  needs no toy floor) still stands independently.

---

## 3. STAGE 1 — MAIN MEASUREMENT (C1's tail law and bit-savings readout;
##    C2's running-minimum trajectory; gated on Stage 0 clearing at least
##    one cell)

### 3.1 Per cleared cell, per draw

For each Stage-0-cleared `(n, beta)` cell, `>= 8` independent `(key, basis)`
draws (KN-TECH-1a5b7e mode 5's own `>= 8`-draws-and-an-interval requirement,
transcribed from `3d71ca`'s own `minimal_test`):

1. Reduce one fresh basis `B` with `fpylll` `BKZ`-`beta`; freeze it.
2. Generate `>= 2^20` (up to `2^22` where Stage-0-derived budget permits)
   ciphertexts under that key via the real encryption routine; form targets;
   batch-Babai them against the frozen basis; record `rho(t)` for every
   target.
3. Compute the RUNNING MINIMUM trajectory `R_min(1), R_min(2), ...,
   R_min(M)` as a deterministic function of the already-computed `rho(t)`
   sequence — zero additional sampling (`8f8f45`'s own zero-marginal-cost
   design). `M = 1` is EXCLUDED from any decay-rate fit as a degenerate case
   (`8f8f45`'s own `baseline_embedding.parameter_slice`).
4. On a subsample of `10^4` targets, attempt the actual decode and measure
   the `rho`-versus-success correlation and `p(beta)` (`3d71ca`'s own
   `minimal_test` step 4).

### 3.2 Controls, in the order they must be run

1. **NULL-2 (Gaussian, matched variance) — REQUIRED, run FIRST, forced-value
   check for BOTH conjuncts.** Replace CBD errors with a discretised
   Gaussian of the same per-coordinate variance, everything else fixed.
   FORCED VALUES: Model A becomes exact by construction (C1's own
   calibration control — a failure here invalidates the real arm before it
   is read); the trajectory computation on this arm must show NO measurable
   deceleration and NO brute-force floor above the Beta-law prediction (C2's
   own forced-null check — a continuous distribution has unbounded left
   support, so a bug reporting "floor detected" regardless of input would
   fail this).
2. **NULL-1 (uniform targets).** Replace each ciphertext target by a
   uniform point of `Z_q^d`. FORCED VALUE (verbatim from `3d71ca`):
   `E[||pi(t)||^2] = (1/12) sum_{i>d-beta} ||b*_i||^2`, relative variance
   `4/5` per coordinate rather than the chi-square value `2` — a
   computable, different tail shape that can fail.
3. **NULL-3 (ephemeral arm / nearby-object control) — SCOPED, see §3.4.**
4. **SENS (graded sensitivity).** Scale the planted error by `lambda in
   {0.5, 0.75, 1.0, 1.5, 2.0}` at fixed basis and fixed candidate set;
   `rho` must move linearly and monotonically, `d(median rho)/d(lambda)`
   within 10% of 1.0 across all five points.
5. **COMP (comparator replication), and Brute-force-feasibility (§2.3),** are
   satisfied by construction of Stage 0 and the `>= 8`-draw design; report the
   interval, never a single draw; leave-one-out false-positive rate for an
   `n`-draw min/max interval is exactly `2/n`.

### 3.3 GSA-profile-fidelity covariate (`IDEA-20260814-137f68`) — OPTIONAL,
###    computed here if included, at zero additional basis generation

**RULING, MADE HERE RATHER THAN DEFERRED.** This document ADMITS
`IDEA-20260814-137f68` into the protocol, exercising the discretion the
goal's own `next_action` explicitly grants ("MAY fold IDEA-20260814-137f68
in too, at its own discretion, if the added bookkeeping ... does not
materially complicate the protocol"). It clears that bar: for each of the
`>= 8` draws already produced by §3.1, compute the SAME "hkz" scalar
(`mean(logb[d-beta:]) - logdet/d`) the `hkz`/HKZ-independence lineage
already defines, from the SAME GSO data `fpylll`'s `BKZ.reduction` already
returns as a byproduct — no new reduction, no new sampling. Correlate it
(Spearman, with confidence interval, `>= 8` points) against the per-basis
departure-from-Beta magnitude `3d71ca`'s own H1 validation already computes
per basis. Report the directional single-instance check (is the best-"hkz"
basis also among the lowest-departure bases, rank `<= 3` of 8) alongside the
aggregate correlation. **This is computed in Stage 3 analysis (§4), not
Stage 1 measurement — it needs no new run.** Per `hypothesis_draft.yaml`'s
own ruling, this covariate's outcome is DIAGNOSTIC ONLY and cannot move
`H-MLKEM-7d9bcc`'s status in either direction; it is reported beside, never
folded into, the C1/C2 termination-branch adjudication (§4).

### 3.4 NULL-3, SCOPED — a deliberate, flagged amendment to `3d71ca`'s literal text

`IDEA-20260805-3d71ca`'s own NULL-3 control reads: "Fresh key and fresh
basis per target." Read literally, at the main arm's own `M >= 2^20`
targets, this requires up to `2^20`-`2^22` independent BKZ reductions for
the null arm ALONE — several orders of magnitude beyond what Stage 0's own
feasibility numbers could possibly license (§6), and beyond what any
defensible budget for this protocol can absorb. **This is flagged and
resolved here, not silently narrowed**, per the task card's own explicit
invitation to report a genuine specification gap rather than paper over it;
the full argument is in `proof_architecture_audit.md` section 3, which this
section summarizes.

**THE SCOPING.** NULL-3 is run at `M_null3 = 64` independent
`(fresh key, fresh basis, single target)` draws PER CLEARED `(d, beta)`
cell — 64 additional BKZ reductions per cell, rather than up to `2^22`. Each
NULL-3 draw is capped at `PER_BASIS_FEASIBILITY_CAP = 3600` s (§6.3), NOT
the `PER_BASIS_STAGE1_CAP = 14400` s the main arm's own draws use — a
single-target draw generates no `>= 2^20`-target grid, so it is priced at
Stage 0's own cheaper per-basis cap, not Stage 1's. `M_null3 = 64` is chosen
to match the scale of this protocol's own other small-`M` controls (SENS's
five points; the `>= 8`-draw COMP interval).

**THE ADJUDICATING RULE, STATED HERE AND NOT MERELY IN §4.3, SO THE TWO DO
NOT DIVERGE.** NULL-3's control fires `T-PROJNOISE-HARNESS-ARTIFACT` (§4.3
item 3) when NULL-3's own measured best-of-`M_null3` gain is statistically
indistinguishable from, or exceeds, the REAL ARM's OWN MEASURED headline
effect (`c1_implied_bit_saving`, not a pre-run estimate) SCALED by
`log2(M_null3) / log2(M)`, where `M` is the tested cell's own main-arm `M`.
This is a RELATIVE comparison against whatever the real arm actually
measures, not an absolute comparison against `M_null3`'s own `log2(64) = 6`
-bit ceiling versus the `>= 5`-bit pre-registered materiality gate (that
absolute gate is `hypothesis_draft.yaml`'s own `predictions` entry for
`implied_bit_saving`, `minimum_effect` field — NOT falsification condition
C1-F1, which is instead the SEPARATE `< 2`-bit closing threshold; the two
numbers must not be conflated). Concretely, at the tested `M` grid `{2^10,
2^14, 2^18, 2^20, 2^22}`, the scale factor `log2(64)/log2(M)` ranges from
`6/22 ~ 0.27` (at `M = 2^22`) to `6/10 = 0.6` (at `M = 2^10`) — so if the
real arm measures, for illustration, a 5-bit headline gain at `M = 2^20`,
NULL-3's own scaled threshold there is `5 x 6/20 = 1.5` bits, not `5` or `6`
bits outright. A measured NULL-3 gain below that SCALED threshold, and
statistically indistinguishable from the `M = 1` baseline, is a genuine,
informative negative for the "the effect requires a shared basis" claim,
even though `M_null3` cannot match the main arm's `M` exactly. **THIS IS AN
INTERPRETATION, NOT A MEASUREMENT OF THE SAME QUANTITY AT THE SAME SCALE**,
and `hypothesis_draft.yaml`'s own `interpretation_limits` disclose plainly
that this weakens, but does not eliminate, NULL-3's discriminating power at
the FULL tested `M`. A reviewer who judges `M_null3 = 64` too small to be
decisive may require a larger value before approval; that is exactly the
kind of protocol-amendment decision this draft flags for, rather than
pre-empts.

### 3.5 Seed and RNG determinism — frozen so a second implementation can
###     reproduce every draw bit-for-bit, matching PREREG-4 §2.1's own
###     convention

No prior `PREREG-*` in this goal's lineage has left its random constructions
unseeded; this document freezes the identical convention. For every fresh
`(key, basis)` draw in Stage 1 (§3.1) and every fresh single-target draw in
scoped NULL-3 (§3.4), the RNG is seeded as:

    seed = default_rng([SEED_ROOT, stage_index, d, beta, arm_index, draw_index])

where `SEED_ROOT = 715923`. CORRECTED FROM AN EARLIER DRAFT, which proposed
`SEED_ROOT = 3` and mischaracterized it as "this goal's fourth distinct seed
root, after 1 and 2" — a targeted check (`default_rng([N` as an actual
seed-prefix usage, not a bare-substring search, which false-positives
constantly against the large numeric values already present throughout this
repository's own run outputs) found this repository's own `hkz`/
HKZ-independence lineage alone already uses AT LEAST the small integer roots
`1` through `10` as `default_rng([N, d, k, ...])` prefixes across multiple
prior batches (e.g. `BATCH-4ed139`, `BATCH-cbe023`, `BATCH-9e3584`), plus
larger fixed constants (`424242`, `313131`, `12345`, `59321`) for specific
auxiliary draws — `SEED_ROOT = 3` literally collides with an existing usage
(`BATCH-cbe023`'s and `BATCH-9e3584`'s own permutation-matrix seeding,
`default_rng([3, d, k, beta, h])`). `715923` was verified free of the
literal `default_rng([715923` pattern, both in this worktree and across the
25 most-recently-updated remote branches, before being frozen here.
`stage_index` is `0` for Stage-0 feasibility draws, `1` for
Stage-1 main-arm draws, `3` for scoped NULL-3 draws (matching this
document's own stage numbering, §2-§4 — there is no `stage_index = 2`);
`d` and `beta` are the cell's own parameters; `arm_index` distinguishes
`real_cbd`, `null1_uniform`, `null2_gaussian`, `null3_ephemeral_scoped`, and
each `sens_lambda` point (five further sub-indices); `draw_index` is the
independent-draw counter within that `(stage, d, beta, arm)` cell, `0`
through `>= 7` for the main arm's `>= 8` draws or `0` through `63` for
NULL-3's `64` draws. Every basis reduction and every CBD/uniform/Gaussian
sample draws from this seed and no other source of randomness; a second
implementation given the same seed tuple reproduces the identical basis and
the identical error/target draws bit-for-bit, exactly as PREREG-4 §2.1's own
`F0` construction requires of the `hkz`/HKZ-independence lineage. The
`SEED_ROOT` value itself, once verified free, is recorded in this
document's own notarization commit and in `run_manifest.yaml` at run time —
never re-chosen mid-protocol.

---

## 4. STAGE 3 — ANALYSIS AND THE TERMINATION-BRANCH TAXONOMY

### 4.1 What is computed

- C1: empirical CDF and left-tail exponent of `rho`, per `(n, beta, arm)`;
  Kolmogorov distance and tail-quantile ratios at `2^-10` and `2^-18` against
  Model A and Model B; the tail-consistency check (single smallest `rho`
  among `2^20` draws against the Beta model's own predicted minimum
  interval); best-of-`M` ratio at `M in {2^10, 2^14, 2^18, 2^20, 2^22}` with
  intervals over `>= 8` draws; measured `p(beta)` and the `rho`-vs-success
  rank correlation; between-basis vs within-basis variance decomposition of
  `rho` (H3's own confound).
- C2: local decay-rate ratio of `R_min(M)` at each tested decade of `M`,
  against the closed-form Beta extreme-value asymptotic slope, with
  intervals over `>= 8` draws; exact `r_min(B)` at the chosen toy sub-cell,
  with wall-clock and certified-gap status; NULL-2/NULL-3 floor-detection
  outcomes.
- §3.3's covariate, if run: Spearman correlation and the directional
  single-instance check, reported separately (§4.4).

### 4.2 Per-cell adjudication — the frozen decision rules

**C1, per cleared `(n, beta)` cell:**

    C1-HOLDS      iff  measured left tail matches Model B (or, if NEITHER
                        A nor B, matches whichever is the closer within a
                        pre-registered tolerance) within the Kolmogorov-
                        distance and tail-quantile-ratio thresholds stated
                        in HEUR-MLKEM-7d9bcc-1's own validation_plan
    C1-FAILS-BY-FACTOR
                  iff  the measured tail departs from BOTH derived curves by
                        a QUANTIFIED, stated factor (reported exactly, not
                        merely "different")
    C1-NEITHER    iff  the measured tail matches neither cleanly nor departs
                        by a clean, single quantified factor -- an
                        explicit, expected, non-defect branch (matching
                        C1's own DECISION RULE FROZEN BEFORE THE RUN
                        language in 3d71ca's own predictions)

**C2, per cleared `(n, beta)` cell (deceleration arm) and at the toy
sub-cell (exact-floor arm):**

    C2-FLOOR-CONFIRMED
                  iff  r_min(B) exceeds the Beta-law's predicted quantile at
                        M = (2*eta+1)^d by any measurable, exact margin, OR
                        the deceleration ratio is significantly below 1
    C2-NO-FLOOR   iff  r_min(B) equals the Beta-law prediction within
                        floating-point tolerance AND the deceleration ratio
                        is statistically indistinguishable from 1
    C2-COLLISION  iff  a floor (by either sub-test) is ALSO detected in
                        NULL-2 -- verdict downgrades per 8f8f45's own
                        observation_collision handling, never reported as a
                        clean discreteness finding

### 4.3 The frozen termination clause — designed fresh for this experiment
###     kind, crossing C1's Beta-law adjudication with C2's floor-test outcome

This is a genuinely different KIND of experiment from every prior branch
shape in this goal's history: real BKZ reduction feeding a distributional
comparison AND an order-statistic/exact-combinatorial check, at multiple
`(n, beta)` cells that may not all clear Stage 0. **Precedence, checked in
order; the first that matches fires ALONE for the affected scope (whole
package, or the named cell(s)):**

1. **`T-PROJNOISE-NODATA`** — fires when EITHER (a) §1's infrastructure
   re-verification fails (fpylll unavailable, batched-Babai exactness check
   fails), OR (b) Stage 0 drops every `(n, beta)` cell (§2.3), OR (c) fewer
   than 4 of the required `>= 8` draws complete within budget at a given
   cleared cell (a stated PARTIAL-DATA floor: below 4 draws, neither
   C1's nor C2's interval-based reporting convention is meaningful at that
   cell). **Scope: fires per affected cell, or for the whole package under
   (a) or (b).** MEANS: this attempt did not produce usable data at the
   affected scope, for a reason OTHER than the hypothesis's own content.
   LICENSES: citing Stage 0's own cell-by-cell benchmark results (wall-clock,
   memory, tours, delta) as a standalone, reportable infrastructure-timing
   deliverable (R-PN-OUT-1) regardless of this branch firing; licenses NO
   statement about C1 or C2's truth at the affected scope, in either
   direction. FORBIDS any claim about C1 or C2 at the affected scope, in
   either direction.
2. **`T-PROJNOISE-INSTRUMENT-MISCALIBRATED`** — fires, per affected conjunct
   and cell, when NULL-2 fails its forced-value check (C1: does not
   reproduce curve A; C2: shows deceleration or a floor). MEANS the
   instrument, not the object, is implicated. LICENSES: reporting that the
   affected conjunct's own instrument requires repair before any real-arm
   reading at that cell is trustworthy, citing NULL-2's own measured
   deviation from its forced value; licenses the OTHER conjunct's own
   finding at the same cell to stand on its own, unqualified by this
   branch, if that conjunct's own NULL-2 check passed independently. FORBIDS
   reporting any real-arm finding for the affected conjunct at that cell
   until fixed; does NOT forbid reporting the OTHER conjunct at the same
   cell if its own NULL-2 check passed independently.
3. **`T-PROJNOISE-HARNESS-ARTIFACT`** — fires when the scoped NULL-3 (§3.4)
   shows a best-of-`M_null3` gain statistically indistinguishable from (or
   exceeding, scaled by `log2(M_null3)/log2(M)`) the real arm's own
   headline effect. MEANS C1's whole effect, at that cell, is a shared-basis
   harness artifact per C1-F3. LICENSES: citing that C1's own selection
   mechanism, at that cell, has not been distinguished from a basis-reuse
   artifact by this run — a complete, informative finding about the
   mechanism's own validity at that cell, not merely an absence of result;
   licenses C2's own floor finding at the same cell to stand, PROVIDED the
   C1 artifact finding is stated alongside it (per FORBIDS below). FORBIDS
   any C1 finding at that cell; does not by itself forbid C2 reporting (C2's
   own floor claim does not depend on C1's selection mechanism being real),
   but any C2 finding at a cell where this fires must state the C1 artifact
   finding alongside it.
4. **Below this line, `T-PROJNOISE-NODATA`,
   `-INSTRUMENT-MISCALIBRATED`, and `-HARNESS-ARTIFACT` have NOT fired for
   the cell/conjunct being adjudicated.** The per-cell C1 and C2 verdicts
   (§4.2) are read directly and reported per cell.
5. **Aggregate, across all CLEARED-AND-NOT-VOIDED cells, reported only if
   they AGREE:**

       T-PROJNOISE-HOLDS-ALL       C1-HOLDS at every such cell.
                                    MEANS: the pre-registered tail model
                                    (Model B, or whichever derived curve is
                                    closer at a NEITHER-leaning cell)
                                    describes the measured left tail at
                                    every cell that cleared and was not
                                    voided by items 1-3. LICENSES: citing a
                                    single, uniform statement that the
                                    tested tail matches its pre-registered
                                    model across the full tested grid, WITH
                                    the per-cell Kolmogorov-distance and
                                    tail-quantile numbers attached, never as
                                    a bare label. FORBIDS extrapolating this
                                    agreement to any cell outside the tested
                                    `(d, beta)` grid, or to `n = 256`
                                    (standardized ML-KEM) scale, without a
                                    new, separately-commissioned measurement
                                    (this section's own "declared forward
                                    boundary" below).
       T-PROJNOISE-FAILS-ALL       C1-FAILS-BY-FACTOR at every such cell.
                                    MEANS: the measured tail departs from
                                    BOTH derived curves by a quantified,
                                    stated factor at every cell that cleared
                                    and was not voided. LICENSES: citing a
                                    uniform statement that neither model
                                    describes the tested tail at this grid,
                                    WITH the quantified departure factor per
                                    cell attached — a complete, informative
                                    negative per C1-FAILS-BY-FACTOR's own
                                    definition (§4.2), not a fatigue report.
                                    FORBIDS inferring WHY the models fail
                                    (asserting a specific alternative
                                    mechanism) beyond what is directly
                                    measured; any such inference is a new
                                    hypothesis requiring its own,
                                    separately-commissioned test.
       T-PROJNOISE-MIXED           the cells disagree on C1 (report per
                                    cell only, no aggregate stronger than
                                    "mixed, parameter-set-dependent, at
                                    this sample"). MEANS: the cells disagree
                                    on C1's own per-cell verdict. LICENSES:
                                    reporting each cell's own verdict
                                    individually, exactly as measured; no
                                    aggregate statement stronger than
                                    "mixed, parameter-set-dependent, at this
                                    sample." FORBIDS any claim of a uniform
                                    C1 verdict across the tested grid, and
                                    any silent selection of a
                                    "representative" cell to stand in for
                                    the others.

   crossed, independently, with:

       T-FLOOR-CONFIRMED-ALL       C2-FLOOR-CONFIRMED at every arm
                                    reporting. MEANS: a combinatorial floor
                                    (by the deceleration-ratio sub-test, the
                                    exact toy-cell sub-test, or both) was
                                    detected at every reporting arm, with no
                                    C2-COLLISION at any reporting arm.
                                    LICENSES: citing that C1's own left-tail
                                    reading, wherever it holds, may not be
                                    extrapolated past the floor without a
                                    stated correction — this TIGHTENS, per
                                    hypothesis_draft.yaml's own
                                    interpretation_limits, how far any
                                    unbounded-M reading (including
                                    IDEA-20260814-10e5e1's own separately
                                    dispatched arithmetic) may be pushed; it
                                    does not itself change C1's own measured
                                    verdict. FORBIDS citing the floor's own
                                    TOY-dimension value as transportable to
                                    ML-KEM scale (`d ~ 1000+`) by
                                    extrapolation.
       T-FLOOR-ABSENT-ALL          C2-NO-FLOOR at every arm reporting.
                                    MEANS: no floor was detected at any
                                    reporting arm, and the deceleration
                                    statistic was statistically
                                    indistinguishable from 1 at every
                                    reporting arm. LICENSES: citing that, at
                                    the tested scale, the continuous
                                    Beta-law order-statistic behavior is not
                                    measurably capped by CBD discreteness —
                                    a complete, informative negative per
                                    C2-NO-FLOOR's own definition (§4.2).
                                    FORBIDS extrapolating "no floor detected
                                    at toy scale" to a claim that no floor
                                    exists at ML-KEM scale — the
                                    toy-dimension exact arm cannot reach
                                    that scale by construction (§4.2's own
                                    method_ceiling).
       T-FLOOR-MIXED               disagreement, or any C2-COLLISION present
                                    (COLLISION always forces at least MIXED,
                                    never absorbed into CONFIRMED or ABSENT).
                                    MEANS: the reporting arms disagree on
                                    C2's own per-arm verdict, OR at least
                                    one reporting arm fired C2-COLLISION.
                                    LICENSES: reporting each arm's own
                                    verdict individually; where COLLISION
                                    fired, reporting it explicitly
                                    downgraded per C2-COLLISION's own
                                    handling (§4.2 — basis-effect not
                                    excluded, discreteness not established)
                                    rather than folded into either CONFIRMED
                                    or ABSENT. FORBIDS reporting an aggregate
                                    C2 verdict stronger than "mixed" when any
                                    COLLISION is present, regardless of how
                                    many other arms cleanly confirm or refute
                                    a floor.

   The full termination state is the ORDERED PAIR (C1 aggregate, C2
   aggregate), e.g. `(T-PROJNOISE-HOLDS-ALL, T-FLOOR-ABSENT-ALL)` — the
   cleanest possible reading: the marginal law holds and no combinatorial
   floor interferes at the tested cells — through
   `(T-PROJNOISE-MIXED, T-FLOOR-MIXED)` — the least decisive reading, fully
   admissible and fully reportable, per this program's own "NEITHER is an
   explicit and expected branch" discipline.

**A DECLARED FORWARD BOUNDARY.** This is the FIRST measurement of
`H-MLKEM-7d9bcc`. Whichever termination state fires, no further measurement
of THIS SAME hypothesis at THESE SAME `(n, beta)` cells under THIS SAME
protocol is licensed by this document alone as an automatic successor — a
genuinely different dimension, beta grid, or compression parameter set is a
NEW question requiring its own, separately-commissioned Coordinator
decision, matching PREREG-7 section 3.6's own convention exactly.

### 4.4 §3.3's covariate, reported separately

If run, the Spearman correlation, its confidence interval, and the
directional single-instance check are reported ALONGSIDE whichever
termination state fires, in their own outcome row (§5), and NEVER folded
into or allowed to change which termination state fires — diagnostic only,
per §3.3.

### 4.5 Repair-bar analysis — checked, not assumed, matching PREREG-7 §3.7's
###     own structure for this goal's own newly-defined criteria

`PREREG-2` §7.5 bars "a further dispersion criterion, fibre clause or gate
repair" from being introduced without being checked against a stated test —
a discipline this goal's own `hkz`/HKZ-independence lineage created for its
own admissibility-gate object and has applied to every new criterion in that
lineage since. C2's `C2-FLOOR-CONFIRMED` / `C2-NO-FLOOR` / `C2-COLLISION`
criterion (§4.2) is, on its face, closer in kind to a "dispersion criterion"
than `H-MLKEM-11aabf`'s own PREREG-7 C1/C2 criteria were (PREREG-7's own
were "an elementary case analysis," explicitly not proof-search-like) — so
this check is owed, not skippable by analogy to PREREG-7 alone.

**DOES `PREREG-2` §7.5's BAR APPLY HERE? NO — checked, not assumed, for the
following reason.** §7.5's bar targets criteria that MODIFY OR EXTEND an
EXISTING admissibility gate within the `hkz`/HKZ-independence lineage's own
object (the `D_route` instrument, the `hkz` GSA-deviation scalar, and their
own admissibility thresholds) — its purpose is to stop that lineage's own
gate from being loosened or tightened ad hoc, mid-campaign, without a
pre-registered test of the change itself. C2's floor criterion is not a
modification of that gate at all: it is a NEW criterion on a DIFFERENT
object (the order-statistic floor of the projected-error ratio under
best-of-M selection), introduced for the FIRST time in a hypothesis that
does not touch the `hkz`/HKZ-independence lineage's own instrument or
threshold in any way (§8, "does not touch, reopen, re-score" that lineage).
§7.5's bar, read by its own stated purpose, governs REPAIRS to an existing
gate, not the INTRODUCTION of an unrelated criterion on an unrelated object
— exactly the same reasoning PREREG-4 and PREREG-7 both applied when they,
too, introduced new criteria outside the `hkz`/HKZ-independence lineage's
own gate without triggering §7.5. This is a re-derivation of that reasoning
for THIS document's own new criterion, not a bare assertion that the bar
does not apply.

---

## 5. OUTCOME ROWS

| row | what it records |
|---|---|
| `R-PN-OUT-0` | section 1's infrastructure re-verification (fpylll availability/version, sampler/compression re-derivation, batched-Babai exactness check) |
| `R-PN-OUT-1` | Stage 0: per-cell feasibility benchmark (wall-clock, memory, tours, delta), cleared/dropped decision per cell; toy-floor-d feasibility sweep and chosen d |
| `R-PN-OUT-2` | Stage 1 obligation 1: per cleared cell, per draw, the full rho distribution, R_min(M) trajectory, and the 10^4-target decode-correlation subsample |
| `R-PN-OUT-3` | Stage 1 obligation 2: NULL-1, NULL-2, scoped NULL-3 (with M_null3 stated), SENS outcomes, per cell |
| `R-PN-OUT-4` | Stage 3: per-cell C1 and C2 adjudication (§4.2) |
| `R-PN-OUT-5` | Stage 3: the termination state read off R-PN-OUT-0 through R-PN-OUT-4 under §4.3's frozen precedence |
| `R-PN-OUT-6` | §3.3's GSA-fidelity covariate, if run: Spearman rho with CI and the directional single-instance check |

---

## 6. BUDGET — DERIVED FRESH FOR THIS EXPERIMENT KIND, NOT REUSED FROM ANY
##    PRIOR BATCH'S NUMBER

### 6.1 Why no prior batch's budget transfers

Task card TASK-20260814-dfaa60 states this explicitly and this document
honors it: every closed-form-estimator batch in this goal (PREREG-5 through
PREREG-7) sized its budget to a sub-minute Sage/estimator readout, and the
`hkz`/HKZ-independence lineage's own real reductions never exceeded `d = 40`
(§1 point 1, `EV-MLKEM-5aa471`). Neither number is a valid basis for `d in
{256, 512}`, `beta in {40, 55, 70}`. This budget is instead derived from
first principles, flagged as an ESTIMATE with wide uncertainty, and is
EXPECTED to be sharply corrected downward (or, if infeasible, downward in
scope) by Stage 0's own measurement before Stage 1 commits any of it (§2).

### 6.2 The derivation

- Per-basis reduction cost scales primarily with `beta` (through
  `fpylll`'s SVP-enumeration cost at each block) and with the number of
  `d/beta`-sized blocks per tour times the number of tours to convergence.
  General published experience with `fpylll`/`fplll` BKZ2.0 at `beta` in
  the 40-80 range on lattices of a few hundred dimensions ranges from well
  under a minute (small `beta`, tuned pruning) to on the order of an hour or
  more (larger `beta`, untuned/default enumeration) per basis on a single
  modern CPU core. **This is general background knowledge, not a specific
  citation, and is flagged as such** — no paper is cited for a specific
  number, and Stage 0 (§2) exists precisely because this estimate is not
  trustworthy enough to budget against directly.
- `PER_BASIS_FEASIBILITY_CAP = 3600` s (Stage 0, one basis per cell) is set
  at the upper end of that published range, generously.
- `PER_BASIS_STAGE1_CAP = 14400` s (4 hours) is set with a 4x margin above
  the feasibility cap, to absorb basis-to-basis variance across the `>= 8`
  draws Stage 0's own single sample cannot see.
- WORST-CASE CEILING (never expected to be reached in full, stated so no
  later reader mistakes it for an expected runtime): 6 cells x 8 draws x
  `PER_BASIS_STAGE1_CAP` = 691,200 s (~192 hours, ~8 days), sequential,
  single worker (no `maximum_workers > 1` is declared — the template's own
  gating rule requires a prior `parallel.verify_determinism` pass this
  protocol does not have, and none is commissioned here).
- Target generation and batched-Babai cost, by contrast, is CHEAP: `O(d^2)`
  per target with BLAS batching, `d <= 512`, `M <= 2^22` targets — on the
  order of `10^11`-`10^12` floating-point operations per basis, expected to
  complete in seconds to low minutes per basis on a modern BLAS backend,
  and is NOT the dominant cost.
- The toy-floor exact/certified-gap arm (`d <= 20`) is small (exhaustive
  search at `d <= 20`, capped at `TOY_FLOOR_FEASIBILITY_CAP = 900` s total)
  and is absorbed inside the ceiling below with margin.
- The scoped `M_null3 = 64` NULL-3 draws (§3.4) are NOT small relative to
  the main grid and are NOT already absorbed in a ceiling sized only for the
  main arm — an earlier version of this section asserted they were; that
  claim was checked against §3.4's own numbers and found false, and is
  corrected here rather than left standing. NULL-3 requires up to `6 cells x
  64 draws = 384` additional BKZ reductions, EIGHT TIMES the main arm's own
  `6 cells x 8 draws = 48` reductions. At NULL-3's own
  `PER_BASIS_FEASIBILITY_CAP = 3600` s per-draw cap (§3.4 — cheaper than the
  main arm's `14400` s cap, since NULL-3 draws are single-target with no
  full-grid generation), NULL-3's own worst case is `6 x 64 x 3600 =
  1,382,400` s. Combined with the main arm's own worst case (`691,200` s
  above), the HONEST worst-case ceiling for this entire protocol is
  `691,200 + 1,382,400 = 2,073,600` s (`576` CPU-hours, `~24` days
  sequential single-worker) — not the `700,000` s an earlier version of §6.3
  declared. §6.3 below states the corrected ceiling.

### 6.3 The frozen budget

    wall_clock_seconds_total (outer ceiling, main arm + NULL-3, honest
      worst case per section 6.1's own corrected derivation): 2073600
      (~576 hours, ~24 days)
    wall_clock_seconds_total (main arm only, 6 cells x 8 draws x
      wall_clock_seconds_per_basis_reduction_stage1): 691200 (~192 hours)
    wall_clock_seconds_total (NULL-3 only, 6 cells x 64 draws x
      wall_clock_seconds_per_basis_reduction_null3): 1382400 (~384 hours)
    wall_clock_seconds_per_basis_reduction (Stage 1 cap, main arm draws): 14400
    wall_clock_seconds_per_basis_reduction (Stage 0 cap, and NULL-3's own
      per-draw cap -- see section 3.4): 3600
    wall_clock_seconds (toy floor feasibility sweep, Stage 0): 900
    maximum_memory_gb: 16
      -- dominant risk is holding all 2^20-2^22 targets x d coordinates in
      memory at once (up to ~16 GB at n=128, M=2^22, 8-byte floats); STREAMED
      / CHUNKED target processing is a REQUIRED implementation choice, not
      an optimization -- an implementation that holds the full target array
      resident is an implementation defect if it exceeds this cap, not a
      valid basis for a larger memory request.
    maximum_cpu_hours: 576  (== wall_clock ceiling, single worker, no
      parallelism verified or declared)
    maximum_workers: 1 (declared explicitly; NOT raised above 1 -- no prior
      `parallel.verify_determinism` pass exists for this lattice code)

**THIS IS A WORST-CASE CEILING, NOT AN EXPECTED RUNTIME.** Stage 0 (§2)
exists precisely to replace it with realistic, per-cell measured numbers
before Stage 1 or NULL-3 commit their own full grids (§2.3); §6.1's own
"general background knowledge" range makes an expected runtime far below
this ceiling plausible, but nothing in this document asserts a tighter
expected figure than the honest worst case above.

**STOP RULE, STATED SO A LATER COORDINATOR CANNOT MISS IT.** If Stage 0's
own measured per-basis times, linearly extrapolated to the full `>= 8`-draw
main-arm grid AND the `64`-draw NULL-3 grid on the cleared cells, would
exceed the outer ceiling above, NEITHER Stage 1 NOR NULL-3 silently
truncates `M` below `2^20` (that would violate `3d71ca`'s own frozen `>=
2^20` floor and produce an uninterpretable result). Instead the LATER
Coordinator session dispatching Stage 1 (a separate act from this drafting
task, per the task card's own "What this task does not do") must choose
explicitly, and record which, for EACH of the main arm and NULL-3
independently: (a) reduce the number of independent draws per cell — for
the main arm, not below a stated floor of 4 (below which
`T-PROJNOISE-NODATA` fires for that cell per §4.3 item 1); for NULL-3, not
below a stated floor of 8 (matching the main arm's own COMP interval size,
below which NULL-3's own scaled comparison in §3.4 loses interval-reporting
discipline); or (b) drop the highest-`beta` cell(s) entirely, for the main
arm and/or NULL-3 independently, and report the tested subset honestly. This
document does not pre-choose between them, and does not pre-choose whether
the main arm and NULL-3 are cut on the same schedule.

---

## 7. GUARDS AND COULD-NOT-FAIL ARRANGEMENTS

### 7.1 Could-not-fail check on the Beta-versus-chi-square comparison

Would hold if Model A and Model B were fixed by construction to agree, or if
the tested `M`/`beta`/`d` combinations could not, even in principle, resolve
their deviation separation. **WE ARE NOT**: the two models are genuinely
distinct predictions (`3d71ca`'s own H1 statement), differing by the factor
`sqrt(1 - beta/d)` in the tail deviation `(1 - x)` at every tested cell.
CORRECTED FROM AN EARLIER DRAFT, WHICH CITED `beta/d = 0.4` — no `(beta, d)`
pair in this protocol's own scope (`beta in {40, 55, 70}`, `d in {256,
512}`) equals `0.4`; the six actual ratios are `40/512 = 0.078`, `55/512 =
0.107`, `70/512 = 0.137`, `40/256 = 0.156`, `55/256 = 0.215`, `70/256 =
0.273`, giving `sqrt(1 - beta/d)` deviations of roughly `4.0%` to `14.7%`
across the tested grid (computed directly from this document's own §0's
stated formula, not from `3d71ca`'s stale illustrative example) — smaller
than the `22.5%` figure an earlier draft transcribed from `3d71ca`'s own
illustrative `beta/d = 0.4` point without checking it against this
protocol's OWN actual cells, repeating exactly the class of error
`EV-MLKEM-159715` already recorded a lesson against (a transcribed premise
must be re-verified against the actual construction being run, not assumed
from the source's stated example). WHAT IS NOT CLAIMED HERE: this document
does not independently re-derive whether a `4.0%`-`14.7%` deviation at
`M = 2^20` clears `3d71ca`'s own "several empirical standard errors"
statistical-power bar at EACH of the six actual cells — that derivation
requires `3d71ca`'s own `minimum_effect` methodology applied cell-by-cell,
which this drafting task did not reproduce and flags here as OWED, not
performed. Whoever notarizes this document should either perform that
per-cell power check before freezing, or accept that the smallest-deviation
cells (`beta = 40`, either `d`) may resolve the separation less cleanly than
the larger-`beta` cells and should be read with that in mind. `C1-NEITHER`
remains an explicit, licensed, non-defect branch (§4.2) regardless of the
outcome of that check.

### 7.2 Could-not-fail check on the floor test

Would hold if the exact/certified-gap search were guaranteed to find a
floor regardless of input, or guaranteed not to. **WE ARE NOT**: NULL-2's
own forced-zero-floor requirement (§3.2 item 1) is a real, checkable,
FAILABLE control precisely because a buggy "always reports floor" pipeline
would fail it, and the real-CBD arm's floor outcome is not fixed by
construction either way (`8f8f45`'s own `predictions` state both a positive
and a clean-negative outcome as complete, licensed results).

### 7.3 The section-1 and Stage-0 guards

Covered in full in §1 and §2.3; both route to `T-PROJNOISE-NODATA` rather
than to any substantive C1/C2 verdict, at the affected scope only.

### 7.4 No lattice reduction beyond what is declared

Every reduction in this protocol is `fpylll` `BKZ`-`beta` at `beta in {40,
55, 70}` on `d in {256, 512}` (main arms) or plain LLL/exhaustive search at
`d <= 20` (toy floor arm) or `beta`-free single-target reductions at the
scoped NULL-3's own `M_null3 = 64` draws (§3.4). No sieving, no enumeration
beyond `fpylll`'s own BKZ-internal SVP calls, and no reduction above `d =
512` occurs anywhere in this document.

---

## 8. WHAT THIS DOCUMENT DOES NOT LICENSE, STATED BEFORE ANY RUN

This document does not touch, reopen, re-score, or reference the `hkz`/
HKZ-independence lineage's own admissibility-gate object in any way beyond
reusing its "hkz" scalar's mathematical DEFINITION for §3.3's optional
covariate (explicitly licensed for reuse under this program's own
established convention — PREREG-5 section 2.2 point 3, "the observable's own
mathematical definition ... is not code-sharing"). This document's outcome,
whichever termination state fires, does NOT close, pause, or complete
`GOAL-MLKEM-005` — it is one measurement of `RQ-MLKEM-001`'s own hypothesis,
against the goal's unbounded `campaign_budget` and `completion_criteria`
(this document alone can, at most, satisfy C3; C1 requires a stated numeric
bound this document does not itself compute — that is a separate, later
arithmetic act, potentially `IDEA-20260814-10e5e1`'s own out-of-scope task,
consuming this document's own C3 output). It does not change
`H-MLKEM-7d9bcc`'s status. It does not license any claim about ML-KEM
security, any FIPS 203 parameter set's deployed safety, or any attack cost,
whichever termination state fires.

---

## 9. SCOPE, INDEPENDENCE, AND WHAT THIS DOCUMENT CANNOT DO

**SCOPE.** `q = 3329`; `n in {64, 128}`, `k = 2`, `d in {256, 512}`;
`beta in {40, 55, 70}`; `eta1 = 3`, `eta2 = 2`; `d_u = 10`, `d_v = 4`; toy
floor `d in {8, 12, 16, 20}`. NOT IN SCOPE: any `n = 256` (standardized
ML-KEM) instance; any real ML-KEM key, ciphertext, secret, or decapsulation
call beyond the synthetic toy-shaped instances this protocol constructs; any
timing side channel; any claim about `IDEA-20260814-10e5e1`'s own separately
dispatched arithmetic.

**CLAIM TIER, RESTATED.** TOY throughout, per the mechanical field-bit-size
rule (`q = 3329` is 12 bits). NEITHER conjunct's toy tier licenses a
universal-impossibility or crypto-scale-safety claim by label alone.

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL**, exactly as every prior
document in this goal's lineage states; `AGENTS.md` rule 12 remains unmet
and unwaived and is not waived here.

**THIS DOCUMENT DOES NOT RE-LITIGATE ANY PRIOR FINDING IN THIS GOAL, AND ITS
EVENTUAL MEASUREMENT OUTCOME EITHER WAY DOES NOT CLOSE, PAUSE, OR COMPLETE
`GOAL-MLKEM-005`.**

---

## 10. AUTHORSHIP GAP, DECLARED RATHER THAN NARRATED CLOSED

The Coordinator session that wrote this file **held no shell** (task card
TASK-20260814-dfaa60: "You hold no shell — you cannot run git or
tools/allocate_id.py"). It ran no git command, computed no hash, cloned no
`fpylll`, and ran no Python. It DID read committed repository files directly
with a read-only tool (`IDEA-20260805-3d71ca.yaml`, `IDEA-20260814-8f8f45.yaml`,
`IDEA-20260814-137f68.yaml`, `IDEA-20260814-10e5e1.yaml`,
`IDEA-20260814-a609eb.yaml`, `GOAL-MLKEM-005.yaml`, `RQ-MLKEM-001.yaml`,
`H-MLKEM-11aabf.yaml`, PREREG-7 in full, `docs/inventor-protocol.md`,
`docs/target-result-profile.md`, `docs/claims-and-verification.md`,
`templates/research-records.md`, `EV-MLKEM-5aa471.yaml`,
`EXP-MLKEM-007/specification.yaml` and its `RUN-MLKEM-028/manifest.yaml`),
and transcribed both source ideas' own frozen predictions, controls,
heuristics, and `proof_search_map` fields VERBATIM where stated as such
above, rather than recomputing them. It performed NO independent arithmetic
beyond §6's OWN EXPLICITLY FLAGGED budget derivation, which is stated as an
estimate throughout and is NOT presented as a measurement. The budget
numbers in §6 are the single most likely thing in this document to be wrong
by a large factor; Stage 0 (§2) exists specifically to correct them before
any Stage-1 compute is spent. If a reviewing session's own reading of
`fpylll`'s published performance characteristics disagrees materially with
§6.2's estimate — corrected in full where the independent review found a
genuine defect (§6.2, §6.3, §7.1, and elsewhere; see "Status of this
document" above) — that correction is recorded IN this frozen text rather
than left for a future reader to catch, per the review-before-approval
discipline this notarization itself is the outcome of.

`prereg_sha256.txt` is generated and committed alongside this file by the
notarizing archive task, by the orchestrating session which holds a shell,
matching every prior `PREREG-*` of this goal.

**END OF FROZEN TEXT.**
