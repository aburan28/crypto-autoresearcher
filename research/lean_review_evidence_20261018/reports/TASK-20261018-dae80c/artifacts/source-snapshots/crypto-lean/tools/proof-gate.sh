#!/usr/bin/env bash
# Repository-wide Lean proof gate (AGENTS.md "Mathematical results should
# include Lean proofs").
#
# For every Lean target in the repository:
#   * a Lake project (a directory with lakefile.toml / lakefile.lean): `lake build`,
#     then audit every module the project itself built;
#   * a standalone .lean file outside any Lake project: compile it with `lean -o`
#     against the core library, then audit that module.
# The audit (AuditAxioms.lean, next to this script) fails any theorem whose transitive
# axioms go beyond propext / Classical.choice / Quot.sound: `sorry`,
# `native_decide` and user axioms all fail. A target with no theorems fails too.
#
# Shipped by the CryptoLean package. A consumer runs its pinned copy from its
# own repository root:  .lake/packages/CryptoLean/tools/proof-gate.sh
# The repository checked is the one containing the current directory, and its
# trust manifest is tools/lean/trusted-native.txt there (override with
# LEAN_GATE_TRUSTED; a missing file means nothing is trusted).
#
# Usage: proof-gate.sh [--list] [--out DIR] [TARGET ...]
#   TARGET is a project directory or standalone file (default: all discovered).
#   --list prints the discovered targets and exits.
#   --out DIR writes one receipt per target (build log, audit log, status).
# Exit status: 0 all targets pass; 1 some target failed; 3 infrastructure error.
set -uo pipefail

here=$(cd "$(dirname "$0")" && pwd)
root=$(git rev-parse --show-toplevel) || exit 3
audit="$here/AuditAxioms.lean"
trusted="${LEAN_GATE_TRUSTED:-$root/tools/lean/trusted-native.txt}"
trust_args=()
[ -f "$trusted" ] && trust_args=(--trusted "$trusted")
out=""
list=0
targets=()
while [ $# -gt 0 ]; do
  case "$1" in
    --list) list=1 ;;
    --out) out=$2; shift ;;
    *) targets+=("$1") ;;
  esac
  shift
done

discover() {
  cd "$root" || exit 3
  # Lake projects: every lakefile outside build output and vendored packages.
  git ls-files -- '*lakefile.toml' '*lakefile.lean' | xargs -r -n1 dirname | sort -u
  # Standalone files: tracked .lean files with no lakefile in any parent directory.
  git ls-files -- '*.lean' | grep -vE '^tools/(lean|selftest)/' | while read -r f; do
    d=$(dirname "$f")
    while [ "$d" != "." ] && [ ! -f "$d/lakefile.toml" ] && [ ! -f "$d/lakefile.lean" ]; do
      d=$(dirname "$d")
    done
    [ "$d" = "." ] && [ ! -f lakefile.toml ] && [ ! -f lakefile.lean ] && echo "$f"
  done
}

if [ ${#targets[@]} -eq 0 ]; then mapfile -t targets < <(discover); fi
if [ $list -eq 1 ]; then printf '%s\n' "${targets[@]}"; exit 0; fi
[ ${#targets[@]} -gt 0 ] || { echo "no Lean targets found" >&2; exit 3; }
command -v lake > /dev/null || { echo "lake not on PATH (install elan)" >&2; exit 3; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
fail=0
summary=()

run_target() {
  local t=$1 slug log status
  slug=$(echo "$t" | tr '/.' '__')
  log="$scratch/$slug"
  mkdir -p "$log"
  status=PASS
  if [ -d "$root/$t" ]; then
    # Lake project. Mathlib projects fetch Mathlib's prebuilt cache first; a
    # failed fetch is an infrastructure error, never evidence about a proof.
    if grep -q '"name": *"mathlib"' "$root/$t/lake-manifest.json" 2>/dev/null; then
      (cd "$root/$t" && lake exe cache get) > "$log/cache.log" 2>&1 \
        || { echo "INFRA_cache   $t (lake exe cache get failed)"; return 3; }
    fi
    if ! (cd "$root/$t" && lake build) > "$log/build.log" 2>&1; then
      status=FAIL_build
    else
      local mods
      mods=$(cd "$root/$t/.lake/build/lib/lean" 2>/dev/null && find . -name '*.olean' \
        | sed 's|^\./||; s|\.olean$||; s|/|.|g' | sort | tr '\n' ' ')
      if [ -z "$mods" ]; then
        status=FAIL_no_modules
      elif ! (cd "$root/$t" && lake env lean --run "$audit" "${trust_args[@]}" $mods) > "$log/audit.log" 2>&1; then
        status=FAIL_audit
      fi
    fi
  else
    # Standalone file: compile into a private olean directory, then audit it.
    local mod dir toolchain
    mod=$(basename "$t" .lean)
    dir="$log/olean"
    mkdir -p "$dir"
    toolchain=$(cat "$(dirname "$root/$t")/lean-toolchain" 2>/dev/null || true)
    if ! (cd "$(dirname "$root/$t")" && lean -o "$dir/$mod.olean" "$root/$t") > "$log/build.log" 2>&1; then
      status=FAIL_build
    elif ! LEAN_PATH="$dir:${LEAN_PATH:-}" lean --run "$audit" "${trust_args[@]}" "$mod" > "$log/audit.log" 2>&1; then
      status=FAIL_audit
    fi
    [ -n "$toolchain" ] && echo "toolchain pin: $toolchain" >> "$log/build.log"
  fi
  # `sorry` that elaborated without being used by a theorem still warns at build time.
  if [ "$status" = PASS ] && grep -q "declaration uses 'sorry'" "$log/build.log"; then
    status=FAIL_sorry_warning
  fi
  echo "$status" > "$log/status"
  if [ -n "$out" ]; then mkdir -p "$out/$slug" && cp -r "$log"/*.log "$log/status" "$out/$slug/"; fi
  local n
  n=$(grep -o 'audited [0-9]* theorems' "$log/audit.log" 2>/dev/null | grep -o '[0-9]*' || echo 0)
  local tr
  tr=$(grep -o '[0-9]* trusted' "$log/audit.log" 2>/dev/null | grep -o '[0-9]*' || echo 0)
  printf '%-22s %4s thm %3s trusted  %s\n' "$status" "${n:-0}" "${tr:-0}" "$t"
  if [ "$status" != PASS ]; then
    grep -E '^FAIL|error|no theorems' "$log/audit.log" "$log/build.log" 2>/dev/null | head -5 | sed 's/^/    /'
    return 1
  fi
}

infra=0
for t in "${targets[@]}"; do
  run_target "$t"
  case $? in 0) ;; 3) infra=1 ;; *) fail=1 ;; esac
done
[ $fail -eq 1 ] && exit 1
[ $infra -eq 1 ] && exit 3
exit 0
