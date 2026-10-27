# Non-cohort A/A control production and canonical-store delivery

- **Status:** `open`
- **Kind:** implementation gap; access/tool limit
- **Affected work:** GOAL-NISTSEED-ab8949; RQ-NISTSEED-ac8851; prospective EXP-NISTSEED-6886da; BATCH-62db73
- **Next action owner:** Executor, TASK-20261025-ad9d68
- **Last updated:** 2026-10-27

## Problem

The future fixed 21-order ECPP comparison cannot yet be admitted because the public runner accepts only frozen cohort indices while the public checker’s A/A path compares—but does not produce—two non-cohort control fixtures; separately, canonical-store delivery has a public HTTP 403 access refusal.

The public runner `cohort_runner.py` accepts only `--index` in `[0,20]`, and a non-cohort A/A fixture cannot lawfully be fabricated by reusing an out-of-range or cohort input. `cohort_checker.aa_compare` requires two complete schema documents, each with a fixture exactly `{id, public_input}`, and rejects cohort identifiers. The frozen protocol requires an A/A engineering control before scientific launch. A canonical-store push was refused at S3 HeadObject HTTP 403; existing hydrated runtime bytes remain hash-bound public inputs, but the refusal cannot be represented as storage success.

## Evidence and uncertainty

- **Observed:** TASK-20261024-b17301 archived the six cohort runner/checker implementation artifacts at snapshot `68904e9b80c21785f1b17e6dfdb0e01b7aaf5a04`.
- **Observed:** guarded V9 static/mock tests reported 9 methods, 0 failures, 0 errors, no original-boundary attempts, `named_orders_executed: 0`, and `legacy_program_executed: false`.
- **Observed:** `artifact-store-push-v1.json` records the HeadObject 403 and preserved hydrated runtime/PDF bytes.
- **Derived:** current A/A comparison has no source-bound producer for two fresh public non-cohort executions.
- **Missing capability:** a fixed-input A/A producer with control-validity gating before equality comparison.
- **What this does not establish:** no named-order legacy behavior, no primality result, no historical selector, no curve weakness, and no ECDLP conclusion.

## What would unblock it

- [ ] TASK-20261025-ad9d68 delivers a source-bound public-prime-101 A/A producer whose static/mock tests pass the exact real `cohort_checker.aa_compare` path and reject invalid identical pairs.
- [ ] TASK-20261025-5dd15e archives those five artifacts with exact source hashes.
- [ ] A later scientific packet states a lawful raw-artifact storage route without bypassing the recorded public 403.

These conditions establish only an A/A-control implementation prerequisite. They remain insufficient for scientific packet approval, named-order execution, independent replay, historical attribution, or a cryptanalytic conclusion.

## Next discriminating step

- **Action:** implement and mock-test the fixed non-cohort A/A producer under TASK-20261025-ad9d68.
- **Inputs and controls:** public 101 newline input; archived runner/checker interfaces; unchanged runtime/kernel/Data bindings; public storage-refusal record.
- **Execution limits and stop condition:** maximum_runs 0; no `execute_case`, VM, QEMU, legacy executable, storage push, or cohort input. Any such invocation is a refusal.
- **Outcomes and next actions:** a passing mocked implementation permits later prospective packet design only. An invalid fixture, mismatch, or access refusal remains an engineering/access obstruction.
- **Recheck trigger:** archived completion of BATCH-62db73 or an actual authorized storage-access receipt.

## Resolution and history

Unresolved.


### 2026-10-27: publication collision; separate completed research observations

The original future EXP-NISTSEED-6886da admission packet remains distinct from the later standalone completed [ECPP](../research/nist_seed_ecpp_full_cohort_20261027/REPORT.txt), [SEA](../research/nist_seed_sea_all_roots_20261027/report.md) and [FreeLIP](../research/nist_seed_pre1997_library_20261027/report.md) observations. Its earlier zero-run statements are historical packet state, not the current count of all research executions. The canonical-store refusal is still not storage success.

Refreshing main to `6464133bfc8d76771c523bfb6bc3c56763b747b4` exposes five immutable-record collisions under `experiments/EXP-NISTSEED-6886da/aa-admission/`: `IMPLEMENTATION_REPORT.md`, `aa_fixture_producer.py`, `aa_fixture_schema.json`, `test-report.txt` and `test_aa_fixture_producer.py`. Main includes the separately archived zero-run snapshot at `f80cf4fbf0`. The [publication receipt](../research/nist_seed_pre1997_library_20261027/PUBLICATION-STATUS.json) binds the exact branch/main Git blobs and failing check; all five branch blobs are unchanged from `01980761a4` before the new FreeLIP commits. This blocks a current-main merge-hygiene pass, not the scientific replay. The earlier pass against an older main ref is not a current pass.

Required publication exit: preserve both already-published byte versions through an allocated successor and a CORR alias mapping, retain all source/runtime bindings, and pass branch merge hygiene against a freshly fetched main. Do not overwrite either frozen snapshot or select one side as a collision resolution. Resolving that publication issue would not identify the historical curve criterion. T-5518 records this obstruction; the current scientific source investigation remains active.


2026-10-27, T-5518 source-body repetition: The separate [Atkin source-body study](../research/nist_seed_ccr_root_matching_20261027/source-recovery-20261027/README.md) retains two complete byte-identical666-call streams, including1196 total cohort GETALL calls. The repeat protocol/export check passes and the public repeat archive replays after decompression and relocation. The first formal-export encoding failure remains in the first archive. This study uses explicit newly written adapters and does not change the archived ECPP fixture producer or earlier zero-run handoffs. Canonical uploads for both new archives again stop at HeadObject403; DELIVERY.json and store-first.stderr/store-repeat.stderr retain these outcomes. Exact archives are committed under the existing PR large-file-ok route; remote object-store delivery remains unconfirmed.
