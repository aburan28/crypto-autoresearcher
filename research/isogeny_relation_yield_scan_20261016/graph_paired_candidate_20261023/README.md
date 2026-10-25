# Paired confirmation summary candidate

`paired.py` reads a completed `confirm.py` analysis and its frozen trial plan,
selection, schedule, and all original arm receipts. The plan must bind hashes
of both `paired.py` and `confirm.py` before confirmation execution. The script
rechecks every confirmation summary against the validated arm receipt, then
binds the collector output to the graph-attempt phase digest. It checks target
order, coefficient stream, curve header, quota, and aggregate useful count.

For every selected vertex and the three native factor bases, the output gives
the paired 2-by-2 occupancy table for `low_x` versus `mid_x`, `low_x` versus
`random_x`, and `mid_x` versus `random_x`. The difference is
`(left_only - right_only) / 32768`. These are descriptive fresh-confirmation
quantities. The exact simultaneous marginal intervals and ratio rule remain
in the preceding analyzer. This script does not calculate an ECDLP time or
ascribe differences to conductor level.

Run controls with:

```sh
python3 -m unittest research/isogeny_relation_yield_scan_20261016/graph_paired_candidate_20261023/test_paired.py -v
```

After all approved confirmation receipts exist:

```sh
python3 research/isogeny_relation_yield_scan_20261016/graph_paired_candidate_20261023/paired.py \
  --repo . --analysis PATH --selection PATH --schedule PATH --plan PATH --out PATH
```

The output path is write-once and must be in the approved artifact scope.
[`report.md`](report.md) and [`report.pdf`](report.pdf) describe the bounded
control and remaining inference limits.
