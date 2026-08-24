# TASK-20260813-415c21 — THE LEAD PRODUCER: RC-3 carry + build & run ROUTE-I2

    goal / batch    GOAL-MLKEM-005 / BATCH-7033ee
    role            executor
    policy          executor-implementation     independent_session_required
    state           queued
    depends_on      TASK-20260813-30cdca
    review_required true   -> TASK-20260813-e04ebc, TASK-20260813-28eb06
    archived_by     TASK-20260813-5d1920
    budget          7200 s, 4 GB, 1 run
    claim tier      TOY

## What this task must do, in this order

1. **Carry RC-3 verbatim** (`PREREG-4` §1) into `report_route_i2.md`. No
   recomputation, no re-run of `measure_c3lane.py`.
2. **Obligation 0** — read `results_relvar.json`'s `G_REL2` block and confirm
   `ROUTE-P`'s per-basis `lam1n`/`hkz` coverage at all 18 cells (3 lattices x
   3 betas). Report the exact path and any gap found.
3. **Build `ROUTE-I2`** — its own basis construction from `PREREG-4` §2.1's
   mathematical specification (`default_rng([1,d,k,i])`, the exact block
   matrix), and its own reduction/enumeration routine satisfying `PREREG-4`
   §2.2's independence requirements (no import/transcription of `make_A`,
   `build_basis`, `hkz_profile`; a genuinely different algorithmic path —
   a different library, or a from-scratch LLL + local-block enumeration,
   explicitly sufficient at `d <= 40`). **This environment has no fpylll,
   sage or flint installed at dispatch time** (declared gap `G-5`) — a
   from-scratch implementation, or a fresh-venv install of a genuinely
   different library, are both acceptable; the budget (7200 s) is sized for
   either.
4. **Obligation 1** — compute `lam1n`/`hkz` via `ROUTE-I2` at every basis of
   every cell, report per-basis values, `D_route_independent`, `s_c^fib`,
   and the per-cell verdict, plus a violation/optimality diagnostic per
   basis. Uncoverable cells are reported `UNCOVERED2` with a reason, never
   defaulted to a verdict.
5. **Obligation 2** — aggregate `COVERED2`/`UNCOVERED2`, the tally, a direct
   per-cell comparison against `PREREG-3`'s own `D_route` (`0.0`), and
   summary statistics.
6. **Read off the termination branch** (`T-INDEP-NODATA` / `-CONFIRMS` /
   `-UNDERMINES`, `-PARTIAL` suffix per its own rule) under `PREREG-4` §2.6's
   frozen precedence, and list any cell to be flagged under §2.7's revisit
   condition (empty list if none).

## The one thing the report must name explicitly

At least one **genuine algorithmic difference** between `ROUTE-I2`'s
reduction pipeline and `hkz_profile`'s (a different LLL delta, a different
block-enumeration strategy, a different or no `fpylll` dependency, a
differently-ordered reduction loop). A report that cannot name one has not
discharged the independence requirement — this is exactly the defect
`KN-FIND-9b5df0` found in the batch this one responds to.

## Artifacts — SEVEN PATHS

    tasks/TASK-20260813-415c21/measure_route_i2.py
    tasks/TASK-20260813-415c21/results_route_i2.json
    tasks/TASK-20260813-415c21/report_route_i2.md
    tasks/TASK-20260813-415c21/command.txt
    tasks/TASK-20260813-415c21/stdout.log
    tasks/TASK-20260813-415c21/stderr.log
    tasks/TASK-20260813-415c21/run_manifest.yaml

## Hard constraints

- No reduction above `d = 40`, anywhere, for any reason.
- No import, `exec`, copy-paste or mechanical transliteration of `make_A`,
  `build_basis`, `hkz_profile`, `gram_int`, or the `fpylll`
  `Strategy`/`BKZReduction`/`Enumeration` call sequence as sequenced in
  `measure_relvar.py`/`measure_am4.py`/`replicate_l7l8.py`, or any file that
  itself carries any of those functions verbatim.
- Commit nothing. Do not edit any prior committed artifact.
- Do not change a success criterion after seeing an outcome — `PREREG-4` is
  frozen.
- A timeout, dependency failure, or infrastructure gap is reported as
  infrastructure signal (`T-INDEP-NODATA` if it blocks every cell), never as
  a route disagreement or a dispersion finding.
- Claim tier stays TOY throughout.
