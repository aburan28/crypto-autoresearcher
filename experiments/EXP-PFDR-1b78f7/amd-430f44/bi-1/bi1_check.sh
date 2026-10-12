#!/usr/bin/env bash
# BI-1 (AMD-20260929-430f44 M-3) build-identity check, TASK-20260929-89c123.
# For every file pinned in RUN-PFDR-1b78f7-census-m4 attempt-1 execution.json
# source_sha256 (summarize_run.py: the DEV-4 hash 68165e09... governs), and for
# every results/ file, README.md and __init__.py (card CODE constraint), compare
#   (1) the working-tree sha256, (2) the recorded pin, (3) sha256 of `git show dc61c5e1e:<path>`,
# and report the git working-tree status of each file. Prints TSV; exit 1 on any mismatch.
set -u
REPO=/home/user/crypto-autoresearcher
PY=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python
cd "$REPO"
"$PY" - <<'PYEOF'
import hashlib, json, subprocess, sys, os
REPO = "/home/user/crypto-autoresearcher"
ex = json.load(open("experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-census-m4/execution.json"))
pins = {k: v["sha256"] for k, v in ex["source_sha256"].items()}
pins["experiments/EXP-PFDR-1b78f7/amd-1de84f/summarize_run.py"] = "68165e094c51f90c2aafd4e51510f414622b53b2145a0af6c279c32af93f5e68"
extra = {
 "src/crypto_autoresearcher/index_calculus/README.md": "01fdffe4b594d16abd7f73c0b2d7ee3c8898cfb2f6f3a0515f7387af217993b4",
 "src/crypto_autoresearcher/index_calculus/results/engines-20260924.jsonl.gz": "85e7d1cb6e6e7ddde52fa4d819b6b08e311e0bb9fb540572f6629842cdecb521",
 "src/crypto_autoresearcher/index_calculus/results/sweep-20260924.jsonl.gz": "57cf3f72f0b0e4f166a93f2204c3f039e9470f067774063fc2ec34582f8de6ca",
 "src/crypto_autoresearcher/index_calculus/results/sweep-arity-20260926.jsonl.gz": "e1e3cf0f3509ff098162e16e8eb3014d7059ad4f2a6d9835237691dc0a1479b2",
 "src/crypto_autoresearcher/index_calculus/results/sweep-arity-minfill-20260926.jsonl.gz": "a0fd55609a86a3d7f6aac7efd2b2f875a7dca0c0911f46728da63947ff9f041f",
 "src/crypto_autoresearcher/index_calculus/results/sweep-arity67-20260928.jsonl.gz": "a1dd28f57d35e632b81256ad46e97e8cdc208a594d5b76bd81e2b7688ef724d5",
 "src/crypto_autoresearcher/index_calculus/results/sweep-minfill-20260926.jsonl.gz": "fbf2e63698698841b0831159fc497dde834c166e2423c218722f4fd128c5d7c5",
 "src/crypto_autoresearcher/index_calculus/results/sweep-mitm-20260926.jsonl.gz": "5f3474158b2dc6dc866f5588ea19e4fec349a7fa178336c49cd172c8a9539931",
 "experiments/EXP-PFDR-1b78f7/amd-1de84f/function-diff.json": "a3192738d0866c3752870851ad97a0e9a610acdb1fb459d9198c43f10f2b6550",
 "experiments/EXP-PFDR-1b78f7/amd-1de84f/source.diff": "6c4c73b90e48374aad8213818a99c3364973dd4349d8a1d67ab4d93934ce7ab7",
}
res_dir = "src/crypto_autoresearcher/index_calculus/results"
listed = sorted(os.listdir(res_dir))
allp = dict(pins); allp.update(extra)
bad = 0
print("path\tsource\tworking_tree_sha256\tpin_sha256\tdc61c5e1e_sha256\tgit_status\tresult")
for rel in sorted(allp):
    wt = hashlib.sha256(open(rel, "rb").read()).hexdigest()
    r = subprocess.run(["git", "show", f"dc61c5e1e:{rel}"], capture_output=True)
    gs = hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else "MISSING"
    st = subprocess.run(["git", "status", "--porcelain", "--", rel], capture_output=True, text=True).stdout.strip() or "clean"
    ok = wt == allp[rel] == gs and st == "clean"
    bad += not ok
    src = "R11 attempt-1 execution.json source_sha256" if rel in pins else "implementation-notes-amd1de84f pin"
    if rel.endswith("summarize_run.py"): src = "DEV-4 hash (AMD-20260929-430f44 M-3)"
    print(f"{rel}\t{src}\t{wt}\t{allp[rel]}\t{gs}\t{st}\t{'PASS' if ok else 'FAIL'}")
print(f"# results/ directory listing: {listed}")
print(f"# results/ files checked == listing: {sorted(p.split('/')[-1] for p in extra if p.startswith(res_dir)) == listed}")
print(f"# files: {len(allp)}  failures: {bad}  BI-1: {'PASS' if bad == 0 else 'FAIL'}")
sys.exit(1 if bad else 0)
PYEOF
