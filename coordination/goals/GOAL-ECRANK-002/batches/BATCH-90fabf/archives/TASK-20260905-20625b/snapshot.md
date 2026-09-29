# Snapshot archive — TASK-20260905-20625b (BATCH-90fabf, GOAL-ECRANK-002)

Archives the complete execution package of TASK-20260905-54bcbf (frozen
protocol EXP-ECRANK-76a70d, approved by DEC-20260905-eb1df9) before any
independent review reads it.

## Archived artifact paths (committed verbatim in this commit)

- tasks/TASK-20260905-54bcbf/engine.py — the delta-multiplier engine (1066 lines)
- tasks/TASK-20260905-54bcbf/run_all.py — the 8-run driver (643 lines)
- tasks/TASK-20260905-54bcbf/results/run_record.yaml — per-run status, seeds, params, counted ops, peak_rss, environment
- tasks/TASK-20260905-54bcbf/results/observations.md — executor's observations and disclosed deviations
- tasks/TASK-20260905-54bcbf/results/summary.json — counts per (n,H) cell, op counters, pre-registered metric fits
- tasks/TASK-20260905-54bcbf/results/controls.json — IV-1 (known-false) and IV-2 (planted synthetic) outcomes
- tasks/TASK-20260905-54bcbf/logs.txt — full execution log

## Executor-reported terminal state (unreviewed — pointer only)

- Run 1 smoke self-test: pass (6/6 checks).
- Runs 2-5 (arms A/B/B-re-run/C): all completed; 0 certified instances at any
  arm; arm B determinism re-run bit-for-bit identical (IV-7 pass).
- Run 6 augmentation scan: no constructed instance -> F6 inconclusive.
- Run 7 known-false control: certified total 7 at n=8 and 9 at n=10 exactly
  (IV-1 pass — relation bookkeeping and certification pipeline validated).
- Run 8 repair margin: not needed (no infrastructure failure).
- Executor's own reading: 0 instances is genuine low yield of the declared
  search (measured per-draw square-hit rate ~1e-7.5), i.e. the honest F1
  scope outcome — a limitation of the declared search, never a conclusion
  about HEUR-1/HEUR-2.
- Resource envelope: stdlib only, peak RSS ~48 MB, total wall ~39 s, counted
  ops inside the 1.0e8 per-arm caps.

## Claim boundary

These executor reports are UNREVIEWED. Independent validation is
TASK-20260905-47742c (review-adversarial, xhigh, blind re-derivation of one
checkpoint prefix and the controls). Exhaustion, zero yield, and infrastructure
outcomes are inert in both directions; no rank is asserted by this archive.
