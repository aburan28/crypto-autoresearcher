# Full ledger validation has unsuppressed integrity errors

- **Status:** `open`
- **Kind:** archived-record integrity gap, review-provenance gap, and a zero-compute classification gap; the cause of each individual error needs separate adjudication
- **Affected work:** [full corpus audit](../docs/reports/2026-10-21-ledger-integrity-audit/report.md), [`validate_ledger.py`](../tools/validate_ledger.py), and repository-wide claims that the archived experiment and decision corpus has a clean integrity gate
- **Next action owner:** Coordinator for scoped record corrections and source-reader assignments; validator maintainers for any schema change
- **Last updated:** 2026-10-21

## Problem

The repository cannot yet support an end-to-end clean ledger-integrity claim:
`tools/validate_ledger.py` exits 1 on a full checkout of main
`e20013ae20d2c09019d8ea1b2fed7556c61ad4ba`, with **162 unsuppressed
error lines in 49 paths**. The existing prune-only baseline separately
suppresses 1,210 grandfathered errors; 543 advisories are non-failing. The
unsuppressed errors include missing provenance, incomplete review plans,
malformed or incomplete experiment/run records, and unresolved cross-record
references. These are mechanical failures requiring record-by-record review,
not 162 established false scientific conclusions.

One special case is a hand-derivation Stage 0 filed in the run namespace.
[`RUN-QSP-33b442-S0`](../experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S0/manifest_v2.yaml)
declares that no program ran, so it has no command capture, environment file,
stdout, stderr, or raw result. The validator requires all five; the archived
manifest already discloses the five errors and names the classification
problem. Supplying invented companion files to clear the errors would
misrepresent execution.

## Evidence and uncertainty

- **Observed:** The [full-checkout log](../docs/reports/2026-10-21-ledger-integrity-audit/evidence/validate-ledger.log)
  has SHA-256 `8d970c4cc0ccecadc8b84eaea63bdbac5c59850c3daf46b6897aedd6351bf0ca`.
  The [classification](../docs/reports/2026-10-21-ledger-integrity-audit/counts.json)
  is 66 prior-art metadata, 32 review/handoff fields, 28 citation provenance,
  19 run-manifest schema, 7 broken references, 5 zero-compute-stage artifacts,
  and 5 experiment-spec fields. The exact same log was obtained on the proof
  branch and on main; the proof branch changed no validator or ledger inputs.
- **Derived or proved:** The validator's exit code and counted messages are
  reproducible facts about this source tree. No mathematical or performance
  conclusion follows from the count alone.
- **Suspected explanation:** Some records predate tightened schemas; some
  issues may need source correction rather than schema changes. This is a
  hypothesis for triage, not a blanket exemption.
- **Missing capability:** Source-backed corrections or complete superseding
  records for archived errors; actual named readers for `internal` citations;
  complete blind-review assignments and controls; a truthful representation
  of zero-compute theory artifacts; and resolution of dangling IDs.
- **What this evidence does not establish:** It does not show that every
  archived computation is wrong, that a Lean proof fails, or that any
  performance graph's numerical value has changed. A separately successful
  static reader build still reports 24 unparseable historical records and
  does not turn the ledger gate green.

## What would unblock it

- [ ] Make the full-checkout `tools/validate_ledger.py` pass with **zero
  unsuppressed errors** on the current head, without adding entries to the
  prune-only legacy baseline or altering sealed run bytes. Use the existing
  source-bound supersession registries for archived record corrections.
- [ ] Resolve every broken reference to a real, reviewed record or an
  explicit truthful correction; fill criteria, provenance, and review-plan
  fields only from actual source reading or assigned review work.
- [ ] Settle the zero-compute hand-derivation category without inventing
  command/output artifacts: either a narrowly specified, tested validator
  representation for no execution or a prospective non-run artifact path,
  preserving the historical directory and its hash bindings.

These conditions would clear this ledger gate. They would not independently
replay historical scientific runs, establish semantic fidelity of the 66 Lean
targets, or certify attack performance. Reader parse warnings and all other
historical archives need their own scoped checks before an all-corpus claim.

## Next discriminating step

- **Action or proof obligation:** Triage one exact source record from each
  high-impact class first: the QSP zero-compute stage, the approved
  `EXP-ECDLP-daee4d` specification, a dangling run/experiment reference,
  and an `internal` citation without `verified_by`. For each, determine
  whether the correct route is an additive supersession, a verified source
  reader assignment, or a prospective schema change with negative controls.
- **Inputs and controls:** Use the raw 162-line log, committed original and
  supersession registry bytes, and the full-checkout validator. Compare the
  old and corrected source hashes; reject placeholder provenance and files
  claiming output from a program that never ran.
- **Execution limits and stop condition:** Scope each correction to a real
  record and preserve archived inputs. Stop that correction if its required
  source or reviewer evidence is unavailable; record the exact missing item
  rather than inventing it. This is not a spending cap on the broader goal.
- **Outcomes and next actions:** A valid additive correction reduces the
  corresponding unsuppressed lines without new errors; a schema ambiguity
  needs a tested contract decision; absent evidence keeps the record red;
  infrastructure failure is reported separately from a data verdict.
- **Recheck trigger:** Every landed correction or validator/schema change,
  then a full current-head ledger run and local dashboard integrity check.

## Resolution and history

- 2026-10-21: Opened after two byte-identical full-checkout validator runs.
  No baseline entry, archived record, hypothesis, or numerical result was
  changed. Unresolved.
