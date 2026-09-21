# PREREGISTRATION — TASK-20260903-695ebe (BATCH-060cb4, GOAL-AES-003) — Stage S0

WRITE-ONCE. Committed before any binary invocation (mtime recorded in
budget_stamps.jsonl as `preregistration_written`, before the first invocation
of the affarm046ex binary). This file binds the S0 producer execution of
IDEA-20260903-8f26ac under DEC-20260903-63cd8d (batch opening; SCOPE-1
binding attribution rule; NARROW-1/2/3 binding paraphrase discipline) and
DEC-20260901-6f9de3 (AMEND-1). It commits the FULL batch decision cascade
(CC, CC8, CC3) pre-arm as the proposal requires; S0 itself decides
instrument validity and anchors ONLY — it decides NO shape (no interior
point k >= 1 is run in S0; interior readings belong to Stages S1/S2).

Instrument lineage (UNCHANGED, zero source change in S0/S1): the BATCH-e5d753
snapshot-bound PIN-T0 widened build `affarm046ex` (HIT_LOG_CAP = 256 per
thread; source sha256 ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37,
binary sha256 74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702),
copied byte-exact into this task's src/ from
`coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/src/`
and re-verified by sha256 against the BATCH-e5d753 snapshot receipt
`coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/archives/TASK-20260902-e19f39/snapshot-receipt.json`
in S0-2.

Pin reference: PIN-T0 (DEC-20260901-fb6f11): SubWord uses TPOS[0] (first
position of the frozen order): identity schedule at k=0, AES schedule at
every k >= 1.

---

## 1. AMEND-1 COUNTER-INCONSISTENCY GATE (VERBATIM)

From DEC-20260901-6f9de3, AMEND-1 (ratified on first application by RAT-2 of
DEC-20260902-7ad3d9):

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

Conjunct form as adopted in the CC cascade (IDEA-20260903-8f26ac
integrity_gate_amend1.verbatim_conjunct): 'counter INCONSISTENCY on an
analysis-bearing receipt -> invalid_measurement', with counter inconsistency
meaning (a), (b), (c) exactly as above.

### 1.1 Saturation-aware evaluation rule (strictest reading, not a relaxation)

On every analysis-bearing receipt, `overflow == hits − logged_detail_records`
EXACTLY, where `logged_detail_records == threads×HIT_LOG_CAP` when
`hits > threads×HIT_LOG_CAP` (saturated; coincides with AMEND-1's verbatim
conjunct-(a) form) and `logged_detail_records == hits` with `overflow == 0`
otherwise (unsaturated). In this instrument `hits` is the receipt field
`W_ge1_nontrivial` (the receipt carries no field literally named "hits"), and
`logged_detail_records` is the total per-thread logged record count,
recoverable from the receipt as the number of `hit_trials` entries (each
thread logs min(hits_t, HIT_LOG_CAP) records).

Predicted saturation status (design-time, from the committed VALIDATED
BATCH-e5d753 readings EV-AES-868db1, unlike the predecessor's unvalidated
priors): S0-5 dead anchor predicted unsaturated; S0-6 ramp-zero anchor
saturated by construction (overflow 2^30 − 1024); S1-1 k=2 seed2 saturated
(predicted overflow ~148k); S1-2 k=8 seed2 predicted unsaturated; S2b k=3
seeds saturated under the multiplicative prior (~1759 hits -> overflow ~735)
but unsaturated legal under AMEND-1 if realized <= 1024 — both paths legal
with the admissible set unchanged.

### 1.2 AMEND-1 proves-too-much control (S0-6)

The AMEND-1 gate must PASS the ramp-zero receipt (overflow 2^30 − 1024,
saturated by construction, all counter identities exact). If the gate fails
THAT receipt, the gate itself is indicted before any interior reading:
CC-GATE-FAIL halt (DEC-20260903-63cd8d review_plan.proves_too_much).

---

## 2. COUNTER IDENTITIES CHECKED PER ANALYSIS-BEARING RECEIPT

1. sum(whist) == nontrivial_trials
2. h == sum(whist[1:]) where h = W_ge1_nontrivial (= "hits")
3. moment identity: sum(W_ge1_by_word) == sum(W * whist[W]) over W in 1..4
4. sum(zhist) == nontrivial_trials — DEV-S0-1 CORRECTED form (lineage
   DEV-S0-1, validator-source-verified, OBS-VAL-1 discharge): affarm046ex.c
   increments zhist ONLY on nontrivial trials (the trivial `continue` at
   affarm046ex.c:458 precedes the zhist/whist increments at :459, frozen
   whist convention 'trivial-swap trials are excluded from all e
   statistics'), so the TRUE internal identity is
   sum(zhist) == nontrivial_trials. The literal '== trials' shorthand of
   IDEA-20260902-9e84ac is NOT carried in this record's gate list; it holds
   only when trivial_swaps_excluded == 0 and is reported informationally as
   `sum_zhist_eq_trials_literal` in every analysis output.
5. sum(ewhist_all) == nontrivial_trials
6. sum(ewhist_hit) == h
7. sum(ewhist_miss) == nontrivial_trials − h
8. overflow == hits − logged_detail_records (saturation-aware form of §1.1;
   coincides with the verbatim conjunct-(a) form `overflow == hits −
   threads×HIT_LOG_CAP` on saturated receipts; the verbatim form is reported
   informationally on unsaturated receipts, never as a gate conjunct there)
9. trials accounting: trivial_swaps_excluded + nontrivial_trials == trials == 2^log2N

---

## 3. ADMISSIBLE vs INADMISSIBLE QUANTITIES

ADMISSIBLE (counter-derived only; survive cap truncation — source-verified,
TASK-20260901-87a39b check_7, re-confirmed at source level by
IDEA-20260903-8f26ac this session): h(k) = W_ge1_nontrivial, whist,
W_ge1_by_word, zhist, all ewhist_*/ewbithist_*/ezdiag_*/ezoff_* class
counters, hit_overflow, excess ratio h/excess_E under the frozen
excess_E = 2^30 convention, excess over the run-internal accidental-hit
rate, Garwood 95% CIs (count and exposure only), band assignment, all
identity checks of section 2, arm_table_concat_sha256 table digests.

INADMISSIBLE (detail-log-derived; NOTHING in this batch is derived from the
capped detail log): hit_e_detail records, hit_trials as a SAMPLE of hit
structure, any distributional statement over hits derived from detail
records, any X-lane computation. On saturated receipts the logged records
are the FIRST 256 hits per thread — biased toward early trials, not a random
sample. Retained as report-only enabling data under the no-reopen clause
(section 12); NO branch conjunct consumes them, so AMEND-1(c) is satisfied
by construction.

---

## 4. TOP-LEVEL CC CASCADE (EXHAUSTIVE, ORDERED) — WITH PRECEDENCE CLAUSE

### 4.1 Precedence clause (restated standalone, mandatory)

This record's decision rule is an EXHAUSTIVE ORDERED CASCADE
(CC-GATE-FAIL > CC-F6 > CC-ANCHOR-FAIL > CC-SEED-DISAGREE >
CC-COUNT-DISAGREE > CC-AGREE, with the orthogonal CC8-FLOOR-DEPART /
CC8-AGREE finding axis evaluated beside branches 4-6, and the CC3
sub-cascade gated to Stage S2) committed in S0-1 before any arm runs. By
construction no two branches can be assigned the same outcome: branches 1-3
are halt conditions preceding all verdict composition; branch 4 consumes any
k=2 band-departure outcome before any count branch composes; branches 5 and
6 are disjoint by conjunct (CI disjointness vs overlap); branches 7/8 are
disjoint by conjunct (h <= 5 vs 6 <= h <= 40) and orthogonal to 4-6; the
CC3 branches are disjoint by the band-partition of the two k=3 readings
with the NULLBAND case ordered before SUBLOCALIZE-EARLY (whose 6 <= h
conjunct excludes it). This cascade is RE-AUTHORED for the post-verdict
replication question, not an amendment of the 9e84ac SH2 cascade (which
remains bound to BATCH-e5d753, immutable, and whose verdict this record
never recomposes).

### 4.2 Branches, evaluated in this FIXED ORDER

1. **CC-GATE-FAIL**: any integrity gate fails (S0-2 build identity or its
   Gate-0x fallback, S0-3 KAT, S0-4 freeze re-verification, S1-3 post-arm
   digest/source-diff, or counter INCONSISTENCY on any analysis-bearing
   receipt — AMEND-1 VERBATIM per section 1, evaluated per section 1.1).
   -> invalid_measurement; HALT; repair (rule 5); never evidence about shape.
2. **CC-F6**: dead anchor reads hits >= 9 -> boundary falsifier of the
   sealed verdict; HALT in-batch flow; escalate to claim-changing review
   (rule 12); no reading admitted.
3. **CC-ANCHOR-FAIL**: k=0 re-seat fails (hits != 2^30, or any nontrivial
   trial with W != 3, or excess ratio != 1.0) -> F3 ramp-anchor indictment;
   HALT; no interior reading admitted; never evidence about shape (rule 5).
4. **CC-SEED-DISAGREE**: branches 1-3 not fired AND band(h(2)_531002) !=
   THRESHOLD -> NO count-level sentence at k=2 of any kind. A band departure
   at the realized magnitude is a ~386-sd event (~354 sd under a -16%
   swing), so this outcome additionally carries an INSTRUMENT-LEVEL ALARM
   flag (the 9e84ac branch-5 k=1 precedent applied to k=2): the table path,
   the stream derivation, and the seat digests are re-examined before any
   successor. Stage S2 BLOCKED (no family extension on a suspect
   instrument); named successors (third seed at k=2, instrument review,
   2^32 arm under a new decision); Coordinator re-rank.
5. **CC-COUNT-DISAGREE**: branch 4 not fired AND (the count CIs are disjoint
   OR the per-seed decay-ratio CIs are disjoint, per section 5) ->
   determinate seed-variance finding at k=2 at count level. The band verdict
   is unaffected (band agreement holds); the count-decay replication FAILS
   at the declared resolution; both per-seed tuples recorded, never pooled,
   never smoothed; the magnitude of the disagreement becomes the input to
   the successor design. Named successors (third seed at k=2 at 2^30 and/or
   a 2^32 k=2 arm under a new decision, Coordinator re-rank); Stage S2 still
   executes (a count-level disagreement is a finding, not an instrument
   indictment).
6. **CC-AGREE**: branch 4 not fired AND count CIs overlap AND ratio CIs
   overlap -> COUNT-REPLICATED: SH2-MONOTONE-DECAY is EXTENDED TO COUNT
   LEVEL for the pairs (1,2) and (2,4): the k1->k2 count-decay ratio is
   replicated across two independent seed environments within the declared
   resolution (both per-seed ratios reported with CIs); and since k=4
   already carries two committed seeds, the (2,4) pair's count decay
   (primary-seed ratio 8786.5) acquires the same per-seed evaluation,
   reported under the identical disjoint-CI rule. NARROW-2's caveat is
   discharged for exactly these two pairs and NO others — (4,8) and (8,16)
   remain COUNT-UNRESOLVED in every outcome of this batch. Stage S2 executes.
7. **CC8-FLOOR-DEPART**: h(8)_531002 <= 5 (NULLBAND; the only live departure
   direction — AMBIGUITY/THRESHOLD departures have probability < 1e-6 under
   any lambda consistent with the committed reading) -> a determinate
   FLOOR-INSTABILITY finding at k=8 that realizes the RT-J8 sensitivity (the
   band verdict implicitly depends on the floor never dipping below
   RESIDUAL; a dip on an independent draw qualifies the verdict's extension
   to the seed population, recorded with both per-seed tuples; the
   BATCH-e5d753 verdict on grid {1,2,4,8,16} remains IMMUTABLE either way).
   Recorded beside the k=2 verdict, never gating it. P(departure) ~ 0.011
   under lambda=13, but ~0.45 if the true rate sits near the committed CI's
   lower edge (lambda=6) — both priced, neither an instrument alarm (a
   ~2.2-sd reading is a finding, not a defect).
8. **CC8-AGREE**: h(8)_531002 in RESIDUAL [6,40] -> the floor is seed-stable
   at band level at k=8 (second independent draw of the live floor; the
   RT-J8-named sensitivity stands tested and untriggered; per-seed counts
   reported, CI overlap declared, never smoothed).

BRANCHES 7/8 ARE EVALUATED FOR BOTH k=2 OUTCOMES (5)/(6) AND ARE ORTHOGONAL
FINDINGS (evaluated after the k=2 verdict, never gating it).

S0 evaluates branches 1-3 only (gate-fail, F6, anchor-fail); if none fires,
the S0 outcome is **PASS-S0**. Branches 4-8 belong to S1 composition; the
CC3 sub-cascade belongs to Stage S2.

Budget halts are resource_exhaustion, NEVER readings (rule 5). Per-point
tuples, the SCOPE-1 scoping rule, the paraphrase discipline, and the
no-reopen clause apply in EVERY branch.

---

## 5. CC DECISION RULE AT k=2 (band + count + ratio)

INPUTS FROZEN (committed BATCH-e5d753 readings, EV-AES-868db1; consumed as
inputs and NOT re-measured): h(1)_531001 = 12,681,109 (CI [12,674,130.4,
12,688,090.5]); h(1)_531002 = 12,679,968; h(2)_531001 = 149,371 (CI
[148,614.5, 150,130.4]); h(4)_531001 = 17 (CI [9.9, 27.2]); h(4)_531002 = 21
(CI [13.0, 32.1]); h(8)_531001 = 13 (CI [6.9, 22.2]). New readings this
batch: h(2)_531002 (S1-1), h(8)_531002 (S1-2).

BAND CRITERION (k=2): BAND-AGREE at k=2 iff band(h(2)_531002) ==
band(h(2)_531001) == THRESHOLD (evaluated on realized readings; the
committed primary band is THRESHOLD, stated so the criterion has determinate
content, but the rule itself compares realized bands).

COUNT CRITERION (k=2, Garwood overlap): COUNT-AGREE at k=2 iff the Garwood
95% CIs (campaign Wilson-Hilferty convention) of h(2)_531001 and
h(2)_531002 OVERLAP: with CI_a = [148,614.5, 150,130.4] and CI_b =
[L_b, U_b], overlap iff 148,614.5 <= U_b AND L_b <= 150,130.4. COMPUTED AT
DESIGN TIME at the realized magnitude 149,371: overlap holds exactly when
the seed ratio h(2)_531002/h(2)_531001 lies in **[0.9899, 1.0102]**
(disjoint-above threshold count 150,891, ratio 1.01018; disjoint-below
threshold count 147,858, ratio 0.98987) — the COUNT-AGREEMENT WINDOW,
committed pre-arm.

RATIO CRITERION (k=2, per-seed decay ratios with corner propagation):
per-seed decay ratios r_s = h(1)_s / h(2)_s, evaluated WITHIN each seed
environment (cross-seed mixed ratios are report-only, never decay
statements — the schedule-derived key co-varies with the seed).
r_531001 = 84.8967 with propagated CI
[L(1)_531001/U(2)_531001, U(1)_531001/L(2)_531001] = [84.4208, 85.3759]
(CORNER PROPAGATION from Garwood count CIs — the campaign convention of
BATCH-e5d753 check_6: ratio CI from the count-CI corners (L_num/U_den,
U_num/L_den)). r_531002 = 12,679,968/h(2)_531002 with CI
[L(1)_531002/U(2)_531002, U(1)_531002/L(2)_531002]. RATIO-AGREE iff
CI(r_531001) and CI(r_531002) overlap. CHECKED IMPLICATION committed
pre-arm: at the committed magnitudes the ratio criterion and the count
criterion coincide to < 1e-4 in the ratio thresholds (the k=1 CIs are
0.055%-scale and shared across the comparison); if the realized readings
ever separate the two criteria, the STRICTER reading wins (any disjointness
-> COUNT-DISAGREE) and the separation is recorded per rule 8.

VERDICT ROUTING: CC-AGREE = BAND-AGREE AND COUNT-AGREE AND RATIO-AGREE;
CC-COUNT-DISAGREE = BAND-AGREE AND (count CIs disjoint OR ratio CIs
disjoint); CC-SEED-DISAGREE = band(h(2)_531002) != THRESHOLD. Routing per
section 4.2 branches 4-6.

k=8 CRITERION (CC8): CC8-AGREE iff band(h(8)_531002) == band(h(8)_531001)
== RESIDUAL; CC8-FLOOR-DEPART iff h(8)_531002 <= 5 (NULLBAND). Orthogonal
finding axis (section 4.2 branches 7/8).

---

## 6. CC3 CASCADE (STAGE S2, committed pre-arm) WITH DECLARED-DIFF LIST AND
SURFACE-DIFF BATTERY REFERENCE

### 6.1 Declared source diff (BINDING allowed-diff list; audited in S2a-1)

(i) arm-mode sbox-token whitelist: ADD token s3 mapping to ksel=3 (one
else-if branch, mirroring the existing s1/s2/s4/s8/s12 lines at
affarm046ex.c:843-847 of the snapshot-bound copy); the refusal message
updated to name the admitted set.
(ii) FREEZE_KS: {0,1,2,4,8,12,16} -> {0,1,2,3,4,8,12,16} (one array entry;
loop bounds 7 -> 8 in the point-emission loop at affarm046ex.c:744 and the
cross-k-nesting loop at :776 of the snapshot-bound copy).
(iii) usage string and the freeze-mode header comment, naming the extended
point.
NOTHING ELSE: no change to counter increment sites (:459-499), cap logic
(:489-495), the schedule-pin block, stream derivation, receipt emission,
pin/pinidentity/geom modes, or any table-construction function. The S2a-1
source-diff audit must show EXACTLY this diff against the snapshot-bound
source; any additional diff is CC3-GATE-FAIL.

### 6.2 Surface-diff battery reference (extended freeze commitment, S2a-4)

S2a-4 runs the extended freeze mode and digests its output via the committed
freeze_digest.py convention into a NEW write-once freeze file
(R4_table_freeze_ext.json, task-scoped). SURFACE-DIFF BATTERY (pre-
registered): (a) for every k in {0,1,2,4,8,12,16}, all per-position table
sha256 digests, position lists, per_position_is_aes flags, bijection and
nestedness checks MUST equal the committed R3_table_freeze.json values
exactly — any mismatch is CC3-GATE-FAIL (the extension perturbed the frozen
surface); (b) the k=3 entry (positions [0,4,8], per-position digests,
bijection true, nestedness true) is committed in the same file with mtime
BEFORE any k=3 arm (S2a-4 precedes S2b-2/S2b-3); (c) cross_k_nesting true
over all eight points (P_3 subset P_4 structural); (d) the folded selfcheck
mini-arms (selfcheck_identity_k0, selfcheck_aes_k16 at log2N=10) pass the
committed assertions — the selfcheck_identity_k0 arm doubles as the extended
build's identity-seat behavioral check (a 2^30 ramp-zero re-seat on the
extended build is DECLINED as redundant — the declared diff provably leaves
the identity path untouched; the diff audit + selfcheck + Gate-0x cover
every code path the extension touches). Post-arm (S2b-4) the freeze re-runs
and re-verifies against R4 exactly.

### 6.3 CC3 branches, evaluated in FIXED ORDER after the S2b readings

1. **CC3-GATE-FAIL**: any S2 integrity gate fails (declared-diff audit,
   Gate-0x extended rebuild field-exact vs L1-AES-R5-P30 under the extended
   allowed-diff list, KAT re-pins, surface-diff battery, dead-anchor counter
   identities, determinism double, post-arm audits, or counter inconsistency
   on any extended-build receipt) -> invalid_measurement, HALT, repair
   (rule 5), never evidence about shape.
2. **CC3-F6**: extended-build dead anchor hits >= 9 -> boundary falsifier of
   the sealed verdict; HALT, escalate to claim-changing review (rule 12).
3. **CC3-SEED-DISAGREE**: band(h(3)_531001) != band(h(3)_531002) -> no
   sub-localization sentence; seed instability at k=3 recorded with both
   tuples; named successors (third seed at k=3, instrument review if the
   departure is >= 2 bands).
4. **CC3-NONMONO-EXT**: h(3) <= 5 (NULLBAND) on EITHER seed while the
   committed k=4 readings stay RESIDUAL -> the bandrank sequence on the
   EXTENDED grid {1,2,3,4,8,16} rises at 3->4 (rank 0 -> 1): a determinate
   non-monotone finding scoped to the extended family (the floor dips below
   the k=4 floor at k=3); the BATCH-e5d753 verdict on grid {1,2,4,8,16}
   stands unchanged and immutable; named successors (third seed at k=3,
   instrument review of the k=3 table path, re-rank). Evaluated before the
   sub-localize branches (the h <= 5 case is a subset of h <= 40; ordering
   plus the 6 <= h conjunct below make the branches disjoint — the
   DEAD-before-NONMONO resolution form of the 9e84ac cascade, inherited
   deliberately).
5. **CC3-SUBLOCALIZE-LATE**: h(3) >= 100 (THRESHOLD) on BOTH seeds ->
   transition localized to (3,4] at band level (refinement of (2,4]);
   count-level tier-2 content for pairs (2,3) and (3,4) reported per seed
   under the disjoint-CI rule, never consumed by the band sentence.
6. **CC3-SUBLOCALIZE-EARLY**: 6 <= h(3) <= 40 (RESIDUAL) on BOTH seeds ->
   transition localized to (2,3] at band level; the extended-grid bandrank
   sequence [3,3,1,1,1,1] is non-rising.
7. **CC3-AMBIGUOUS**: 41 <= h(3) <= 99 (AMBIGUITY) on BOTH seeds ->
   transition stays in (2,4] with ambiguity declared at k=3; named successor
   (third seed at k=3 at 2^30 and/or one 2^32 k=3 arm under a new decision,
   Coordinator re-rank).
8. **CC3-RESIDUAL-COMPLEMENT**: declared complement — any outcome matching
   none of the above (including mixed near-boundary readings not caught by
   branch 3), never force-binned, recorded as measured with named
   successors.

EVERY CC3 outcome carries the floor-is-alive statement (NARROW-1) and the
SCOPE-1 attribution rule; budget halts are resource_exhaustion, never
readings (rule 5).

---

## 7. ANCHOR ORDER (BINDING)

- S0-5 dead anchor is run and ANALYZED FIRST among reading-bearing arms
  (the ramp-zero anchor is an alive reading; its arm is invoked only AFTER
  the dead anchor's analysis has completed without firing CC-F6 or
  CC-GATE-FAIL).
- S0-6 ramp-zero anchor before any interior point (interior points are S1
  and are not run by this task).
- Within S1 (successor task): S1-1 (k=2 seed2) before S1-2 (k=8 seed2); CC
  composition after both. Within S2a: extended-build dead anchor analyzed
  first among extended alive readings. Within S2b: k=3 primary (531001)
  then k=3 second seed (531002); CC3 composition after both. The batch's
  additive content is composed only after ALL executed arms are read.

---

## 8. SEAT TUPLES (armids 1/3/5/6/11)

All seats: amask=1, smask=1, log2N=30 (2^30 trials), threads=4, r=5 except
the r=6 dead anchor; PIN-T0 schedule pin (DEC-20260901-fb6f11). Seeds:
531001 primary grid, 531002 second seeds everywhere (same-pair
comparability), 531004 dead anchor (re-seat of the lineage dead anchor).
Per-seed readings, never pooled. Seat-fixed armid convention for second
seeds (9e84ac precedent): the seat's armid is fixed, the seed family varies.
Stream derivation seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15
makes each (seed, armid) pair a distinct thread-stream.

| armid | seat | rounds | sbox token | seed | stage | role |
|------:|------|--------|-----------|------|-------|------|
| 1 | aes (S_16 table set, r6 death reference) | 6 | aes | 531004 | S0 | DEAD ANCHOR, analyzed FIRST among reading-bearing arms (gate hits <= 8; tripwire >= 9 -> CC-F6) |
| 5 | S_0 (identity) | 5 | identity | 531001 | S0 | RAMP-ZERO ANCHOR, BLOCKING (hits = 2^30, W=3 on 100% of nontrivial, excess ratio 1.0 exact; overflow 2^30 − 1024 legal under AMEND-1 with identities exact; AMEND-1 proves-too-much control) |
| 3 | S_2 | 5 | s2 | 531002 | S1 | CORE MANDATORY second seed k=2 (seat-fixed armid convention; table digests re-verified vs the R3 k=2 entry per receipt; overflow predicted saturated ~148k) |
| 6 | S_8 | 5 | s8 | 531002 | S1 | second seed k=8 (seat-fixed armid convention; overflow predicted unsaturated) |
| 11 | S_3 (NEW seat, extension point) | 5 | s3 | 531001 then 531002 | S2b | first-ever k=3 measurement, then unconditional second seed (two-draw entry discipline). Introduced per the frozen armid-plan convention (new seats take the lowest unallocated armid >= 11); DEC-20260903-63cd8d confirms armid 11; no Coordinator relabel was issued at dispatch |

Armids 2/4/7/8/9/10 are NOT spent by this batch's S0 (armids 9 and 10 stay
unspent lineage-wide; k=1 is not re-measured in this batch).

---

## 9. SCOPE-1 JOINT-EFFECT SCOPING RULE (adopted by DEC-20260902-38227b,
carried as binding by DEC-20260903-63cd8d)

Under PIN-T0 the key schedule is the AES schedule at every interior point
k >= 1 and is constant across interior k; interior-to-interior comparisons
are schedule-clean; any interior decay is attributed to table dilution AT
FIXED SCHEDULE; no dilution-only language. Extended here to grid+{3}: k=3
is interior under PIN-T0 and joins the schedule-clean comparisons.
PINCTRL-1 remains deferred (RANK 3, untouched).

Consequences for S0 and every downstream record citing this batch: every
statement about h(1), and every k=0->k=1 comparison, is scoped as the JOINT
EFFECT of the schedule switch and the first dilution step. No dilution-only
attribution of h(1) anywhere. The k=0 ramp-zero anchor is consumed as the
instrument's zero only, never as the first point of a dose-attributed decay.

---

## 10. TWO-TIER RESOLUTION RULE

TIER 1 (BAND LEVEL) is the resolution of every branch conjunct — the frozen
sentinel granularity. Frozen per-point bands: NULLBAND h <= 5; RESIDUAL-BAND
6 <= h <= 40; AMBIGUITY-BAND 41 <= h <= 99; GRADUAL-THRESHOLD h >= 100.
bandrank: NULLBAND = 0, RESIDUAL = 1, AMBIGUITY = 2, THRESHOLD = 3.

TIER 2 (COUNT LEVEL) is admitted ONLY as reported content, under a
pre-registered disjoint-CI rule: a consecutive pair (k_a, k_b) is
COUNT-RESOLVED iff their Garwood 95% CIs are disjoint; if disjoint with
h(k_b) < h(k_a) it is reported as COUNT-DECAY-RESOLVED with the ratio and
propagated CI; if overlapping it is reported as COUNT-UNRESOLVED for that
pair, declared, never smoothed. Design-time expectation at the committed
magnitudes: pairs (1,2) and (2,4) COUNT-DECAY-RESOLVED; pairs (4,8) and
(8,16) COUNT-UNRESOLVED in every outcome of this batch.

---

## 11. PER-POINT SENSITIVITY FLOORS

Inherited from the lineage (re-derived at design time by
IDEA-20260903-8f26ac, exact Poisson): one-sided rejection toward excess at
h >= 6; size P(h >= 6 | lambda=1) = 5.94e-4; power 0.084 at lambda=3, 0.384
at 5, 0.554 at 6, 0.699 at 7, 0.809 at 8, 0.933 at 10, 0.950 at 10.5, 0.989
at 13, 0.9998 at 19.

DECLARED PER-POINT SENSITIVITY FLOORS: lambda_80 ~= 8.0, lambda_95 ~= 10.5
hits per 2^30 — a NULLBAND reading excludes a per-point excess >= ~8-10.5 at
80-95% power and excludes NOTHING below that (a true lambda=6 point reads
NULLBAND 45% of the time). Floor-vs-null (analytic lambda_0 = 1.0 per 2^30)
is decidable at 2^30; floor MAGNITUDE (17 vs 13 vs 12 vs comparator 1.0) is
NOT resolvable at 2^30 (overlapping Garwood CIs; the cheap pooled hook was
computed and declined: per-2^30 CI [8.09, 18.45]) — priced obstruction,
deferred to the RANK-2 pooled route, never smoothed.

---

## 12. NO-REOPEN CLAUSE

The X statistic is not tested, decided, or reported as a reading at any
point; the t=1 X lane is closed by EV-AES-896ef2 and stays closed. The
instrument's e fields (zero_mask_e, wt_e_byte, wt_e_bit,
vanishing_word_mask inside hit_e_detail; ezdiag_*/ezoff_* class counters)
ride as enabling artifacts only; NO branch conjunct consumes them, and no
carrier sentence about e is drawn from them. There is NO rho-exclusion of
any kind at any interior point. The measured t=1 frontier rho_80 = 0.1183
of EV-AES-896ef2 is carried as the standing closed-lane sensitivity-floor
control reading, reported BESIDE this batch's verdicts, never merged. Any
downstream paraphrase reporting these fields as a carrier reading violates
this record's scope.

---

## 13. NARROW-1/2/3 DISCIPLINE (VERBATIM, from DEC-20260903-63cd8d
rules_carried, ratified from DEC-20260902-7ad3d9)

- **NARROW-1** (source DEC-20260902-7ad3d9): Floor-is-alive: every
  downstream sentence carries the live residual floor (h(4..16) = 17/13/12,
  decidable excess over the analytic null) and the bar on
  extinction-by-k=4 sentences. Sub-localization sentences must not invite
  'the decay finishes early' readings.
- **NARROW-2** (source DEC-20260902-7ad3d9): No count-level decay sentence
  without second seeds at the named k. This batch's CC rule is the
  mechanism: pairs (1,2)/(2,4) may reach count level only if CC-AGREE
  fires; k=3 enters with two draws from the start.
- **NARROW-3** (source DEC-20260902-7ad3d9): Determinism is not
  replication: exact re-runs under identical seed/seat/build are instrument
  determinism and never count as independent draws. The determinism double
  on the extended build (S2a-6) is a certification of the new binary, not a
  replication arm.

Record-specific bars (paraphrase discipline): never 'ramp closed' or any
closure sentence beyond the scoped branch verdicts; never 'extinction by
k=4' or any extinction sentence at any k (NARROW-1); never 'count
completion' as decay-to-zero completion — the batch name means
replication-completion of the count sentence, stated wherever the name
appears; never a carrier sentence about e, never 'zeros again', never
X-lane fields reported as readings; never a count-decay sentence citing the
BATCH-7b798d readings as validated evidence; never an attribution of h(1)
or the k=0->k=1 drop to dilution per se (SCOPE-1); never 'the curve is
seed-stable' as a whole-curve sentence (replication is named per pair);
never a sub-interval localization finer than the CC3 branch states; never
present the exact-diff source change as an instrument improvement; never
present AMEND-1 as a retroactive validation of the BATCH-7b798d readings
(no post-hoc rescue; prospective only). Always carry scope: cell
(amask=1, smask=1), r=5, PIN-T0, 2^30 per arm, frozen family subset
{0,1,2,4,8,16} plus k=3 only if Stage S2 runs, seeds as run, toy tier.

---

## 14. TIMING STRIP SET (determinism comparisons)

Byte-identity comparisons of receipts (any cross-batch receipt comparison,
and the S2a-6 overflow-positive determinism double on the extended build)
strip EXACTLY the two-field set pre-registered by the predecessor lineage
(wall-clock/timestamp fields only):

- `elapsed_seconds_measured`
- `measured_rate_trials_per_sec`

and no other fields.

---

## 15. S0 GATE/ANCHOR EXPECTATIONS (this task)

- S0-2 BUILD IDENTITY RE-VERIFICATION: sha256 of the copied source and
  binary vs the BATCH-e5d753 snapshot-bound receipt hashes (source
  ec748cef..., binary 74e3d65c...) — EXPECTED PASS (zero source change in
  S0/S1). PRICED FALLBACK on ANY mismatch: full Gate-0x rebuild (aes, r5,
  amask=1, smask=1, 2^30, seed 531001, armid 1, threads 2) field-exact vs
  L1-AES-R5-P30 under the extended allowed-diff list {arm,
  elapsed_seconds_measured, hit_log_cap, measured_rate_trials_per_sec,
  oracle, probe} + additive pin-label fields {schedule_pin,
  schedule_pin_position, schedule_pin_decision}, BEFORE any reading arm.
  Which path ran is recorded in RESULTS.json.
- S0-3 KAT PINS: `pin 363851` and `pinidentity 363851` on the re-verified
  build; byte-identity EXPECTED vs the lineage KAT receipts
  (runs/S2a_pin.json sha256 9ba9a3bf... / runs/S2b_pinidentity.json sha256
  ff06c0c0... under archives/TASK-20260902-e19f39). Any failure ->
  CC-GATE-FAIL.
- S0-4 TABLE-FREEZE RE-VERIFICATION: rerun `freeze 363851`; compare against
  the committed R3_table_freeze.json
  (coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json):
  digests, bijection, nestedness, cross_k_nesting ALL identical;
  position_order and the cap-INDEPENDENT folded-smoke selfcheck counters
  additionally compared; the cap-DEPENDENT selfcheck fields
  (hit_detail_records, hit_log_overflow) differ by construction (committed
  file cap-64, this build cap-256) and are disclosed, NOT compared. Any
  mismatch on compared fields -> CC-GATE-FAIL.
- S0-5 DEAD ANCHOR (analyzed FIRST among reading-bearing arms): (aes, r6,
  amask=1, smask=1, 2^30, seed 531004, armid 1, threads 4). Gate hits <= 8
  (carried dead band at 2^30). Tripwire hits >= 9 -> CC-F6 HALT, escalate
  to claim-changing review (rule 12), no reading admitted. A 0-hit anchor
  passes with reduced assurance (direction-safe; inherited precedent,
  rule 8 recorded). Baseline ~27 min (campaign hardware ran it in ~2-3 min
  in the predecessor; real times stamped, either is fine).
- S0-6 RAMP-ZERO ANCHOR (BLOCKING): k=0 identity re-seat (S_0, r5, amask=1,
  smask=1, 2^30, seed 531001, armid 5, threads 4). Gate: hits = 2^30
  exactly, T = 0, W = 3 on 100% of nontrivial trials (whist
  [0,0,0,2^30,0]), excess ratio 1.0 exact; overflow = 2^30 − 1024
  saturated-by-construction with ALL counter identities exact — legal under
  AMEND-1 (pure cap truncation; section 1.2 proves-too-much control: if the
  gate fails this receipt, the gate itself is indicted -> CC-GATE-FAIL).
  Any count-level departure -> CC-ANCHOR-FAIL (F3) halt. This receipt is
  the AMEND-1 proves-too-much control.

S0 OUTCOME (ordered, first match wins): CC-GATE-FAIL / CC-F6 /
CC-ANCHOR-FAIL / PASS-S0. A halt is a committed instrument/anchor result,
never a shape reading (rule 5).

---

## 16. BUDGET AND SCOPE DISCIPLINE (this task)

Wall clock 5400 s TOTAL for S0 (binding stop; every arm stamped in
budget_stamps.jsonl with arm id, command, start/end epochs, wall s, rss if
available). Maximum 7 binary invocations. Memory 4 GB. Every reading arm
runs under `timeout 3600`. Budget exhaustion is resource_exhaustion, NEVER
a reading (rule 5).

Toy tier. NO deployed-AES claims. NO published-cryptanalysis comparisons in
either direction. NO k >= 1 interior readings at this stage (S1's job). No
X statistic, no rho-exclusion (section 12). No git add/commit by this
producer. No status/strength/promotion interpretation — observations only.

Binding baseline convention: ~27 min per 2^30 4-thread arm is the BUDGET
contract; measured campaign hardware rates are OPTIMISTIC-RELATIVE and
disclosed, never charged as the baseline.
