# PREREGISTRATION.md — TASK-20260901-f5d3a4 (executor, BATCH-fe0bdc, GOAL-AES-003)

Frozen spec: `ledger/proposals/IDEA-20260901-04606c.yaml` (read whole before this file was
written). This file is written BEFORE any run output exists (mtime-gated; budget_stamps.jsonl
start stamp is the only earlier file, as the budget clock is the mandated first act). Sections
1–4 below are VERBATIM copies from the idea record; section 5 is the executor's build/run plan.
The frozen cell set is CLOSED: any cell added after data is seen is post-hoc and VOID.

## 1. GATE 0 requirements (verbatim from the idea record)

From `predictions` PR-0:

> GATE 0 - anchor cell under the repaired object, fresh code (ranks; D_5 M_5 = I_128
> both directions; exact P(W>=1 | nontrivial) from word maps; 1000 keyed trials)
>
> Ranks exactly (32,0,0,0); D_5 M_5 = M_5 D_5 = I_128; P = 1.0 exact; 1000/1000
> q0^q1 = p0^p1 and W=3 on 100% of nontrivial trials. BLOCKING and FIRST: any
> deviation halts the task as derivation/convention/implementation defect (F1), never
> a negative observation. This gate caught the voided object; it must pass before any
> other census cell is read.

From `proof_search_map.baseline_embedding.reproduction_check`:

> GATE 0, BLOCKING, FIRES BEFORE ANY OTHER CENSUS CELL IS READ. Fresh implementation:
> (a) D_5 M_5 = I_128 and M_5 D_5 = I_128 via byte-level basis-vector simulation
> independent of the census matrix-product code (anchor_check.py pattern); (b) ranks
> of A_{5,{0},j} exactly (32,0,0,0); (c) exact P(W>=1 | nontrivial) = 1.0 derived
> from the word maps (word-0 map identity on nonzero inputs, words 1..3 zero maps);
> (d) 1000 keyed trials: q0^q1 = p0^p1 on 1000/1000 and W=3 on 100% of nontrivial
> trials. Any failure halts: invalid_measurement, never negative evidence (rule 5).
> This is exactly the check that voided ec54fe's object.

From `falsification_conditions` F1:

> F1 (BLOCKING, GATE 0). Any Gate 0 component fails - ranks not (32,0,0,0), D_5 M_5 !=
> I_128, derived P != 1.0, or keyed anchor trials deviate. Instrument/convention/port
> defect; every prospective census reading VOID; the run returns invalid_measurement,
> never evidence against the skeleton. This is the check that caught the voided object,
> placed first by design.

Repaired census object at the anchor (record `claim` P1, ANCHOR REDUCTION):

> at the anchor cell (r=5, A={0}, S={0}),
> A_{5,{0},j} = P_j (D_5 M_5) P_0^T, symbol-for-symbol the archived algebra_rank.py
> object. With D_5 M_5 = I_128 (archived-verified, fresh-code re-verified by producer and
> validator), A_j = P_j P_0^T: the 32-bit identity for j=0, the zero map for j=1,2,3.
> Ranks 32,0,0,0. The per-trial law follows: the word-0 input is conditioned nonzero by
> the rejection rule, the word-0 map is the identity so its output never vanishes, and
> words 1..3 vanish identically: W = 3 and P(W>=1) = 1.0 exactly on every nontrivial
> trial - the archived anchor reading (EV-AES-048545 O-7: ranks 32,0,0,0, E[W>=1] = 1.0,
> measured ratio 1.0000000000002). The reduction is an equality of expressions, not a
> numerical coincidence: the repaired object IS the archived object at the anchor.

## 2. Census table over the frozen 100-cell set (verbatim from the idea record, PR-1)

From `predictions` PR-1 `metric`:

> Census table over the frozen set C (ten cells) x r=1..10, committed as a digest
> before the fixture arm

From PR-1 `minimum_effect`:

> All 100 cell-instances equal the pre-registered flat law: rank pattern 32 x [j in
> A]; W = 4-|A| deterministic; P(W>=1 | nontrivial) = 1 for |A|<=3; P(W>=1) = 0 for
> |A|=4; D_r M_r = I_128 in both directions for every r; and rho equal to this table
> (rows = cells, entries = rho at r=1..10):
>
>     (A={0},S={0}):        8,32,8,32,32,32,32,32,8,32
>     (A={0},S={1}):        8,0,8,32,32,32,32,32,8,0
>     (A={0},S={2}):        8,0,8,32,32,32,32,32,8,0
>     (A={0},S={3}):        8,0,8,32,32,32,32,32,8,0
>     (A={1},S={1}):        8,32,8,32,32,32,32,32,8,32
>     (A={2},S={2}):        8,32,8,32,32,32,32,32,8,32
>     (A={3},S={3}):        8,32,8,32,32,32,32,32,8,32
>     (A={0,1},S={0}):      16,32,16,32,32,32,32,32,16,32
>     (A={0},S={0,1}):      16,32,16,32,32,32,32,32,16,32
>     (A={0,1,2,3},S={0}):  32,32,32,32,32,32,32,32,32,32
>
> Rho=0 cells (r=2 and r=10, A={0}, S in {1,2,3}) are DEGENERATE: every trial is
> trivial, the instrument sees zero nontrivial trials, and the per-trial conditional
> law is vacuous there (the unconditional identity law still holds on every trial).
> The table values are this record's derivation (verified in the throwaway port); the
> executor recomputes fresh - any mismatch is F3, table void. The table is the
> deliverable even if no measurement arm runs.

Frozen cell set C (record `claim` P2, inherited UNCHANGED from ec54fe; the record counts
the set — ten cells):

> (A={0},S={0}), (A={0},S={1}), (A={0},S={2}),
> (A={0},S={3}), (A={i},S={i}) for i=1,2,3, (A={0,1},S={0}), (A={0},S={0,1}),
> (A={0,1,2,3},S={0}) - ten cells, at every r in 1..10 (100 cell-instances; ec54fe's
> prose said eight, its set lists ten; this record counts the set).

Object computed per cell-instance (record `object`):

> the census object per cell is the word map A_{r,S,j} = P_j . (D_r M_r) . Pi_A from
> active-word differences to PW[j], where Pi_A embeds PW[A] and P_j projects PW[j].
> ... Since D_r M_r = I_128, A_{r,S,j} = P_j Pi_A: rank 32 for j in A, rank 0 for j
> not in A; W = 4-|A| on EVERY trial (trivial or not); P(W>=1 | nontrivial) = 1 for
> |A|<=3; P(W>=1) = 0 for |A|=4. The census is FLAT over r by construction. The only
> per-cell structure the affine limit retains is the trivial-swap map tau_{r,A,S} :
> d|PW[A] -> (M_r d)|CW[S], whose rank rho gives the trivial-trial probability 2^-rho.

The census additionally re-verifies D_r M_r = I_128 in both directions for every r in
1..10 as a per-r port guard (record P2). The census is pure sparse GF(2) algebra with
zero cipher evaluations.

## 3. Keyed bridge predictions (verbatim from the idea record, PR-2)

> Keyed bridge: five pre-registered cells x 500 fresh keyed trials - (r=5,A={0},S={1}),
> (r=6,A={0},S={0}), (r=2,A={0},S={0}), (r=5,A={0,1,2,3},S={0}), (r=2,A={0},S={1})
>
> q0^q1 = p0^p1 and W = 4-|A| on 100% of trials in every cell; the structure-destroyed
> cell shows W=0 on 500/500 (known-false control: zero hits on the affine cipher);
> the degenerate cell (r=2,A={0},S={1}) shows trivial swaps on 500/500 trials (the
> rho=0 prediction). Any deviation is a defect verdict (F2/F3 class), never a
> mechanism reading.

## 4. Fixture-arm prediction (verbatim from the idea record, PR-4)

> FIXTURE ARM (one arm, only after Gate 0 passes and the census digest is committed):
> affine cipher, cell (r=6, A={0}, S={0}), fresh implementation, 2^30 trials
>
> KNOWN-ANSWER PREDICTION: W=3 on 100% of nontrivial trials; hit count 2^30 - T with
> T the realized trivial count, E[T] = 2^30 x 2^-rho = 0.25 (rho=32 in this cell),
> acceptance band hits >= 2^30 - 8 (Poisson margin >7 sigma over E[T]); excess ratio
> 1.0 +/- 2^-20 against frozen excess_E = 2^30. This is the census-predicted-ALIVE
> cell at AES's measured death round: confirming it at scale is the empirical content
> of MISMATCH-ALIVE. A nontrivial trial with W != 3, or hits below the band, is F2 -
> the pipeline manufactures a deviation from a theorem on a known-affine object; the
> instrument is indicted and the task escalates to the 02f7c4 battery and independent
> review. A MISMATCH here is never evidence against the identity law (rule 5).

## 5. Pre-registered decision rule (verbatim from the idea record)

> Committed before Stage 1 runs. (CONFIRMED-MISMATCH-ALIVE) Gate 0 passes AND the census
> recomputes exactly flat with the pre-registered rho table AND the keyed bridge is 100%
> AND the fixture arm lies inside its band -> record the toy-tier conclusion "the pinned
> instrument's affine-limit trial map is the identity (flat census); the skeleton is
> alive at every r <= 10 including r=6 where AES is measured dead; the death round is not
> carried by the linear skeleton and is nonlinearity-driven", citing this record's
> artifacts plus EV-AES-048545, EV-AES-64750e, and EV-AES-d33b1c; the residual question
> (magnitude ~15x, nine-order gap) routes to IDEA-20260901-bcb117 with the carrier e =
> (q0^q1)^(p0^p1) named, and IDEA-20260901-69912d consumes the flat census (with the
> disclosed consequence below). (GATE FAIL) any Gate 0 component fails -> halt, all
> prospective census readings VOID, invalid_measurement, repair dispatched, no mechanism
> conclusion (F1). (CENSUS FAIL) census recomputation disagrees with the pre-registered
> table -> table void, halt, convention/port defect (F3). (PIPELINE FAIL) keyed bridge or
> fixture arm deviates -> instrument indicted (F2), escalate to 02f7c4 battery +
> independent review, no mechanism conclusion. A budget halt is resource_exhaustion,
> never a reading.

## 6. Executor build/run plan (this task; budget 3600 s wall, max 6 runs)

Code (all fresh; references used for DEFINITIONS ONLY: BATCH-803af6 TASK-20260901-3dffdc
src/census.py + src/anchor_check.py + src/affprobe.c, BATCH-b41ba9 TASK-20260806-47f217
algebra_rank.py + probe_sbox.c, campaign arm conventions of BATCH-014/BATCH-015):

- `src/gate0.py` — Gate 0 (BLOCKING): byte-level basis-vector simulation builds M_5, D_5;
  checks (a) D_5 M_5 = I_128 and M_5 D_5 = I_128, (b) ranks of A_{5,{0},j} = P_j(D_5 M_5)P_0^T
  == (32,0,0,0) with the word maps checked COLUMN-EQUAL to the identity/zero maps, (c) exact
  P(W>=1 | nontrivial) = 1.0 derived from those maps, (d) 1000 fresh keyed trials
  (seed 2026090104606c) with q0^q1 = p0^p1 and W=3 checks. Exits 5 on any failure -> HALT.
- `src/census046.py` — Stage 0 census: fresh sparse GF(2) code; M_r = SR.(MC.SR)^{r-1},
  D_r = (ISR.IMC)^{r-1}.ISR built from explicit SR/ISR/MC/IMC matrices (my own construction),
  per-r guard D_r M_r = M_r D_r = I_128 both directions; for each of the 100 cell-instances
  computes the 4 word maps of A_{r,S,j} = P_j (D_r M_r) Pi_A on basis vectors, checks column
  equality against P_j Pi_A, derives rank pattern / W / P(W>=1), and computes
  rho = rank(d -> (M_r d)|CW[S]). Compares every value against section 2's pre-registered
  table; writes runs/census.json and prints its sha256 digest. Frozen cell set hard-coded and
  CLOSED; the program has no mechanism to accept another cell.
- `src/bridge.py` — Stage 0.5 keyed bridge: the five PR-2 cells, 500 fresh keyed trials each
  (seed 46060901b), exact identity-law and W checks on every trial, trivial-swap counts,
  W=0 count for the structure-destroyed cell, trivial count for the degenerate cell.
- `src/affarm046.c` — Stage 1 fresh C implementation of the affine trial instrument:
  splitmix64 RNG, FIPS-197-shaped key expansion using a global S-box, pinned round functions
  (column-major state, sub_shift/inv_sub_shift, mix_columns/inv_mix_columns with xtime 0x1b,
  enc_r/dec_r round order), PW/CW geometry, verbatim trial worker semantics (re-randomise
  active words, zero word-diff rejected, CW[S] swap with trivial detection, Z/W counters),
  pthreads with the campaign per-thread seed formula. Modes: `pin` (FIPS-197 C.1 KAT + the
  BATCH-003 r=5/r=10 anchor ciphertexts under the AES table — the convention-drift control),
  `pinidentity` (identity-table bijectivity + r=1..10 roundtrips), `geom`, and `arm`
  (identity sbox ONLY; any other sbox token refused). KAT pins and the source-diff audit of
  the round functions against the campaign build are recorded in INDEPENDENCE_AUDIT.md per
  the record's confounders control.
- Calibration before the frozen arm: double-run determinism check (identical config twice,
  byte-identical receipts) and an exact Python replication of a small 1-thread arm stream
  (same splitmix64/key/thread-seed formulas) to tie the C worker to the Gate-0/bridge Python
  semantics; rate measurement to size the thread count (4 baseline, 8 allowed if determinism
  preserved).
- `src/analyze.py` — decision_analysis.json: applies the section-5 decision rule to the run
  receipts; Poisson band check hits >= 2^30 - 8, excess ratio vs frozen excess_E = 2^30,
  census-digest re-verification after the arm (file unchanged), preregistration mtime ordering
  check, parse attestation of every JSON artifact.

Run sequence (each stamped in budget_stamps.jsonl):
1. RUN 1: `python3 src/gate0.py runs/gate0.json` — BLOCKING; exit != 0 halts the task.
2. RUN 2: `python3 src/census046.py runs/census.json` — census + digest (before the arm).
3. RUN 3: `python3 src/bridge.py runs/keyed_bridge.json`.
4. RUN 4: build affarm046 + `pin` + `pinidentity` + `geom` + calibration/determinism +
   Python cross-check -> runs/build_pin_cal.json, runs/source_diff.txt.
5. RUN 5: fixture arm `affarm046 arm FIXTURE-R6-A0-S0 6 1 1 30 <seed> 1 <threads> identity`
   under /usr/bin/time -l -> runs/fixture_arm.json (+ .timing.txt, .err).
6. RUN 6: `python3 src/analyze.py` -> runs/decision_analysis.json, runs/parse_check.txt;
   RESULTS.json written last.

Halt semantics: any Gate 0 failure -> invalid_measurement halt (F1), no census cell read.
Census-vs-table mismatch -> F3 halt (census-mismatch verdict arm). Bridge/arm deviation ->
F2 defect verdict. Budget stop -> resource_exhaustion, never a reading; halting at the stop
is full compliance.

Digest-commit discipline (V-804-2): the executor is forbidden to `git add`/commit (task
constraint), so the census table + code + digest are FINALIZED as write-once run files before
the fixture arm launches (runs/census.json written in RUN 2, digest recorded in RUN 2's
stdout and re-verified byte-for-byte in RUN 6 after the arm), and git commitment of the
package is performed by the snapshot archiver TASK-20260901-e5a72d, which commits the exact
declared inventory before any independent validator reads it. Disclosed adaptation, not a
deviation from the decision rule: the arm cannot influence a file finalized before it runs.

Seeds (pre-declared, recorded in every receipt): Gate 0 keyed trials 2026090104606c; bridge
46060901b; fixture arm seed 46063001, arm_id 1.

Claim tier: TOY throughout. 64/128-bit toy probe geometry only; nothing about deployed AES;
no comparison to published cryptanalysis in either direction (RQ-AES-003 R3). No hypothesis
status, evidence strength, or promotion is interpreted by this task.

## 7. Inference block (every structured artifact of this task)

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

Parse attestation: every JSON artifact produced by this task is parsed whole with
python3 json.load before task completion and this is stated inside each artifact.
