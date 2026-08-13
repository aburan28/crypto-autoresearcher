#!/usr/bin/env bash
# probe_git_plumbing.sh -- TASK-20260813-451a6d (Validator)
#
# Independently checks, with git plumbing, the two archive commits of
# BATCH-fbb639 named in the task envelope:
#   3d2eabf8d  PREREG-3 notarization (TASK-20260813-6ad846, 3 declared paths)
#   391f811e7  lead producer snapshot (TASK-20260813-7ac7cd, 8 declared paths)
#
# Checks performed:
#   1. prereg.md ABSENT at the notarizing commit's parent (743a2fb31).
#   2. prereg.md PRESENT at 3d2eabf8d, sha256 matches the frozen hash cited
#      in the task envelope (3f64e2688f...).
#   3. change-set of 3d2eabf8d vs its parent EQUALS the declared 3-path set,
#      0 extra / 0 missing.
#   4. ZERO producer artifacts (measure_c3lane.py etc.) exist anywhere under
#      tasks/TASK-20260813-7b3039 at commit 3d2eabf8d (only task_card.md,
#      a batch-opening coordination artifact committed earlier, is present).
#   5. `git log --all --follow` for prereg.md returns EXACTLY ONE commit.
#   6. change-set of 391f811e7 vs its parent (18bf28634) EQUALS the declared
#      8-path set, 0 extra / 0 missing.
#   7. Each of the 7 producer artifacts + the 7ac7cd receipt FIRST APPEARS
#      (exact path, not --follow) at 391f811e7 and nowhere earlier.
#   8. Both notarizing and producer-snapshot commits are ancestors of HEAD.
#   9. A known git --follow artifact: for the 0-byte stderr.log, --follow
#      matches unrelated empty blobs across history (100%-similarity rename
#      heuristic on empty content) -- checked and explained, not treated as
#      a defect, since the exact-path (non-follow) log is unambiguous.

set -u
cd /home/user/crypto-autoresearcher

NOTARIZE_SHA=3d2eabf8ddfa9e33ed3c9cf5b0cc0d9f14ebcd82
NOTARIZE_PARENT=743a2fb312090e5eef4d99cd68a0d38d71c6f394
PRODUCER_SHA=391f811e7b6b23fb40235a0608aebeb05b5b9c4a
PRODUCER_PARENT=18bf286348fabc13114f200509ee12f65d6c9756
PREREG_PATH=coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-0eb5a3/prereg.md
PREREG_SHA256_EXPECTED=3f64e2688f0d52b93ad2428ffa99883b0234edeb47aff0c242628a6d880c7138

echo "=== 1. prereg.md ABSENT at notarizing commit's parent ($NOTARIZE_PARENT)? ==="
git show "$NOTARIZE_PARENT:$PREREG_PATH" 2>&1 | head -3

echo
echo "=== 2. prereg.md PRESENT at $NOTARIZE_SHA, sha256 ==="
git show "$NOTARIZE_SHA:$PREREG_PATH" | sha256sum

echo
echo "=== 3. change-set of $NOTARIZE_SHA vs parent (expect exactly 3 added paths) ==="
git diff --name-status "$NOTARIZE_PARENT" "$NOTARIZE_SHA"
echo "count: $(git diff --name-only "$NOTARIZE_PARENT" "$NOTARIZE_SHA" | wc -l) (expect 3)"

echo
echo "=== 4. producer-dir listing at $NOTARIZE_SHA (expect ONLY task_card.md, zero producer artifacts) ==="
git ls-tree "$NOTARIZE_SHA" -- coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/
echo "(task_card.md pre-existed at the batch-opening commit 743a2fb31, confirmed below)"
git show 743a2fb31:coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/task_card.md 2>&1 | head -1

echo
echo "=== 5. git log --all --follow for prereg.md (expect exactly one commit) ==="
git log --all --follow --format='%H' -- "$PREREG_PATH"

echo
echo "=== 6. change-set of $PRODUCER_SHA vs parent (expect exactly 8 added paths) ==="
git diff --name-status "$PRODUCER_PARENT" "$PRODUCER_SHA"
echo "count: $(git diff --name-only "$PRODUCER_PARENT" "$PRODUCER_SHA" | wc -l) (expect 8)"

echo
echo "=== 7. first-appearance check, EXACT PATH (no --follow), for each of the 7 producer artifacts + receipt ==="
for f in command.txt measure_c3lane.py report_c3lane.md results_c3lane.json run_manifest.yaml stderr.log stdout.log; do
  p="coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/$f"
  echo "-- $f --"
  git log --all --format='%H' -- "$p"
done
echo "-- archives/TASK-20260813-7ac7cd/snapshot-receipt.json --"
git log --all --format='%H' -- coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/archives/TASK-20260813-7ac7cd/snapshot-receipt.json

echo
echo "=== 8. both commits ancestors of HEAD? ==="
git merge-base --is-ancestor "$NOTARIZE_SHA" HEAD && echo "3d2eabf8d IS an ancestor of HEAD"
git merge-base --is-ancestor "$PRODUCER_SHA" HEAD && echo "391f811e7 IS an ancestor of HEAD"
echo "HEAD = $(git rev-parse HEAD)"

echo
echo "=== 9. the --follow empty-blob artifact, explained (stderr.log is 0 bytes) ==="
echo "size of stderr.log blob at $PRODUCER_SHA:"
git cat-file -s "$(git rev-parse "$PRODUCER_SHA:coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/stderr.log")"
echo "git log --all --follow for stderr.log (WILL show many unrelated commits -- known git --follow"
echo "rename-detection artifact for 0-byte files, every empty blob in history is '100% similar'):"
git log --all --follow --format='%H' -- coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/stderr.log | wc -l
echo "(count above is NOT evidence of an earlier appearance; the exact-path log in check 7 is authoritative"
echo " and returns exactly one commit, 391f811e7)"
