# TASK-20260813-630414 — THE LEAD PRODUCER

    goal / batch    GOAL-MLKEM-005 / BATCH-8d09f5
    role            executor
    policy          executor-implementation            effort medium
    state           queued
    depends_on      TASK-20260813-62cd6b
    review_required true
    archived_by     TASK-20260813-cb8943
    budget          3600 s HARD CAP (wall clock), 2 GB, 1 run.
                    EXPECTED: MINUTES (Branch A / fpylll only — no Branch-B
                    contingency is commissioned by PREREG-6 §1/§3.3).
    claim tier      TOY

## What it must do, in order

**(1)** Independently RE-VERIFY, in this own session, `PREREG-6` §1's
infrastructure signal (identical sequence to `PREREG-5` §1: `pip install
fpylll` [+ `cysignals` if needed], the same import set, an LLL smoke test).
Report plainly, either way, as infrastructure signal only. **If `fpylll` is
unavailable in this session, STOP and report `T-MUTCTRL-NODATA` branch
(b) — do not attempt a from-scratch fallback; none is commissioned by this
document.**

**(2)** Independently RECOMPUTE `PREREG-6` §2.3's frozen prediction
directly from `results_relvar.json`'s own `G_REL1.hkz.L7`/`L11` per-basis
arrays (cyclic adjacent-basis max-abs-difference at `hkz/L7_b5`'s `X_a`
field and `hkz/L11_b30`'s `X_b` field). Report whether your own
recomputation matches `PREREG-6`'s stated numbers (`0.0665893489077094` at
`L7_b5`, `0.00948000985335451` at `L11_b30`). A mismatch is reported as a
finding about `PREREG-6`, not silently corrected or substituted.

**(3)** Write a NEW, self-contained file (never editing
`measure_hkz_indep.py`, never importing from it) that is a byte-for-byte
copy of its `route_ii_make_A`, `route_ii_build_basis`, `hkz_route_ii` and
`route_ii_hkz_value` functions, with **EXACTLY ONE line changed**, in the
copy of `route_ii_make_A` only: the seed-formula index argument changed
from `i` to `(i + 1) % N_BASES` (`PREREG-6` §2.2). Include, in the report, a
literal machine-generated diff (`difflib.unified_diff` or equivalent)
between the new file and `measure_hkz_indep.py`, confirming mechanically
that exactly this one functional line differs.

**(4)** Run obligation 1 (§2.4): for `hkz/L7_b5` and `hkz/L11_b30` only,
compute `D_route_mut` = max absolute deviation between the mutant's output
and `results_relvar.json`'s OWN `G_REL1.hkz` per-basis values — NEVER
`results_l7l8.json`/`results_am4.json` — and `VERDICT_mut` via `PREREG-3`
§3.3's own formula, verbatim. State explicitly, per cell, whether the
result reads DETECTED (`VERDICT_mut = "DOES NOT EXCEED"`) or NOT DETECTED
(`VERDICT_mut = "EXCEEDS"`) — §2.4 point 5's mapping, quoted in full in
your own report so a reader does not have to cross-reference `PREREG-6`.
Run obligation 2 (§2.5). Read off the termination branch
(`T-MUTCTRL-NODATA`/`-DETECTED`/`-NOT-DETECTED`/`-MIXED`, `-PARTIAL` suffix
as required) under §2.6's frozen precedence.

## Absolute constraints

**NO NEW REDUCTION ABOVE `d = 40`, ANYWHERE, FOR ANY REASON.** Only the two
named cells (`hkz/L7_b5`, `hkz/L11_b30`) are attempted — do not extend to
any other cell. If the hard wall-clock cap is reached before both named
cells have a computed `D_route_mut`, this is INFRASTRUCTURE SIGNAL (§3.2 of
`PREREG-6`) — report exactly which basis/cell was not computed, as `NOT
COMPUTED: budget exhausted`, never defaulted to either verdict. Do not
specify, propose or imply a replacement dispersion criterion, gate or
threshold — §2.4's comparison is `PREREG-3` §3.3's own formula, reused
verbatim for a third time. `measure_hkz_indep.py` is FROZEN and must not be
edited in place (rule 15) or imported from. `lam1n` is OUT OF SCOPE — do
not compute it. This task does not, and cannot, characterize the
instrument's power against any defect OTHER than the one named seed-index
mutation.

## Artifacts — EIGHT PATHS

    tasks/TASK-20260813-630414/measure_hkz_mutation6.py
    tasks/TASK-20260813-630414/results_hkz_mutation6.json
    tasks/TASK-20260813-630414/hkz_mutation6_writeup.md
    tasks/TASK-20260813-630414/command.txt
    tasks/TASK-20260813-630414/stdout.log
    tasks/TASK-20260813-630414/stderr.log
    tasks/TASK-20260813-630414/run_manifest.yaml
    tasks/TASK-20260813-630414/environment.json

`hkz_mutation6_writeup.md` must list every path this task wrote, exactly as
this goal's every prior lead producer has done, so the snapshot archive's
change-set-equality check is verifiable. File names are this Coordinator's
suggestion; the executor may adjust them if it records the actual names
used consistently across `command.txt`, `run_manifest.yaml` and the report
(matching `TASK-20260813-c0ec71`'s own precedent renaming
`report_hkz_indep.md` → `hkz_indep_writeup.md`).
