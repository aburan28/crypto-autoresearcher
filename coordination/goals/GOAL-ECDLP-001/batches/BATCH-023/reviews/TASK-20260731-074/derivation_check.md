# TASK-20260731-074 — Derivation / protocol check for PA-DS-001-v2-ctrl-plant-contrast

**Report:** `RT-20260731-074` (path + task id).
**Reviewed snapshot:** `f41fd196e1cf0345c903b68d4326b311e5ea573b` (TASK-20260731-073; parent `1bd8cd5b`).
**Parent contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable; sha256 `898304bf…a5636a`; **not** in snapshot commit delta).
**Prior disposition:** DEC-20260731-017 closed BATCH-022 theater-r2 inconclusive (EV-DS-006; RT070-B1–B6). DEC-20260731-018 opens BATCH-023 plant-contrast addendum for RC-23 review only — not Executor run.
**Exact next action under review:** BATCH-023 — CTRL-PLANT-CONTRASTIVE-F2 under PA-DS-001-v2-ctrl-plant-contrast; CI-IDENTITY / SPARSE-P-SUCCESS / structure-null deferred.
**Session:** Independent `review-adversarial`; `resolved_model_id` cursor-grok-4.5; `fallback_used: true`; xhigh not claimable. This session did not author the addendum. Unauthorized `RUN-DS-001-ctrl-theater` ignored as non-binding.
**Question:** Does the frozen CTRL-PLANT-CONTRASTIVE-F2 require plant-OFF fail ∧ plant-ON pass (discriminative), forbid F2-on-F2 credit on already-F2_eligible cells, keep toy ceiling and immutable parent, so TASK-075 may APPROVE?

## Verdict

**PASS.** RT070-B2 / RT047-B3 residual is addressed at protocol level:

1. **Contrastive credit required** — `discriminative_credit` = `plant_off_gate == false AND plant_on_gate == true`, with `null_gate_f2_shape` inlined as `R < 0.5 ∧ R_null < 0.9`. `planted_bug_detected` true only if `contrastive_discriminative` true.
2. **F2-on-F2 forbidden** — crediting detection when `plant_off_gate` is true is forbidden and falsifying; default cell `(20,64,4,seed=101)` is marked known non-discriminative from EV-DS-006.
3. **Honest out** — small ladder (≤6) or `contrastive_fail` as honest negative (not infrastructure failure). No full 54-cell matrix.

Toy ceiling, v2 immutability, deferred CI/SPARSE/structure-null, theater WIP not laundered, and no S1_met promotion hold. No measurement; no approval issued here. TASK-075 should APPROVE.

## Snapshot binding

| Path | sha256 at `f41fd196` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_plant_contrast.yaml` | `e796544a7b42e61e179b5415f1d444e2cb759ce9f65648ba2ffa90ed28650aba` | PA-DS-001-v2-ctrl-plant-contrast |
| `experiments/EXP-DS-001/controls/CTRL-PLANT-CONTRASTIVE-F2.yaml` | `305be6ab5aa3e99f7b89e6f1c77772d9e832d5ba7f81a00803648df6fa662d71` | contrastive plant control |
| `ledger/decisions/DEC-20260731-018.yaml` | `8ad2d63c6e0cad8118a0c188b8ebb29ead40614b061b44727f27254254d566ad` | opens BATCH-023 for review |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-023/SCOPE-DECISION.md` | `cdd6bce26586e1b778ae28aece051ba28f30ce9d987cb9d27e404ae45eb33ee4` | scope decision |
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | **not** in commit delta; parent pin matches |

`git merge-base --is-ancestor f41fd196 HEAD` succeeds. Snapshot path list excludes all `specification*.yaml` and hypothesis records. Working-tree freeze paths match `f41fd196` (`git diff` empty). Receipt `source_path_sha256` matches recomputed blobs.

## Anti-tautology derivation (why PASS)

### RT070-B2 → contrastive discrimination

Theater-r2 (`EV-DS-006`) returned `planted_bug_detected=true` via closed `null_gate_f2_shape` on a cell whose **plant-OFF** primary costs already satisfied `R≈0.0345 < 0.5 ∧ R_null≈0.044 < 0.9`. The gate outcome was entailed by pre-plant F2 shape, not by detecting `/4`. RT070 required: evaluate the gate on plant-OFF and plant-ON costs; credit detection **only** when plant-OFF fails and plant-ON passes (or an adjacent cell showing that contrast).

`CTRL-PLANT-CONTRASTIVE-F2` encodes exactly that: `primary_costs_plant_off` vs `costs_as_read_by_gate`; `contrastive_discriminative`; forbid credit when plant-OFF already F2; ladder or honest `contrastive_fail`. Closed-path hygiene (`/4` before gate; enum; `echo_entailment_check=false`) is retained via extension of `CTRL-RT056-PLANT-CLOSED-PATH` without editing it. Composing null-split is required for contrast feasibility under `/4`.

That is the scientific fix RT070-B2 demanded, encoded as a decidable pass bit. Empirical discharge still needs an APPROVED run.

## Card checklist

| # | Requirement | Status |
|---|---|---|
| 1 | Plant-OFF fail ∧ plant-ON pass for detection credit | **met** |
| 2 | Forbid F2-on-F2 / non-discriminative credit on already-F2_eligible cells | **met** |
| 3 | Ladder ≤6 or honest contrastive_fail; no full 54-cell | **met** |
| 4 | Parent v2 immutable; theater-r2 / BATCH-021 freeze not mutated | **met** |
| 5 | Toy ceiling; no run until TASK-075; no H-IC/H-STR; RC-23 one cycle | **met** |
| 6 | Deferred CI / SPARSE / structure-null named | **met** |

## Scope of this check

Pre-execution control-addendum review only. No cells measured. No approval issued. Companion `contract_review.yaml` carries the full gate ledger. Protocol PASS does not assert empirical discriminative plant detection.

## Coordinator handoff

On PASS: TASK-20260731-075 should record `APPROVAL_DETERMINATION: APPROVED` and may authorize `RUN-DS-001-ctrl-plant-contrast` only. Ignore unauthorized `RUN-DS-001-ctrl-theater`. Mark TASK-074 completed and regenerate the BATCH-023 plan outside this write_scope.
