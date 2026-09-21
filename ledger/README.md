# Research Ledger

Canonical machine-readable state of the research program. One YAML record
per file, schemas in `templates/research-records.md`.

```text
ledger/
  goals/        GOAL-<AREA>-NNN.yaml    Persistent Coordinator research goals
  questions/    RQ-<AREA>-NNN.yaml      Research questions (Coordinator)
  proposals/    IDEA-YYYYMMDD-NNN.yaml  Idea Generator proposals
  hypotheses/   H-<AREA>-NNN.yaml       Specified hypotheses + status
  evidence/     EV-<AREA>-NNN.yaml      Reviewed evidence records
  decisions/    DEC-YYYYMMDD-NNN.yaml   Coordinator decisions
  handoffs/     TASK-YYYYMMDD-NNN.yaml  Inter-agent task assignments
```

Rules:

- IDs are immutable; files are never renamed or reused.
- Records are append-only in spirit: corrections create new records that
  supersede old ones. The exception is a hypothesis record's `status`
  field, which only the Coordinator advances, citing a decision record.
- Experiment contracts and run artifacts live in `experiments/<EXP-ID>/`,
  not here (see `docs/evidence-and-reproducibility.md`).
- A persistent goal remains `active` across dispatch batches until a committed
  Coordinator decision reaches a declared success condition, the user stops
  it, or the Coordinator records a scoped `pause`. A negative result narrows a
  hypothesis; it does not complete the goal by itself.
