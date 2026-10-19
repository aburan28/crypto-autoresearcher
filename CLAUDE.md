# CLAUDE.md

Read **[AGENTS.md](AGENTS.md)**, the one normative contract for every runtime,
Claude Code included: budgets are advisory, `run` is the only execution skill,
only the Coordinator changes research state, records are immutable,
"ECC comes first", "Goals are never paused",
"Approval is bounded by execution", "Stop at the PR", "Every improvement is
a success", and `main` takes merge
commits only. One file, because two copies of a rule become two rules; the
earlier long form of this file stays unchanged at
[`docs/claude-code-runtime.md`](docs/claude-code-runtime.md).

## What is Claude Code specific

- **Batch delivery**: `python3 -m orchestration.adapter batch …` for
  single-turn prompts; records are write-once under
  `coordination/inference-batches/` (`docs/batch-inference.md`).
- **Subagents** (`.claude/agents/`) are generated from `agents/*.md` by
  `tools/generate_runtime_agents.py`: eight roles (`idea-synthesist` is Claude
  Code only; `experiment-director` writes Haiku's task cards,
  `docs/model-tiers.md`) plus the policy-tier variants `executor-mechanical` (Haiku;
  runbooks), `validator-sweep` (Sonnet; `audit-runs`), `validator-breakthrough`
  and `red-team-breakthrough`. They keep
  `model: inherit` except the `runtime_model_pins` roles
  (`orchestration/roles.yaml`), pinned to their policy's `anthropic` binding;
  each `effort:` derives from the role's policy (`orchestration/roles.yaml` →
  `orchestration/model-policies.yaml`). Never hand-edit a model or an effort;
  `tools/check_runtime_bindings.py --list` shows where each comes from.
  Session default `claude-opus-5-5` (`.claude/settings.json`); `--model` or
  `adapter env --runtime claude_code --role <role>` overrides it.
- **Skills** (`.claude/skills/`): `run` (execution only), `coordinate` (rank,
  approve, dispatch, archive, publish; never runs trials), `propose-ideas`,
  `design-experiment`, `review-evidence`, `research-status`, `deep-research`,
  `curate-knowledge`, `agent-bus`, `consolidate-lanes`, `tune-skill`,
  `research-visuals`, `audit-curve`, `transfer`, `audit-runs` (periodic
  runbook-session audit). Each ends by writing its session receipt.
- **Retrieval**: `.mcp.json` starts the read-only `kb/` server (relative
  `--directory`; machine settings in `kb/.env`). The derived index starts
  empty: `make -C kb qdrant-up`, `crypto-kb stage-repo .`, `crypto-kb ingest`.

## Typical loop

```text
/research-status                # read the census, not the corpus
/coordinate                     # rank, approve (capacity + runnable), dispatch, archive
  → /propose-ideas RQ-...
  → /design-experiment IDEA-... # runnable in this turn or review_required
  → /run EXP-...                # execution; publishes run records, then reports
  → snapshot commit, independent validation / red team
  → /review-evidence EXP-...    # knowledge-promotion gate; decision report
  → ledger commit, verified decision → next iteration
```
