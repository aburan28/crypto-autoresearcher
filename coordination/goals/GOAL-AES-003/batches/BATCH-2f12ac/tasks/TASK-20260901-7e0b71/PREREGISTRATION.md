# PREREGISTRATION — TASK-20260901-7e0b71 (BATCH-2f12ac, GOAL-AES-003)

Write-once preregistration file per IDEA-20260901-363851 `integrity_gates.digest_commit_discipline`
(V-804-2; BATCH-fe0bdc precedent). This file's mtime MUST predate every run output in `runs/`
(verified at completion). All tables, position sets, test definitions, thresholds, allowed-diff
lists, and seat tuples below are committed BEFORE the first arm; any post-data change is VOID.

Frozen spec: `ledger/proposals/IDEA-20260901-363851.yaml` (read whole this session).
STAGE 0 ONLY is executed. The frozen dilution family is CLOSED: pinned row-major position order
and point set k in {0,1,2,4,8,12,16} exactly as recorded; any change after seeing data is void.

Environment (recorded at session start):
- Host Adams-MacBook-Pro.local, arm64, Darwin 25.6.0, macOS 26.6, 14 CPUs, 48 GiB RAM.
- Python 3.12.8 (stdlib only). C: Apple clang 17.0.0.
- Git: worktree `.worktrees/aes003-batch015-20260831`, branch `aes003-batch2f12ac-20260901`,
  HEAD `17fa491fb231eb1dfb702c5b2c255ea0a7c6ac22`; dirty-tree state at start = only this task's
  (then-empty) write_scope directory.

Budget: declared wall clock 7200 s; start 2026-09-01T20:11:01Z; binding stop 2026-09-01T22:11:01Z
(`budget_stamps.jsonl`). Halt at the stop is FULL COMPLIANCE (rule 5); dropped work is SCOPE,
never an answer (rule 8). MAXIMUM 8 RUNS; the run list below is 7 record runs (R6 = two
invocations), i.e. 8 binary invocations total — at the cap, no spare invocation exists, which is
why the instrument smoke check is folded into R3 (disclosed below), not run separately.

---

## 1. STAGE-0 GATES (verbatim from IDEA-20260901-363851 `integrity_gates`)

### gate_0_anchor_reproduction
BLOCKING, before any ramp arm: the instrumented worker (affarm046.c derivative, logging
ENABLED) runs the committed anchor seat - (sbox=aes, rounds=5, amask=1, smask=1, log2N=30,
seed=531001, armid=1, threads=2) - and must reproduce the committed immutable receipt
L1-AES-R5-P30 FIELD-BY-FIELD: all 14 hit indices identical as (thread, in-thread index)
pairs, whist, W_ge1_nontrivial, W_ge1_by_word, trivial_swaps_excluded, nontrivial_trials,
thread_seeds, plaintext_stream_digest, sbox_first8, and every remaining field of the
receipt, with the preregistered allowed-diff list EXACTLY {arm label, probe label, oracle
label, elapsed_seconds_measured, measured_rate_trials_per_sec} plus fields the derivative
ADDS (zhist, sbox_table_hex, all e fields). Missing fields fail the gate; the derivative
must emit the full committed field set with identical semantics (including the receipt's
hit_trials_logged = thread-0 hit count quirk, read from the receipt this session).
This single run is simultaneously Gate 0, the perturbation check, and the J5 carrier measurement
at seed 531001: receipt identity on the trial-map fields proves the logging changed nothing
observable, because any perturbation of stream, key, round function, or counters would move
at least one of the 14 indices or one histogram count. Precedents: TASK-20260901-e2e66e C4
(ENABLED build reproduces L1-AES-R5-P30, 14 hits, identical indices, toggle diff exactly one
#define line) and TASK-20260901-92672b (field-by-field reproduction with a preregistered
three-field allowed-diff list).

### kat_pins
Before any arm: pin mode (FIPS-197 C.1 KAT enc+dec at r=10, BATCH-003 r=5/r=10 anchor
ciphertexts, 512-vector r=1..10 roundtrips under the AES table) and pinidentity mode
(identity table bijection + 512 roundtrips) must pass on the derivative; catches
self-consistent-but-unpinned convention drift, exactly as in the affarm046.c lineage.

### source_diff_audit
Recorded diff of the derivative against affarm046.c with an annotation table: the round
functions, geometry, RNG, trial loop, and counter updates must be UNCHANGED; the diff must
consist only of (i) the widened table surface, (ii) the e-logging block (pure reads after
all trial decisions into new counters only), (iii) the widened receipt emission. Any diff
line touching the trial stream or existing counters voids the gate (F4).

### determinism
Byte-identical double-run of the derivative at log2N=20, threads=4, seed=531001 (two
invocations, identical command line): ALL fields identical including every e histogram and
per-hit record, timing fields excepted. Full-exposure determinism at the anchor seat is
additionally implied by Gate-0 receipt identity.

### digest_commit_discipline
All tables, position sets, test definitions, thresholds, allowed-diff lists, and seat
tuples committed as a write-once preregistration file (mtime BEFORE the first arm); the
table-freeze digests re-verified post-arm; deviations go in procedure_deviations, never
absorbed (V-804-2; BATCH-fe0bdc precedent).

---

## 2. PREDICTIONS UNDER BOTH HYPOTHESES (verbatim from `carrier_statistic`)

### predicted_distribution_H_carrier
(a) t=1 AES seat: the miss-trial wt(e) distribution is spread over moderate-to-large weights
(the identity law fails in the mass); the ~14 hit weights sit in the low tail of F_miss;
p_small <= 0.05 at seed 531001, direction reproduces at 531002. (b) Along the ramp: the
all-trial mean wt(e) falls monotonically with k toward 0; at every testable interior point
the hit weights concentrate in the low tail of that point's F_miss (Holm-adjusted p_small
<= 0.05 at >= half the testable points); at k=0, wt(e) = 0 on ALL trials (delta at 0) and
every trial hits - the limit is consistent with the coupling by construction.

### predicted_distribution_H_null
Hit weights are iid draws from F_miss at every point: p_small > 0.05 at both seeds at t=1;
no Holm-adjusted rejections at interior points; hit-vs-miss mean separation ~ 0 everywhere.
The excess may still decay with k (the ramp shape is measured independently); the carrier
clause is then dead within the tested scope (this statistic, this family, this exposure),
and the residual rides on something e does not measure.

(Stage 0 tests part (a) only, at seed 531001; second-seed replication is Stage 1a, not run here.)

---

## 3. r=6 KNOWN-DEAD REFERENCE BAND AND TRIPWIRE (verbatim from PR-2 / F6)

PR-2 minimum_effect: hits <= 8 (carried dead band; committed comparator: AES dead at r=6,
pooled 1.72x bound; expectation ~1-2 hits at 2^30). The MISS wt(e) distribution at the death
round is logged as the no-excess reference (report-only observation: how e's mass moves between
r=5 and r=6). Tripwire: hits >= 9 is a boundary falsifier of the sealed verdict (F6) - halt
and escalate.

F6 (ESCALATION TRIPWIRE, not a defect). The r=6 known-dead reference reads >= 9 hits: a
boundary falsifier of the sealed verdict (future committed r=6 excess). Halt the ramp;
record; escalate to a claim-changing review (review-breakthrough at max per rule 12 - a
contradiction of established evidence). The ramp's own claims are suspended pending review.

---

## 4. STAGE-0 DECISION RULE (verbatim from `preregistered_decision_rule`, STAGE 0 part)

Committed before any ramp arm. STAGE 0: (S0-CARRIER-ALIVE) Gate 0 passes AND p_small <= 0.05
at seed 531001 -> Stage 1 dispatched; carrier reading alive at t=1. (S0-WEAK) Gate 0 passes,
p_small > 0.05 but all/most hit weights descriptively below the miss median (or marginal
0.05 < p_small <= 0.15) -> carrier reading weakened, not falsified; Stage 1 dispatched with
the disclosure (interior points carry more power if hit counts rise). (S0-DEAD) Gate 0 passes
and p_small > 0.15 with hit weights descriptively at or above the miss median, or p_large
<= 0.05 -> carrier clause FALSIFIED at t=1 (F1); record the finding; the ramp-shape question
survives only if the Coordinator re-ranks a reduced Stage 1 (design change, new decision) -
the default is return to idea generation with e named non-carrier. (S0-GATE-FAIL) any gate
failure -> invalid_measurement, halt, repair (rule 5); no reading.

Operational reading committed for the gray phrases (disclosed, applied mechanically):
- "all/most hit weights descriptively below the miss median" := a strict majority (> 50%) of
  the n hit weights strictly below the miss median.
- "hit weights descriptively at or above the miss median" := the majority (>= 50%) of hit
  weights >= the miss median.
- miss median := the smallest byte weight w with cumulative miss-count >= ceil(N_miss/2)
  (lower median of the exact 17-bin distribution).
Evaluation order (preregistered): if Gate 0 fails -> S0-GATE-FAIL; else if p_large <= 0.05
-> S0-DEAD; else if p_small <= 0.05 -> S0-CARRIER-ALIVE; else if (0.05 < p_small <= 0.15) or
(majority of hit weights < miss median) -> S0-WEAK; else -> S0-DEAD.
(SHAPE-ONLY is a STAGE 1 arm of the decision rule and cannot fire in Stage 0; it is reported
as not-reachable-here in RESULTS.json.)

---

## 5. CARRIER TEST DEFINITION (verbatim from `carrier_statistic.test_statistic`)

EXACT ONE-SIDED EXCHANGEABILITY TEST, preregistered before any arm. Let n = number of hit
trials, w_1..w_n their byte weights, T_obs = sum(w_i). Let F_miss be the run's own empirical
byte-weight distribution over MISS trials (exact 17-bin counts; hits excluded from the
reference by construction). NULL H0: conditional on the hit count, hit labels are
independent of wt(e), so w_i are iid draws from F_miss. CARRIER DIRECTION (preregistered,
one-sided): small-e concentration. p_small = P_{F_miss}(sum of n iid draws <= T_obs),
computed by exact dynamic-programming convolution of the 17-bin distribution for n <= 2000.
For n > 2000 (possible at GRADUAL interior points): deterministic subsample = the first 2^20
miss trials in stream order (pinned, not data-dependent); two-sample Wilcoxon rank-sum with
tie correction (normal approximation) as the decision statistic plus a mean-difference
z-test, both reported, Wilcoxon deciding. p_large (>= direction) is computed and reported at
every point; a significant p_large is the anti-carrier (large-e concentration) signal.
Decision at a single point: carrier-alive iff p_small <= 0.05.

Stage-0 assignment: the record's decision rule consumes p_small at seed 531001 in Stage 0
(`stage_0.decides`: "the carrier question at t=1 on the anchor seed ... discharged as a
measurement"), so the executor COMPUTES the exact DP test in `decision_analysis.py` (exact
integer arithmetic; n = 14 expected <= 2000) and emits its full inputs (F_miss 17-bin counts,
hit weights, T_obs, n) for the validator's fresh-code re-derivation. The Wilcoxon branch is
not reachable at n = 14 and is not implemented in this stage.

---

## 6. FROZEN DILUTION FAMILY (verbatim pin content, from `dilution_family`)

- Parameter: k = number of byte positions carrying the AES S-box; remaining 16-k positions
  carry the identity table. t = k/16. S_k(position j) = AES table if j in P_k, else identity,
  for j = 0..15 (state byte index byte[4*col+row], campaign column-major convention).
- Position order (FROZEN, nested, word-stratified, no data-dependent choices): the pinned
  total order of the 16 byte positions is the row-major sweep
  [0,4,8,12, 1,5,9,13, 2,6,10,14, 3,7,11,15]; P_k = the first k positions of this order.
  Nesting: P_1 < P_2 < P_4 < P_8 < P_12 < P_16.
- Points: k in {0, 1, 2, 4, 8, 12, 16} exactly.
- Table construction: each S_k built from the pinned AES table (build_sbox(), KAT-pinned)
  and the identity; the table-freeze run emits, for every k, the 16 per-position table
  digests (sha256 of each 256-byte table), the bijection check, and the nestedness check
  (S_k[j] == AES[j] for j in P_k and S_k[j] == j elsewhere, all 16 positions, all 7 points).
  The digest file is write-once committed BEFORE the first arm and re-verified post-arm.
  Tables are deterministic functions of k - no seeds, no draws, no data-dependent choices.

CONSTRUCTION PIN (build-level, disclosed, frozen with this file): the position-dependent
SubBytes applies the per-position table at the PRE-ShiftRows (source) state position in the
forward direction and at the post-InvShiftRows (destination) position in the inverse
direction, i.e. forward `t[4*c+r] = T[4*((c+r)&3)+r][ s[4*((c+r)&3)+r] ]`, inverse
`t[4*c+r] = INV_T[4*c+r][ s[4*((c-r+4)&3)+r] ]`. This is the reading under which the byte is
substituted at the state position it occupies at the moment of substitution (SubBytes
precedes ShiftRows in the pinned round order; InvShiftRows precedes InvSubBytes in the pinned
inverse order), and it is the reading consistent with the record's stratification rationale
(the active difference diagonal PW[0] = {0,5,10,15} "receives its first AES byte at k=1
(byte 0)" — the difference lives at those positions before round-1 substitution). At k=0
and k=16 both endpoints reduce EXACTLY to the committed affarm046/campaign sub_shift and
inv_sub_shift expressions, so both committed endpoint receipts are unaffected by this pin;
Stage 0 runs no interior arm, so no Stage-0 reading depends on the pin beyond the endpoints.

KEY-SCHEDULE CONVENTION (verbatim from `assumptions`): Key schedule co-varies with the S-box
table (SubWord uses the current global SBOX - pinned convention in the affarm046.c header and
the campaign build): every ramp point has its own schedule. Implementation consequence for
THIS Stage-0 build: the arm surface accepts sbox tokens `aes` (k=16; global SBOX = AES, AES
schedule) and `identity` (k=0; global SBOX = identity, identity schedule) — the two Stage-0
arm seats — plus a `tablecheck` path for interior k used ONLY by the freeze mode. ARM RUNS at
interior k in {1,2,4,8,12} are REFUSED by this build with an explicit error: the co-variation
convention names a single "current global SBOX" for SubWord, which is undefined for a
position-dependent table until the Coordinator pins which table SubWord uses at interior
points (Stage-1 question, named in BUILD.md). This refusal is a scope disclosure, not a
family change: the frozen family, its points, order, and tables are fully frozen and digested
here; only the interior ARM surface awaits the Stage-1 pin.

---

## 7. SEAT TUPLES AND ALLOWED-DIFF LIST (committed before any arm)

- R4 GATE-0 / J5-1 (BLOCKING): (sbox=aes, rounds=5, amask=1, smask=1, log2N=30, seed=531001,
  armid=1, threads=2). Must reproduce L1-AES-R5-P30 field-by-field.
- R5 known-dead reference: (sbox=aes, rounds=6, amask=1, smask=1, log2N=30, seed=531001,
  armid=1, threads=4). Dead band <= 8 hits; tripwire >= 9.
- R6 determinism double: (sbox=aes, rounds=5, amask=1, smask=1, log2N=20, seed=531001,
  armid=1, threads=4), two invocations of the IDENTICAL command line — including the arm
  name label `DET-AES-R5-P20`, per the record's "identical command line" — with stdout
  captured to two different files. Comparison strips exactly the two timing fields
  {elapsed_seconds_measured, measured_rate_trials_per_sec} per the record's "timing fields
  excepted"; everything else byte-identical including every e histogram and per-hit record.
- Gate-0 allowed-diff list, EXACTLY: {arm label, probe label, oracle label,
  elapsed_seconds_measured, measured_rate_trials_per_sec} plus fields the derivative ADDS
  (zhist, sbox_table_hex, all e fields, key_hex, and the hit/e detail fields listed below).
  Missing committed fields fail the gate.

Added receipt fields (derivative additions, preregistered set):
- zhist[17] (lineage field absent from L1-AES-R5-P30), sbox_table_hex, key_hex;
- ewhist_all[17], ewhist_miss[17], ewhist_hit[17] (byte-weight histograms over
  nontrivial / miss / hit trials; trivial-swap trials excluded from all e statistics,
  matching the whist convention);
- ewbithist_all[129], ewbithist_miss[129], ewbithist_hit[129] (secondary bit-weight);
- hit_e_detail: per-hit records capped at 64 (HIT_LOG_CAP convention), each
  {thread, in-thread index, W, Z, vanishing word mask over PW[0..3], wt(e) byte, wt(e) bit};
- hit_trials / hit_trials_logged (thread-0 hit count, receipt quirk) / hit_log_overflow /
  hit_log_cap (committed-semantics fields, required for Gate-0 field-by-field match);
- key_stream_seeds, stream_gap_min_log2_plaintext_threads, stream_gap_min_log2_key_threads,
  key_stream_seed_equals_any_plaintext_stream_seed, null_expectation_analytic,
  plaintext_stream_digest (committed-semantics fields, required for Gate-0 match);
- e definition: e_i = (q0[i]^q1[i]) ^ (p0[i]^p1[i]), i = 0..15, computed per trial AFTER the
  swap leg and both decryptions, from buffers already live in the worker; a pure read that
  feeds no trial decision, no RNG state, and no existing counter.

---

## 8. BUILD / RUN PLAN

Build: `src/affarm046e.c` — derivative of BATCH-fe0bdc `src/affarm046.c` (the pinned
lineage), compiled `cc -O2 -pthread -o src/affarm046e src/affarm046e.c`. The diff vs
affarm046.c must consist ONLY of (i) widened table surface, (ii) e-logging block (pure reads
into new counters), (iii) widened receipt emission, plus the committed-semantics reporting
fields of §7 (plaintext digest, hit log, key-stream-seed/gap reporting) which are themselves
pure reads/new counters; recorded in `runs/source_diff.txt` with annotation table in
`src/INDEPENDENCE_AUDIT.md`. Round functions, geometry, RNG, trial loop, and existing counter
updates UNCHANGED (Gate 0 is the empirical proof: any perturbation moves one of the 14 hit
indices or a histogram count).

Runs (in order; each stamped in budget_stamps.jsonl; invocation count total = 8 = cap):

- R1 `src/affarm046e pin 363851` -> runs/R1_pin.json (+.timing.txt/.err). KAT pins under the
  AES table. Pin seed 363851 (from the idea-record id; committed here). BLOCKING.
- R2 `src/affarm046e pinidentity 363851` -> runs/R2_pinidentity.json. Identity-table
  bijection + 512 roundtrips. BLOCKING. (This is the Stage-0 identity/k=0 seat named in the
  dispatch handoff: the identity table is exercised at the k=0 limit by pinidentity; the full
  k=0 arm re-seat is Stage 1a R5, not run here.)
- R3 `src/affarm046e freeze 363851` -> runs/R3_table_freeze.json — table freeze for the FULL
  pinned family (all k in {0,1,2,4,8,12,16}): per-position table hex + sha256 digests (computed
  by src/freeze_digest.py from the C output and written into the final JSON), bijection check,
  nestedness check, cross-k nesting. FOLDED INSTRUMENT SMOKE (preregistered, same invocation):
  the freeze run internally executes two mini self-checks at log2N=10, seed 363851, armid 1,
  threads 2, amask=1, smask=1, r=5 — (a) identity k=0: asserts whist concentrated at W=3 on
  nontrivial, wt(e)=0 on ALL nontrivial trials, hit count = nontrivial count; (b) aes k=16:
  runs the worker, asserts internal consistency (histogram sums, hit count = whist[1..4] sum,
  per-hit detail conservation: detail_records + overflow = hits, detail_records <= threads*64
  under the committed PER-THREAD cap of 64). This fold keeps the invocation count within the
  8-run cap; it is an instrument self-test, NOT a Stage-0 measurement arm, and its assertions
  are committed here before any run. (Cap convention: the 64-record hit cap is PER THREAD,
  as in rc8probe_freshfeistel.c HIT_LOG_CAP and the L1-AES-R5-P30 receipt; the first written
  version of the assertion script misread it as a global cap and was corrected before any
  freeze artifact was accepted — recorded as a procedural deviation in RESULTS.json.)
- R4 GATE-0 / J5-1 (BLOCKING): `/usr/bin/time -l src/affarm046e arm GATE0-J5-1-AES-R5-P30 5 1
  1 30 531001 1 2 aes` -> runs/R4_gate0_j5.json (+.timing.txt/.err). Then
  `python3 src/gate0_cmp.py runs/R4_gate0_j5.json runs/R4_gate0_cmp.json` — field-by-field
  comparison against the committed L1-AES-R5-P30 receipt. ANY field outside the allowed-diff
  list differing, ANY missing committed field, or ANY of the 14 hit indices disagreeing ->
  HALT as F4/invalid_measurement (rule 5): no further arms, honest report.
- R5 known-dead reference: `/usr/bin/time -l src/affarm046e arm R6DEAD-REF-AES-R6-P30 6 1 1
  30 531001 1 4 aes` -> runs/R5_r6_reference.json. Band <= 8 hits; >= 9 hits -> HALT and
  report for escalation per F6 (do not continue to remaining runs beyond writing the halt
  report).
- R6 determinism double: identical command line twice at log2N=20 threads=4 seed=531001 ->
  runs/R6_det_a.json, runs/R6_det_b.json; `python3 src/det_cmp.py` strips the two timing
  fields and requires byte-identical remainder -> runs/R6_det_cmp.json.
- R7 post-arm digest re-verification: `src/affarm046e freeze 363851` again, digests
  recomputed and compared against the committed R3 freeze JSON ->
  runs/R7_digest_reverify.json (all digests/checks identical, or the instrument is void).

Analysis (not counted as runs; pure post-processing of recorded outputs):
- `python3 src/decision_analysis.py runs/decision_analysis.json` — Gate-0 result, carrier
  statistic (hit/miss histograms, exact DP p_small/p_large with full inputs), r=6 band/
  tripwire evaluation, Stage-0 decision-rule arm per §4, r5-vs-r6 miss-wt(e) report-only
  observation.

Timing capture convention (lineage): `/usr/bin/time -l <cmd> > runs/X.json 2> runs/X.timing.txt`;
program stderr merges into the timing file on any failure (a failed run's JSON will not parse,
which is itself the failure signal); `runs/X.err` is created empty per arm to record the
"no program stderr" convention explicitly.

Every structured artifact: parse-checked whole with python3 json before task completion
(stated inside each artifact); inference block on every structured artifact (policy,
requested_policy, resolved model, fallback_used true under DEC-20260831-0d1eeb,
model_verified false, standing basis 0137a051eb5828789eb267fa83c8278086578d4c).

HALT POLICY: budget stop, Gate-0 failure (F4), KAT-pin failure, determinism failure, digest
mismatch, or F6 tripwire -> stop, write the honest halt report into RESULTS.json, and report.
Halting is full compliance (rule 5). No ramp points are in this batch; no status/strength/
promotion interpretation anywhere.

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL model serving
this session under inference amendment DEC-20260831-0d1eeb; no adapter probe executed in this
session); fallback_used: true (session-backend transport under the amendment);
model_verified: false; degraded_requirements: []; amendment: DEC-20260831-0d1eeb;
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c.
