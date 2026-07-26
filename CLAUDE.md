# CLAUDE.md

Claude Code **runtime binding** for the autonomous, reproducible ECDLP
research program. The program itself is runtime-neutral: the binding
inter-agent contract is `AGENTS.md`, the role contracts are `agents/*.md`
and `orchestration/roles.yaml`, and Claude Code is one of several runtimes
that can execute them (see `docs/inference-backends.md`). Read `AGENTS.md`
before doing any research work. This file wires that contract into Claude
Code specifically.

## Harness layout

- **Subagents** (`.claude/agents/`): `coordinator`, `idea-generator`,
  `executor`, `validator`, and `red-team`. These are the operational versions
  of the role contracts in `agents/*.md`. Research work is done BY these
  subagents; the top-level session orchestrates and talks to the user.
- **Skills** (`.claude/skills/`), one per lifecycle stage:
  - `/propose-ideas` — ideation for a research question
  - `/design-experiment` — hypothesis + frozen approved protocol
  - `/run-experiment` — bounded execution, immutable run records
  - `/review-evidence` — validation, evidence strength, official decision
  - `/research-status` — read-only ledger overview
  - `/curate-knowledge` — maintain the knowledge corpus
  - `/coordinate-research-goal` — launch and continuously coordinate a committed
    research goal across dispatch batches
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
   and budget; toy-scale evidence is never presented as crypto-scale. Claim
   tiers and solution certificates are defined in
   `docs/claims-and-verification.md`: any claimed solve/relation carries a
   certificate the run wrapper re-verifies independently, and no evidence
   record asserts above its claim tier.
5. Never fabricate commands, outputs, timings, statistics, citations, or
   runs. Missing data stays missing and is reported as such.
6. Every conclusion cites the experiment/run/evidence IDs supporting it.
7. The Coordinator makes isolated snapshot and ledger commits for declared
   research artifacts. A theory, run package, review report, or ledger record
   is not official until the dispatcher's post-commit verifier accepts it.

## Conventions

- IDs: `RQ-<AREA>-NNN`, `IDEA-YYYYMMDD-NNN`, `H-<AREA>-NNN`,
  `EXP-<AREA>-NNN`, `RUN-*`, `EV-<AREA>-NNN`, `DEC-YYYYMMDD-NNN`,
  `TASK-YYYYMMDD-NNN`, `KN-{LIT,TECH,FIND,OPEN}-NNN`. Immutable, never
  reused. Find the next free number by grepping the relevant directory.
- Record schemas live in `templates/research-records.md`; copy, don't
  invent fields.
- The Coordinator alone stages declared research paths in the shared worktree:
  snapshot before review, then ledger commit before a state transition. Commit
  messages reference the task and record IDs; never rewrite history over
  pushed run records.
- Keep a working branch current by **merging** `main` into it, never by
  rebasing — a rebase rewrites every commit, including pushed run records.
  `.github/workflows/sync-main.yml` does this every six hours for open pull
  requests; a branch it reports as conflicted, or as failing post-merge
  validation, is yours to resolve before further work lands on it. Re-run the
  validators after any sync: two branches can each be valid and invalid
  together (duplicate id, cross-reference to a record that moved). A conflict
  inside an immutable record is resolved by superseding it under a new id,
  never by editing it in place. See `docs/github-automation.md`.

## Model policy note

Policies are vendor-neutral capability contracts
(`orchestration/model-policies.yaml`); the model that serves one is chosen
per backend in `orchestration/model-bindings.yaml` and resolved by
`orchestration/adapter/`. Subagent frontmatter in `.claude/agents/` cannot
express a policy, so per-role model selection under this runtime is
process-level: launch the session with the resolved environment rather
than mixing policies in one session, and keep `model: inherit` in the
frontmatter.

```sh
# resolve a role's policy and see exactly what would answer
python3 -m orchestration.adapter resolve --role coordinator
# run this runtime against a different backend entirely (e.g. GLM)
eval "$(python3 -m orchestration.adapter env \
          --runtime claude_code --backend zai-anthropic --role coordinator)"
```

That `env` output also sets `AUTORESEARCH_POLICY` and
`AUTORESEARCH_BACKEND`, which is how `harness/runner.py` records the exact
resolved model in each run manifest's `inference` block. Record
`requested_policy` from the handoff alongside it, with `fallback_used:
true` and a reason if they differ — never silently substitute. Do not edit
`.claude/agents/*.md` tool lists directly: authority and tool surface come
from `orchestration/roles.yaml`, and `tools/check_runtime_bindings.py`
fails the build if the two disagree.

## Typical loop

```text
/research-status
  → /propose-ideas RQ-...
  → /design-experiment IDEA-...
  → /run-experiment EXP-...
  → (Coordinator snapshot commit + independent validation/red team)
  → /review-evidence EXP-...
  → (knowledge-promotion gate: proven results → /curate-knowledge KN-FIND;
     every decision fills knowledge_promotion or says why not)
  → (Coordinator ledger commit + verified decision)
  → (decision drives next iteration)
```
