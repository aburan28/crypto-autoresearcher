#!/usr/bin/env bash
# Merge the current HEAD into the shared lane branch `lane/<lane>` and push it
# (docs/ci-tiers.md).
#
#   scripts/lane-push.sh <lane> [--dry-run]
#
# Many sessions working one research lane push to one branch, so the lane has
# one PR instead of one per session. The merge is computed with
# `git merge-tree`, so the caller's checkout and index are untouched and no
# second worktree is needed. A merge commit is pushed, never a rebase or a
# force-push; if another session pushed first, the merge is recomputed on the
# new lane head and retried. A conflict stops with exit status 2: resolve it
# by merging `origin/lane/<lane>` into your branch, then run this again.
#
# A new lane branch starts from the default branch. Open its PR as a draft;
# the merge sweeper marks an idle lane draft ready (lane_idle_hours).
set -euo pipefail

lane=${1:?usage: scripts/lane-push.sh <lane> [--dry-run]}
dry_run=${2:-}
case $lane in
  *[!a-z0-9._-]*|'') echo "lane name must match [a-z0-9._-]+: $lane" >&2; exit 64 ;;
esac
ref="lane/$lane"
default=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
default=${default:-main}
head=$(git rev-parse HEAD)
src=$(git rev-parse --abbrev-ref HEAD)

for attempt in 1 2 3 4 5; do
  git fetch --quiet origin "$default"
  if git fetch --quiet origin "refs/heads/$ref:refs/remotes/origin/$ref" 2>/dev/null; then
    base=$(git rev-parse "refs/remotes/origin/$ref")
  else
    base=$(git rev-parse "refs/remotes/origin/$default")
    echo "creating $ref from origin/$default"
  fi
  if git merge-base --is-ancestor "$head" "$base"; then
    echo "$ref already contains $head"
    exit 0
  fi
  if ! tree=$(git merge-tree --write-tree --name-only --no-messages "$base" "$head"); then
    echo "conflict merging $src into $ref; files:" >&2
    printf '%s\n' "$tree" | tail -n +2 >&2
    echo "merge origin/$ref into $src, resolve, commit, then run this again" >&2
    exit 2
  fi
  tree=$(printf '%s\n' "$tree" | head -n 1)
  commit=$(git commit-tree "$tree" -p "$base" -p "$head" -m "Merge $src into $ref")
  if [ "$dry_run" = "--dry-run" ]; then
    echo "would push $commit to $ref"
    exit 0
  fi
  if git push --quiet origin "$commit:refs/heads/$ref"; then
    echo "pushed $commit to $ref"
    exit 0
  fi
  delay=$((2 ** attempt))
  echo "push to $ref was rejected (attempt $attempt); retrying in ${delay}s" >&2
  sleep "$delay"
done
echo "gave up pushing to $ref after 5 attempts" >&2
exit 1
