# Independent ICPERF review route unverified in this workspace

- **Status:** open
- **Kind:** access/tool limit; no mathematical obstruction is established
- **Affected work:** [prime63 postrun review plan](../coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml), [Red Team task](../ledger/handoffs/TASK-20261019-02a5c2.yaml), [blind Validator task](../ledger/handoffs/TASK-20261019-bb87e3.yaml), [ICPERF goal](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml). The ordinary-binary m=8 review lane has the same reviewer-policy access requirement; its separate evidence remains separate.
- **Next action owner:** runtime operator to restore a configured reviewer API or verify an exactly receipt-bound independent direct runtime; Coordinator then rechecks the exact queue and dispatches independent reviewers
- **Last updated:** 2026-10-19

## Problem

The committed prime63 m=2 custody snapshot cannot advance to independent review because the tested reviewer routes failed and no fresh `review-adversarial` reviewer session has yet been verified or claimed at the required effort and independence boundary. Other allowed direct-runtime routes have not been excluded.

The affected experiment is `EXP-ICPERF-515ae3`, run `RUN-ICPERF-eb0d88`, over the fixed 63-bit prime field with B=475 and m=2. The postrun plan assigns separate Red Team and blind Validator joints. The additive queue verifies the custody snapshot and offers a reviewer task, but a Ready card is not a valid review. `TASK-20261019-6398fb` cannot compose evidence or retrospectively disposition the experiment until both independent reports, attestations and completed releases exist.

## Evidence and uncertainty

- **Observed:** `python3 -m orchestration.adapter doctor --probe` in the 2026-10-19 worktree reported the tested credentialed API backends unusable because their API-key environment variables were unset; the local model listing probe was not available. The bound default API `review-adversarial` model remains unverified in this workspace. A no-tools one-turn `claude -p` probe with the configured reviewer model and `--effort xhigh` returned `is_error: true` and `Failed to authenticate: OAuth session expired and could not be refreshed`. The local probe outputs were inspected in this session but are not archived as research evidence. No independent direct Codex/Claude reviewer has yet been verified or claimed.
- **Observed:** The snapshot-binding queue at `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/dispatch_queue.postfailed-RUN-ICPERF-eb0d88.snapshot-candidate.json` passes `research_dispatch.py --ready-only --claims refs` and selects one Red Team card. Neither reviewer has a claim, report, attestation or completed release. The source run retains `invalid_output` and three 600-second positive censors.
- **Derived or proved:** Only the review-admission requirement is unmet. The backend probe says nothing about the mathematics, output-contract correction, factor-base quality or ECDLP cost.
- **Suspected explanation:** The tested Claude CLI's OAuth expiration is observed; whether credentials or a provider service can be restored is not known. A direct Codex/Claude review route may be available, but requires exact policy and receipt verification.
- **Missing capability:** A fresh independent session resolving the declared `review-adversarial` policy without fallback or degradation, with model serving verified by a configured API probe or an exactly receipt-bound direct-runtime session.
- **What this evidence does not establish:** It does not invalidate the custody snapshot, turn a solver censor into a negative result, or justify a factor-base ranking or complete-cost claim.

## What would unblock it

- [ ] Restore a configured API backend and obtain a successful `python3 -m orchestration.adapter doctor --probe` for the exact `review-adversarial` model and requirements, or verify a fresh exactly receipt-bound direct Codex/Claude session under the same policy without fallback or degradation. The direct session must be independent of Coordinator session `01a15643-3e5c-7011-83d4-061a5b4857dd`. Record the resolved model, requested `xhigh` effort, actual effort, backend and verification in each new review receipt.
- [ ] Launch the two review tasks in genuinely independent sessions under their exact published handoffs and blindness rules. Each must produce a write-once report, attestation, and matching completed release; the Validator must avoid the plan's `blind_from` paths until its blind derivation is sealed.
- [ ] Run the independence composer on both reports and archive their exact bytes before any Coordinator evidence decision.

The first condition restores admission only. The second and third could establish a valid review process for this failed-output run. They would not by themselves provide a solver certificate, natural relation yield, useful rank, a best factor base or an end-to-end speedup.

## Next discriminating step

- **Action or proof obligation:** Run the read-only adapter probe after API restoration or verify an exactly receipt-bound independent direct runtime, resolve `review-adversarial` for a fresh Red Team session, and compare the result with the handoff's model and effort requirements before claiming `TASK-20261019-02a5c2`.
- **Inputs and controls:** Published snapshot-binding queue and standalone review plan; retain the original run, claim/release and candidate hashes. Reject an unverified model, fallback, degraded binding, reused originating session, or a reviewer that reads its peer's unsealed report.
- **Execution limits and stop condition:** One review task at a time under queue `max_concurrent: 1`; no scientific solver call. Stop at any admission mismatch or model probe failure and preserve the unclaimed task.
- **Outcomes and next actions:** A verified binding permits ordinary independent review dispatch. A failed or unavailable probe retains this impediment and prompts runtime repair, with no scientific inference. A report/attestation failure remains a review-process failure requiring a fresh scoped correction.
- **Recheck trigger:** Credential or binding change, successful API probe, or a fresh direct-runtime session with equivalent exact policy and receipt verification.

A planned reviewer step is not a completed review. The active ICPERF goal and all scientific acceptance criteria remain unchanged.

## Resolution and history

Unresolved. The custody snapshot is committed and hash-verified; no independent scientific review or final ledger decision has been made. This record and its merge do not solve the backend problem.
