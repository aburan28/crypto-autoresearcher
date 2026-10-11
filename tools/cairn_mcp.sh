#!/bin/sh
# The cairn network as MCP tools for an agent in this repository
# (`.mcp.json` and `opencode.json` server "cairn").
# docs/cairn-runbook.md is the operator's page.
#
# Two arrangements, chosen by CAIRN_MODE:
#
#   node     (default) `cairn run`: this session's own complete node -- MCP on
#            stdio, P2P sync, the HTTP API and the reader, one exclusive log --
#            with the MCP client as its process supervisor, which is the
#            arrangement cairn documents as the live bridge. What the agent
#            submits reaches peers while the session runs; what peers settle
#            reaches the agent's tools. Needs a binary built with the reader
#            (every release binary; `make ui-build` from source).
#   offline  `cairn mcp`: a standalone server on a log that reaches nobody
#            until a daemon syncs it with the MCP server stopped. For work
#            that should stay off the network on purpose.
#
# `.mcp.json` is committed and shared across every worktree, and cairn wants
# absolute paths, so this wrapper resolves them at launch:
#
#   CAIRN_BIN            the cairn binary (default: `cairn` on PATH)
#   CAIRN_IDENTITY       an ed25519 identity file from `cairn identity --out`;
#                        REQUIRED: an unsigned submitter authenticates nothing,
#                        and a claim this program makes must be its own
#   CAIRN_DATA           node mode: the data directory (identity, root key,
#                        checkpoint, queue, log); default ~/.cairn/<worktree>/
#   CAIRN_LOG            the log (default: $CAIRN_DATA/cairn.jsonl in node mode,
#                        ~/.cairn/<worktree>.jsonl offline)
#   CAIRN_LISTEN         node mode: the P2P address (default 127.0.0.1:9000;
#                        0.0.0.0:<port> to be reachable from other machines)
#   CAIRN_SERVE          node mode: the HTTP address (default 127.0.0.1:8080)
#   CAIRN_BOOTSTRAP      node mode: a bootstrap file from `cairn gen-bootstrap`
#                        naming the operator's node; repeat with ':' between
#   CAIRN_ATTEST_IDENTITY node mode: also run the validator loop under this
#                        funded identity (cairn's own variable; passed through)
#
# Two sessions on one machine need two data directories and two port pairs:
# a log has one writer, and cairn refuses a second rather than forking it.
#
# Exits 3 with one line on stderr when something is missing, so an MCP client
# sees "server failed to start: <reason>" instead of a silent empty tool list.
# A machine without cairn loses the network tools and nothing else.
set -eu
# This launcher serves research agents, not the Coordinator's funding key.
# Current cairn also exposes post_objective over MCP; never inherit a spend
# ceiling from an operator shell or a service environment.
CAIRN_MCP_MAX_SPEND=0
export CAIRN_MCP_MAX_SPEND
repo=$(cd "$(dirname "$0")/.." && git rev-parse --show-toplevel 2>/dev/null || pwd)
name=$(basename "$repo")
bin=${CAIRN_BIN:-$(command -v cairn || true)}
[ -n "$bin" ] && [ -x "$bin" ] || { echo "cairn_mcp.sh: no cairn binary (set CAIRN_BIN or put cairn on PATH)" >&2; exit 3; }
[ -n "${CAIRN_IDENTITY:-}" ] || { echo "cairn_mcp.sh: CAIRN_IDENTITY is unset; make one with: $bin identity --out ~/.cairn/$name.identity.json" >&2; exit 3; }
[ -f "$CAIRN_IDENTITY" ] || { echo "cairn_mcp.sh: CAIRN_IDENTITY=$CAIRN_IDENTITY is not a file" >&2; exit 3; }
mode=${CAIRN_MODE:-node}
# The log goes on the command line below; left in the environment, cairn
# warns that CAIRN_LOG is a deprecated spelling of CAIRN_LOG_PATH on every start.
log_env=${CAIRN_LOG:-}
unset CAIRN_LOG

case "$mode" in
  offline)
    log=${log_env:-$HOME/.cairn/$name.jsonl}
    mkdir -p "$(dirname "$log")"
    exec "$bin" mcp --log "$log" --root "$repo" --identity "$CAIRN_IDENTITY"
    ;;
  node)
    # `cairn run` needs the reader embedded; a plain `cargo build` says so at
    # start, but saying it here names the fix instead of a dead server.
    if ! "$bin" --version 2>/dev/null | grep -q 'embedded'; then
      echo "cairn_mcp.sh: $bin was built without the reader, which \`cairn run\` needs; use a release binary or \`make ui-build\`, or set CAIRN_MODE=offline" >&2
      exit 3
    fi
    data=${CAIRN_DATA:-$HOME/.cairn/$name}
    log=${log_env:-$data/cairn.jsonl}
    mkdir -p "$data" "$(dirname "$log")"
    set -- --listen "${CAIRN_LISTEN:-127.0.0.1:9000}" --serve "${CAIRN_SERVE:-127.0.0.1:8080}" \
           --mcp-identity "$CAIRN_IDENTITY" --queue "$data/queue"
    if [ -n "${CAIRN_BOOTSTRAP:-}" ]; then
      old_ifs=$IFS; IFS=:
      for peer in $CAIRN_BOOTSTRAP; do
        [ -f "$peer" ] || { echo "cairn_mcp.sh: CAIRN_BOOTSTRAP entry $peer is not a file" >&2; exit 3; }
        set -- "$@" --bootstrap "$peer"
      done
      IFS=$old_ifs
    fi
    if [ -n "${CAIRN_ATTEST_IDENTITY:-}" ]; then
      [ -f "$CAIRN_ATTEST_IDENTITY" ] || { echo "cairn_mcp.sh: CAIRN_ATTEST_IDENTITY=$CAIRN_ATTEST_IDENTITY is not a file" >&2; exit 3; }
      set -- "$@" --attest-identity "$CAIRN_ATTEST_IDENTITY"
    fi
    exec "$bin" --log "$log" --root "$repo" --data-dir "$data" run "$@"
    ;;
  *)
    echo "cairn_mcp.sh: CAIRN_MODE=$mode is not one of node, offline" >&2
    exit 3
    ;;
esac
