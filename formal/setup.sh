#!/usr/bin/env bash
# Bring this Lean workspace up on a machine that can reach the network.
#
# Everything here needs network and a Lean toolchain, which is why it is a
# script you run rather than something the harness does: the repository commits
# the CONTRACT (lakefile.toml, AxiomAudit.lean) and the resolved PIN
# (lake-manifest.json, lean-toolchain), and this produces the pin.
#
#     ./formal/setup.sh              # track mathlib master, pin what it resolves
#     ./formal/setup.sh v4.22.0      # track a Mathlib tag instead
#
# Re-running it re-resolves the pin. Commit lake-manifest.json and
# lean-toolchain afterwards -- those two files are what make a later
# verification reproducible.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd .. && pwd)"
REV="${1:-}"

if ! command -v elan >/dev/null 2>&1; then
  cat >&2 <<'MSG'
error: elan not found.

Lean is installed per machine, not vendored here. Install elan first:
  curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
then re-run this script.
MSG
  exit 1
fi

if [ -n "$REV" ]; then
  echo "==> pinning mathlib rev to $REV in lakefile.toml"
  python3 - "$REV" <<'PY'
import pathlib, re, sys
rev = sys.argv[1]
p = pathlib.Path("lakefile.toml")
p.write_text(re.sub(r'^rev = ".*"$', f'rev = "{rev}"', p.read_text(), flags=re.M))
PY
fi

# Chicken-and-egg: running lake at all needs SOME toolchain, and the one we
# must end up with is whichever Mathlib itself uses. Bootstrap on stable, then
# adopt Mathlib's and rebuild.
if [ ! -f lean-toolchain ]; then
  echo "==> bootstrapping on leanprover/lean4:stable"
  elan toolchain install stable
  echo "leanprover/lean4:stable" > lean-toolchain
fi

echo "==> resolving dependencies (writes lake-manifest.json -- this is the pin)"
lake update

MATHLIB_TOOLCHAIN=".lake/packages/mathlib/lean-toolchain"
if [ -f "$MATHLIB_TOOLCHAIN" ]; then
  if ! cmp -s "$MATHLIB_TOOLCHAIN" lean-toolchain; then
    echo "==> adopting Mathlib's toolchain: $(cat "$MATHLIB_TOOLCHAIN")"
    cp "$MATHLIB_TOOLCHAIN" lean-toolchain
    # The resolution above ran under the bootstrap toolchain; redo it under the
    # real one so the manifest is the one that toolchain produces.
    lake update
  fi
else
  echo "warning: no Mathlib toolchain found; lean-toolchain left as-is" >&2
fi

echo "==> fetching prebuilt Mathlib oleans (skip this and you compile Mathlib yourself)"
lake exe cache get || echo "warning: cache unavailable; 'lake build' will compile Mathlib" >&2

echo "==> generating the root module"
python3 "$REPO_ROOT/tools/rebuild_formal_root.py" --workspace "$(pwd)"

echo "==> building"
lake build

# Last, and on purpose: AxiomAudit.lean is the gate every run gets judged by,
# and it was written without a live toolchain to check it against. Find out now.
echo "==> compiling the axiom audit"
lake env lean AxiomAudit.lean

cat <<'MSG'

done. Commit lean-toolchain and lake-manifest.json -- they are the pin a later
verification reproduces against. Then:

    autoresearch formal doctor
MSG
