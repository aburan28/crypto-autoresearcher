# Audit interface (EXP-CRYPTO-6505c6, preparation only)

This document specifies how a **future**, genuinely-claimed symbolic audit
task — with actual source-reading and runtime capabilities, a genuine
claim, frozen scope, and a preregistered independent review plan — would
fill the 20-file output bundle declared in `certificate-schema.json`, and
how it would preserve partial, open, and negative results honestly. It is
an interface specification. It is not a numerical execution wrapper of any
kind, and no run of it has occurred (`maximum_runs: 0` for this task,
`maximum_runs: 1` for the future audit task per the frozen specification's
`budget` block).

## 1. Bundle-filling responsibilities

| Root file | Filled from | Honesty requirement |
|---|---|---|
| `audit-manifest.yaml` | Future task's own commit/environment/inputs | Records the actual audit-task ID, revision, and inputs; never a placeholder ID minted here. |
| `source-readings.yaml` | Actual primary-source reading sessions | Every entry needs `read_status: read_and_matched` with the exact passage; extends `source-obligations.yaml` in this bundle, does not replace its open items until they are actually closed. |
| `source-hypothesis-matrix.yaml` | Hypothesis-by-hypothesis match against source theorems | Each row cites the exact source hypothesis and states whether the audit's object satisfies it, with justification, not assertion. |
| `case-index.yaml` | `symbolic-fixtures.yaml` (this bundle), unchanged | The 16 cases, families, bases, and roles are copied verbatim; the future audit does not narrow, merge, or drop a case. |
| `obligation-results.yaml` | `obligation-matrix.yaml` (this bundle), each row's `result_status` actually filled | Every one of the 160 keys keeps its key; `result_status` moves from `null` to an actual value from the frozen enum, with a certificate anchor for anything other than `NOT_ATTEMPTED_AFTER_STOP`. |
| `chart-coverage.yaml` | `symbolic-fixtures.yaml` chart-tag definitions (this bundle) | All 400 `(case_id, left_tag, right_tag)` keys present; compatibility or emptiness each carries a certificate, never a silent omission. |
| `normalization-and-weights.yaml` | Actual source-matched normalization derivations | Records the specific sqrt(p)/Frobenius/weight conventions actually used and their source justification. |
| `complexity-ledger.yaml` | Actual complexity/conductor computations, kept separate | Curve conductor, rank, embedding degree, and derived-complex complexity `C` are recorded as distinct fields per the specification; none substitutes for another. |
| `shared-constituents.yaml` | Actual geometric analysis of shared loci | Diagonal and off-diagonal translation-stabilizer loci are recorded with their actual dimension/degree if known, or `OPEN` if unknown; never assumed small. |
| `moment-certificates.yaml` | Actual proof or actual counterexample for the fourth moment | `B(C)` is either an explicit effective formula with dependencies, or the obligation stays `OPEN`; a finite observed maximum is never recorded as if it discharged the all-extension claim. |
| `stratification-application.yaml` | Actual hypothesis-by-hypothesis check of source Theorem 2.4 | Each hypothesis of the cited theorem gets its own checked/unchecked status for this specific embedded object. |
| `control-results.yaml` | Actual matched-null and constant-control analysis | A required match without a certificate is recorded `OPEN`, not silently treated as passing; constant controls (`C1`, `C2`) must be shown actually rejected by the cancellation argument. |
| `counterexamples.yaml` | Any actual checked counterexample found | Recorded with exact scope (family/base/case); an in-main-scope counterexample is negative evidence for that scope only, per the frozen `falsification_criterion`. |
| `open-obligations.yaml` | Roll-up of every row still `OPEN` or `NOT_ATTEMPTED_AFTER_STOP` | This file is the honest ledger of what remains unresolved; it is never emptied by reclassifying an unresolved row as resolved without a certificate. |
| `work-and-resources.yaml` | Actual measured time/memory/bytes for the audit pass | Measured values only; unmeasured fields stay `null` with a reason, per the frozen specification's `pending_values` rule. |
| `audit-report.md` | Narrative summary of the above | Separates observation from interpretation; states the frozen `success_criterion` / `falsification_criterion` / `outcomes` verbatim and reports which applies, without declaring the hypothesis supported or refuted. |
| `certificate-bundle.md` | Full certificate text per `cert_id`, per `certificate-schema.json` | Every `cert_id` referenced anywhere in the bundle is defined here exactly once. |
| `dependency-dag.yaml` | Actual dependency edges among certificates | Acyclic; every edge references a `cert_id` defined in `certificate-bundle.md`. |
| `checker-results.yaml` | Actual run of the future checker (per `checker-specification.md`, section 2) | Records only structural/mechanical findings; does not report a semantic verdict, which belongs to the separate independent review round. |
| `artifact-sha256.json` | sha256 of every other root file | Excludes itself; used by the Coordinator's archive step to bind the bundle to a commit. |

## 2. Preserving partial, open, and negative results

- **Partial**: if one main family (`K` or `L`) reaches `CERTIFIED_MAIN_SCOPE`
  while the other does not, `audit-report.md` reports this as `partial` per
  the frozen `outcomes.partial` rule — never rounded up to
  `overall_positive`.
- **Open**: any obligation lacking a certificate is `OPEN` in
  `obligation-results.yaml` and appears in `open-obligations.yaml`; it is
  never converted to `CERTIFIED` or `NOT_APPLICABLE_WITH_CERTIFICATE`
  without an actual certificate.
- **Negative**: an exact, independently checkable counterexample to the
  quantified main target is recorded in `counterexamples.yaml` with its
  exact scope and is reported as scope-limited negative evidence for that
  family/base/claim only, per the frozen `falsification_criterion` — it
  does not, by itself, close the hypothesis or the goal.
- **Stopping mid-panel**: if the audit stops at the first independently
  checkable exact contradiction (per the frozen `stopping_rule`), every
  cell not yet reached is marked `NOT_ATTEMPTED_AFTER_STOP` with its
  position in `case_order`/`phase_order` preserved, not silently dropped.

## 3. What this interface is not

- It is not a numerical experiment wrapper: no primes, extensions, or
  points are sampled or enumerated by this interface.
- It is not itself a checker run, a proof, or a review; `checker-results.yaml`
  and any semantic verdict remain the future audit task's and the future
  independent review round's outputs respectively.
- It allocates no future audit task ID; the Coordinator allocates that ID
  separately when it dispatches the future audit under its own frozen
  scope and preregistered review plan.
