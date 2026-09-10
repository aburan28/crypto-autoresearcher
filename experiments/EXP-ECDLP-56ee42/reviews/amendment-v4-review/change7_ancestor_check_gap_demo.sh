#!/usr/bin/env bash
# Independent demonstration of V4-CHG-7's git merge-base --is-ancestor
# mechanism's soundness gap: it verifies DAG REACHABILITY of the cited
# power_check_ancestor_commit_sha, never its CONTENT or IDENTITY. Any
# earlier commit on the same history -- including one that has nothing to
# do with the power check and contains no power_check_results.yaml at all --
# passes the check with exit code 0.
#
# This directly inverts this program's OWN established archive-receipt
# discipline (CLAUDE.md "Archive receipts bind to CONTENT first":
# tools/research_dispatch.py verifies path_sha256 as primary and treats
# commit reachability as merely advisory).
#
# Run in a scratch directory; creates and destroys its own throwaway git repo.
set -e
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
git init -q
git config user.email "review@test.local"
git config user.name "amendment-v4-review"

echo "init" > README.md
git add README.md
git commit -qm "commit A: unrelated initial commit, NO power-check artifact"
UNRELATED_SHA=$(git rev-parse HEAD)

echo "wrong_data" > other_file.txt
git add other_file.txt
git commit -qm "commit B: some other unrelated work, still no power-check artifact"

echo "real power_check_results.yaml content (20/20 unanimity, all seeds recorded)" > power_check_results.yaml
git add power_check_results.yaml
git commit -qm "commit C: THE REAL power-check artifact commit"
REAL_SHA=$(git rev-parse HEAD)

echo "later work" > later.txt
git add later.txt
git commit -qm "commit D: calibration-run task-card branch HEAD"
HEAD_SHA=$(git rev-parse HEAD)

echo "=== Scenario 1: correct sha cited (should pass, and rightly does) ==="
if git merge-base --is-ancestor "$REAL_SHA" "$HEAD_SHA"; then
  echo "PASS (exit 0): $REAL_SHA is an ancestor of $HEAD_SHA -- correct citation, correctly accepted."
fi

echo ""
echo "=== Scenario 2: WRONG-but-still-ancestor sha cited (THE GAP) ==="
if git merge-base --is-ancestor "$UNRELATED_SHA" "$HEAD_SHA"; then
  echo "PASS (exit 0): $UNRELATED_SHA is ALSO accepted as an ancestor,"
  echo "but this commit contains NO power_check_results.yaml at all:"
fi
git show "$UNRELATED_SHA":power_check_results.yaml 2>&1 | sed 's/^/    /' || true

echo ""
echo "=== Conclusion ==="
echo "git merge-base --is-ancestor checks DAG reachability only. It never"
echo "inspects file existence or content at the cited sha. A task card"
echo "author who cites ANY earlier ancestor commit (a typo, a stale"
echo "copy-paste, or a wrong-but-plausible-looking sha from the same"
echo "branch's history) passes V4-CHG-7's 'mechanical' check exactly as"
echo "cleanly as the correct citation would -- exit code 0 either way."

rm -rf "$WORKDIR"
