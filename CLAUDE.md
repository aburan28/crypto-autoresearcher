# CLAUDE.md

Claude Code harness for autonomous, reproducible ECDLP research. The
binding inter-agent contract is `AGENTS.md` — read it before doing any
research work. This file wires that contract into Claude Code.

## Harness layout

- **Subagents** (`.claude/agents/`): `coordinator`, `idea-generator`,
  `executor`. These are the operational versions of the role contracts in
  `agents/*.md`. Research work is done BY these subagents; the top-level
  session orchestrates and talks to the user.
- **Skills** (`.claude/skills/`), one per lifecycle stage:
  - `/propose-ideas` — ideation for a research question
  - `/design-experiment` — hypothesis + frozen approved protocol
  - `/run-experiment` — bounded execution, immutable run records
  - `/review-evidence` — validation, evidence strength, official decision
  - `/research-status` — read-only ledger overview
  - `/curate-knowledge` — maintain the knowledge corpus
- **State**:
  - `ledger/` — canonical YAML records (questions, proposals, hypotheses,
    evidence, decisions, handoffs)
  - `experiments/` — frozen contracts and immutable run artifacts
  - `knowledge/` — curated long-term corpus (literature, techniques,
    internal findings, open problems)

## Non-negotiable rules (summary of AGENTS.md)

1. Only the coordinator changes hypothesis status or approves experiments.
2. Run records, ledger records, and knowledge entries are immutable —
   corrections supersede, never overwrite.
3. Timeouts/crashes/infra failures are never negative mathematical
   evidence.
4. Every conclusion is scoped to the tested curves, parameters, solver,
   and budget; toy-scale evidence is never presented as crypto-scale.
5. Never fabricate commands, outputs, timings, statistics, citations, or
   runs. Missing data stays missing and is reported as such.
6. Every conclusion cites the experiment/run/evidence IDs supporting it.

## Conventions

- IDs: `RQ-<AREA>-NNN`, `IDEA-YYYYMMDD-NNN`, `H-<AREA>-NNN`,
  `EXP-<AREA>-NNN`, `RUN-*`, `EV-<AREA>-NNN`, `DEC-YYYYMMDD-NNN`,
  `TASK-YYYYMMDD-NNN`, `KN-{LIT,TECH,FIND,OPEN}-NNN`. Immutable, never
  reused. Find the next free number by grepping the relevant directory.
- Record schemas live in `templates/research-records.md`; copy, don't
  invent fields.
- Commit ledger/experiment changes with messages referencing the record
  IDs they touch. Never rewrite history over pushed run records.

## Typical loop

```text
/research-status
  → /propose-ideas RQ-...
  → /design-experiment IDEA-...
  → /run-experiment EXP-...
  → /review-evidence EXP-...
  → (decision drives next iteration)
```
