# Prime63 postrun review composition checker mismatch

- **Status:** open
- **Kind:** implementation and attestation-contract gap; no mathematical obstruction is established
- **Affected work:** [frozen postrun plan](../coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml), [final archive handoff](../ledger/handoffs/TASK-20261019-6398fb.yaml), [checker](../tools/check_review_independence.py), [active goal](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml)
- **Next action owner:** Independent reviewer TASK-20261019-52baee under [the snapshot binding decision](../ledger/decisions/DEC-20261019-6fcb3f.yaml), then Coordinator review archive TASK-20261019-a0ad65
- **Last updated:** 2026-10-19

## Problem

The frozen TASK-20261019-6398fb completion gate requires `tools/check_review_independence.py` to accept the composed P1–P4 review. The first checker could not match explicit P1–P4 IDs, and the original blind Validator used a top-level attestation schema. An archived ID-aware correction and original-session Validator addendum resolved those format mismatches, but independent T1/T2 review then found three false acceptances in the corrected checker. DEC-20261019-da1c84 rejected it as a final composition gate. Neither sealed original reviewer file was rewritten.

This blocks the **final retrospective review decision**, not the active GOAL-ICPERF-e6b6a4 campaign or any mathematical conclusion. RUN-ICPERF-eb0d88 remains `invalid_output`; its three positive solver calls remain censored.

## Evidence and uncertainty

- **Observed:** The original plan and both sealed reports and attestations are bound by the verified four-file snapshot [TASK-20261019-6398fb](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/archives/TASK-20261019-6398fb/snapshot-receipt.json) at `f48fbd115f41ac55d471b85c2bfb762e48093daa`. Both reviewers have matching completed releases. Final archive epoch 1 was [released abandoned](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/claims/TASK-20261019-6398fb.1.release.json) at `60138cdda109b99590d1f29bee15a6d8ce3ddcad` without a ledger decision.
- **Observed:** Passing only `report.md` files to the checker exits 2 because it collects YAML `review_attestation` blocks. Passing both sealed `attestation.yaml` files exits 1: the Validator block is not recognized, while P3/P4 labels do not match the chosen full sentences. The exact failures are reproducible from the frozen plan, checker, and sealed files.
- **Observed independent break:** The completed TASK-20261019-fcedbb report (SHA-256 `c3992f55e055973bae9f0a1392529cf7da53d774a4e58e66050f56863d8be240`) and attestation (`22b4bf62515f91cc206802b38afa3261a82cc6f53d7c3150ed50557bbe8e7d2a`), bound by the verified TASK-20261019-bb606b snapshot and ledger receipts, report T1/T2 breaks. A scalar verdict for a two-joint owner, an empty P3 full statement, and swapped P3/P4 full statements each returned `PASS []` on synthetic fixtures. Wrong-owner, duplicate/wrong-ID, missing-attestation/verdict, sibling-read and blind_from controls rejected. The frozen scientific-plan digest `1242a62527951bd0f2bb7f908fd2be50e85dcd79cf7a0db0dd09d69de64a29db` binds the actual plan; swapped synthetic statements expose missing exact-plan admission, not altered archived bytes. DEC-20261019-da1c84 rejects checker acceptance despite a diagnostic exit-0 PASS on the frozen attestations.
- **Derived:** A Coordinator-generated normalization would invent reviewer testimony about reads and verdicts. A manual comparison can document a process limitation but cannot satisfy the frozen checker-acceptance gate.
- **Implementation explanation:** The initial mismatch came from a plan dialect assumption and a different attestation schema. The current checker accepts an empty explicit-ID statement and a scalar verdict for a multi-joint owner; generic plan semantics also need an external exact-plan binding. These are implementation and admission gaps, not evidence of disagreement in P1–P4 science.
- **Observed v2 source:** TASK-20261019-387c8c released checker and test hashes `546d6cca...` and `220567fd...`; TASK-20261019-b541a8 snapshotted exactly those two paths at `b271ae5e1534db2fe6958af7dae1cba2fe8742f7`, with [verified receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/archives/TASK-20261019-b541a8/snapshot-receipt.json) introduced at `11a4af22ef7cf4f5cf26e01008748e6afe673dd5`. The 79 focused and addendum tests passed; the frozen plan and two archived attestations passed with the externally pinned SHA-256, and the same CLI refused an omitted pin. These are producer checks, pending independent V1/V2 review.
- **Missing capability:** Fresh independent V1/V2 review of that exact source and controls, followed by a scoped operational decision. The original-session Validator clarification is already archived.
- **What this evidence does not establish:** It does not prove the round independent, validate the historical supervisor output contract, supply a solver certificate, rank factor bases, or measure complete IC cost.

## What would unblock it

- [x] TASK-20261019-c9dbad changed explicit-ID matching and TASK-20261019-d6f5cb snapshotted those source bytes. Independent TASK-20261019-fcedbb found the three false acceptances above; DEC-20261019-da1c84 rejected operational acceptance.
- [x] Original Validator thread `01a15726-e967-7983-a7d5-fc8f08bae009` filed a separately released P1/P2 `review_attestation` addendum under TASK-20261019-7b08c1, citing sealed hashes and original and clarification read scopes without peer content. TASK-20261019-bb606b snapshotted it. The post-seal clarification is recorded as a procedure deviation.
- [x] TASK-20261019-387c8c changed only the checker and focused tests; TASK-20261019-b541a8 snapshotted those bytes and the completed release binds its receipt. Producer checks reject the three previously accepted false fixtures under the pinned CLI admission, and prior refusal controls remain tested. Independent confirmation is still required.
- [ ] Fresh independent TASK-20261019-52baee tests every false fixture and TASK-20261019-a0ad65 archives its verdict before operational acceptance.
- [ ] The corrected checker passes on the **frozen** plan, original Red Team attestation and archived Validator clarification under pinned SHA-256 admission; DEC-20261019-3bf0cd binds the exact invocation, independent review and controls.

A positive DEC-20261019-3bf0cd can establish only the corrected tool gate; the blocked TASK-20261019-6398fb requires a separate additive queue before claim. A negative decision preserves the impediment. Neither outcome supplies a scientific performance result or repairs the separate supervisor output-contract defect.

## Next discriminating step

- **Action or proof obligation:** After TASK-20261019-eeb1d8's selector binding is archived and verified, run fresh independent V1/V2 review TASK-20261019-52baee on the exact source snapshot.
- **Inputs and controls:** Frozen plan and sealed attestations; exact source snapshot and completed releases; synthetic passing and known-false checker fixtures. The original Validator's peer-free checkout must not import the Red Team report.
- **Execution limits and stop condition:** `max_concurrent: 1`; no scientific trial or solver call. Stop if code review rejects the patch or the checker still fails.
- **Outcomes and next actions:** If all three previously accepted false fixtures and preserved refusal controls reject under the pinned-plan gate, the Coordinator may record a scoped positive tool decision after archive; any false acceptance yields another explicit correction and leaves the final task blocked. No science is inferred.
- **Recheck trigger:** Independent tool-review verdict, its archive, or a changed checker result.

## Resolution and history

Unresolved. This record preserves the sealed outputs and abandoned epoch as history. Its publication does not finish the review or change scientific status.

- 2026-10-19: Independent first checker review T1/T2 BREAKS archived under TASK-20261019-bb606b; DEC-20261019-da1c84 rejects the gate. The original-session Validator clarification is separately preserved. V2 correction is prospective and final composition remains unclaimed.
- 2026-10-19: V2 checker source and focused tests were released and snapshotted under TASK-20261019-b541a8. DEC-20261019-6fcb3f and CORR-20261019-b2a866 bind an additive successor queue for independent review only; tool acceptance is undecided.
