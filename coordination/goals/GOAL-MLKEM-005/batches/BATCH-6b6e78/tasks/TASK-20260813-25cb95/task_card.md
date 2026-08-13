# TASK-20260813-25cb95 — Author PREREG-2

    goal / batch    GOAL-MLKEM-005 / BATCH-6b6e78
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           completed
    depends_on      (none)
    review_required false
    archived_by     TASK-20260813-502381
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## What it had to do, in this order

**(a) STATE THE NUMBERED ASSUMPTION FIRST, TEXTUALLY, WITH AN EXPLICIT
FALSIFICATION CONDITION** — what "non-constant on the fibre" means at finite
precision — **before any replacement criterion appears anywhere in the document**
(`AM-18(a)`). The assumption in force until now, *non-constant on the fibre in
IEEE-754 float64 ≡ non-constant on the fibre*, is measured **false** at 38 of 38
cells for `rdet` under three of six routes and has never been numbered.

Then, and only then: the per-candidate fibre construction and its guard
(`AM-18(c)`), the two-precision axis and the exact routes (`AM-18(b)`), the
null-object calibration at declared amplitudes (`AM-18(e)`), the **four-way
termination clause** with the branch where the assumption cannot be stated in a
form its own falsifier could reach, the **published reachability** of the
must-pass guard's VOID row **and of that branch itself** (`AM-18(d)`), and the
**repair bar** `PREREG-1` 7.3's FORBIDS list lacked (Red Team `O-3`).

## Executed 2026-08-13 by the session that opened this batch, WITH NO SHELL

It wrote `prereg.md` and stopped. No git command, no probe, no `allocate_id`, no
hash. `prereg_sha256.txt` therefore belongs to `TASK-20260813-502381` (declared
gap `G-2`). Every number in PREREG-2 is attributed to the record that measured
it, in its §12.

## What PREREG-2 contains that no prior record of this goal contains

1. **`A-1` is numbered and its falsifier is mostly constant-free.** Four of the
   five falsifiers (`FC-1`, `FC-2a`, `FC-2b`, `FC-3b`) are existence, direction
   or order tests carrying **no numeric constant at all**; the one that does
   (`FC-3a`'s window `[1/2, 2]`) declares its basis and its honest consequence in
   the same section (§1.4).
2. **The `precision_degenerate` hole is frozen with both readings named** (§1.3).
   At a cell where `rho(binary64) == 0` exactly — definitional for route `R0` —
   the strict reading would falsify `A-1` *by the definition of `R0`*. The frozen
   reading exempts those cells; the strict reading must be printed beside it at
   every one (`R3-OUT-7`). That is the could-not-HOLD arrangement, named in
   advance (§6.3).
3. **An exact route for `X_gso_k` is DERIVED** (§2.9):
   `X_gso_k = (1/(2k)) log det(I_k + A A^T)`, an exact **integer** determinant.
   It is what makes `A-1.1` decidable for the one candidate on the list that
   reads the instance, it is the Coordinator's own derivation, and it is subject
   to `P-GRAM`: if it disagrees with the committed `RQ`/`RG` values, the route is
   reported **UNAVAILABLE**, `FC-1` fires, and that is a **finding** rather than
   something to patch.
4. **§7.5, the repair bar.** Six conditions each demonstrable from committed
   artifacts, plus an absolute bar on an **eighth** consecutive gate repair
   without a committed decision recording why the `C3` lane cannot be entered
   instead — and, in the same section, an explicit statement that the bar is
   **not** a licence to close the lane, close the goal, or declare the problem
   saturated.

## Artifacts — ONE PATH

    tasks/TASK-20260813-25cb95/prereg.md

## The single thing not to get wrong — AND IT IS STILL LIVE

**`prereg.md` MUST NOT RIDE IN THE BATCH-OPENING COMMIT.** It exists in the
working tree from the moment this batch was opened, because the opening session
authored it. Its **first appearance in the history must be the notarizing commit**
`TASK-20260813-502381`. Stage paths explicitly; never `git add -A` in this batch.
