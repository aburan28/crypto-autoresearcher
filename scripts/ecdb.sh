#!/usr/bin/env bash
# ecdb.sh: a thin client for the lab's curve database (ecdb), for shell tools
# and agents without the MCP server. The same file is in each isogeny-labs
# repository that reads ecdb; the guide is crypto's ecdb/docs/AGENTS.md.
#
#   ecdb.sh get /v1/meta                       any GET route (see /openapi.yaml)
#   ecdb.sh curve secp256k1 [part]             a curve document, or one part:
#                                              isogenies graph transfers covers traits relations
#                                              endomorphisms division-polynomials measurements
#   ecdb.sh sql 'SELECT ... FROM v_curve_summary LIMIT 5'
#   ecdb.sh results leaderboard|progress|boundary|benchmarks ['query string']
#   ecdb.sh ecbench [session_id]
#   ecdb.sh check                              is ecdb's copy of this repository's files current?
#
# Environment: ECDB_TOKEN (the read token; when unset and the AWS CLI can read
# secret ecdb/api, it is read from there into this process only and never
# printed), ECDB_URL (default: the deployed function URL).
set -euo pipefail

ECDB_URL=${ECDB_URL:-https://l6zg6lz4dr45t75p5qn5aocnme0pckrm.lambda-url.us-west-2.on.aws}
ECDB_URL=${ECDB_URL%/}

die() { echo "ecdb.sh: $*" >&2; exit 2; }
command -v curl >/dev/null || die "needs curl"
command -v jq >/dev/null || die "needs jq"

token() {
  if [ -z "${ECDB_TOKEN:-}" ] && command -v aws >/dev/null; then
    ECDB_TOKEN=$(aws secretsmanager get-secret-value --region us-west-2 --secret-id ecdb/api \
      --query SecretString --output text 2>/dev/null | jq -r .read_token 2>/dev/null || true)
  fi
  [ -n "${ECDB_TOKEN:-}" ] || die "set ECDB_TOKEN (secret ecdb/api, key read_token) or give the AWS CLI access to it"
}

req() { # req METHOD PATH [JSON]
  token
  local args=(-sS --fail-with-body -X "$1" -H "authorization: Bearer $ECDB_TOKEN" -H 'accept: application/json')
  [ $# -ge 3 ] && args+=(-H 'content-type: application/json' --data-binary "$3")
  curl "${args[@]}" "$ECDB_URL$2"
}

urlenc() { jq -rn --arg v "$1" '$v|@uri'; }

repo_name() {
  local url; url=$(git remote get-url origin 2>/dev/null || true)
  url=${url%.git}
  case "$url" in
    *github.com[:/]*) echo "${url#*github.com[:/]}" ;;
    *) basename "$(git rev-parse --show-toplevel)" ;;
  esac
}

sha_of() { # sha256 of a file, or of its .gz copy uncompressed
  if [ -f "$1" ]; then sha256sum "$1" | cut -d' ' -f1
  elif [ -f "$1.gz" ]; then gzip -dc "$1.gz" | sha256sum | cut -d' ' -f1
  fi
}

cmd=${1:-}; shift || true
case "$cmd" in
  get) [ $# -ge 1 ] || die "get PATH"; req GET "$1" ;;
  curve)
    [ $# -ge 1 ] || die "curve REF [PART]"
    path="/v1/curves/$(urlenc "$1")"; [ $# -ge 2 ] && path="$path/$2"
    req GET "$path" ;;
  sql) [ $# -ge 1 ] || die "sql QUERY"; req POST /v1/sql "$(jq -cn --arg q "$1" '{sql: $q}')" ;;
  results)
    kind=${1:-leaderboard}; qs=${2:-}
    case "$kind" in
      leaderboard|progress|boundary) req GET "/v1/ic/$kind${qs:+?$qs}" ;;
      benchmarks) req GET "/v1/benchmarks${qs:+?$qs}" ;;
      *) die "results leaderboard|progress|boundary|benchmarks" ;;
    esac ;;
  ecbench)
    if [ $# -ge 1 ]; then req GET "/v1/ecbench/sessions/$(urlenc "$1")"; else req GET "/v1/ecbench/sessions?limit=50"; fi ;;
  check)
    root=$(git rev-parse --show-toplevel); repo=$(repo_name)
    # One row per path with every SHA-256 ecdb has pinned for it (re-imports keep older versions).
    case "$repo" in *"'"*) die "unexpected repository name $repo" ;; esac
    sql=$(printf "SELECT path, string_agg(DISTINCT sha256::text, ','), max(git_commit) FROM source WHERE kind = 'repository_file' AND repository = '%s' AND path NOT LIKE '%%/' GROUP BY path ORDER BY path" "$repo")
    rows=$(req POST /v1/sql "$(jq -cn --arg q "$sql" '{sql: $q}')" | jq -r '.rows[] | @tsv')
    [ -n "$rows" ] || { echo "ecdb has no files of $repo"; exit 0; }
    current=0; stale=0; missing=0
    while IFS=$'\t' read -r path shas commit; do
      local_sha=$(cd "$root" && sha_of "$path")
      if [ -z "$local_sha" ]; then missing=$((missing + 1)); [ -n "${VERBOSE:-}" ] && echo "missing  $path"
      elif [[ ",$shas," == *",$local_sha,"* ]]; then current=$((current + 1))
      else
        stale=$((stale + 1))
        if [ -n "${VERBOSE:-}" ] || [ "$stale" -le 20 ]; then
          echo "stale    $path (ecdb pinned it at ${commit:0:9}; this checkout differs: redeploy ecdb)"
        fi
      fi
    done <<< "$rows"
    echo "$repo: $current current, $stale stale, $missing not in this checkout (ecdb keeps every pinned version; VERBOSE=1 lists them)"
    [ "$stale" -eq 0 ] ;;
  ""|-h|--help|help) sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//' ;;
  *) die "unknown command $cmd (try --help)" ;;
esac
