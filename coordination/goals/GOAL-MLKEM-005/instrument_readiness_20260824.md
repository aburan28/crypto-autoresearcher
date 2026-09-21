# GOAL-MLKEM-005 — instrument readiness for RT-CTRL-1, 2026-08-24

Coordinator pre-dispatch check, run BEFORE opening the successor batch to
BATCH-0d5018. Nothing here is a research result. No lattice claim, no cost claim,
and no statement about ML-KEM at any parameter set. Claim tier is untouched.

## Why this check exists

`GOAL-MLKEM-005.next_action` names EXACTLY ONE action: a producer running the Red
Team's RT-CTRL-1 — ONE FULL BKZ TOUR AT (d=512, beta=55), SEED 452658293,
BYTE-IDENTICAL CONSTRUCTION AND SEED FORMULA, AT mpfr_bits = 100 — with expected
cost of the same order as the 2502.74 s already spent at 75 bits, and reporting
marks at 3600 s and 14400 s. A four-hour dispatch is worth ten minutes of checking
first.

## What was checked, and the result

1. **fpylll was ABSENT and is now OBTAINED.** `import fpylll`, `g6k` and `gmpy2`
   all failed at session start. `KN-TECH-14efa5`'s route — `python3 -m venv` then
   `pip install --no-cache-dir passagemath-standard` — reproduced in THIS container
   on the first attempt, giving fpylll 0.6.4 with LLL, GSO, BKZ and
   `fpylll.algorithms.bkz2.BKZReduction` all importable. `KN-TECH-797223` records
   the recipe as container-dependent with four further failures; this is a
   successful reproduction in a new container and is reported as one data point,
   not as a general claim about the recipe.
2. **The note's documented breakage reproduces exactly.** `BKZ.EasyParam(...)`
   raises `RuntimeError: Cannot open strategies file.`, and its documented fix
   works: dim-60 qary q=3329, BKZ-30 x 4 loops, ||b0|| 176.1 -> 125.3 in 0.21 s.
   `FPLLL.set_precision(100)` returns 100, so the precision RT-CTRL-1 needs is
   settable.
3. **The pinned producer script IMPORTS and RUNS here, and then FAILS.** Running
   `worker_main_cell` from the committed, hash-pinned
   `BATCH-0d5018/tasks/TASK-20260815-f14d3c/stage0_d512_beta5570_precision_bisection_and_reattempt.py`
   (sha256 58a1fdc21f45730789feeff69c6a6fd7c24bf4938be15d6e878afd246d0de485) on a
   deliberately tiny smoke cell (d=60, beta=20, mpfr=100) completes the outer LLL
   in 0.0559 s and then returns `status: ERROR`,
   `error: RuntimeError: Cannot open strategies file.` It fails at `BKZ.Param`,
   BEFORE any tour. It also cannot serialise its own error report: the recorded
   field `strategies_file_used` is the BYTES object
   `b'/project/local/share/fplll/strategies/default.json'`, which raises
   `TypeError: Object of type bytes is not JSON serializable`.

## The blocker, stated precisely

The script's `_strategies_path()` tries `/usr/share/libfplll8/strategies/default.json`
and falls back to `BKZ.DEFAULT_STRATEGY`. In this container the Debian path does not
exist (no libfplll8 package), and `BKZ.DEFAULT_STRATEGY` is the wheel's build-time
path, also absent. A filesystem search found NO fplll strategies file anywhere.

**THE BLOCKER IS NOT THAT fpylll IS MISSING — IT IS OBTAINED AND VERIFIED.** The
blocker is that RT-CTRL-1's comparability to its own 75-bit reference depends on a
BKZ strategies input that the predecessor recorded BY PATH AND NOT BY CONTENT:

    environment.json                          strategies_file      = '/usr/share/libfplll8/strategies/default.json'
    main_grid_..._results.json  main_grid[0]. strategies_file_used = '/usr/share/libfplll8/strategies/default.json'

No sha256. No libfplll8 package version. The predecessor's `fpylll_version` is
0.6.4 — the SAME version obtained here — so the gap is the strategies file alone,
and it is a container that no longer exists. This is exactly the failure mode
CLAUDE.md's "Archive receipts bind to CONTENT first" exists to prevent, occurring
on a load-bearing input to a producer rather than on an archive receipt.

The available substitute is not equivalent. `KN-TECH-14efa5`'s in-process
`[Strategy(b) for b in range(41)]` is PRUNING-FREE — block 30 carries a single
pruning parameter — whereas fplll's `default.json` carries a tuned pruning
schedule per block size. Upstream fplll master's `strategies/default.json` is
fetchable, but it is upstream master and NOT identified as the Debian libfplll8
build the reference run used.

Substituting any of these changes the reduction's pruning schedule while RT-CTRL-1
is varying precision. That CONFOUNDS THE CONTROL'S OWN VARIABLE: a 100-bit run
under one pruning schedule compared against a 75-bit run under another cannot
attribute a difference to precision, which is the single thing RT-CTRL-1 exists to
measure.

## Recommendation to the Coordinator — a decision is required and is not self-grantable

Three routes, in the order this session ranks them:

(c) PREFERRED — RE-RUN THE 75-BIT REFERENCE CELL ALONGSIDE THE 100-BIT CELL, under
    whatever single strategies source this container can supply, in the SAME
    invocation. This converts an unresolvable provenance gap into a matched pair
    and makes the batch self-contained: the absent file stops mattering because
    nothing is compared across containers. Cost is one extra cell, roughly
    doubling the run (~2 x 2502.74 s at the reference scale), against a campaign
    budget that is UNBOUNDED (maximum_batches null, wall clock null). It is the
    same matched-control discipline this repository already applies everywhere.
    The 2502.74 s figure would then be a cross-container sanity reference only,
    never the contrast.

(a) Obtain the Debian libfplll8 `default.json` matching the predecessor's build,
    hash-pin it, and bind it by content in the successor batch. Restores
    byte-identical comparability if and only if the version can be established;
    this session could not establish it from any committed record.

(b) Amend the protocol to declare a substituted strategies source and record the
    precision/pruning confound as a named limitation. Weakest: it keeps the
    cross-container comparison while admitting it is confounded.

Route (c) needs no protocol amendment to the CONSTRUCTION (basis, seed, mpfr,
ROW_EXPO-free GSO are all reproducible byte-identically and were verified to run),
only an explicit Coordinator decision to add the reference cell.

## Status

RT-CTRL-1 IS NOT DISPATCHED. This is an INFRASTRUCTURE AND PROVENANCE finding, and
under AGENTS.md rule 3 it is NOT negative evidence about precision, about the
obstruction RT-CTRL-1 targets, or about anything else. GOAL-MLKEM-005 stays
`active`; no pause condition is declared by this note; no budget is debited,
because no executor ran; no hypothesis moves; no claim tier moves.
