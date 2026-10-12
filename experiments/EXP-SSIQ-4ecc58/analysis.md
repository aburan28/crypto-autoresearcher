# Analysis — EXP-SSIQ-4ecc58 / H-SSIQ-d724f2

Review plan: `experiments/EXP-SSIQ-4ecc58/review/review-plan.yaml`
(`REVIEW-SSIQ-4ecc58-20261003`). Review task: `TASK-20261003-b37591`.
Producer: `TASK-20261003-7277b1` at commit
`cc4bb30dc99d0ff82fbae59622a7bdf381b41ad5`. Approval:
`DEC-20261003-9f9c4f`. Evidence: `EV-SSIQ-3efbe0`. Decision:
`DEC-20261003-3be607`.

Class: heuristic-validation census. No attack. No exponent.

---

## Observation

**Validity.** Two runs, both `status: completed_valid`, receipts
`output_validated`, `returncode: 0`, `check_returncode: 0`,
`check.stdout.log` = `OK`. Run count 2 is within `maximum_runs: 4`.

| Run | Stage | Raw outcome | Receipt |
| --- | --- | --- | --- |
| `RUN-SSIQ-ca745b` | 0 | `O-STAGE0-OK` (`fixtures_ok`, `twin_ok`) | `output_validated`, rc 0 |
| `RUN-SSIQ-1820e6` | 1 | `O-CLOSED`, `n_readable: 2`, `artifact_flags: []` | `output_validated`, rc 0 |

`RUN-SSIQ-1820e6/raw-result.json` matches `RESULTS.md`: outcome
`O-CLOSED`; `claims.break: false`; `claims.exponent_move: false`.
Stdout is `{"outcome": "O-CLOSED", "stage": 1}`. Amazon Bedrock:
`NOT_USED`. `certificate.kind: none` on both manifests. No solve or
relation is claimed.

**Readability** (archived `stage1/panels.json`; a cell is readable iff
`p_gt_N4` and `twin_ok` and `iso_ok` and not `undetermined`).
`5^4 = 625` and `7^4 = 2401`, computed independently of the package.

| Cell | p > N^4 | twin_ok | iso_ok | undetermined | readable | \|H\| | index | ab_sl | R_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `p1031_N5` | 1031 > 625 | true | true | false | yes | 480 | 1 | 1 | 4 |
| `p2063_N5` | 2063 > 625 | true | true | false | yes | 480 | 1 | 1 | 4 |
| `p1031_N7` | 1031 > 2401 is false | true | true | false | no | 1008 | 2 | 1 | 3 |
| `p2063_N7` | 2063 > 2401 is false | true | true | false | no | 1008 | 2 | 1 | 3 |

`n_readable = 2`. Both readable cells have `index = 1` and `ab_sl = 1`.

**Group order.** Standalone arithmetic, without importing the experiment
package: `|GL_2(F_q)| = (q^2-1)(q^2-q)`. For `q = 5`, `24 * 20 = 480`.
For `q = 7`, `48 * 42 = 2016`. Archived `|GL2_S|` equals those orders.
Index is `|GL2_S| / |H|`: `480/480 = 1` on the N=5 cells and
`2016/1008 = 2` on the N=7 cells.

**Controls.** Cayley Z/12: `abelian`, `full`, `twin_ok`, `order: 12`.
Iso fixture: `one_is_I: true`, `det_bad: 0`. Spine arm abelian and
twin-ok on all four cells. `artifact_flags: []`.

**Replay.** `implementation/run.py --help` exposes `--stage {0,1}`,
`--trial-plan`, and `--run-dir`. Stage 1 was replayed from a copy at
`/tmp/review-ssiq-4ecc58` (implementation, frozen `stage0/`, and
`trial-plan.json` only). Command:

```text
python3 /tmp/review-ssiq-4ecc58/implementation/run.py --stage 1 \
  --trial-plan /tmp/review-ssiq-4ecc58/trial-plan.json \
  --run-dir /tmp/review-ssiq-4ecc58/replay-run
```

Stdout: `{"outcome": "O-CLOSED", "stage": 1}`. Regenerated
`stage1/panels.json` sha256
`7ff72998ed07205b26ba7296a58678162cd35a5ec1cc1284e719d2f1c3a51956`
matches the archive. `control-table.json` sha256
`5005ed552e3c12e720a85c0131840e02ab5c1105981c3cd2bc5145a9a236c523`
matches. `RESULTS.md` matches. The in-tree stage files were not
rewritten. Replay `raw-result.json` `wall_clock_seconds` is
`15.924066543579102`; the archived stage-1 raw value is
`14.18135118484497`. That is the only difference.

---

## Comparison

Against the frozen formula in `stage0/preregistered-predictions.json`
and `H-SSIQ-d724f2` outcome `O-CLOSED`: every readable cell has index 1
and `|(H ∩ SL_2)^{ab}| = 1`. The two readable cells are `p1031_N5` and
`p2063_N5`. The N=7 rows fail `p > N^4`, so they stay outside the
label. Their index 2 with `ab_sl = 1` is not the `O-OPEN` band (that
band wants an extra abelian quotient on a readable cell) and is not
relabelled `O-OPEN`.

The coordinator prior in the review plan expected this reading. The
replay and the archived panels agree with it. Cayley and spine controls
hold, so the proves-too-much objects (a non-abelian Cayley/spine key;
`O-CLOSED` covering the N=7 cells; a memory-exponent move) do not fire.

---

## Inference

`O-CLOSED` is the correct label for the two readable N=5 cells under
the frozen S-smooth generating set, on this pure-Python instrument, at
`p ∈ {1031, 2063}`. `|H| = 480` fills `|GL_2(F_5)|`, so the measured
index is 1, and `ab_sl = 1`, `R_max = 4`. Strength is preliminary: one
producer package, two readable cells, coordinator-owned joints (PD-1).
`claim_tier: toy`. `proof_status: empirical_only`. Hypothesis
`approved → supported`. Experiment `approved → analyzed`.

---

## Limitation

The supported sentence is those two cells. The N=7 rows (`|H| = 1008`,
index 2, `ab_sl = 1`, `R_max = 3`, `p_gt_N4` false) are reported and
are not in the label. The generating set is the frozen S-smooth set
(reduced norms `2^a 3^b` with `a+b ≤ 12`), not the full S-unit group.
Heuristic H1 for all large `p` is not proved. PD-1: one coordinator
task owns J1, J2, and J3; there is no separate validator or red-team.
No exponent. No transfer to all large `p`. No memory-exponent claim.
No Deuring Stage 2.
