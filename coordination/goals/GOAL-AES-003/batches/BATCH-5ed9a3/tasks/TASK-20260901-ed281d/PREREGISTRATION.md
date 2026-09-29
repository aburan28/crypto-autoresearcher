# PREREGISTRATION — TASK-20260901-ed281d (BATCH-5ed9a3, GOAL-AES-003)

Write-once preregistration (integrity_gates.digest_commit_discipline, V-804-2,
BATCH-fe0bdc precedent). This file's mtime is BEFORE the first fresh arm of
Stage r1. Frozen contract: `ledger/proposals/IDEA-20260901-026d6a.yaml`
(Stages r0+r1 only; Stage 1 of the ramp stays gated and is NOT spent here).

- task_id: TASK-20260901-ed281d; batch: BATCH-5ed9a3; idea: IDEA-20260901-026d6a
- role: executor (observations only; no status/strength/promotion interpretation)
- claim_tier: toy; no full-round/deployed-AES statements; no published-cryptanalysis
  comparisons in either direction (RQ-AES-003 R3).

## Inference block (all artifacts of this task)

- policy: executor-implementation; requested_policy: executor-implementation
- resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL
  session model; no adapter probe executed in this session; model_verified: false)
- fallback_used: true — session-backend transport under inference amendment
  DEC-20260831-0d1eeb (standing_basis
  0137a051eb5828789eb267fa83c8278086578d4c); degraded_requirements: []
- independent_session_required: true (per handoff)

## 1. Statistic (verbatim semantics of IDEA-20260901-026d6a.repaired_statistic)

Per hit h with e_i = (q0[i]^q1[i]) ^ (p0[i]^p1[i]) as in the frozen instrument:

- Ze(h) = #{i : e_i = 0} = 16 - wt_e_byte(h). (The logged Z field counts zeros of
  q0^q1 — affarm046e.c:388 — and is NEVER used in the statistic.)
- m(h) = vanishing_word_mask, bit j set iff (q0^q1) vanishes on PW word j;
  PW word 0 = {0,5,10,15} (diagonal/active word).
- F(h) = 4 * popcount(m(h) & 0b1110) — forced zero bytes by the envelope theorem.
- X(h) = Ze(h) - F(h) >= 0 (extra zeros beyond the forced envelope).
- Primary scalar S = sum of X(h) over the arm's hits.
- Subclasses (CO-PRIMARY, per seed, never pooled):
  inactive-word hits (m in {2,4,8}): X = 12 - wt_e_byte, range [0,12];
  active-word hits (m = 1): F = 0, X = 16 - wt_e_byte, range [0,16].

## 2. Byte-class partition (null rates per non-forced byte)

- D0 — diagonal bytes (PW[0]) of a hit whose ACTIVE word vanished (m & 1):
  e_i = d_i, input-drawn; p = 1/256 EXACT under the drawing model.
- D1 — diagonal bytes when the active word did NOT vanish: e_i = (q0^q1)_i ^ d_i;
  p_diag = (zeros of e on the 4 diagonal positions over the arm's MISS trials)
  / (4 * n_miss) — exact rational from the same run.
- O — off-diagonal bytes of non-vanished words: e_i = (q0^q1)_i;
  p_off = (zeros of e on the 12 off-diagonal positions over the arm's MISS
  trials) / (12 * n_miss) — exact rational from the same run.

Class membership is determined by m(h) alone; no data-dependent choice.

## 3. Null model H0-X and test

- H0-X (per arm, exact-conditional on realized mask multiset and hit count):
  non-forced bytes of e on hit trials are independent Bernoulli at their class
  rates; X(h) Poisson-binomial over its 16 - F(h) non-forced bytes, independent
  across hits. Declared approximation: the DP conditions on the point estimates
  of p_diag/p_off (exact rationals; ~2^30-trial denominators at these seats).
- TEST STATISTIC: p_extra = P_{H0-X}(S >= S_obs), computed by exact
  dynamic-programming convolution of the per-hit Poisson-binomial pmfs in exact
  rational arithmetic (fractions.Fraction), for n_hits <= 2000.
- For n_hits > 2000 (not expected at t=1): deterministic subsample = the first
  2^20 hits in stream order (global trial index = thread partition offset +
  in-thread index; pinned, not data-dependent), exact DP on the subsample
  deciding, full-sample mean-excess z-score reported as audit.
- p_deficit = P(S <= S_obs) computed and reported at every arm, DESCRIPTIVE ONLY.
- One-sided carrier direction: EXTRA zeros (large S).
- Stage r0 (committed receipts carry no class baseline): NAIVE uniform null,
  p = 1/256 for every non-forced byte (per IDEA-20260901-026d6a PR-2).
- Stage r1 fresh arms: run-internal empirical null (D0 exact 1/256; D1 = p_diag;
  O = p_off from the arm's own miss counters).
- Overdispersion audit: any arm with n_hits >= 50 reports the first two moments
  of the per-hit X distribution vs the null mean/variance. At small n the
  variance-calibration limit is disclosed with the reading, never smoothed.

## 4. Seats (exact tuples)

Stage r0 (0 cipher runs; fresh-code exact arithmetic on committed receipts):
- A1-ANCHOR: committed r=6 dead reference —
  coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R5_r6_reference.json
  (aes, r6, amask=1, smask=1, 2^30, seed 531001, armid 1, threads 4; 3 hits,
  masks {1,1,2}, weights {16,16,12}). Analyzed FIRST; must read p_extra > 0.05
  (expected 1.0 exactly) before the restatement is admitted.
- A1-RESTATEMENT: committed seed-531001 hits —
  .../runs/R4_gate0_j5.json (aes, r5, amask=1, smask=1, 2^30, seed 531001,
  armid 1, threads 2; 14 hits). HYPOTHESIS-GENERATING ONLY (inspected data).

Stage r1 (extended build `affarm046ex`; arm command
`src/affarm046ex arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads> aes`):
- G1: this file (no invocation).
- G2a (BLOCKING): `src/affarm046ex pin 363851` (FIPS-197 C.1 KAT, BATCH-003
  anchors, 512-vector roundtrips r=1..10).
- G2b (BLOCKING): `src/affarm046ex pinidentity 363851`.
- G3 (BLOCKING, GATE-0 EXTENDED): arm GATE0X-J5-1-AES-R5-P30, tuple
  (sbox=aes, r=5, amask=1, smask=1, log2N=30, seed=531001, armid=1, threads=2);
  field-by-field reproduction of L1-AES-R5-P30
  (coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/runs/L1-AES-R5-P30.json)
  under the extended allowed-diff list (§5). Doubles as the seed-531001
  class-baseline collection and the continuity check (14 hits unchanged).
- G4 (FRESH DEAD ANCHOR, analyzed FIRST of the fresh arms, BINDING ORDER):
  arm ANCHORX-R6DEAD-AES-R6-P30, tuple (sbox=aes, r=6, amask=1, smask=1,
  log2N=30, seed=531002, armid=1, threads=4).
- G5 (CONFIRMATORY ALIVE ARM J5-2, admitted ONLY if G4 passes): arm
  J5-2-AES-R5-P30, tuple (sbox=aes, r=5, amask=1, smask=1, log2N=30,
  seed=531002, armid=1, threads=4).
- G6 (determinism double): arm DETX-AES-R5-P20, tuple (sbox=aes, r=5, amask=1,
  smask=1, log2N=20, seed=531001, armid=1, threads=4), IDENTICAL command twice;
  byte-identical receipts including the new counters and zero_mask_e, timing
  fields excepted (strip set exactly {elapsed_seconds_measured,
  measured_rate_trials_per_sec}).
- G7: `src/affarm046ex freeze 363851` + freeze_digest.py re-verification against
  the committed frozen table-freeze file
  coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json
  (family unchanged from 363851; re-verification only) + source-diff audit record.

## 5. Gate-0 EXTENDED allowed-diff list (frozen here)

Allowed to DIFFER between the extended receipt and L1-AES-R5-P30, exactly:
{arm, probe, oracle, elapsed_seconds_measured, measured_rate_trials_per_sec}.
Fields the derivative ADDS (recorded informationally, never failures):
{zhist, sbox_table_hex, key_hex, sbox, sbox_k, sbox_positions, sbox_bijective,
arm_table_concat_sha256, ewhist_all, ewhist_miss, ewhist_hit, ewbithist_all,
ewbithist_miss, ewbithist_hit, hit_e_detail}  [Stage-0 set]
PLUS this batch's extension, exactly:
{ezdiag_all, ezoff_all, ezdiag_miss, ezoff_miss, ezdiag_hit, ezoff_hit}
(the class-wise zero-byte counters) and the zero_mask_e field INSIDE the
already-added hit_e_detail records. Any committed field missing, any non-allowed
field differing, or any unexpected added field -> GATE FAIL (exit 5) -> HALT as
FX5/invalid_measurement (rule 5).

## 6. Instrument delta (the ONLY change to the Stage-0 affarm046e source)

Pure reads AFTER all trial decisions, into new counters/fields only:
1. per-arm class-wise zero-byte accumulators over the all/miss/hit splits:
   ezdiag (zeros of e on the 4 diagonal positions PW[0] = {0,5,10,15}) and
   ezoff (zeros of e on the 12 off-diagonal positions), with denominators
   (4*n_split, 12*n_split) derived in analysis from existing nontrivial/W_ge1
   fields;
2. per-hit detail adds one field within the existing HIT_LOG_CAP = 64
   convention: zero_mask_e (16-bit mask, bit i set iff e_i = 0).
No trial stream, RNG, round function, or existing counter is touched. The
source diff vs the Stage-0 source is recorded and annotated in G7; any line
touching stream/RNG/round-function/existing counters voids the gate (FX5).
Probe label: affarm046ex. Oracle label: live_aes_r<R>_affarm046ex_derivative_of_affarm046.

## 7. Anchor sequence and decision rule (frozen here)

STAGE r0 (committed data):
- (R0-ANCHOR-PASS) repaired statistic on the committed r=6 arm reads
  p_extra > 0.05 (expected 1.0 exactly) -> proceed to restatement.
- (R0-ANCHOR-FAIL) any other value -> executor recomputation error or field
  mismatch; HALT and reconcile; no restatement admitted.

STAGE r1 (G4 analyzed BEFORE G5; G5 admitted only if the anchor passes):
- Anchor gate at G4: p_extra > 0.05 (run-internal empirical null) AND
  hits <= 8 (carried dead band). Tripwire hits >= 9 is F6 escalation: HALT,
  no alive reading admitted, report for claim-changing review.
- (RX-ALIVE) anchor passes AND at G5 p_extra <= 0.05 AND S_obs above its
  run-internal null mean.
- (RX-WEAK) anchor passes AND (0.05 < p_extra <= 0.15 at G5, OR p_extra <= 0.05
  at the 531001 restatement but > 0.15 at G5 [direction not reproduced]).
- (RX-DEAD) anchor passes AND p_extra > 0.15 at G5 AND S_obs at or below its
  null mean (residual not replicated; FX1 within the tested scope).
- (RX-ANCHOR-FAIL) p_extra <= 0.05 at G4 -> statistic indicted (proves-too-much
  recurrence, FX4); HALT and repair; invalid_measurement; NO alive reading;
  never evidence about e (rule 5).
- (RX-GATE-FAIL) any gate failure (G2/G3/G6/G7) -> invalid_measurement, HALT,
  repair (rule 5).
- Budget halts are resource_exhaustion, NEVER readings (rule 5).

Thresholds: alpha_extra = 0.05 (one-sided), weak band (0.05, 0.15], dead band
p_extra > 0.15 with S_obs <= null mean. Subclass readings (active/inactive X,
mask composition) reported per seed whatever the outcome, never pooled.

## 8. Budget and stopping rules

- wall_clock_seconds 7200 (binding stop, stamped in budget_stamps.jsonl);
  maximum_runs 8 (planned: 8 binary invocations = G2a, G2b, G3, G4, G5, G6 x2,
  G7 = 7 record runs, at cap; analysis scripts are not runs); memory_gb 4.
- Every stage boundary is a stopping point with a committed reading (r0 halt =
  restatement+anchor result; after G3 = instrument-validation result; after G4
  = anchor result). Stage 1a/1b of 363851 is NOT spent here.

## 9. Artifacts

runs/G2a_pin.json, runs/G2b_pinidentity.json, runs/G3_gate0x.json (+cmp),
runs/G4_anchor_r6.json, runs/G5_j5_2.json, runs/G6_det_a.json,
runs/G6_det_b.json (+cmp), runs/G7_freeze_c_output.json,
runs/G7_freeze_rerun.json, runs/G7_digest_reverify.json, runs/source_diff.txt,
runs/r0_analysis.json, runs/G4_anchor_analysis.json (if reached),
runs/G5_analysis.json (if reached), runs/G6_det_cmp.json, runs/G3_gate0x_cmp.json,
RESULTS.json, budget_stamps.jsonl, src/ (extended build + scripts + BUILD.md).

## 10. Parse attestation discipline

RESULTS.json must parse as JSON (validated with python3 json.load before task
completion; attestation inside RESULTS.json).
