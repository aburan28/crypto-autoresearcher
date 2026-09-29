# TASK-20260813-c0ec71 — THE LEAD PRODUCER

    goal / batch    GOAL-MLKEM-005 / BATCH-a6fab5
    role            executor
    policy          executor-implementation            effort medium
    state           queued
    depends_on      TASK-20260813-d63082
    review_required true
    archived_by     TASK-20260813-861a58
    budget          3600 s HARD CAP (wall clock), 2 GB, 1 run.
                    EXPECTED: MINUTES if fpylll is available in this session
                    (Branch A); potentially close to the full cap if falling
                    back to a from-scratch HKZ implementation (Branch B).
    claim tier      TOY

## What it must do, in order

**(1)** Independently RE-VERIFY, in this own session, `PREREG-5` §1's
infrastructure signal: attempt `pip install fpylll` (and `pip install
cysignals` if that first attempt fails on the same missing-transitive-
dependency error the dispatching session hit), then
`import fpylll; from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration`,
and a basic LLL reduction as a functional smoke test. Report the outcome
PLAINLY, either way, as infrastructure signal — never as a research result —
BEFORE choosing an implementation branch.

**(2)** Declare the `ROUTE-I''` implementation choice (`PREREG-5` §2.2)
BEFORE any `D_route''` number is computed: **Branch A** (fpylll available —
use its own public reduction/enumeration API directly, matching `ROUTE-P`'s
own BKZ(block=`d`) + explicit-HKZ-sweep + independent-per-index-enumeration
structure as closely as an independently-written wrapper allows) or
**Branch B** (fpylll unavailable — a from-scratch full HKZ implementation in
pure Python/numpy, bounded to `d <= 40`, fresh code not derived from
`BATCH-6e08fe`'s own `ROUTE-I'` reduction/enumeration code). State which
branch and why, checkable against the actual committed script.

**(3)** Confirm (§2.3) that genuine `ROUTE-P` per-basis ground truth exists
at all 6 named cells (`hkz/L7_b5`, `L7_b15`, `L9_b7`, `L9_b22`, `L11_b10`,
`L11_b30`) by a direct read of `results_relvar.json`'s own `G_REL1.hkz`
block, reporting the exact basis count at each cell.

**(4)** Run obligation 1 (§2.4): for every one of the 6 cells, compute
`D_route''` = max absolute deviation against `results_relvar.json`'s OWN
`G_REL1.hkz` per-basis values — NEVER against `results_l7l8.json` or
`results_am4.json` — and `VERDICT''` via `PREREG-3` §3.3's own formula,
verbatim. Run obligation 2 (§2.5 — aggregate `ALL-SURVIVE`/`SOME-ARTIFACT`).
Read off the termination branch (`T-HKZINDEP-NODATA`/`-ARTIFACT`/
`-CONFIRMED`, `-PARTIAL` suffix as required) under §2.6's frozen precedence.

## Absolute constraints

**NO NEW REDUCTION ABOVE `d = 40`, ANYWHERE, FOR ANY REASON.** If Branch B is
judged INFEASIBLE (not merely slow — genuinely not achievable as a correct
HKZ implementation within budget), state this explicitly with reasoning; do
not conflate "infeasible" with "did not finish in time." If the hard
wall-clock cap is reached before every named cell has a computed
`D_route''`, this is INFRASTRUCTURE SIGNAL (§3.2 of `PREREG-5`) — report
exactly which cells were not computed, as `NOT COMPUTED: budget exhausted`,
never defaulted to either verdict. Do not specify, propose or imply a
replacement dispersion criterion, gate or threshold — §2.4's comparison is
`PREREG-3` §3.3's own formula, reused verbatim for a second time. Do NOT
copy, adapt or structurally paraphrase `BATCH-6e08fe`'s own
`measure_route_reimpl.py` reduction/enumeration code for `ROUTE-I''`'s
reduction/enumeration step (`PREREG-5` §2.2 point 1). `lam1n` is OUT OF
SCOPE — do not compute it.

## Artifacts — SEVEN PATHS

    tasks/TASK-20260813-c0ec71/measure_hkz_indep.py
    tasks/TASK-20260813-c0ec71/results_hkz_indep.json
    tasks/TASK-20260813-c0ec71/report_hkz_indep.md
    tasks/TASK-20260813-c0ec71/command.txt
    tasks/TASK-20260813-c0ec71/stdout.log
    tasks/TASK-20260813-c0ec71/stderr.log
    tasks/TASK-20260813-c0ec71/run_manifest.yaml

`report_hkz_indep.md` must list every path this task wrote, exactly as this
goal's every prior lead producer has done, so the snapshot archive's
change-set-equality check is verifiable. File names are this Coordinator's
suggestion; the executor may adjust them if it records the actual names used
consistently across `command.txt`, `run_manifest.yaml` and the report.
