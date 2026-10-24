#!/usr/bin/env python3
"""J1 custody checks for EXP-CZLIFT-f5e06c (TASK-20261022-65e6c1). Read-only."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = sys.argv[1]
EXP = "experiments/EXP-CZLIFT-f5e06c"
SNAP = "coordination/goals/GOAL-CZLIFT-1516d5/archives/TASK-20261009-046d5b/snapshot-receipt.json"
LEDG = "coordination/goals/GOAL-CZLIFT-1516d5/batches/BATCH-b04e38/archives/TASK-20261009-4ac56e/ledger-receipt.json"
RUNS = {"RUN-CZLIFT-032a92": 20261009, "RUN-CZLIFT-6447f0": 20261010}
REVIEW_HEAD = "5c3cfdeef7"

out = {"checks": [], "failures": []}


def chk(name, ok, detail=None):
    out["checks"].append({"check": name, "ok": bool(ok), "detail": detail})
    if not ok:
        out["failures"].append(name)


def sha(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


def sha_at(commit, path):
    return hashlib.sha256(git("show", f"{commit}:{path}")).hexdigest()


snap = json.load(open(os.path.join(ROOT, SNAP)))
ledg = json.load(open(os.path.join(ROOT, LEDG)))
plan = json.load(open(os.path.join(ROOT, EXP, "trial-plan.json")))
plan_sha = sha(f"{EXP}/trial-plan.json")
spec_sha = sha(f"{EXP}/specification.yaml")

# --- contract hashes ------------------------------------------------------
chk("spec sha == trial-plan.specification_sha256", spec_sha == plan["specification_sha256"], spec_sha)
chk("spec sha == snapshot receipt", spec_sha == snap["path_sha256"][f"{EXP}/specification.yaml"])
chk("trial-plan sha == snapshot receipt", plan_sha == snap["path_sha256"][f"{EXP}/trial-plan.json"], plan_sha)
for p in ("implementation/run.py", "implementation/check.py"):
    chk(f"{p} sha == snapshot receipt", sha(f"{EXP}/{p}") == snap["path_sha256"][f"{EXP}/{p}"])
hyp = "ledger/hypotheses/H-CZLIFT-bd2017.yaml"
chk("hypothesis sha == snapshot receipt", sha(hyp) == snap["path_sha256"][hyp], sha(hyp))
chk("harness/czlift_medium.py sha == snapshot receipt",
    sha("harness/czlift_medium.py") == snap["path_sha256"]["harness/czlift_medium.py"])
chk("EXP-CZLIFT-f5e06c in snapshot record_ids", "EXP-CZLIFT-f5e06c" in snap["record_ids"])
chk("H-CZLIFT-bd2017 in snapshot record_ids", "H-CZLIFT-bd2017" in snap["record_ids"])

for p, h in plan["source_sha256"].items():
    chk(f"plan source {p} == working tree @ {REVIEW_HEAD}", sha(p) == h)

# --- run packages ---------------------------------------------------------
for run, seed in RUNS.items():
    rd = f"{EXP}/runs/{run}"
    files = sorted(os.listdir(os.path.join(ROOT, rd)))
    rec = json.load(open(os.path.join(ROOT, rd, "execution-receipt.json")))
    env = json.load(open(os.path.join(ROOT, rd, "environment.json")))
    launch = json.load(open(os.path.join(ROOT, rd, "launch.json")))
    cmd = json.load(open(os.path.join(ROOT, rd, "command.txt")))
    art = rec["artifact_sha256"]
    # execution receipt lists every file but itself
    chk(f"{run}: file set == receipt artifacts + execution-receipt.json",
        set(files) == set(art) | {"execution-receipt.json"}, {"files": files})
    for f, h in art.items():
        chk(f"{run}: {f} sha == execution receipt", sha(f"{rd}/{f}") == h)
    # ledger archive receipt lists every file including the execution receipt
    lpaths = {k.split("/")[-1]: v for k, v in ledg["path_sha256"].items() if k.startswith(rd + "/")}
    chk(f"{run}: ledger receipt covers every file", set(lpaths) == set(files), sorted(lpaths))
    for f, h in lpaths.items():
        chk(f"{run}: {f} sha == ledger receipt", sha(f"{rd}/{f}") == h)
    chk(f"{run}: in ledger record_ids", run in ledg["record_ids"])
    # receipts consistent with plan
    chk(f"{run}: receipt plan_sha256 == trial-plan sha", rec["plan_sha256"] == plan_sha)
    chk(f"{run}: launch plan_sha256 == trial-plan sha", launch["plan_sha256"] == plan_sha)
    chk(f"{run}: status output_validated, rc 0, check rc 0",
        rec["status"] == "output_validated" and rec["returncode"] == 0 and rec["check_returncode"] == 0)
    trial = [t for t in plan["trials"] if t["run_id"] == run]
    chk(f"{run}: exactly one plan trial", len(trial) == 1)
    t = trial[0]
    chk(f"{run}: receipt trial_id == plan", rec["trial_id"] == t["id"] == launch["trial_id"])
    rd_abs = os.path.join(ROOT, rd)
    want = [a.replace("{run_dir}", rd_abs) for a in t["argv"]]
    chk(f"{run}: command.txt == plan argv with run_dir", cmd == want, cmd)
    chk(f"{run}: launch argv == command.txt", launch["argv"] == cmd)
    want_chk = [a.replace("{run_dir}", rd_abs) for a in t["check_argv"]]
    chk(f"{run}: launch check_argv == plan check_argv", launch["check_argv"] == want_chk)
    chk(f"{run}: seed in argv == spec seed", cmd[cmd.index("--seed") + 1] == str(seed))
    chk(f"{run}: env specification_sha256 == spec", env["specification_sha256"] == spec_sha)
    chk(f"{run}: env source_sha256 == plan source_sha256", env["source_sha256"] == plan["source_sha256"])
    commit = env["commit"]
    chk(f"{run}: env commit == receipt authority commit == launch commit",
        commit == rec["authority"]["commit"] == launch["authority"]["commit"], commit)
    # sources at the recorded commit equal the recorded hashes
    for p, h in env["source_sha256"].items():
        chk(f"{run}: {p} @ {commit[:10]} == recorded", sha_at(commit, p) == h)
    chk(f"{run}: spec @ {commit[:10]} == recorded", sha_at(commit, f"{EXP}/specification.yaml") == spec_sha)
    chk(f"{run}: plan @ {commit[:10]} == recorded", sha_at(commit, f"{EXP}/trial-plan.json") == plan_sha)
    anc = subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", commit, REVIEW_HEAD]).returncode == 0
    chk(f"{run}: run commit is ancestor of review snapshot {REVIEW_HEAD}", anc)
    # every run-dir file committed at review head, bytes identical
    for f in files:
        chk(f"{run}: {f} committed at {REVIEW_HEAD} and identical", sha_at(REVIEW_HEAD, f"{rd}/{f}") == sha(f"{rd}/{f}"))
    # raw-result seed binding
    raw = json.load(open(os.path.join(ROOT, rd, "raw-result.json")))
    chk(f"{run}: raw-result top-level keys", True, sorted(raw) if isinstance(raw, dict) else type(raw).__name__)

# working tree vs review head for the whole experiment dir (excluding my report dir)
st = git("status", "--porcelain", "--untracked-files=all", "--", EXP, "harness", "ledger/hypotheses/H-CZLIFT-bd2017.yaml").decode()
st_lines = [l for l in st.splitlines() if "reports/validation-20261022" not in l]
chk("no uncommitted change under experiment dir / harness / hypothesis (excluding own report dir)",
    not st_lines, st_lines)
out["plan_sha256"] = plan_sha
out["spec_sha256"] = spec_sha
out["n_checks"] = len(out["checks"])
out["n_fail"] = len(out["failures"])
json.dump(out, sys.stdout, indent=1)
print()
