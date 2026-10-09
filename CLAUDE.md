# CLAUDE.md

Read **[AGENTS.md](AGENTS.md)**. It is the one normative contract for every
runtime, Claude Code included: budgets are advisory, `run` is the only
execution skill, only the Coordinator changes research state, records are
immutable, "ECC comes first", "Goals are never paused", "Approval is bounded
by execution", and `main` takes merge commits only. One file rather than two,
because two copies of a rule become two different rules; the earlier long
form of this file is kept, unchanged, at
[`docs/claude-code-runtime.md`](docs/claude-code-runtime.md).

## What is Claude Code specific

- **Subagents** live in `.claude/agents/` and are generated from
  `agents/*.md` by `tools/generate_runtime_agents.py`: seven roles (the
  newest, `idea-synthesist`, is Claude Code only) plus three policy-tier
  variants (`executor-mechanical`, `validator-breakthrough`,
  `red-team-breakthrough`). Subagents keep `model: inherit` except the roles
  in `runtime_model_pins` (`orchestration/roles.yaml`), which name their
  policy's `anthropic` binding; never hand-edit either. The session default
  is `claude-opus-5-5` (`.claude/settings.json`); `--model` and
  `adapter env --runtime claude_code --role <role>` override it. Each file's
  `effort:` is derived from its role's policy (`orchestration/roles.yaml` →
  `orchestration/model-policies.yaml`), never edited by hand; `tools/check_runtime_bindings.py` fails the build on
  drift and `--list` shows where each role's effort comes from.
- **Skills** are in `.claude/skills/`: `run` (execution only), `coordinate`
  (rank, approve, dispatch, archive, publish; never runs trials),
  `propose-ideas`, `design-experiment`, `review-evidence`,
  `research-status`, `deep-research`, `curate-knowledge`, `agent-bus`,
  `consolidate-lanes`, `tune-skill`, `research-visuals`. Every skill ends by
  writing a session receipt (`docs/session-receipts.md`).
- **Retrieval**: `.mcp.json` starts the read-only `kb/` server with a
  relative `--directory`; machine settings go in `kb/.env`. The index is
  derived and starts empty (`make -C kb qdrant-up`, `crypto-kb stage-repo .`,
  `crypto-kb ingest`).
- **Batch delivery**: `python3 -m orchestration.adapter batch …` for
  single-turn prompts; records are write-once under
  `coordination/inference-batches/` (`docs/batch-inference.md`).

## Typical loop

```text
/research-status                       # read the census, not the corpus
/coordinate                            # rank, approve (capacity + runnable), dispatch, archive
  → /propose-ideas RQ-...
  → /design-experiment IDEA-...        # runnable in this turn or review_required
  → /run EXP-...                       # execution; publishes run records, then reports
  → snapshot commit, independent validation / red team
  → /review-evidence EXP-...           # knowledge-promotion gate; decision report
  → ledger commit, verified decision → next iteration
```
