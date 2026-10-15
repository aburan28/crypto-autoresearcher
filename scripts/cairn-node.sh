#!/usr/bin/env bash
# cairn-node.sh - keep one cairn node running in this cloud session, joined to
# the published seed nodes.
#
#   scripts/cairn-node.sh ensure    install if needed, start if not running (default)
#   scripts/cairn-node.sh status    is it up, and which seeds/peers has it reached
#   scripts/cairn-node.sh stop      stop the supervisor and the node
#
# Who calls it: the Claude Code SessionStart hook (.claude/settings.json) in
# every cloud session, and Codex cloud tasks through AGENTS.md ("cairn node")
# and the environment's setup script. The same file is committed in
# aburan28/crypto, cryptanalysis, crypto-autoresearcher and ml-cryptanalysis;
# change it in all four.
#
# Seeds: `cairn run` dials the seed list compiled into the binary and refreshes
# it from https://aburan28.github.io/cairn/seeds.json at start (fetched with
# curl, so it goes through the session's HTTPS proxy). Nothing here pins a seed,
# so a seed published to that list is dialled by the next session with no
# change to this repository. CAIRN_SEEDS=<file> names another list.
#
# One node per container: whichever repository's hook runs first starts it and
# the others find it running. It has its own data directory and ports so it
# never collides with the conductor control plane (8080) or with
# crypto-autoresearcher's per-session `cairn run` MCP node (9000/8080).
#
# It needs a binary built with the embedded reader (`cairn --version` says
# "embedded"): `cairn run` refuses without it. `cairn mcp` (the .mcp.json server
# in some of these repositories) does not, so an older binary is rebuilt here
# with `--features ui` and keeps serving `cairn mcp` too.
#
# Never fatal to the session: every failure is one line on stderr and exit 0.
#
# Environment:
#   CAIRN_NODE=off         do nothing (escape hatch for one environment)
#   CAIRN_REV              cairn git revision to build (default: main)
#   CAIRN_NODE_HOME        node state (default: ~/.cairn/session-node)
#   CAIRN_NODE_P2P         P2P listen address (default 127.0.0.1:9100)
#   CAIRN_NODE_HTTP        HTTP address (default 127.0.0.1:9180)
#   CAIRN_NODE_WAIT        seconds `ensure` waits for /health (default 30)
set -uo pipefail

cmd=${1:-ensure}
home=${CAIRN_NODE_HOME:-$HOME/.cairn/session-node}
p2p=${CAIRN_NODE_P2P:-127.0.0.1:9100}
http=${CAIRN_NODE_HTTP:-127.0.0.1:9180}
src=${CAIRN_SRC:-$HOME/.cache/cairn-src}
prefix=${CAIRN_PREFIX:-/usr/local}
supervisor_pid="$home/supervisor.pid"
log="$home/node.log"

say() { echo "cairn-node: $*" >&2; }

if [ "${CAIRN_NODE:-}" = "off" ]; then
  say "CAIRN_NODE=off; not starting"
  exit 0
fi

mkdir -p "$home" && chmod 700 "$home"

healthy() { curl -fsS --noproxy '*' --max-time 3 "http://$http/health" >/dev/null 2>&1; }

has_reader() { command -v cairn >/dev/null && cairn --version 2>/dev/null | grep -q 'embedded'; }

running() {
  [ -s "$supervisor_pid" ] && kill -0 "$(cat "$supervisor_pid")" 2>/dev/null
}

install() {
  has_reader && return 0
  say "installing cairn with the embedded reader (first launch only; several minutes)"
  {
    if [ -d "$src/.git" ]; then
      git -C "$src" fetch --depth 1 origin "${CAIRN_REV:-main}" && git -C "$src" checkout -q FETCH_HEAD
    else
      rm -rf "$src"
      git clone -q https://github.com/aburan28/cairn "$src" \
        && { [ -z "${CAIRN_REV:-}" ] || git -C "$src" checkout -q "$CAIRN_REV"; }
    fi \
      && (cd "$src/ui" && npm ci --no-audit --no-fund && npm run build) \
      && cargo install --locked --force --root "$prefix" --features ui --path "$src" --bin cairn
  } >>"$home/install.log" 2>&1
  if has_reader; then
    say "installed $(cairn --version | head -n 1)"
  else
    say "install failed; see $home/install.log"
    return 1
  fi
}

start() {
  if running; then
    return 0
  fi
  # The checkers objectives pin live in the cairn repository; a node without
  # them answers every claim `unavailable` (launch/seed.service, "The bundle").
  local root=$home
  [ -d "$src/examples" ] && root=$src
  # A supervisor so the node stays up for the whole session, as the published
  # seed does under systemd's Restart=always. setsid detaches it from the hook,
  # which the harness waits on and then reaps.
  CAIRN_DATA="$home" CAIRN_BEACON_PORT=off CAIRN_PORTMAP=off CAIRN_ROLES=relay \
  CAIRN_MCP_MAX_SPEND=0 \
    setsid nohup bash -c '
      echo $$ > "$1"; shift
      trap "kill \$child 2>/dev/null; exit 0" TERM INT
      while :; do
        echo "== $(date -u +%FT%TZ) cairn run"
        cairn --root "$1" run --no-mcp --listen "$2" --serve "$3" </dev/null &
        child=$!
        wait $child
        echo "== $(date -u +%FT%TZ) exited $?; restarting in 5s"
        sleep 5
      done' cairn-node "$supervisor_pid" "$root" "$p2p" "$http" \
      >>"$log" 2>&1 </dev/null &
  disown 2>/dev/null || true
  local wait=${CAIRN_NODE_WAIT:-30}
  for _ in $(seq "$wait"); do
    healthy && return 0
    sleep 1
  done
  say "started but /health is not answering after ${wait}s; see $log"
  return 1
}

seed_report() {
  # The daemon logs one line on the list it loaded and one per seed it reached
  # or could not; repeat the latest of each so a session sees it at a glance.
  grep -E 'seeds?:|peer' "$log" 2>/dev/null | tail -n 4 | sed 's/^/  /' >&2
}

case "$cmd" in
  ensure)
    # Two hooks in one container (two repositories) must not race to start two
    # nodes, and a second `cairn run` on this data directory would be refused.
    exec 9>"$home/.lock"
    flock 9
    install || exit 0
    if start; then
      say "running: http://$http (p2p $p2p), data $home, log $log"
      seed_report
    fi
    exit 0
    ;;
  status)
    if healthy; then
      say "up at http://$http"
      # GET /network carries the sessions summary: who this node has spoken to.
      curl -fsS --noproxy '*' --max-time 5 "http://$http/network" 2>/dev/null \
        | head -c 800 | sed 's/^/  /' >&2
      echo >&2
    else
      say "not answering at http://$http"
    fi
    seed_report
    ;;
  stop)
    if running; then
      kill "$(cat "$supervisor_pid")" 2>/dev/null
      rm -f "$supervisor_pid"
      say "stopped"
    else
      say "not running"
    fi
    ;;
  *)
    say "usage: $0 [ensure|status|stop]"
    exit 2
    ;;
esac
