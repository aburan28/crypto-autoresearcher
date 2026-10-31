# CLAUDE.md

Read [AGENTS.md](AGENTS.md), the only normative contract for every runtime,
including Claude Code. The earlier long form and typical loop remain in
[docs/claude-code-runtime.md](docs/claude-code-runtime.md).

The AGENTS.md rules “ECC comes first” and “Goals are never paused” also bind
Claude Code; their full requirements and limits are stated there.

## Claude Code specifics

- Batch delivery follows AGENTS.md, "Model policy".
- `.claude/agents/` contains hand-written wrappers around `agents/*.md`.
  `orchestration/roles.yaml` and `orchestration/model-policies.yaml` define
  roles, model pins, and effort. `tools/generate_runtime_agents.py` generates
  Codex and OpenCode bindings; `tools/check_runtime_bindings.py` checks Claude
  wrappers. Keep `model: inherit` except declared `runtime_model_pins` roles.
  Never hand-edit model or effort; use `tools/check_runtime_bindings.py --list`
  for provenance. The session defaults to `claude-opus-5-5`; `--model` or
  `adapter env --runtime claude_code --role <role>` overrides it.
- Use `.claude/skills/`: only `run` executes trials; `coordinate` governs and
  never runs them. Follow AGENTS.md, "Skill routing", for other skills. Each
  skill writes a session receipt.
- `.mcp.json` starts the read-only `kb/` server. See the runtime guide for
  index setup and retrieval commands.

**Resume checkpoints** (owner, 2026-10-24): before any experiment run, fill
`.resume/RESUME.md` (`scripts/checkpoint.sh init`) so a fresh session could
resume the effort from it alone. The hooks push it to S3 with the specs,
leads and unpushed work, and refuse run launchers until that succeeds.
AGENTS.md, "Resume checkpoints in S3 before every run".

Look up curve facts and existing measurements in the lab's curve database
before computing them: MCP server `ecdb` (export `ECDB_TOKEN` from secret
`ecdb/api` first) or `scripts/ecdb.sh`. AGENTS.md, "Querying the curve
database (ecdb)".
