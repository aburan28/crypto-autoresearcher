# PREREGISTRATION -- TASK-20260802-9dcca8

The wrong-hint null for the hinted r=6 and r=7 constructions of
GOAL-AES-003 BATCH-001.

Written and frozen BEFORE any measurement in this task. Timestamps of
the writing and of first execution are in `budget_stamps.jsonl`.

Standing basis: 0137a051eb5828789eb267fa83c8278086578d4c.
Claim tier: toy. Nothing here asserts anything about full-round or
deployed AES, and nothing here is a comparison to published
cryptanalysis in either direction (RQ-AES-003 R3).

## 1. The object under test

`coordination/goals/GOAL-AES-003/batches/BATCH-001/tasks/attack/sq.c`,
modes `attack6` and `attack7`.

Both modes derive their hint bytes INSIDE the binary from the true key
schedule of the target key:

- `mode_attack6` (sq.c:341-342): `hint[d][t] = rk[rounds][DIAGP[d][t]]`,
  i.e. 3 of the 4 bytes of each inverse-ShiftRows diagonal of the true
  last round key K6.
- `mode_attack7` (sq.c:541-545): K6' = MC^{-1}(K6) is computed from the
  true schedule and 3 of the 4 bytes of each K6' diagonal are handed over
  as `hint`; the full true last round key K7 is also handed over.

Survivor test, both modes (sq.c:392-402 and 584-592): a candidate byte
k3 survives for diagonal d iff for every row r in 0..3 there exists some
k4 with `cand[d][r][k3][k4]` still set after all structures. `cnt` is the
number of such k3; `uniq` is set only if `cnt == 1` for all four
diagonals. `mode_attack7` additionally compares the survivor to the true
K6' byte.

## 2. The two hypotheses this task separates

- **(A) KEY ISOLATION.** The construction isolates the CORRECT byte. The
  unique survivor is unique *because* the integral balance identity holds
  for the true key bytes and generically fails otherwise, so the filter
  carries information about the key.
- **(B) STRUCTURAL SINGLETON.** The filter admits exactly one survivor
  per diagonal for structural reasons independent of the hint's truth,
  and BATCH-001 saw the correct byte only because the hint it was handed
  was correct.

BATCH-001 cannot separate these, because it never ran the filter with a
false hint. Both BATCH-001 reviewers flagged this and neither could rule.

## 3. Arms

Target key is FIXED across all arms and identical to BATCH-001's:
`2b7e151628aed2a6abf7158809cf4f3c`. The oracle always encrypts under the
target key. Only the source of the hint bytes varies.

| arm | mode | nwrong (of 3 hint bytes per diagonal) | hint source |
|---|---|---|---|
| TRUE6 | attack6n | 0 | true key schedule |
| WRONG6-01..08 | attack6n | 3 | 8 distinct independent wrong keys |
| PART6-01..02 | attack6n | 1 | 1 byte from wrong key, 2 true |
| TRUE7 | attack7n | 0 | true key schedule |
| WRONG7-01..08 | attack7n | 3 | 8 distinct independent wrong keys |
| PART7-01..02 | attack7n | 1 | 1 byte from wrong key, 2 true |

In every attack7 arm the last round key K7 stays TRUE, exactly as in
BATCH-001, so the ONLY variable changed is the truth of the K6'/K6 hint.

Structures per trial: 2 (BATCH-001's setting; uniqueness in BATCH-001
appeared only after the second structure). Threads: 4. Distinct seed per
trial; seeds recorded. The TRUE arm is run in this session, on this
binary, with a seed drawn from the same list, so the comparison is
against a number measured here.

The binary is a COPY of sq.c placed in this task's own directory as
`sq_null.c`, with two ADDED modes `attack6n` / `attack7n` that take a
separate hint key and an `nwrong` count. The BATCH-001 file is not
touched. The added modes reuse the unmodified `worker6` / `worker7`
folding code and the unmodified survivor test; the only change is where
`hint[d][t]` comes from, plus richer per-diagonal reporting (survivor
list, true byte, wrong-key byte).

## 4. Predictions (frozen)

Prediction rests on the following count, which is arithmetic, not a
measurement. Per (d,r) there are 2^16 candidate pairs (k3,k4). A pair
that does not satisfy the balance identity passes one structure with
probability about 2^-8, so about 2^-16 after two structures, leaving
about 65536 * 2^-16 = 1 random survivor pair per (d,r) after two
structures. For a given k3 to survive a diagonal it must appear in the
survivor set of all four rows: about 2^-8 per row, about 2^-32 over four
rows, about 2^-24 after summing over the 256 values of k3. Under a false
hint no k3 is algebraically protected.

- **P1 (TRUE6).** cnt == 1 for all 4 diagonals; the survivor equals the
  true K6 byte; `unique` = 1. Reproduces BATCH-001 `attack6b_out.json`.
- **P2 (TRUE7).** cnt == 1 for all 4 diagonals; survivors equal the true
  K6' bytes `8034b976`; `diagonals_correct` = 4.
- **P3 (WRONG6, WRONG7).** cnt == 0 for essentially every diagonal of
  every trial. Expected number of diagonals with cnt >= 1 across all 64
  wrong-hint diagonals (8 trials x 4 diagonals x 2 modes) is of order
  64 * 2^-24, i.e. indistinguishable from zero. Predicted counts: 0
  diagonals with cnt == 1, 0 diagonals with a survivor equal to the true
  byte, 0 diagonals with a survivor equal to the wrong hint key's own
  corresponding byte.
- **P4 (PART6, PART7).** Same as P3: cnt == 0. One false hint byte is
  enough to break the identity.

## 5. Falsification conditions, stated in advance

- **Falsifies (B), supports (A):** WRONG6 and WRONG7 arms yield cnt == 0
  on the overwhelming majority of diagonals while the matched TRUE arms
  in the same session yield cnt == 1 with the correct byte. Under this
  outcome the survivor is not a structural artefact: the filter is
  sensitive to whether the hint is true, and the r=6 / r=7 results stand
  as hint-assisted key isolation (still hint-assisted, still toy tier,
  and for r=6 still dominated -- see section 6).
- **Falsifies (A), supports (B):** WRONG6 or WRONG7 arms ALSO yield
  cnt == 1 per diagonal. Under this outcome the r=6 and r=7 results DO
  NOT DEMONSTRATE KEY ISOLATION, and this task will record exactly that
  sentence, unhedged, in RESULTS.json, together with the observation that
  BATCH-001's `diagonals_correct = 4` was then an artefact of being
  handed the correct hint. This is a legitimate result of the task.
- **Ambiguous / neither:** intermediate outcomes (e.g. cnt == 1 in a
  minority of wrong-hint diagonals, or cnt > 1) are reported as measured
  with the full distribution and are NOT resolved into either hypothesis
  by this task.
- **Partial arm reading.** If PART arms behave like WRONG arms, the
  filter needs ALL hint bytes correct. If PART arms behave like TRUE
  arms, the filter is insensitive to the flipped hint byte, which would
  be a distinct and separately reported finding.

A crash, timeout, or infrastructure failure in any arm is recorded as
that and is NOT counted as cnt == 0 and NOT counted as evidence in
either direction.

## 6. Carried forward unchanged from BATCH-001 / CORR-20260802-003

The r=6 key recovery WORKS AND IS DOMINATED: it requires 12 hint bytes
and, by the package's own measured numbers, costs 69.39 s against roughly
25 s for exhaustive search over the same hinted residual.
`dominated_by`: exhaustive search over the hinted residual.
`sota_delta`: NEGATIVE. This task does not re-measure those two numbers
and reports them as carried-forward BATCH-001 measurements, not as
measurements of this task. The r=7 run is NOT a key recovery and carries
no certificate; K7 is supplied as input.

## 7. Budget and stopping

Wall clock 3000 s from 2026-08-02T17:06:47Z, binding stop
2026-08-02T17:56:47Z. Memory 8 GB. Max 24 runs. Execution order is
decisive-first: build, TRUE6, WRONG6 x8, TRUE7, WRONG7 x8, then the PART
arms only if the clock allows. At the binding stop the task halts, sets
`halted_on_budget: true`, and names the dropped arms. Halting on the
stamp is full compliance.

## 8. Inference block

```json
{
  "policy": "executor-implementation",
  "requested_policy": "executor-implementation",
  "resolved_model_id": "claude-opus-5",
  "fallback_used": true,
  "model_verified": false,
  "model_verification_note": "adapter probe not run in this session; resolved id is the harness-reported model of the executing session, and orchestration/model-policies.yaml aliases are not resolvable under Claude Code (CLAUDE.md model policy note)",
  "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c"
}
```
