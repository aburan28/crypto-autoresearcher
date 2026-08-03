# BATCH-027 dispatch plan

**Goal:** GOAL-ECDLP-001  
**Batch:** BATCH-027  
**Cycle:** RC-27 / QUEUE-AMEND-20260731-016  
**Open decision:** DEC-20260731-032  
**Approval decision:** DEC-20260731-034  
**Amend freeze:** `d65c5e21` (TASK-122)  
**Approval snapshot:** `8f02ab4b` (TASK-124)

| Task | Role | State | Depends | Notes |
|------|------|-------|---------|-------|
| TASK-20260731-120 | coordinator | completed | — | Open DEC-032 |
| TASK-20260731-121 | coordinator | completed | 120 | Author PA-IT-001-v3 |
| TASK-20260731-122 | coordinator | completed | 121 | Amend freeze `d65c5e21` |
| TASK-20260731-123 | reviewer | completed | 122 | PASS (RT-20260731-123) |
| TASK-20260731-124 | coordinator | completed | 123 | **APPROVED** `8f02ab4b` / DEC-034 |

**Authorization:** `run_authorized: true` against `experiments/EXP-IT-001/specification.v3.yaml` only (toy).  
**H-IT-001:** remains `specified`. **H-DS-001:** untouched (`analyzed`).  
**BATCH-026 CI:** disjoint; TASK-115 in flight under DEC-033 — not cancelled.  
**DEC remint:** DEC-033 taken by BATCH-026 → IT uses DEC-034.  
**No Executor tasks in this queue.**

**Next:** Open BATCH-028 with Executor for a bounded toy EXP-IT-001 run (null control IDEA-011; planted-path; matched rho/BSGS; snapshot before Val+RT). No STR. No push.
