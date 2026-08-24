# TASK-20260806-411ffd: Ledger archive of BATCH-fca4e2

- **goal:** GOAL-ECTD-001
- **batch:** BATCH-fca4e2
- **role:** coordinator
- **state:** queued
- **priority:** 70
- **depends_on:** TASK-20260806-5bc785
- **review_required:** False
- **archived_by:** TASK-20260806-411ffd (self; ledger archives are terminal)

## Objective

Archive the validator's report, mint and file a new `EV-ECTD-*` evidence
record and a new `DEC-YYYYMMDD-*` decision, set `H-ECTD-001` status per the
validated `decision_branch`, and checkpoint `GOAL-ECTD-001` (batch
checkpoint entry, `current_batch_id`, `latest_verified_commit` advanced to
this archive's own verified commit, exactly one `next_action`).

## Disposition rules (binding; do not overclaim)

| Validated `decision_branch` | Required decision | Notes |
|---|---|---|
| `scoped_homogeneity` | `weaken` | Never `reject_scoped` on a single unreplicated empirical-only run (AGENTS.md binding rule). Forward guidance from H-ECTD-001/EXP-ECTD-001 stands: path-hiding, detection, vertical (017), DDH (018) remain open. |
| `heavy_tail_hit` | `replicate` | Not `support`. No trapdoor/asymptotic language. Schedule a dedicated Red Team pass in the next batch before any stronger disposition — `GOAL-ECTD-001.completion_criteria` requires **both** Validator and Red Team admission of the decisive package; this batch supplies Validator only. |
| `instrument_void` | `pause` or scoped harness-repair `next_action` | Explicitly not a mathematical negative on H-ECTD-001 (AGENTS.md rule 5). |
| `resource_incomplete` | budget-scoped continuation `next_action` | Explicitly not a homogeneity claim. |
| Validator verdict `invalid`/`incomplete` | return to Executor with concrete defects | Not evidence; do not proceed to a hypothesis-status decision. |

## Other constraints

- `knowledge_promotion` is mandatory on the decision record. This is a
  first, unreplicated run — strength cannot exceed `preliminary` regardless
  of outcome, so `promoted: []` with a concrete `not_warranted` reason is
  expected here; a `KN-FIND` becomes warranted only after independent
  replication reaches `replicated`/`strong`.
- Mint all new IDs via `tools/allocate_id.py --next <type> --area|--date <x>
  --check`; never invent an ID by inspection.
- Advance `ledger/goals/GOAL-ECTD-001.yaml.latest_verified_commit` to this
  archive's own verified commit — do not leave it pointing at the prior
  batch's design-snapshot commit (see `SCOPE-DECISION.md` Section 4).

## Completion gate

- Evidence + decision + goal checkpoint committed with exactly one
  `next_action`.
- `knowledge_promotion` filled with a `promoted` list or a concrete
  `not_warranted` reason.
- Dispatcher verifies commit reachability, parent, exact declared paths, and
  matching hashes before this result is official.
