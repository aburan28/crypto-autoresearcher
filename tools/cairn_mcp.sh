#!/bin/sh
# The cairn network as MCP tools for an agent in this repository.
#
# `.mcp.json` is committed and shared across every worktree, and cairn wants
# absolute paths, so this wrapper resolves them at launch: the repository
# root for `--root` (pinned checkers resolve against it), the per-worktree log
# for `--log`, and the signing identity that makes a submitter a key rather
# than a nickname. The same reasoning made the crypto-kb stanza use a relative
# --directory and the lab stanza go through tools/lab_mcp.sh.
#
#   CAIRN_BIN       the cairn binary (default: `cairn` on PATH)
#   CAIRN_LOG       the log this worktree submits to
#                   (default: ~/.cairn/<worktree-basename>.jsonl, the bridge's own default)
#   CAIRN_IDENTITY  an ed25519 identity file from `cairn identity --out`;
#                   REQUIRED: an unsigned submitter authenticates nothing, and
#                   a claim this program makes on the network must be its own
#
# Exits 3 with one line on stderr when something is missing, so an MCP client
# sees "server failed to start: <reason>" instead of a silent empty tool list.
# A machine without cairn loses the network tools and nothing else.
set -eu
repo=$(cd "$(dirname "$0")/.." && git rev-parse --show-toplevel 2>/dev/null || pwd)
bin=${CAIRN_BIN:-$(command -v cairn || true)}
[ -n "$bin" ] && [ -x "$bin" ] || { echo "cairn_mcp.sh: no cairn binary (set CAIRN_BIN or put cairn on PATH)" >&2; exit 3; }
log=${CAIRN_LOG:-$HOME/.cairn/$(basename "$repo").jsonl}
[ -n "${CAIRN_IDENTITY:-}" ] || { echo "cairn_mcp.sh: CAIRN_IDENTITY is unset; make one with: $bin identity --out ~/.cairn/$(basename "$repo").identity.json" >&2; exit 3; }
[ -f "$CAIRN_IDENTITY" ] || { echo "cairn_mcp.sh: CAIRN_IDENTITY=$CAIRN_IDENTITY is not a file" >&2; exit 3; }
mkdir -p "$(dirname "$log")"
exec "$bin" mcp --log "$log" --root "$repo" --identity "$CAIRN_IDENTITY"
