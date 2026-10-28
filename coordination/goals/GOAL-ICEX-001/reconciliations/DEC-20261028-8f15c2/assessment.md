# ICEX/BINSTD existing-source adoption and residual-gap assessment

Observed 2026-10-28T01:20:33.535360Z. Research main `4f1893c572ba16f4a455eced0ed52c458ac1ad11`; crypto main `d4e85a6a70875c6ad7fe90559882e1d172ed94e0`; owner-held PR2596 head `d62c0c075548a4c1bbc83d194d870b650af66474`. This is a zero-run static source assessment, not an evidence review or experiment approval.

## Observations

The implementation premise of `IDEA-20261018-1bc873` is stale at the pinned source. All five sparse selectors are in `is_deferred_sparse()` and `matrix_by_name()`; `mod.rs` reaches the factory from the unknown-log pipeline and uses FullRank for all five. Known-log bases bypass the factory. Rank-audited/archive-import paths refuse deferred sparse instead of reporting misleading per-row ranks. The historical rejected spelling is not evidence that current solver names are unavailable.

| Selector | Filtering | Core |
| --- | --- | --- |
| `sparse-cado` | CADO-style filter | BlockWiedemann |
| `filter+wiedemann` | CADO-style filter | BlockWiedemann |
| `filter+lanczos` | CADO-style filter | BlockLanczos |
| `wiedemann` | No filter; surplus folding | BlockWiedemann |
| `lanczos` | No filter; surplus folding | BlockLanczos |

`SparseCado::new()` selects filtered BlockWiedemann; `with_core()` selects the other configurations. Five names share one deferred wrapper. They are not five independently implemented verification engines. Full-rank completion is a stopping requirement, not a deterministic rank certificate: `try_solve()` requires two seeded solved vectors to agree, while the underlying Solved contract expressly disclaims rank certification.

## Selector-to-pipeline source trace

- `ic_framework/mod.rs:386-404`: audit/archive applicability,1..4096-column bound and incremental-only audit admission.
- `mod.rs:390-394,436-453`: selected/default solver,known-log bypass and matrix factory call with `fb.columns+1` and `ctx.r`.
- `linalg.rs:592-632`: complete five-name classification and factory map.
- `linalg.rs:389-428`: exact filtered/unfiltered/core configuration.
- `linalg.rs:437-478`: deferred attempts, outcome branches, two solved vectors and summed row_ops.
- `mod.rs:509-525`: FullRank rule and residual-collector incompatibility.

All line numbers refer to crypto main `d4e85a6a70875c6ad7fe90559882e1d172ed94e0`. A source change requires rebinding, not silently reusing these lines. Source implementations, reports and documented tests were read; no compilation,test,benchmark,checker or run was executed.

## Semantic and cost comparison

### Domain and object

matrix_by_name/SparseCado use u64 modulus and ordinary RHS system; underlying core supports wider modulus paths. A returned solution vector is not an arbitrary homogeneous kernel basis.

Freeze exact modulus,width,rows,RHS and verification objective; no automatic GF(2) toy-race transfer.

### Stopping and rank

Deferred methods wait for full-rank completion and use seeded equal-solution checks; preacceptance rank() is a placeholder. Underlying Solved explicitly does not certify rank.

Compare with full-rank incremental oracle on the same rows; do not equate timing/rank with TargetPinned or promote seeded agreement into deterministic proof.

### Counted work

row_ops counts nonzero multiply-subtracts plus conversions/filter/fold/reconstruction/checks/returned Krylov products; all attempted report charges are summed. Small block arithmetic and dense scans are excluded by documented convention.

row_ops is a scoped counter, not complete arithmetic/wall/memory cost or separate field-add/multiply counts; no whole-system cost claim.

### Telemetry already available

FilterReport has input/output rows,columns,nonzeros and removal/merge counters; SparseSolveReport has filter/core dimensions/nonzeros,solver reports,attempts,reconstruction,row_ops.

Reuse existing report types rather than infer no telemetry exists.

### Pipeline export gap

Inspected SparseCado wrapper accumulates report.row_ops but does not retain the per-attempt reports in its state; rank audit refuses deferred sparse.

Need an exact source-bound same-matrix capture/export bridge or separate bounded interface specification before a sparse/matched-null measurement protocol is complete.

### Archive/rank interfaces

Current main has archive-backed factor bases, AuditedMatrix and replay; docs freeze comparisons and explicitly say no candidate selected. Audit <=4096 columns,8MiB receipt prefix, truncated replay refused, sparse deferred refused.

Reuse verified-context complete Gaussian transcripts within scope; no unsupported sparse rank audit or unqualified whole-run duplicate total.

### Cost-unit junction

H-ICEX-5666b2 distinguishes field multiplications/additions from group-operation collection/baselines and requires declared conversion before totals.

Source intake grants no calibration or exponent result; preserve missing original-generation/transfer and uncalibrated hash/index work in archive docs.

## Existing-work overlap

- [Merged crypto PR1874](https://github.com/isogeny-labs/crypto/pull/1874), merge `ae8ac7df98b9b62bdcdc9cbd8a5d88d8fdff98e2` on2026-10-17, establishes landed sparse-cado integration and is an ancestor of the pinned main. Later aliases are observed on current main; they are not all attributed to that PR.
- [Open crypto PR2596](https://github.com/isogeny-labs/crypto/pull/2596), author `aburan28`, head `d62c0c075548a4c1bbc83d194d870b650af66474`, owns its branch/study. Its README/protocol are pinned; reported clean/interrupted/unreplayed outcomes are not re-certified or adopted. Main-vs-PR linalg exact-byte equality: **True**. Code overlap must not be treated as evidence that every unmerged study artifact is on main.
- Existing `research/la_engines_20261014` already reports a synthetic prime-field matrix/filter study under its own protocol. Its existence refutes a global claim that no matrix measurement exists; no ratios,fastest-tool or scaling conclusions are adopted here.
- H-BINSTD-dcc004 is a distinct GF(2) Python instrument race,not this Z/r pipeline. DEC-20261004-29f894 records invalid Stage0 and no rerun authorization. H-ICEX-5666b2 already states a matched-real/synthetic matrix-law question and refuses unconverted field/group totals.
- Existing ICEX task TASK-20261001-4862b6 has a prior failed release for epoch-bound driver/C7 admission. Its card,implementation,claims and goal routing remain unchanged. BATCH-1104d5 and BATCH-454f85 remain open; BATCH-227e0d is closed. This assessment takes over neither lane.

## Residual gap and one next action

The source supports routing and telemetry-interface facts. It does not yet identify a frozen,pinned same-matrix corpus/export bridge meeting this proposal's matrix-law comparison and H-ICEX cost-unit requirements. Current archive/rank support provides a reusable starting point with explicit limits; it is not sparse rank-audit support or a completed comparison. See [the problem](../../../../../problems/icex-sparse-la-source-adoption-and-matched-matrix-gap.md).

Coordinator: draft a source-bound same-matrix capture/export and comparison contract using existing five selectors, FilterReport/SparseSolveReport and complete Gaussian rank transcripts where supported. Pin actual rows/RHS/modulus and full-rank oracle, preserve separate field/group cost units, account for wrapper report loss and exclude owner-held PR2596 studies. Identify missing corpus/export interfaces before any fresh task or approval; no scientific runs, replay, storage access or old Executor claim.

## Provenance and boundaries

Exact source commit/path/OID/bytes/SHA256 bindings, trace,semantic matrix and ownership map are in [source-bindings.json](source-bindings.json), SHA256 `3a5e0104fb659ace68d926a0a83b3661c0b679a6353920427f395a199fb732ee`. No research code,data,old record,IDEA status,goal head,queue,claim,hypothesis or approval was edited. No fresh task or lane is opened because this is a synchronous Coordinator source assessment.

This Codex Coordinator subagent reasoned over the sources. Configured policy/backend is coordinator-orchestration-code/high on openai-gpt61/gpt-6.1-sol; exact serving identity remains unverified. No separate orchestration or Amazon Bedrock inference call was made. Primary source review here is code/record fidelity only,not paper-level novelty,mathematical or performance validation. Publication remains local for parent sequencing; no all-green CI or future archive SHA is asserted.
