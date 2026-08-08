# Local peer-MCP client snippets

The peer daemon is a loopback-only, shared local coordination service. Start
it once from a Crypto Autoresearcher checkout before connecting any host:

```sh
python3 -m pip install -e ".[campaign-mcp]"
python3 -m orchestration.campaign.mcp_server --repo /absolute/path/to/crypto-autoresearcher
```

It listens at `http://127.0.0.1:8765/mcp` by default. The server stores only
derived check-ins and controller-lease observations; it cannot dispatch work,
write a ledger record, or change research state.

Before an agent calls one of the peer tools, it must compute its own checkout
binding and pass the resulting `workspace_id` as `expected_workspace_id`:

```sh
autoresearch campaign workspace --repo /absolute/path/to/crypto-autoresearcher
```

The daemon rejects a mismatch before reading or writing its SQLite state. This
prevents accidental cross-checkout routing; it is not an identity mechanism.

| Host | Snippet | Installation |
| --- | --- | --- |
| Codex | `codex.toml` | Merge the table into a deliberately chosen Codex configuration after the daemon is running, or run `codex mcp add crypto-autoresearcher-peer --url http://127.0.0.1:8765/mcp`. The plugin intentionally does not auto-register it. |
| Claude Code | `claude-code.mcp.json` | Merge only its `mcpServers.crypto-autoresearcher-peer` entry into checkout-root `.mcp.json`, or run `claude mcp add --scope project --transport http crypto-autoresearcher-peer http://127.0.0.1:8765/mcp`. |
| OpenCode | `opencode.json` | Merge its `mcp.crypto-autoresearcher-peer` entry into the user or project configuration, or run `opencode mcp add crypto-autoresearcher-peer --url http://127.0.0.1:8765/mcp`. |

Do not overwrite a user-owned `.mcp.json`/`opencode.json` or a generated
runtime binding when installing a snippet. All clients for one checkout must
point to the same daemon URL. If another checkout uses a daemon on the same
host, give it a distinct loopback port, use a distinct MCP server name, and
update only that checkout's explicit configuration; peer identity is untrusted
advisory data, not authentication.

For example, start a second checkout on port `8766` and configure its chosen
server name with `http://127.0.0.1:8766/mcp`. An IPv6 loopback daemon uses a
bracketed URL such as `http://[::1]:8765/mcp`. Never reuse one static client
entry for multiple checkouts.
