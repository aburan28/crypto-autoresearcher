# Analysis: EXP-BINSTD-0f2222 (H-BINSTD-f4b5bb)

Review plan: `experiments/EXP-BINSTD-0f2222/review/review-plan.yaml`
(`REVIEW-BINSTD-0f2222-20261004`), written before this analysis.
Addendum: `experiments/EXP-BINSTD-0f2222/review/addendum-pd1.yaml` (PD-1).
Producer: TASK-20261003-9c39d2. Approval: DEC-20261003-c943ba.
Execution code commit `6df4b8e6fdad60e2e3cc738b979a869a61bc3ba4`, dirty false.
Decision: **inconclusive**. Outcome label: **O-FAIL-BAND**. No winning
model. No break. No exponent. No Stage 2. No Bedrock, AUXIN, Magma, or Sage.

## Observation

**Validity (J1).** Two runs.

| run | stage | outcome | receipt | returncode | check_returncode | certificate |
| --- | --- | --- | --- | --- | --- | --- |
| RUN-BINSTD-15c441 | 0 | O-STAGE0-OK | output_validated | 0 | 0 | kind none |
| RUN-BINSTD-df8235 | 1 | O-FAIL-BAND | output_validated | 0 | 0 | kind decomposition, verified true |

Stage 0 raw result: `group_order` 130972, `empty_pool_hits` 0,
`twin_add_ok` true, `twin_order_ok` true, `claims.exponent_move` false,
`claims.break` false. Both manifests record `code.dirty: false` and
`code.commit` `6df4b8e6fdad60e2e3cc738b979a869a61bc3ba4`.

Stage 1 raw result matches `RESULTS.md` on the summary fields that file
carries: outcome `O-FAIL-BAND`, winning model null (`RESULTS.md` prints
Python `None`), holds M1 0, M2 2, M3 2, `empty_pool_hits` 0, `twin_ok`
true, `cert_ok` true. Cell rows, all at n=17 and 200 attempts:

| N | hits | p_hat | relerr M1 | relerr M2 | relerr M3 | in band |
| --- | --- | --- | --- | --- | --- | --- |
| 58 | 6 | 0.03 | 1.3769872958257712 | 0.16800237812128407 | 0.1830665896132939 | M2, M3 |
| 100 | 21 | 0.105 | 1.778193939393939 | 0.37520600000000004 | 0.4283740168249337 | none |
| 162 | 40 | 0.2 | 1.0086189709378115 | 0.0018899557994207217 | 0.10144745658023525 | M2, M3 |

`claims.exponent_move` is false. `winning_model` is null.

**Label order (J2).** `RELERR_BAND` is 0.25. `decide()` counts a model
as holding a cell only when that cell's relative error is at most 0.25,
and a winner needs three cells. M1 is outside the band on every cell.
M2 and M3 are inside on N=58 and N=162 and outside on N=100
(0.37520600000000004 and 0.4283740168249337). `len(winners)==0` returns
`O-FAIL-BAND` before the tie test. The unique-winner branch does not fire.

**Blind rates and M2 (J3), computed before opening `implementation/`.**

| quantity | exact value | archived float | equal as float64 |
| --- | --- | --- | --- |
| 6/200 | 0.03 | p_hat 0.03 | yes |
| 21/200 | 0.105 | p_hat 0.105 | yes |
| 40/200 | 0.2 | p_hat 0.2 | yes |
| 58²/130972 = 3364/130972 | 0.0256848792108236875… | p_m2 0.02568487921082369 | yes |
| 100²/130972 = 10000/130972 | 0.0763521974162416394… | p_m2 0.07635219741624164 | yes |
| 162²/130972 = 26244/130972 | 0.2003787068991845585… | p_m2 0.20037870689918455 | yes |

**Replay.** Stage 1 only, from a copy at `/tmp/review-binstd-0f2222`,
after deleting that copy's `stage1/bakeoff-table.json`,
`stage1/control-table.json`, and `RESULTS.md`. Command:

```text
python3 /tmp/review-binstd-0f2222/implementation/run.py --stage 1 \
  --trial-plan /tmp/review-binstd-0f2222/trial-plan-v1.json \
  --run-dir /tmp/review-binstd-0f2222/replay-run
```

Exit code 0. Outcome `O-FAIL-BAND`. Holds M1 0, M2 2, M3 2.
`winning_model` null. Cell hits, `p_hat`, model probabilities, and
relative errors match `RUN-BINSTD-df8235` raw-result.json. Archived
repository `RESULTS.md`, stage1 JSON, and the Stage-1 raw result were
unchanged (sha256 identical before and after).

## Comparison

Against the frozen distinguishable outcomes in H-BINSTD-f4b5bb:

- Twin agreement, certificate pass, and empty-pool hits 0: hold. Not O-ARTIFACT.
- Exactly one model inside 0.25 on all three cells: not met. Not O-SUPPORT.
- No model holds three cells: met. Label is O-FAIL-BAND.
- Two or more models each holding three cells, or a tie within 5% on every cell: not reached. `decide()` returns O-FAIL-BAND when the winner list is empty, before the tie test. Not O-INCONCLUSIVE as an experiment label.
- Infrastructure failure: not met. Not O-IMPEDIMENT.

M2 and M3 each hold two of the three cells. The cell both miss is N=100.
O-FAIL-BAND here is the zero-winner branch. It does not name a winner,
and it does not refute M2 or M3 at n=17.

## Inference

The package is valid. The Stage-1 label is the frozen zero-winner
outcome O-FAIL-BAND. No model is inside relative error 0.25 on all three
n=17 cells, so `winning_model` stays null. The official decision is
**inconclusive**: do not support (no unique winner), and do not weaken
or reject_scoped (M2 and M3 each hold two of three cells; one n=17
bake-off; empirical_only). Hypothesis and experiment move
`approved → analyzed`. Analyzed records O-FAIL-BAND and names no winning
model. Direction neutral. Strength inconclusive. Claim tier toy.
Proof status empirical_only. No exponent. No Stage 2 n=23 from this
decision. No KN-FIND.

## Limitation

One n=17 bake-off, 200 attempts per cell, group order 130972 equal to
the full curve order rather than a prime-order subgroup. PD-1: one
coordinator task owns J1, J2, and J3; no separate validator and no
red-team. The unique-winner branch was not taken and stays unread as a
result. Stage 2 n=23 is not authorized by this decision. Nothing here
is an ECC2K-130 result or an exponent move. Amazon Bedrock was not
selected.
