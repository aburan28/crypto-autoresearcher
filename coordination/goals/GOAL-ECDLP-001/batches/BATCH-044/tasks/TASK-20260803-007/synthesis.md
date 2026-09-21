# BATCH-044 Coordinator synthesis — TASK-20260803-007

**Goal:** GOAL-ECDLP-001 (active)  
**Batch:** BATCH-044  
**Amendment:** `PA-IT-001-v3-rc44-repair-4`  
**Proposal snapshot:** `3b93abccee76` (TASK-004)  
**Review snapshot:** (TASK-006)  
**Red-team:** `RT-20260803-005` verdict **REVISE** ([review](86a6337f-c319-4ef3-ae3c-9281c4469955))

## Adopted on the merits

Adopt REVISE. Do **not** authorize Executor/implementation on rc44.

### Substantive progress (RT-314 B1–B3 closed in text)

- B1: `c_smart=8` ⇒ ratio ≈0.176 at pinned bits=20  
- B2: plant bit + matched_rho restated + quadratic Smart superseded  
- B3: density abscissa restored to `{20,24,28}`

### Blockers preventing admission

1. **RT-044-Y1** — frozen amendment fails `yaml.safe_load` (unquoted acceptance criterion at line 205)  
2. **RT-044-M2 / RT-244-M2** — `recompute_null_plant_from_ledger.py` listed in archive manifest but absent at snapshot

## Status / non-transitions

H-IT-001 remains `specified`. No run. Knowledge promotion: `not_warranted`.

## Exact next action

Open a successor batch for **`PA-IT-001-v3-rc45-repair-5`** that (1) quotes/fixes all YAML acceptance lines so `yaml.safe_load` succeeds, (2) either authors the null-recompute script into the pre-run archive list as a present file or removes the path and states an explicit pre-run creation gate without claiming presence, then obtain independent review before any implementation.

Records: `EV-IT-006`, `DEC-20260803-001`.
