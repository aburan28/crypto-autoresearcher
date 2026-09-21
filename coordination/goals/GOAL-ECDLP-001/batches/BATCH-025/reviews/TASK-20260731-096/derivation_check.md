# TASK-20260731-096 — Derivation / protocol check for PA-DS-001-v2-ctrl-structure-null-r2

**Report:** `RT-20260731-096` (path + task id).
**Reviewed snapshot:** `0d13ad5a83f77f35ac3b87194b72ac6be942013f` (TASK-20260731-095; parent `d39ceeed`).
**Parent contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable; sha256 `898304bf…a5636a`; **not** in snapshot commit delta).
**Open decision:** DEC-20260731-025 restores executable structure-null-r2 and supersedes DEC-024 pivot for execution (does not rewrite DEC-024 / `1aa3b957` / `303ae797`).
**Prior disposition:** DEC-20260731-022 closed BATCH-024 as RC-24 non-execution after RT-20260731-083 REVISE on abandoned stubs at `32165e30`. RT079-B3 remained unmet. BATCH-025 re-authors on fresh `-r2` paths.
**Exact object under review:** PA-DS-001-v2-ctrl-structure-null-r2 / CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2 as admitted at `0d13ad5a` for possible `RUN-DS-001-ctrl-structure-null-r2` authorization by TASK-097.
**Session:** Independent `review-adversarial` (fresh after stall; prior admission had zero artifacts); `resolved_model_id` cursor-grok-4.5; `fallback_used: true`; xhigh not claimable. This session did not author the package. EXP-IT-001 / H-IT-001 at `303ae797` not laundered; TASK-105 out of scope.

**Question:** Is the frozen structure-null-r2 addendum executable and reviewable such that TASK-097 may APPROVE a structure-null-r2 run?

## Verdict

**PASS.** RT079-B3 / RT070-B3 residual is addressed at protocol level; RT-083 abandoned-stub failure is cured by fresh executable paths:

1. **Executable status** — Both PA and CTRL set `status: executable` (not `abandoned_before_archive`, not `cancelled_before_approval`).
2. **RT079-B3 encoded** — `structure_gate_eligible` = (`R < 0.5`) ∧ (`R_null >= 0.9`); `rising_ladder_ok` documented (≤6 cells); `structure_direction_pass` / `structure_direction_fail` required; forbid renaming plant-contrast / `planted_bug_detected` as structure support.
3. **Honest fail** — advantageous R with `R_null` stuck `< 0.9` and no rising ladder ⇒ `structure_direction_fail` (not infra; not lane death / `reject_scoped`).
4. **Hygiene** — Abandoned BATCH-024 stubs untouched (blob-identical to `32165e30`); toy ceiling; parent v2 immutable; no EXP-IT launder; no STR; no H-IC/H-STR edits; no run authorized by this review.

Toy ceiling and deferred CI/SPARSE naming hold. No measurement; no approval issued here. TASK-097 should APPROVE (this reviewer does not).

## Snapshot binding

| Path | sha256 at `0d13ad5a` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_structure_null_r2.yaml` | `29b9f223025a25d7faa2e7fb6573f02dd9d25e8ce18475540350baba66635973` | executable PA |
| `experiments/EXP-DS-001/controls/CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2.yaml` | `fde7a628d503a6c270af71554ddba1e43095e551f17062bed5c2b42240a6e348` | executable CTRL |
| `ledger/decisions/DEC-20260731-025.yaml` | `ea17d7f70139a2a3679e1564f777e0662fbcb2a5ed73baae8f339a282c6a5df4` | restore / supersede DEC-024 |
| `…/BATCH-025/SCOPE-RESTORE-DEC025.md` | `c4e2ea808b081e8c6ea563b95ed70835e3a407610f3c9f01ae28a95a55d66390` | scope restore |
| `…/BATCH-025/QUEUE-AMEND-20260731-013.md` | `eda8ee896dce4ca4d3db3b48fae958649281564207d15dc37b198dc7b0804e27` | restore amend |
| `…/tasks/TASK-20260731-094/task_report.md` | `9b83e9459e87a8902058815a1b7e4273631c031a458c1a24a8997814657a9776` | authoring report |
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | **not** in commit delta |

Abandoned stubs (not edited; not in delta):

| Path | sha256 (same at `0d13ad5a` and `32165e30`) |
|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_structure_null.yaml` | `498fe171502bc9385c4202e1c6db0d132d7c6c26cd90fafc1d8c09e92e9e7d18` |
| `experiments/EXP-DS-001/controls/CTRL-NULL-OBJECT-STRUCTURE-DIRECTION.yaml` | `c32f53eb3004fe977c3eea54c161a618d6f78da3eba558041787d26280ee9032` |

`git merge-base --is-ancestor 0d13ad5a HEAD` succeeds. Commit name-only list excludes all `specification*.yaml`, H-IC/H-STR, and EXP-IT/H-IT freeze paths. Receipt `source_path_sha256` matches recomputed blobs; receipt `commit_sha` is `null` (informational process note I-1, not REVISE-forcing).

## Anti-tautology derivation (why PASS)

### RT079-B3 → structure-null control

EV-DS-007 / RT079 recorded contrastive plant success at cell 16/128/4/102 with `R_null≈0.016≪1`. Inventor-protocol controls-before-belief: structure credit needs null-object packaging where `R_null` rises toward ≥0.9 while `R` stays advantageous; plant flip alone is not structure support (RT079-B3 / RT070-B3).

`CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2` encodes exactly that: `advantageous_R`, `structure_null_ok` (`R_null >= 0.9`), `structure_gate_eligible`, optional `rising_ladder_ok` (≤6), and honest `structure_direction_fail`. Plant-contrast / `planted_bug_detected` cannot be renamed as structure credit. Composing null-split hygiene is reused from `CTRL-RT056-NULL-SPLIT-HARD-DESTROY` without editing that blob.

That is the scientific fix RT079-B3 demanded, encoded as decidable pass/fail bits. Empirical discharge still needs an APPROVED run — and under EV-DS-007 priors, `structure_direction_fail` is the expected scientific outcome, not an infra failure.

### vs RT-083 REVISE

At `32165e30`, PA/CTRL were `abandoned_before_archive` stubs with no RT079-B3 vocabulary; TASK-081 narrative ≠ frozen protocol. At `0d13ad5a`, fresh `-r2` blobs are executable and carry the full vocabulary; authoring report (TASK-094) matches the frozen package; abandoned stubs remain untouched parking markers, not the execution target.

### Decision / scope

DEC-025 vocabulary: approve restores the BATCH-025 structure-null-r2 path for independent RC-25 review — not Executor run, not H-DS-001 support, not lane death, not EXP-IT promotion. SCOPE-RESTORE / QUEUE-AMEND-013 agree. Pivot to SG-ECDLP-002 remains dominated_by finishing RT079-B3.

## Card checklist

| # | Requirement | Status |
|---|---|---|
| 1 | `status: executable` on PA and CTRL | **met** |
| 2 | Structure credit requires `R_null ≥ 0.9` (or rising ladder) while `R` advantageous | **met** |
| 3 | `structure_gate_eligible` / `structure_direction_pass` / `structure_direction_fail` present | **met** |
| 4 | Honest `structure_direction_fail` allowed (not infra / lane death) | **met** |
| 5 | Fresh `-r2` paths; abandoned BATCH-024 stubs not edited | **met** |
| 6 | Toy ceiling; no EXP-IT launder; no STR; no H-IC/H-STR edits | **met** |
| 7 | No run authorized by this review; RC-25 one-cycle understood | **met** |

## Scope of this check

Pre-execution review of the admitted structure-null-r2 snapshot only. No cells measured. No approval issued. No Executor authorization. Companion `contract_review.yaml` carries the full gate ledger. Protocol PASS does not assert empirical structure-null success.

## Coordinator handoff

On PASS: TASK-20260731-097 should record `APPROVAL_DETERMINATION: APPROVED` and may authorize `RUN-DS-001-ctrl-structure-null-r2` only against `CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2` into `results/ctrl_structure_null_r2`. Mark TASK-096 completed and regenerate the BATCH-025 plan outside this write_scope. Do not alter H-IC-001 / H-STR-002. Do not launder EXP-IT. Do not edit abandoned BATCH-024 stubs. Do not admit TASK-105.
