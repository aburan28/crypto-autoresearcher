# BATCH-025 — RC-25b design-path non-execution failure (EXP-IT-001)

**Date:** 2026-07-31  
**Goal:** GOAL-ECDLP-001  
**Batch:** BATCH-025  
**Cycle:** RC-25b / QUEUE-AMEND-20260731-014  
**Sub-goal:** SG-ECDLP-002 / H-IT-001 / EXP-IT-001 v2  
**Amend freeze:** `285e533e` (TASK-108)  
**First REVISE:** RT-20260731-105 / TASK-105 (B-1–B-4) → TASK-106 NOT APPROVED (`7dc2b39b`)  
**Second REVISE:** RT-20260731-109 / TASK-109 — **REVISE**  
**Approval:** TASK-110 **NOT APPROVED**  
**Decision:** DEC-20260731-028  

## What failed

Independent re-review after the sole authorized RC-25b protocol amendment
returned a **second REVISE**. Per RC-25b / QUEUE-AMEND-014 / DEC-026:
**second REVISE ⇒ BATCH-025 design-path non-execution** for EXP-IT-001.
No Executor. No third amend cycle inside BATCH-025.

### Blocker discharge at `285e533e`

| ID | Status | Notes |
|---|---|---|
| B-1 | **DISCHARGED** | F_hit / d=3 / H_min decidable |
| B-2 | NOT_FULLY_DISCHARGED | detectors ok; density universe residual → **B-5** |
| B-3 | NOT_FULLY_DISCHARGED | formulas ok; aggregation residual → **B-6** |
| B-4 | NOT_FULLY_DISCHARGED | identities ok; construction/plant → **B-7**, **B-8** |

### Open blocking residuals (RT-20260731-109)

- **B-5** — Density-universe N / cofactor designation not unique (`rho_special` not uniquely recomputable)
- **B-6** — R_xfer path / endpoint aggregation rule not frozen (Executor-manipulable gate)
- **B-7** — NULL-IT-ISOGENY-TRANSFER graph construction not a closed algorithm
- **B-8** — CTRL-NULL-IT-PLANT detection predicate not frozen

## What this is not

- Not a mathematical negative on H-IT-001
- Not SG-ECDLP-002 lane death
- Not approval or run of EXP-IT-001
- Not reopen / support / reject of H-DS-001
- Not cancellation of parallel structure-null-r2 Val/RT under DEC-027
- Not a third amendment cycle inside BATCH-025 / RC-25b
- Not STR reopen; H-IC-001 / H-STR-002 untouched

## Standing

H-IT-001 remains `specified`. H-DS-001 remains `analyzed` / deferred. Quarantine
and toy ceiling stand. Promotion gates OPEN. Fresh amend of B-5–B-8 belongs in
**BATCH-026** outside RC-25b (new author session) if SG-ECDLP-002 stays selected.
