# BATCH-047 frozen input capsule

Executor and reviewers must reconstruct all claims from these immutable inputs:

- Frozen amendment: `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc45-repair-5.yaml`
  archived at commit `16f7b7bf8b9d8a483b6ef939e9ebcc2a0fcb4620` (BATCH-045
  proposal snapshot).

- Prior run package: `RUN-IT-001-rc45-smoke` snapshot-archived at
  `e7d14020ca711729e76bbf420d4ec24184a4a7a0` (TASK-020, BATCH-046).

- Validator void findings: `VAL-20260803-021` (BF-1..BF-3) and Red Team void
  findings: `RT-20260803-022` (RT-046-B1..B3).

- Governing decisions: `DEC-20260803-004` (BATCH-046 inconclusive, exact next
  action), `DEC-20260803-003` (BATCH-046 open), `DEC-20260803-002` (expand on
  repair-5).

- Recompute script: `experiments/EXP-IT-001/implementation/recompute_null_plant_from_ledger.py`
  as frozen in the repair-5 snapshot.

## Required Executor outcome

1. Generate a Smart anomalous positive-control curve at bits=20: an ordinary
   prime-field curve E/F_p with #E(F_p) = p (so trace t = 1 in the Smart sense,
   equivalently N = p is prime), verified via `anomalous_trace1_certificate.json`
   with `verified: true`. Use `C_special = ceil(8 * log2(p))` with
   `c_special_formula_id: C_special_smart`. Do NOT use embedding-degree-1 MOV,
   the quadratic formula `20*(log2 N)^2`, or `ceil(2*sqrt(N*))` as the anomalous
   pass threshold.

2. Run `recompute_null_plant_from_ledger.py` against the raw edge data; persist
   a non-empty null-plant edge ledger (≥1 row). The CTRL-NULL-PACKAGING-GATE
   must run and reject a pre-registered synthetic R_xfer < 0.7 claim.

3. Set manifest `batch_id: BATCH-047`, `task_id: TASK-20260803-027`, and
   `execution_report` path to the current task directory.

4. If all smoke controls pass: proceed with the reserved measure seeds. Record
   `dominated_by`, `time_exponent`, `memory_exponent`, `data_or_query_exponent`,
   and quantitative `sota_delta` on every run deliverable.

5. If any smoke control fails: halt the measure phase, record which control
   failed, set `validity_status: inconclusive` for the smoke run, and do NOT
   fabricate measure results.

## Claim ceiling

Toy tier only. No result from this batch can support a crypto-scale ECDLP claim,
an asymptotic bound, a promotion of H-IT-001 beyond `specified/analyzed`, or a
GOAL-ECDLP-001 completion. Charged transfer ratios and HEUR-ISO-1 toy
distribution status are the only reportable scientific quantities.

## Pareto declaration (this capsule)

Non-solver metadata. `dominated_by` not_applicable; all three SOTA deltas null.
