# CLAUDE.md

Read [AGENTS.md](AGENTS.md), the only normative contract for every runtime,
including Claude Code. The earlier long form and typical loop remain in
[docs/claude-code-runtime.md](docs/claude-code-runtime.md).

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
