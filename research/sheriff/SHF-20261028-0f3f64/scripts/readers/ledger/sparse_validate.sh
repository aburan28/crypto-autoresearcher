#!/usr/bin/env bash
# Run tools/validate_ledger.py (the commit's own copy, with its own baseline)
# at an arbitrary commit, in a temporary sparse git worktree, then remove it.
#
# Sheriff case SHF-20261028-0f3f64, B7 ledger reader.
# Usage: sparse_validate.sh <commit> <label> <output-dir>
#
# Disk is tight (a full tree is ~9 GB), so tracked files larger than 1 MB are
# left out of the checkout and replaced by empty placeholders of the same name:
# the validator tests those paths for existence (capture artifacts) but does
# not read them. Fidelity of this method is controlled by running it on the
# current main commit and comparing with the full-checkout result.
set -euo pipefail
commit=$1 label=$2 out=$3
repo=/home/user/crypto-autoresearcher
scratch=/tmp/claude-0/-home-user-crypto-autoresearcher/536b79e7-3675-57b6-80e8-5308079d00ae/scratchpad
wt=$scratch/wt-$label
export GIT_LFS_SKIP_SMUDGE=1
# Every off-cone path gets a placeholder below, so nothing reads as missing.
export CRYPTO_AR_ALLOW_SPARSE=1
mkdir -p "$out"
cleanup() { git -C "$repo" worktree remove --force "$wt" >/dev/null 2>&1 || rm -rf "$wt"; git -C "$repo" worktree prune; }
trap cleanup EXIT
git -C "$repo" worktree add --no-checkout --detach "$wt" "$commit" >/dev/null 2>&1
big=$scratch/big-$label.txt
# YAML records are always materialized whatever their size: the validator parses
# them (a 1 MB specification and a 2 MB run manifest exist on main).
git -C "$repo" ls-tree -r -l "$commit" | awk '$4!="-" && $4>1000000 {sub(/^[^\t]*\t/, ""); print}' \
  | grep -Ev '(\.ya?ml|/manifest\.json)$' > "$big" || true
{
  echo '/*'
  sed 's|^|!/|' "$big"
} > "$scratch/sparse-$label.txt"
git -C "$wt" sparse-checkout init --no-cone >/dev/null 2>&1
git -C "$wt" sparse-checkout set --no-cone --stdin < "$scratch/sparse-$label.txt"
git -C "$wt" checkout --quiet --detach "$commit" 2>/dev/null || git -C "$wt" read-tree -mu HEAD
while IFS= read -r p; do mkdir -p "$wt/$(dirname "$p")"; : > "$wt/$p"; done < "$big"
du -sh "$wt" | awk '{print "worktree_size " $1}' > "$out/validate_ledger_$label.meta"
echo "commit $(git -C "$wt" rev-parse HEAD)" >> "$out/validate_ledger_$label.meta"
echo "placeholders $(wc -l < "$big")" >> "$out/validate_ledger_$label.meta"
( cd "$wt" && set +e; python3 tools/validate_ledger.py > "$out/validate_ledger_$label.txt" 2>&1; echo "exit=$?" >> "$out/validate_ledger_$label.txt" )
( cd "$wt" && set +e; python3 tools/validate_ledger.py --no-baseline > "$out/validate_ledger_${label}_nobaseline.txt" 2>&1; echo "exit=$?" >> "$out/validate_ledger_${label}_nobaseline.txt" )
grep -c '^  - ' "$out/validate_ledger_$label.txt" | awk '{print "new_errors " $1}' >> "$out/validate_ledger_$label.meta"
grep -c '^  - ' "$out/validate_ledger_${label}_nobaseline.txt" | awk '{print "all_errors_no_baseline " $1}' >> "$out/validate_ledger_$label.meta"
cat "$out/validate_ledger_$label.meta"
