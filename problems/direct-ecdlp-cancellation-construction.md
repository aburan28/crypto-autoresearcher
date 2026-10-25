# Direct ECDLP tagged counting lacks an EC-specific constructive rule

- **Status:** open
- **Kind:** EC-specific construction/proof gap; finite instrumentation and scientific admission now completed
- **Affected work:** [original plan](../docs/reports/direct-ecdlp-cancellation-20261025/PLAN.md), [experiment programme](../docs/reports/direct-ecdlp-cancellation-20261025/programme/EXPERIMENTS.md), [readiness](../docs/reports/direct-ecdlp-cancellation-20261025/programme/READINESS.json)
- **Next action owner:** design/implementation lane for a new rule; the admitted pilot executor and archive tasks are completed
- **Last updated:** 2026-10-25

## Problem

We cannot test a new direct classical ECDLP cancellation algorithm because no public EC-specific rewrite with a constructive cost bound and compositional invariant has been supplied.

For a non-anomalous prime-field curve, prime-order P of order r and public Q=[k]P, canonical scalar range and a total uniquely witnessed scalar program define a square-zero-ring tagged count Z_Q=(1,k). This is known algebraic model counting. Computing it by enumeration costs O(r) scalar evaluations. A small final response does not construct an inexpensive evaluator. Coefficient-prefix, target-local quotient and exact-residue successor proposals share this gap; they are not independent evidence for a solver.

The requested outcome is a novel classical non-generic algorithm outside index calculus, with complete correctness and cost evidence. The current work does not meet that outcome. Neither quantum methods nor factor-base pipelines are dependencies or proposed workarounds.

## Evidence and uncertainty

- **Observed:** fixed development C++ fixtures over p=5,17,23 pass 13,731 assertions, including 2,362 exact one/two-step tagged boundary checks against known fixed-window arithmetic. [Checks and receipts](../docs/reports/direct-ecdlp-cancellation-20261025/programme/CHECKS.md) retain source digests and failed attempts. These are development checks, not admitted scientific trials, gate-level wire verification, performance measurements or independent-session review.
- **Later observed:** [EXP-ECDLP-fe3337 / RUN-ECDLP-d7f049](../experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z/HEADER.md) completed an admitted eight-fixture pilot with real deterministic Boolean EC circuits, 828,896 tagged boundary cells and all ten diagnostic tracks. Exact-byte preapproval passed, the selector was ready, the published executor claim preceded launch, and the genuine supervisor records output validation. The isolated 111-path archive commit `6689f7036932ba0a4e9a9a6b6511af285a7987a0` passed the repository Git verifier. This is toy instrumentation/observation, not a new cancellation identity or independent scientific review.
- **Fresh follow-up observed:** [EXP-ECDLP-7c0b1e / RUN-ECDLP-0b7dd5](../experiments/EXP-ECDLP-7c0b1e/reports/run-20261025T0651Z/HEADER.md) completed 3,624 rows on 24 fresh 8/10/12-bit subgroup fixtures and 192 public targets. A public-input approximate decoder now exists; its controls and complete construction costs establish no algorithmic advantage. Exact pair-entropy gaps are smaller than the pilot; unary gaps have mixed signs. The enlarged rational grammar has 16 AND-only survivors but zero joint AND-and-pin survivors. A [characteristic-two invariant](../harness/classical_ecdlp_followup/theory/pin-obstruction.md) obstructs invertible independent local gauges of the fixed isolated AND tensor; it does not obstruct block grouping, elimination or sums. The exact archive receipt `3e6ca92887e07e4d9a1710eddd8c450e70fc86fa` binds 349 paths. No EC-specific cancellation constructor follows from this.
- **Derived:** the tagged response returns k under canonical uniqueness. The full point-state fixed-window matrix has binary rank r−1 for odd r; its [proof and scope](../docs/reports/direct-ecdlp-cancellation-20261025/programme/window-control.md) obstruct only small exact rank-one decompositions of that flattening. This is not a lower bound for arbitrary coordinate or target-local algorithms.
- **Suspected explanation:** unknown. Generic counting may remain expensive, but no blanket impossibility is established.
- **Missing capability:** an explicit EC-specific replacement rule with a cheap constructor and composition proof, followed by a complete target decoder and full-cost comparison. The gate/carry compiler, local certified fixtures, bounded common-basis grammar and normal pilot admission are now implemented. All 48 invertible bases in that finite grammar fail its signature test; this does not close other bases, block groupings or target-local constructions.
- **What this evidence does not establish:** novelty, low complexity, security, a complete solver, an asymptotic exponent, or exhaustion of all classical approaches. Runtime censoring and missing constructors are not mathematical negative results.

## What would unblock it

- [ ] Supply a finite public procedure from (E,P,Q), without k, planted labels or an uncharged inverse table, identifying all retained boundary variables and computing its replacement object with recorded costs.
- [ ] Prove equality of every tagged coefficient on all declared boundaries, or a stated narrower invariant closed under composition; check all finite tiny boundaries, exceptions and deliberately corrupted candidates.
- [ ] Give a uniform construction/composition cost analysis, including coefficient growth, constructor and schedule search, storage, decoding and verification. Separate an identity from a proposed performance claim.
- [x] For the finite diagnostic pilot, bind exact source/input hashes, certified fixtures, trial plan, launcher, archives, lawful lane and executor queue, with genuine prospective `approvable: true`, committed approval and selector `ready`. A future candidate/scale uses a fresh contract and repeats normal admission.

The first three conditions establish a concrete testable mechanism at its stated scope. They do not establish a full solver gain, asymptotics or novelty. The last admits its scientific measurement; independent reconstruction, prior-art collision review and matched full-cost baselines remain downstream.

## Next discriminating step

- **Action:** use the now-implemented [gate/block instrument](../harness/classical_ecdlp_pilot/src/circuit.cpp) to test a newly supplied EC-specific exact identity beyond the known fixed-window rule and the exhausted 48-arm common-basis grammar. A public constructor and invariant must be stated before a new solver-cost study.
- **Inputs and controls:** registered tiny synthetic subgroups, canonical range, identity and exceptional points, independent arithmetic, doubled auxiliary witnesses, XOR elimination, known fixed-window rule, affine injective map, and an explicitly charged tiny permutation.
- **Execution limits:** development fixtures remain fixed and tiny. Scientific samples and host-protection memory/concurrency/watchdog settings are frozen during admission; no arbitrary lifetime campaign cap is introduced.
- **Outcomes:** a counterexample rejects the exact rule revision; no surviving rule exhausts only the frozen grammar; a surviving compositional rule proceeds to a fresh blinded cohort with complete costs. Operational failures are retained and classified separately.
- **Recheck trigger:** a submitted explicit EC-specific identity/constructor, completed gate compiler/grammar, or a genuinely different structural ingredient. Repetition of the tagged-count formula is not a trigger.

## Resolution and history

2026-10-25: named the construction gap while designing all ten classical workstreams. Point-level development scaffolding and finite known controls completed; gate-level construction, scientific admission, experiments, novelty and solver advantage remain unresolved. This report does not alter frozen evidence or an official hypothesis/goal status. No new goal impediment or inventor-protocol obstruction ID was registered; those references remain to be bound when a formal prospective contract is created.

2026-10-25, later: implemented all ten finite diagnostics and completed the genuine admitted pilot. Instrumentation/admission gaps above are updated with linked receipts; original planning evidence remains unchanged. The new campaign is GOAL-ECDLP-087fc3 / H-ECDLP-98a95a. The EC-specific constructive rule, algorithmic advantage and novelty remain unresolved; no original lead disposition or supported/rejected hypothesis status is changed.

2026-10-25, follow-up: completed the separately admitted projection-scale, public-decoder and expanded basis investigation under GOAL-ECDLP-0c7d6f / H-ECDLP-8dfef7. A post-run [fifth-character/interface bound](../harness/classical_ecdlp_followup/theory/character-kernel-bound.md) explains a restricted unary channel and a fixed-signature candidate ceiling; it is neither a bound on the pair-entropy experiment nor a classical ECDLP lower bound. Local-gauge failures leave block cancellation and richer target interfaces open. Finite completion does not close the research problem.
