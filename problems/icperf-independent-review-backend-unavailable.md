# Independent ICPERF review awaits blind Validator and archive

- **Status:** open
- **Kind:** reviewer admission and evidence-process gap; no mathematical obstruction is established
- **Affected work:** [prime63 postrun review plan](../coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml), [Red Team task](../ledger/handoffs/TASK-20261019-02a5c2.yaml), [blind Validator task](../ledger/handoffs/TASK-20261019-bb87e3.yaml), [ICPERF goal](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml). Ordinary-binary m=8 has a separate reviewer-access gap.
- **Next action owner:** Coordinator publishes prospective Validator admission; blind Validator owns its sealed P1/P2 report; Coordinator later archives and composes only after both releases.
- **Last updated:** 2026-10-19

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
