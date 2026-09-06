# PREREGISTRATION — TASK-20260901-3dffdc (IDEA-20260901-ec54fe STAGE 0)

Written 2026-09-01T17:24Z, BEFORE any run output (mtime of this file predates every
file under runs/). Frozen spec: `ledger/proposals/IDEA-20260901-ec54fe.yaml` (read whole).
Task card: `coordination/goals/GOAL-AES-003/batches/BATCH-803af6/dispatch_queue.json`,
task TASK-20260901-3dffdc. Budget: 5400 s wall (start 2026-09-01T17:17:29.512413Z,
binding stop 2026-09-01T18:47:29.512413Z), 4 GB, MAXIMUM 8 RUNS.

Scope of this task per the task card: (1) blocking anchor reproduction
(ranks 32,0,0,0 -> P(hit)=1.0), (2) the exact GF(2) census T_{r,S} over the FROZEN cell
set at r=1..10, (3) ONE 2^30 affine fixture arm at a census NULL-predicted cell,
(4) RESULTS.json applying the record's Stage-0 decision rule. Stages 1-2 of the record's
`minimal_test` beyond the named items are NOT run (task card: "Implement STAGE 0 ONLY";
the card's item list is authoritative for what runs here).

## 1. VERBATIM from the frozen spec — census object (idea record `object` / `claim` P2)

> for an input difference d supported on the active plaintext words PW[A], the swapped and
> decrypted difference is T_{r,S}(d) = M_r^{-1} . Z_{CW[S]} . M_r . d, where Z_{CW[S]} zeroes
> the swapped ciphertext word(s). W counts the plaintext words PW[j] on which T_{r,S}(d)
> vanishes, so the entire per-trial law of the probe in cell (r, A, S) is determined by the
> ranks and joint kernel structure of the four word maps T_{r,S,j} : GF(2)^{32|A|} -> GF(2)^32
> obtained by restricting T_{r,S} to PW[j]. AddRoundKey drops out (translation on differences)

> (P2) THE CENSUS. Compute, with zero cipher evaluations (sparse 128x128 GF(2) matrix
> products), the rank quadruple and the induced per-trial law for every cell in the frozen set
> C = { (A={0},S={0}), (A={0},S={1}), (A={0},S={2}), (A={0},S={3}), (A={i},S={i}) for i=1,2,3,
> (A={0,1},S={0}), (A={0},S={0,1}), (A={0,1,2,3},S={0}) } at every r in 1..10.

Cipher convention (record `assumptions`, pinned): `E_K^r = ARK_r . SR . SB .
[ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0` with FIPS-197 ShiftRows offsets and MixColumns
matrix; with SB = id the difference map is M_r = SR . (MC . SR)^{r-1} (final round drops
MixColumns). State column-major: byte index 4*col+row. Probe geometry (BATCH-002 pinned,
BATCH-b41ba9 geom.json): PW[j][row] = 4*((j+row)%4)+row, CW[j][row] = 4*((j-row)%4)+row.

**FROZEN CELL SET IS CLOSED.** The 8 cells above are the complete universe of cells this
task predicts or measures. Any cell added after seeing data is post-hoc and void (record's
own disclosure, `target_complexity.hidden_overhead` / `confounders`); this task enforces it:
no other cell is computed against a prediction and no other cell is measured.

## 2. VERBATIM from the frozen spec — predictions (record `predictions` block)

### PR-1
metric: "Anchor cell re-measurement (affine cipher, r=5, A={0}, S={0}, fresh implementation,
2^30 trials)"
minimum_effect: "W=3 on 100% of nontrivial trials; excess ratio 1.0 against the frozen
excess_E; rank quadruple 32,0,0,0 recomputed. BLOCKING: any deviation is an
instrument/derivation defect (F1), never a negative observation."

### PR-2
metric: "Census-predicted per-trial P(W>=1) for every frozen cell at r=1..10, committed as a
digest before measurement"
minimum_effect: "A complete table with exact rational values (multiples of 2^-32 per trial at
32-bit word granularity), each cell labelled SKELETON-ALIVE (P > 2^-30) or SKELETON-NULL
(P = 2^-30) or intermediate, and the affine death round r*_aff named. The table is the
deliverable even if no measurement arm runs."

### PR-3
metric: "The affine death round r*_aff versus the measured AES death round (alive@5, dead@6)"
minimum_effect: "One of the three pre-registered readings MATCH / MISMATCH-ALIVE /
MISMATCH-DEAD, with the committed interpretation of each. Recorded prior, disclosed as a
prior and not a prediction: P(MATCH) ~ 0.35, P(MISMATCH-ALIVE) ~ 0.40, P(MISMATCH-DEAD)
~ 0.25 - the anchor cell proves the skeleton alive at r=5 and the r=2 control proves it
alive at r=2, but nothing committed pins its behaviour at r=6."

### PR-4
metric: "Measured hit count of at least two census NULL-predicted cells on the AFFINE cipher
at matched exposure (2^30 or 2^32)"
minimum_effect: "Count inside the null band (<=12 at 2^32, i.e. excess factor <=3.0x per the
BATCH-002 non-replication rule N1; Garwood 95% CI contains the null rate at 2^30). An excess
in a null-predicted cell on a known-structured object is F2."
(Task-card scope note: this task runs ONE such arm, not two; the second arm belongs to the
record's Stage 2 and is out of scope here. Recorded as a scope statement, not a deviation
from the frozen spec's Stage-2 design.)

### PR-5
metric: "Affine prediction for the structure-destroyed cell (A={0,1,2,3}, S={0}) versus the
committed AES amask=15 readings (1.00x; 4 at N=2^32)"
minimum_effect: "The census must predict ~null (per-trial P within a factor 3 of 2^-30) for
this cell, or the census masks are misaligned with the instrument's amask semantics and the
whole table is void pending repair."
(This task checks the census-prediction half of PR-5 / F4; no amask=15 arm is run here.)

### PR-6
metric: "W-histogram fingerprint across r in the anchor cell (census-predicted W value for
r=1..10 under SKELETON-ALIVE)"
minimum_effect: "A pre-registered per-r predicted W value (the anchor gives W=3 at r=5; the
r=2 control gives W=3 at r=2 even with the real S-box). Where the census predicts a different
W for some r, a single cheap affine arm at that r decides whether the fingerprint holds; the
fingerprint is a finer invariant than the hit count and costs nothing to predict."
(The per-r predicted W values for the anchor cell are part of this task's census table; the
optional extra arm at r != 5 is Stage 2 and out of scope here.)

## 3. VERBATIM from the frozen spec — decision rule and falsifiers

preregistered_decision_rule:
> Committed before Stage 2 runs, keyed to PR-3: (MATCH) r*_aff = 6 AND all measured cells
> agree with their census predictions -> record the conclusion "the round-count location of
> the excess is carried by the linear skeleton" at toy tier and route the residual question
> to IDEA-20260901-bcb117; (MISMATCH-ALIVE) r*_aff > 6 AND measured cells agree -> record
> "the skeleton outlives the AES excess; death-round is nonlinearity-driven" and the ramp
> becomes RANK 1; (MISMATCH-DEAD) or ANY measured cell disagreeing with its exact prediction
> -> F1/F2 fires, all readings VOID as instrument/derivation defect, repair dispatched, no
> mechanism conclusion recorded. A budget halt is resource_exhaustion, never a reading.

F1 (BLOCKING):
> The anchor reproduction fails - W != 3 on some nontrivial trial, or the recomputed ranks
> are not 32,0,0,0. Instrument or convention defect; every census reading is VOID; the run
> returns as invalid_measurement, never as evidence against the skeleton.

F2 (PROVES-TOO-MUCH):
> A census NULL-predicted cell reads excess on the affine cipher (count above the null band
> at matched exposure). The pipeline manufactures excess on a known-structured object; the
> instrument is indicted; this indicts the whole localization program's interpretability and
> escalates to IDEA-20260901-02f7c4's battery and to independent review before any further
> mechanism reading.

r*_aff definition (record P3):
> Define r*_aff as the smallest r >= 2 at which the census-predicted per-trial P(W >= 1) for
> cell (A={0}, S={0}) falls to or below the analytic null 2^-30 (equivalently: the predicted
> hit count at the frozen exposure lies inside the campaign's null band).

## 4. Anchor values reproduced from the committed anchor (EV-AES-048545 O-7, BATCH-b41ba9
TASK-20260806-47f217 results.json — read directly from the source files this session)

- Anchor cell: r=5, A={0} (amask=1), S={0} (smask=1), SBOX = identity.
- Archived rank quadruple: word maps 32, 0, 0, 0 (Validator independently reproduced;
  D.M = I_128 verified by the archived algebra_rank.py).
- Archived measurement (N=2^32, seed 189001301, armid 301, 8 threads):
  trivial_swaps_excluded=0, W_ge1_nontrivial=4294967296, whist=[0,0,0,4294967296,0],
  W_ge1_by_word=[0,4294967296,4294967296,4294967296], excess=2^30, ratio to frozen
  excess_E = 1.0000000000002.
- This task's anchor arm: fresh implementation, 2^30 trials (PR-1), seed 189001301,
  armid 301, 8 threads. With the lineage's per-thread seeding
  (seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15) and 8|2^30, each thread's
  2^27-trial stream is an exact PREFIX of the archived arm's per-thread 2^29-trial stream
  (same seed_thread values), so the fresh arm re-measures a substream of the archived anchor
  stream. Prediction is seed-independent anyway (record P1 / DEC-20260804-73977c D-8(ii)).
- PR-1 pass criterion (frozen): W=3 on 100% of nontrivial trials; excess ratio 1.0 against
  frozen excess_E = 2^30 (excess formula: W_ge1_nontrivial / (nontrivial_trials * 2^-30),
  archived results.json `measured.excess_formula`); recomputed ranks 32,0,0,0.

## 5. Fixture-cell pick rule (documented BEFORE any census output exists)

The fixture arm runs at one census NULL-predicted cell of the frozen set, picked by this
pre-declared rule applied to the census table (the record says "whichever cells the census
names"; the tie-break below is executor-declared and is part of this preregistration):

1. NULL tier (record definition): cells with census per-trial P(W>=1) == 2^-30 EXACTLY
   (exact rational equality, per-trial over all trials incl. d=0 — the convention the
   archived anchor used for E[W>=1] per trial). Among these, additionally prefer cells with
   |A| <= 3 over |A| == 4, because an |A|<=3 cell is the strong known-false control (the
   record's controls block: the same cipher is known maximally structured elsewhere) while
   the |A|=4 cell is structurally forced to read ~0 hits. Within the preferred group:
   smallest r, then frozen-set enumeration order C1..C8 as listed in section 1.
2. Fallback tier (only if NO cell has P == 2^-30 exactly): cells with 0 < P < 2^-30
   (sub-null), pick MAX P (closest to the null band from below — most powerful fixture),
   same |A|<=3 preference, then smallest r, then enumeration order.
3. Last resort (only if tiers 1 and 2 are both empty): the structure-destroyed cell
   (A={0,1,2,3}, S={0}) at the smallest r, with this deviation disclosed in RESULTS.json.

The picked cell and the tier that picked it are written to runs/fixture_pick.json BEFORE the
fixture arm executes.

## 6. Fixture-arm prediction (record PR-4, at 2^30)

- Per-trial analytic null = 2^-30 (campaign frozen null; EV-AES-d33b1c / BATCH-002
  preregistration as cited by the record). At 2^30 trials the null expectation is 1.0 hit.
- PASS band (preregistered): Garwood 95% CI on the excess factor
  R = W_ge1_nontrivial / (nontrivial_trials * 2^-30) contains 1.0; equivalently the CI on
  the rate contains 2^-30. Additionally report the scaled count band <=3 hits at 2^30
  (the record's "<=12 at 2^32 / excess factor <=3.0x" scaled by exposure ratio 1/4).
- FAIL (F2): count above the null band at matched exposure — Garwood CI lower bound > 1
  (excess factor CI excludes 1 from below), per the record's F2.

## 7. EXECUTOR-DERIVED competing preregistration (identity-law analysis)

Separated from the frozen spec above: this is the executor's own derivation, preregistered
before any run, so the arms arbitrate between two stated predictions rather than one.

Derivation (pure linear algebra over the pinned trial logic of probe_sbox.c, BATCH-b41ba9):
(i) swapping byte values between c0 and c1 leaves their XOR difference unchanged at every
swapped coordinate (c0'[i]^c1'[i] = c1[i]^c0[i] = c0[i]^c1[i]); (ii) with SBOX = id the
cipher is affine, E(p) = M_r p + k_E, D(c) = M_r^{-1} c + k_D with D the exact inverse of E
(pinned convention, pinidentity roundtrips), so q0^q1 = M_r^{-1}(c0'^c1') = M_r^{-1}(c0^c1)
= p0^p1 for EVERY r, EVERY S, EVERY key. The archived anchor record itself states the r=5
instance: "q0^q1 = M^-1*(c0'^c1') = M^-1*M*(p0^p1) = p0^p1 (The CW[0] ciphertext-byte swap
preserves the XOR difference)" and its empirical check found qdiff==pdiff on 2000/2000
trials. Therefore the harness trial map on differences in the affine limit is the IDENTITY,
and the worker's zero-word-diff rejection makes W = 4 - |A| on every nontrivial trial:

- ID-PRED (harness law, all cells, all r): W = 4-|A| deterministically; P(W>=1) = 1 for
  |A| <= 3 and P(W>=1) = 0 for |A| = 4; trivial-swap exclusion removes exactly
  d in ker(Z_{CW[S]} M_r restricted to the active domain) (measure 2^{-rank} at |A|=|S|=1).
- Relation to the census object: T_{r,S}(d) = M_r^{-1} Z_{CW[S]} M_r d is the COMMON
  one-sided perturbation q0^p0 = q1^p1 (each decrypted-swapped endpoint vs its own
  plaintext), NOT the pair difference q0^q1 measured by the instrument. The two objects
  induce the same W-count exactly in cells where T_{r,S}(d) vanishes on precisely the
  inactive PW words for every active-supported d (the anchor cell is committed to be one).
- Consequence preregistered for the fixture arm: if the picked NULL-predicted cell has
  |A| <= 3, this analysis predicts the arm reads W_ge1 = nontrivial_trials (excess factor
  ~2^30, Garwood CI lower bound >> 1) and the record's F2/derivation-defect branch of the
  decision rule fires ("ANY measured cell disagreeing with its exact prediction -> F1/F2
  fires, all readings VOID as instrument/derivation defect"). If the picked cell is
  |A| = 4, this analysis predicts 0 hits (inside the null band; census and identity law
  then agree to within the band and the fixture is non-discriminating — disclosed).
- This preregistration asserts nothing about the census TABLE itself (an exact mathematical
  object computed honestly whatever it contains); it predicts only what the HARNESS arm
  will read, and which branch of the record's decision rule the comparison enters.

## 8. Build/run plan

Fresh code under src/ (no AES round content — no S-box table, no AES KAT, no key-schedule
SubWord table — in the census path; SR/MC probe-geometry constants disclosed in
INDEPENDENCE_AUDIT.md with source citations):

- src/census.py — fresh census implementation. Builds SR and MC as explicit 128x128 GF(2)
  permutation/linear matrices from the pinned geometry constants, M_r = SR.(MC.SR)^{r-1} by
  GF(2) matrix product, M_r^{-1} by Gauss-Jordan (cross-checked against the decrypt-path
  matrix D_r = (ISR.IMC)^{r-1}.ISR and against M_r^{-1} M_r = I), T = M_r^{-1} Z M_r,
  word maps, GF(2) ranks, all 16 kernel-intersection dimensions, Mobius-exact W histogram,
  exact-rational P, labels, r*_aff, trivial-exclusion ranks. Zero cipher evaluations.
- src/anchor_check.py — INDEPENDENT anchor recomputation (record baseline_embedding:
  "rank quadruple 32,0,0,0 recomputed independently of the census code"): different
  construction path — byte-level simulation of the pinned round functions on basis vectors
  (the archived algebra_rank.py's method class, re-derived fresh), NOT census.py's matrix
  products; verifies D_5 M_5 = I, computes BOTH the record's census object ranks
  (T_{5,{0}} word maps) and the archived object's ranks (P_j (D.M) P_0^T), plus a
  byte-level empirical identity-law check (real identity key schedule, multiple cells,
  qdiff==pdiff and W==4-|A| counters). This is RUN 1 and is BLOCKING per F1.
- src/affprobe.c — affine oracle for the arms: adaptation of the campaign probe lineage
  (BATCH-b41ba9 probe_sbox.c, itself from BATCH-713991 probe.c / BATCH-002 pinned
  convention), with the AES S-box construction, random-S-box path, and FIPS KAT pin REMOVED
  (no AES content in the affine oracle); identity S-box only; trial worker, RNG, round
  functions, geometry, and arm JSON schema kept identical to the pinned instrument
  (instrument semantics must not drift; disclosed in INDEPENDENCE_AUDIT.md). Modes:
  pinidentity (roundtrips r=1..10), geom, arm.
- src/analysis.py — decision arithmetic: Garwood CIs (regularized incomplete gamma inverse,
  mechanism of the campaign frozen comparator as implemented in BATCH-015's analysis.py —
  disclosed reuse of statistical convention, verified against its published figures
  garwood(1,1)=[0.025,5.572] and the 14-vs-1 exact test), excess factors, census-vs-harness
  comparison per measured cell, application of the record's decision rule. Pure arithmetic
  on already-written run JSONs; not a run.

Run ledger (maximum 8; each binary invocation producing a measurement output = 1 run;
analysis.py is arithmetic on existing files, per BATCH-015 precedent):

- RUN 1 (BLOCKING): python3 src/anchor_check.py -> runs/anchor_recompute.json (+.err,
  .timing.txt). Gate: ranks(T-anchor) == 32,0,0,0 and P(hit)=1.0, D.M=I, empirical
  identity-law check. FAIL -> HALT per F1: document divergence, report infra, no further
  cells or arms.
- RUN 2: python3 src/census.py -> runs/census.json; sha256 digest + UTC timestamp written
  to runs/census_digest.txt immediately after, BEFORE any arm runs (record's
  committed-digest-before-measurement discipline, V-804-2; the commit itself is the
  Coordinator archive task's job — this task does not commit).
- RUN 3: ./src/affprobe pinidentity <seed> -> runs/pinidentity.json (roundtrip pin before
  any arm, archived practice).
- RUN 4: ./src/affprobe arm CAL 5 1 1 20 <seed> 900 8 identity -> runs/arm_CAL.json
  (2^20 calibration in the anchor cell before the frozen arms, archived practice).
- RUN 5: ./src/affprobe arm ANCHOR-P30 5 1 1 30 189001301 301 8 identity ->
  runs/arm_ANCHOR-P30.json (PR-1 anchor arm, 2^30).
- RUN 6: ./src/affprobe arm FIXTURE-P30 <r> <amask> <smask> 30 189001301 302 8 identity ->
  runs/arm_FIXTURE-P30.json (fixture arm at the picked NULL cell; cell pick written to
  runs/fixture_pick.json BEFORE this run).
- Then: python3 src/analysis.py -> runs/decision_analysis.json; RESULTS.json last.

Determinism: all runs deterministic from stated seeds; per-thread seeding identical to the
lineage formula; 8 threads used (task card permits 8 if determinism preserved — the
lineage's per-thread seed formula is a fixed function of (seed, armid, thread index), so
thread count is part of the deterministic specification and is recorded in every arm JSON).
Every run wrapped with /usr/bin/time -l -> runs/<name>.timing.txt; stderr -> runs/<name>.err.

Halt discipline: binding stop 2026-09-01T18:47:29.512413Z; halting at the stop is full
compliance (rule 5); dropped work is SCOPE, never an answer (rule 8). If the budget forces
a halt, RESULTS.json records exactly what completed and the halt reason; a budget halt is
resource_exhaustion, never a reading (record decision rule).

## 9. Constraints restated

- Toy tier. r<=10 AES-shaped SPN probe geometry, SBOX=id arms only; nothing about deployed
  AES; no comparison to published cryptanalysis in either direction.
- No git add / commit. Writes only inside
  coordination/goals/GOAL-AES-003/batches/BATCH-803af6/tasks/TASK-20260901-3dffdc/.
- No hypothesis-status interpretation, no evidence strength, no promotion.
- Every structured artifact parses (checked and stated inside each).
- Inference block on every structured artifact (below).

## 10. Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    session-backend transport under inference amendment DEC-20260831-0d1eeb
    (standing basis 0137a051eb5828789eb267fa83c8278086578d4c)
  degraded_requirements: []
  amendment: DEC-20260831-0d1eeb
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```
