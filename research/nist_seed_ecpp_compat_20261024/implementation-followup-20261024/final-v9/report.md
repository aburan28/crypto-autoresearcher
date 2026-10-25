# ECPP cohort implementation: final guarded V9 result

2026-10-25 UTC. Engineering observations for TASK-20261024-4f1bf4 and prospective EXP-NISTSEED-6886da under GOAL-NISTSEED-ab8949. **Named cohort orders executed: 0.**

## Question and scope

Can the prepared compatibility library be wrapped in a source-bound producer and independent checker that preserve exact cohort identity, raw observations, interrupted output, certificate admission and supervisor manifests? This is a static/mocked implementation evaluation. The legacy ECPP executable and its original VM boundary are replaced by fake artifacts throughout these tests.

The scientific question remains whether a period primality program treats eleven reconstructed omitted orders differently from ten published controls. This report contains no observations on that comparison. A program-specific difference, if later measured, would still require historical linkage to the original curve-generation program.

## Measured implementation observations

The actual command was `python3 coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-08d006/operator-static-tests-v9.py`. Python 3.12.8 on macOS 26.6 arm64 compiled the three Python modules successfully. The retained V9 receipt reports **9 test methods, 0 failures, 0 errors**. The test log records 30.673 seconds. Original-call guard attempts are empty and `legacy_program_executed` is false.

The nine passing methods cover complete admitted fake output, consistent censored failure envelopes, corrupted-censor refusal, mutations that reach the intended independent semantic checks, all 21 exact certificate mappings, manifests/status/inventory mutations, A/A controls, trace/catalog/raw offsets, and actual `complete_manifest` compatibility using mock data. The synthetic certificate is an interface fixture; it is not a mathematical proof.

All 18 original task input hashes still match. Published P-224 selects its exact coefficient in the existing certificate record labeled `side: other`; this is an identity convention correction, with uniqueness and all certificate bindings retained. Four code/schema hashes in IMPLEMENTATION_REPORT.md match the passing receipt. The reports-only V10 patch changes none of those four files.

## Retained attempts

| Guarded capture | Methods | Failures | Errors | Scope |
| --- | ---: | ---: | ---: | --- |
| V1 | 4 | 1 | 0 | Trace-expression assertion |
| V2 | 5 | 1 | 1 | Provenance/path handling |
| V3 | 5 | 0 | 2 | Actual container/catalog contracts |
| V4 | 7 | 0 | 23 | Cascading exact P-224 join errors |
| V6 | 9 | 0 | 29 | Cascading trace JSON byte errors |
| V8 | 9 | 1 | 4 | Censored status and mutation metadata |
| V9 | 9 | 0 | 0 | Final passing fake-boundary suite |

V5 was a metadata-only diagnostic and incomplete test proposal. V7 was a source patch. Neither is a full-suite capture. Earlier failures and patches remain retained. Cascading subtest errors are not independent defects, curves or replications. Test methods are not independent mathematical observations.

## Additional delivery check

A separate two-case partial-clone fixture reproduces the artifact CI failure caused by abbreviated object IDs. Setting local `core.abbrev` to 40 permits the unchanged artifact checker to fetch full object IDs: the 1,024-byte data fixture passes and the 1,100,000-byte fixture is still rejected. The workflow caller now uses that setting. This addresses object lookup without changing storage policy.

After merging main at f61b6e66d471c09feab45a0610853e646e208fb1, the mock-tested `complete_manifest` function was verified byte-identical to its V9 version. No redundant suite rerun was performed. The unrelated upstream plan-admission changes remain in the merged tree.

The official canonical-store migration command was attempted separately and refused at S3 HeadObject with HTTP 403. `artifact-store-push-v1.json` retains the exact command/error and confirms that all five pre-existing hydrated runtime/PDF files keep their original hashes. No manifest or upload success is asserted. This is a delivery-access obstruction; the local scientific inputs remain available. The long V6 mock log is retained losslessly as `.log.gz`, with a round-trip receipt, and its original local hydration remains present.

## Limits and next action

The mock verification step is complete. The implementation snapshot, separate frozen scientific specification/plan, actual preapproval, approval archive and ready-state check remain required before a future run. No ECPP acceptance label, catalog traversal, certificate result or timing exists for the named orders in this task. The original caller and selection trace remain missing; the commonality question stays open.

The canonical admission diagram was updated together with its SVG. Mathematical weakness, isogeny and ECDLP frontier graphs were checked for relevance and left unchanged because this round establishes implementation behavior only. The final diagram uses dashed edges for prospective measurements and historical attribution.

## Evidence and provenance

All evidence here is internal and retrieved directly from retained artifacts. `source-bindings.json` records exact paths and SHA-256 values. Raw receipts/logs, versioned operator wrappers and producer responses live in `coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-08d006/`. The complete 18-input table and four implementation hashes are in `experiments/EXP-NISTSEED-6886da/implementation/IMPLEMENTATION_REPORT.md`. Editable diagram: status.dot; rendering: status.svg; PDF source: report.typ.
