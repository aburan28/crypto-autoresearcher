# PREREGISTRATION — TASK-20260902-987716 (BATCH-e5d753, GOAL-AES-003) — Stage S0

WRITE-ONCE. Committed before any arm runs (mtime recorded in
budget_stamps.jsonl as `preregistration_written`, before the first binary
invocation). This file binds the S0 producer execution of
IDEA-20260902-9e84ac under DEC-20260902-38227b (batch opening, SCOPE-1
adoption) and DEC-20260901-6f9de3 (AMEND-1). S0 decides instrument validity
and anchors ONLY; it decides NO shape (no interior point is run in S0).

Instrument lineage (UNCHANGED, zero source change in this design): the
BATCH-7b798d PIN-T0 widened build `affarm046ex` (HIT_LOG_CAP = 256 per
thread), copied byte-exact from
`coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/tasks/TASK-20260901-706b1d/src/`
and re-verified by sha256 against the snapshot receipt
`coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/archives/TASK-20260901-56ecb6/snapshot-receipt.json`
in S0-2.

---

## 1. AMEND-1 COUNTER-INCONSISTENCY GATE (VERBATIM)

From DEC-20260901-6f9de3, AMEND-1 (committed):

> PROSPECTIVE amendment for successor batches under the frozen
> 582ea9 instrument lineage: the branch-1 conjunct 'hit_overflow
> > 0 on any analysis-bearing receipt -> invalid_measurement' is
> rescoped to 'counter INCONSISTENCY on an analysis-bearing
> receipt -> invalid_measurement', where counter inconsistency
> means (a) overflow != hits − threads×HIT_LOG_CAP, or (b) any
> cap-independent counter (hits, W, ewhist_hit) disagrees with
> its internal identities, or (c) any analysis-bearing quantity
> is derived from the capped detail log rather than the
> counters. Pure cap truncation of the detail log with all
> counter identities intact is NOT a gate failure. This amendment
> applies to batches opened AFTER this decision; it does not
> re-adjudicate BATCH-7b798d, whose readings remain unvalidated
> as shape evidence (red-team RT3-A: no post-hoc rescue).

Conjunct form as adopted in the SH2 cascade (IDEA-20260902-9e84ac
integrity_gate_amend1.verbatim_conjunct): 'counter INCONSISTENCY on an
analysis-bearing receipt -> invalid_measurement', with counter inconsistency
meaning (a), (b), (c) exactly as above.

### 1.1 Saturation-aware evaluation rule (strictest reading, not a relaxation)

On every analysis-bearing receipt, `overflow == hits − logged_detail_records`
EXACTLY, where `logged_detail_records == threads×HIT_LOG_CAP` when
`hits > threads×HIT_LOG_CAP` (saturated; AMEND-1's verbatim form) and
`logged_detail_records == hits` with `overflow == 0` otherwise (unsaturated;
both forms coincide when saturated). In this instrument `hits` is the receipt
field `W_ge1_nontrivial` (the receipt carries no field literally named
"hits"), and `logged_detail_records` is the total per-thread logged record
count, recoverable from the receipt as the number of `hit_trials` entries
(each thread logs min(hits_t, HIT_LOG_CAP) records).

Predicted saturation status (design-time priors from the flagged-unvalidated
BATCH-7b798d observations): k=0 anchor saturated by construction
(overflow 2^30 − 1024); k=1 and k=2 saturated (predicted overflows
~12,680,085 and ~148,347); k=4/k=8/k=16 predicted unsaturated — if any
realizes hits > 1024, truncation is legal under AMEND-1 and the admissible
set is unchanged.

### 1.2 AMEND-1 proves-too-much control (S0-6)

The AMEND-1 gate must PASS the ramp-zero receipt (overflow 2^30 − 1024,
saturated by construction, all counter identities exact). If the gate fails
THAT receipt, the gate itself is indicted before any interior reading:
SH2-GATE-FAIL halt (DEC-20260902-38227b review_plan.proves_too_much).

---

## 2. COUNTER IDENTITIES CHECKED PER ANALYSIS-BEARING RECEIPT

1. sum(whist) == nontrivial_trials
2. h == sum(whist[1:]) where h = W_ge1_nontrivial (= "hits")
3. moment identity: sum(W_ge1_by_word) == sum(W * whist[W]) over W in 1..4
4. sum(zhist) == trials
5. sum(ewhist_all) == nontrivial_trials
6. sum(ewhist_hit) == h
7. sum(ewhist_miss) == nontrivial_trials − h
8. overflow == hits − logged_detail_records (saturation-aware form of §1.1;
   coincides with the verbatim conjunct-(a) form `overflow == hits −
   threads×HIT_LOG_CAP` on saturated receipts)
9. trials accounting: trivial_swaps_excluded + nontrivial_trials == trials == 2^log2N

---

## 3. ADMISSIBLE vs INADMISSIBLE QUANTITIES

ADMISSIBLE (counter-derived; survive cap truncation — source-verified,
TASK-20260901-87a39b check_7): h(k) = W_ge1_nontrivial, whist,
W_ge1_by_word, zhist, all ewhist_*/ewbithist_*/ezdiag_*/ezoff_* class
counters, hit_overflow, excess ratio h/excess_E under the frozen
excess_E = 2^30 convention, excess over the run-internal accidental-hit
rate, Garwood 95% CIs (count and exposure only), band assignment, all
identity checks of section 2.

INADMISSIBLE (detail-log-derived): hit_e_detail records, hit_trials as a
SAMPLE of hit structure, any distributional statement over hits derived from
detail records (zero_mask_e distributions, per-hit diagnostics), any X-lane
computation. On saturated receipts the logged records are the FIRST 256 hits
per thread — biased toward early trials, not a random sample (red-team J2).
These are retained as report-only enabling data under the no-reopen clause
(section 10); NO branch conjunct consumes them, so AMEND-1(c) is satisfied by
construction.

---

## 4. SH2 BRANCH CASCADE (EXHAUSTIVE, ORDERED) — WITH PRECEDENCE CLAUSE

### 4.1 Precedence clause (restated standalone, mandatory)

This record's decision rule is an EXHAUSTIVE ORDERED CASCADE
(SH2-GATE-FAIL > SH2-F6 > SH2-ANCHOR-FAIL > SH2-RESEAT-FAIL >
SH2-SEED-DISAGREE > SH2-DEAD-INTERIOR > SH2-NONMONO > SH2-MONOTONE-DECAY >
SH2-PLATEAU > SH2-RESIDUAL) committed in S0-1 before any arm runs. By
construction no two branches can be assigned the same outcome: branches 1-4
are halt conditions preceding all verdict composition; branch 5 consumes any
seed-disagreement outcome before any shape branch composes; branches 6-9 are
mutually disjoint on their conjuncts (SH2-DEAD-INTERIOR requires all four
interior h <= 5; SH2-NONMONO requires a band rise AND not-DEAD and precedes
the monotone-conditional branches; SH2-MONOTONE-DECAY requires h(4) <= 40
while SH2-PLATEAU requires h(4) >= 100, both under h(1) >= 100 and band
non-rising); SH2-RESIDUAL is the declared complement. This cascade is
RE-AUTHORED for the realized regime, not an amendment of the 582ea9 cascade
(which remains bound to BATCH-7b798d, immutable); AMEND-1 governs the
branch-1 rescoping, and the red-team J6 vacuity finding is answered by making
the k=4 locator — not the vacuous band-non-rising conjunct — the branch
selector between MONOTONE-DECAY and PLATEAU.

### 4.2 Branches, evaluated in this FIXED ORDER

1. **SH2-GATE-FAIL**: any integrity gate fails (S0-2 build identity or its
   Gate-0x fallback, S0-3 KAT, S0-4 freeze re-verification, S1-6 determinism
   double, S1-7 digest/source-diff, or counter INCONSISTENCY on any
   analysis-bearing receipt — AMEND-1 VERBATIM per section 1, evaluated per
   section 1.1). -> invalid_measurement; HALT; repair (rule 5); never
   evidence about shape.
2. **SH2-F6**: dead anchor reads hits >= 9 -> boundary falsifier of the
   sealed verdict; HALT in-batch flow; escalate to claim-changing review
   (rule 12); no interior reading admitted.
3. **SH2-ANCHOR-FAIL**: k=0 re-seat fails (hits != 2^30, or any nontrivial
   trial with W != 3, or excess ratio != 1.0) -> F3 ramp-anchor indictment;
   HALT; no interior reading admitted; never evidence about shape (rule 5).
4. **SH2-RESEAT-FAIL**: k=16 re-seat reads outside [6, 30] -> F5 indictment
   of THIS batch's table path (committed measurements stand); HALT; interior
   readings recorded but no shape verdict composed; repair.
5. **SH2-SEED-DISAGREE**: branches 1-4 not fired AND (second-seed band at
   k=1 != primary-seed band at k=1, OR second-seed band at k=4 !=
   primary-seed band at k=4) -> NO shape verdict composed; seed instability
   at a load-bearing point recorded with both per-seed tuples; a k=1
   disagreement (a >2-order swing at the predicted magnitude) is additionally
   flagged as an instrument-level alarm; named successors: third seed at the
   disagreeing point and/or 2^32 arm and/or instrument review; Coordinator
   re-rank.
6. **SH2-DEAD-INTERIOR**: h(1) <= 5 AND h(2) <= 5 AND h(4) <= 5 AND h(8) <= 5
   (primary-seed readings) -> no hit-count excess at any tested interior
   point; the r=5 count excess does not survive dilution within the tested
   family (it exists only at or near k=16, which passed the re-seat gate);
   the k=1 conjunct is scoped as the JOINT EFFECT of the schedule switch and
   the first dilution step (SCOPE-1, section 7); recorded with per-point
   floors and named successors (k=12 finer dose near the full table;
   schedule-separated control under a new pin if adopted).
7. **SH2-NONMONO**: not SH2-DEAD-INTERIOR, and the band sequence over
   {1, 2, 4, 8, 16} is BAND-RISING (some k_a < k_b with bandrank(h(k_b)) >
   bandrank(h(k_a))) -> non-monotone curve, recorded as measured with the
   rise located; named successor (family-extension point inside the rise
   interval, or instrument review if the rise is k=8 NULL -> k=16 RESIDUAL,
   which also trips F5-adjacent scrutiny of the midpoint table path).
8. **SH2-MONOTONE-DECAY**: band sequence non-rising AND h(1) >= 100 AND
   h(4) <= 40 -> the count excess at THRESHOLD at the minimal dose decays
   with dilution to RESIDUAL-or-below by k=4; tunable-dose reading within
   tested scope; transition localized: (2,4] if h(2) >= 100; (1,2] if
   h(2) <= 40; ambiguous-at-k=2 if h(2) in 41-99 (recorded); count-level
   localization reported per tier-2 disjoint-CI pair (section 8); named
   successors: family extension to sub-localize the located interval
   (k=3/5/6, Coordinator decision), schedule-separated k=1 control (pin
   question), layer autopsy (IDEA-20260901-69912d) consumes the
   localization.
9. **SH2-PLATEAU**: band sequence non-rising AND h(1) >= 100 AND h(4) >= 100
   -> the count excess persists at THRESHOLD through k=4 (persistence
   plateau); first band drop at or after (4,8]: transition reported in (4,8]
   if h(8) <= 40, in (8,16] if h(8) >= 100, ambiguous-at-k=8 if h(8) in
   41-99 (recorded); named successors: family extension or k=12 inside the
   located interval (Coordinator re-rank), schedule-separated control (pin
   question).
10. **SH2-RESIDUAL**: DECLARED COMPLEMENT — any outcome matching none of the
    above, never force-binned. Enumerated expected subcases: (a) h(1) in
    41-99 (ambiguity at the minimal dose); (b) h(1) >= 100 with h(4) in
    41-99 (ambiguity at the locator); (c) h(1) <= 40, not DEAD, band
    non-rising — the residual-level-from-first-dose curve (the 582ea9
    SH-STEP / global-fragility outcome); (d) any remaining pattern. Named
    successors per subcase: (a)/(b) third seed at the ambiguous point at
    2^30 and/or one 2^32 arm at that point, Coordinator re-rank; (c) 2^32
    k=1 arm and/or schedule-separated control under a new pin; (d) record as
    measured, Coordinator re-rank.

Budget halts are resource_exhaustion, NEVER readings (rule 5). Per-point
tuples, the joint-effect scoping rule, the paraphrase discipline, and the
no-reopen clause apply in EVERY branch.

S0 evaluates branches 1-3 only (gate-fail, F6, anchor-fail); if none fires,
the S0 outcome is **PASS-S0**. Branches 4-10 belong to S1/S2 composition.

---

## 5. ANCHOR ORDER (BINDING)

- S0-5 dead anchor is run and ANALYZED BEFORE any alive reading (the
  ramp-zero anchor is an alive reading).
- S0-6 ramp-zero anchor before any interior point (interior points are S1
  and are not run by this task).
- Within S1 (successor task): k=16 re-seat ANALYZED FIRST, then k=1, k=2,
  k=4, k=8. S2 second seeds after S1. The SH2 verdict is composed only after
  ALL arms including second seeds are read, under the cascade of section 4.

---

## 6. SEAT TUPLES (armids 1/2/3/4/5/6/8/9)

All seats: amask=1, smask=1, log2N=30 (2^30 trials), threads=4, r=5 except
the r=6 dead anchor; PIN-T0 schedule pin (DEC-20260901-fb6f11). Seeds:
531001 primary grid, 531002 second seeds, 531004 dead anchor. Per-seed
readings, never pooled.

| armid | seat | rounds | sbox token | seed | stage | role |
|------:|------|--------|-----------|------|-------|------|
| 1 | aes (S_16 table set, r6 death reference) | 6 | aes | 531004 | S0 | DEAD ANCHOR, analyzed first (gate hits <= 8; tripwire >= 9 -> SH2-F6) |
| 5 | S_0 (identity) | 5 | identity | 531001 | S0 | RAMP-ZERO ANCHOR, BLOCKING (hits = 2^30, W=3 on 100% of nontrivial, excess ratio 1.0 exact; overflow 2^30 − 1024 legal under AMEND-1 with identities exact) |
| 8 | S_16 (aes) | 5 | aes | 531001 | S1 | KNOWN-ALIVE RE-SEAT, analyzed first within S1 (band [6,30] or SH2-RESEAT-FAIL) |
| 2 | S_1 | 5 | s1 | 531001 | S1 | AMEND-1 re-run, primary k=1 (overflow predicted saturated) |
| 3 | S_2 | 5 | s2 | 531001 | S1 | AMEND-1 re-run k=2 (overflow predicted saturated) |
| 4 | S_4 | 5 | s4 | 531001 | S1 | LOAD-BEARING TRANSITION LOCATOR k=4, first measurement |
| 4 | S_4 | 5 | s4 | 531002 | S2 | second seed k=4 — pre-registered by IDEA-20260902-9e84ac at the seat-fixed armid convention (seat armid fixed, seed family varies; no frozen pre-specification exists for that seat; no Coordinator relabel was issued at dispatch) |
| 6 | S_8 | 5 | s8 | 531001 | S1 | AMEND-1 re-run, floor point k=8 |
| 9 | S_1 | 5 | s1 | 531002 | S2 | second seed k=1 — the frozen 363851 pre-specified replication seat (not data-dependent) |

armid 7 (k=12) and armid 10 (amask=15 known-false seat) are reserved and NOT
spent in this design.

---

## 7. SCOPE-1 JOINT-EFFECT SCOPING RULE (adopted by DEC-20260902-38227b)

JOINT-EFFECT SCOPING (IDEA-20260902-9e84ac R4 resolution): under PIN-T0 the
key schedule is the AES schedule at EVERY interior point k >= 1 and is
therefore CONSTANT across k in {1,2,4,8,16}; all interior-to-interior
comparisons in this batch are schedule-clean, and any measured decay of h(k)
across the interior grid is attributed to table dilution at fixed schedule.
The schedule-vs-dilution confound attaches only to comparisons against
identity-schedule counterfactuals (k=0 anchor comparisons and any PINCTRL-1
control), which this batch does not make. Adopted for this batch only.

Consequences for S0 and every downstream record citing this batch: every
statement about h(1), and every k=0->k=1 comparison, is scoped as the JOINT
EFFECT of the schedule switch and the first dilution step. No dilution-only
attribution of h(1) anywhere. The k=0 ramp-zero anchor is consumed as the
instrument's zero only, never as the first point of a dose-attributed decay.

---

## 8. TWO-TIER RESOLUTION RULE

TIER 1 (BAND LEVEL) is the resolution of every branch conjunct — the frozen
sentinel granularity. Frozen per-point bands (inherited unchanged from 363851
Stage 1 via 582ea9): NULLBAND h <= 5; RESIDUAL-BAND 6 <= h <= 40;
AMBIGUITY-BAND 41 <= h <= 99; GRADUAL-THRESHOLD h >= 100. bandrank:
NULLBAND = 0, RESIDUAL = 1, AMBIGUITY = 2, THRESHOLD = 3. Band-rising
sentinel: the curve over tested interior points {1,2,4,8,16} is BAND-RISING
iff there exist tested points k_a < k_b with bandrank(h(k_b)) >
bandrank(h(k_a)); within-band inversions do NOT fire the sentinel.

TIER 2 (COUNT LEVEL) is admitted ONLY as reported content, under a
pre-registered disjoint-CI rule: a consecutive pair (k_a, k_b) is
COUNT-RESOLVED iff their Garwood 95% CIs are disjoint; if disjoint with
h(k_b) < h(k_a) it is reported as COUNT-DECAY-RESOLVED with the ratio and
propagated CI; if overlapping it is reported as COUNT-UNRESOLVED for that
pair, declared, never smoothed. Tier 2 replaces the frozen band-only
monotonicity SENTINEL for reporting purposes only (the sentinel's band-level
operation remains the branch-selection granularity). Design-time expectation
at the observed magnitudes: pairs (1,2) and (2,4) COUNT-DECAY-RESOLVED,
pairs (4,8) and (8,16) COUNT-UNRESOLVED.

---

## 9. PER-POINT SENSITIVITY FLOORS

Re-derived at design time (IDEA-20260902-9e84ac design_time_power, exact
Poisson; unchanged from 582ea9): one-sided rejection toward excess at
h >= 6; size P(h >= 6 | lambda=1) = 5.94e-4; power 0.084 at lambda=3, 0.384
at 5, 0.554 at 6, 0.699 at 7, 0.809 at 8, 0.933 at 10, 0.950 at 10.5, 0.989
at 13, 0.9998 at 19.

DECLARED PER-POINT SENSITIVITY FLOORS: lambda_80 ~= 8.0, lambda_95 ~= 10.5
hits per 2^30 — a NULLBAND reading excludes a per-point excess >= ~8-10.5 at
80-95% power and excludes NOTHING below that (a true lambda=6 point reads
NULLBAND 45% of the time). Floor-vs-null (analytic lambda_0 = 1.0 per 2^30)
is decidable at 2^30; floor MAGNITUDE (12 vs 13 vs 14 vs 19) is NOT
resolvable at 2^30 single seed (overlapping Garwood CIs) — priced
obstruction, never smoothed.

---

## 10. NO-REOPEN CLAUSE

The X statistic is not tested, decided, or reported as a reading at any
point; the t=1 X lane is closed by EV-AES-896ef2 and stays closed. The
instrument's e fields (zero_mask_e, wt_e_byte, wt_e_bit, vanishing_word_mask
inside hit_e_detail; ezdiag_*/ezoff_* class counters) ride as enabling
artifacts only; NO branch conjunct consumes them, and no carrier sentence
about e is drawn from them. There is NO rho-exclusion of any kind at any
interior point. The measured t=1 frontier rho_80 = 0.1183 of EV-AES-896ef2
is carried as the standing closed-lane sensitivity-floor control reading,
reported BESIDE the shape verdict, never merged. Any downstream paraphrase
reporting these fields as a carrier reading violates this record's scope.

---

## 11. SEED-DISAGREEMENT RULE

Second seeds at k=1 (frozen 363851 armid-9 seat, seed 531002) and k=4 (this
record's pre-registered seat-fixed armid-4 seat, seed 531002). Per-seed
readings, never pooled. Band agreement at k=1 and k=4 between primary seed
531001 and second seed 531002 is the pre-registered verdict-stability
condition: disagreement fires branch 5 (SH2-SEED-DISAGREE) of the cascade —
no shape verdict composed; the instability itself is the scoped finding,
recorded with both per-seed tuples and named successors (third seed at the
disagreeing point and/or 2^32 arm and/or instrument review; Coordinator
re-rank). A k=1 band disagreement (a >2-order swing at the predicted
magnitude) is additionally an instrument-level alarm. Exact-rate comparisons
at agreed bands report seed variance with propagated Garwood CIs.

---

## 12. TIMING STRIP SET (determinism comparisons)

Byte-identity comparisons of receipts (the S1-6 overflow-positive
determinism double and any cross-batch receipt comparison) strip EXACTLY:

- `elapsed_seconds_measured`
- `measured_rate_trials_per_sec`

and no other fields.

---

## 13. S0 GATE/ANCHOR EXPECTATIONS (this task)

- S0-2 BUILD IDENTITY: sha256 of the copied source and binary vs the
  BATCH-7b798d snapshot receipt hashes — EXPECTED PASS (zero source change).
  PRICED FALLBACK on ANY mismatch: full Gate-0x rebuild (aes, r5, amask=1,
  smask=1, 2^30, seed 531001, armid 1, threads 2) field-exact vs
  L1-AES-R5-P30 under the extended allowed-diff list
  {arm, elapsed_seconds_measured, hit_log_cap, measured_rate_trials_per_sec,
  oracle, probe} + additive pin-label fields {schedule_pin,
  schedule_pin_position, schedule_pin_decision}, BEFORE any reading arm.
- S0-3 KAT PINS: `pin 363851` -> pin_pass true; `pinidentity 363851` ->
  pin_pass true. Any failure -> SH2-GATE-FAIL.
- S0-4 TABLE-FREEZE RE-VERIFICATION: rerun `freeze 363851`; digests,
  bijection, nestedness, cross_k_nesting ALL identical to the committed
  R3_table_freeze.json
  (coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json);
  position_order and the cap-INDEPENDENT folded-smoke selfcheck counters
  additionally compared; the cap-DEPENDENT selfcheck fields
  (hit_detail_records, hit_log_overflow) differ by construction (committed
  file is cap-64, this build cap-256) and are disclosed, not compared. Any
  mismatch on compared fields -> SH2-GATE-FAIL.
- S0-5 DEAD ANCHOR (analyzed FIRST among reading-bearing arms): (aes, r6,
  amask=1, smask=1, 2^30, seed 531004, armid 1, threads 4). Gate hits <= 8
  (carried dead band at 2^30). Tripwire hits >= 9 -> SH2-F6 HALT, escalate
  to claim-changing review (rule 12), no interior reading admitted. A 0-hit
  anchor passes with reduced assurance (direction-safe; inherited precedent,
  rule 8 recorded).
- S0-6 RAMP-ZERO ANCHOR (BLOCKING): k=0 identity re-seat (S_0, r5, amask=1,
  smask=1, 2^30, seed 531001, armid 5, threads 4). Gate: hits = 2^30
  exactly, T = 0, W = 3 on 100% of nontrivial trials (whist
  [0,0,0,2^30,0]), excess ratio 1.0 exact; overflow = 2^30 − 1024
  saturated-by-construction with ALL counter identities exact — legal under
  AMEND-1 (pure cap truncation; section 1.2 proves-too-much control: if the
  gate fails this receipt, the gate itself is indicted -> SH2-GATE-FAIL).
  Any count-level departure -> SH2-ANCHOR-FAIL (F3) halt.

S0 OUTCOME (ordered, first match wins): SH2-GATE-FAIL / SH2-F6 /
SH2-ANCHOR-FAIL / PASS-S0.

---

## 14. BUDGET AND SCOPE DISCIPLINE (this task)

Wall clock 5400 s TOTAL for S0 (binding stop; every arm stamped in
budget_stamps.jsonl). Maximum 8 binary invocations. Memory 4 GB. Every arm
runs under `timeout 3600`. Budget exhaustion is resource_exhaustion, NEVER a
reading (rule 5).

Toy tier. NO deployed-AES claims. NO published-cryptanalysis comparisons in
either direction. NO interior k arms (k=1/2/4/8) in S0 — those belong to
Stage S1 (TASK-20260902-525d16). No X statistic, no rho-exclusion (section
10). No git add/commit by this producer. No status/strength/promotion
interpretation — observations only.

Binding baseline convention: ~27 min per 2^30 4-thread arm and ~54 min for
the 2-thread Gate-0x rebuild are the BUDGET contract; measured campaign
hardware rates (~94-155 s per arm) are OPTIMISTIC-RELATIVE and disclosed,
never charged as the baseline.

## 15. PARAPHRASE DISCIPLINE (binding on downstream citation)

Never: 'ramp closed' or any closure sentence beyond the scoped branch
verdict; a carrier sentence about e; 'zeros again'; X-lane fields reported
as readings; a decay/survival sentence citing the BATCH-7b798d readings as
validated evidence; an attribution of h(1) or the k=0->k=1 drop to dilution
per se (SCOPE-1 joint effect); 'extinction by k=8'/'floor reached at k=8'
from within-band comparisons; presenting overflow at k=1/k=2 as a gate
failure under AMEND-1; presenting AMEND-1 as a retroactive validation of the
BATCH-7b798d readings (no post-hoc rescue; prospective only); presenting the
k=4 arm as refinement (it is the load-bearing transition locator).

Always carry scope: cell (amask=1, smask=1), r=5, PIN-T0, 2^30 per point,
frozen family subset {0,1,2,4,8,16}, seeds as run (531001 primary grid,
531002 second seeds, 531004 dead anchor), toy tier.
