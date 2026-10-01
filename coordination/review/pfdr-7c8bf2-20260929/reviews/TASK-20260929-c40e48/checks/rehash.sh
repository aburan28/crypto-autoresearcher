#!/usr/bin/env bash
# TASK-20260929-c40e48 J1: re-hash the committed run package at 1a037688c.
# Run ONLY after the J2 section of validation-report.yaml is written (RV-2).
# Usage: rehash.sh <detached worktree at 1a037688c> <python>
set -u
WT="$1"; PY="$2"
RUN=experiments/EXP-PFDR-7c8bf2/runs/RUN-PFDR-7c8bf2-stage0
REC=coordination/design/TASK-20260928-102217/archives/TASK-20260928-f15632/snapshot-receipt.json
cd "$WT" || exit 2
echo "== HEAD and cleanliness"
git rev-parse HEAD
git status --porcelain --untracked-files=all | sed 's/^/DIRTY /'
echo "== files in run dir (working tree) vs files in git tree at 1a037688c"
find "$RUN" -type f | sort
git ls-tree -r --name-only 1a037688c -- "$RUN" | sort
echo "== sha256 of every run-dir file, worktree bytes and git-object bytes"
for f in $(git ls-tree -r --name-only 1a037688c -- "$RUN" experiments/EXP-PFDR-7c8bf2/analyze_floor.py experiments/EXP-PFDR-7c8bf2/execution-report.yaml | sort); do
  wt=$(sha256sum "$f" | cut -c1-64); go=$(git show "1a037688c:$f" | sha256sum | cut -c1-64)
  echo "$wt $go $f"
done
echo "== checksums.sha256 verification (sha256sum -c, run from the run dir)"
(cd "$RUN" && sha256sum -c checksums.sha256)
echo "== receipt path_sha256 comparison for the Stage 0 package"
"$PY" - "$REC" <<'EOF'
import hashlib, json, subprocess, sys
rec = json.load(open(sys.argv[1]))
ps = rec["path_sha256"]
bad = 0
n = 0
for p, h in sorted(ps.items()):
    if "EXP-PFDR-7c8bf2" not in p:
        continue
    n += 1
    blob = subprocess.run(["git", "show", f"1a037688c:{p}"], capture_output=True, check=True).stdout
    got = hashlib.sha256(blob).hexdigest()
    ok = got == h
    bad += not ok
    print(("OK  " if ok else "BAD ") + p)
print(f"receipt entries for EXP-PFDR-7c8bf2: {n}; mismatches: {bad}")
EOF
