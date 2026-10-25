# ICPERF independent review admission is task-specific

- **Status:** open
- **Kind:** reviewer runtime access and evidence-process gap; no mathematical obstruction is established.
- **Affected work:** [ICPERF goal](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), ordinary binary m=8 review lane, and [v2 output-contract O1-O3 plan](../coordination/review/icperf-prime63-m2-output-contract-v2-20261025/review-plan.yaml).
- **Next action owner:** Coordinator obtains an exact independent review-adversarial xhigh Validator receipt for [TASK-20261025-b2e2cd](../ledger/handoffs/TASK-20261025-b2e2cd.yaml), archives a separate session-bound admission, then allows only that exact thread to review. Ordinary binary m=8 requires its own route.
- **Last updated:** 2026-10-25

## Current 2026-10-25 state

The prime63 postrun P1-P4 review referenced in the historical record below is sealed and composed under [DEC-20261019-471fe2](../ledger/decisions/DEC-20261019-471fe2.yaml). Its direct Codex reviewer sessions do not transfer admission to a new task. The completed v2 no-science source and fixture package now has a verified [ten-file snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-ac3c38/archives/TASK-20261020-fa096d/snapshot-receipt.json), and [DEC-20261025-888555](../ledger/decisions/DEC-20261025-888555.yaml) freezes a separate O1-O3 independent engineering review.

**Observed access:** The default Anthropic review-adversarial resolution is unverified because the tested API route has no usable key. The explicit openai route resolves prospectively to gpt-5.6-sol at xhigh, and exact independent Codex sessions are supported, but no receipt exists for TASK-20261025-b2e2cd. Neither default failure nor prospective resolution proves global unavailability or grants this task a session. The ordinary binary m=8 lane still needs its own task-specific review route.

**What is blocked:** Only the new Validator card and its dependent review snapshot, plus ordinary binary m=8's separate reviewer access. The v2 producer and source snapshot are already completed. This access gap says nothing about source correctness, solver feasibility or ECDLP performance.

**Exit criteria:** After the frozen O1-O3 plan and handoff are committed and pushed, obtain a fresh independent exact-session receipt matching task, validator role, review-adversarial policy, xhigh effort, model/provider/workdir and runtime bindings with no fallback/degradation. Verify lane and claim, archive a separate additive sole-Ready admission, then run the review in the exact receipt-bound thread. A sealed report, attestation and completed release followed by TASK-20261025-6d007d snapshot clear this task's review-process gap; ordinary binary m=8 has its own exit.

**Next discriminating action:** Probe the explicit direct Codex route for TASK-20261025-b2e2cd after publication. If verified, bind and admit only that session. If the probe fails, retain the receipt and exact failure reason, leave the card blocked, and test a different allowed route only after recording its own identity. No scientific solver call or source edit is part of this review.

## Historical 2026-10-19 admission snapshot

The following text preserves the earlier admission-stage account and its then-open actions. Its present-tense references to the blind P1/P2 Validator are historical, not current dispatch instructions.

## Problem

The prime63 m=2 failed-run custody snapshot has two exactly verified independent `review-adversarial` sessions at `xhigh`. The Red Team completed its P3/P4 task with a hash-bound [release](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/claims/TASK-20261019-02a5c2.1.release.json). Its report and attestation bytes remain uncommitted in the Coordinator worktree and are not yet a composed review finding. The blind Validator has no claim, report, attestation or release. Its exact runtime custody is committed, but a prospective side queue must first name those committed runtime files as read-only admission inputs.

The affected experiment is `EXP-ICPERF-515ae3`, run `RUN-ICPERF-eb0d88`, over the fixed 63-bit prime field with B=475 and m=2. The frozen plan assigns independent P3/P4 and blind P1/P2 joints. `TASK-20261019-6398fb` cannot compose evidence or retrospectively disposition the run until the Validator completes, both outputs are archived, and review independence is checked. The source run remains `invalid_output` with three 600-second positive solver censors.

## Evidence and uncertainty

- **Observed:** The earlier adapter API probe lacked usable credentials and a Claude CLI probe reported expired OAuth. A GPT-6.1 direct probe failed with `launch_nonzero_exit`. A later direct Codex probe verified Red Team thread `01a156fd-3de0-7230-8f95-96e8e9328627` at `gpt-6-sol`/`xhigh` with no fallback or degradation. Its [custody manifest](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/reviewer-runtime/TASK-20261019-02a5c2/custody-manifest.json) and [snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/archives/TASK-20261019-4a119b/snapshot-receipt.json) bind exact bytes. Resumed local thread metadata again showed `gpt-6-sol`/`xhigh`; its completed release binds report SHA-256 `b359b009caea5af81cdd76307e0974676f7e920dd138053a576b5239be08cc25` and attestation SHA-256 `c0d6ef21da646a74cdad697d00bbff8f6021ffb330ed2edbc27023bdfbc0b435`. The Coordinator has not interpreted its substantive findings.
- **Observed:** An initial blind Validator probe used backend `openai` and failed before thread launch with `model_policy_mismatch`. The preserved failed receipt does not grant admission. A second probe using the overlay's `openai-gpt6` backend verified exact independent thread `01a15726-e967-7983-a7d5-fc8f08bae009` at `gpt-6-sol`/`xhigh`, without fallback or degradation. Its [custody manifest](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/reviewer-runtime/TASK-20261019-bb87e3/custody-manifest.json) and [snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/archives/TASK-20261019-553ac8/snapshot-receipt.json) bind the exact session and failed control. The detached Validator checkout at Red Team release commit `05bbf1d20b` contains neither Red Team output file.
- **Observed:** The current runtime-admission queue's claims-aware selector offers only the unclaimed Validator card. The prospective validator-admission queue also selects that card and adds five committed runtime custody files only to its admission inputs and read scopes. It must be archived and pushed before use.
- **Derived or proved:** Exact-session reviewer access exists for both named threads. The Red Team has a matching completed process release. Neither establishes the blind Validator's derivation, a joint review finding, factor-base quality or ECDLP cost.
- **Suspected explanation:** The original API and Claude credential failures are operational. The exact direct Codex sessions address these two task-specific routes but do not verify the backend catalog globally or the ordinary-binary m=8 review lane.
- **Missing capability:** Prospective Validator queue publication in its blind checkout, a blind P1/P2 report and attestation with matching completed release, then immutable archive and independence composition of both reports.
- **What this evidence does not establish:** It does not repair the historical supervisor output contract, turn a censor into a mathematical negative, rank a factor base, or support a complete-cost speedup.

## What would unblock it

- [x] Verify and archive exact independent Red Team session `01a156fd-3de0-7230-8f95-96e8e9328627`; publish its corrected admission queue, scoped claim and hash-bound completed release.
- [x] Verify and archive exact independent blind Validator session `01a15726-e967-7983-a7d5-fc8f08bae009` in a detached checkout that excludes Red Team output files. The first failed wrong-backend probe remains preserved.
- [ ] Publish and independently verify the prospective validator-admission side queue and its content-at-commit receipt. Advance the detached checkout to include that commit while confirming both Red Team output paths remain absent. The five runtime custody paths are admission inputs only, never sources for P1/P2 derivation.
- [ ] Claim only the Ready Validator card and resume its exact verified thread at `review-adversarial`/`xhigh`. It must read only its permitted original data for the blind derivation, then publish write-once P1/P2 report and attestation with a matching completed release. No scientific solver call is permitted.
- [ ] Verify and archive both reviewers' exact output bytes and releases, run the independence composer, then let the Coordinator record a scoped decision. The original output-contract failure and missing complete-cost measurements remain separate obligations.

The checked conditions establish session admission and one released review process, not a mathematical or performance result. Completion of the remaining conditions can establish a valid independent review of this failed-output run; it cannot by itself provide natural relation yield, useful rank, a best factor base or end-to-end speedup.

## Next discriminating step

- **Action or proof obligation:** Verify the new side queue's receipt and selector, advance the detached blind checkout, recheck its absence of Red Team outputs and exact Validator session metadata, then claim `TASK-20261019-bb87e3`.
- **Inputs and controls:** Frozen review plan and public P1/P2 source files; runtime custody paths for admission only; Red Team release digest for sequence control without reading its report. Preserve `blind_from` exclusions and reject a different session, fallback, degradation, or accidental peer access.
- **Execution limits and stop condition:** One review task at a time under queue `max_concurrent: 1`; zero scientific solver calls. Stop on admission, identity or blindness mismatch and preserve the unclaimed state.
- **Outcomes and next actions:** A valid blind report and release permit immutable archive and independent composition. A failed or unavailable session preserves the exact access impediment. A reading-scope or attestation failure becomes a review-process failure needing a fresh scoped correction, with no scientific inference.
- **Recheck trigger:** Publication of the validator-admission queue, any claim attempt, a session-binding change, or a new review-process deviation.

A planned reviewer step is not a completed review. The active ICPERF goal and all scientific acceptance criteria remain unchanged.

## Resolution and history

Unresolved. Failed-run custody and two exact session admissions are hash-verified, and the Red Team has a completed release. The blind Validator and final independent composition remain outstanding. This record and its merge do not seal or interpret a joint review.
