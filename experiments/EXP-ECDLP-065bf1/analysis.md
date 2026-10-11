# Analysis EXP-ECDLP-065bf1

Review task TASK-20261003-7d9ed0. Producer commit
`61d9f673a8ea84c9a8950df216566ce0a5e730a9`. Approval
DEC-20261003-c6641c. Hypothesis H-ECDLP-0fd4b9. Runs
RUN-ECDLP-cf076a (stage 0) and RUN-ECDLP-d38476 (stage 1).

Toy curve only: `y^2 = x^3 + x + 1` over `F_17`, `G = (0, 1)`,
`k ∈ {2, 3}`, `null_seed = 2026100303`. No exponent. No discrete-log
solve.

## Observation

Two archived runs, both `completed_valid`, both with
`certificate.kind = none`, `claims.solve = false`,
`claims.break = false`, `claims.exponent_move = false`, and
`amazon_bedrock: NOT_USED`. `check.py` return code is 0 on both
execution receipts (`check.stdout.log` is `OK`). Source SHA-256 values
in both manifests match the current `implementation/{run,check,elliptic,meters}.py`
bytes. Trial-plan SHA-256 matches `813ff2871d6280cb82a17e5e5d8a1d34ebc2d8b4061b83ad049da8c140b6381a`.
Specification SHA-256 matches `9d1225295ac93e87ac0b29a4b64f3d8eee20607f165daaf991e251b70aeffd6d`.
Run count is 2, inside `maximum_runs = 4`. Receipt artifact hashes
match the committed companions (the receipt's `manifest.yaml` digest
is the producer manifest).

Stage 0, RUN-ECDLP-cf076a, outcome `O-STAGE0-OK`, `fixtures_ok = true`,
`twin_ok = true`. Frozen fixtures: `[2]G = (13, 1)`, `[3]G = (4, 16)`,
`k1_nearby.width = 0` (ceiling `ptm_k1_max_width = 1`).

Stage 1, RUN-ECDLP-d38476, outcome `O-MIXED`. `RESULTS.md` names
`outcome: O-MIXED`. Both cells `toy_f17_k2` and `toy_f17_k3` have
`rep_diff = true`, `incidence_rank_diff = true`, cell `twin_ok = true`,
`perm_iso = true`.

Representation deltas (projective minus affine, absolute):

| cell | n_vars | n_aux | width | max_degree |
| --- | ---: | ---: | ---: | ---: |
| k=2 | 6 | 2 | 0 | 0 |
| k=3 | 9 | 3 | 0 | 0 |

Incidence ranks at identical matrix dimensions, affine versus the
`null_seed + k` random-coefficient clone:

| cell | affine rank | random rank | shape |
| --- | ---: | ---: | --- |
| k=2 | 4 | 5 | 5×5 |
| k=3 | 7 | 8 | 9×8 |

`random_coeff.twin_ok` is false on both cells (`witness_ok = false`).
`presentation_stats` sets its own `twin_ok` to
`width_agree ∧ rank_agree ∧ witness_ok`. The random-coefficient clone
keeps the monomial incidence and replaces coefficients, then evaluates
the original public witness, so the residuals are not all zero and
`witness_ok` fails. The cell gate in `measure_cell` does not use that
flag. Cell `twin_ok` is affine, projective, and permutation `twin_ok`,
plus random `rank_agree` and `width_agree`. Both of those agree, so
cell `twin_ok` stays true while `random_coeff.twin_ok` is false.

k=1 nearby width is 0, which is ≤ 1. Variable-name reversal leaves
`n_vars`, `n_edges`, width, and rank unchanged (`perm_iso = true`).

## Comparison

An in-tree invocation of the frozen command refuses to overwrite
`stage0/preregistered-predictions.json` (`FileExistsError`) and writes
nothing into the experiment directory. The replay that produced an
outcome copied the experiment tree to `/tmp`, deleted only the runner
output files on that copy, and ran:

`python3 implementation/run.py --stage 0 --trial-plan trial-plan.json --run-dir /tmp/review-ecdlp-065bf1-s0`

`python3 implementation/run.py --stage 1 --trial-plan trial-plan.json --run-dir /tmp/review-ecdlp-065bf1-s1`

`check.py` on each `/tmp` run directory printed `OK` and returned 0.
Stage 0 outcome `O-STAGE0-OK`. Stage 1 outcome `O-MIXED`. Regenerated
`stage0/preregistered-predictions.json`, `stage0/fixtures.json`,
`stage1/panels.json`, `stage1/control-table.json`, and `RESULTS.md` are
byte-identical to the archived files. Raw outcomes match the archived
`raw-result.json` files aside from `wall_clock_seconds`.

Independent scalar multiplication, written in this review and not
imported from `experiments/EXP-ECDLP-065bf1/implementation/`, uses the
chord-and-tangent law on `y^2 = x^3 + x + 1` over `F_17` with
`G = (0, 1)`. Double-and-add and repeated addition both give
`[2]G = (13, 1)` and `[3]G = (4, 16)`. Both points lie on the curve.
That matches `stage0/fixtures.json`.

The `decide_outcome` map reads `O-MIXED` when every cell has `twin_ok`
and `perm_iso` and at least one cell has both `rep_diff` and
`incidence_rank_diff`. Both cells fire both differences, so the label
is exactly `O-MIXED`, not `O-REP-SENSITIVE`, `O-INCIDENCE-INSUFFICIENT`,
`O-NO-DIFF`, or `O-ARTIFACT`.

## Inference

The archived label is the frozen contract's reading of these two cells.
H-ECDLP-0fd4b9's scoped diagnostic — public known-scalar forward
presentations, representation `|Δ| ≥ 1` in `{n_vars, width, max_degree, n_aux}`
and incidence rank `|Δ| ≥ 1` at identical dimensions, with twin meters
and permutation control — holds on this curve and these two scalars.

The representation half is the added homogeneous `Z` auxiliaries:
`n_vars` and `n_aux` move, and width and max degree do not. The rank
half is the non-tautological comparison: same incidence, different
coefficients, Jacobian rank 4 versus 5 and 7 versus 8. Greedy width is
an upper bound from the min-fill scan, not treewidth, and its delta is 0.

This supports that scoped toy measurement at strength `preliminary`.
It does not support an attack, a discrete logarithm, or an exponent.

## Limitation

First observation of this instrument on one curve and two public
scalars. Strength is below `replicated` / `strong`, so no `KN-FIND`.
Procedure deviation PD-1: one coordinator task owns J1, J2, and J3;
there is no separate validator session and no separate red-team session.
No transfer to a cryptographic curve. Budget of the approved contract:
1800 seconds, 2 GB, at most 4 runs. Pure Python. `null_seed = 2026100303`.
No solve.
