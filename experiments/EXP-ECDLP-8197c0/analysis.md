# Analysis: EXP-ECDLP-8197c0 (H-ECDLP-df33b3)

Review plan: `experiments/EXP-ECDLP-8197c0/review/review-plan.yaml`
(`REVIEW-ECDLP-8197c0-20261004`), committed as
`8836ce59c3fe9413d30497035b6df0321bcb3ab2` before this analysis.
PD-1: `experiments/EXP-ECDLP-8197c0/review/addendum-pd1.yaml`.
Producer: TASK-20261003-a28582. Approval: DEC-20261003-c8da17.
Execution code: `fc4a09b5a4225379ea74c2942daba3ba3810b8ee`.
Decision: **refine**. Direction: **neutral**. Strength: **inconclusive**.
The pre-registered remainder under the one-predictor reading is
**O-INCONCLUSIVE** (D1 pass, not floor, not concentration).
RESULTS.md is left as the producer wrote it. No exponent. No discrete
log. No transfer to field_bits {16, 20, 24} or cryptographic p.
Amazon Bedrock not selected. No Magma, Sage, or AUXIN.

## Observation

**Validity.** Two runs: RUN-ECDLP-e85bc9 (Stage 0) and RUN-ECDLP-d953db
(Stage 1). Both manifests are `completed_valid`. Both receipts are
`output_validated` with `returncode` 0 and `check_returncode` 0.
`code.dirty` is null. `code.commit` is
`fc4a09b5a4225379ea74c2942daba3ba3810b8ee`. `certificate.kind` is
`none` on both. `claims.break` and `claims.exponent_move` are false.
Amazon Bedrock is NOT SELECTED. Stage 0 `worksheet_ok` is true and
`selfchecks_all_pass` is true, including `S0-4_D1_break`,
`S0-5_D2_break`, and `S0-6_no_passthrough`. Stage 1 `n_cells` is 260
and the archived `outcome` string is `O-FLOOR`.

**Blind maxima from `stage1/ladder.json`, before any implementation
read.** 260 cells. Families `popcount`, `x_interval`, `x_residue`.
Predictors `legendre_x`, `legendre_y`, `one`, `x_lsb`. Field bits
8, 10, 12.

The `(x_residue, x_lsb)` max ratio is 0.0 at field_bits 8 (3 cells),
10 (4 cells), and 12 (4 cells). Every one of those 11 cells is
`weil_informative` true, `spike_obj` 0.0, `spike_null` positive, and
`C` null. That max is outside [0.5, 2]. No other one-predictor group
max is outside [0.5, 2].

Family maxima, the max over predictors at each size, sit inside
(0.5, 2). None is >= 4.

| family | bits 8 | bits 10 | bits 12 |
| --- | --- | --- | --- |
| popcount | 1.5866141979756514 | 1.32125029725501 | 1.4304476160915873 |
| x_interval | 1.9996987467834753 | 1.5824944801716068 | 1.9989320705647282 |
| x_residue | 1.8883074294190805 | 1.405333858267348 | 1.4777556335393698 |

D1 in `stage1/d1-control.json` and `ladder.json` extra passes at
field_bits 8, 10, and 12 with `eps_at_q` 1.0.

**Replay.** A copy at `/tmp/review-ecdlp-8197c0` ran Stage 1 into
`/tmp/review-ecdlp-8197c0-run`. Outcome `O-FLOOR`. `check.py` printed
`PASS` and exited 0. Stage 2 was not launched. The repository
experiment directory was not written by the replay.

## Comparison

Three frozen sentences name the scored quantity, and they do not name
the same set.

- `stage1/decision-rules.json`: O-FLOOR is "all bounded-degree
  one-predictor max ratios in [0.5, 2] at every size". The recorded
  outcome string is `O-FLOOR`. The recomputed `x_residue` × `x_lsb`
  max is 0.0 at every approved size, so this sentence is not met.
- `specification.yaml` `outcome_table`: O-FLOOR is "every
  bounded-degree family ratio in [0.5, 2] at every size; D1 pass".
  The family maxima above sit in that band, and D1 passes.
- Hypothesis FLOOR clause: every bounded-degree family on the ladder
  has spike ratio to the equal-size random subset in [0.5, 2] at every
  approved size. Same family aggregate.

No frozen sentence outside `implementation/` excludes `x_lsb`, a ratio
of 0, or a null `C` from the scored set. The family sentences score a
coarser maximum. They do not drop the 0.0 cells. The only "not scored"
sentence outside `implementation/` is the D2 discrete-log interval.
Under the one-predictor reading those 0.0 cells stay inside the scored
set.

D1 passed. No family max is >= 4, so O-CONCENTRATION is not met and a
ratio of 0 is not the stated falsifier. The pre-registered remainder
in the outcome table is O-INCONCLUSIVE: D1 pass, and neither floor nor
concentration. The archived word O-FLOOR does not match the
one-predictor sentence. The temp replay still emits O-FLOOR, which
confirms the instrument and does not repair the prose.

## Inference

The package is a valid toy measurement. It does not license support of
E-FLOOR, because the one-predictor decision-rules sentence is unmet and
no frozen exclusion of the 0.0 cells was quoted. It does not license
support of E-CONCENTRATION, weaken, or reject_scoped: no family ratio
>= 4 was measured. The decision is refine. Direction is neutral.
Strength is inconclusive. `claim_tier` is toy. `proof_status` is
`not_applicable`. H-ECDLP-df33b3 stays `approved`. EXP-ECDLP-8197c0
moves from `approved` to `analyzed`. A later protocol must name the
scored set in the frozen prose before any relabel. This package does
not authorize a new curve search, Stage 2, or field_bits >= 16.

## Limitation

One toy package at field_bits {8, 10, 12}, one curve per size. PD-1:
one coordinator task owns J1, J2, and J3; there is no separate
validator or red-team. `certificate.kind` is none. No discrete
logarithm was recovered. No exponent is claimed. Nothing here transfers
to field_bits {16, 20, 24} or to cryptographic p. The replay confirms
that the instrument still prints O-FLOOR; it does not decide which
English sentence is the scored set. Strength is below replicated, so
no KN-FIND is promoted.
