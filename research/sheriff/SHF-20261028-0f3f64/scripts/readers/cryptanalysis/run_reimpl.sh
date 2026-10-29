#!/usr/bin/env bash
# Recover the two off-disk runs.jsonl files from git history (they became artifact-store pointers in
# cryptanalysis 5569ba6e), verify them against the committed hashes, and run the independent
# re-implementation. Executes no code from the audited clone; reads it with git only.
set -euo pipefail
CLONE=${CLONE:-/home/user/cryptanalysis}
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${WORK:-$(mktemp -d)}
OUT=${OUT:-$HERE/out}
EXP=experiments/koblitz-n83-opcounts-20261023
ARCH=experiments/koblitz-n83-stacked-20261016/run_github_38862448935/panel
git -C "$CLONE" show 5a6c233e:$EXP/run_github_39882571652/panel/runs.jsonl > "$WORK/opcounts_runs.jsonl"
git -C "$CLONE" show 5569ba6e^:$ARCH/runs.jsonl > "$WORK/stacked_runs.jsonl"
want_new=$(awk '$2=="./panel/runs.jsonl"{print $1}' "$CLONE/$EXP/run_github_39882571652/SHA256SUMS")
want_ptr=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["files"]["runs.jsonl"]["sha256"])' "$CLONE/$EXP/run_github_39882571652/panel/.artifacts.json")
want_arch=$(git -C "$CLONE" show HEAD:$ARCH/.artifacts.json | python3 -I -c 'import json,sys; print(json.load(sys.stdin)["files"]["runs.jsonl"]["sha256"])')
got_new=$(sha256sum "$WORK/opcounts_runs.jsonl" | cut -d' ' -f1)
got_arch=$(sha256sum "$WORK/stacked_runs.jsonl" | cut -d' ' -f1)
echo "opcounts runs.jsonl: got $got_new SHA256SUMS $want_new pointer $want_ptr"
echo "stacked runs.jsonl:  got $got_arch pointer $want_arch"
[ "$got_new" = "$want_new" ] && [ "$got_new" = "$want_ptr" ] && [ "$got_arch" = "$want_arch" ] || { echo "HASH MISMATCH"; exit 1; }
cd "$WORK"
python3 -I "$HERE/reimpl_analyze.py" --clone "$CLONE" --runs-jsonl "$WORK/opcounts_runs.jsonl" \
  --archive-runs-jsonl "$WORK/stacked_runs.jsonl" --out "$OUT"
