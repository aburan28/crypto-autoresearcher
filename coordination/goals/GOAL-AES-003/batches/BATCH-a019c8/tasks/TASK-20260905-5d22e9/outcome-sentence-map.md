# Outcome-to-Sentence Map — TASK-20260905-5d22e9 (deliverable C)

- id: OUTCOME-MAP-TASK-20260905-5d22e9
- kind: outcome-sentence-map
- status: design_only_not_frozen_not_authorized
- recorded_at: 2026-09-05
- task_id: TASK-20260905-5d22e9
- batch_id: BATCH-a019c8
- goal_id: GOAL-AES-003
- question_id: RQ-AES-003
- candidate: IDEA-20260904-6aed0b
- companions:
  - `coordination/goals/GOAL-AES-003/batches/BATCH-a019c8/tasks/TASK-20260905-5d22e9/execution-design.yaml`
  - `coordination/goals/GOAL-AES-003/batches/BATCH-a019c8/tasks/TASK-20260905-5d22e9/execution-budget.json`

## 0. Binding preamble

**Binding-text carrier.** Under the R5-3 NON-RELIANCE declaration, `execution-design.yaml`
of this task is the binding carrier of every branch conjunct and every NOT-licensed
prohibition text. This map QUOTES or POINTS at that record and never paraphrases a
conjunct or a prohibition (RAT-3 with SR-1). Where a row below gives a licensed sentence,
it is the exact sentence the carried branch text licenses; where a row gives prohibitions,
the itemised NOT-licensed list in the carried text governs in full.

**Realized readings, carried verbatim (design INPUTS, never re-measured, never entering a
test statistic):** h(4) = 17 (seed 531001) and 21 (seed 531002); h(8) = 13 (seed 531001)
and 18 (seed 531002); h(16) = 12 (seed 531001); each at 2^30 trials per arm, cell (1,1),
r = 5, PIN-T0. Sources: EV-AES-868db1 OBS-2/OBS-3; EV-AES-ac5c12 OBS-3; DEC-20260905-1ea7a0
context. Binding use inventory: U1 (planning-constant sizing: lambda_plan = 16 chosen inside
the span [12, 21]), U2 (declared REPORT-ONLY consistency comparison AFTER the branch has
fired), U3 (Branch G4 hard-gate threshold calibration from the committed k = 16 reading's
exact Garwood lower bound, SR-4 disclosure). No branch conjunct, test statistic, equivalence
criterion, or licensing sentence consumes any committed reading; the new-arms-only discipline
binds.

**Exact Garwood CI, carried verbatim:** The exact Garwood 95% confidence interval for
h(4)_531001 = 17 hits is [9.903, 27.219].

**Never-live values (bind every row of this map):**
1. The RAT-5 citation-error figure is never a live value anywhere and is deliberately NOT
   reprinted in this file; its single occurrence across the three deliverables is inside the
   verbatim RAT-5 quotation in `execution-design.yaml` whose function is to record the error.
2. The superseded arcsine power sizing is never a live value; its numeral is deliberately not
   reprinted in this file.
3. The Branches-1-5-only decay power 0.970869 is never an unconditional live value; wherever
   it appears it is labelled CONDITIONAL ON BRANCH H NOT FIRING.

**Live values (corrected pricing):** written-cascade-order decay power 0.952538
(FM-DECAY-CONTINUES under OBJ-4 at the MDE rho = 2, with 0.018883 to FM-OVERDISPERSED);
plateau false-positive bound 0.171940 (residual range exactly [0.114124, 0.171940]);
OBJ-5B comparator routing 0.989349 falling to 0.884236 as phi runs 1.0 -> 2.0
(FM-OVERDISPERSED capture 0.008843 -> 0.115764 both-points reading;
FM-PLATEAU-CONSISTENT 0.000000 at every phi).

**Priced semantics (R5-1), carried inline because rows below are bound-carrying:**
- 0.171940 is certified over the OBJ-5A calibration family and the probed configurations,
  NOT as a theorem for all equal-mean configurations (RT2-F6). The worst case is a supremum
  attained at phi = 1.0, the degenerate homogeneous limit; over strictly heterogeneous
  phi > 1 it is approached as phi -> 1+ (largest swept value 0.1718971 at phi = 1.001);
  residual range exactly [0.114124, 0.171940]; plateau mass convention-invariant.
  "Bounded" is not "small" or "removed".
- 0.018883 is the written-cascade-order FM-OVERDISPERSED routing price of the decay branch,
  priced on OBJ-4 at the preregistered MDE rho = 2 at the committed constants
  (lambda_plan = 16, n = 4 per point, 2^30 per arm), a design-time exact enumeration
  independently re-derived to every reported digit, NOT a theorem for all decay alternatives.

**Prohibited-sentence register (binds every row):** no composed sentence anywhere under this
design may be an EXTINCTION sentence (NARROW-1); a COMPLETION or decay-has-ended sentence
(NARROW-1, NARROW-4); a CLIFF-AT-4 or sub-sub-interval reading (NARROW-4); a WHOLE-CURVE
sentence (RAT-4: every sentence names its pairs and its per-pair resolution); a
PLATEAU-SAFE-FOR-ALL-PHI sentence (the SR-2 bound is a disclosed residual risk, not a
removal); or a COUNT-VERDICT-AT-K=8 (NARROW-5). Margin-zone outcomes map to FM-UNRESOLVED
sentences ONLY. Absence of decay NEVER maps to plateau evidence.

**Evaluation discipline:** the floor cascade (Branch H, then Branches 1-5) is evaluated
EXACTLY ONCE, after position 17 completes, in the fixed written order, on the complete data.
No interim floor-branch evaluation exists; no discretionary stopping exists in either
direction. Gate/halt verdicts are admissibility and custody events, not statistics about the
floor: under a gate halt NO floor sentence is composed at all.

---

## Section A — Gate and halt verdicts (every one ENDS THE BATCH EARLY; none composes a floor sentence)

### A1. FM-GATE-FAIL (Branch G1)
- **Trigger points:** pre-arm battery; any receipt completion (per-receipt AMEND-1
  saturation-aware counter identity); any SR-5 periodic checkpoint (after positions 4, 8,
  12, 16 or every 3600 s); post-arm battery; pre-arm stream-distinctness collision (H2).
- **Exact effect (quote of carried text):** "ENDS THE BATCH EARLY. Remaining arms do not
  run. Record invalid_measurement (or resource_exhaustion / infrastructure failure where
  that is the cause), preserve the defective outputs, leave receipts untouched, name the
  failing gate, bound checkpoint attribution to the arms completed since the last passing
  checkpoint. NEVER evidence about the floor (AGENTS rules 3 and 5); no floor sentence of
  any kind."
- **Licensed sentence:** none about the floor. The only recordable content is the named
  failing gate, the validity status, and the bounded attribution.
- **NARROW/RAT tests:** AGENTS rules 3 and 5; AMEND-1 (rescoped counter-inconsistency gate,
  carried verbatim in the design); NARROW-3 (no re-arm to replace an unwelcome reading —
  a re-invocation at identical (seed, armid, build) is instrument determinism, never
  replication).

### A2. FM-ANCHOR-FAIL (Branch G2)
- **Trigger point:** analysis of the position-1 anchor receipt (FM-A00, k = 0, seed 531001),
  first among alive readings. The anchor is saturated by construction under PIN-T0
  (predicted: hits = 2^30, W = 3 on 100 percent of nontrivial trials, overflow exactly
  2^30 − 1024 = 1073740800, legal under AMEND-1); G2 checks these construction properties.
- **Exact effect (quote):** "ENDS THE BATCH EARLY. invalid_measurement, HALT; no floor
  sentence."
- **Licensed sentence:** none about the floor. The anchor is the AMEND-1 proves-too-much
  control: it must PASS, showing the rescoped gate is not vacuous. Its failure is an
  instrument finding.
- **NARROW/RAT tests:** AMEND-1; AGENTS rule 3 (an anchor failure is infrastructure/
  instrument signal, never evidence against a mathematical hypothesis).

### A3. FM-DEAD-ANCHOR-FAIL (Branch G3)
- **Trigger point:** completion of ANY r = 6 null arm (FM-N01..N06) reading >= 9 hits.
- **Exact effect (quote):** "ENDS THE BATCH EARLY. A boundary falsifier of the sealed
  verdict: HALT and escalate to claim-changing review (AGENTS rule 12); never a floor
  sentence."
- **Licensed sentence:** none about the floor. The finding is that the r = 6 null object is
  not dead at the committed threshold; the escalation route is claim-changing review of the
  sealed null verdict, not a floor composition.
- **NARROW/RAT tests:** AGENTS rule 12 (claim-changing review); AGENTS rule 3.

### A4. FM-NULL-CONTROL-FAIL (Branch G4)
- **Trigger point:** null-block completion (position 17), OR immediately when the running
  pooled count over completed null arms reaches 39 (monotone, deterministic,
  pre-committed: the pooled count is monotone in completed arms, so a partial sum >= 39
  forces the completed value >= 39; the early firing is deterministic and pre-committed,
  not discretionary, and the verdict is identical under both readings). Threshold basis:
  lambda_hat_null >= 6.5 per 2^30, the exact Garwood lower bound of the committed single-arm
  h = 12 reading (U3/SR-4 disclosure: a gate calibration, not an evidential input).
- **Exact effect (quote):** "ENDS THE BATCH EARLY. HALT, instrument review; NO floor
  sentence of any kind may be composed."
- **Licensed sentence:** none about the floor.
- **NARROW/RAT tests:** SR-4 (third disclosed use of the five committed readings);
  AGENTS rule 3.

### A5. FM-INADMISSIBLE-INPUT (Section 2, preconditions P1-P5)
- **Trigger point:** any receipt offered to the cascade failing P1-P5.
- **Sub-case A5a — exclusion removes an arm from a primary point, from the null block, or
  prevents G2 evaluation of the anchor:** "ENDS THE BATCH EARLY ...; the exclusion is
  recorded with the failing precondition named, never silently absorbed, never replaced by
  a substitute arm." Licensed sentence: none about the floor.
- **Sub-case A5b — exclusion of a k = 8 report-only arm (FM-K8-1/2):** "recorded and does
  NOT end the batch (no conjunct reads it)." The batch proceeds; the exclusion is recorded;
  the report-only U2 comparison runs on the surviving k = 8 arm(s) or is recorded as not
  runnable. Licensed sentence: none about the floor from this surface ever (NARROW-5).
- **NARROW/RAT tests:** NARROW-5; AGENTS rule 8 (unexpected observations recorded, not
  silently discarded).

### A6. resource_exhaustion / infrastructure failure (budget, timeout, crash)
- **Trigger point:** any time; includes HALT at binding_stop_utc under the C2 budget
  discipline (halted_on_budget recorded truthfully, dropped work NAMED).
- **Exact effect (quote):** "ENDS THE BATCH (or the affected arm under the reseeding
  discipline). Recorded as resource_exhaustion or infrastructure failure; NEVER negative
  mathematical evidence about the floor (AGENTS rule 3); no verdict is composed from
  partial primary data; dropped work is named as scope, never as an answer."
- **Licensed sentence:** none about the floor. A halt is infrastructure signal, never a
  negative mathematical result.
- **NARROW/RAT tests:** AGENTS rules 3 and 6; C2 budget discipline.

---

## Section B — Comparator-setting step sub-cases (NOT a branch; runs after G1-G4 pass, before the cascade)

The step (carried text, quoted): compute U_null, the EXACT one-sided 95 percent Garwood
upper bound on the pooled measured null rate from the r = 6 null-object arms, per 2^30, by
the committed closed form U(T, n) = 0.5 * chi2_{0.95}(2T + 2) / n; set the operative
comparator lambda_op = max(lambda_0, U_null) with lambda_0 = 1.0 per 2^30; every branch
statement is evaluated against lambda_op and every composed sentence DISCLOSES both
lambda_0 and U_null and states which one was operative.

### B1. lambda_op = lambda_0 = 1.0 (pooled null count T <= 1; committed row U(T_0,6) = 0.499, U(T_1,6) = 0.791, both <= 1.0)
- **Effect on sentences:** every branch statement is evaluated at lambda_op = 1.0. The
  Branch-1 threshold is exactly T_4 <= 11 AND T_16 <= 11 (reject at T >= 12 per primary
  point; exact Poisson(4) upper tail P(X >= 12) = 9.152e-4 <= 0.001 < P(X >= 11) = 2.840e-3).
- **Disclosure obligation:** every composed sentence still discloses lambda_0 and U_null
  and states that lambda_0 was operative.
- **NARROW/RAT tests:** none additional; this is a disclosure row, not a verdict row.

### B2. lambda_op = U(T, 6) > 1.0 (pooled null count T >= 2; committed row U(T_2,6) = 1.049, U(T_3,6) = 1.292, U(T_4,6) = 1.526)
- **Effect on sentences:** the whole cascade is restated against the larger value and the
  resulting sentences are WEAKER (carried text: "Both outcomes are informative; neither is
  a failure"). The Branch-1 numeric threshold is recomputed exactly from the pre-committed
  rule — the first T with P(Poisson(n_k x lambda_op) >= T) <= 0.001 at the lambda_op value
  fixed BEFORE the cascade is evaluated; a deterministic function of a pre-cascade-fixed
  constant, not a post-data choice.
- **Disclosure obligation:** every composed sentence discloses lambda_0, U_null, and states
  that U_null was operative.
- **NARROW/RAT tests:** the measured null is a control, not a decoration; no sentence may
  quote lambda_0 as operative when U_null was operative.

---

## Section C — Branch H: FM-OVERDISPERSED (Step 5.0, evaluated FIRST in the single post-completion valuation)

- **Completion semantics:** requires ALL 17 committed arms run to completion. Branch H is
  NOT a batch halt (carried text: "a DETERMINATE FINDING ..., not a halt of the batch").
- **Conjunct:** fires if, at EITHER primary point k in {4, 16}, the Poisson dispersion index
  D_k = sum_j (X_kj − Xbar_k)^2 / Xbar_k is at or above c_gate = chi2_{0.99}(n_k − 1) =
  11.344867 on n_k − 1 = 3 degrees of freedom (alpha_H = 0.01), under the committed boundary
  conventions. Sub-cases "at k = 4 only", "at k = 16 only", "at both" fire the SAME branch;
  the sentence names the point(s) that fired.
- **Exact licensed sentence (quote of carried license):** "that the per-arm floor counts at
  the named point are over-dispersed relative to Poisson at alpha_H, with the realized
  dispersion index and its degrees of freedom stated." Plus: the FM-OVERDISPERSED sentence
  ONLY; every per-arm tuple recorded individually (never smoothed, never pooled); NO pooled
  magnitude sentence of any kind; the k = 8 report-only data, the measured null, the
  operative comparator, and the first heterogeneity estimate are all still produced and
  recorded; successors named (a larger n to estimate the heterogeneity; a re-priced design
  carrying the inflation explicitly).
- **NOT licensed (quote):** "any magnitude sentence; any plateau, decay, extinction,
  completion or comparator sentence; any statement that the floor is or is not constant;
  any statement about k = 8, k = 12 or any point outside the domain."
- **Sentence price:** 0.018883 with its priced-semantics statement (preamble) attached to
  every composed FM-OVERDISPERSED sentence.
- **NARROW/RAT tests:** NARROW-1 (no extinction/completion reading of over-dispersion);
  RAT-4 (the sentence names its point(s) and per-point scope); heuristic H3 (exposure
  additivity) is the falsified heuristic and is recorded as such.

---

## Section D — Branches 1-5 (evaluated only if Branch H did not fire, in written order 1 -> 5, single post-completion valuation; every one requires ALL 17 arms complete)

### D1. Branch 1 — FM-COMPARATOR-INDISTINGUISHABLE (Step 5.1)
- **Conjunct:** both pooled counts fail to reject lambda_k = lambda_op under one-sided exact
  Poisson tests against mean n_k x lambda_op at alpha_N = 0.001 (at lambda_op = 1.0 exactly
  T_4 <= 11 AND T_16 <= 11).
- **Exact licensed sentence (quote):** exactly one sentence — "at pooled exposure
  n × 2^30 per point, cell (1,1), r = 5, PIN-T0, neither k = 4 nor k = 16 is
  distinguishable from the operative comparator lambda_op at alpha_N" — together with the
  instrument-review routing and the disclosed contradiction with the committed readings
  (five committed readings carry 81 hits where the comparator predicts about 5; the branch
  ALSO routes to instrument review before any interpretive sentence is composed).
- **NOT licensed (quote):** "ANY extinction sentence. 'Indistinguishable from the comparator
  at this exposure' is a statement about resolution, not about absence, and NARROW-1 bars
  the extinction reading in this branch as in every other. Also not licensed: any completion
  sentence, any cliff-at-4 reading, any statement that the decay finished, any statement
  about k = 8, k = 12 or any untested k, and any re-composition of the immutable
  SH2-MONOTONE-DECAY verdict."
- **NARROW/RAT tests:** NARROW-1; NARROW-4; NARROW-5; RAT-4.

### D2. Branch 2 — FM-DECAY-CONTINUES (Step 5.2)
- **Conjunct:** Branch 1 did not fire AND the exact two-sided conditional binomial test of
  pi = 0.5 on (T_4, T_16), conditional on T = T_4 + T_16, equal exposures n_4 = n_16,
  binding minimum-likelihood convention, rejects at alpha = 0.05 AND realized
  pi_hat = T_4 / T > 0.5.
- **Exact licensed sentence (quote):** "that over the two tested points k = 4 and k = 16, in
  cell (1,1) at r = 5 under PIN-T0 at the realized pooled exposure, the floor rate at k = 4
  exceeds the floor rate at k = 16 at alpha = 0.05, with the ratio and its interval named;
  and that the floor is alive at both points (NARROW-1 carried)." The estimated rate ratio
  rho_hat and its exact Clopper-Pearson-mapped 95 percent interval are recorded.
- **NOT licensed (quote):** "any statement about the SHAPE of the decay between the two
  points (no intermediate point is in the primary domain); any statement about k = 8 at
  count level; any statement about k = 12, which is frozen-never-measured; any extrapolation
  to k > 16 or to any untested k; any extinction, completion or cliff-at-4 sentence; any
  rehabilitation of the broken-authority multiplicative prior; any dilution-only attribution
  (SCOPE-1 binds); any whole-curve sentence."
- **Sentence price and power:** the composed sentence is reported beside the written-order
  priced power 0.952538 with 0.018883 to FM-OVERDISPERSED (priced semantics inline,
  preamble) AND the realized-power restatement (Section F).
- **NARROW/RAT tests:** NARROW-1; NARROW-4; NARROW-5; SCOPE-1 (attribution bounded; no
  dilution-only attribution); RAT-4 (names its pair and per-pair resolution).

### D3. Branch 3 — FM-INVERTED (Step 5.3)
- **Conjunct:** Branch 1 did not fire AND the same exact test rejects at alpha = 0.05 AND
  realized pi_hat < 0.5.
- **Exact licensed sentence (quote):** "the inversion at the two tested points with its
  ratio and interval, and the explicit statement that the band verdict is unaffected."
  Carried consequence: a determinate rate INVERSION at floor magnitude — the k = 16 floor
  rate exceeds the k = 4 floor rate — a count-level non-monotone finding scoped to the two
  tested points; SH2-MONOTONE-DECAY is a BAND-trajectory statement, untouched and
  unre-composed; a count-level inversion inside the RESIDUAL band is not a band rise.
- **NOT licensed (quote):** "any re-composition of SH2-MONOTONE-DECAY; any claim of a band
  rise; any statement beyond the two tested points; and all of the exclusions listed under
  Branch 2."
- **NARROW/RAT tests:** NARROW-1; NARROW-4; NARROW-5; SCOPE-1; RAT-4.

### D4. Branch 4 — FM-PLATEAU-CONSISTENT (Step 5.4)
- **Conjunct (all four, carried in full in the design; the containment conjunct and the SR-3
  margin conjunct are NOT OPTIONAL and may not be dropped or moved post-data):** Branch 1
  did not fire; AND the exact two-sided conditional binomial test does NOT reject at
  alpha = 0.05; AND the exact 95 percent interval for rho = lambda_4 / lambda_16
  (Clopper-Pearson mapped through rho = (pi / (1 − pi)) × (n_16 / n_4)) is entirely
  CONTAINED in [1/1.5, 1.5]; AND at BOTH primary points D_k < c_margin = chi2_{0.95}(3) =
  7.814728 (SR-3 remedy option a: AFFIRMATIVE homogeneity evidence, not mere failure to
  reject Branch H).
- **Exact licensed sentence (quote):** exactly one sentence — "over the two tested points
  k = 4 and k = 16, in cell (1,1) at r = 5 under PIN-T0 at the realized pooled exposure,
  the floor rate ratio is confined to [1/1.5, 1.5]; the floor is PLATEAU-CONSISTENT AT
  RESOLUTION 1.5" — together with the realized interval, the operative comparator, the
  floor-is-alive statement (NARROW-1), and the SR-2 disclosed plateau-heterogeneity
  false-positive bound. Every composed sentence under this branch MUST carry that bound
  (0.171940) as a disclosure with the R5-1 priced-semantics scope statement inline
  (preamble).
- **NOT licensed (carried itemisation, quoted in full in the design; summary of the
  itemised list):** NOT "the floor is constant"; NOT "the decay has ended" / "the decay
  completes" / "the excess has reached its floor"; NOT any extinction sentence (NARROW-1);
  NOT a cliff-at-4 or sub-sub-interval reading (NARROW-4); NOT any statement about k = 8 at
  count level (NARROW-5), k = 12 (frozen-never-measured), or untested k; NOT a mechanism —
  the leading interpretation on the record is ARTIFACT-FIRST (inventor-protocol section 3,
  controls before belief), read beside the batch's own measured null, and any structural or
  mechanistic reading requires at minimum the 256-byte random-bijection null at r = 5,
  which this design does NOT run (disclosed control gap); NOT "the branch is safe for all
  phi" — the SR-2 bound is a disclosed residual false-positive risk, a bound, not a
  removal.
- **Favorable-reading discipline (quote):** "A FAVORABLE PLATEAU READING IS NEVER A
  STOPPING POINT: there is no interim reading to stop after, and the composed sentence
  arrives only with the realized-power restatement, the run-order disclosure, the
  operative-comparator disclosure and the full 0.171940 bound disclosure."
- **NARROW/RAT tests:** NARROW-1; NARROW-4; NARROW-5; SR-2 (bound disclosed, never
  removed); SR-3 (margin conjunct load-bearing); RAT-4; RT2-F6 (priced-semantics scope of
  the bound).

### D5. Branch 5 — FM-UNRESOLVED (Step 5.5), including EVERY margin-zone demotion
- **Conjunct:** Branch 1 did not fire AND the exact test does NOT reject at alpha = 0.05,
  AND EITHER (sub-case D5a) the exact 95 percent interval for rho is NOT entirely contained
  in [1/1.5, 1.5], OR (sub-case D5b — the MARGIN ZONE) the SR-3 margin conjunct of Step 5.4
  fails at either primary point, i.e. c_margin <= D_k < c_gate (7.814728 <= D_k <
  11.344867) at that point while Branch H does not fire. Carried text: "Such margin-zone
  readings lack affirmative homogeneity evidence and are demoted from a plateau sentence to
  this branch."
- **Exact licensed sentence (quote):** "the realized rate-ratio interval at the realized
  pooled exposure, recorded as a measured obstruction with its scope; and the re-priced
  exposure a successor would need for a named resolution." Carried consequence: "the
  realized exposure did not decide the question. This is a complete and reportable outcome,
  not a failure."
- **NOT licensed (quote):** "anything about plateau, decay, completion, extinction or
  comparator equivalence. This branch's whole content is 'not decided at this exposure'."
- **Margin-zone rule (binds both sub-cases):** margin-zone outcomes map to FM-UNRESOLVED
  sentences ONLY; absence of decay NEVER maps to plateau evidence; a non-rejecting reading
  without interval containment AND affirmative homogeneity margin is FM-UNRESOLVED; the
  equivalence gate plus the SR-3 margin conjunct are load-bearing and may not be dropped or
  moved post-data.
- **NARROW/RAT tests:** NARROW-1; NARROW-4; SR-3; RAT-4.

---

## Section E — Run-order disclosure sub-case (recorded IN EVERY BRANCH; never a gate)

- **Test:** Spearman rank correlation between per-arm count and run position within each
  primary point, evaluated at alpha_O = 0.01.
- **E1. Not significant:** disclosed with the composed sentence; nothing further.
- **E2. Significant:** disclosed with the composed sentence; does NOT by itself halt the
  cascade — the committed interleaving (k = 4, k = 16 strictly alternating at positions
  3, 4, 6, 7, 10, 11, 13, 14; never blocked by point) makes drift common-mode and cancels
  it in the conditional statistic. Carried residual disclosure: "A drift that acts
  differently on the two points is not common-mode, would not cancel, and is recorded as an
  uncontrolled residual nothing in this design can detect."
- **NARROW/RAT tests:** none additional; this row can never convert a disclosure into a
  verdict, and no sentence may cite the run-order test as evidence for or against the floor.

---

## Section F — Mandatory realized-power restatement (whatever branch fires)

- **Obligation (quote):** "Whatever branch fires, the composed record MUST restate the
  achieved discriminating power recomputed at the REALIZED event total, beside the power
  priced pre-arm (written cascade order at the MDE rho = 2: FM-DECAY-CONTINUES 0.952538
  with 0.018883 to FM-OVERDISPERSED — with the priced-semantics statement carried inline)."
- **Shortfall sub-case:** "If the realized total falls materially below the priced total,
  the branch outcome is reported at the realized power and the shortfall is disclosed.
  Priced power is a design commitment; it is never reported as though it had been
  delivered."
- **Conditional value discipline:** the Branches-1-5-only value 0.970869 may appear in this
  restatement ONLY labelled CONDITIONAL ON BRANCH H NOT FIRING; the unconditional live
  figure is the written-order 0.952538.
- **NARROW/RAT tests:** RAT-5 discipline (no superseded or mis-cited power figure may enter
  a composed record); the never-live-values preamble.

---

## Section G — Report-only surfaces (no row of this section ever composes a floor sentence)

### G1. k = 8 per-arm counts (FM-K8-1, FM-K8-2; positions 8 and 15)
- Recorded individually; NO count verdict in any branch (NARROW-5 discipline extended
  prospectively). After the branch fires, a declared REPORT-ONLY consistency comparison of
  the new pooled per-point rates against the five committed readings' exact intervals (U2)
  — it can never move the branch; a gross inconsistency is an instrument-review trigger,
  not a floor sentence. Exclusion of a k = 8 arm is recorded and does NOT end the batch
  (sub-case A5b).
- **Prohibited:** any COUNT-VERDICT-AT-K=8 sentence, in any record, any summary.

### G2. Floor W-tail above 1 (O5)
- Counter-derived, AMEND-1-admissible, rides free on the receipts, DECLARED REPORT-ONLY —
  no conjunct consumes it, too sparse at this exposure to carry a verdict; named as the
  successor lens.

### G3. Pooled intensity lambda_k itself
- Report-only beside the ratio (the ratio cannot say whether the floor is high or low).

- **NARROW/RAT tests (all of Section G):** NARROW-5; AMEND-1; AGENTS rule 8.

---

## Section H — Single-valuation exhaustiveness row

- **Partition (quote of carried Step 5.6):** "Branches 1 through 5 partition every
  admissible outcome: Branch 1 covers the comparator-indistinguishable case; conditional on
  Branch 1 not firing, the exact test either rejects (Branches 2 and 3, split by the
  direction of pi_hat, which cannot be exactly 0.5 when the test rejects) or does not
  reject (Branches 4 and 5, split by the containment criterion and the SR-3 margin
  criterion ...). Branch H receives every reading with D_k >= c_gate at either point before
  any of Branches 1 through 5 is evaluated. No admissible reading lands in two branches and
  none lands in none. Branch H and the gates precede all of them and are themselves
  ordered."
- **No-rearm rule (quote):** "No arm may be re-run to replace an unwelcome reading; any
  re-invocation at an identical (seed, armid, build) is instrument determinism and NEVER
  replication (NARROW-3). The batch composes at most the sentences its fired branch
  licenses, and no others."
- **Coverage claim:** this map covers EVERY possible branch verdict of EVERY arm class of
  the committed 17-arm plan: all six gate/halt verdicts and resource_exhaustion (Section A);
  Branch H at either or both primary points (Section C); Branches 1-5 including both
  Branch-5 sub-cases and the margin-zone demotion (Section D); the comparator-setting
  sub-cases (Section B); the run-order disclosure sub-case (Section E); the realized-power
  restatement obligation (Section F); the report-only surfaces (Section G); and the
  single-valuation exhaustiveness row (this section).

---

## Zero-arm attestation

ZERO ARMS EXECUTED. ZERO EXPERIMENT RUNS AUTHORIZED AND ZERO PERFORMED. This map is a
design artifact: it authorizes nothing, freezes nothing, and changes no status. It becomes
operative only inside a future committed Coordinator authorization decision that freezes it
by exact path. No statistical simulation was run in its production; the only arithmetic is
exact pricing arithmetic on committed, independently re-derived constants and exact
tabulated constants copied from their named sources.

## Inference provenance

requested_policy: research-deep; reasoning_effort: null; fallback_used: true (opencode
idea-generator role binding balance-dead, known since DEC-20260903-16bfc2; session
dispatched as a general agent carrying the full idea-generator role contract per the
handoff's fallback_allowed: true); degraded_allowed: false; degraded_requirements: none
claimed; resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max;
model_verified: false (no adapter probe executed for this session; recorded rather than
omitted per AGENTS.md model policy); independent_session: true.
