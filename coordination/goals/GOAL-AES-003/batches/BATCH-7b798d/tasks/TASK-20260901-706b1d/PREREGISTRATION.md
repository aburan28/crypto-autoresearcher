# PREREGISTRATION — TASK-20260901-706b1d (BATCH-7b798d, GOAL-AES-003) — Stage S0

Write-once. This file is committed in content before the first fresh arm of this
task (S0-2 KAT pins); its mtime must predate every fresh run receipt under
`runs/`. It carries the S0-relevant frozen commitments of
`ledger/proposals/IDEA-20260901-582ea9.yaml` (the shape-only reduced Stage-1
design) and the Coordinator pin decision `ledger/decisions/DEC-20260901-fb6f11.yaml`.
Stage S0 decides instrument validity of the PIN-T0 widened build, the dead-arm
control at matched exposure, and the ramp's zero. It does NOT decide the shape
(no interior point is run in S0). A halt here is a committed instrument/anchor
result, never a shape reading (rule 5).

Executor scope note: this task executes S0 ONLY. Interior k arms (k=1/2/8; the
k=16 re-seat) belong to Stage S1 (TASK-20260901-c2b265) and are NOT run here.

## 0. PIN-T0 schedule pin (adopted, binding for this batch)

Reference: `ledger/decisions/DEC-20260901-fb6f11.yaml` (`pin_adopted`), adopting
the `schedule_pin` block of IDEA-20260901-582ea9. Statement:

> SubWord uses TPOS[0], the table at the FIRST position of the frozen order.
> Result: identity schedule at k=0, AES schedule at every k >= 1. Rationale:
> the unique pin under which BOTH committed endpoints (k=0 identity seat, k=16
> AES seat) remain receipt-exact; interior readings proven pin-invariant across
> the two endpoint-preserving candidate pins by the proposal. Adoption scoped
> to this batch only; any other pin or schedule convention requires a new
> Coordinator decision.

Since POS_ORDER[0] == 0 and position 0 enters P_k exactly at k >= 1, PIN-T0 is
implemented by construction as: after `set_diluted_tables(k)`, the key
schedule's global SubWord table is reloaded from TPOS[0]/INV_TPOS[0]. At k=0
this reloads the identity table; at every k >= 1 the AES table. Both committed
endpoints remain receipt-exact except for the additive pin-label fields below.

## 1. Frozen per-point bands (inherited from 363851 Stage 1, rebinned for the 2^30 comparator)

- NULLBAND: h <= 5 (consistent with analytic null 1.0 at >= 99.9% per-point power conventions)
- RESIDUAL-BAND: 6 <= h <= 40 (covers the committed 14/19 AES seats and the ~13-15 random-bijection level with Poisson headroom)
- AMBIGUITY-BAND: 41 <= h <= 99
- GRADUAL-THRESHOLD: h >= 100 (~8 sd above the residual band at 2^30)
- bandrank: NULLBAND = 0, RESIDUAL = 1, AMBIGUITY = 2, THRESHOLD = 3

Band-level monotonicity sentinel (frozen): the curve over tested interior
points {1, 2, 8, 16} is BAND-RISING iff there exist tested points k_a < k_b
with bandrank(h(k_b)) > bandrank(h(k_a)). Within-band inversions do NOT fire
the sentinel.

## 2. Per-point sensitivity floors (design-time, declared BEFORE any reading)

From IDEA-20260901-582ea9 `design_time_power` (design-rate null lambda_0 = 1.0
hit per 2^30; one-sided rejection toward excess at h >= 6, size 5.94e-4):

- lambda_80 ~= 8.0 hits per 2^30 (power 0.809 at lambda = 8)
- lambda_95 ~= 10.5 hits per 2^30 (power 0.950 at lambda = 10.5)
- A point reading NULLBAND excludes a per-point hit-rate excess >= ~8-10.5 at
  80-95% power, and excludes NOTHING below that (a true lambda = 6 point reads
  NULLBAND 45% of the time).
- Within-residual-band trends (e.g. lambda = 14 vs lambda = 30) are NOT
  resolvable at 2^30 (Garwood 95% CIs [7.6, 23.5] vs [20.2, 42.8] overlap).
- NO rho-exclusion of any kind is claimed at any interior point; the measured
  t=1 frontier rho_80 = 0.1183 of EV-AES-896ef2 is consumed as the standing
  sensitivity-floor control reading of the closed lane, reported beside the
  shape verdict (in S1), never merged with it.

## 3. Seat tuples (armid reuse per IDEA-20260901-363851 / 582ea9, seed family 531001)

All arms: amask = 1, smask = 1, log2N = 30 (2^30 trials), frozen nested family
S_k over position order [0,4,8,12, 1,5,9,13, 2,6,10,14, 3,7,11,15].

| seat            | sbox token | r | seed   | armid | threads | stage |
|-----------------|------------|---|--------|-------|---------|-------|
| Gate-0x rebuild | aes        | 5 | 531001 | 1     | 2       | S0-4  |
| dead anchor     | aes        | 6 | 531004 | 1     | 4       | S0-5  |
| k=0 re-seat     | identity   | 5 | 531001 | 5     | 4       | S0-6  |
| k=16 re-seat    | aes        | 5 | 531001 | 8     | 4       | S1 (not this task) |
| k=1             | s1         | 5 | 531001 | 2     | 4       | S1 (not this task) |
| k=2             | s2         | 5 | 531001 | 3     | 4       | S1 (not this task) |
| k=8             | s8         | 5 | 531001 | 6     | 4       | S1 (not this task) |

Interior sbox tokens s1/s2/s4/s8/s12 map to k in {1,2,4,8,12} under PIN-T0.
The k=0 re-seat uses the armid 5 that 363851 pre-specified for that seat, so
the reading sits on the exact stream the frozen design would have used.

## 4. Anchor-first ordering (BINDING for S0)

1. S0-2 KAT pins (pin, pinidentity) — BLOCKING; any failure = SH-GATE-FAIL.
2. S0-3 table-freeze re-verification — BLOCKING; any mismatch = SH-GATE-FAIL.
3. S0-4 Gate-0x rebuild — BLOCKING; any non-allowed field difference = SH-GATE-FAIL.
4. S0-5 DEAD ANCHOR (aes, r6, seed 531004, armid 1, 4 threads) — run and
   ANALYZED FIRST among reading-bearing arms, before any alive reading.
5. S0-6 RAMP-ZERO ANCHOR (k=0 identity re-seat, seed 531001, armid 5, 4
   threads) — BLOCKING ramp anchor, before any interior point (S1).

## 5. Ordered SH cascade WITH precedence clause (copied from IDEA-20260901-582ea9)

Committed before any arm. ORDERING (BINDING): S0-5 dead anchor is run and
ANALYZED BEFORE any alive reading; S0-6 ramp-zero anchor before any interior
point; within S1, the k=16 re-seat is ANALYZED FIRST, then k=1, k=2, k=8; the
shape verdict is composed only after all interior points are read, under the
cascade below. BRANCH CASCADE — exhaustive, evaluated in this FIXED ORDER,
which IS the branch-precedence clause:

1. SH-GATE-FAIL: any integrity gate fails (S0-2 KAT, S0-3 freeze
   re-verification, S0-4 Gate-0x identity, S1-5 determinism, S1-6
   digest/source-diff, or hit_overflow > 0 on any analysis-bearing receipt) ->
   invalid_measurement; HALT; repair (rule 5); never evidence about shape.
   (S0-executor note on the k=0 anchor: at k=0 every nontrivial trial hits, so
   the capped per-hit DETAIL LOG necessarily overflows (2^30 hits vs
   threads x 256 slots); the campaign's own frozen selfcheck_identity_k0
   assertion pattern expects overflow = nontrivial - threads*min(per_thread,
   256). The COUNT observable (W_ge1_nontrivial, whist) is cap-independent.
   The S0-6 anchor gate is evaluated on its named conjuncts — hits, W=3 on
   100% of nontrivial trials, excess ratio — and the anchor's
   hit_log_overflow value is recorded exactly and flagged for the validator
   rather than silently absorbed (rule 8). This note concerns the anchor's
   detail log only; for every arm where hits are expected sparse
   (S0-4, S0-5, and all S1 arms) hit_overflow > 0 remains SH-GATE-FAIL.)
2. SH-F6: dead anchor reads hits >= 9 (scaled tripwire at the frozen 2^30 dead
   band 8) -> boundary falsifier of the sealed verdict; HALT in-batch flow;
   escalate to claim-changing review (rule 12); no interior reading admitted.
3. SH-ANCHOR-FAIL: k=0 re-seat fails (hits != 2^30, or any nontrivial trial
   with W != 3, or excess ratio != 1.0) -> F3 ramp-anchor indictment; HALT; no
   interior reading admitted; never evidence about shape (rule 5).
4. SH-RESEAT-FAIL: k=16 re-seat reads outside [6, 30] -> F5 indictment of THIS
   record's widened table path (the committed measurements stand); HALT;
   interior readings are recorded but no shape verdict is composed; repair.
   (S1 branch; recorded here for cascade completeness.)
5. SH-DEAD: h(1) <= 5 AND h(2) <= 5 AND h(8) <= 5 -> no hit-count excess at
   any powered interior point; recorded with the per-point floors and the
   named successor (finer dose resolution near k=16: k=12 first).
6. SH-OTHER-NONMONO: not SH-DEAD, and the band sequence over {1, 2, 8, 16} is
   BAND-RISING (some k_a < k_b with bandrank(h(k_b)) > bandrank(h(k_a))) ->
   non-monotone curve; recorded as measured with the rise located; named
   successor (k=4 to interpolate the rise, or instrument review if the rise is
   k=8 NULL -> k=16 RESIDUAL).
7. SH-STEP (= SHAPE-FLAT): band sequence non-rising AND h(1) <= 40 AND h(2) <=
   40 -> the count excess persists UNDECAYED at residual level through every
   tested interior dose; global class fragility within the frozen family.
8. SH-GRADUAL (= SHAPE-DECAY): band sequence non-rising AND h(1) >= 100 -> the
   shortfall from the affine limit decays jointly with dilution toward k=0;
   tunable-dose reading; recorded with the located transition and the named
   refinement successors k=4/k=12.
9. SH-OTHER-RESIDUAL: DECLARED COMPLEMENT — any outcome matching none of the
   above (in particular h(1) in the AMBIGUITY band 41-99); recorded as
   measured, never force-binned; named successors preregistered: k=1
   second-seed arm at 2^30 and/or one 2^32 k=1 arm. Budget halts are
   resource_exhaustion, NEVER readings (rule 5).

### Branch precedence clause (restated standalone, per the f8294e precedent)

This record's decision rule is an EXHAUSTIVE ORDERED CASCADE (SH-GATE-FAIL >
SH-F6 > SH-ANCHOR-FAIL > SH-RESEAT-FAIL > SH-DEAD > SH-OTHER-NONMONO > SH-STEP
> SH-GRADUAL > SH-OTHER-RESIDUAL) committed in S0-1 before any arm runs. By
construction no two branches can literally match the same outcome: branches
5-8 are mutually disjoint on their conjuncts (SH-DEAD requires all interior
h <= 5; SH-OTHER-NONMONO requires a band rise and precedes the
monotone-conditional branches; SH-STEP requires h(1) <= 40 while SH-GRADUAL
requires h(1) >= 100), and SH-OTHER-RESIDUAL is the declared complement. THIS
REPAIRS A VERIFIED DEFECT IN THE FROZEN 363851 WORDING: under 'STEP = k=1 and
k=2 both <= 40; OTHER = everything else (thresholds, non-monotone,
intermediate)', the curve h = {15, 14, 2, 16} over {1, 2, 8, 16} literally
matches BOTH STEP (first two conjuncts) and OTHER (non-monotone), the exact
RX-WEAK-b2/RX-DEAD overlap pattern of 026d6a (EV-AES-241790 OBS-5ED-6). Repair
adopted from the red team's RT-B wording: (a) the cascade is exhaustive and
ordered, so no overlap can recur; (b) the dead/anchor/gate branches precede
all shape branches (dead-arm-first discipline); (c) SH-DEAD precedes
SH-OTHER-NONMONO because its defining conjunct (no excess at ANY powered
interior point) is strictly more specific than generic non-monotony — whenever
a more-specific-branch and a more-general-branch description both fit, the more
specific governs the verdict and the more general branch's named successor
SURVIVES as the revisit condition, never silently preempted; (d) the
sentinel's band-level resolution is the declared granularity of the
monotonicity conjuncts, so within-band inversions can never resurrect an
overlap argument.

## 6. Gate-0x allowed-diff list (extended for the PIN-T0 widening)

S0-4 runs (aes, r5, amask=1, smask=1, 2^30, seed 531001, armid 1, threads 2)
under the widened build and must reproduce the certified Gate-0x receipt of
BATCH-ace664 (runs/P2_gate0x.json of TASK-20260901-579808 — itself the
field-exact cap-256 rebuild of the committed immutable L1-AES-R5-P30 receipt,
BATCH-015 TASK-20260805-d408ac) field-by-field, under this extended
allowed-diff list.

Value-difference allowed list (fields that MAY differ in value):
`{arm, probe, oracle, elapsed_seconds_measured, measured_rate_trials_per_sec, hit_log_cap}`
— inherited from the BATCH-ace664 Gate-0x convention (arm label is this task's
own; timing fields are wall-clock; hit_log_cap is 256 on both sides and is
carried for convention continuity).

Additive allowed list (fields this build ADDS, absent from the reference;
pin label + interior-surface declaration ONLY):
`{schedule_pin, schedule_pin_position, schedule_pin_decision}`
with the pinned values `"PIN-T0"`, `0`, `"DEC-20260901-fb6f11"`.

Every other field — including all trial-stream, counter, digest, hit-index,
hit-detail, ez-counter, table, and key fields — MUST be identical. Any missing
committed field, any non-allowed value difference, or any unexpected added
field -> SH-GATE-FAIL; halt. The Gate-0x rebuild is simultaneously the
stream-identity check, the widening-perturbation check, and the continuity
check that the committed 14-hit reading is unchanged under the widened build
(PIN-T0 keeps the k=16 schedule exactly AES, so field-exact reproduction is
the preregistered expectation).

Source-diff audit scope (S0, recorded in runs/source_diff_raw.txt): the diff
of this task's src/affarm046ex.c against the BATCH-ace664 lineage copy must
consist ONLY of (i) the pinned interior-surface widening (interior k token
admission + PIN-T0 TPOS[0] schedule reload), (ii) the additive pin-label
receipt fields, and (iii) header/comment annotation of exactly those changes.
No change to the RNG, trial loop, round functions, existing counters, or any
existing receipt field emission.

## 7. S0 gate/anchor decision rules

- S0-2 KAT: both `pin` and `pinidentity` must report pin_pass true (exit 0).
- S0-3 freeze: rerun of freeze mode at the committed freeze seed 363851;
  digests, bijection flags, nestedness flags, AND cross_k_nesting must be ALL
  identical to the committed R3_table_freeze.json
  (BATCH-2f12ac TASK-20260901-7e0b71 runs/R3_table_freeze.json). Any mismatch
  -> SH-GATE-FAIL.
- S0-4 Gate-0x: per section 6. Any non-allowed difference -> SH-GATE-FAIL.
- S0-5 dead anchor: gate hits <= 8 (carried dead band at 2^30; committed r=6
  arms read 2-4). Tripwire hits >= 9 -> SH-F6: HALT, record, escalate (rule
  12), NO interior surface admitted in this batch. A reading of 0 hits passes
  the gate but is recorded per rule 8 as below-expectation with reduced
  anchor assurance (direction-safe; the EV-AES-896ef2 n=4 anchor precedent,
  requantified at this arm's realized count).
- S0-6 ramp-zero anchor: BLOCKING. hits = 2^30 exactly, T = 0, W = 3 on 100%
  of nontrivial trials, whist [0,0,0,2^30,0], excess ratio 1.0 exact against
  the frozen excess_E = 2^30 comparator convention. Any departure is F3 /
  SH-ANCHOR-FAIL: the ramp's zero is void, every interior reading confounded,
  invalid_measurement, halt and repair before any reading. Under PIN-T0 the
  receipt's schedule fields additionally match the committed affine anchor
  (identity schedule at k=0).

S0 outcome is exactly one of: SH-GATE-FAIL / SH-F6 / SH-ANCHOR-FAIL / PASS-S0,
under the cascade order above.

## 8. No-reopen clause (binding)

NO X statistic is tested, computed for decision, or reported as a reading at
any point in this batch; no rho-exclusion is claimed anywhere. Every e field
the certified instrument already logs (ewhist_*, per-hit detail with
zero_mask_e, the X-statistic inputs) rides as report-only enabling data. The
t=1 X lane is closed by EV-AES-896ef2 and stays closed; any downstream
paraphrase reporting these fields as a carrier reading violates this record's
scope (never 'zeros again', never a carrier sentence).

## 9. Budget and run discipline

Declared wall clock 9000 s TOTAL for this task; maximum 8 binary invocations;
memory 4 GB. Every arm start/end is stamped in budget_stamps.jsonl with wall
seconds and RSS where obtainable. Each arm runs under a shell timeout
(`timeout 3600`). Budget exhaustion is reported as resource_exhaustion, NEVER
as a reading (rule 5). Timeouts/crashes are infrastructure, not evidence
(rule 5). Toy tier; no deployed-AES claims; no published-cryptanalysis
comparisons in either direction (RQ-AES-003 R3).

## 10. Inference manifest

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: session backend unknown (no adapter probe run in this
session); fallback_used: true (session-backend transport under inference
amendment DEC-20260831-0d1eeb); model_verified: false;
degraded_requirements: []; amendment: DEC-20260831-0d1eeb;
independent_session: true.
