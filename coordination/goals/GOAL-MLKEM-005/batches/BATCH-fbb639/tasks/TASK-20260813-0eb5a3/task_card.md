# TASK-20260813-0eb5a3 — Author PREREG-3

    goal / batch    GOAL-MLKEM-005 / BATCH-fbb639
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           completed
    depends_on      (none)
    review_required false
    archived_by     TASK-20260813-6ad846
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## What it had to do, in this order

**(a) DISCHARGE RC-1** — supersede `BATCH-6b6e78`'s headline count of 1,416
`VAR-F`-verdict-changing cells with the **1,313 reading**, matching `PREREG-2`
2.6's own **declared** binary32 `route_provenance`. Adopted (not left as a
choice for the lead) because it requires no new declaration and is the more
conservative correction; the reasoning is stated in full in `PREREG-3` §1.

**(b) DISCHARGE RC-2** — supersede the false "`P-A12a` mis-scored `HELD` ...
left unedited" narrative with the true, already-verified fact: the committed
`results_a1.json` `OUTCOME` was, and always was, `FALSIFIED`. The immutable
commit `4e466c6bf` and its message are untouched; the correction lives in
`PREREG-3` §2 and must be carried into a new committed ledger record by this
batch's ledger archive.

**(c) FREEZE THE LEAD MEASUREMENT** — at `d <= 40` (`L7`/`L9`/`L11`, no
reduction of any kind anywhere in this batch), whether `lam1n`, `hkz`,
`rawtail` have their own `binary64` fibre dispersion exceeding their
**two-route disagreement**, using ONLY already-committed corpus artifacts. A
coverage audit (obligation 0) runs first because this Coordinator's own
pre-dispatch read found a genuine independent second route ("`ROUTE-I`")
committed for `lam1n`/`hkz` at `L7` only (`BATCH-4ed139`'s P-L1 rider,
`TASK-20260812-0e930c`), an **unverified candidate** for `L9`/`L11`
(`BATCH-cbe023`'s `results_am4.json`, comparability unchecked), and **nothing**
equivalent for `rawtail` beyond a labelled, non-equivalent, never-counted
proxy residual. A four-branch termination clause (`T-C3LANE-NODATA` /
`-OBSTRUCTED` / `-OPEN`, each with a mandatory `-PARTIAL` suffix rule) is
frozen before any cell is read, with explicit precedence and an explicit
statement of why `PREREG-2` 7.5's repair bar does not apply (§3.6).

## Executed 2026-08-13 by the session that opened this batch, WITH NO SHELL

It wrote `prereg.md` and stopped. No git command, no probe, no `allocate_id`,
no hash. `prereg_sha256.txt` therefore belongs to `TASK-20260813-6ad846`
(declared gap `G-2`). It **did** use read-only file access (never a shell) to
inspect the committed corpus for `ROUTE-I` candidates, and every number cited
from that reading is attributed as this session's own observation, weaker than
a measurement, with its exact source path given so the lead can check it
independently.

## Artifacts — ONE PATH

    tasks/TASK-20260813-0eb5a3/prereg.md

## The single thing not to get wrong — AND IT IS STILL LIVE

**`prereg.md` MUST NOT RIDE IN THE BATCH-OPENING COMMIT.** It exists in the
working tree from the moment this batch was opened. Its **first appearance in
the history must be the notarizing commit** `TASK-20260813-6ad846`. Stage
paths explicitly; never `git add -A` in this batch.

## The other open gap this task did not and could not close

**G-5: the ledger archive's `TASK-` identifier is not yet minted.** This
Coordinator was given six identifiers and two reserved ledger identifiers
(`EV-MLKEM-965a37`, `DEC-20260813-28d7b2`) but explicitly not a seventh
`TASK-` id, and was instructed to ask rather than invent one. The ledger
archive's full shape is specified under `pending_ledger_archive_task` in
`dispatch_queue.json`, outside the `tasks` array, so nothing is dispatched
under an invented id.
