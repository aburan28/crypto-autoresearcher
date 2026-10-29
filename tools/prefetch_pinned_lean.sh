#!/usr/bin/env bash
set -euo pipefail

# Prefetch a frozen toolchain before lean-action invokes Lean. Elan's own
# download retry is short; hosted runners have intermittently received TLS
# errors from the Lean release endpoint before any proof control could run.
toolchain_file=${1:?usage: prefetch_pinned_lean.sh PATH/lean-toolchain}
test -f "$toolchain_file"
toolchain=$(tr -d '\r\n' < "$toolchain_file")
if [[ ! "$toolchain" =~ ^leanprover/lean4:v[0-9]+\.[0-9]+\.[0-9]+(-rc[0-9]+)?$ ]]; then
  echo "Expected an exact leanprover/lean4 release in $toolchain_file" >&2
  exit 1
fi

if [ ! -x "$HOME/.elan/bin/elan" ]; then
  installer=$(mktemp)
  trap 'rm -f "$installer"' EXIT
  curl --fail --location --silent --show-error --retry 3 --retry-all-errors \
    --retry-delay 2 \
    https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
    -o "$installer"
  sh "$installer" -y --default-toolchain none --no-modify-path
fi

for attempt in 1 2 3; do
  if "$HOME/.elan/bin/elan" toolchain install "$toolchain"; then
    workspace=$(dirname "$toolchain_file")
    version=$(cd "$workspace" && "$HOME/.elan/bin/lean" --version)
    expected=${toolchain##*:v}
    if [[ "$version" != *"version $expected,"* ]]; then
      echo "Installed Lean does not match $toolchain: $version" >&2
      exit 1
    fi
    echo "$HOME/.elan/bin" >> "$GITHUB_PATH"
    exit 0
  fi
  if [ "$attempt" -eq 3 ]; then
    echo "Could not install $toolchain after 3 attempts" >&2
    exit 1
  fi
  sleep $((2 ** attempt))
done
