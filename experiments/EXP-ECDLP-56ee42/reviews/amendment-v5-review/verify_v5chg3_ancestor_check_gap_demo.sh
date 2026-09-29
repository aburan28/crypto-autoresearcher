#!/usr/bin/env bash
# Independent re-demonstration (not a copy of the amendment-v4-review's own
# change7_ancestor_check_gap_demo.sh, built fresh) of: (1) V4-CHG-7's
# git merge-base --is-ancestor check alone cannot distinguish a wrong-but-
# real ancestor commit (no artifact at all) from the correct one; (2)
# V5-CHG-3's added git show <sha>:<path> | sha256sum content check DOES
# reject the wrong commit, because the path does not even exist in its tree.
set -euo pipefail
WORK="$(mktemp -d)"
cd "$WORK"
git init -q
git config user.email "test@test.local"
git config user.name "test"

echo "unrelated content" > unrelated.txt
git add unrelated.txt
git commit -qm "A: unrelated initial commit, NO power-check artifact"
SHA_A=$(git rev-parse HEAD)

echo "more unrelated" > unrelated2.txt
git add unrelated2.txt
git commit -qm "B: unrelated second commit, still no artifact"

mkdir -p reviews
echo "regime_decision: BLOCKING" > reviews/power_check_results.yaml
git add reviews/power_check_results.yaml
git commit -qm "C: the REAL power-check-artifact commit"
SHA_C=$(git rev-parse HEAD)

echo "task card work" > taskcard.txt
git add taskcard.txt
git commit -qm "D: later calibration-run task-card HEAD"
SHA_D=$(git rev-parse HEAD)

echo "=== V4-CHG-7 ancestry check alone ==="
echo "-- citing CORRECT sha C --"
git merge-base --is-ancestor "$SHA_C" "$SHA_D" && echo "exit 0 (PASS)" || echo "exit nonzero (FAIL)"
echo "-- citing WRONG-but-still-ancestor sha A (no artifact at all) --"
git merge-base --is-ancestor "$SHA_A" "$SHA_D" && echo "exit 0 (PASS -- SAME as correct C!)" || echo "exit nonzero (FAIL)"

echo
echo "=== V5-CHG-3 added content check: git show <sha>:<path> | sha256sum ==="
echo "-- content hash at the CORRECT sha C --"
git show "$SHA_C":reviews/power_check_results.yaml | sha256sum
echo "-- attempting content hash at the WRONG sha A (no such path) --"
set +e
git show "$SHA_A":reviews/power_check_results.yaml 2>&1
RC=$?
set -e
echo "exit code: $RC"

rm -rf "$WORK"
echo
echo "CONCLUSION: the ancestry check alone cannot distinguish sha A from sha"
echo "C (both PASS identically, independently re-confirmed). V5-CHG-3's"
echo "content check correctly rejects sha A: git show fails outright"
echo "(path does not exist in that tree), so the COMBINED check (both"
echo "required, per V5-CHG-3's own text) closes exactly the gap the"
echo "amendment-v4-review demonstrated."
