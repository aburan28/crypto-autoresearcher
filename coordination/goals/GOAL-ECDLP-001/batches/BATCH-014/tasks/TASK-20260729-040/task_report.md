# TASK-20260729-040 — completion report

**Role:** coordinator  
**Goal / batch:** GOAL-ECDLP-001 / BATCH-014  
**Status:** completed (producer artifacts written; no commit by this card)  
**Archived by:** TASK-20260729-041

## Deliverables

| Path | Bytes | Role |
|---|---:|---|
| `experiments/EXP-STR-004/specification.yaml` | 113828 | frozen contract at `review_required`, `approved_by: null` |
| `experiments/EXP-STR-004/derivation_note.md` | 26879 | labelled `derivation`, defines `T(cell)` |
| `.../TASK-20260729-040/feasibility_table.md` | 28064 | CAN FIRE / CANNOT FIRE + F-1..F-5 evaluability |

This report itself is an **undeclared** artifact relative to
`declared_commit_sets.TASK-20260729-041_snapshot_commits_4_paths`. It is
recorded here and must **not** be staged by TASK-20260729-041 unless a
QUEUE-AMEND adds it.

## G1–G13

| Gate | Verdict |
|---|---|
| G1 Contract completeness | MET — status `review_required`, `approved_by: null`, 28-run inventory, criteria, verdict rule, budgets |
| G2 Two arms and no third | MET — A-prime, E-prime; `main()` forbidden |
| G3 Fourteen named cells | MET — L12..L193, X96/X97, A12M3/A13M3 |
| G4 PRED-ID-STR in contract text | MET |
| G5 Derivation note | MET — defines `T(cell)`, labelled `derivation`, EXACT/CONDITIONAL inventory |
| G6 Matched `R_base(cell)=ceil(B/3)` | MET — identical across arms; shortfall disposition present; suppression pre-registered 0 |
| G7 Certificate discipline | MET — base `decomposition`, appended `none`, Sage via `sage` binary |
| G8 Solver fact with provenance | MET — carried as pre-freeze host observation; Executor capture obligation written |
| G9 Budgets / stopping rules | MET — 900/7200/900 s; 2 MiB / 64 MiB; pre-flight disk <5 GiB stop |
| G10 `mixed` reachable | MET — repairs EV-STR-003 O-5 |
| G11 Feasibility table | MET — CANNOT FIRE rules removed and recorded (REMOVED-1..3) |
| G12 Ceiling and prohibitions | MET — N-1..N-5, RC-7 inapplicable, UC-7, EV-STR-001 range |
| G13 ID check and provenance | MET — see verbatim block below |

## Verbatim `tools/allocate_id.py --check` (this session)

Re-run 2026-07-30 after the freeze files already existed in the worktree.
`git ls-files experiments/EXP-STR-004` returned empty (untracked only).

```
=== EXP-STR-004 ===
identifier: EXP-STR-004
  well-formed: YES -- matches experiment pattern ^EXP-[A-Z]+-\d{3}$
  occurrences across the union (8346 files scanned): 1
    experiments/EXP-STR-004/specification.yaml

REFUSE: taken. Allocate above the union maximum; never reuse, and never fill a gap.
exit=1
```

Self-occurrence only (this deliverable's directory). Not a collision with another
record. EV-STR-004, DEC-20260729-004, and all 28 `RUN-STR-004-*` identifiers
returned `OK: well-formed and free across the union.` / `exit=0`. Nothing was
renamed.

## Host observations (dispatching session, not archived results)

- `sage`: `/usr/local/bin/sage` — `SageMath version 10.9, Release Date: 2026-05-04`
- disk on `/Volumes/SSD990`: 1.8Ti size, 208Gi used, **1.6Ti available**, 12% capacity
- discrepancy: the BATCH-014 opening note recorded ~30 GiB free / 99% capacity; that
  older figure is retained as historical context and is **not** overwritten
- `.git/index.lock`: absent

## Model provenance

```yaml
requested_policy: coordinator-orchestration-code
resolved_model_id: cursor-grok-4.5  # parent session model; not a policy binding
model_verified: false
model_verification_note: >-
  No `python3 -m orchestration.adapter doctor --probe` was run for this session.
fallback_used: true
fallback_reason: >-
  Claude Code / Cursor subagent frontmatter cannot resolve
  orchestration/model-policies.yaml identifiers; this card ran in the parent
  session after a prior Task() dispatch hit an API usage limit.
degraded_allowed: false
degraded_requirements: []
independent_session_required: false
independence_status: same_session_as_orchestrator
```

## Scope confirmation

- No git commit was made by this card.
- No write outside
  `experiments/EXP-STR-004/{specification.yaml,derivation_note.md}` and
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/tasks/TASK-20260729-040/**`.
- No hypothesis or goal status was changed.
- No experiment was executed (`maximum_runs: 1` is schema-only; semantic runs = 0).

## Defects / notes

1. Freeze body was already present in the worktree when this coordinating session
   resumed after an API-limit failure on a prior subagent dispatch. This session
   audited G1–G13, re-ran the allocator checks, and wrote this report; it did not
   re-author the three producer files from scratch.
2. Feasibility table line claiming the authoring session “had no shell” is
   retained as written by that earlier authoring pass; this report’s shell-backed
   checks supersede it for ID / host facts only.
3. Queue vs mirror: no disagreement found on role, deps, write_scope, or
   deliverables for TASK-20260729-040.
