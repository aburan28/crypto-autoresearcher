# EXP-SEMAEV-002 — implementation note

## What was built
- `harness/semaev.py`: `measure_yield` (fraction of random on-curve targets that
  decompose as a sum of two factor-base points, by exact enumeration) plus three
  factor-base geometries: `factor_base_random` (control), `factor_base_interval`
  (consecutive on-curve x), `factor_base_ap` (arithmetic progression).
- `harness/run_yield.py`: the EXP-SEMAEV-002 entry point.

## Command
```
python -m harness.run_yield
```
9 runs = {bits 12,14,16} x {seeds 1,2,3}, factor base 20, 300 targets each.

## Deviations from the approved protocol
None to the frozen parameters. See analysis.md for a confound (low decomposition
counts at high bits) that the v1 protocol did not control; this is recorded, not
silently corrected.

## Honesty flags
- This is an independent m=2 (S_3) implementation, separate from the campaign's
  m=3 semaev_tree.py; it complements, not restates, EXP-FB-001.
- Every counted decomposition is verified by an exact point-sum check; one is
  emitted as a certificate per run.
