# Crypto Autoresearcher Harness plugin

This package exposes one portable, evidence-gated front door for the
repository's ECDLP research harness. It does **not** package a new scheduler,
copy the role instructions, or alter the research ledger. The checkout remains
the authority for roles, model-policy resolution, dispatch, reviews, archival,
and state transitions.

## Host adapters

| Host | Adapter | How it is discovered |
| --- | --- | --- |
| Codex | `.codex-plugin/plugin.json` plus `skills/` | Install from the repository's Codex marketplace. |
| Claude Code | `.claude-plugin/plugin.json` plus the same `skills/` | Install from the repository's Claude marketplace. |
| OpenCode | `.agents/skills/crypto-autoresearcher-harness/` | OpenCode discovers the project-local agent-compatible skill automatically. |

The OpenCode integration is intentionally an Agent Skill rather than an
in-process V2 plugin. The harness needs shared operating instructions, not
event hooks, and OpenCode's V2 plugin API is explicitly beta. Its generated
`.opencode/agent/` bindings stay authoritative for role permissions.

## Install and use

Clone the repository, install its normal Python dependencies, and start in the
checkout. The plugin makes no credential, backend, or marketplace changes by
itself.

### Codex

```sh
codex plugin marketplace add /absolute/path/to/crypto-autoresearcher
codex plugin add crypto-autoresearcher-harness@crypto-autoresearcher
```

Start a new Codex task in the checkout and ask, for example: “show the current
Crypto Autoresearcher research status” or “resume GOAL-ECDLP-001.”

### Claude Code

```sh
claude plugin marketplace add /absolute/path/to/crypto-autoresearcher
claude plugin install crypto-autoresearcher-harness@crypto-autoresearcher
```

Restart Claude Code in the checkout, then make the same natural-language
request. The plugin's shared skill routes the task to the checked-in Claude
role bindings.

### OpenCode

No npm package is needed. Start OpenCode in the repository checkout; it finds
the project-local `.agents/skills/crypto-autoresearcher-harness/` adapter and
then loads the canonical shared skill from this package. The existing
`opencode.json` and generated `.opencode/agent/` files continue to control
models and permissions.

## Safety model

Every invocation begins with:

```sh
python3 plugins/crypto-autoresearcher-harness/scripts/preflight.py \
  --repo . --runtime <claude-code|opencode|codex> --doctor
```

It is read-only: it checks source contracts, generated role bindings, and the
harness's credential/dependency doctor; it does not run an experiment or make
a backend call. The host then follows `AGENTS.md`, the role contract, and the
dispatch queue. A readiness failure blocks execution but is never research
evidence.

## Verify the package

```sh
python3 plugins/crypto-autoresearcher-harness/tests/test_bundle.py
python3 /Users/adamburan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/crypto-autoresearcher-harness
```

The first test validates every packaging boundary and runs the static
preflight. The second checks the Codex plugin manifest contract.
