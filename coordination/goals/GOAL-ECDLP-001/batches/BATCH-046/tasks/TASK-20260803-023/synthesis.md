# BATCH-046 Coordinator synthesis — TASK-20260803-023

**Goal:** GOAL-ECDLP-001 (`active`)  
**Batch:** BATCH-046  
**Amendment:** `PA-IT-001-v3-rc45-repair-5` (frozen; blob unchanged)  
**Run snapshot:** `e7d14020ca711729e76bbf420d4ec24184a4a7a0` (TASK-020)  
**Run:** `RUN-IT-001-rc45-smoke` only (`RUN-IT-001-rc45-measure` absent)  
**Validator:** `VAL-20260803-021` → **COMPLETED_VALID_SCOPED**  
**Red Team:** `RT-20260803-022` → **PASS_SCOPED** (with RT-046-B1..B3 voids)

## Adopted on the merits

Adopt both independent reviews. The smoke package is mechanically
`completed_valid` under the frozen RC-45 string (exact command, yaml parse,
null-recompute script present, `c_smart=8` runtime metadata, D2 CLI wired).

Transfer-gate / sub-rho / HEUR-ISO-1 scientific interpretation is **VOID**:

- Planted positive control remains embedding-degree-1 MOV
  (`CTRL-PLANTED-PATH-POS`), not live `CTRL-ANOMALOUS-TRACE1`
  (`anomalous_trace_eq_1=false`; no `anomalous_trace1_certificate.json`;
  `C_special=22` MOV charge under a Smart formula_id label).
- Null-plant independence unmet (`edge_ledger=[]`; packaging gate absent;
  `R_null=null` on all 21 cells).
- Measure arm not executed; smoke alone cannot authorize a hypothesis
  transition (RT-046-B2).
- No certificate-bearing unplanted `R_xfer<0.7`; expected transfer cost
  unbounded under `p_success=0`.

`planted_path_recovered=true` / `plant_detected=true` are packaging theater,
not transfer-capability validation.

## Status / non-transitions

- **Decision:** `inconclusive` (observations-only; not null result; not
  weaken/reject_scoped).
- **H-IT-001:** remains `specified` (`hypothesis_status_transition: none`).
- **GOAL-ECDLP-001:** remains `active`.
- **Knowledge:** `not_warranted` — no validated cryptanalytic finding.
- **Asymptotic promotion gates:** all four remain OPEN.
- **No** STR reopen, lane death, crypto-scale claim, or GOAL completion.

## Exact next action

Open a successor Executor batch under frozen
`PA-IT-001-v3-rc45-repair-5` that (1) exercises `CTRL-ANOMALOUS-TRACE1` at
bits=20 with a verified anomalous certificate and
`C_special=ceil(8*log2(p))`, (2) persists a non-empty
`CTRL_NULL_IT_PLANT` edge ledger and a live
`CTRL-NULL-PACKAGING-GATE`, (3) emits `dominated_by` / quantitative
`sota_delta` on run deliverables, (4) rebinds execution_report/manifest
provenance to the current batch/task IDs, then runs reserved measure seeds
if smoke controls pass; obtain independent validation + red-team. Do not
cite `RUN-IT-001-rc45-smoke` planted/null positives as transfer evidence.

Records: `EV-IT-008`, `DEC-20260803-004`.
