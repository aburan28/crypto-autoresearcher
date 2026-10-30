# NIST dual archive identity and later source custody

- **Status:** open
- **Kind:** source-custody implementation gap; independent-review serving limit
- **Affected work:** GOAL-NISTSEED-ab8949, PR #2602; [source inventory](../coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-921b7b/source-inputs.json), [DEC-20261027-9eed13](../ledger/decisions/DEC-20261027-9eed13.yaml)
- **Next action owner:** Coordinator, TASK-20261027-9b7b37
- **Last updated:** 2026-10-27

## Problem

The nine colliding paths cannot be integrated by choosing one side without losing historical completed provenance. Both f80 main and 592 branch snapshots bind zero-run mocked producer artifacts under the same task IDs; four branch-head AA artifacts subsequently evolved. The later source-reported real A/A is a third version, not the 592 archive and not validated here.

## Evidence and uncertainty

- **Observed:** The pinned inventory includes full commit, blob and SHA256 identities for all nine paths at both snapshots and both published lineages, plus both six-path archive maps. Each map hashes correctly at its own snapshot.
- **Derived or proved:** Exact byte differences only; no scientific conclusion.
- **Suspected explanation:** Parallel historical publication reused identities; provenance alone does not adjudicate scientific claims or source ownership.
- **Missing capability:** A reviewed native successor/CORR representation preserving both bindings. The available openai-gpt61 backend currently lacks a review-adversarial binding.
- **What this evidence does not establish:** Mergeability, historical ECPP use, omission mechanism, primality, security, or validity of later reported real runs. Local T-5518 lookup returned 404; global ownership is unknown.

## What would unblock it

- [ ] Independently rederive all nine identities and both complete receipt maps, preserving claim/release lineage and distinguishing later source evolution.
- [ ] A native-validator-supported prospective successor namespace/CORR mapping changes no completed binding; otherwise record the exact unsupported field/check and stop.
- [ ] Snapshot, independent custody review, administrative ledger archive and normal publication gates verify before a separately ranked integration act.

These establish administrative custody only. Scientific protocol, runtime/custody availability, approval, admission and execution remain separate obligations.

## Next discriminating step

- **Action:** Publish the bounded BATCH-921b7b envelope, then claim TASK-20261027-9b7b37 under native gates.
- **Inputs and controls:** Pinned main f80, branch 592, current main and branch head; reject collapse by duplicate TASK ID and reject labeling evolved c24f producer as archived at 592.
- **Execution limits and stop:** Source-only Git reads and new-scope documents, memory 2 GiB, concurrency one, zero scientific/VM/storage operations. Never touch original bindings or PR heads.
- **Outcomes:** A feasible map goes to isolated snapshot and independent review; an unsupported map records a structural obstruction; missing inputs/ownership or serving route remains inconclusive. No source integration happens in this batch.
- **Recheck trigger:** Published producer snapshot, newly available independent review binding, or new exact source/owner evidence.

## Resolution and history

Unresolved. This record is a custody followup distinct from the existing [A/A and storage-delivery problem](nistseed-aa-control-and-store-delivery.md). Preparing or merging it resolves neither problem.
