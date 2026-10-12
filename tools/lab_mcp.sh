#!/bin/sh
# MCP stdio launcher for the cairn lab (`.mcp.json` server "cairn-lab").
#
# The lab's tools (lab_read, lab_write, lab_claim, lab_send, lab_exec, ...)
# give an agent the program's research state without git: every write is
# signed by this machine's lab identity, a write against a stale read becomes
# a visible conflict, and `lab_exec` runs in a sandboxed environment whose
# backend only CAIRN_LAB_SANDBOX here can choose. See docs/cairn-lab.md.
#
# Unconfigured machines get one stderr line naming what is missing and a
# non-zero exit, which the client shows as a server that failed to start;
# nothing else in the session depends on it.
set -eu
repo="$(cd "$(dirname "$0")/.." && pwd)"
bin="${CAIRN_BIN:-$(command -v cairn || true)}"
lab="${CAIRN_LAB:-$repo/.cairn-lab}"
if [ -z "$bin" ]; then
    echo "cairn-lab: no cairn binary (set CAIRN_BIN or put cairn on PATH)" >&2
    exit 3
fi
if [ ! -e "$lab/space" ]; then
    echo "cairn-lab: no lab at $lab (tools/lab_sync.py init, or cairn lab clone)" >&2
    exit 3
fi
if [ -z "${CAIRN_LAB_IDENTITY:-}" ]; then
    echo "cairn-lab: CAIRN_LAB_IDENTITY is not set" >&2
    exit 3
fi
# The address messages and leases are attributed to: a role, because roles
# outlive the sessions playing them (the same convention as tools/agent_bus.py).
exec "$bin" lab --lab "$lab" mcp --identity "$CAIRN_LAB_IDENTITY" --as "${CAIRN_LAB_ADDRESS:-agent}"
