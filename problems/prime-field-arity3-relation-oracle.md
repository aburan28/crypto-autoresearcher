# Prime-field arity-3 useful-relation enumerator and verifier

- **Status:** `open`
- **Kind:** implementation gap; intermittent Conductor authentication and database lock timeouts were a separate access/tool limit.
- **Affected work:** [study report](../research/conductor_relation_yield_20261014/README.md), [prospective plan](../research/conductor_relation_yield_20261014/plan.json), draft [H-ECTD-e88346](../ledger/hypotheses/H-ECTD-e88346.yaml) and [EXP-ECTD-0cf008](../experiments/EXP-ECTD-0cf008/specification.yaml).
- **Next action owner:** Coordinator for contract admission; Executor for implementation after a valid handoff.
- **Last updated:** 2026-10-15.

## Problem

The fixed 29-bit and 37-bit prime-field conductor pairs cannot yet yield the requested arity-3 native useful-relation comparison. The local component implementations pass bounded controls, but there is no published approved contract, post-freeze seed commitment, admitted 20-arm collection, or full-size completeness and resource receipt for the 32,768-target schedule. The Coordinator draft is `review_required`; the readiness selector requires an already approved, frozen specification and committed dispatcher binding, so readiness cannot be checked before approval under the current tool ordering.

The previous `crypto` ecbench pair sessions implement an arity-2 MITM IC pipeline with 256 and 2,048 abscissae, respectively. They do not enumerate all three-point representations of the selected target stream or implement the exact distinct-row/rank definition in this plan. Reusing their hit rates would answer a different question. The `GF(2^51)` selected degree-271 edges also lack a general serialized point evaluator and dual, so a same-point transported-base arm is separate future work.

## Evidence and uncertainty

- **Observed:** The archived external specs under `crypto/research/ecbench_conductor_gap_20261012/specs/` bind the two endpoint pairs and `ic.pipeline` with `mitm:m=2`. `cryptanalysis/experiments/volcano-ic/README.md` records a completed binary-field arity-2 census; it supplies calibration only. Conductor initially returned `401 unauthenticated` and later PostgreSQL lock-timeout `500` responses; the authenticated CLI subsequently admitted and claimed task `T-2911` for this record. These access events are infrastructure history, not relation-yield evidence.
- **Derived or proved:** The all-target ordered-triple sum is `|F|³`, for any finite group and any factor base, by counting each ordered triple once. This identity does not determine useful nonempty-target probability or rank.
- **Suspected explanation:** None is needed; the missing implementation is directly visible from the current program scope. No claim is made that the specified workload is infeasible.
- **Implementation control:** `collector.rs` enumerates exact group-law triples from prepared inputs. `verify_collector.py` independently replays reported triples, target equations, and modular rank; `test_collector.py` exhaustively compares all triple sets and counts across 18 nonidentity targets of a 19-point group and checks both Q-column layouts. The [collector receipts](../research/conductor_relation_yield_20261014/controls/small_group_20261015/insight.md) bind the attempted versions. `prepare_input.py` now constructs the six specified endpoints and four arms; its [algebraic control](../research/conductor_relation_yield_20261014/controls/preparer_20261015/insight.md) checks eight fixed test targets per arm. `exact_interval.py` has [integer-tail controls](../research/conductor_relation_yield_20261014/controls/exact_interval_20261015/insight.md). These are implementation checks, not P29/P37 yield measurements. A full-size completeness run and formally admitted scientific provenance remain missing; the bounded wrapper has only a small-group control.
- **Missing capability:** Formal approved `EXP-*` admission and dispatch binding for the [bounded execution component](../research/conductor_relation_yield_20261014/controls/EXECUTION_WRAPPER_20261015.md); execution of the independent full-size no-hit completeness oracle; a serialized degree-ell point map for any future same-point transport arm; actual post-freeze seed issue, public commitment and post-seal reveal; full-size resource receipts. The separate [ordered-count oracle](../research/conductor_relation_yield_20261014/controls/independent_count_20261015/insight.md) passes the small exhaustive control, but has not checked the frozen panel. The fixed-panel [source and conductor certificate](../research/conductor_relation_yield_20261014/controls/panel_certificate_20261015/insight.md) verifies the selected model identities and conductors; it does not provide the map.
- **What this evidence does not establish:** No direction or magnitude of native yield difference, no conductor-causal effect, no transported same-point comparison, and no ECDLP cost advantage.

## Current coordination impediment

The component and control commits are local on
`codex/conductor-relation-yield-20261014`. A read-only merge-tree preview
against `origin/main` produced a tree without conflicts, but the required
pre-design merge has not been applied: Conductor's `dir:.` conflict check
reported active claims across files that current main would update. The
earlier push of this branch was rejected by automatic approval review because
the external Git remote was not established as trusted. The user subsequently
fully approved publication, and the source branch was pushed. Its integration
branch is based on fetched `origin/main` in an isolated sparse worktree, where
the merge completed without conflicts. These coordination events are not
mathematical results. Formal approval, seed issuance and collection still wait
for a frozen executable plan and admitted dispatcher checks.

## What would unblock it

- [ ] Bind the committed preparer, collector, independent count oracle, verifier, interval inverter and bounded wrapper to a formal approved specification and dispatcher. Commit and publish all 20 prepared inputs before collection; the collector must receive no seed file or planted log.
- [ ] Run the full-size independent ordered-count verifier, exact targetwise `u=2` transported-base count equality, planted-triple and all-target `|F|³` controls under the admitted schedule. The exhaustive small-group oracle and independent point-addition replay have archived local receipts.
- [ ] Establish a formal `EXP-*` contract whose `newest_experiments` execution state is `ready`, with Coordinator approval, archival, publication and a run handoff. The problem is already filed and indexed.
- [ ] Break the preparation/admission dependency with a committed, Coordinator-authorized **preparation-only** stage: freeze the exact source and preparatory contract, issue seeds without collector authority, commit all public commitments and prepared-input digests, then approve the fully bound scientific plan and handoff. Acceptance requires a tool-enforced distinction between preparation authority and trial authority and a post-archive `newest_experiments --experiment EXP-ECTD-0cf008` result of `ready`; provisional status strings or an uncommitted queue do not pass. The present `issue_seeds.py` requires a frozen approved specification, while `newest_experiments.py` filters out nonapproved specifications and requires a valid queue, so the current ordering cannot meet both gates as written.

These conditions allow the fixed-pair native measurement. They do not construct a degree-ell point evaluator or prove a general conductor law. Map transport and full attack-cost accounting remain separate obligations.

## Next discriminating step

- **Action:** Bind the locally committed components to a complete formal contract, publish the source freeze, issue and commit seed/input digests, then run the 20-arm matrix through the admitted dispatcher with all predeclared controls.
- **Inputs and controls:** Exact [plan](../research/conductor_relation_yield_20261014/plan.json) models; raw and useful triple definitions; planted-sum, transported-base isomorphism, rebuilt-native-base coordinate-sensitivity checks, same-cardinality random signed-pair bases, and early rank-prefix checks.
- **Execution limits:** One worker, 4 GiB memory, 1,800 seconds per endpoint for the eventual scientific run. A control failure stops admission; it is an implementation failure, not negative mathematical evidence.
- **Outcomes:** Passing controls permits the frozen run. A memory or watchdog stop preserves raw receipts and prompts a versioned resource/implementation amendment. A count mismatch prompts oracle repair before measurement. An inconclusive yield contrast triggers sensitivity review without reselecting targets.
- **Recheck trigger:** published approved specification and admitted handoff, with Conductor scopes available; the local CLI works while this desktop MCP session remains unauthenticated.

## Resolution and history

Unresolved. This canonical record was filed after `T-2911` obtained the `problems/` lease. The earlier [draft obstruction](../research/conductor_relation_yield_20261014/OBSTRUCTION.md) is retained as history; it does not supersede this record. The bounded execution component passed only the archived 19-point control; no scientific run is certified by filing this record.
