# Independent replication of BATCH-d2a728 review, 2026-08-13

**These are not archived reviews and are not evidence.** They carry no receipt,
no `path_sha256` binding, and no ledger record, and they change no status.

`GOAL-MLKEM-004` closed as `closed_at_budget` on 2026-08-05 under
`DEC-20260805-0b3e11`. `BATCH-d2a728` was reviewed and ledger-archived long
before that under `TASK-20260803-586a7f`. The reviews in this directory were
produced on 2026-08-13 by a session resuming from a stale snapshot that still
showed the batch as pending; the full account is `KN-FIND-3546c2`.

The artifacts live here, rather than in
`batches/BATCH-d2a728/tasks/TASK-20260803-{535d15,bc2f41}/`, because those paths
hold immutable files bound by hash to the ledger archive. Writing to them would
break that archive permanently (AGENTS.md rule 15).

They are retained for one reason: the red team had no access to the archived
reviews and independently reproduced the campaign's central negative result by a
different route — a norm-matched sign-and-coordinate permutation null returning a
402x variance design effect against 404x for the real sieve `X`, versus the
campaign's ablated-Y-only arm holding `X` exactly fixed. Same conclusion, no
contact, different null.

| File | Origin | Status |
| --- | --- | --- |
| `red_team_report.yaml` | `TASK-20260803-bc2f41` re-run | complete; verdict `blocking_objections` |
| `red_team_notes.md` | `TASK-20260803-bc2f41` re-run | complete |
| `validator_notes_partial.md` | `TASK-20260803-535d15` re-run | partial |
| `validator_scripts/*.py` | `TASK-20260803-535d15` re-run | recomputation scripts |

The red team's `blocking_objections` verdict and its eight objections are
addressed to a batch-2 design that was superseded by events; read them as
methodological commentary, not as a live gate. Its model provenance records
`fallback_used: true` with `degraded_requirements: []` and
`model_verified: false`.
