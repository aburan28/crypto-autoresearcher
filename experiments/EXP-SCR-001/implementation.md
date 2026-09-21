# EXP-SCR-001 implementation note

Task: TASK-20260727-006 (Executor). Frozen contract: `specification.yaml` v1
(status approved, frozen: true). This note describes the implementation and
every deviation or ambiguity resolution. Observations only; no conclusion on
H-SCR-001 is drawn here or anywhere in the Executor artifacts.

## Components

- `sheet/apply_sheet.py` — single-file mechanical adjudicator and run harness
  (python3 stdlib + PyYAML 6.0.3; no packages installed). Subcommands:
  - `run-a` — corpus integrity control (`CTRL-CORPUS-INTEGRITY`): reads every
    one of the 61 pinned corpus paths as a git blob at the pinned commit
    `b8af1551e45fbe4435745239d29f4d141eea3356` via `git cat-file blob`,
    recomputes the git blob SHA-1 from the bytes read and the SHA-256 of the
    content, and writes `corpus_manifest.json`. Then `CTRL-SHEET-CALIBRATION`:
    the frozen sheet is applied to CAL-PASS-SCR-001 (synthetic typed-operation
    fixture, descriptor embedded in the code exactly as declared in the spec:
    explicit operation, occurrence-level signed source return, complete
    declared ledger lambda=0.44, mu=0.40, all terms assigned, distinct from
    every closed class) and to CAL-FAIL-SCR-001 (the real A1 record). Writes
    `sheet/calibration_receipt.json`. Any corpus mismatch or calibration miss
    aborts the run as completed_invalid.
  - `run-b` — re-verifies corpus integrity and calibration in-process, then
    adjudicates groups A (A1–A9) and B (B1–B5).
  - `run-c` — re-verifies corpus integrity and calibration in-process,
    adjudicates group C (C1–C7), runs `CTRL-REPLAY-DETERMINISM` (a fresh second
    full-sheet application over all 21 items byte-compared against the pass-1
    table assembled from RUN-SCR-001-B's raw record plus this run's C
    verdicts), builds the residual frontier table, and writes
    `admissibility_table.json` and `residual_frontier.json`.
  - `harness` — executes one payload run inside an immutable
    `runs/<RUN-ID>/` directory (refuses to overwrite), enforces the frozen
    1800 s per-run wall-clock cap via `subprocess` timeout plus
    `RLIMIT_AS = 4 GB` / `RLIMIT_CPU = 3600 s`, captures stdout/stderr, and
    measures wall seconds (`time.monotonic`), CPU seconds and peak RSS
    (`resource.getrusage(RUSAGE_CHILDREN)` delta around the payload child;
    on this darwin host ru_maxrss is bytes). Writes `manifest.yaml`,
    `command.txt`, `environment.json`, `raw-result.json`, `summary.json`,
    `stdout.log`, `stderr.log` and the byte-identical handoff-named aliases
    `raw.json`, `stdout.txt`, `stderr.txt`.
  - `validate` — lifecycle step-7 checks (see execution-report.yaml).

## How the adjudication stays mechanical

For each audit item the code runs explicitly coded checks against pinned
corpus bytes (YAML field equality, required substring markers, with quoted
excerpts recorded per check), deriving a fact vector; predicates S1–S5 are
then a pure function of that vector (`apply_sheet`). If any grounding marker
is absent, the item receives `undecidable_with_reason` — never a silent
verdict. Group-B obligations are extracted verbatim from the pinned BATCH-005
candidate report's `narrowest_remaining_open_problems` section. Verdict
vocabulary is exactly the frozen set: ADMIT, reject_duplicate,
reject_closed_class, reject_no_explicit_operation, reject_not_sub_rho,
residual_open_problem, undecidable_with_reason.

C-item wiring (grounded in the pinned candidate report's
`literature_deduplication` and `corpus_deduplication` sections and the named
KN-LIT records): C1 survey class → no explicit operation (S4, owner
KN-LIT-006); C2 Petit-Kosters-Messeng prime-field decomposition class → the
S3 closed class owned by KN-LIT-025 / FINDING-PF-IC-001; C3 McGuire-Mueller
summation-evaluation screen → same S3 class with the McGuire-Mueller screen
named (pinned record also reports exponential stated complexity); C4
Mahalanobis zero-minor lineage → S2 rename of the excluded
IDEA-20260723-002 interface, with the S2 scope guard checked (no pinned
record presents a repaired named variant); C5 kSUM/3SUM cluster → S4, P1552 /
P1553 records supply no endpoint-only source operation inside the charged
rectangle; C6 Shoup lower bound → S4 (a barrier theorem, not an operation;
it grounds the 0.50 baseline S5 compares against); C7 quantum resource
reduction → S4 with the recorded reason "different computational model;
excluded from the classical screen" per the frozen `external_references`.

## Deviations and ambiguity resolutions

1. **Per-run artifact naming (ambiguity resolution, not a content change).**
   The frozen specification's `required_artifacts` names per-run files
   `raw-result.json`, `stdout.log`, `stderr.log`; the handoff
   (TASK-20260727-006) deliverables name `raw.json`, `summary.json`,
   `stdout.txt`, `stderr.txt`. Both enumerations are satisfied: each run
   directory carries both naming sets with byte-identical content plus a
   harness-generated `summary.json`. No required artifact is missing and no
   protocol content was altered. Recorded as DEV-1 in the execution report.
2. `required_artifacts` also lists `ledger/hypotheses/H-SCR-001.yaml`. That
   file pre-exists as a frozen input outside the Executor write scope; it was
   verified present and left untouched (the Executor changes no ledger
   record).
3. Non-path owner records (P1547, P1540, P1553-id mentions, McGuire-Mueller
   screen) are verified by explicit mention markers inside the pinned
   BATCH-005 exclusion entries; corpus-path owners are verified by content
   markers in their pinned blobs.

No other deviations from the frozen protocol. No amendment was requested.
