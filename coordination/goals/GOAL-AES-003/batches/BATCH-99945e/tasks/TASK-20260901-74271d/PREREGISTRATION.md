# PREREGISTRATION.md — TASK-20260901-74271d (executor, BATCH-99945e, GOAL-AES-003)

Hardening battery: the five red-team controls from
`coordination/goals/GOAL-AES-003/batches/BATCH-fe0bdc/tasks/TASK-20260901-31bac8/red_team_report.yaml`
(J1–J4 + the proves-too-much GUARD) against the verdict under test in
`ledger/evidence/EV-AES-ec53f1.yaml` (scope-narrowed CONFIRMED-MISMATCH-ALIVE,
producer TASK-20260901-f5d3a4).

This file is written BEFORE any run output exists (mtime-gated; only
budget_stamps.jsonl start stamp predates it — the budget clock is the mandated
first act). Every arm expectation below is PREREGISTERED and quotes the control
it discharges. Frozen comparator/excess_E convention, reused UNCHANGED by every
arm: comparator = AES dead at r=6 under the frozen excess_E = 2^30 convention
(carried from EV-AES-d33b1c OBS-B2-5, one-sided pooled 1.72x bound; not
re-measured here); excess ratios are reported against frozen excess_E = 2^30.

LINEAGE (reuse, disclosed): BATCH-fe0bdc TASK-20260901-f5d3a4 src/affarm046.c,
src/census046.py, src/bridge.py, KAT pins, and the frozen comparator/excess_E
convention; BATCH-014 TASK-20260805-b95720 src/rc8probe_feistel.c and BATCH-015
TASK-20260805-d408ac freshfeistel harness lineage for the GUARD arm.

## 0. Budget and run cap

Declared wall clock 2700 s: start 2026-09-01T19:15:52Z (epoch 1788290152),
binding stop 2026-09-01T20:00:52Z (epoch 1788292852). Halting at the stop is
full compliance (rule 5); dropped work is SCOPE, never an answer (rule 8).
MAXIMUM 8 RUNS. Plan: RUN 1 build+pins; RUN 2 J4 arm; RUN 3 J3 arm; RUN 4 J2
bridge; RUN 5 J1 census extension + r=16 keyed cell; RUN 6 GUARD; RUN 7
analyze; RUN 8 reserved for repair.

## 1. ARM J4 (LOAD-BEARING) — random-bijection arm at r=6, full 2^30

Discharges control J4 of TASK-20260901-31bac8 red_team_report.yaml
("cheapest_falsification_control": ONE r=6 arm with a random bijective S-box,
full 2^30, pre-registered band vs the analytic null; "falsifies_if: the
random-bijection arm is ALIVE at r=6 (excess well above null): then the r=6
death is AES-table-value-specific, not nonlinearity-driven, and the
factor-contrast reading dies").

GEOMETRY: exactly the BATCH-fe0bdc fixture arm — cell (r=6, A={0}, S={0}),
amask=1, smask=1, log2N=30 (2^30 trials), PW/CW probe geometry, trivial-swap
exclusion, W over all four PW words, per-thread splitmix64 seed formula
`seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15`, 8 threads, JSON arm
receipt. Comparator: the frozen comparator/excess_E = 2^30 convention, unchanged.

S-BOX (single factor varied): replaced by a FROZEN RANDOM BIJECTION ON 16
SYMBOLS, per the task card wording (authoritative frozen contract). Concrete
construction, pinned here before any draw:
- pi = uniformly random permutation of the 16 symbols {0..15}, drawn ONCE by
  Fisher-Yates with splitmix64 (campaign RNG convention, same modulo-bias
  disclosure as the archived set_random_sbox) at the PINNED DRAW SEED
  **46064002**.
- Byte S-box lift (fixed, deterministic, disclosed): SBOX[x] = pi[x>>4]<<4 |
  pi[x&0x0f]; INV_SBOX from pi^{-1} per nibble. The lift makes SBOX a bijection
  on all 256 byte values; with probability ~ 1 - |AGL(4,2)|/16! (~1 - 1.5e-8)
  it is nonlinear over GF(2). The key schedule uses this same SBOX for SubWord
  (single-factor semantics: the S-box is replaced everywhere it appears, as in
  the archived O-3 recipe).
- DISCLOSED INTERPRETATION DEVIATION: the red-team J4 control text says "the
  EV-AES-048545 O-3 recipe moved to r=6" and the archived O-3 recipe
  (probe_sbox.c set_random_sbox, BATCH-b41ba9) draws a uniform permutation over
  256 byte values; the task card frozen contract says "a freshly drawn random
  bijection on 16 symbols". The task card is authoritative; this arm implements
  the task card. Consequence: a DEAD reading here scopes the nonlinearity
  reading to the nibble-wise-bijection nonlinear subclass, not to uniform
  256-byte permutations; reviewers may re-scope. This is disclosed, not hidden.
- FROZEN-TABLE DISCIPLINE (task constraint): the table is drawn once at the
  pinned draw seed and frozen BEFORE the arm runs. RUN 1 `pinbij` receipt
  records the full table hex pre-arm; the RUN 2 arm re-derives the table from
  the same pinned seed inside the binary; the analyzer verifies byte-identity
  of the two tables. Redrawing after seeing data is VOID (the seed is pinned
  here, pre-data, so any redraw is detectable).
- NONLINEARITY GATE (blocking for J4): the drawn table must be bijective and
  must FAIL the exhaustive GF(2)-affinity test (S(x)^S(y)^S(0) == S(x^y) for
  all x,y). A drawn affine or non-bijective table is invalid_measurement
  (F-class halt), never a reading (rule 5).

ARM PARAMETERS: arm seed **46064001**, arm_id **4**, threads 8, log2N 30.
Key derived by the pinned formula kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL, splitmix64
(key_hex disclosed in the receipt).

PREREGISTERED EXPECTATION under the nonlinearity reading (EV-AES-ec53f1
OBS-FE0-4 / red-team J4): DEAD / absence like AES at r=6.
- Analytic null: E[hits] = (2^30 - T) * 4 * 2^-32 ~= 1.0 (per-word zero-diff
  probability 2^-32, 4 words), T the trivial count (E[T] = 2^30 * 2^-rho, rho
  carried as 32 in this cell => E[T] = 0.25).
- DEAD band (preregistered): hits <= 8 (Poisson(1.0) tail P(X >= 9) ~= 1.1e-6);
  excess ratio vs frozen excess_E = 2^30 at or below ~8/2^30; whist dominated
  by W <= 1.
- ALIVE trigger (preregistered, KILLS the 'nonlinearity-driven' wording):
  hits >= 100 (>= 100x the analytic null mean). An ALIVE reading is reported
  as such: the r=6 death is then S-box-table-specific within this contrast and
  the factor-contrast reading reverts to naming the AES S-box specifically
  (DEC-20260901-f41451 outcome clause).
- Gray zone (preregistered): 9 <= hits <= 99 => J4 INCONCLUSIVE (neither sealed
  nor killed); reported with the exact count.

## 2. ARM J3 — second-seed/key rerun of the r=6 affine arm (~49 s)

Discharges control J3 of the red-team report ("Re-run the fixture arm at one
fresh pre-registered seed AND fresh key"; "falsifies_if: any nontrivial trial
with W != 3, or hits below the pre-registered band 2^30-8"; "Prediction if the
claim holds: identical W statistics, hits = 2^30 - T', T' ~ Poisson(0.25)").

GEOMETRY: byte-identical reuse of the producer's src/affarm046.c (lineage copy,
disclosed in src/BUILD.md), cell (r=6, A={0}, S={0}), amask=1, smask=1,
log2N=30, 8 threads, identity S-box, frozen comparator/excess_E convention.
FRESH SEED **46063002** and FRESH arm_id **2** (producer used seed 46063001,
arm_id 1); the pinned key formula then yields a fresh key.

PREREGISTERED EXPECTATION (deterministic identity law): hits = 2^30 with T = 0
trivial swaps, W = 3 on 100% of nontrivial trials, whist = [0,0,0,2^30,0],
excess ratio 1.0 exact vs frozen excess_E = 2^30. Acceptance band (red-team
falsification band): hits >= 2^30 - 8. Any nontrivial trial with W != 3, or
hits below the band, is an F2-class instrument indictment at J3, never a
mechanism reading.

## 3. ARM J2 — keyed bridge cells at r=3 and r=7 (500 trials each)

Discharges control J2 of the red-team report ("Keyed bridge cells at r in {3,7}
(two derivation-only round counts), 500 trials each, fresh seed -- seconds";
"falsifies_if: any trial with q0^q1 != p0^p1 or W != 4-|A| at r=3 or r=7").

GEOMETRY: reuse of the producer's bridge.py structure (lineage copy adapted,
disclosed), cells (r=3, A={0}, S={0}) and (r=7, A={0}, S={0}) — the two
derivation-only round counts named by the control — 500 FRESH keyed trials per
cell (fresh key per trial, identity S-box), FRESH SEED **"46060902a"**.
Frozen comparator/excess_E convention carried in the reporting fields.

PREREGISTERED EXPECTATION: identity law q0^q1 = p0^p1 on 500/500 trials AND
W = 4 - |A| = 3 on 500/500 trials in BOTH cells (100%); any deviation is an
F2/F3-class defect verdict, never a mechanism reading.

## 4. ARM J1 — census extension r=11..16 + one r=16 keyed cell

Discharges control J1 of the red-team report ("Pre-register a flatness
extension at r=11..16 (same law, same rho recursion), then run census046.py on
the extended range (zero cipher compute) PLUS one keyed bridge cell at r=16
(500 trials, fresh seed)"; "falsifies_if: D_r M_r != I_128 or any non-flat W
law at r in 11..16 under the pinned convention").

PART A (census extension, pure GF(2) algebra, ZERO cipher compute): reuse of
the producer's census046.py construction (lineage copy adapted: rmax extended
10 -> 16; the frozen 10-cell set is UNCHANGED and CLOSED), convention
M_r = SR.(MC.SR)^{r-1}, D_r = (ISR.IMC)^{r-1}.ISR, same rho recursion.

PREREGISTERED EXPECTATION (flat per the r-free derivation), for every r in
11..16 and all 10 cells:
- per-r port guards D_r M_r = I_128 AND M_r D_r = I_128;
- word maps A_{r,S,j} = P_j(D_r M_r)Pi_A column-equal to P_j Pi_A (rank 32 for
  j in A, rank 0 otherwise);
- W = 4 - |A| deterministic; P(W>=1 | nontrivial) = 1 for |A| <= 3 and 0 for
  |A| = 4 (structure-destroyed cell flat-dead at every extended r).
- rho at r=11..16 is recomputed under the SAME recursion and REPORTED as data;
  no numeric rho values for r=11..16 exist in the frozen inputs, so none are
  numerically preregistered here (disclosed; the control's falsification
  criteria are D_rM_r != I_128 or a non-flat W law, not rho values).

PART B (one r=16 keyed cell, 500 trials): cell (r=16, A={0}, S={0}), 500 FRESH
keyed trials, FRESH SEED **"46060903a"**, identity S-box, bridge.py lineage.
DISCLOSED CONVENTION EXTENSION for r=16 keyed trials only: the pinned key
expansion provides r+1 = 17 round-key blocks; the rcon sequence is continued
canonically as successive GF(2^8) powers under the AES polynomial (xtime
iteration; rounds 11..16 get 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f), the unique
FIPS-197-consistent continuation. Under the identity S-box the identity law is
a theorem for ANY round-key values, so this extension cannot manufacture a law
violation; it is disclosed for exactness.

PREREGISTERED EXPECTATION (keyed cell): identity law on 500/500 and W = 3 on
500/500 (the law holds on every trial, trivial or not); any deviation is an
F2/F3-class defect verdict.

## 5. ARM GUARD — identity-law bridge on the dead Feistel substitute (500 trials)

Discharges the proves-too-much guard of the red-team report
(proves_too_much.objects[0].residual_risk: "run the identity-law bridge check
(q0^q1 == p0^p1?) on the archived Feistel substitute at r=5, 500 trials --
seconds; the harness exists ... Prediction: the identity law FAILS on most
trials. If it HELD, the identity law would not discriminate alive from dead and
the argument would prove too much").

OBJECT: the dead keyed murmur3-fmix64 balanced Feistel substitute of
EV-AES-dec938 (BATCH-014 TASK-20260805-b95720 rc8probe_feistel.c; 16 rounds,
64-bit halves, fmix64 round function; absent at matched 2^30 exposure per
EV-AES-dec938 OBS-B14-3 M1: 0 hits, and EV-AES-5478a0 OBS-B16-1/2). The EXACT
dead instance is used: key bdf3823182ad657dab3d556b3886ba72, which the pinned
campaign key formula (kst = seed ^ 0xA5A5..., splitmix64) derives from seed
**531001** — verified computationally before this battery (both bytes match the
committed M1-FEISTEL-P30 receipt). Probe geometry amask=1, smask=1 (the r=5
yoyo probe geometry of the original measurement; the Feistel oracle's round
count is fixed at 16 and its rounds field is not a tunable).

IMPLEMENTATION: byte-identical copy of BATCH-014 rc8probe_feistel.c for the C
detcheck gate and a C stream cross-check arm; plus a fresh Python port of the
oracle + trial semantics (expression-identical, disclosed) that logs the
per-trial identity law the C harness does not log. TRIAL STREAM: seed 531001,
arm_id **999** (fresh stream; key unchanged), threads 1, 512-trial stream.
PORT-PARITY GATE (blocking): Python aggregate whist + trivial counts over the
512-trial stream must EXACTLY match the C arm receipt over the same stream;
C detcheck (4096 vectors) must pass. Any parity failure is invalid_measurement,
never a reading.
READ: identity-law statistics on the FIRST **500** trials of that stream (the
preregistered exposure); the full 512 are used only for the C/Python parity
gate.

PREREGISTERED EXPECTATION: the identity law FAILS there (premise D-affine does
not hold for the nonlinear-D substitute; the derivation breaks at premise (b),
red-team proves_too_much).
- Quantitative decision rule (preregistered): identity law holds (q0^q1 ==
  p0^p1) on < 50% of the 500 trials => GUARD PASS: the non-transfer is
  empirically sealed (the proves-too-much guard of EV-AES-ec53f1
  unresolved_confounds is discharged at this exposure). Analytic expectation:
  ~0 holds (a random-looking 128-bit qdiff equals the fixed pdiff with
  probability ~2^-128 per trial).
- identity law holds on >= 50% => GUARD FAIL: the identity law does not
  discriminate alive from dead; the skeleton/death contrast proves too much;
  verdict-level consequence = proves-too-much fired (reported as such).

## 6. Battery-level consequence map (preregistered)

- ALL FIVE arms meet expectations => ALL-SEALED: the four overclaim joints'
  named cheapest controls (J1-J4) and the proves-too-much guard all hold
  within their preregistered scopes; the scope-narrowed verdict of
  EV-AES-ec53f1 survives this battery (consequence named per arm: sealed).
- J4 ALIVE (hits >= 100) => KILLED-AT-J4: the 'nonlinearity-driven' wording
  dies; the reading reverts to the factor-contrast with the AES S-box named
  specifically (and the J4 nibble-bijection subclass named as ALIVE).
- J4 gray zone (9..99 hits) => J4 INCONCLUSIVE; battery reports
  narrowed/inconclusive-at-J4, not sealed.
- J3 deviation => F2-class instrument indictment; the alive side of the
  contrast is voided at this batch (repair route, not a mechanism reading).
- J2 or J1 deviation => F2/F3-class defect verdict at that joint.
- GUARD FAIL => proves-too-much fired (see section 5).
This executor interprets NOTHING about hypothesis status, assigns no evidence
strength, and recommends no promotion; consequence labels above are the
preregistered outcome names the validator/coordinator consume.

## 7. Halt and deviation semantics

Budget stop => resource_exhaustion halt; halting is full compliance; dropped
work is SCOPE, never an answer. Implementation/parity failure =>
invalid_measurement (rule 5), never evidence against a hypothesis. Unexpected
observations are recorded in RESULTS.json deviations, never discarded (rule 8).

## 8. Inference block (every structured artifact of this task)

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max   # ACTUAL model serving this session
  model_verified: false          # no orchestration.adapter doctor --probe run this session
  fallback_used: true            # session-backend transport under inference amendment DEC-20260831-0d1eeb
  fallback_reason: session-backend transport under inference amendment DEC-20260831-0d1eeb
  degraded_requirements: []
  amendment: DEC-20260831-0d1eeb
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

Parse attestation: every JSON artifact produced by this task is parsed whole
with python3 json.load before task completion and this is stated inside each
artifact. Claim tier: TOY throughout; nothing about deployed AES; no comparison
to published cryptanalysis in either direction (RQ-AES-003 R3).
