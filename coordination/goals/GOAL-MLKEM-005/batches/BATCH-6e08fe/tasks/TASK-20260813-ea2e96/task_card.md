# TASK-20260813-ea2e96 — THE LEAD PRODUCER

    goal / batch    GOAL-MLKEM-005 / BATCH-6e08fe
    role            executor
    policy          executor-implementation            effort medium
    state           queued
    depends_on      TASK-20260813-e24ad9
    review_required true
    archived_by     TASK-20260813-2d6b5e
    budget          1800 s HARD CAP (wall clock), 2 GB, 1 run.
                    EXPECTED: MINUTES, NOT HOURS. This is the one task in
                    this batch that performs genuinely NEW reduction.
    claim tier      TOY

## What it must do, in order

**(a)** Carry `PREREG-4` §1's frozen RC-3 correction verbatim into its
report — `hkz/L9_b15`/`hkz/L11_b20` restated UNCOVERED, `hkz/L9_b22`/
`hkz/L11_b30` restated with the corrected true `beta_hi` source, unchanged
at `0.0`. No recomputation.

**(b)** Run `PREREG-4` §2's coverage-audited independent-route measurement:
**obligation 0** (§2.3 — read `results_relvar.json`'s `G_REL1` block only,
report per-basis ground-truth availability for `lam1n`/`hkz` at all 18
cells, expect the 3 middle-beta cells UNCOVERED, verify rather than assume);
**declare the ROUTE-I' implementation choice** (§2.2 — a genuinely
non-code-shared basis-construction + reduction/enumeration path, stated and
justified BEFORE any `D_route'` number is computed, and checkable against
the actual script: no import, copy or structural paraphrase of `make_A`,
`build_basis` or `hkz_profile` from `measure_am4.py`/`measure_relvar.py`/
`replicate_l7l8.py` or any descendant, INCLUDING `BATCH-4ed139`'s
`replicate_l7l8.py`); **obligation 1** (§2.4 — for every covered cell, up
to 8 independently-computed values, `D_route'` = max absolute deviation
against `results_relvar.json`'s OWN `G_REL1` per-basis values — NEVER
against `results_l7l8.json` or `results_am4.json`, both explicitly excluded
as `ROUTE-P` sources — `VERDICT'` via `PREREG-3` §3.3's own formula,
verbatim); **obligation 2** (§2.5 — aggregate `ALL-SURVIVE`/`SOME-ARTIFACT`).
Read off the termination branch (`T-INDVERIFY-NODATA`/`-ARTIFACT`/
`-CONFIRMED`, `-PARTIAL` suffix as required) under §2.6's frozen precedence.

## Absolute constraints

**NO NEW REDUCTION ABOVE `d = 40`, ANYWHERE, FOR ANY REASON.** If the hard
wall-clock cap is reached before every covered cell has a computed
`D_route'`, this is INFRASTRUCTURE SIGNAL (§3.2 of `PREREG-4`) — report
exactly which cells were not computed, as `NOT COMPUTED: budget exhausted`,
distinct from genuinely `UNCOVERED` cells, never defaulted to either
verdict. Do not specify, propose or imply a replacement dispersion
criterion, gate or threshold — §2.4's comparison is `PREREG-3` §3.3's own
formula, reused verbatim.

## Artifacts — SEVEN PATHS

    tasks/TASK-20260813-ea2e96/measure_route_reimpl.py
    tasks/TASK-20260813-ea2e96/results_route_reimpl.json
    tasks/TASK-20260813-ea2e96/report_route_reimpl.md
    tasks/TASK-20260813-ea2e96/command.txt
    tasks/TASK-20260813-ea2e96/stdout.log
    tasks/TASK-20260813-ea2e96/stderr.log
    tasks/TASK-20260813-ea2e96/run_manifest.yaml

`report_route_reimpl.md` must list every path this task wrote, exactly as
this goal's every prior lead producer has done, so the snapshot archive's
change-set-equality check is verifiable. File names are this Coordinator's
suggestion; the executor may adjust them if it records the actual names used
consistently across `command.txt`, `run_manifest.yaml` and the report.
