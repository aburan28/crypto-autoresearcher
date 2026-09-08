# Audit interface (preparation artifact, EXP-CRYPTO-6505c6)

Status: interface description only. This document describes how a future,
genuinely claimed, proof-producing symbolic audit fills the fixed 20-file
bundle and how it must preserve partial, open, and negative results. It does
not run, simulate, or wrap any audit. No future audit task ID is allocated
here (`specification.artifacts.audit_receipt`: "No future audit ID is
allocated by this protocol").

## 1. Where the audit writes

`specification.artifacts.directory`:

```
experiments/EXP-CRYPTO-6505c6/audits/<genuinely_allocated_future_audit_TASK_ID>/
```

The `<genuinely_allocated_future_audit_TASK_ID>` placeholder is filled only
when the Coordinator dispatches an actual audit task and mints its ID with
`tools/allocate_id.py`. This preparation package does not invent, guess, or
reserve that ID.

## 2. The 20 fixed files and what each preserves

| # | Filename | What it must preserve |
|---|---|---|
| 1 | `audit-manifest.yaml` | Exact scope, revision, task ID, dirty-tree state, and budget actually used. |
| 2 | `source-readings.yaml` | Every source passage the audit itself opened, with provenance and verified_by — extending, never replacing, `source-obligations.yaml`'s already-read record. |
| 3 | `source-hypothesis-matrix.yaml` | The hypothesis-by-hypothesis match against the source theorem (obligation O07); an unmatched hypothesis is recorded OPEN, not silently dropped. |
| 4 | `case-index.yaml` | The 16 cases exactly as fixed in `symbolic-fixtures.yaml`; no case added, removed, or redefined. |
| 5 | `obligation-results.yaml` | All 160 keyed rows from `obligation-matrix.yaml`, each resolved to one of the six fixed statuses or left OPEN with a reason — never silently omitted. |
| 6 | `chart-coverage.yaml` | All 400 keyed rows from `symbolic-fixtures.yaml`'s chart-pair keys, each resolved to a compatibility/emptiness status with a certificate anchor. |
| 7 | `normalization-and-weights.yaml` | The fixed normalization/zero-boundary/weight conventions actually used, matching `specification.frozen_symbolic_domain` and `families.*.normalization`. |
| 8 | `complexity-ledger.yaml` | Rank, Artin/Swan conductors, embedded-derived complexity, and operation costs, kept as **separate** ledger fields (`specification.main_transfer_target.conductor_separation`) — never collapsed into one another. |
| 9 | `shared-constituents.yaml` | Geometric shared constituents/coinvariants of the two translated pullbacks, diagonal and off-diagonal, with their actual dimension — never assumed small or omitted. |
| 10 | `moment-certificates.yaml` | The all-extension fourth-moment statement and effective B(C) if certified, or an explicit OPEN obligation naming exactly what is missing. |
| 11 | `stratification-application.yaml` | The hypothesis-by-hypothesis application of the source's stratification theorem to this X and complex. |
| 12 | `control-results.yaml` | Matched-null (`case-07`/`case-08`) and constant-sheaf (`case-15`/`case-16`) control outcomes; a control that fails to be rejected invalidates the argument, and that failure is recorded, not hidden. |
| 13 | `counterexamples.yaml` | Any checked exact counterexample, with its certified violated statement and exact scope — never generalized beyond that scope. |
| 14 | `open-obligations.yaml` | Every obligation/chart cell left OPEN or NOT_ATTEMPTED_AFTER_STOP, with the exact missing source/proof/effectiveness prerequisite. This file is the audit's honesty ledger and must never be empty unless every one of the 160+400 cells is genuinely resolved. |
| 15 | `work-and-resources.yaml` | Actual measured construction work, peak bytes, and certificate size — `null` with a reason if not measured, never a fabricated or estimated value presented as measured. |
| 16 | `audit-report.md` | Prose summary separating observation, comparison, inference, and limitation, per `docs/task-lifecycle.md` Section 8. |
| 17 | `certificate-bundle.md` | Unique explicit `cert-ID` markers for every certificate, conforming to `certificate-schema.json`. |
| 18 | `dependency-dag.yaml` | Acyclic dependency graph over `cert-ID`s; a reused global lemma requires an explicit parameter/scope substitution recorded per row it discharges. |
| 19 | `checker-results.yaml` | The structural checker's findings (Section 2 of `checker-specification.md`) — never a semantic verdict. |
| 20 | `artifact-sha256.json` | Hash of every other materialized artifact in the bundle. The Coordinator archive binds this file itself. |

## 3. Preserving partial, open, and negative results

- **Partial**: one family certified, the other open, is reported as partial
  in `audit-report.md` and in the per-family status fields; it is never
  converted into an overall-success claim
  (`specification.outcomes.partial`).
- **Open**: a missing source, proof, or effectiveness prerequisite is recorded
  in `open-obligations.yaml` with the exact missing item — never silently
  assumed true, never resampled away.
- **Negative**: an exact in-main-scope counterexample is recorded in
  `counterexamples.yaml` with its exact scope; it closes only that named
  family/base/claim, not the wider target (`specification.outcomes.negative`).
- **Invalid argument**: if the argument accepts a constant-sheaf control, that
  is recorded as an invalid argument, not as a negative result about the main
  target (`specification.falsification_criterion`).
- Degeneration-only failure and absence of proof are explicitly excluded from
  refuting the main target by themselves; the audit records them as scoped
  diagnostics only.

## 4. No numerical execution wrapper

This preparation package defines **no** runner, supervisor, subprocess
receipt, or resource-measurement wrapper for a numerical computation, because
`specification.replication.mode` is "Fixed symbolic universal-quantifier
audit" with `numerical_primes_or_extensions: []` and
`maximum_numerical_runs: 0`. A future audit that needs to check a symbolic
identity by hand or by a computer-algebra derivation records that as
proof/derivation work in `certificate-bundle.md`, not as a numerical
experiment run, and any such derivation remains subject to the same
independent semantic review as every other certificate — it does not become
self-certifying because a tool executed it.

## 5. What launches the audit (not this document)

Per `specification.launch_gate`: exact approval archive/publication, this
zero-run preparation and its snapshot, a separate ranked proof-audit task with
actual source-reading/runtime capabilities and a genuine claim, frozen scope,
and a preregistered independent review. This document is part of the
preparation; it does not itself launch, claim, or authorize the audit.
