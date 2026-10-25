# Direct ECDLP tagged counting lacks an EC-specific constructive rule

- **Status:** open
- **Kind:** proof gap and implementation gap; scientific admission not yet attempted
- **Affected work:** [original plan](../docs/reports/direct-ecdlp-cancellation-20261025/PLAN.md), [experiment programme](../docs/reports/direct-ecdlp-cancellation-20261025/programme/EXPERIMENTS.md), [readiness](../docs/reports/direct-ecdlp-cancellation-20261025/programme/READINESS.json)
- **Next action owner:** design/implementation lane; formal executor not yet assigned
- **Last updated:** 2026-10-25

## Problem

We cannot test a new direct classical ECDLP cancellation algorithm because no public EC-specific rewrite with a constructive cost bound and compositional invariant has been supplied.

For a non-anomalous prime-field curve, prime-order P of order r and public Q=[k]P, canonical scalar range and a total uniquely witnessed scalar program define a square-zero-ring tagged count Z_Q=(1,k). This is known algebraic model counting. Computing it by enumeration costs O(r) scalar evaluations. A small final response does not construct an inexpensive evaluator. Coefficient-prefix, target-local quotient and exact-residue successor proposals share this gap; they are not independent evidence for a solver.

The requested outcome is a novel classical non-generic algorithm outside index calculus, with complete correctness and cost evidence. The current work does not meet that outcome. Neither quantum methods nor factor-base pipelines are dependencies or proposed workarounds.

## Evidence and uncertainty

- **Observed:** fixed development C++ fixtures over p=5,17,23 pass 13,731 assertions, including 2,362 exact one/two-step tagged boundary checks against known fixed-window arithmetic. [Checks and receipts](../docs/reports/direct-ecdlp-cancellation-20261025/programme/CHECKS.md) retain source digests and failed attempts. These are development checks, not admitted scientific trials, gate-level wire verification, performance measurements or independent-session review.
- **Derived:** the tagged response returns k under canonical uniqueness. The full point-state fixed-window matrix has binary rank r−1 for odd r; its [proof and scope](../docs/reports/direct-ecdlp-cancellation-20261025/programme/window-control.md) obstruct only small exact rank-one decompositions of that flattening. This is not a lower bound for arbitrary coordinate or target-local algorithms.
- **Suspected explanation:** unknown. Generic counting may remain expensive, but no blanket impossibility is established.
- **Missing capability:** a total Boolean gate/carry compiler with unique-wire checks; a frozen finite candidate grammar; an explicit new rule/constructor and composition proof; registered scientific inputs and normal admission packet. No claim is made that a specified new rule failed, since none exists yet.
- **What this evidence does not establish:** novelty, low complexity, security, a complete solver, an asymptotic exponent, or exhaustion of all classical approaches. Runtime censoring and missing constructors are not mathematical negative results.

## What would unblock it

- [ ] Supply a finite public procedure from (E,P,Q), without k, planted labels or an uncharged inverse table, identifying all retained boundary variables and computing its replacement object with recorded costs.
- [ ] Prove equality of every tagged coefficient on all declared boundaries, or a stated narrower invariant closed under composition; check all finite tiny boundaries, exceptions and deliberately corrupted candidates.
- [ ] Give a uniform construction/composition cost analysis, including coefficient growth, constructor and schedule search, storage, decoding and verification. Separate an identity from a proposed performance claim.
- [ ] Bind exact source/input hashes, certified fixtures, trial plan, launcher, archives, lawful lane and executor queue; require repository prospective `approvable: true`, committed approval/archive and selector `execution_state: ready` before scientific dispatch.

The first three conditions establish a concrete testable mechanism at its stated scope. They do not establish a full solver gain, asymptotics or novelty. The last admits its scientific measurement; independent reconstruction, prior-art collision review and matched full-cost baselines remain downstream.

## Next discriminating step

- **Action:** finish the D0 gate-level instrument and D1 exact one/two-step finite grammar in the [programme](../docs/reports/direct-ecdlp-cancellation-20261025/programme/EXPERIMENTS.md). Do not benchmark a missing evaluator.
- **Inputs and controls:** registered tiny synthetic subgroups, canonical range, identity and exceptional points, independent arithmetic, doubled auxiliary witnesses, XOR elimination, known fixed-window rule, affine injective map, and an explicitly charged tiny permutation.
- **Execution limits:** development fixtures remain fixed and tiny. Scientific samples and host-protection memory/concurrency/watchdog settings are frozen during admission; no arbitrary lifetime campaign cap is introduced.
- **Outcomes:** a counterexample rejects the exact rule revision; no surviving rule exhausts only the frozen grammar; a surviving compositional rule proceeds to a fresh blinded cohort with complete costs. Operational failures are retained and classified separately.
- **Recheck trigger:** a submitted explicit EC-specific identity/constructor, completed gate compiler/grammar, or a genuinely different structural ingredient. Repetition of the tagged-count formula is not a trigger.

## Resolution and history

2026-10-25: named the construction gap while designing all ten classical workstreams. Point-level development scaffolding and finite known controls completed; gate-level construction, scientific admission, experiments, novelty and solver advantage remain unresolved. This report does not alter frozen evidence or an official hypothesis/goal status. No new goal impediment or inventor-protocol obstruction ID was registered; those references remain to be bound when a formal prospective contract is created.
