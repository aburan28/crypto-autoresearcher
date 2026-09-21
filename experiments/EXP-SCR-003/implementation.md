# EXP-SCR-003 implementation note

Executor: handoff TASK-20260727-008. Frozen protocol: `specification.yaml` v1
(status approved, frozen: true). No amendment requested or applied.

## What was implemented

Two stdlib + PyYAML programs under `sheet/`:

- `apply_screen.py` — the mechanical adjudicator. One invocation per stage:
  - `freeze_and_calibrate` (RUN-SCR-003-A): reads every corpus artifact as git
    blob content at pinned commit `b8af1551e45fbe4435745239d29f4d141eea3356`
    (`git rev-parse <commit>:<path>` for the blob SHA-1, `git cat-file blob`
    for content), checks all 30 paths against the spec hash manifest, records
    SHA-256 of each blob in `corpus_manifest.json`; then adjudicates the three
    frozen calibration fixtures through the NS-TX-PRIME-001 machine BEFORE any
    corpus family verdict and writes `sheet/calibration_receipt.json`.
  - `dedup_classification` (RUN-SCR-003-B): re-verifies the corpus and
    re-binds to RUN-A's manifest (SHA-256 equality), then assigns each of the
    8 frozen families its dedup class with a named owner. Assignment is
    mechanical: the family name, the pinned BATCH-007 eligibility token, the
    criterion_result token (all in the hash-verified
    `ggm_screen_report.yaml`), and the owner-record tokens (THM-JETBARRIER1
    T2/T4/T1.3/T6, P1547 gate additive/nonadditive, ECDLP-IDEA-268,
    FINDING-PF-IC-001, EV-EQJ-001, EV-TTN-001, ggm_simulability_note G2) must
    all be present; anything missing yields `undecidable_with_reason` (run
    inconclusive, never negative). No family required judgement beyond the
    mechanical sheet.
  - `ns_tx_application_and_aggregate` (RUN-SCR-003-C): applies the frozen
    N1–N5 routing to all 8 families (families covered by a verified named
    owner do not proceed to admission scoring), runs the full screen twice
    (CTRL-REPLAY-DETERMINISM, canonical-JSON byte comparison), carries the 4
    residual placeholders unscored, applies the split-gate tail checks, and
    emits `family_table.json` and `admission_decision.json`.
- `run_stage.py` — the per-run driver: hard 1800 s wall-clock timeout via
  subprocess kill, byte-exact stdout/stderr capture, measured wall/CPU/peak
  RSS, terminal-status classification, immutable run directory (refuses to
  overwrite an existing one).

Key implementation choices:

- Separation (N1–N3) and usefulness (N4–N5) verdicts are separate fields on
  every family. `simulable_closed` requires a verified pinned covering
  theorem; `encoding_only_gap` is never recorded as source-bearing; both rules
  are re-checked as tail checks on the emitted table.
- The additive-channel boundary is structural: F3 closes under P1547 with the
  scope note recorded, while F4 (nonadditive) remains a distinct
  `uninstantiated_residual` with `cannot_apply_without_oracle`.
- Calibration fixtures are structured declarations instantiating the frozen
  fixture descriptions; the screen must map them to the pre-declared verdicts
  (ADMIT / simulable_closed / N3-certified+N4-rejected) before any corpus
  verdict is emitted. Observed: 3/3.

## Measurement mechanisms (measured, never guessed)

- Timeout: `subprocess.run(..., timeout=1800)` hard kill; on expiry the run is
  classified `resource_exhaustion`.
- Memory: darwin rejects `setrlimit(RLIMIT_AS)`, so no pre-hoc address-space
  limit was installed. The 4 GB cap is enforced post-hoc: measured peak RSS
  (`max(RUSAGE_SELF, RUSAGE_CHILDREN).ru_maxrss`, bytes on darwin) is compared
  against the cap after child exit; overflow classifies `resource_exhaustion`.
  The mechanism is recorded in every manifest.
- CPU: RUSAGE_CHILDREN utime+stime delta plus driver self delta.
- Git dirty flag: `git status --porcelain` at run start over tracked paths,
  excluding any path with a component beginning `._` (exFAT AppleDouble
  artifacts of this volume) and excluding untracked paths, per the task basis
  "non-._ tracked paths". Basis disclosed in every manifest. Observed:
  `dirty=false` for all runs at commit
  `9c9ec23fbe55067cdf4954dd7b8a0d25494ce0e3`.
- Seeds: `[]` — deterministic audit, no randomness (seed_policy recorded).

## Deviations from the approved protocol

1. Artifact naming: the frozen specification's `required_artifacts` names
   per-run files `raw-result.json`, `stdout.log`, `stderr.log`; handoff
   TASK-20260727-008 deliverables name `raw.json`, `summary.json`,
   `stdout.txt`, `stderr.txt`. Both naming sets are emitted for every run;
   paired files are byte-identical; `summary.json` is handoff-only. No
   protocol content changed.
2. Repair re-execution: the first attempt at planned run RUN-SCR-003-A
   terminated `failed_implementation` (KeyError: 'calibration_fixtures' —
   wrong spec key path in the fixture loader; an implementation bug, not a
   protocol or corpus defect). Per the failure taxonomy
   (`implementation_error` requires repair; a crash is evidence for nothing),
   the implementation was repaired and stage A re-executed as
   `RUN-SCR-003-A-b` under a new immutable run directory; the failed attempt
   is preserved unmodified at `runs/RUN-SCR-003-A/`. The frozen protocol was
   not changed and no completed run was re-scored. This yields 4 run
   directories against `maximum_runs: 3` planned; recorded here and in the
   execution report for Coordinator adjudication.

No other deviations. No anomalies beyond the above. No external web review;
no packages installed (python3 3.12.8 stdlib + PyYAML 6.0.3, git).

## Reproduction

Each run directory's `command.txt` holds the exact screen argv; e.g.:

```sh
python3 experiments/EXP-SCR-003/sheet/apply_screen.py \
  --repo-root <repo-root> --stage freeze_and_calibrate \
  --run-id RUN-SCR-003-A-b \
  --result-path experiments/EXP-SCR-003/runs/RUN-SCR-003-A-b/raw-result.json
```

Stages: `freeze_and_calibrate`, `dedup_classification`,
`ns_tx_application_and_aggregate` (run in order; B/C re-bind to the RUN-A
corpus manifest). Top-level artifacts (`corpus_manifest.json`,
`family_table.json`, `admission_decision.json`,
`sheet/calibration_receipt.json`) contain no timestamp or run-specific fields
and regenerate byte-identically from the same pinned commit and frozen spec.
