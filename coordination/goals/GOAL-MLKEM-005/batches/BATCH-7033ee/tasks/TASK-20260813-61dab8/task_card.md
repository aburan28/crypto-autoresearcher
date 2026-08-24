# TASK-20260813-61dab8 — Author PREREG-4

    goal / batch    GOAL-MLKEM-005 / BATCH-7033ee
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           completed
    depends_on      (none)
    review_required false
    archived_by     TASK-20260813-30cdca
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## What it had to do, in this order

**(a) DISCHARGE RC-3** — restate `BATCH-fbb639`'s `R-C-OUT-0` coverage table
at exactly four `hkz` cells: `hkz/L9_b15` and `hkz/L11_b20` as genuinely
`UNCOVERED` (the Red Team's own probe found no genuine `am4` value at these
middle betas); `hkz/L9_b22` and `hkz/L11_b30` with the corrected `TRUE`
`beta_hi`-based `D_route` source, **numerically unchanged at `0.0`**. No new
computation; both values are already in `probe_coverage_beta_mismatch_
output.json`, read and carried verbatim.

**(b) FREEZE THE LEAD MEASUREMENT** — commission `ROUTE-I2`: a genuinely
non-code-shared re-implementation of the `lam1n`/`hkz` observables at
`L7`/`L9`/`L11`, forbidding import or transcription of `make_A`,
`build_basis` or `hkz_profile` from any prior committed file, requiring a
genuinely different reduction/enumeration algorithmic path (a different
library, or a from-scratch LLL + local-block enumeration — explicitly stated
sufficient at `d <= 40`), and re-running the exact `D_route` comparison
against the same already-archived `ROUTE-P` values. `PREREG-4` §2 freezes
the `F0` basis specification as prose (not code), the exact `results_
relvar.json` `G_REL2` location of `ROUTE-P`'s per-basis values, a
three-obligation structure (verify `ROUTE-P` → build+run `ROUTE-I2` →
aggregate comparison), and a three-branch termination clause (`T-INDEP-
NODATA` / `-CONFIRMS` / `-UNDERMINES`, each with a mandatory `-PARTIAL`
suffix and explicit precedence), plus §2.8's statement of why `PREREG-2`
7.5's repair bar does not apply.

## Executed 2026-08-13 by the session that opened this batch

This session held a shell used only for `git fetch`/`merge`, ID minting via
`tools/allocate_id.py`, and read-only inspection (including a direct Python
import check confirming `fpylll`/`sympy` are not installed in this
environment — declared gap `G-5`). It ran **no reduction, no measurement of
this batch's substantive comparison, and computed no hash of a producer
artifact**. It wrote `prereg.md` and stopped. `prereg_sha256.txt` therefore
belongs to `TASK-20260813-30cdca` (declared gap `G-2`). Every number cited
from reading the committed corpus (the `results_am4.json` `X_hi` values, the
`G_REL2` path structure, the `lam1n`/`hkz` formulas, the `EV-MLKEM-aa39ad`
`OBS-1` anchor) is attributed as this session's own observation, weaker than
a measurement, with its exact source path given so the lead can check it
independently.

## Artifacts — ONE PATH

    tasks/TASK-20260813-61dab8/prereg.md

## The single thing not to get wrong

**`prereg.md` MUST NOT RIDE IN THE BATCH-OPENING COMMIT.** It exists in the
working tree from the moment this batch was opened. Its **first appearance
in the history must be the notarizing commit** `TASK-20260813-30cdca`. Stage
paths explicitly; never `git add -A` in this batch.
