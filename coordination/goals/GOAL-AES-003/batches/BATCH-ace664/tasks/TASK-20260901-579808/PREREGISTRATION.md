# PREREGISTRATION — TASK-20260901-579808 (BATCH-ace664, GOAL-AES-003)

Write-once preregistration (integrity_gates.digest_commit_discipline, V-804-2,
BATCH-fe0bdc precedent). This file's mtime is BEFORE the first fresh arm of
Stage P. Frozen contract: `ledger/proposals/IDEA-20260901-f8294e.yaml`
(Stage P only; Stage 1/1a/1b of the 363851 ramp stay gated and are NOT spent).

- task_id: TASK-20260901-579808; batch: BATCH-ace664; idea: IDEA-20260901-f8294e
- role: executor (observations only; no status/strength/promotion interpretation)
- claim_tier: toy; no full-round/deployed-AES statements; no published-cryptanalysis
  comparisons in either direction (RQ-AES-003 R3).
- consumed lineage: BATCH-5ed9a3 TASK-20260901-ed281d instrument package
  (src/affarm046ex.c, gate conventions, anchor-first order), EV-AES-241790
  (2^30 readings and power limits), committed G5 receipt (joint-LR control),
  committed G3 receipt + L1-AES-R5-P30 (Gate-0 targets), committed
  R3_table_freeze.json (digest re-verification target).

## Inference block (all artifacts of this task)

- policy: executor-implementation; requested_policy: executor-implementation
- resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL
  session model; no adapter probe executed in this session; model_verified: false)
- fallback_used: true — session-backend transport under inference amendment
  DEC-20260831-0d1eeb (standing_basis
  0137a051eb5828789eb267fa83c8278086578d4c); degraded_requirements: []
- independent_session_required: true (per handoff)

## 1. Statistic (inherited VERBATIM from IDEA-20260901-026d6a.repaired_statistic; no statistic change in f8294e)

Per hit h with e_i = (q0[i]^q1[i]) ^ (p0[i]^p1[i]) as in the frozen instrument:

- Ze(h) = #{i : e_i = 0} = 16 - wt_e_byte(h). (The logged Z field counts zeros of
  q0^q1 and is NEVER used in the statistic.)
- m(h) = vanishing_word_mask, bit j set iff (q0^q1) vanishes on PW word j;
  PW word 0 = {0,5,10,15} (diagonal/active word).
- F(h) = 4 * popcount(m(h) & 0b1110) — forced zero bytes by the envelope theorem.
- X(h) = Ze(h) - F(h) >= 0 (extra zeros beyond the forced envelope).
- Primary scalar S = sum of X(h) over the arm's hits.
- Subclasses (CO-PRIMARY, per seed, never pooled):
  inactive-word hits (m in {2,4,8}): X = 12 - wt_e_byte, range [0,12];
  active-word hits (m = 1): F = 0, X = 16 - wt_e_byte, range [0,16].

## 2. Byte-class partition (null rates per non-forced byte; inherited verbatim)

- D0 — diagonal bytes (PW[0]) of a hit whose ACTIVE word vanished (m & 1):
  e_i = d_i, input-drawn; p = 1/256 EXACT under the drawing model.
- D1 — diagonal bytes when the active word did NOT vanish:
  p_diag = ezdiag_miss / (4 * n_miss) — exact rational from the same run.
- O — off-diagonal bytes of non-vanished words:
  p_off = ezoff_miss / (12 * n_miss) — exact rational from the same run.

Class membership is determined by m(h) alone; no data-dependent choice.

## 3. Null model H0-X, test, and cutoff rule

- H0-X (per arm, exact-conditional on realized mask multiset and hit count):
  non-forced bytes of e on hit trials are independent Bernoulli at their class
  rates; X(h) Poisson-binomial over its 16 - F(h) non-forced bytes, independent
  across hits. Declared approximation: the DP conditions on the point estimates
  of p_diag/p_off (exact rationals; ~2^32-trial denominators at these seats,
  relative SE ~7e-5).
- TEST STATISTIC: p_extra = P_{H0-X}(S >= S_obs), computed by exact
  dynamic-programming convolution of the per-hit Poisson-binomial pmfs in exact
  rational arithmetic (common-denominator integer polynomials; fractions.Fraction
  for the reported values), for n_hits <= 2000 (frozen cap; not expected at t=1).
- p_deficit = P(S <= S_obs) computed and reported at every arm, DESCRIPTIVE ONLY.
- One-sided carrier direction: EXTRA zeros (large S).
- Fresh arms: RUN-INTERNAL EMPIRICAL NULL (D0 exact 1/256; D1 = p_diag;
  O = p_off from the arm's own miss counters) — frozen rule of 026d6a.
- REALIZED-COMPOSITION CUTOFF RULE (new bookkeeping of f8294e, frozen here):
  c = the SMALLEST integer with exact-DP tail P(S >= c | realized mask multiset,
  run-internal rates) <= 0.05 (alpha_extra = 1/20, one-sided). Executor
  re-verifies c > null mean (degeneracy check; clause (c) of the precedence
  clause: if c <= mean at the realized composition, PX-ALIVE's mean conjunct is
  decisive and the outcome falls to the PX-WEAK residual — recorded, never
  smoothed). Design-time bracket: c in {8, 9, 10} over the full composition
  range at n = 76 (sizes 0.0429/0.0211/0.0234-0.0290).
- OVERDISPERSION AUDIT (mandatory at n_hits >= 50, expected here): first two
  moments of the per-hit X distribution vs the null mean/variance, reported
  whatever the outcome; at n_hits < 50 the variance-calibration limit is
  disclosed with the reading, never smoothed.

## 4. Effect model and power reporting (frozen here)

- E-rho (preregistered): each hit independently gains EXACTLY ONE extra zero
  with probability rho: X_eff = X_null + Bernoulli(rho). Power statements are
  under E-rho; the per-byte-rate alternative agrees to first order in the
  per-hit mean shift (disclosed confounder, not smoothed).
- Power at realized N and composition: power(rho) = P(S_null + Binom(n, rho) >= c)
  = sum_k C(n,k) rho^k (1-rho)^(n-k) * P_null(S >= c - k), exact null tails from
  the DP, float64 rho-scan with declared approximation error << 1e-6.
- Reported: rho_50, rho_80 (bisection to 1e-6) and power at the grid
  {0.02, 0.05, 0.08, 0.096, 0.10, 0.12, 0.139, 0.15, 0.214, 0.30}.
- Bayes-factor calibration at the realized S_obs: BF(null vs rho) =
  P(S_obs | null)/P(S_obs | rho) under E-rho, with P(S_obs | rho) =
  sum_k C(n,k) rho^k (1-rho)^(n-k) P_null(S_obs - k). At S_obs = 0 this reduces
  exactly to (1-rho)^-n.
- JOINT-LR CONTROL (PR-P4, 0 runs): joint likelihood-ratio table of the new arm
  + committed G5 (seed 531002, n = 19, S_obs = 0; exact null pmf recomputed
  from the committed G5 receipt) against the rho grid
  {0.02, 0.05, 0.08, 0.096, 0.10, 0.15, 0.214}; joint LR = LR_new(rho) *
  LR_G5(rho), LR_G5(rho) = (1-rho)^19 exactly. Sanity envelope: at S_new = 0
  the joint BF reproduces (1-rho)^-(n_new+19) within DP tolerance. Reported
  whatever the branch outcome.
- Design-time power tables (f8294e session computation; executor re-derives
  from the definition at realized N): n = 76 design composition 57/19, p=1/256:
  null mean 247/64 = 3.85938, cutoff c = 8 (size 0.042871), rho_50 ~= 0.050,
  rho_80 ~= 0.083; G5-ratio composition 48/28: mean 4.0, cutoff 9 (size
  0.021131); N = 56 worst case: rho_80 <= 0.109. Binding design claim: 80%
  power against rho >= 0.109 uniformly over N >= 56.

## 5. Seats (exact tuples; arm command
`src/affarm046ex arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads> aes`)

- P0: this file (no invocation).
- P1a (BLOCKING): `src/affarm046ex pin 363851` (FIPS-197 C.1 KAT, BATCH-003
  anchors, 512-vector roundtrips r=1..10) -> runs/P1a_pin.json.
- P1b (BLOCKING): `src/affarm046ex pinidentity 363851` -> runs/P1b_pinidentity.json.
- P2 (BLOCKING, GATE-0 EXTENDED REBUILD, BEFORE any 2^32 arm): arm
  GATE0X256-J5-1-AES-R5-P30, tuple (sbox=aes, r=5, amask=1, smask=1, log2N=30,
  seed=531001, armid=1, threads=2) -> runs/P2_gate0x.json. Field-by-field
  reproduction of L1-AES-R5-P30
  (coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/runs/L1-AES-R5-P30.json)
  under the extended allowed-diff list (§7), AND hit_e_detail + ezdiag/ezoff
  counters + hit_trials IDENTICAL to the committed G3 receipt
  (coordination/goals/GOAL-AES-003/batches/BATCH-5ed9a3/tasks/TASK-20260901-ed281d/runs/G3_gate0x.json)
  (cap 256 >= 14 hits logs the same 14 records), AND hit_overflow = 0, AND
  hit_log_cap = 256. Any other difference voids the gate (FX5-P).
- P3 (FRESH DEAD ANCHOR AT MATCHED EXPOSURE, ANALYZED FIRST of the fresh arms,
  BINDING ORDER): arm ANCHORX-R6DEAD-AES-R6-P32, tuple (sbox=aes, r=6, amask=1,
  smask=1, log2N=32, seed=531003, armid=1, threads=4) -> runs/P3_anchor_r6.json.
- P4 (POWERED ALIVE ARM J5-2-P32, admitted ONLY if P3 passes): arm J5-2-P32,
  tuple (sbox=aes, r=5, amask=1, smask=1, log2N=32, seed=531003, armid=1,
  threads=4) -> runs/P4_j5_2_p32.json; X statistic, run-internal null,
  realized-composition cutoff, overdispersion audit (fires at n >= 50),
  subclass co-primary, power under E-rho at realized N/composition, joint-LR
  with committed G5.
- P5a/P5b (determinism double): arm DETX256-AES-R5-P20, tuple (sbox=aes, r=5,
  amask=1, smask=1, log2N=20, seed=531001, armid=1, threads=4), IDENTICAL
  command twice -> runs/P5_det_a.json, runs/P5_det_b.json; byte-identical
  receipt including all counters and zero_mask_e, timing fields excepted (strip
  set exactly {elapsed_seconds_measured, measured_rate_trials_per_sec}).
- P6: `src/affarm046ex freeze 363851` -> runs/P6_freeze_c_output.json +
  freeze_digest.py re-verification against the committed frozen table-freeze
  file coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-
  20260901-7e0b71/runs/R3_table_freeze.json (family unchanged; re-verification
  only) + source-diff audit record (post-arm re-verification of the pre-arm
  diff).

## 6. Instrument delta (the ONLY change to the BATCH-5ed9a3 affarm046ex source)

`#define HIT_LOG_CAP 64` -> `#define HIT_LOG_CAP 256` (line 341 of the
committed source). Pure logging capacity: the per-thread per-hit detail arrays
are sized by the macro; no trial stream, RNG, round function, or existing
counter is touched. Cap semantics unchanged: PER THREAD (each thread logs while
its own hit_count < HIT_LOG_CAP, else increments its own hit_overflow; receipt
aggregates sums). Expected ~66-76 hits at 2^32 (~16-19 per thread of 4) are far
below 256 per thread; 256 covers > 23 standard deviations above the observed
rate bracket. hit_overflow = 0 is a HARD GATE on every analysis-bearing receipt
(P3, P4); any overflow -> PX-GATE-FAIL per the cascade.
The receipt field hit_log_cap correspondingly reads 256 (was 64); this is the
sole new allowed diff of §7.

Support-script deltas (disclosed, NOT instrument source):
1. freeze_digest.py: the folded smoke self-check cap constants 64 -> 256
   (min(per_thread_hits, 64) -> min(per_thread_hits, 256) and
   hit_detail_records <= nthr * 64 -> <= nthr * 256) — a pure consequence of
   the instrument cap constant; no digest or table check touched.
2. gate0x_cmp.py: ALLOWED_DIFF extended by {hit_log_cap} (§7); added G3-receipt
   identity checks (hit_e_detail, ezdiag/ezoff counters, hit_trials,
   hit_log_overflow) per P2.
3. det_cmp.py, freeze_digest.py: task/idea labels updated to this task.
4. FRESH analysis code for this task: xstat.py (exact rational DP with
   realized-composition cutoff), power.py (E-rho power/BF at realized N),
   jointlr.py (joint LR with committed G5), assemble_results.py (ordered PX
   cascade). The BATCH-5ed9a3 xstat.py is NOT reused for decision-bearing
   numbers; the new DP is cross-checked against it on the committed G5 receipt
   (must reproduce S_obs = 0, p_extra = 1, null mean
   17180538557/17179868864, p_deficit 0.3671453866933061 digit-for-digit) and
   the check is recorded in runs/crosscheck_g5.json.

## 7. Gate-0 EXTENDED allowed-diff list (frozen here; inherits and extends the BATCH-5ed9a3 list)

Allowed to DIFFER between the cap-256 receipt and L1-AES-R5-P30, exactly:
{arm, probe, oracle, elapsed_seconds_measured, measured_rate_trials_per_sec}
PLUS this record's single new allowed diff: {hit_log_cap} (64 -> 256).
Fields the derivative ADDS (recorded informationally, never failures):
{zhist, sbox_table_hex, key_hex, sbox, sbox_k, sbox_positions, sbox_bijective,
arm_table_concat_sha256, ewhist_all, ewhist_miss, ewhist_hit, ewbithist_all,
ewbithist_miss, ewbithist_hit, hit_e_detail, ezdiag_all, ezoff_all,
ezdiag_miss, ezoff_miss, ezdiag_hit, ezoff_hit} (zero_mask_e rides INSIDE the
already-added hit_e_detail records).
ADDITIONAL IDENTITY REQUIREMENTS vs the committed G3 receipt (same seat):
hit_e_detail identical (14 records, byte-for-byte as JSON values), ezdiag_*/
ezoff_* identical, hit_trials identical, hit_log_overflow = 0 on both sides.
Any committed field missing, any non-allowed field differing, any unexpected
added field, or any G3-identity failure -> GATE FAIL (exit 5) -> HALT as
FX5-P/invalid_measurement (rule 5).

## 8. Anchor sequence and ordered PX decision cascade (frozen here)

BINDING ORDER: P3 is run and ANALYZED BEFORE P4; the alive reading is admitted
ONLY if the anchor passes; anchor failure halts the batch with no alive reading
admitted and no statement about e (rule 5).

Anchor gate at P3: p_extra > 0.05 (run-internal empirical null) AND
hits <= 32 (scaled dead band, 4x the 2^30 band of 8). Tripwire hits >= 33 is
the F6 escalation. Expected reading S_obs = 0 / p_extra = 1 exact (envelope
filled; both committed r=6 arms and G4 read S = 0). Anchor power limit
disclosed (catches systematic firing: at ~10 dead hits, 8/2 design composition,
rejects at S >= 3, P = 0.0142; band edge 32 hits rejects at S >= 6, P = 0.0248).

BRANCH CASCADE — exhaustive, evaluated in this FIXED ORDER, which IS the
branch-precedence clause:
1. PX-GATE-FAIL: any integrity gate fails (P1a/P1b KAT, P2 Gate-0 identity,
   P5a/P5b determinism, P6 digest/diff, or hit_overflow > 0 on an
   analysis-bearing receipt) -> invalid_measurement; HALT; repair (rule 5);
   never evidence about e.
2. PX-ANCHOR-FAIL: P3 reads p_extra <= 0.05 under its run-internal null (the
   repaired statistic FIRES ON THE DEAD ARM at 2^32) -> statistic indicted at
   this exposure (proves-too-much recurrence; FX4-P); HALT and repair; NO alive
   reading admitted; never evidence about e (rule 5).
3. PX-F6: anchor hits >= 33 (scaled tripwire, 4x the 2^30 band of 8) -> F6
   escalation to claim-changing review per the frozen taxonomy; HALT in-batch
   flow; alive reading not admitted in this batch.
4. PX-ALIVE: anchor passes AND at P4 p_extra <= 0.05 AND S_obs above its
   run-internal null mean -> the excess-zero signature RESURRECTS at t=1 at
   2^32, fresh seed 531003; EV-AES-241790's non-replication is converted into a
   measured seed-variance event; escalation to a claim-changing review round
   (Coordinator writes review_plan before any reviewer runs); Stage 1 spend
   stays GATED on that review and a new decision (nothing automatic).
5. PX-DEAD: anchor passes AND p_extra > 0.15 at P4 AND S_obs at or below its
   null mean -> weak excess-zero effects FALSIFIED at t=1 for rho >=
   rho_80(N_realized, composition_realized) at 80% power within
   statistic/cell/exposure/seeds (FX1-P); STOP RULE (non-replication branch):
   two monotone null readings at increasing exposure (531002@2^30 S = 0;
   531003@2^32 S <= mean) with rising power close the t=1 lane of the X
   statistic — no further t=1 exposure escalation without a NEW proposal; the
   obstruction block records the measured exclusion frontier
   rho_80(N_realized); effects rho < rho_50 remain named-unmeasured with the
   concrete revisit condition (only a pooled multi-seed design or larger
   exposure can touch them).
6. PX-WEAK: RESIDUAL branch — anchor passes AND neither PX-ALIVE nor PX-DEAD
   (at design composition this is S in {4..7}: direction above the mean with
   0.05 < p_extra <= 0.15, or S above the mean with p_extra > 0.15) ->
   weak-signal SURVIVAL, not closure; STOP RULE (survival branch): name the
   pooled multi-seed successor (second 2^32 arm at a fresh seed OR 4 x 2^30
   joint analysis, joint LR decision), report the joint LR with G5 NOW
   (0 runs), and return to the Coordinator for re-rank; the lane stays OPEN.

PRECEDENCE CLAUSE (repairing the RX-WEAK-b2/RX-DEAD overlap of
IDEA-20260901-026d6a per TASK-20260901-281b77 RT-B, applied prospectively to
this record's OWN rule): (a) the cascade is exhaustive and ordered — every
outcome matches EXACTLY ONE branch, because PX-WEAK is defined as the residual
and the ALIVE/DEAD conjuncts (p_extra <= 0.05 vs p_extra > 0.15; S above vs
at/below null mean) are disjoint; no two branches can both literally match, so
the 026d6a ambiguity cannot recur; (b) should any future RESTATEMENT of these
data match both a weak/non-replication description and a dead description, the
DEAD branch governs the SIGNATURE verdict (it adds the strictly more specific
conjunct S_obs <= null mean) and the weak-branch successor SURVIVES as a named
revisit condition — never silently preempted; (c) at realized compositions
where the computed cutoff c <= null mean (degenerate; not met at any
design-time composition, executor re-verifies c > mean), PX-ALIVE's mean
conjunct is decisive and the outcome falls to the PX-WEAK residual — recorded,
never smoothed. NOTE: because c > null mean at every examined composition,
p_extra <= 0.05 implies S above the mean automatically; both conjuncts are
retained for frozen-rule continuity. Budget halts are resource_exhaustion,
NEVER readings (rule 5). Thresholds: alpha_extra = 0.05 one-sided, weak band
(0.05, 0.15], dead band p_extra > 0.15 with S at/below null mean — inherited
from 026d6a. Subclass readings per seed whatever the outcome, never pooled.

## 9. Budget and stopping rules

- wall_clock_seconds 18000 (binding stop, stamped in budget_stamps.jsonl);
  maximum_runs 8 = planned 8 binary invocations (P1a, P1b, P2, P3, P4, P5a,
  P5b, P6; P0 is 0 runs; analysis scripts are not runs); memory_gb 4.
- BINDING BASELINE: each 2^32 analysis arm charged 4x the ~27 min 2^30 4-thread
  handoff baseline (~108 min); Gate-0 rebuild at the ~54 min 2-thread baseline;
  baseline total ~4.5 h. Measured campaign-hardware estimate ~14 min is
  flagged OPTIMISTIC-RELATIVE (disclosed, not the budget contract).
- Every stage boundary is a stopping point with a committed reading (halt after
  P2 = instrument-validation result; after P3 = anchor result; rule 5: budget
  exhaustion reported as resource_exhaustion, never as a result about e).
- Stage 1a/1b of IDEA-20260901-363851 is EXPLICITLY NOT spent by this record.

## 10. Artifacts

runs/P1a_pin.json, runs/P1b_pinidentity.json, runs/P2_gate0x.json (+cmp),
runs/P3_anchor_r6.json (+analysis), runs/P4_j5_2_p32.json (+analysis, +power,
+jointlr if reached), runs/P5_det_a.json, runs/P5_det_b.json (+cmp),
runs/P6_freeze_c_output.json, runs/P6_freeze_rerun.json,
runs/P6_digest_reverify.json, runs/source_diff_raw.txt, runs/source_diff.txt,
runs/crosscheck_g5.json, RESULTS.json, budget_stamps.jsonl, src/ (cap-256
build + scripts + BUILD.md).

## 11. Parse attestation discipline

RESULTS.json must parse as JSON (validated with python3 json.load before task
completion; attestation inside RESULTS.json).
