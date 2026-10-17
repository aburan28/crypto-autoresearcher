# Full-width index-calculus arity grid has no complete measurement

- **Status:** `investigating`
- **Kind:** implementation gap; resource limit; missing measurement. No mathematical obstruction is claimed.
- **Affected work:** [2026-10-16 baseline and factor-base assessment](../docs/reports/2026-10-16-elite-factor-base-baseline.md); [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml); [prime-field implementation](../src/crypto_autoresearcher/index_calculus/README.md); [ordinary-binary arity-3 obstruction](../research/conductor_relation_yield_20261014/OBSTRUCTION.md).
- **Next action owner:** Coordinator for a frozen runnable contract; Executor for implementation and trials under that contract.
- **Last updated:** 2026-10-16

## Problem

The requested complete end-to-end comparison for prime, Koblitz, and ordinary binary curves with subgroup order near 2^50–2^63 and decomposition arities 2–8 cannot yet be established: this checkout has one independently reviewed complete Koblitz N53 baseline, but the prime-field complete-solve arity ladder stops at 32 bits and m=7, and an ordinary-binary complete-solve baseline at the requested size is not identified. The original acceptance criterion is a verified measured improvement over each applicable index-calculus baseline with a whole-problem `S` including base construction, relation yield, useful rank, linear algebra, target work and verification; every row also retains matched rho distance.

## Evidence and uncertainty

- **Observed:** [RUN-KIC-e3dbed](../research/cold_single_ic_20260921/REPORT.md) reports 24 held-out N53 cold-start same-point pairs and independent review. [RUN-KIC-8b5038](../research/cold_capacity_ic_20260921/REPORT.md) reports a distinct 24-target capacity comparison. The [prime arity ladder](../src/crypto_autoresearcher/index_calculus/README.md) completed m=2..7 through 32 bits and states that its compact numpy path stops below 2^32. [GF(2^51) relation study](../research/conductor_relation_yield_20261014/OBSTRUCTION.md) names an exact arity-3 collector/checker and point-map evaluator gap; it is not a full ECDLP pipeline.
- **Derived:** Under the current prime engine's stated default-base and h-point-tail formulas, an m=8 tail array alone has an approximate 2.17 GiB payload at 2^50 and 201 GiB at 2^63, before process and sort overhead. The m=7 values are approximately 16.3 GiB and 2.81 TiB. These are preflight capacity calculations, not memory measurements or impossibility results; smaller bases and different algorithms alter them.
- **Suspected explanation:** Wide-prime table representation and memory are practical bottlenecks for a direct extension. Whether a streaming join, alternative base density, or solver-aware structured base yields a lower complete cost is unknown.
- **Missing capability:** A bounded >32-bit prime-field complete-solve runner, a verified ordinary-binary 50–63-bit complete-solve runner, and a frozen high-arity direct `S_8` / chained `S_3` comparison that distinguishes seven from eight summands.
- **What this evidence does not establish:** It does not rule out useful factor bases, high-arity decompositions, or end-to-end improvements. A capacity estimate is not a solver runtime or a failed search. Separate families and target panels cannot be pooled into a single speed ratio.

## What would unblock it

- [ ] A committed, runnable frozen protocol identifies at least one exact public curve, prime subgroup and known-answer target schedule per family in the 50–63-bit range, with independently checked scalar recovery and matched rho on the identical unseen points.
- [ ] Its source and receipts support arities 2–8 or preserve a distinct, explicit `unavailable`, `censored`, or `invalid` result for each unexecuted cell; direct `S_8` and eight-summand `S_9` or chained systems have unambiguous labels. Resource caps, seeds, controls and stopping rules are frozen before trials.
- [ ] At least one candidate/base comparison records target-blind base selection, exact realized size and digest, input and observed solving degree, sparsity, every attempt, verified useful rank, complete phase costs, peak memory, and independent replay. A quantitative improvement claim passes `tools.progress_fidelity validate` with a matched baseline and the remaining rho gap.

The first two conditions establish a trustworthy baseline matrix and honest censoring. The third would establish a scoped candidate comparison if it passes review. None alone proves scaling beyond the tested curve, size or target schedule.

## Next discriminating step

- **Action or proof obligation:** Freeze a 50–53-bit three-family pilot with one existing Koblitz baseline arm, a prime and an ordinary-binary baseline arm, and memory preflight for m=2..8; implement only the missing exact runners needed for admission. Pair each candidate base with its equation formulation.
- **Inputs and controls:** Public known-answer targets held out from factor-base selection; size-matched random and affine-placement bases; planted correctness and independent point-sum checks; same-point matched rho; rank/duplicate controls. Keep Koblitz, ordinary binary and prime-field representations separate.
- **Execution limits and stop condition:** A Coordinator-approved finite fixture/seed grid and justified per-process memory watchdog; do not infer a campaign budget cap. Stop a cell on its declared resource or time boundary and preserve the partial record as censored.
- **Outcomes and next actions:** A complete candidate improvement advances to independent review and full-cost claim validation. A complete non-improvement redirects base/solver co-design in the exact tested scope. A timeout narrows the implementation/capacity question. An invalid certificate triggers a new source/protocol revision before any repeat.
- **Recheck trigger:** Publication of a runnable full-width runner, an m=8/direct-`S_8` experiment contract, or a verified 50–63-bit complete-solve receipt.

A planned step is not a completed experiment. Apply existing execution, review, budget and archival rules before acting on it.

## Resolution and history

- 2026-10-16: Opened from the source-linked baseline assessment. Unresolved. The record preserves the original end-to-end requirement and asserts no scientific status transition.
