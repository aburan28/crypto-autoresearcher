# ICEX sparse-LA source adoption leaves a matched-matrix contract gap

- **Status:** `open`
- **Kind:** prospective corpus/export and measurement-contract interface gap; no proved mathematical obstruction
- **Affected work:** `IDEA-20261018-1bc873`, `GOAL-ICEX-001`; [source assessment](../coordination/goals/GOAL-ICEX-001/reconciliations/DEC-20261028-8f15c2/assessment.md)
- **Next action owner:** Coordinator; existing ICEX Executor and PR2596 study ownership preserved
- **Last updated:** 2026-10-28

## Problem

Existing sparse solvers are reachable, but no frozen source-bound same-matrix capture/export and cost comparison contract is established by this assessment. Commissioning the implementation described as absent would duplicate landed code; declaring the scientific matrix-law question settled would exceed the evidence.

## Evidence and uncertainty

- **Observed:** At crypto main `d4e85a6a70875c6ad7fe90559882e1d172ed94e0`, all five selectors route through the existing factory; see [exact source pins and trace](../coordination/goals/GOAL-ICEX-001/reconciliations/DEC-20261028-8f15c2/source-bindings.json). PR1874 merged at `ae8ac7df98b9b62bdcdc9cbd8a5d88d8fdff98e2`.
- **Observed:** The low-level reports already carry dimensions/nonzeros/filter/core counters. The deferred wrapper sums row_ops without retaining per-attempt reports. Current main provides archive-backed Gaussian rank audit/replay but explicitly refuses deferred sparse audit. Known-log bases bypass matrix solving.
- **Observed:** The underlying Solved vector is not a deterministic rank certificate; full-rank stopping and seeded equality are distinct. row_ops excludes documented work and is not separate field-add/multiply accounting or complete pipeline cost.
- **Observed:** Open PR2596 head `d62c0c075548a4c1bbc83d194d870b650af66474` and existing la_engines_20261014 have adjacent source/studies; no performance claims or current review acceptance are adopted. The separate GF(2) instrument's Stage0 failure/invalid disposition is preserved.
- **Not established:** Pinned available corpus satisfying all proposed matrix-law constraints,complete replayable export for the sparse path,matched cost crossover,asymptotic or deployed-curve conclusion.

## What would unblock it

- [ ] Pin actual rows,RHS,modulus,width,source context and complete transcripts where used; name exact export and consumption interfaces. Use a full-rank reference on the same matrices rather than a target-pinned stopping comparison.
- [ ] Reuse existing filter/core telemetry and specify retention of per-attempt reports; supply row/column laws and verification/rank semantics. Truncated 8 MiB Gaussian transcripts and unsupported sparse audits must be unavailable,not silently accepted.
- [ ] Separate field additions/multiplications,scoped row_ops and group-operation costs; declare any conversion and all missing setup/transfer/hash/index cost. Do not adopt a complete-cost or winner claim from partial counters.
- [ ] Map owner-held PR2596 and existing contracts before any new task; freeze control/sample/resource/review/admission requirements in a separately ranked protocol. No new implementation or run authorized by this problem.

## Next discriminating step

Coordinator: draft a source-bound same-matrix capture/export and comparison contract using existing five selectors, FilterReport/SparseSolveReport and complete Gaussian rank transcripts where supported. Pin actual rows/RHS/modulus and full-rank oracle, preserve separate field/group cost units, account for wrapper report loss and exclude owner-held PR2596 studies. Identify missing corpus/export interfaces before any fresh task or approval; no scientific runs, replay, storage access or old Executor claim.

This is source/contract preparation only. No compilation,tests,benchmark,trial,archive fetch/storage operation or historical replay is authorized here. A source-bound design can advance if the interfaces and corpus are supplied; otherwise record the precise absent artifact and retain the gap. Recheck on relevant source/corpus/publication or ownership change.

## Resolution and history

2026-10-28: Open. Source reachability is established for pinned code; scientific outcomes and IDEA status remain unverified/unchanged. No task,approval or run created. This Codex Coordinator reasoned over sources; no separate orchestration or Bedrock inference call was made and exact serving identity is unverified.
