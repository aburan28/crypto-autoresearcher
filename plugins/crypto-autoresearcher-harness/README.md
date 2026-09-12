# Crypto Autoresearcher Harness plugin

This package exposes one execution skill named **run**. It launches existing
experiment programs, shows progress, retains outputs, and reports results.
Protocol preparation, repository audits, publication, and scientific review
are separate tasks. The runner's built-in checks remain active.

## Host adapters

| Host | Adapter | Discovery |
| --- | --- | --- |
| Codex | `.agents/skills/run/` | Repository discovery; installation is optional. |
| Claude Code | `.claude/skills/run/` | Repository discovery; installation is optional. |
| OpenCode | `.agents/skills/run/` | Project-local skill discovery. |

## Run experiments

Invoke `$run` in Codex/OpenCode or `/run` in Claude Code:

```text
$run
$run EXP-...
$run GOAL-...
```

A named experiment or goal limits execution to that scope. Existing command-based
experiments use their documented launchers; they do not need migration to a new
trial-plan format. A refused launch is reported once, with its concrete reason.
An unqualified run can continue other runnable work.

The canonical skill is [`skills/run/SKILL.md`](skills/run/SKILL.md).
The old `crypto-autoresearcher-harness`, `run-experiment`,
`launch-research-harness`, and `coordinate-research-goal` execution skills are
retired. Their broader coordination material is retained as
[`WORKFLOW.md`](skills/crypto-autoresearcher-harness/WORKFLOW.md), outside skill
discovery, for explicitly requested coordination work.

The run skill does not add preflight, whole-ledger/schema/protocol validation,
portfolio-health sweeps, branch synchronization, protocol authoring, PR creation,
or an independent-review cycle. It reports actual outputs and failures; a
scientific claim still needs the separate evidence-review process.

## Maintaining the package

These are developer checks, not steps in the run skill:

```sh
python3 plugins/crypto-autoresearcher-harness/scripts/entrypoints.py --repo . --write
python3 plugins/crypto-autoresearcher-harness/scripts/entrypoints.py --repo . --check
python3 -m unittest discover -s plugins/crypto-autoresearcher-harness/tests -v
```

The generator writes the two host adapters. Its check reports any retired
execution skill that reappears, without deleting local files. Preflight remains
available as an explicit maintenance diagnostic.

A repository adapter and an installed plugin can both be discovered. Prefer the
repository adapter while developing here. Inspect additional known roots with
`entrypoints.py --repo . --check --skill-root <installed-skill-root>`.
This is a filesystem inventory, not the host's enabled-skill list. An installed
plugin cache is a separate copy and is not refreshed by editing this checkout.

The optional `scripts/checkpoint.py` is a maintenance view of queue state;
experiment progress comes directly from the running program and its outputs.

## Local peer check-in service

The package also describes one optional, standalone local peer service. Run it
once in a checkout, then let every host connect to its single loopback-only
Streamable HTTP endpoint:

```sh
python3 -m pip install -e ".[campaign-mcp]"
python3 -m orchestration.campaign.mcp_server \
  --repo /absolute/path/to/crypto-autoresearcher
```

The default endpoint is `http://127.0.0.1:8765/mcp`. It is intentionally a
daemon rather than a stdio server: a stdio process started once by each host
would not provide a common view of other local agents. The daemon holds only
short-lived check-ins and a read-only observation of any internal controller
lease. Its SQLite file is rebuildable runtime state under a private user-state
directory (or an explicit private `--state-db` path), never ledger evidence.
It is hard-bound to `127.0.0.1` by default, rejects non-loopback listener
configuration, and explicitly enables Host/Origin protection.

The MCP surface is deliberately narrow:

- `check_in`, `list_peers`, and `check_out` provide bounded, advisory local
  presence information.
- `get_coordination_status` reports daemon health and any observed lease.
- No tool can dispatch or claim a task, change a goal/hypothesis/experiment,
  advance a checkpoint, archive an artifact, or grant Coordinator authority.

The service intentionally has no identity or authorization layer: any process
that can reach the same loopback port may submit, replace, or remove advisory
presence. Treat every peer identity, summary, scope, and lease observation as
untrusted operational context—not as authorization or evidence. Run one daemon
per checkout; if you run more than one checkout on the same host, choose a
different loopback `--port` and update that checkout's client URL deliberately.
The private SQLite file does not make the HTTP API private: any same-host
process can read peer summaries, task IDs, scopes, source commits, and bounded
goal-projection metadata. Keep peer summaries non-sensitive.
Each MCP operation also requires the caller's locally computed
`expected_workspace_id`; obtain it with `autoresearch campaign workspace
--repo /absolute/path/to/crypto-autoresearcher`. A mismatch fails before any
read or heartbeat write, preventing accidental cross-checkout use of a shared
port. This is an anti-misrouting check, not authentication.

Install/merge only the host-specific snippet in
[`clients/`](clients/README.md). The Codex plugin deliberately does **not**
auto-register a peer endpoint: a fixed loopback port could belong to a daemon
from another checkout or another same-host process. Start the daemon, then add
the endpoint explicitly for that checkout. Claude Code and OpenCode users
should likewise merge the provided template or use the documented CLI command;
merge only the named MCP entry and do not overwrite a user-owned
`.mcp.json`/`opencode.json`, generated `.codex/config.toml`, or generated role
bindings.

## Install and use

Clone the repository, install its normal Python dependencies, and start in the
checkout. The plugin makes no credential, backend, or marketplace changes by
itself.

### Codex (optional plugin installation)

The repository adapter already works in a checkout. Install only if you prefer
the plugin source, and check duplicate discovery above.

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
role bindings. To connect the optional local peer service, merge only
`mcpServers.crypto-autoresearcher-peer` from `clients/claude-code.mcp.json`
into a checkout-root `.mcp.json`, or preferably run:

```sh
claude mcp add --scope project --transport http \
  crypto-autoresearcher-peer http://127.0.0.1:8765/mcp
```

### OpenCode

No npm package is needed. Start OpenCode in the repository checkout; it finds
the project-local `.agents/skills/run/` adapter and
then loads the canonical shared skill from this package. The existing
`opencode.json` and generated `.opencode/agent/` files continue to control
models and permissions. To connect the optional local peer service, merge the
`mcp.crypto-autoresearcher-peer` object from `clients/opencode.json`, or run:

```sh
opencode mcp add crypto-autoresearcher-peer \
  --url http://127.0.0.1:8765/mcp
```

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
