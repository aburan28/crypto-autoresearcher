# SUPERSEDED — this placeholder is discharged

**This directory name was never an identifier.** It was a deliberately
non-conforming placeholder (not of the form `TASK-YYYYMMDD-<tok>`) held while
declared gaps **G-1** and **G-2** were open, so that no reader or tool could
mistake it for a minted id.

**Both gaps are closed.** The dispatching session minted two identifiers on
2026-08-12 and **two-scope confirmed** each — worktree `--check` (well-formed and
free) **plus** a bounded sweep of the 25 most-recently-updated origin branches
(0 hits). Recorded as two-scope confirmed and **not** as `--check` alone, because
`--check` answers from the working tree only.

    G-1  ->  TASK-20260812-655fe9   the LEDGER archive
             card: ../TASK-20260812-655fe9/task_card.md
    G-2  ->  TASK-20260812-b53c2f   the RIDER SNAPSHOT (the better shape, taken)
             card: ../TASK-20260812-b53c2f/task_card.md

`dispatch_queue.json` now carries eleven tasks, no `PENDING-LEDGER-ARCHIVE-ID`
placeholder remains anywhere in it, and the `declared_gaps` entries for G-1 and
G-2 are retained with their resolutions rather than deleted.

**This directory carries no research content and may be deleted before the
opening commit.** It is a coordination placeholder, not a record, so removing it
destroys nothing; it is left here only so that a reader who followed a link to
the old path is not stranded. If it is kept, it must be included in the opening
commit alongside `dispatch_queue.json` and the eleven task cards — never in an
archive commit, whose change set must equal its declared set exactly.
