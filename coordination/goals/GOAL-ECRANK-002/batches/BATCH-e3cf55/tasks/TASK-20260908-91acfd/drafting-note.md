# TASK-20260908-91acfd — approval authorship note (Coordinator inline)

- Date: 2026-09-08
- Session: coordinator portfolio run, worktree `/Volumes/SSD990/llm/tmp/opencode/portfolio-main-20260908`, branch `ecrank-73275e-v2-replication-20260908` from `origin/main` @ `cd84f162b8`.
- Authority: GOAL-ECRANK-002 committed `next_action` (DEC-20260908-d361ab, disposition `replicate`, requirements N1–N3) + AGENTS.md standing user authorization 2026-09-06 ("all is approved. ideas/experiments should be always approved"). No user confirmation requested or needed; protocol readiness was the gate.

## Deliverables authored (all new files; nothing existing edited)

1. `experiments/EXP-ECRANK-73275e/amendments/v2_replication_protocol.yaml`
   - sha256 `6f61031861c97da69eac11b947fb7f51e0cf522e3676d3820a5411d8933f847d`
   - Additive amendment `v2_replication` on frozen v1 `specification.yaml` (sha256 `ae6d170af4fe2e6ffb8f136304f4735b1461c7541f68119a5322888116483c8e`, untouched).
   - Seven runs R9–R15, fixed order, control admission first; fresh seeds 760912/760908/760914/760906/760906/760910/760916; repairs IV-1R, IV-1C (fixed ladder 1500/10000/100000, graded), IV-3R (9 planted elliptic n=6, R3-family shape), N2R (dual-convention height reconciliation, predicates bound verbatim pre-count, decade ratios descriptive under both conventions), N3R (R14 cap 2.0e9, IC-732-3 box retained and disclosed), IV-2R replay, IV-4R null re-run; RD-1/RD-2/RD-3 recording repairs.
2. `experiments/EXP-ECRANK-73275e/amendments/v2_authorized.yaml` — approval gate record marking the amendment authorized under DEC-20260908-614199.
3. `ledger/decisions/DEC-20260908-614199.yaml` — Coordinator decision approving amendment v2 and binding the executor handoff; records protocol-completeness check (controls, metrics, budgets, stopping rules, artifact paths, dependencies, inference policy, committed handoffs all present) before the approval mark.
4. `ledger/handoffs/TASK-20260908-5291f8.yaml` — executor handoff: full envelope (objective, inputs, constraints, deliverables, write_scope, inference `executor-implementation`, budget 50400 s / 8 GiB / 7 runs, completion gate); observations-only, zero-interpretation, no status changes.
5. `coordination/goals/GOAL-ECRANK-002/batches/BATCH-e3cf55/dispatch_queue.json` — 4-task serial chain (91acfd → a94ad8 → 5291f8 → 9439c0), max_concurrent 1, archive blocks on a94ad8 (ledger) and 9439c0 (snapshot) with null commit bindings pending their commits.

## Identifier provenance (rule 14)

All IDs minted via `python3 tools/allocate_id.py --next <type> --date 20260908` and confirmed with `--check` before use: BATCH-e3cf55; TASK-20260908-91acfd / -a94ad8 / -5291f8 / -9439c0; DEC-20260908-614199. No grep-for-max allocation.

## Boundaries restated

- v1 `specification.yaml` and runs R1–R8 are immutable and never re-scored; v2 is additive only.
- Approval asserts no truth: it does not claim HEUR-1 or the n=6 result is true, and it does not validate any future run.
- The review round for v2 results (frozen review_plan, blind re-derivation, validator, red team) is a SEPARATE later batch after TASK-20260908-9439c0's snapshot archive.
- H-ECRANK-36d8d7 stays `analyzed`; no status change occurs in this batch.

## Next

TASK-20260908-a94ad8 (ledger archive) binds this package in one exact-path commit; then push + PR; then TASK-20260908-5291f8 executor dispatch.
