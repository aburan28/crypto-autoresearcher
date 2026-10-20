# Prime63 postrun review composition checker mismatch

- **Status:** open
- **Kind:** implementation and attestation-contract gap; no mathematical obstruction is established
- **Affected work:** [frozen postrun plan](../coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml), [final archive handoff](../ledger/handoffs/TASK-20261019-6398fb.yaml), [checker](../tools/check_review_independence.py), [active goal](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml)
- **Next action owner:** Coordinator to publish [the prospective repair decision](../ledger/decisions/DEC-20261019-9e6a84.yaml); checker implementer, independent tool reviewer, and the original Validator then own their separate handoffs
- **Last updated:** 2026-10-19

## Problem

The frozen TASK-20261019-6398fb completion gate requires `tools/check_review_independence.py` to accept the composed P1–P4 review, but the sealed attestations and current checker do not share one machine-readable contract. The Red Team attests P3/P4 by the plan's explicit IDs; the checker instead chooses each full-sentence `joint` value before its `id`. The original blind Validator filed a top-level `independent_blind_review_attestation.v1` rather than a `review_attestation` block and did not supply the checker's complete `sources_read` or enum verdict fields. Neither sealed file may be rewritten to produce a PASS.

This blocks the **final retrospective review decision**, not the active GOAL-ICPERF-e6b6a4 campaign or any mathematical conclusion. RUN-ICPERF-eb0d88 remains `invalid_output`; its three positive solver calls remain censored.

## Evidence and uncertainty

- **Observed:** The original plan and both sealed reports and attestations are bound by the verified four-file snapshot [TASK-20261019-6398fb](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/archives/TASK-20261019-6398fb/snapshot-receipt.json) at `f48fbd115f41ac55d471b85c2bfb762e48093daa`. Both reviewers have matching completed releases. Final archive epoch 1 was [released abandoned](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/claims/TASK-20261019-6398fb.1.release.json) at `60138cdda109b99590d1f29bee15a6d8ce3ddcad` without a ledger decision.
- **Observed:** Passing only `report.md` files to the checker exits 2 because it collects YAML `review_attestation` blocks. Passing both sealed `attestation.yaml` files exits 1: the Validator block is not recognized, while P3/P4 labels do not match the chosen full sentences. The exact failures are reproducible from the frozen plan, checker, and sealed files.
- **Derived:** A Coordinator-generated normalization would invent reviewer testimony about reads and verdicts. A manual comparison can document a process limitation but cannot satisfy the frozen checker-acceptance gate.
- **Suspected explanation:** The checker was written for a plan dialect in which the label begins the `joint` text; this plan has separate `id` and statement fields. The Validator's attestation used a different schema. No evidence here shows a mathematical disagreement between reviewer findings.
- **Missing capability:** A fail-closed ID-aware checker accepted after independent tool review, plus a truthful, original-session Validator clarification attesting the original read inventory and P1/P2 verdicts.
- **What this evidence does not establish:** It does not prove the round independent, validate the historical supervisor output contract, supply a solver certificate, rank factor bases, or measure complete IC cost.

## What would unblock it

- [ ] TASK-20261019-c9dbad changes only explicit-ID matching and regression tests; TASK-20261019-d6f5cb snapshots exact code bytes. Independent TASK-20261019-fcedbb rejects wrong-owner, duplicate-ID, missing-attestation, invalid-verdict, sibling-read and blind-from known-false fixtures before operational acceptance.
- [ ] Original Validator thread `01a15726-e967-7983-a7d5-fc8f08bae009` truthfully files an additive P1/P2 `review_attestation` under TASK-20261019-7b08c1, citing its sealed hashes and complete original and clarification read scopes without peer content. A matching release and TASK-20261019-bb606b snapshot bind it. The post-seal clarification is recorded as a procedure deviation.
- [ ] The patched checker passes on the **frozen** plan, original Red Team attestation and archived Validator clarification. The exact invocation, inputs, independent tool review and failure controls are bound in DEC-20261019-da1c84. Only then may final TASK-20261019-6398fb be re-claimed at epoch 2.

These checks would establish a compliant process gate for a bounded retrospective review. They would not establish a scientific performance improvement or resolve the separate output-contract defect.

## Next discriminating step

- **Action or proof obligation:** Archive [the prospective correction](../ledger/corrections/CORR-20261019-ea1209.yaml) and run the claims-aware selector; dispatch only the checker implementation TASK-20261019-c9dbad first.
- **Inputs and controls:** Frozen plan and sealed attestations; exact source snapshot and completed releases; synthetic passing and known-false checker fixtures. The original Validator's peer-free checkout must not import the Red Team report.
- **Execution limits and stop condition:** `max_concurrent: 1`; no scientific trial or solver call. Stop if code review rejects the patch, the original session cannot attest its reads, or the checker still fails.
- **Outcomes and next actions:** A verified PASS permits a later epoch-2 final archive claim. Any other outcome leaves that ledger gate unmet and requires a new explicit correction or a scoped record of the impediment.
- **Recheck trigger:** Publication of the packet, checker source snapshot, clarification release, tool-review verdict, or a changed checker result.

## Resolution and history

Unresolved. This record preserves the sealed outputs and abandoned epoch as history. Its publication does not finish the review or change scientific status.
