# Full ledger validation has unsuppressed integrity errors

- **Status:** `open`
- **Kind:** archived-record integrity gap, review-provenance gap, and a zero-compute classification gap; the cause of each individual error needs separate adjudication
- **Affected work:** [full corpus audit](../docs/reports/2026-10-21-ledger-integrity-audit/report.md), [`validate_ledger.py`](../tools/validate_ledger.py), and repository-wide claims that the archived experiment and decision corpus has a clean integrity gate
- **Next action owner:** Coordinator for scoped record corrections and source-reader assignments; validator maintainers for any schema change
- **Last updated:** 2026-10-28

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

The newer [2026-10-28 hosted-job inventory](../docs/reports/2026-10-28-ledger-validation/REPORT.md)
compares two complete-tree `ledger` CI jobs on heads `64da2f50560c3565c36880fc86b0aad8addeb223`
and `a94a304f1e76d81e4a9899e8bcb709b8fdb0e21c`. Each fails with the same
**65 unsuppressed errors in 22 paths**: 30 handoff review-plan messages, 30
run-manifest schema messages, four proposal prior-art messages, and one
experiment-specification classification message. The exact normalized error
sets match with zero added or removed messages. This is the current observed
hosted gate, not a local rerun on the later `main` merge commit. The earlier
162-error count above remains bound to its named October 21 commit.

One special case is a hand-derivation Stage 0 filed in the run namespace.
[`RUN-QSP-33b442-S0`](../experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S0/manifest_v2.yaml)
declares that no program ran, so it has no command capture, environment file,
stdout, stderr, or raw result. The validator requires all five; the archived
manifest already discloses the five errors and names the classification
problem. Supplying invented companion files to clear the errors would
misrepresent execution.

The frozen `RUN-FROB-91ee9c-7119f2` has a separate execution-source custody
gap. Its pre-run `code.head_commit` does not contain the archived
`implementation.py`; the run directory was untracked when execution began.
Hash-matched artifacts and an exact checker replay establish what the archived
checker reports, but cannot identify the implementation bytes that produced
the original outputs. The [scoped provenance audit](../docs/reports/2026-10-22-frob-provenance-audit/REPORT.md)
keeps that distinction explicit.

## Evidence and uncertainty

- **Observed:** The [full-checkout log](../docs/reports/2026-10-21-ledger-integrity-audit/evidence/validate-ledger.log)
  has SHA-256 `8d970c4cc0ccecadc8b84eaea63bdbac5c59850c3daf46b6897aedd6351bf0ca`.
  The [classification](../docs/reports/2026-10-21-ledger-integrity-audit/counts.json)
  is 66 prior-art metadata, 32 review/handoff fields, 28 citation provenance,
  19 run-manifest schema, 7 broken references, 5 zero-compute-stage artifacts,
  and 5 experiment-spec fields. The exact same log was obtained on the proof
  branch and on main; the proof branch changed no validator or ledger inputs.
- **Observed, scoped FROB replay:** The [machine-readable audit](../docs/reports/2026-10-22-frob-provenance-audit/audit.json)
  verifies all 14 frozen artifact hashes and reproduces the archived checker
  report byte for byte. The checker matches three trace-kernel dimensions and
  checks six orbit-divisibility values. Its three `ok` entries under
  `tuple_sum_reverifications` check curve point, order, primality, and
  Frobenius witnesses; they do not recompute tuple sumsets or control arms.
  The other three curve entries are skipped for size. The source-commit and
  environment fields remain unbound in the archived manifest.
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
- [ ] Resolve FROB execution-source custody from a contemporaneous source
  snapshot, or run a new source-bound replay of its frozen core cells and
  controls with a separately recorded Coordinator decision. Do not relabel
  the pre-run HEAD as the execution-source commit.
- [x] Settle the QSP Stage 0 zero-compute hand-derivation category with a
  source-bound, tested non-execution admission. Preserve the historical
  directory and all five absent capture artifacts; keep ordinary runs under
  the five-artifact rule.

These conditions would clear this ledger gate. They would not independently
replay historical scientific runs, establish semantic fidelity of the 66 Lean
targets, or certify attack performance. Reader parse warnings and all other
historical archives need their own scoped checks before an all-corpus claim.

## Next discriminating step

- **Action or proof obligation:** Triage the remaining prior-art, review-plan,
  and run-schema errors through actual source reading and record review.
  The current stacked citation corrections removed the specific citation
  errors they targeted; that does not establish complete source review.
  For FROB, look for a contemporaneous driver snapshot before considering a
  new prospective, source-bound replay.
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

- 2026-10-28: Two hosted `ledger` jobs fail with identical 65-message sets
  across 22 paths. The [current inventory and chart](../docs/reports/2026-10-28-ledger-validation/REPORT.md)
  preserve each path and message plus source job URLs and log hashes. No
  archived data, validator code, baseline, numerical result, or canonical
  performance graph was changed. The full-ledger gate and this problem remain
  open.

- 2026-10-21: Opened after two byte-identical full-checkout validator runs.
  No baseline entry, archived record, hypothesis, or numerical result was
  changed. Unresolved.
- 2026-10-21: [PR #2454](https://github.com/aburan28/crypto-autoresearcher/pull/2454)
  proposes a hash-bound validator correction for five references to frozen
  refused drafts. Its complete-tree run reports 157 remaining unsuppressed
  lines; the historical 162-line audit above remains bound to the named main
  commit. The broader problem remains open.
- 2026-10-22: The QSP Stage 0 frozen specification says `compute: ZERO` and
  that no program is run. Its registered supersession identifies a
  misclassification and explicitly preserves the five missing-artifact
  errors. A prospective validator representation needs an exact non-execution
  scope and negative controls; no command, environment, stdout, stderr, or
  raw-result file was created.
- 2026-10-22: This audit branch adds two complete, hash-pinned schema
  replacements. `EXP-ECDLP-daee4d` adds only the singular success/falsification
  fields and decision impact already fixed by its original objective,
  hypothesis, and approval decision. The frozen specification and its trial
  plan hash stay intact. `EV-QSP-2c78d3` removes `RUN-QSP-715b58` from
  structured `run_ids`: that expired attempt has an execution receipt but no
  manifest or raw result. The replacement still cites its receipt and states
  that no scientific result was produced. The
  [source-bound triage report](../docs/reports/2026-10-22-ledger-triage/report.md)
  checks both hashes and changed fields. A complete-tree validator rerun
  removed exactly those five errors, added none, and still failed with 157
  unsuppressed lines in 47 paths. Its log SHA-256 is
  `c4aa4214b060c9628e15221ea1373ed3899e811437c276b1c8d6ddafb6c97e66`.
- 2026-10-22: Source reading of `IDEA-20260920-b9f0c5` found that its citation
  describes `IDEA-20260906-a77711` as establishing no solving-degree drop,
  while the cited proposal labels this a prediction. The missing `verified_by`
  fields remain errors until that attribution is corrected and the source
  readings are recorded. This is a semantic gap, not an excuse to stamp
  provenance fields mechanically.
- 2026-10-22: After merging main `53c4975c34f5bd5cd278e63b2cce6cd098245d16`,
  whose separate refused-draft validator correction removes five more
  decision-reference errors, the complete-tree gate still exits 1 with
  **152 unsuppressed lines in 42 paths**. The merged log has SHA-256
  `0db4c3a97c3a1058aba90275764545f9cdf075347ce890362ba35bef22f53dad`;
  the [triage report](../docs/reports/2026-10-22-ledger-triage/report.md)
  verifies both five-line deltas and zero added errors.
- 2026-10-22: A third hash-pinned supersession of `IDEA-20260920-b9f0c5`
  records five actual source readings and corrects the citation to
  `IDEA-20260906-a77711`: its no-solving-degree-drop statement is a prediction,
  not a theorem or measurement. The complete-tree gate still exits 1 with
  **147 unsuppressed lines in 41 paths**; the final log SHA-256 is
  `dbc8b77fa464ed139e6b7857cefe3f7312545168786764825d3abb2a72dd9036`.
  The [triage report](../docs/reports/2026-10-22-ledger-triage/report.md)
  verifies this third five-line deletion and zero added errors. The other 23
  citation-provenance errors and all unrelated ledger errors remain open.
- 2026-10-22: A repository-level non-execution category admits only the
  hash-bound `RUN-QSP-33b442-S0` hand derivation under the frozen spec and
  derivation note. No process output, command, environment, raw result, or
  measurement was created. The [category report](../docs/reports/2026-10-22-zero-compute-category/report.md)
  records negative controls and the full-tree delta: five exact QSP
  missing-artifact errors removed, zero added, **142 unsuppressed lines in 40
  paths** (log SHA-256
  `cab54654ca535678d86c955d0ebe2575a85dfc73d8f0216d8dc7597586bf271d`),
  and one new non-failing classification advisory. The historical
  correction's five-error statement remains a true description of the old
  validator rule. The broader ledger gate still exits 1.
- 2026-10-22: The [FROB provenance audit](../docs/reports/2026-10-22-frob-provenance-audit/REPORT.md)
  matched all 14 frozen artifact hashes and reproduced the archived checker
  report byte for byte. Source review found that three `ok` entries check
  curve witnesses, not tuple sumsets or control arms; three more entries were
  skipped for size.
  The pre-run HEAD lacks the archived driver, so execution-source custody
  remains unresolved. This review changes no frozen bytes, ledger count,
  numerical result, or canonical performance graph.
- 2026-10-24: Post-merge CI for index-calculus PR#2520 (merge73a77f2)
  reports143 unsuppressed errors, including two new missing `from`/`to`
  fields in TASK-20261023-e485d9. CORR-20261024-7c17bf supplies an
  additive, hash-bound routing-only replacement and records the actual
  issuing/assigned Coordinator roles. The original handoff and all prior
  values remain unchanged; a targeted run of the actual validator reproduces
  those two errors before routing and accepts the replacement afterward.
  The [diagnosis](../coordination/tasks/TASK-20261024-f195f6/diagnosis.json)
  retains every observed CI error and provenance. This is a scoped repair,
  not a clean-current-corpus result or retrospective admission claim; the
  broader problem and unrelated historical errors remain open.
- 2026-10-22: A source-reading [BINSTD citation correction](../docs/reports/2026-10-22-binstd-source-provenance/REPORT.md)
  named readers for the five internal citations of `EV-BINSTD-030b4e` and
  corrected its `AGENTS.md` attribution from core rule 3 to core rule 5.
  On exact main archive `13eb217678653267553dcbfa9601f2564f63706b`, the
  complete-tree validator moved from 141 unsuppressed errors in 39 paths to
  136 in 38: exactly those five citation errors disappeared and none was
  added. The original evidence and run bytes remain unchanged, and the
  whole-ledger gate still fails.
- 2026-10-22: The [BINSTD toy-yield citation audit](../docs/reports/2026-10-22-binstd-yield-provenance/REPORT.md)
  read the source chain for two more frozen evidence records and added
  16 named source readings through hash-bound replacements. Its focused
  checker confirms all other evidence fields are equal and recomputes
  the four published aggregate ratios from hash-matched Stage-1 matrices.
  On parent commit `5e499ba86dfa5fde589c353d446433ad0cdcab3e`,
  complete-tree validation moves from 136 errors in 38 paths to 120 in
  36 paths, with exactly those 16 citation errors removed and none added.
  Both validator runs exit 1. The audit does not replay per-target solver
  work or change either toy-scope yield decision.
- 2026-10-23: The [BINSTD proposal citation correction](../docs/reports/2026-10-23-binstd-proposal-citation-provenance/REPORT.md)
  names the internal heuristic source and reader for two archived proposals.
  Its [full-tree receipt](../docs/reports/2026-10-23-binstd-proposal-citation-provenance/validation.json)
  compares parent `f7408a231b` with corrected tree `6c08b90468`: 120 to
  **118 unsuppressed errors in the same 36 paths**, exactly the two targeted
  citation errors removed and none added. Both runs exit 1; the 1,210-entry
  legacy baseline is unchanged. The remaining 118 include 66 prior-art
  metadata errors. Original proposal bytes and numerical results are unchanged.
- 2026-10-23: The [four-proposal prior-art correction](../docs/reports/2026-10-23-odd-characteristic-prior-art-correction/REPORT.md)
  reads six committed nearest-prior-work cards, preserves the four archived
  proposal files, and registers hash-bound metadata replacements. On exact PR
  parent `9fc0685a5fd51e5fe66a80d42124f1d522f7c8f5`, the full-tree
  validator moves from 118 errors in 36 paths to **88 in 32 paths**: exactly
  30 targeted lines removed and none added. Both runs still exit 1. The
  1,210-entry legacy baseline, experiment results, and performance charts are
  unchanged; the broader integrity problem remains open.
- 2026-10-23: After merging main `73a77f2def370f621f1b4c1aaf3cb1734738f853`
  into this correction branch at `b82d5180f6f033370c9d2224fdf2da24bcd2e1a6`,
  a full-tree validator run reports **90 unsuppressed errors in 33 paths**.
  Compared with the archived 88-error correction checkpoint, no error
  disappeared and exactly two appeared. Both concern the new archived
  `TASK-20261023-e485d9` handoff, which lacks required `from` and `to`
  fields. Its task source does not identify both endpoints, so this branch
  leaves them unresolved rather than inventing an assignment. The full log
  SHA-256 is `fcfd4769d535c68be0a84d74dfb9a3f775d9cd9c740491cbf463b2ad30f06590`;
  this is a new current-tree check, not a revision of the frozen 118-to-88
  source correction receipt.

- 2026-10-30: Complete original post-merge job `41001067477` contained **38**, not six, errors. PR #2764 repaired six focused errors; subsequent complete job `41013419479` reports 32. The [remaining schema repair](../reports/ci-remaining-ledger-schema-20261030/README.md) reproduces those 32 and removes 31 in focused native validation, preserving all archived originals. The [last run capture gap](binstd-f7ca97-original-execution-captures-missing.md) remains open. This is a dated correction to the earlier focused count, not a clean whole-corpus claim.

- 2026-10-30 follow-up: Complete #2771 CI reveals16new parser regressions outside its14-record focused set, leaving17whole-corpus errors (16shared-quantity-layout errors plus the original missing RUN-BINSTD-f7ca97 captures). The [shared-quantity correction](../reports/ci-shared-blind-quantity-repair-20261030/README.md) reproduces17affected findings and reduces them to1 with44focused controls and all7320archived plan paths checked. No baseline, frozen plan or capture requirement changes; fresh complete hosted checks remain required.
