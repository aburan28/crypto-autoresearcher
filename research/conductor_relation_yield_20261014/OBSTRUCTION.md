# Prime-field arity-3 useful-relation enumerator and verifier

- **Status:** `open`
- **Kind:** implementation gap; current Conductor authentication is a separate access/tool limit for filing the canonical `problems/` record.
- **Affected work:** [`README.md`](README.md), [`plan.json`](plan.json), prospective `H-ECTD-e88346` / `EXP-ECTD-0cf008` (IDs allocated and checked, formal records not written).
- **Next action owner:** Coordinator for contract admission; Executor for implementation after a valid handoff.
- **Last updated:** 2026-10-14.

## Problem

The fixed 29-bit and 37-bit prime-field conductor pairs cannot yet yield the requested arity-3 native useful-relation comparison because this repository has no committed exact triple enumerator, independent verifier, or admitted launcher for the 32,768-target schedule in `plan.json`.

The previous `crypto` ecbench pair sessions implement an arity-2 MITM IC pipeline with 256 and 2,048 abscissae, respectively. They do not enumerate all three-point representations of the selected target stream or implement the exact distinct-row/rank definition in this plan. Reusing their hit rates would answer a different question. The `GF(2^51)` selected degree-271 edges also lack a general serialized point evaluator and dual, so a same-point transported-base arm is separate future work.

## Evidence and uncertainty

- **Observed:** The archived external specs under `crypto/research/ecbench_conductor_gap_20261012/specs/` bind the two endpoint pairs and `ic.pipeline` with `mitm:m=2`. `cryptanalysis/experiments/volcano-ic/README.md` records a completed binary-field arity-2 census; it supplies calibration only. The current Conductor conflict/claim calls for a new `problems/` path and formal ledger paths returned `401 unauthenticated` after an earlier successful claim for this study directory, so the canonical record and index were not edited.
- **Derived or proved:** The all-target ordered-triple sum is `|F|³`, for any finite group and any factor base, by counting each ordered triple once. This identity does not determine useful nonempty-target probability or rank.
- **Suspected explanation:** None is needed; the missing implementation is directly visible from the current program scope. No claim is made that the specified workload is infeasible.
- **Missing capability:** A bounded, exact arity-3 enumerator; independent group-law replay and small-group exhaustive reference; fixed-column rank over `F_r`; target-generation and provenance seals; an admitted formal experiment specification.
- **What this evidence does not establish:** No direction or magnitude of native yield difference, no conductor-causal effect, no transported same-point comparison, and no ECDLP cost advantage.

## What would unblock it

- [ ] Implement and commit a deterministic launcher that accepts both hash-bound input specs and the exact `plan.json` schedule without reading the planted log inside the collector; it writes every target outcome and all failure/censor receipts immutably.
- [ ] Pass a separate exhaustive small-group oracle, independent point-addition replay, the isomorphic `u=2` targetwise conservation control, planted triples, and the all-target `|F|³` count identity, including repeated and cancellation cases.
- [ ] Establish a formal `EXP-*` contract whose `newest_experiments` execution state is `ready`, with Coordinator approval/archival and a run handoff. File this problem under `problems/` and index it when coordination access is restored.

These conditions allow the fixed-pair native measurement. They do not construct a degree-ell point evaluator or prove a general conductor law. Map transport and full attack-cost accounting remain separate obligations.

## Next discriminating step

- **Action:** Implement the pair-sum histogram and a disjoint exhaustive oracle on a small prime field, then run only the predeclared controls before admitting the 29/37-bit schedule.
- **Inputs and controls:** Exact `plan.json` models; raw and useful triple definitions; planted-sum and isomorphic-presentation checks; same-cardinality random bases.
- **Execution limits:** One worker, 4 GiB memory, 1,800 seconds per endpoint for the eventual scientific run. A control failure stops admission; it is an implementation failure, not negative mathematical evidence.
- **Outcomes:** Passing controls permits the frozen run. A memory or watchdog stop preserves raw receipts and prompts a versioned resource/implementation amendment. A count mismatch prompts oracle repair before measurement. An inconclusive yield contrast triggers sensitivity review without reselecting targets.
- **Recheck trigger:** committed launcher plus restored Conductor authorization for the canonical record and formal handoff.

## Resolution and history

Unresolved. This file is a draft within the claimed study directory because Conductor authentication prevented a claim on `problems/` and the index. It is not a substitute for the canonical problem record required by `AGENTS.md`.
