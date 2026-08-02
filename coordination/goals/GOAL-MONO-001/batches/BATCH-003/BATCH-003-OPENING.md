# GOAL-MONO-001 · BATCH-003 — opening

**Opened** 2026-08-02 · **Authorized by** `DEC-20260802-505759` (`GOAL-PATH-001`
prioritization) · **Budget** batch 3 of 3, 21600 s campaign wall clock ·
**Claim-tier ceiling** toy

## Why this batch exists

The user asked to launch the harness on *index calculus for ECDLP*. Every goal in
that chain was self-deferred, and three of the four deferred to `GOAL-PATH-001`'s
unresolved three-way prioritization choice. `DEC-20260802-505759` makes that
choice and selects this goal, because **`GOAL-MONO-001` is the only child whose
sole recorded blocker was that decision** — `GOAL-SDEG-001` additionally needs the
`GOAL-ECDLP-001` verifier-hash residuals to clear, and `GOAL-RELN-001` additionally
needs activation residuals to clear. Neither is reachable from here.

The protocol this batch executes was already frozen and already carried an
independent red-team PASS (`RT-20260725-707`, `EV-MONO-002`). Nothing about the
specification is new work; only its execution is.

## Task set

| Task | Role | Purpose |
|---|---|---|
| `TASK-20260802-815548` | executor | Run `MONO-m3-census-1.1.0-repair-cm-gate` as `EXP-MONO-4b50b6` |
| `TASK-20260802-d49dee` | coordinator | Snapshot-archive the run package before any reviewer reads it |
| `TASK-20260802-e2702a` | validator | Independent verification of controls, determinism and derivation |
| `TASK-20260802-1b4130` | red-team | Attack the readings: overreach, hidden scope, premature closure |
| `TASK-20260802-32e4bf` | coordinator | Ledger archive: evidence, decision, correction, knowledge, goal updates |

Rendered plan: `dispatch_plan.md` / `dispatch_plan.json`, all ten dispatch gates
passing.

## Archive shape, and the BATCH-001 defect it avoids

`BATCH-001` of `GOAL-HAWK-001` committed a receipt *separately* from the artifacts
it bound, a shape `tools/research_dispatch.py` rejects
(`CORR-20260802-008`; the same family as `CORR-20260729-003`). This batch uses the
shape the tool requires and that `TASK-20260725-706` used correctly:

> the receipt rides **inside its own archive commit** with `commit_sha: null`
> written in the receipt body, and the resulting sha is recorded in the queue's
> `archive.commit_sha` afterwards.

`CORR-20260802-bc9e33` OI-3 recorded that a conforming queue was owed before any
batch that dispatches workers. **This is that queue.**

## Ordering, stated plainly

The authorization decision `DEC-20260802-505759` and this opening are committed
first; the run package is snapshot-archived second; independent review reads only
the snapshot; evidence and decision records are written last. The census was
executed by this same session under that authorization — the independence in this
batch is at the **review** step, not at the production step, and no record here
claims otherwise.

## Provenance repair riding in this batch

`GOAL-PATH-001.latest_verified_commit` was
`9f80eebbef2df9a521a9cce8da66391cfcb63e73`, which **does not resolve in this
repository**. A driver resuming the index-calculus chain could not verify the
checkpoint it was building on. `CORR-20260802-7787de` measures the damage and
rebinds the field to this batch's snapshot commit. This is `CORR-20260802-a1f151`
OI-1 being discharged for one of its three named goals; `GOAL-FIND-001` and
`GOAL-MLKEM-001` remain for their own Coordinators.

## What this batch may not do

- No crypto-scale reading. Largest prime in the frozen protocol is 1601.
- No `FULL_MONODROMY_BARRIER_TOY` without the CM hard gate `CTRL-CM-GATE-FULL`.
- No hypothesis status change; `active_hypothesis_ids` stays empty on both goals.
- No statement about `m ≥ 4`; `KN-OPEN-009` is not closed there by anything here.
- Nothing admissible toward the AGENTS.md rule 13 closure quorum.
