# NOT FILED. Superseded before entering the ledger by DEC-20260812-7c4a1e.

`DEC-20260812-2233ed` and `EV-MLKEM-c7a814` in this directory are **drafts that were
never committed to the ledger and never will be.** The identifiers were minted and
`--check`ed, are recorded here as spent, and must never be reused or filed.

## Why

While TASK-20260812-2a3aa0 was running, another session committed
`DEC-20260812-7c4a1e` (decision `synthesize`, task `TASK-20260812-2b40d2`, commit
`85f0f6e1e`), which performs the same reconciliation DEC-20260812-15d3b2 ordered. It
cites both evidence records, both decisions, all four review reports and the probes,
promotes `KN-FIND-4b8d73`, adds AM-17, and the goal record's `next_action` already
records the reconciliation as discharged.

Filing a second reconciliation would have created a two-chain collision **one level
above the collision the reconciliation exists to resolve** — two competing syntheses of
two competing review waves. That is the failure mode compounding, not a second opinion.

## What this is instead

An **independently produced second reading, not a competing record.** It reached its
conclusions without sight of `DEC-20260812-7c4a1e`, which makes convergence between them
worth noting and divergence worth checking. Two points where that matters:

1. **The C-1 numeric contradiction.** This reading found that wave 1 reports 15 of 19
   G-REL2 cells below 6x while wave 2 reports 2 of 29 entries, from the same committed
   file; endpoints agree, the count does not; it recomputed neither and recorded the
   count as **non-citable from either wave pending a re-read**. The committed decision's
   next_action independently schedules exactly that resolving test as rider (i). Two
   readings arriving separately at the same unresolved contradiction is the useful part.
2. **AM-16(d) is insufficient.** Every route in `probe_nullroute.py` lives in F0 — the
   family in which a dispersion criterion has the most power against a determinant-only
   functional — so a criterion validated only there is scored where its own
   family-blindness cannot appear. That is this program's characteristic error, and this
   is the seventh instance of it. Whether the committed decision's AM-17 already covers
   this is for a successor to check; this reading does not assert that it does not.

## Status

Not evidence. Not a decision. No claim tier, because no claim is made. The committed
reconciliation is `DEC-20260812-7c4a1e` and nothing here modifies, corrects, or contests
it — this file exists so a later reader knows these drafts were deliberately not filed
rather than lost.
