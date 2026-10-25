# Non-cohort A/A control production and canonical-store delivery

- **Status:** `open`
- **Kind:** implementation gap; access/tool limit
- **Affected work:** GOAL-NISTSEED-ab8949; RQ-NISTSEED-ac8851; prospective EXP-NISTSEED-6886da; BATCH-62db73
- **Next action owner:** Executor, TASK-20261025-ad9d68
- **Last updated:** 2026-10-25

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
