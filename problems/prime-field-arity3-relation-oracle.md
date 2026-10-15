# Prime-field arity-3 useful-relation enumerator and verifier

- **Status:** `open`
- **Kind:** implementation gap; intermittent Conductor authentication and database lock timeouts were a separate access/tool limit.
- **Affected work:** [study report](../research/conductor_relation_yield_20261014/README.md), [prospective plan](../research/conductor_relation_yield_20261014/plan.json), prospective `H-ECTD-e88346` / `EXP-ECTD-0cf008` (IDs allocated and checked, formal records not written).
- **Next action owner:** Coordinator for contract admission; Executor for implementation after a valid handoff.
- **Last updated:** 2026-10-14.

## Problem

The fixed 29-bit and 37-bit prime-field conductor pairs cannot yet yield the requested arity-3 native useful-relation comparison because this repository has no committed exact triple enumerator, independent verifier, or admitted launcher for the 32,768-target schedule in `plan.json`.

The previous `crypto` ecbench pair sessions implement an arity-2 MITM IC pipeline with 256 and 2,048 abscissae, respectively. They do not enumerate all three-point representations of the selected target stream or implement the exact distinct-row/rank definition in this plan. Reusing their hit rates would answer a different question. The `GF(2^51)` selected degree-271 edges also lack a general serialized point evaluator and dual, so a same-point transported-base arm is separate future work.

## Evidence and uncertainty

- **Observed:** The archived external specs under `crypto/research/ecbench_conductor_gap_20261012/specs/` bind the two endpoint pairs and `ic.pipeline` with `mitm:m=2`. `cryptanalysis/experiments/volcano-ic/README.md` records a completed binary-field arity-2 census; it supplies calibration only. Conductor initially returned `401 unauthenticated` and later PostgreSQL lock-timeout `500` responses; the authenticated CLI subsequently admitted and claimed task `T-2911` for this record. These access events are infrastructure history, not relation-yield evidence.
- **Derived or proved:** The all-target ordered-triple sum is `|F|³`, for any finite group and any factor base, by counting each ordered triple once. This identity does not determine useful nonempty-target probability or rank.
- **Suspected explanation:** None is needed; the missing implementation is directly visible from the current program scope. No claim is made that the specified workload is infeasible.
- **Missing capability:** A bounded, exact arity-3 enumerator; independent group-law replay and small-group exhaustive reference; fixed-column rank over `F_r`; target-generation and provenance seals; an admitted formal experiment specification.
- **What this evidence does not establish:** No direction or magnitude of native yield difference, no conductor-causal effect, no transported same-point comparison, and no ECDLP cost advantage.

## What would unblock it

- [ ] Implement and commit a deterministic launcher that accepts both hash-bound primary input specs, the two declared secondary P29 floors, and the exact prospective plan schedule without reading the planted log inside the collector; it writes every target outcome and all failure/censor receipts immutably.
- [ ] Pass a separate exhaustive small-group oracle, independent point-addition replay, the isomorphic `u=2` targetwise conservation control, planted triples, and the all-target `|F|³` count identity, including repeated and cancellation cases.
- [ ] Establish a formal `EXP-*` contract whose `newest_experiments` execution state is `ready`, with Coordinator approval/archival and a run handoff. File this problem under `problems/` and index it when coordination access is restored.

These conditions allow the fixed-pair native measurement. They do not construct a degree-ell point evaluator or prove a general conductor law. Map transport and full attack-cost accounting remain separate obligations.

## Next discriminating step

- **Action:** Implement the pair-sum histogram and a disjoint exhaustive oracle on a small prime field, then run only the predeclared controls before admitting the 29/37-bit schedule.
- **Inputs and controls:** Exact [plan](../research/conductor_relation_yield_20261014/plan.json) models; raw and useful triple definitions; planted-sum, transported-base isomorphism, rebuilt-native-base coordinate-sensitivity checks, same-cardinality random signed-pair bases, and early rank-prefix checks.
- **Execution limits:** One worker, 4 GiB memory, 1,800 seconds per endpoint for the eventual scientific run. A control failure stops admission; it is an implementation failure, not negative mathematical evidence.
- **Outcomes:** Passing controls permits the frozen run. A memory or watchdog stop preserves raw receipts and prompts a versioned resource/implementation amendment. A count mismatch prompts oracle repair before measurement. An inconclusive yield contrast triggers sensitivity review without reselecting targets.
- **Recheck trigger:** committed launcher plus restored Conductor authorization for the canonical record and formal handoff.

## Resolution and history

Unresolved. This canonical record was filed after `T-2911` obtained the `problems/` lease. The earlier [draft obstruction](../research/conductor_relation_yield_20261014/OBSTRUCTION.md) is retained as history; it does not supersede this record. No launcher or scientific run is certified by filing it.
