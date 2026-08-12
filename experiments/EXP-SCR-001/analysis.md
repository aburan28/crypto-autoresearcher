# EXP-SCR-001 analysis (Executor, observations only)

Lifecycle §8 structure. The Executor reports observations and comparisons
against the frozen metrics and controls. No conclusion that H-SCR-001 is
supported or refuted is drawn; status transitions belong to the Coordinator.

## 1. Observation — what was measured

Three planned runs, all `completed_valid`:

| Run | Wall (s) | CPU (s) | Peak RSS (bytes) | Controls |
|---|---|---|---|---|
| RUN-SCR-001-A | 1.258 | 0.959 | 30,736,384 | CTRL-CORPUS-INTEGRITY pass, CTRL-SHEET-CALIBRATION pass |
| RUN-SCR-001-B | 1.748 | 1.404 | 30,621,696 | pre-controls pass; 14 items adjudicated |
| RUN-SCR-001-C | 2.060 | 1.699 | 32,424,396 | all 4 controls pass |

- Corpus integrity: 61/61 pinned blobs verified at
  `b8af1551e45fbe4435745239d29f4d141eea3356` (git blob SHA-1 recomputed from
  bytes read via `git cat-file`; SHA-256 per file in `corpus_manifest.json`).
- Calibration: CAL-PASS-SCR-001 → ADMIT (as pre-declared); CAL-FAIL-SCR-001 →
  reject_duplicate via S1 (as pre-declared). Accuracy 2/2 = 1.0, verified
  in-process before every adjudicating run.
- Admissibility table over the 21 frozen corpus items
  (`admissibility_table.json`):

  | Verdict | Count | Items |
  |---|---|---|
  | reject_duplicate | 3 | A1 (S1), A2 (S2), C4 (S2) |
  | reject_closed_class | 9 | A3–A9 (S3), C2 (S3), C3 (S3) |
  | reject_no_explicit_operation | 4 | C1, C5, C6, C7 (S4) |
  | residual_open_problem | 5 | B1–B5 |
  | undecidable_with_reason | 0 | — |
  | ADMIT | 0 | — |

- Primary metrics: admissible_candidate_count = 0; table_completeness = 1.0;
  calibration_accuracy = 1.0; dedup_owner_coverage = 1.0 (every rejected item
  carries a named owner assignment); corpus_hash_mismatch_count = 0.
- Secondary metrics: first failed predicate per item as tabled above;
  campaign_045_flag_count = 0 (no admitted items); residual frontier entries:
  SOURCE-LOCATOR-OPEN, KN-OPEN-005, KN-OPEN-004, KN-OPEN-006, KN-OPEN-001,
  each with its frozen admission obligation extracted from the pinned
  BATCH-005 candidate report (KN-OPEN-001's pinned record carries no separate
  `admission_obligation` field; its umbrella statement is carried and the
  source is flagged); undecidable_items = 0.
- CTRL-REPLAY-DETERMINISM: two full-sheet applications over all 21 items
  produced byte-identical admissibility tables (pass1 SHA-256
  1e54abf45b5bb6e3…, pass2 identical, zero verdict flips).
- Tail checks: dual-pass consistency holds; residual-frontier completeness
  holds (all five required entries present with obligations).

## 2. Comparison — versus the pre-registered quantities

Every measured primary metric equals its frozen required value (admissible
count 0, completeness 1.0, calibration 1.0, owner coverage 1.0, mismatches
0). The measured table is therefore point-identical to the pre-registered
prediction's quantity as computed by the frozen formula over this snapshot.
This is a comparison statement, not an inference.

## 3. Inference

Left to the Coordinator (lifecycle §9). The Executor records only that the
frozen sheet, as instrumented, mechanically produced the table above on the
frozen snapshot with all controls passing.

## 4. Limitation — what this experiment cannot establish

- Scope is exactly the 21 frozen corpus items at the pinned commit; per
  AGENTS.md rule 6 a zero-admissible table closes only that checked scope.
- The claim tier is toy; nothing here is medium- or crypto-scale evidence in
  either direction, and no live retrieval was performed (external literature
  enters only as the pinned records' claims about it).
- The sheet is an instrument: its predicates were applied as frozen. Whether
  the sheet itself is the right instrument is a Coordinator/Reviewer
  question, not an Executor one.
- The audit adjudicates records, not the mathematics behind them; owner
  records are cited as the corpus's own prior negatives.

## Unexpected observations (recorded, none discarded)

1. The pinned `knowledge/INDEX.md` blob at the frozen commit contains
   unresolved git merge-conflict markers (`<<<<<<< HEAD` /
   `>>>>>>> origin/main`). No sheet check reads INDEX.md (the frozen item
   list is the specification's `audit_item_index`), so no verdict depends on
   it. Recorded for provenance.
2. The pinned `ledger/EV-NET-001.yaml` has internal id `NET-EV-001` (path/id
   mismatch). Owner naming follows the frozen sheet's name (EV-NET-001).
   Recorded for provenance.
3. KN-OPEN-001's residual entry in the pinned candidate report carries no
   separate `admission_obligation` field; the umbrella statement is carried
   with `obligation_source` flagged accordingly.
4. One harness spawn attempt failed before any payload execution (darwin
   rejects `setrlimit RLIMIT_AS`); the harness was repaired (wall-clock
   timeout enforced in-process; memory budget enforced post-hoc against
   measured peak RSS) and the incomplete directory was removed. No run
   record was produced by that attempt and it is not counted among the three
   planned runs.
