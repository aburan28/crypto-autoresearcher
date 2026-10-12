# Analysis: EXP-CERTBIN-0f4599 (H-CERTBIN-a3d441)

Review plan: `experiments/EXP-CERTBIN-0f4599/review/review-plan.yaml`
(`REVIEW-CERTBIN-0f4599-20261003`), written before this analysis.
Addendum: `experiments/EXP-CERTBIN-0f4599/review/addendum-pd1.yaml` (PD-1).
The coordinator prior was not rewritten. Producer: TASK-20261003-c3b10e.
Approval: DEC-20261003-f561a3. Decision: **inconclusive**. Neither E-NULL
nor E-SLICE is kept. No exponent. No KN-FIND. Amazon Bedrock not used.
No AUXIN, Magma, or Sage.

## Observation

**Validity (J1).** Two runs, both `completed_valid`, `code.dirty: false`,
execution commit `82d8e0091dfbf68e0323963515cbcb85b62a5e04`.

| run | stage | outcome | receipt | check |
| --- | --- | --- | --- | --- |
| RUN-CERTBIN-2c8176 | 0 | O-STAGE0-OK | output_validated | returncode 0, stdout `OK` |
| RUN-CERTBIN-3f45ba | 1 | O-INCONCLUSIVE | output_validated | returncode 0, stdout `OK` |

Stage 0 raw fields: order 523492, r 130873, `twin_mul_ok` true,
`twin_add_ok` true, `planted_probe_on_curve` true. Both manifests set
`certificate.kind: none`. Both raw results set `claims.break` false,
`claims.exponent_move` false, `claims.n_ge_131` false,
`amazon_bedrock: NOT_USED`.

Stage 1 raw rows match `RESULTS.md` and `stage1/panels.json`. RESULTS
prints six significant figures; the raw floats are the same values.

| seed | tag | B | C | image | rate(U) | rate(P) | rate(W) | W/U | sw | b |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026100319 | seed_a | 34 | 7140 | 6478 | 0.04949836864746739 | 1 | 0 | 0 | 32 | 1.1021920345785736 |
| 2026100320 | seed_b | 30 | 4960 | 4496 | 0.034353915628128034 | 1 | 0 | 0 | 36 | 1.103202846975089 |

**Blind census identities (J3), computed before `implementation/` was opened.**

| quantity | value |
| --- | --- |
| C(36, 3) | 7140 |
| C(32, 3) | 4960 |
| 4 * 130873 | 523492 |
| 6478 / 130873 | 0.04949836864746739 |
| 4496 / 130873 | 0.034353915628128034 |
| 0.04949836864746739 * 32 | 1.5839477967189566 |
| 0.034353915628128034 * 36 | 1.2367409626126094 |

C(36, 3) equals the seed-a column count (B+2 = 36). C(32, 3) equals the
seed-b column count (B+2 = 32). 4 * 130873 equals the Stage-0 order.
The two quotients are the IEEE values of the archived `rate_U` fields.
The expected intersection counts are about 1.58 and 1.24 hits.

**Label order (J2), read from `outcome_label` after the table above.**
`NULL_LO = 0.5`, `NULL_HI = 2.0`, `SLICE_MIN = 4.0`. The function
returns `O-NULL` only when every W/U ratio lies in [0.5, 2], `O-SLICE`
only when every ratio is at least 4, and `O-INCONCLUSIVE` for every
other ratio once `rate(P)` is 1 and `rate(U)` matches `|image|/r`.
Both archived ratios are 0, so neither positive band fires.

**Stage-1 replay.** Copy under `/tmp/review-certbin-0f4599` held
`implementation/`, `trial-plan-v1.json`, and `stage0/`
(`curve.json`, `cells.json`, `preregistered-predictions.json`). The
copy had no `stage1` json and no `RESULTS.md` before the run.

```
python3 /tmp/review-certbin-0f4599/implementation/run.py --stage 1 --trial-plan /tmp/review-certbin-0f4599/trial-plan-v1.json --run-dir /tmp/review-certbin-0f4599/runs/replay-stage1
```

Exit 0 in 1.020s. Outcome `O-INCONCLUSIVE`. Seed 2026100319: `rate_P`
1.0, `rate_W` 0.0, B 34, C 7140, image 6478, sw 32. Seed 2026100320:
`rate_P` 1.0, `rate_W` 0.0, B 30, C 4960, image 4496, sw 36. Writes
landed in the temp copy (`stage1/panels.json`, `RESULTS.md`, and the
fresh run directory). The archived repo files were not overwritten.

## Comparison

Against H-CERTBIN-a3d441 distinguishable outcomes and the frozen bands
`null_band: [0.5, 2.0]`, `slice_min: 4.0`:

- `rate(P) = 1` and `rate(U) = |image|/r` on both seeds. The census
  checksum holds. This is not O-ARTIFACT.
- W/U = 0 on both seeds. 0 is outside [0.5, 2] and below 4. O-NULL
  (E-NULL) does not fire. O-SLICE (E-SLICE) does not fire.
- The hypothesis text for O-INCONCLUSIVE names ratios in (2, 4) or
  seed disagreement. These rows are not that case. The code's residual
  bucket is wider, and that residual is what the archived label and
  the temp replay both emitted. The run is not relabeled.
- A zero intersection with `|S_W|` 32 and 36, against null expectations
  about 1.58 and 1.24, is not a proved occupancy failure. It does not
  support weaken or reject_scoped.
- `rate(W) = 0` is not a slice concentration and not an ECDLP speedup.
  Slice requires W/U at least 4. No discrete logarithm is solved.
  `claims.exponent_move` is false.
- O-IMPEDIMENT does not apply. Both runs completed and the replay
  completed.

## Inference

The package is valid. The official label is the residual
**O-INCONCLUSIVE**. Decision: **inconclusive**. Direction neutral.
Strength inconclusive. Claim tier toy. Proof status not applicable.
Hypothesis and experiment move `approved` to `analyzed`. Analyzed
records that residual label and keeps neither law. Do not support.
Do not weaken. Do not reject_scoped. No exponent. No n>=131 transfer.
No KN-FIND. GOAL-ECDLP2M-001 is not edited.

## Limitation

One n=19 cell, two seeds, `|S_W|` 32 and 36. The null expectation of
an intersection is about one hit, so a zero count cannot separate the
occupancy model from a small sample. The hypothesis prose and the
code residual do not name the same set of ratios; this review keeps
the code's emitted label and does not treat ratio 0 as (2, 4). PD-1:
one coordinator task owns J1, J2, and J3; no separate validator and
no red-team. Certificate kind is none. A later card that wants a law
band needs a larger `|S_W|` or more seeds. This cell does not move an
ECDLP exponent.
