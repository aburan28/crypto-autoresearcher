# PREREGISTRATION SKELETON — FLOOR-MAGNITUDE ADJUDICATION (FM CASCADE), SCOPED SUCCESSOR REVISION

Authored under TASK-20260904-30f2f7 (idea-generator, BATCH-e479db, GOAL-AES-003,
RQ-AES-003), revising the TASK-20260903-92ade4 skeleton to discharge SR-2, SR-3,
SR-1, SR-6 and to carry SR-4, SR-5, SR-7, SR-8. **This is a skeleton, not a
preregistration.** It becomes binding only if a successor batch adopts it VERBATIM
under its own opening Coordinator decision and commits it write-once, pre-arm, in
that batch's stage-0 producer task.

**THIS DOCUMENT AUTHORIZES NOTHING.** No experiment, no arm, no exposure increase,
no build change, no status change, no evidence record, no knowledge promotion, no
successor batch. Zero arms were executed to produce it.

**RAT-3 DISCIPLINE, WITH EXTENDED SCOPE (SR-1).** Every branch conjunct AND every
branch's NOT-licensed prohibition text below is written out IN FULL. This text is
the binding version. No other section of any artifact may paraphrase a branch
conjunct or a NOT-licensed prohibition; where another document names a branch or
composes a fired branch's outcome sentence, it must quote this file or point at it.
This extended scope binds any downstream evidence, decision, or knowledge-promotion
record that composes a sentence describing a fired branch's outcome, and closes the
paraphrase gap named by TASK-20260903-4fdf77 NARROW-AUDIT-6. The inverted
CC3-NONMONO paraphrase (DEV-S2b-1, ratified as RAT-3 by DEC-20260903-be4472) is why
this rule exists.

**BLINDNESS-ENABLING SEPARATION.** No statistical derivation appears in this file.
Thresholds are stated as RULES (a test, a level, an interval containment, a named
null-law quantile), never as derived numbers. Every derived number — expected
counts, confidence intervals, power, count thresholds, false-positive rates, margin
decimals, cost — lives only in
`coordination/goals/GOAL-AES-003/batches/BATCH-e479db/tasks/TASK-20260904-30f2f7/pooled-exposure-pricing.json`.

---

## Section 0 — Verbatim standing discipline

The following are quoted verbatim from committed ledger records and bind every
sentence a successor batch may compose.

### AMEND-1 (DEC-20260901-6f9de3; standing gate for the frozen 582ea9 lineage, ratified as RAT-2 of DEC-20260902-7ad3d9)

> PROSPECTIVE amendment for successor batches under the frozen 582ea9 instrument
> lineage: the branch-1 conjunct 'hit_overflow > 0 on any analysis-bearing receipt
> -> invalid_measurement' is rescoped to 'counter INCONSISTENCY on an
> analysis-bearing receipt -> invalid_measurement', where counter inconsistency
> means (a) overflow != hits − threads×HIT_LOG_CAP, or (b) any cap-independent
> counter (hits, W, ewhist_hit) disagrees with its internal identities, or (c) any
> analysis-bearing quantity is derived from the capped detail log rather than the
> counters. Pure cap truncation of the detail log with all counter identities intact
> is NOT a gate failure. This amendment applies to batches opened AFTER this
> decision; it does not re-adjudicate BATCH-7b798d, whose readings remain
> unvalidated as shape evidence (red-team RT3-A: no post-hoc rescue).

### NARROW-1 (DEC-20260902-7ad3d9)

> Red-team RT-A adopted: every successor record must carry the floor-is-alive
> finding and the bar on extinction-by-k=4 sentences. MONOTONE-DECAY is a
> band-trajectory statement.

### NARROW-2 (DEC-20260902-7ad3d9)

> Red-team RT-B adopted: no count-level decay sentence without second seeds at the
> named k; the count-decay magnitudes (84.90, 8786.5) are primary-seed-only until
> replicated.

### NARROW-3 (DEC-20260902-7ad3d9)

> Red-team RT-C adopted: determinism-discipline — exact re-runs under identical
> seeds are instrument determinism and must never be recorded as independent
> replication; the only independent draws of this batch are the k=1 and k=4 second
> seeds.

### NARROW-4 (DEC-20260903-be4472)

> RT-B2 adopted: (3,4] coexists with a live floor; no cliff-at-4, completion, or
> sub-sub-interval reading; the multiplicative prior stays BROKEN-AUTHORITY despite
> its ~4% proximity to h(3) (rule-8 successor bait, never restored authority); the
> extended-family label must disclose k=12 as frozen-never-measured.

### NARROW-5 (DEC-20260903-be4472)

> RT-N4 adopted: k=8's two draws establish band-level floor stability ONLY; no count
> verdict at k=8; the count rule's pre-arm domain was k=2 and its non-application to
> k=8 is domain discipline, not cherry-picking (proves-too-much record kept: the
> 13-vs-18 ratio 1.3846 would formally read COUNT-DISAGREE if applied).

### RAT-5 / CORR-20260903-d3cab5

The exact Garwood 95% confidence interval for h(4)_531001 = 17 hits is
**[9.903, 27.219]**. The figure 29.2 carried in EV-AES-868db1 OBS-2 is a recorded
citation error and must not reappear in any successor artifact.

---

## Section 1 — Pre-arm domain (FIXED BEFORE ANY ARM RUNS)

Every element of this section is committed write-once before the first invocation.
An arm run outside this domain is INADMISSIBLE and its receipt may not enter any
conjunct.

1. **Question.** Is the residual floor, over the tested points, (a) a constant
   nonzero plateau, (b) still decaying with k, or (c) indistinguishable from the
   operative comparator? Nothing else.
2. **Cell.** amask = 1, smask = 1. One probe cell.
3. **Round count.** r = 5 for every floor arm; r = 6 for every null-object arm;
   these two sets never mix inside a conjunct.
4. **Primary points.** k = 4 and k = 16, with n_4 = n_16 = n arms each.
5. **Secondary point.** k = 8, n_8 arms, DECLARED REPORT-ONLY. No conjunct reads it.
   No count verdict at k = 8 is drawn in any branch (NARROW-5 discipline extended
   prospectively).
6. **Exposure.** Exactly 2^30 trials per arm. Unchanged from the committed lineage.
   No 2^32 arm is run.
7. **Schedule pin.** PIN-T0 throughout. SCOPE-1 attribution binds.
8. **Threads.** 4 per arm. HIT_LOG_CAP 256.
9. **Build.** The FROZEN build only: source
   `ec748cef...`, binary `74e3d65c...`. NOT the
   frozen-build-plus-declared-extension (`3ccc377c...`). All points used are already
   on the frozen arm-token whitelist and in the committed `R3_table_freeze.json`, so
   this design makes NO source change, requires NO declared diff, requires NO
   Gate-0x extended rebuild, and creates NO new freeze commitment. If a successor
   ever changes the per-arm exposure or the point grid, THAT successor needs a new
   freeze commitment with a pre-arm digest; this design deliberately avoids it.
10. **Seats (armids).** k = 4 → armid 4; k = 8 → armid 6; k = 16 → armid 8; r = 6
    dead anchor → armid 1; k = 0 ramp-zero anchor → armid 5. Seat-fixed convention:
    the seat's armid is fixed and the seed varies, mirroring the committed
    second-seed precedent.
11. **Seed list.** Committed write-once, pre-arm, in full. Floor arms draw from a
    declared seed block; null arms draw from a DISJOINT declared seed block. An arm
    run at a seed not on the committed list is inadmissible. No data-dependent seed
    selection may enter at any point.
12. **Run order.** Floor arms are run INTERLEAVED across the two primary points
    (k = 4, k = 16, k = 4, k = 16, …), never blocked by point. The interleaving is
    committed pre-arm. Rationale: any wall-clock or thermal drift in the instrument
    then acts as a common-mode effect on both points and cancels in the conditional
    test, and a run-order trend becomes separately testable. A blocked order would
    confound drift with k and is barred.
13. **Levels.** alpha = 0.05 two-sided for the floor-versus-floor test;
    alpha_N = 0.001 one-sided for the comparator test; alpha_H = 0.01 for the
    homogeneity test; alpha_O = 0.01 for the run-order test.
14. **Equivalence resolution.** rho* = 1.5, committed pre-arm.
15. **Minimum detectable effect.** rho_1 = 2, committed pre-arm.
16. **Test data.** The test statistic is computed from NEW ARMS ONLY. The five
    committed readings (17, 21, 13, 18, 12) are NOT part of any conjunct. They are
    used only for the three purposes declared in
    `pooled-exposure-pricing.json` under
    `measured_null_object_pricing.committed_readings_use_inventory`: (U1) bounding
    the planning constant before any arm runs; (U2) a declared REPORT-ONLY
    consistency comparison AFTER the branch has fired; and (U3, SR-4) calibrating
    the Branch G4 hard-gate threshold from the committed k = 16 reading's exact
    Garwood lower bound. No other use exists.
17. **Two-sided exact-test convention (SR-6).** The binding convention for every
    exact two-sided conditional binomial test of `pi = 0.5` in this file is the
    MINIMUM-LIKELIHOOD convention: the p-value is the sum of all `Binomial(T, 0.5)`
    probability-mass values not exceeding the observed mass value, matching
    `scipy.stats.binomtest(..., alternative='two-sided')` with its default exact
    method. The equal-tail convention is named but NOT binding. The two conventions
    can disagree near a branch boundary: at a discrete total whose rejection
    threshold lies within one mass atom of alpha = 0.05, the two p-values can
    straddle 0.05, flipping routing between Branches 2/3 and Branches 4/5. Any
    successor that substitutes equal-tail must re-price the branch thresholds
    pre-arm; otherwise the substitution is a rule change, not an evaluation choice.
18. **Periodic custody checkpoints (SR-5).** In addition to the pre-arm and
    post-arm checks of Branch G1, build-identity and KAT re-verification
    checkpoints run every four completed arms OR every 3600 seconds of batch
    wall clock, whichever comes first. Each checkpoint re-checks the build
    identity hash, the KAT pin receipts, and the table-freeze digest against the
    committed values. A mismatch at a checkpoint routes to FM-GATE-FAIL with
    attribution bounded to the arms completed since the last passing checkpoint.

---

## Section 2 — Admissibility preconditions

An arm's receipt is ADMISSIBLE to the floor cascade if and only if ALL of the
following hold. These are conjuncts, not hygiene; Section 6 shows that the rule's
correctness on known-false objects rests on them.

- **P1** the arm's round count is r = 5;
- **P2** the arm's k is in the pre-arm domain of Section 1, item 4 (primary) or
  item 5 (secondary, report-only);
- **P3** the arm's exposure is exactly 2^30 trials;
- **P4** the receipt is UNSATURATED, i.e. `hit_overflow == 0` and
  `logged_detail_records == hits`;
- **P5** the arm's (seed, armid) pair is on the pre-arm committed list of
  Section 1, items 10 and 11.

**FM-INADMISSIBLE-INPUT.** If any receipt offered to the floor cascade fails any of
P1–P5, that receipt is excluded, the exclusion is recorded with the failing
precondition named, and if the exclusion removes any arm from a primary point the
cascade HALTS with no floor sentence composed. An exclusion is never silently
absorbed and is never replaced by a substitute arm run after the fact.

---

## Section 3 — Gates, evaluated in fixed order before anything else

**Branch G1 — FM-GATE-FAIL.** Fires if ANY of the following holds on ANY
analysis-bearing receipt of the batch: counter INCONSISTENCY as defined verbatim in
AMEND-1 above, evaluated in the saturation-aware form `overflow == hits −
logged_detail_records` where `logged_detail_records == min(hits, threads ×
HIT_LOG_CAP)`; or the build-identity direct hash does not match the frozen source
and binary of Section 1 item 9; or the KAT pin receipts are not byte-identical to
the committed lineage KAT receipts; or the pre-arm, periodic, or post-arm
table-freeze re-verification against the committed `R3_table_freeze.json` reports
any mismatch; or the post-arm source and binary diff against the snapshot-bound
build is non-empty; or any periodic custody checkpoint required by Section 1 item
18 (SR-5) fails. The periodic checkpoints run every four completed arms or every
3600 seconds of batch wall clock, whichever comes first, and re-check the build
identity hash, the KAT pin receipts, and the table-freeze digest. **Consequence:**
`invalid_measurement`, HALT, repair, never evidence about the floor (AGENTS rule
5). A periodic-checkpoint mismatch is attributed to the arms completed since the
last passing checkpoint. A budget or tooling failure is `resource_exhaustion` or
infrastructure failure and is likewise never a finding about the floor.

**Branch G2 — FM-ANCHOR-FAIL.** Fires if the k = 0 ramp-zero anchor arm does not
read hits = 2^30 exactly, or its excess ratio is not 1.0 exactly, or W = 3 does not
hold on 100 percent of nontrivial trials, or its counter identities are not exact
under the saturation-aware form (its receipt is saturated by construction and that
saturation is legal under AMEND-1). **Consequence:** `invalid_measurement`, HALT.
This arm is the AMEND-1 proves-too-much control and it is analysed FIRST among the
batch's alive readings.

**Branch G3 — FM-DEAD-ANCHOR-FAIL.** Fires if any r = 6 matched dead-anchor arm
reads at or above the committed lineage tripwire of 9 hits. **Consequence:** a
boundary falsifier of the sealed verdict; HALT and escalate to claim-changing
review (AGENTS rule 12), never a floor sentence.

**Branch G4 — FM-NULL-CONTROL-FAIL.** Fires if the POOLED count over the null-object
arms reaches the preregistered hard threshold, defined as the count at which the
pooled measured null rate reaches the exact Garwood lower bound of the committed
single-arm k = 16 reading. **SR-4 disclosure:** this threshold calibration is the
third disclosed use of the five committed readings (U3 in
`pooled-exposure-pricing.json`
`measured_null_object_pricing.committed_readings_use_inventory`). It is a
gate calibration, not an evidential input; it enters no branch conjunct, no test
statistic, no equivalence criterion and no composed sentence. **Consequence:** the
measured null is no longer separable from floor magnitude; HALT, instrument review,
and NO floor sentence of any kind may be composed. The numeric threshold at the
adopted null exposure is fixed pre-arm from `pooled-exposure-pricing.json` and
written into this file's adopted copy.

---

## Section 4 — Comparator-setting step (not a branch)

After G1–G4 pass and before the cascade of Section 5 is evaluated:

1. Compute `U_null`, the EXACT one-sided 95 percent Garwood upper bound on the
   pooled measured null rate from the r = 6 null-object arms, per 2^30.
2. Set the **operative comparator** `lambda_op = max(lambda_0, U_null)`, where
   `lambda_0 = 1.0` per 2^30 is the campaign's analytic comparator under the frozen
   excess_E convention.
3. Every branch statement in Section 5 is evaluated against `lambda_op` and every
   composed sentence DISCLOSES both `lambda_0` and `U_null` and states which one was
   operative.

This step is what makes the measured null object a control rather than a decoration:
if the instrument's own null is above the analytic comparator, the whole cascade is
restated against the larger value and the resulting sentences are weaker. Both
outcomes are informative; neither is a failure.

---

## Section 5 — The floor-magnitude cascade

Evaluated in FIXED ORDER after Sections 2, 3 and 4. The branches are mutually
exclusive and exhaustive over the admissible readings. Every branch is written out
in full. Where a branch names a test, the BINDING computation is the exact one; no
normal approximation may be substituted at evaluation time.

### Step 5.0 — Homogeneity, evaluated BEFORE any pooling

**Branch H — FM-OVERDISPERSED.** Fires if, at EITHER primary point k in {4, 16}, the
Poisson dispersion index of that point's per-arm counts,
`D_k = sum_j (X_kj − Xbar_k)^2 / Xbar_k`, exceeds the chi-squared critical value on
`n_k − 1` degrees of freedom at alpha_H = 0.01.

**Consequence:** between-arm heterogeneity at that point exceeds the Poisson model,
so exposure additivity (heuristic H3) fails and the arms may not be pooled. NO
pooled magnitude sentence of any kind is composed. The per-arm tuples are recorded
individually, never smoothed and never pooled. This is a DETERMINATE FINDING about
the instrument's seed behaviour at floor magnitude, not a halt of the batch, and it
names its successors: a larger n to estimate the heterogeneity, and a re-priced
design that carries the inflation explicitly.

**Licensed by this branch:** that the per-arm floor counts at the named point are
over-dispersed relative to Poisson at alpha_H, with the realized dispersion index
and its degrees of freedom stated.

**NOT licensed by this branch:** any magnitude sentence; any plateau, decay,
extinction, completion or comparator sentence; any statement that the floor is or is
not constant; any statement about k = 8, k = 12 or any point outside the domain.

### Step 5.1 — Branch 1, FM-COMPARATOR-INDISTINGUISHABLE

**Conjunct, in full.** Fires if BOTH of the following hold: the pooled count at
k = 4 fails to reject the hypothesis `lambda_4 = lambda_op` under a one-sided exact
Poisson test against mean `n_4 × lambda_op` at alpha_N = 0.001; AND the pooled count
at k = 16 fails to reject the hypothesis `lambda_16 = lambda_op` under a one-sided
exact Poisson test against mean `n_16 × lambda_op` at alpha_N = 0.001.

**Consequence and routing.** The batch records that at the realized pooled exposure
neither primary floor point is distinguishable from the operative comparator. Because
this outcome would contradict five committed readings that together carry 81 hits
where the comparator predicts about 5, it ALSO routes to instrument review before
any interpretive sentence is composed.

**Licensed by this branch:** exactly one sentence — "at pooled exposure n × 2^30 per
point, cell (1,1), r = 5, PIN-T0, neither k = 4 nor k = 16 is distinguishable from
the operative comparator lambda_op at alpha_N" — together with the instrument-review
routing and the disclosed contradiction with the committed readings.

**NOT licensed by this branch:** ANY extinction sentence. "Indistinguishable from the
comparator at this exposure" is a statement about resolution, not about absence, and
NARROW-1 bars the extinction reading in this branch as in every other. Also not
licensed: any completion sentence, any cliff-at-4 reading, any statement that the
decay finished, any statement about k = 8, k = 12 or any untested k, and any
re-composition of the immutable SH2-MONOTONE-DECAY verdict.

### Step 5.2 — Branch 2, FM-DECAY-CONTINUES

**Conjunct, in full.** Fires if Branch 1 did not fire AND the exact two-sided
conditional binomial test of `pi = 0.5` on the pair `(T_4, T_16)`, conditional on
`T = T_4 + T_16` and evaluated at equal exposures `n_4 = n_16`, rejects at
alpha = 0.05, AND the realized `pi_hat = T_4 / T` is strictly greater than 0.5.

**Consequence and routing.** The residual floor is still decaying between k = 4 and
k = 16 at count level. The estimated rate ratio `rho_hat` and its exact
Clopper-Pearson-mapped 95 percent interval are recorded.

**Licensed by this branch:** that over the two tested points k = 4 and k = 16, in
cell (1,1) at r = 5 under PIN-T0 at the realized pooled exposure, the floor rate at
k = 4 exceeds the floor rate at k = 16 at alpha = 0.05, with the ratio and its
interval named; and that the floor is alive at both points (NARROW-1 carried).

**NOT licensed by this branch:** any statement about the SHAPE of the decay between
the two points (no intermediate point is in the primary domain); any statement about
k = 8 at count level; any statement about k = 12, which is frozen-never-measured; any
extrapolation to k > 16 or to any untested k; any extinction, completion or
cliff-at-4 sentence; any rehabilitation of the broken-authority multiplicative prior;
any dilution-only attribution (SCOPE-1 binds); any whole-curve sentence.

### Step 5.3 — Branch 3, FM-INVERTED

**Conjunct, in full.** Fires if Branch 1 did not fire AND the exact two-sided
conditional binomial test of `pi = 0.5` on the pair `(T_4, T_16)` rejects at
alpha = 0.05, AND the realized `pi_hat` is strictly less than 0.5.

**Consequence and routing.** A determinate rate INVERSION at floor magnitude: the
k = 16 floor rate exceeds the k = 4 floor rate. This is a count-level non-monotone
finding scoped to the two tested points. The committed band-level verdict
SH2-MONOTONE-DECAY is a BAND-trajectory statement and is untouched and unre-composed
by this branch; a count-level inversion inside the RESIDUAL band is not a band rise.

**Licensed by this branch:** the inversion at the two tested points with its ratio
and interval, and the explicit statement that the band verdict is unaffected.

**NOT licensed by this branch:** any re-composition of SH2-MONOTONE-DECAY; any claim
of a band rise; any statement beyond the two tested points; and all of the exclusions
listed under Branch 2.

### Step 5.4 — Branch 4, FM-PLATEAU-CONSISTENT

**Conjunct, in full.** Fires if ALL of the following hold: Branch 1 did not fire;
AND the exact two-sided conditional binomial test of `pi = 0.5` on the pair
`(T_4, T_16)`, using the binding minimum-likelihood convention of Section 1 item
17, does NOT reject at alpha = 0.05; AND the exact 95 percent interval for the rate
ratio `rho = lambda_4 / lambda_16`, obtained by mapping the exact Clopper-Pearson
interval for `pi` through `rho = (pi / (1 − pi)) × (n_16 / n_4)`, is entirely
CONTAINED in the preregistered equivalence interval `[1 / rho*, rho*]` with
`rho* = 1.5`; AND, at BOTH primary points k in {4, 16}, the Poisson dispersion
index `D_k = sum_j (X_kj − Xbar_k)^2 / Xbar_k` is strictly below the margin
threshold `c_margin = chi2_{0.95}(n_k − 1)`, where the Branch-H critical value is
`c_gate = chi2_{0.99}(n_k − 1)`. This final conjunct is the SR-3 remedy (option a):
it requires AFFIRMATIVE homogeneity evidence, not mere failure to reject Branch H.

**The containment conjunct is not optional and may not be dropped.** A test that
merely fails to reject licenses NOTHING about a plateau; absence of evidence for
decay is not evidence for constancy. Without the containment conjunct this branch
would convert an underpowered result into a positive claim, which is the precise
failure NARROW-1 and NARROW-4 bar.

**The SR-3 margin conjunct is not optional and may not be dropped or moved
post-data.** The threshold is a named quantile of the dispersion index's null
reference law and is fixed pre-arm; it consults no realized reading and no
red-team object. Its satisfiability under the homogeneous null and its effect on
the branch's firing rate are derived in `pooled-exposure-pricing.json`
`sr3_remedy` and are not restated here.

**Licensed by this branch:** exactly one sentence — "over the two tested points
k = 4 and k = 16, in cell (1,1) at r = 5 under PIN-T0 at the realized pooled
exposure, the floor rate ratio is confined to [1/1.5, 1.5]; the floor is
PLATEAU-CONSISTENT AT RESOLUTION 1.5" — together with the realized interval, the
operative comparator, the floor-is-alive statement (NARROW-1), and the SR-2
disclosed plateau-heterogeneity false-positive bound carried from
`pooled-exposure-pricing.json` `plateau_heterogeneity_sensitivity`. Every composed
sentence under this branch MUST carry that bound as a disclosure.

**NOT licensed by this branch, itemised because this is where the branch is most
likely to be over-read:**
- NOT "the floor is constant". The claim is confinement of a ratio to a stated
  interval at a stated resolution, nothing more.
- NOT "the decay has ended", NOT "the decay completes", NOT "the excess has reached
  its floor" — none of these is decidable from two points at resolution 1.5.
- NOT any extinction sentence (NARROW-1). A plateau at a rate far above the
  operative comparator is the OPPOSITE of extinction.
- NOT a cliff-at-4 reading, NOT a sub-sub-interval reading inside (3,4] (NARROW-4).
- NOT a statement about k = 8 at count level (NARROW-5 discipline), NOT any statement
  about k = 12 (frozen-never-measured), NOT any statement about untested k.
- NOT a mechanism. **A constant excess that does not decay as the parameter meant to
  destroy it increases is the canonical signature of a MEASUREMENT ARTIFACT**
  (inventor-protocol section 3, controls before belief). If this branch fires, the
  leading interpretation on the record is artifact-first, and the batch's own
  measured null object is the control that has to be read beside it. Any structural
  or mechanistic reading of a plateau requires a further control — at minimum the
  256-byte random-bijection null at r = 5 — which this design does NOT run.
- NOT "the branch is safe for all phi". The SR-2 bound is a disclosed residual
  false-positive risk under seed heterogeneity in the priced phi range; it is a
  bound, not a removal, and no sentence may present it as eliminating the
  heterogeneity risk or as making the plateau sentence safe beyond the bound's
  stated conditions.

### Step 5.5 — Branch 5, FM-UNRESOLVED

**Conjunct, in full.** Fires if Branch 1 did not fire AND the exact two-sided
conditional binomial test of `pi = 0.5` on the pair `(T_4, T_16)`, using the
binding minimum-likelihood convention of Section 1 item 17, does NOT reject at
alpha = 0.05, AND EITHER the exact 95 percent interval for `rho` is NOT entirely
contained in `[1 / 1.5, 1.5]`, OR the SR-3 margin conjunct of Step 5.4 fails at
either primary point, i.e. `c_margin <= D_k < c_gate` at that point while Branch H
does not fire. Such margin-zone readings lack affirmative homogeneity evidence and
are demoted from a plateau sentence to this branch.

**Consequence and routing.** The realized exposure did not decide the question. This
is a complete and reportable outcome, not a failure: the realized ratio interval is
recorded as the measured obstruction, and the successor exposure is re-priced from
it.

**Licensed by this branch:** the realized rate-ratio interval at the realized pooled
exposure, recorded as a measured obstruction with its scope; and the re-priced
exposure a successor would need for a named resolution.

**NOT licensed by this branch:** anything about plateau, decay, completion,
extinction or comparator equivalence. This branch's whole content is "not decided at
this exposure".

### Step 5.6 — Exhaustiveness statement

Branches 1 through 5 partition every admissible outcome: Branch 1 covers the
comparator-indistinguishable case; conditional on Branch 1 not firing, the exact test
either rejects (Branches 2 and 3, split by the direction of `pi_hat`, which cannot be
exactly 0.5 when the test rejects) or does not reject (Branches 4 and 5, split by
the containment criterion and the SR-3 margin criterion: Branch 4 requires interval
containment AND `D_k < c_margin` at both points; Branch 5 receives every remaining
non-rejecting reading, including interval non-containment and margin-zone readings
with `c_margin <= D_k < c_gate`). Branch H receives every reading with
`D_k >= c_gate` at either point before any of Branches 1 through 5 is evaluated. No
admissible reading lands in two branches and none lands in none. Branch H and the
gates of Section 3 precede all of them and are themselves ordered.

---

## Section 6 — Proves-too-much controls (paper controls, zero compute, run BEFORE any arm)

Each object below is routed through Sections 2 to 5 on paper and the routing is
recorded pre-arm. Routing details and the derivation are in
`pooled-exposure-pricing.json` under `proves_too_much_routing`.

1. **The k = 0 ramp-zero arm** (count 2^30 by construction). Correct routing: HALT
   via FM-INADMISSIBLE-INPUT, failing P2 and independently P4.
2. **The r = 6 dead anchor at 0 hits** (floor absent by construction). Correct
   routing: HALT via FM-INADMISSIBLE-INPUT for the floor cascade, failing P1;
   admissible only to the comparator-setting step of Section 4.
3. **Synthetic counts drawn from the analytic null at the proposed exposure.**
   Correct routing: FM-COMPARATOR-INDISTINGUISHABLE.
4. **A synthetic still-decaying generator at the preregistered MDE.** Correct
   routing: FM-DECAY-CONTINUES.
5. **A synthetic heterogeneous generator in the disclosed phi range with true
   per-point arithmetic mean at lambda_plan (the OBJ-5 calibration target).**
   Required verdict: FM-OVERDISPERSED, or at minimum NEVER
   FM-PLATEAU-CONSISTENT, because no single rate governs k = 4. The revised rule
   does not make this object route cleanly to a single correct branch; its
   residual false-plateau mass is the SR-2 disclosed bound, and every composed
   plateau sentence must carry that bound.
6. **A synthetic heterogeneous generator in the disclosed phi range with true
   pooled mean AT the analytic comparator lambda_0.** Required verdict:
   FM-COMPARATOR-INDISTINGUISHABLE or a halt, never a floor-magnitude verdict.

**Disclosed, and stated rather than hidden:** the correct routing of objects 1 and 2
is carried by the ADMISSIBILITY PRECONDITIONS of Section 2, not by the statistic. A
statistic-only version of this rule would return FM-PLATEAU-CONSISTENT on two
ramp-zero arms and FM-DECAY-CONTINUES on a dead-anchor-versus-floor contrast. The
preconditions are therefore load-bearing conjuncts and any successor that relaxes
them breaks the rule.

---

## Section 7 — Heuristic assumptions and their in-batch validation

Each is stated formally in `design-proposal.yaml` under `heuristic_assumptions` with
its falsification condition. This section records only WHAT THE BATCH RUNS to
validate each one, so the validation is preregistered rather than retrofitted.

- **H1 Poisson counting model.** Validated by the Step 5.0 dispersion test at each
  primary point, plus a recorded comparison of the maximum per-arm count against the
  Poisson upper tail at the realized pooled rate. Power disclosure carried; the
  plateau-branch consequence of the test's weak small-n power is the SR-2 bound
  carried by any Branch-4 sentence, and the SR-3 margin conjunct requires
  affirmative homogeneity evidence before Branch 4 can fire.
- **H2 independence across arms.** Validated (i) PRE-ARM by an algebraic check, at
  zero compute, that the derived per-thread stream seeds are pairwise distinct across
  every (seed, armid, thread) triple in the committed domain, and (ii) by the same
  dispersion test. A stream collision is a hard FM-GATE-FAIL.
- **H3 exposure additivity.** Validated by the Step 5.0 dispersion test; its failure
  is Branch H.
- **H4 instrument stationarity.** Validated by the committed interleaved run order
  (Section 1 item 12) plus a preregistered run-order test: the Spearman rank
  correlation between per-arm count and run index within each primary point,
  evaluated at alpha_O = 0.01 and RECORDED IN EVERY BRANCH. A significant trend does
  not by itself halt the cascade — the interleaving makes drift common-mode — but it
  is disclosed with the composed sentence. Build-identity and KAT custody across the
  longer batch is additionally checked by the periodic checkpoints of Section 1
  item 18 and Branch G1 (SR-5).
- **H5 no cap or overflow interaction.** Validated on every receipt by the
  saturation-aware AMEND-1 identity of Section 3 Branch G1. Predicted status is
  UNSATURATED on every floor and null arm and SATURATED by construction on the k = 0
  anchor.
- **H6 the comparator.** Validated by the measured null object and the
  comparator-setting step of Section 4.

---

## Section 8 — Realized-power restatement (mandatory)

Whatever branch fires, the composed record MUST restate the achieved discriminating
power recomputed at the REALIZED event total, beside the power priced pre-arm. If
the realized total falls materially below the priced total, the branch outcome is
reported at the realized power and the shortfall is disclosed. Priced power is a
design commitment; it is never reported as though it had been delivered.

---

## Section 9 — Halt branches and budget discipline

- Any gate failure of Section 3 halts with `invalid_measurement`; the defective
  outputs are preserved and the receipts are untouched.
- Any inadmissible receipt at a primary point halts the cascade (Section 2).
- A budget exhaustion, timeout, crash or infrastructure failure is recorded as
  `resource_exhaustion` or infrastructure failure and is NEVER negative mathematical
  evidence about the floor (AGENTS rule 3).
- No arm may be re-run to replace an unwelcome reading. Any re-invocation at an
  identical (seed, armid, build) is instrument determinism and NEVER replication
  (NARROW-3), and is recorded as such.
- The batch composes at most the sentences its fired branch licenses in Section 5,
  and no others.

---

## Section 10 — Scope statement carried by every composed sentence

Toy tier (RQ-AES-003 R7 default). Cell (amask = 1, smask = 1). r = 5, with r = 6
matched dead anchors. Points k = 4 and k = 16 primary, k = 8 secondary and
report-only, k = 0 anchor only. 2^30 trials per arm. PIN-T0. Frozen build only.
Committed seed list only. No distinguisher, no key recovery, no deployed-AES
statement, no carrier, no X-lane, no rho-exclusion, no published-cryptanalysis
comparison in either direction. Nothing about k = 1, 2 or 3 (the THRESHOLD regime),
nothing about k = 12 (frozen-never-measured), nothing about the transition position,
nothing about any other cell, round count or exposure. The immutable
SH2-MONOTONE-DECAY verdict of EV-AES-868db1 and the additive content of
EV-AES-ac5c12 are inputs and are never re-composed.

---

## Section 11 — Inference and provenance

- requested_policy: research-deep
- resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
- resolved_model_id_note: session-reported identifier; no adapter probe was run in
  this session, so it is unverified configuration.
- fallback_used: true
- fallback_reason: opencode idea-generator role binding hit a balance-dead backend
  twice ('Insufficient balance or no resource package'); dispatched as general
  agent carrying the full idea-generator role contract, per AGENTS.md fallback
  rules and this handoff's fallback_allowed: true
- degraded_allowed: false
- degraded_requirements: none claimed; the reasoning-effort match to research-deep
  cannot be verified from inside this dispatch and is not asserted.
- model_verified: false
- independent_session: true
- knowledge_retrieval: search_knowledge attempted; KB index collection missing,
  recorded as an infrastructure note; internal ledger search used instead; silence
  not read as novelty.
- zero-arm attestation: zero experiment arms executed; no build run; no instrument
  invoked; no ledger record written; no identifier minted; no commit made.
