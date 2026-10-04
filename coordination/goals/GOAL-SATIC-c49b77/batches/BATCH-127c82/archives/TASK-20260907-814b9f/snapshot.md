# Opening snapshot — TASK-20260907-814b9f

Self-neutral content binding for BATCH-127c82's opening authority: the frozen
known-bad-control contract, the dispatch queue, the seven task handoffs, and the
approval decision DEC-20260907-ca563a. This receipt binds a PROTOCOL, not a
result. No trial has run, no mutation has been planted, no instrument has been
invoked, no verdict exists, and no attestation has been obtained. Any later
record citing this snapshot as evidence of a sensitivity outcome is misciting it.

**What the lane executes.** DEC-20260905-6e8621 ranked one next action first:
execute BATCH-2cca27's frozen KNOWN-BAD CONTROL alone. That control has never
been run by any session — DEC-20260905-29416d records it explicitly unperformed
for the TASK-20260905-5681fc refusal, and DEC-20260905-6e8621 records under
`unperformed_checks` that BATCH-008925's delivered control is a *different*
control with an opposite purpose. BATCH-008925's `proves_too_much` control is a
SPECIFICITY check on a known-good set (1 flag of 17, uncorrelated with batch
outcome — a real result, neither restated nor revised here). BATCH-2cca27's
checks[5] is a SENSITIVITY check on a planted defect. Neither substitutes for
the other, and AGENTS.md's own proves-too-much obligation is the known-false
form, which matches BATCH-2cca27's clause and not BATCH-008925's.

**Scope, asserted here and not to be widened later.** This lane measures the
sensitivity of an archive-receipt verification procedure and nothing else. It
asserts NOTHING scientific about SATIC, summation polynomials, Semaev
polynomials, SAT encodings, solvers, or the ECDLP. Neither of
GOAL-SATIC-c49b77's completion criteria is met and this lane moves neither.
DEC-20260905-6e8621's impediment disposition stands exactly as given: nested
IMP-1 cleared, top-level IMP-1 partially cleared, IMP-3 standing, IMP-2 out of
scope. This lane addresses only the FIRST of IMP-3's two separable recheck
conditions and cannot clear IMP-3 even on a clean result.

**The mutation never enters the repository.** The corrupted copy lives under
`/tmp/satic-kbc-BATCH-127c82/`, verified outside the checkout by git itself
(`git check-ignore -v /tmp` → `fatal: /tmp: '/tmp' is outside repository at
'/workspace'`). TASK-20260907-39511d's declared `write_scope` contains only
paths beneath its own task directory: no receipt, no queue, no archive and no
ledger path appears in it.

**Base checked before this commit.** `origin/main` was fetched and merged into
`cursor/satic-c49b77-imp1-recheck-276e` before these artifacts were generated:
merge-base `e6059f4de563be3cb1f1b25383782ab9a708352f`, `origin/main` at
`0100b949e67373234f1f4a7f2b13dffa7cfb7e51`, merged cleanly (no conflict, no
record touched) to `4ed696969cedbf45f2b594d1fc62bf77e12f3090`. Merge, never
rebase. This receipt's own path is self-neutral (null hash and size before
commit); its digest and this commit's sha are bound in the queue's archive block
by the immediately following backfill commit, which stages only
`dispatch_queue.json` — the established pattern on this branch, where
`4feb619f1` backfilled `70cf21653`.

**Not in the declared set, and why.** `coordination/goals/GOAL-SATIC-c49b77/lanes/BATCH-127c82.lane.json`
was committed separately at `2fbcb237e` by `tools/goal_lanes.py open-lane`. Lane
registration is a write-once coordination side file that deliberately lives
outside the dispatch queue (`docs/concurrent-goal-lanes.md`), so it is not a
declared research artifact of any task and is not staged here.
`dispatch_plan.json` and `dispatch_plan.md` are gitignored generated artifacts
and are never staged.

**Queue structure.** Four non-archive tasks, each assigned to exactly one
archive: `9ceaba → 814b9f`, `39511d → e7cc96`, `6fbd6d → 9b71ea`,
`c3d2d8 → 9b71ea`. `TASK-20260907-c3d2d8` is planned into the OPENING queue as
an unconditionally-running non-archive node so the terminal ledger archive
always has a source it can consume — `CORR-20260907-5afd89` records a queue that
could not represent a closing archival node its opening plan had not
anticipated, and on this goal that failure is not hypothetical (the BATCH-2cca27
review refused before check 1, and the top-level IMP-1 records
`review-adversarial` at `xhigh` as unservable through the adapter).
`DEC-20260907-6c6137` is minted, checked free, declared in `9b71ea`'s
`artifact_paths` and `record_ids`, and NOT YET AUTHORED — disclosed as reserved
rather than presented as existing.

Binding (sha256 of the working-tree bytes at staging time):

```json
{
  "receipt_kind": "opening_snapshot_binding",
  "task_id": "TASK-20260907-814b9f",
  "source_task_ids": ["TASK-20260907-9ceaba"],
  "goal_id": "GOAL-SATIC-c49b77",
  "batch_id": "BATCH-127c82",
  "record_ids": [
    "GOAL-SATIC-c49b77",
    "BATCH-127c82",
    "DEC-20260907-ca563a",
    "TASK-20260907-9ceaba",
    "TASK-20260907-814b9f",
    "TASK-20260907-39511d",
    "TASK-20260907-e7cc96",
    "TASK-20260907-6fbd6d",
    "TASK-20260907-c3d2d8",
    "TASK-20260907-9b71ea"
  ],
  "expected_parent": "2fbcb237e32fab63a614554c8845ece7e7a02b28",
  "path_sha256": {
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/contracts/known-bad-control.json": "2d3a790249cff5e737757e25c64c08c7dcee4712057daaed43ff8b1b1a78245b",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/dispatch_queue.json": "4a34bdfb956de340b81b1987a5d03eb8946a0b54f03d83b3d28622157449f0ac",
    "ledger/decisions/DEC-20260907-ca563a.yaml": "e1417ada5b66137a9254a02f188194a68f0e0711af1bb55371f9cdad6b8aae48",
    "ledger/handoffs/TASK-20260907-9ceaba.yaml": "db18d61db5109dc550aaccc6777bd0272ada3096d3bdc897b827fac84bcd3c0b",
    "ledger/handoffs/TASK-20260907-814b9f.yaml": "6559f931522b8733b0039a7b800be421a0a64e6334f039492a4fa5967460b010",
    "ledger/handoffs/TASK-20260907-39511d.yaml": "2e8309aa95cec42ed4f3a3c46bc4162340db151588cfa99aa02d42ea62740fd4",
    "ledger/handoffs/TASK-20260907-e7cc96.yaml": "e797c0e1ec5999fcccc7613351542f4b5bcb10e8edb5e620e680d6911ea1acbd",
    "ledger/handoffs/TASK-20260907-6fbd6d.yaml": "a331adf8fbe0b0771686918d9d1b1f141c63c35125747312cb3255906326f179",
    "ledger/handoffs/TASK-20260907-c3d2d8.yaml": "7aac4fe845cd471911e964eb8102126d1c483bf519b5bad8a3c2632de15ea2d3",
    "ledger/handoffs/TASK-20260907-9b71ea.yaml": "edc9797f90217280385c3f2ae2d5d4bd6f13c755a35b13556d244bc158e4c268"
  },
  "self_path": "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/archives/TASK-20260907-814b9f/snapshot.md",
  "self_sha256": null,
  "self_size": null
}
```

**Inference provenance.** Requested policy `coordinator-orchestration-code`;
configured binding `coordinator-orchestration-code -> anthropic:claude-opus-5
(effort=high)`, resolved by this session; runtime a Cursor Cloud Agent
claude_code-family session self-reporting Claude Opus 5; `fallback_used` false;
`degraded_requirements` empty; `bedrock_used` false. **`model_verified` is
false** — this session did not run `doctor --probe`, and the most recent probe on
record (DEC-20260905-6e8621, 2026-09-07) found every API backend
uncredentialed. A configured binding is not verification and is not treated as
one here.
