# Independent ICPERF reviews awaiting admission and sealing

- **Status:** open
- **Kind:** access/tool limit; no mathematical obstruction is established
- **Affected work:** [prime63 postrun review plan](../coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml), [Red Team task](../ledger/handoffs/TASK-20261019-02a5c2.yaml), [blind Validator task](../ledger/handoffs/TASK-20261019-bb87e3.yaml), [ICPERF goal](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml). The ordinary-binary m=8 review lane has the same reviewer-policy access requirement; its separate evidence remains separate.
- **Next action owner:** Coordinator to publish the prospective runtime-admission queue; Red Team then resumes its exact verified thread after claim; runtime operator verifies a separate blind Validator session
- **Last updated:** 2026-10-19

## Problem

The committed prime63 m=2 custody snapshot now has one exactly verified, archived `review-adversarial` Red Team session at `xhigh`. It is unclaimed and has produced no review. The tested adapter API and Claude CLI routes failed; a separate independent Validator session has not been verified. The prospective runtime-admission queue must be published before the Red Team card may use the archived receipt and binding.

The affected experiment is `EXP-ICPERF-515ae3`, run `RUN-ICPERF-eb0d88`, over the fixed 63-bit prime field with B=475 and m=2. The postrun plan assigns separate Red Team and blind Validator joints. The additive queue verifies the custody snapshot and offers a reviewer task, but a Ready card is not a valid review. `TASK-20261019-6398fb` cannot compose evidence or retrospectively disposition the experiment until both independent reports, attestations and completed releases exist.

## Evidence and uncertainty

- **Observed:** The earlier adapter API probe found missing API credentials and the Claude CLI probe reported expired OAuth. A direct GPT-6.1 probe failed with `launch_nonzero_exit`; its failed receipt is preserved. A later direct Codex probe verified exact thread `01a156fd-3de0-7230-8f95-96e8e9328627` for Red Team policy `review-adversarial` at `xhigh`, model `gpt-6-sol`, provider `openai`, without fallback or degradation. [The source/copy manifest](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/reviewer-runtime/TASK-20261019-02a5c2/custody-manifest.json) and [snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/archives/TASK-20261019-4a119b/snapshot-receipt.json) bind its exact bytes. The receipt verifies only that thread, not the global backend or a review result.
- **Observed:** The snapshot-binding queue at `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/dispatch_queue.postfailed-RUN-ICPERF-eb0d88.snapshot-candidate.json` passes `research_dispatch.py --ready-only --claims refs` and selects one Red Team card. Neither reviewer has a claim, report, attestation or completed release. The source run retains `invalid_output` and three 600-second positive censors.
- **Derived or proved:** One session-scoped Red Team runtime route meets admission; the handoff correction and reviewer claim have not occurred. The runtime probe says nothing about the mathematics, output-contract correction, factor-base quality or ECDLP cost.
- **Suspected explanation:** The tested Claude CLI's OAuth expiration is observed; whether its credentials or API provider can be restored is unknown. The exact direct Codex route is available for this one Red Team thread; its later resumability under the frozen review handoff remains to be exercised.
- **Missing capability:** A separately verified independent blind Validator runtime and both sealed reviewer outputs. The Red Team also needs the prospective side queue to name its archived runtime records as read-only admission inputs.
- **What this evidence does not establish:** It does not invalidate the custody snapshot, turn a solver censor into a negative result, or justify a factor-base ranking or complete-cost claim.

## What would unblock it

- [x] Verify and archive one exact independent `review-adversarial` Red Team session at `xhigh` without fallback or degradation. Its thread ID is `01a156fd-3de0-7230-8f95-96e8e9328627`, separate from Coordinator session `01a15643-3e5c-7011-83d4-061a5b4857dd`. The archive establishes custody and session admission only.
- [ ] Publish the prospective side queue naming the committed runtime records as Red Team read-only admission inputs; independently verify the archive receipt and queue selector before claim.
- [ ] Verify a separate independent `review-adversarial` blind Validator session at required effort, without fallback or degradation, before its claim. A configured API `doctor --probe` or an exactly receipt-bound direct session can meet this condition.
- [ ] Launch the two review tasks in genuinely independent sessions under their exact published handoffs and blindness rules. Each must produce a write-once report, attestation, and matching completed release; the Validator must avoid the plan's `blind_from` paths until its blind derivation is sealed.
- [ ] Run the independence composer on both reports and archive their exact bytes before any Coordinator evidence decision.

The checked condition restores Red Team session admission only. The remaining conditions and sealed reviews could establish a valid review process for this failed-output run. They would not by themselves provide a solver certificate, natural relation yield, useful rank, a best factor base or an end-to-end speedup.

## Next discriminating step

- **Action or proof obligation:** Archive and verify the runtime-admission side queue; then recheck exact Red Team session metadata and selector before claiming `TASK-20261019-02a5c2`. Separately probe the blind Validator runtime before its later claim.
- **Inputs and controls:** Published snapshot-binding and successor queues, direct runtime snapshot receipt, and standalone review plan; retain the original run, claim/release and candidate hashes. Reject a different or unverified Red Team thread, fallback, degraded binding, reused originating session, or a reviewer that reads its peer's unsealed report.
- **Execution limits and stop condition:** One review task at a time under queue `max_concurrent: 1`; no scientific solver call. Stop at any admission mismatch or model probe failure and preserve the unclaimed task.
- **Outcomes and next actions:** A verified queue and exact resumed thread permit the Red Team review; an admission mismatch stops the claim or review and requires a fresh scoped correction. A failed Validator probe retains its access gap. A report/attestation failure remains a review-process failure, with no scientific inference.
- **Recheck trigger:** Publication of the side queue, Red Team claim attempt, Validator credential or binding change, or a fresh Validator probe.

A planned reviewer step is not a completed review. The active ICPERF goal and all scientific acceptance criteria remain unchanged.

## Resolution and history

Unresolved. The failed-run custody snapshot and one exact Red Team runtime admission are committed and hash-verified; no independent scientific review or final ledger decision has been made. This record and its merge do not seal either review.
