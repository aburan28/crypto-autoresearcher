# Prime-field arity-3 useful-relation enumerator and verifier

- **Status:** `open`
- **Kind:** implementation gap; intermittent Conductor authentication and database lock timeouts were a separate access/tool limit.
- **Affected work:** [study report](../research/conductor_relation_yield_20261014/README.md), [prospective plan](../research/conductor_relation_yield_20261014/plan.json), draft [H-ECTD-e88346](../ledger/hypotheses/H-ECTD-e88346.yaml) and [EXP-ECTD-0cf008](../experiments/EXP-ECTD-0cf008/specification.yaml).
- **Next action owner:** Coordinator for contract admission; Executor for implementation after a valid handoff.
- **Last updated:** 2026-10-15.

## Problem

The fixed 29-bit and 37-bit prime-field conductor pairs cannot yet yield the requested arity-3 native useful-relation comparison. The 20-arm input package and raw preparation attempts were published in PR #2204, but the experiment still lacks a completed correction/supplemental archive receipt, a published approved contract and dispatch queue, admitted collection, and full-size completeness and resource receipts for the 32,768-target schedule. The committed specification remains `review_required`. The readiness selector requires an approved, frozen working-tree specification and a valid trial plan/dispatcher binding; the Coordinator must test that complete provisional tree before committing the separate approval decision and recheck readiness after publication.

The previous `crypto` ecbench pair sessions implement an arity-2 MITM IC pipeline with 256 and 2,048 abscissae, respectively. They do not enumerate all three-point representations of the selected target stream or implement the exact distinct-row/rank definition in this plan. Reusing their hit rates would answer a different question. The `GF(2^51)` selected degree-271 edges also lack a general serialized point evaluator and dual, so a same-point transported-base arm is separate future work.

## Evidence and uncertainty

- **Observed:** The archived external specs under `crypto/research/ecbench_conductor_gap_20261012/specs/` bind the two endpoint pairs and `ic.pipeline` with `mitm:m=2`. `cryptanalysis/experiments/volcano-ic/README.md` records a completed binary-field arity-2 census; it supplies calibration only. Conductor initially returned `401 unauthenticated` and later PostgreSQL lock-timeout `500` responses; the authenticated CLI subsequently admitted and claimed task `T-2911` for this record. These access events are infrastructure history, not relation-yield evidence.
- **Derived or proved:** The all-target ordered-triple sum is `|F|³`, for any finite group and any factor base, by counting each ordered triple once. This identity does not determine useful nonempty-target probability or rank.
- **Suspected explanation:** None is needed; the missing implementation is directly visible from the current program scope. No claim is made that the specified workload is infeasible.
- **Implementation control:** `collector.rs` enumerates exact group-law triples from prepared inputs. `verify_collector.py` independently replays reported triples, target equations, and modular rank; `test_collector.py` exhaustively compares all triple sets and counts across 18 nonidentity targets of a 19-point group and checks both Q-column layouts. The [collector receipts](../research/conductor_relation_yield_20261014/controls/small_group_20261015/insight.md) bind the attempted versions. The [host binary manifest](../research/conductor_relation_yield_20261014/binary_build_manifest.json) binds the actual Rust and C++ executable hashes, and those binaries passed the same bounded control. `prepare_input.py` constructs the six specified endpoints and four arms; its [algebraic control](../research/conductor_relation_yield_20261014/controls/preparer_20261015/insight.md) checks eight fixed test targets per arm. `exact_interval.py` has [integer-tail controls](../research/conductor_relation_yield_20261014/controls/exact_interval_20261015/insight.md). These are implementation checks, not P29/P37 yield measurements. A full-size completeness run and formally admitted scientific provenance remain missing; the bounded wrapper has only a small-group control.
- **Missing capability:** Formal approved `EXP-*` admission and dispatch binding for the [bounded execution component](../research/conductor_relation_yield_20261014/controls/EXECUTION_WRAPPER_20261015.md); execution of the independent full-size no-hit completeness oracle; a serialized degree-ell point map for any future same-point transport arm; post-seal seed reveal; full-size resource receipts. The private roots and public commitment were issued after source freeze and before input generation. The separate [ordered-count oracle](../research/conductor_relation_yield_20261014/controls/independent_count_20261015/insight.md) passes the small exhaustive control, but has not checked the frozen panel. The fixed-panel [source and conductor certificate](../research/conductor_relation_yield_20261014/controls/panel_certificate_20261015/insight.md) verifies the selected model identities and conductors; it does not provide the map.
- **What this evidence does not establish:** No direction or magnitude of native yield difference, no conductor-causal effect, no transported same-point comparison, and no ECDLP cost advantage.

## Current coordination impediment

The integrated source and draft H/EXP contract were merged in PR #2203 at
`4ddd40053ac0c09f909227efd90958e6ae3691cf`. PR #2204 merged the subsequent
binary provenance, preparation-only decision `DEC-20261015-df1003`, batch
`BATCH-fd3847`, public seed commitment, 20 input/manifest/preparatory-admission
triplets, 60 raw attempt files, and the preparation integrity index at
`ee74d0c6dfb84ffcc24799af7c0c848567a67c86`. The public commitment was the
sole file in commit `6c1dd5fc2c3e01faabbf1d2794672f8f03d79a2a`, before
any arm input. The private seeds remain outside the repository. The exact
prepared-input snapshot is `de147a18a880e724e8663967197b267bc47a33e6`,
with its receipt in `7faa81dd778e5d491a6e77eacf0476ad9ba80ba9`; the
raw-attempt supplement is `2f36d1420b1cff0f8e644a0fcf0b820572f060a9`.
All 20 preparatory admissions have `status: prepared` and
`execution_authorized: false`. The integrity index checked 32,768 distinct
targets per arm, native/random target alignment, pointwise `u=2` transport,
and input/source/binary hashes. These are preparation checks, not relation-yield
observations.

The original producer's goal-lane claim was published only after its 20 input
generation calls. [CORR-20261015-a7f0a4](../ledger/corrections/CORR-20261015-a7f0a4.yaml)
records that dispatch-precondition violation and preserves the original claim.
The correction and raw-attempt supplemental handoffs require separate archive
receipts under `coordination/goals/GOAL-ECTD-001/batches/BATCH-fd3847/archives/`.
Conductor task `T-354`, a concurrent isogeny-volcano campaign, currently owns
`dir:coordination/goals` exclusively and blocks both exact receipt paths and
the new scientific queue under `BATCH-999f49`. This is an active coordination
access limit; it does not change the checked input bytes or supply a scientific
outcome. The provisional H/EXP approval packet, 20 separate scientific
admissions, and trial plan are drafted but uncommitted while the queue cannot
pass `newest_experiments` readiness.

## What would unblock it

- [ ] Bind the committed preparer, collector, independent count oracle, verifier, interval inverter and bounded wrapper to a formal approved specification and dispatcher. The 20 prepared inputs are published; preserve their hashes and keep seed files and planted logs outside the collector.
- [ ] Run the full-size independent ordered-count verifier, exact targetwise `u=2` transported-base count equality, planted-triple and all-target `|F|³` controls under the admitted schedule. The exhaustive small-group oracle and independent point-addition replay have archived local receipts.
- [ ] Establish a formal `EXP-*` contract whose `newest_experiments` execution state is `ready`, with Coordinator approval, archival, publication and a run handoff. The problem is already filed and indexed.
- [ ] Seal the separate correction and raw-attempt supplemental archive receipts once `T-354` releases or narrows `dir:coordination/goals`. The 20 preparation triplets, their hashes, and the independent integrity index are already published. Then test the exact provisional approved spec/plan/queue tree with `newest_experiments`, commit a separate approval decision only if that tree is `ready`, and recheck `ready` after publication. Prepared admissions remain separate from the new scientific admissions.

These conditions allow the fixed-pair native measurement. They do not construct a degree-ell point evaluator or prove a general conductor law. Map transport and full attack-cost accounting remain separate obligations.

## Next discriminating step

- **Action:** After `T-354` frees `dir:coordination/goals`, write and publish the two exact archive receipts, validate the four-task scientific queue including independent review and ledger archive, and test `newest_experiments` readiness before publishing Coordinator approval. Then run the 20-arm matrix through the admitted dispatcher with all predeclared controls.
- **Inputs and controls:** Exact [plan](../research/conductor_relation_yield_20261014/plan.json) models; raw and useful triple definitions; planted-sum, transported-base isomorphism, rebuilt-native-base coordinate-sensitivity checks, same-cardinality random signed-pair bases, and early rank-prefix checks.
- **Execution limits:** One worker, 4 GiB memory, 1,800 seconds per endpoint for the eventual scientific run. A control failure stops admission; it is an implementation failure, not negative mathematical evidence.
- **Outcomes:** Passing controls permits the frozen run. A memory or watchdog stop preserves raw receipts and prompts a versioned resource/implementation amendment. A count mismatch prompts oracle repair before measurement. An inconclusive yield contrast triggers sensitivity review without reselecting targets.
- **Recheck trigger:** Conductor releases or narrows `T-354`'s `dir:coordination/goals` claim; then the exact receipt and queue paths can be claimed and readiness retested. The local CLI works while this desktop MCP session remains unregistered.

## Resolution and history

Unresolved. This canonical record was filed after `T-2911` obtained the `problems/` lease. The earlier [draft obstruction](../research/conductor_relation_yield_20261014/OBSTRUCTION.md) is retained as history; it does not supersede this record. The bounded execution component passed only the archived 19-point control; no scientific run is certified by filing this record.
