# Control report — TASK-20260824-dd5b5c

## Execution record

This report records the bounded execution already completed before the task
was interrupted. On resume, the control program was **not rerun**, per the
handoff instruction. The existing script and table were hash-checked and left
unchanged.

The relevant commands and statuses were:

```text
python3 plugins/crypto-autoresearcher-harness/scripts/preflight.py \
  --repo /Volumes/SSD990/crypto-autoresearcher-ssi-harness-20260824 \
  --runtime codex --doctor
exit status: 0
result: READY; generated bindings, role bindings, dependencies, and harness doctor passed

python3 -B coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/corrected_charging.py \
  --raw experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json \
  --output coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/recomputed_table.json
exit status: 0
result: RG-1 PASS; RG-2 PASS; RG-3 PASS; WROTE .../recomputed_table.json rows=240
```

The second command was run once before the interruption. It read the frozen
raw result and wrote the already-existing table only in the declared task
directory. It did not execute `experiments/EXP-WESOVOW-001/cost_model.py`.

The dispatch preflight had also confirmed the batch queue's sole ready task
was `TASK-20260824-dd5b5c`; no queue, ledger, archive, or commit operation was
performed by this task.

## RG-1 — committed-law reproduction gate

RG-1 ran first inside `corrected_charging.py`, before the output table was
opened. It recomputed all five field sizes × six memory budgets × four
overhead values under the frozen law and compared each value with the matching
`van_oorschot_wiener[*].log2T_w` value in
`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json`.

Recorded output:

```text
RG-1 PASS: checked=120 max_abs_diff=0 tolerance=1.0000000000000001e-09 mismatches=0
```

Verdict: `PASS`. The exact reproduction gate did not detect an arithmetic or
input-integrity mismatch. A failure condition would have been a missing
committed cell or any absolute difference greater than `1e-9`; the script is
written to return before writing a corrected table in that case.

## RG-2 — cap control at w=M

RG-2 evaluated both laws at `log2 w = log2 M`, with zero overhead, for both
anchors and all five field sizes. Values below are the recorded output,
shown to the displayed precision of the command output.

| Anchor | log2p | log2M (= log2w) | committed/null log2T(w) | corrected log2T(w) | log2T_full |
|---|---:|---:|---:|---:|---:|
| fitted_opt | 256 | 93.27781828665178 | 62.091980444680289 | 108.73088958800618 | 108.73088958800618 |
| fitted_opt | 384 | 137.48765358816084 | 89.130563524095109 | 157.87439031817553 | 157.87439031817553 |
| fitted_opt | 512 | 181.43583267427067 | 115.38598040228246 | 206.10389673941779 | 206.10389673941779 |
| fitted_opt | 576 | 203.30702177853001 | 128.32769935032093 | 229.98121023958595 | 229.98121023958595 |
| fitted_opt | 768 | 268.68673590177326 | 166.59206774694192 | 300.93543569782855 | 300.93543569782855 |
| PAPER_PAIRS | 256 | 92.5 | 60.25 | 106.5 | 106.5 |
| PAPER_PAIRS | 384 | 138.59999999999999 | 88.200000000000003 | 157.5 | 157.5 |
| PAPER_PAIRS | 512 | 181.30000000000001 | 113.54999999999998 | 204.19999999999999 | 204.19999999999999 |
| PAPER_PAIRS | 576 | 206 | 127.90000000000001 | 230.90000000000001 | 230.90000000000001 |
| PAPER_PAIRS | 768 | 272.19999999999999 | 166.29999999999998 | 302.39999999999998 | 302.39999999999998 |

Recorded control line:

```text
RG-2 PASS: checked_rows=10 corrected_cap_identity=True committed_null_detected_as_non_cap=True
```

Verdict: `PASS` as a discriminating cap control. The corrected law satisfies
the declared `w=M` identity for every anchor/field row; the committed law
does not. This is an implementation/control observation, not a claim about
the underlying attack.

RG-2 would fail if the corrected value differed from `T_full` at any exact
`w=M` row, or if the committed/null value were not distinguishable from
`T_full` at any such row. The frozen specification's cap requirement is
`experiments/EXP-WESOVOW-001/specification.yaml:146-149`; the frozen
implementation and serialized formula are at
`experiments/EXP-WESOVOW-001/cost_model.py:236,265-276` and
`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json:9-15`.

## RG-3 — null-law discrimination

RG-3 used the same anchors and all five field sizes at the low-memory probe
`log2w=30`, `c=0`, with the corrected procedure swapped back to the committed
law. The recorded output was:

| Anchor | log2p | committed/null log2T(w) | corrected log2T(w) | corrected − committed |
|---|---:|---:|---:|---:|
| fitted_opt | 256 | 93.730889588006178 | 140.36979873133208 | 46.638909143325904 |
| fitted_opt | 384 | 142.87439031817553 | 211.61821711225593 | 68.743826794080405 |
| fitted_opt | 512 | 191.10389673941779 | 281.8218130765531 | 90.717916337135307 |
| fitted_opt | 576 | 214.98121023958595 | 316.63472112885097 | 101.65351088926502 |
| fitted_opt | 768 | 285.93543569782855 | 420.27880364871521 | 134.34336795088666 |
| PAPER_PAIRS | 256 | 91.5 | 137.75 | 46.25 |
| PAPER_PAIRS | 384 | 142.5 | 211.80000000000001 | 69.300000000000011 |
| PAPER_PAIRS | 512 | 189.19999999999999 | 279.85000000000002 | 90.650000000000034 |
| PAPER_PAIRS | 576 | 215.90000000000001 | 318.89999999999998 | 102.99999999999997 |
| PAPER_PAIRS | 768 | 287.39999999999998 | 423.5 | 136.10000000000002 |

Recorded control line:

```text
RG-3 PASS: probe_log2w=30 checked_rows=10 all_rows_discriminate=True
```

Verdict: `PASS`. The null procedure discriminated in all ten rows. A
non-discriminating output would have been discarded: RG-3 fails if any
corrected/committed pair has absolute difference at most `1e-12`.

## Artifact and scope checks

The table metadata records:

```text
row_count: 240
anchors: fitted_opt=120, PAPER_PAIRS=120
field sizes: 256, 384, 512, 576, 768
log2w values: 30, 40, 50, 60, 70, 80
overhead values: 0.0, 0.5, 1.0, 2.0
```

Every table row names its anchor. The corrected value is the reported
comparison quantity; the committed-law value is retained as an explicit null
field for control traceability. No result is treated as a measurement of a
real attack.

The P=512 boundary is preserved verbatim:

> The `P=512` crossover value and its `w=2^80` sign are **NOT citation-eligible**. This task does not lift that prohibition. Only a committed Coordinator decision on independently reviewed evidence can lift it.

No SQIsign, CSIDH, standardized-parameter, security, asymptotic, hypothesis,
ledger, or queue conclusion is made here.
