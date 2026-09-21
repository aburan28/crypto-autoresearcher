# TASK-20260731-083 — Derivation / protocol check for PA-DS-001-v2-ctrl-structure-null

**Report:** `RT-20260731-083` (path + task id).
**Reviewed snapshot:** `32165e30f79b58f2fe1a3f2643eea264daee4864` (TASK-20260731-082; parent `092281e0`).
**Parent contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable; sha256 `898304bf…a5636a`; **not** in snapshot commit delta).
**Prior disposition:** DEC-20260731-019 closed BATCH-023 plant-contrast inconclusive (EV-DS-007; RT079-B1–B6). DEC-20260731-020 at this snapshot opens BATCH-024 as an SG-ECDLP-002 pivot and marks structure-null WIP `abandoned_before_archive`.
**Exact object under review:** PA-DS-001-v2-ctrl-structure-null / CTRL-NULL-OBJECT-STRUCTURE-DIRECTION as admitted at `32165e30` for possible `RUN-DS-001-ctrl-structure-null` authorization.
**Session:** Independent `review-adversarial`; `resolved_model_id` cursor-grok-4.5; `fallback_used: true`; xhigh not claimable. This session did not author the package. Concurrent EXP-IT-001 / H-IT-001 WIP not in commit — ignored.

**Question:** Is the frozen structure-null addendum executable and reviewable such that TASK-084 may APPROVE a structure-null run?

## Verdict

**REVISE.** The admitted snapshot does not contain an executable control addendum.

1. **Abandoned stubs** — Both PA and CTRL set `status: abandoned_before_archive` with “Do not execute. Do not cite as evidence.” That forbids `RUN-DS-001-ctrl-structure-null`.
2. **RT079-B3 not encoded** — No `structure_direction_pass` / `structure_gate_eligible` requiring `R_null ≥ 0.9` (or rising ladder toward 1) while `R` advantageous under null-object packaging; no forbid renaming plant-contrast / `planted_bug_detected` as `structure_gate`; no honest `structure_direction_fail` outcome vocabulary in the PA/CTRL blobs.
3. **Decision contradiction** — DEC-020 / SCOPE select SG-ECDLP-002 pivot and abandon this WIP; they do not open an executable structure-null package for Executor authorization.
4. **Authoring mismatch** — TASK-081 report narrates R_null≥0.9 pass semantics and residual priority; archived PA/CTRL are abandon markers. Report text is not a frozen protocol.

Toy ceiling, parent-v2 immutability, deferred CI/SPARSE naming, and absence of EXP-IT-001/H-IT-001 freeze files in the commit hold, but they cannot salvage a non-executable package. RC-24 one-cycle: **REVISE ⇒ BATCH-024 non-execution** for this run path. No measurement; no approval issued here. TASK-084 must record **NOT APPROVED**.

## Snapshot binding

| Path | sha256 at `32165e30` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_structure_null.yaml` | `498fe171502bc9385c4202e1c6db0d132d7c6c26cd90fafc1d8c09e92e9e7d18` | abandoned stub |
| `experiments/EXP-DS-001/controls/CTRL-NULL-OBJECT-STRUCTURE-DIRECTION.yaml` | `c32f53eb3004fe977c3eea54c161a618d6f78da3eba558041787d26280ee9032` | abandoned stub |
| `ledger/decisions/DEC-20260731-020.yaml` | `00ff297061ef3e02bbfddb67d29511e34314cd6ec8402be9e7fa2d0b53d1c5e2` | pivot / abandon |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-024/SCOPE-DECISION.md` | `8b665a479c7719a3b57dea434a0b1dbc182a30ba509c1fb68e4d7872abe072d4` | pivot selected |
| `…/tasks/TASK-20260731-081/task_report.md` | `45085c29e2ce36300d70d7027c36d1f47648472a56de561c89b6221949a5da3f` | narrative ≠ protocol |
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | **not** in commit delta |

`git merge-base --is-ancestor 32165e30 HEAD` succeeds. Commit name-only list excludes all `specification*.yaml` and any EXP-IT-001 / H-IT-001 freeze paths. Receipt `source_path_sha256` matches recomputed blobs; receipt `commit_sha` is `null` (process defect B-5).

## Anti-tautology derivation (why REVISE)

### RT079-B3 → structure-null control

EV-DS-007 / RT079 recorded contrastive plant success at cell 16/128/4/102 with `R_null≈0.016≪1`. Inventor-protocol controls-before-belief: structure credit needs null-object packaging where `R_null` rises toward ≥0.9 while `R` stays advantageous; plant flip alone is not structure support (RT079-B3 / RT070-B3).

A PASS review would require that requirement to be frozen as a decidable control addendum (pass/fail bits, forbid renaming plant-contrast as structure_gate, honest `structure_direction_fail`, ≤6-cell ladder or equivalent — not a full 54-cell matrix).

At `32165e30` the PA/CTRL files intentionally discard that content and mark the residual deferred. Parking a residual is not the same as encoding a runnable control. Approving a run against “Do not execute” stubs would fabricate executability.

### Decision / scope

DEC-020 vocabulary: approve opens BATCH-024 as SG-ECDLP-002 design-experiment freeze for independent review — not structure-null Executor run, not H-DS-001 support, not lane death. SCOPE explicitly supersedes uncommitted structure-null WIP as abandoned. Therefore the structure-null run authorization path fails independently of any future IT freeze (IT package absent from this commit and out of scope).

## Card checklist

| # | Requirement | Status |
|---|---|---|
| 1 | Structure credit requires `R_null ≥ 0.9` (or rising ladder) while `R` advantageous | **not met** (absent from PA/CTRL) |
| 2 | Forbid renaming plant-contrast / `planted_bug_detected` as `structure_gate` | **not met** |
| 3 | Honest `structure_direction_fail` allowed (not infra / lane death / reject_scoped) | **not met** in protocol blobs |
| 4 | Deferred CI-IDENTITY / SPARSE named; prior freezes not edited; toy ceiling | **met** (DEC/SCOPE) |
| 5 | Parent v2 immutable; no EXP-IT-001/H-IT-001 package in commit | **met** |
| 6 | Amendment reviewable/executable without full 54-cell matrix | **not met** (abandoned) |
| 7 | RC-24: REVISE ⇒ BATCH-024 non-execution understood | **met** (this disposition) |

## Scope of this check

Pre-execution review of the admitted structure-null snapshot only. No cells measured. No approval issued. No Executor authorization. Companion `contract_review.yaml` carries the full gate ledger and blocking defects B-1–B-5.

## Coordinator handoff

On REVISE: TASK-20260731-084 should record `APPROVAL_DETERMINATION: NOT APPROVED`, must not authorize `RUN-DS-001-ctrl-structure-null`, and must treat the RC-24 structure-null execution path as BATCH-024 non-execution. Mark TASK-083 completed and regenerate the BATCH-024 plan outside this write_scope. Do not alter H-IC-001 / H-STR-002. Do not launder concurrent IT WIP.
