# Protocol publication validation

- Main merged: `7b1428c2fac72440930abf8d3bf626f3488ffabc`.
- `tools/test_research_dispatch.py`, `tests/test_research_dispatch_reconciliation.py`, `tools/test_validate_dispatch_reference.py`: 117 passed, 37 subtests passed.
- Native shell: `sh -n` passed.
- Newest selector: `EXP-ISOU-e7eeb5` has `execution_state: ready` before archive.
- `tests/test_newest_experiments.py` plus reconciliation: 10 passed, one unchanged-main failure in `test_planned_trial_needs_a_real_dispatch_queue` (fixture expects ready, current selector returns needs_plan_repair). No production/test source is changed by this package.
- `tools/newest_experiments.py` SHA256: `55ab4a50c9799e212638fe87fbe91f22fac9296e184a235a31839d9193b15aa4`.
- `tests/test_newest_experiments.py` SHA256: `f78135892b7f59bf3a9690c516186980ff2e1015edf97181ac89ceb909b9dcf8`. Both match origin/main.
- Initial full ledger validation refused the sparse checkout; explicitly sparse diagnostic produced missing-record errors and was not a passing gate. Full materialization and validation follow.

No scientific trial was executed during coordination.

Full checkout completed: 131,871 tracked files materialized. `validate_ledger.py` ran fully and reported 315 errors in existing records; the log names none of this package's GOAL/EXP/H/RQ/DEC/TASK identifiers. The full gate remains non-green. Raw log is preserved alongside this note. Unrelated LFS content refresh differences are excluded from the package.
