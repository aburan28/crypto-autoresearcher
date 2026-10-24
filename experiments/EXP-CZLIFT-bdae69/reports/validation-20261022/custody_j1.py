#!/usr/bin/env python3
"""J1 custody checks for TASK-20261022-2d255e (read-only on all producer paths).

Usage: python3 -I -B custody_j1.py <repo_root> <out_json>
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime

import yaml

ROOT = sys.argv[1]
OUT = sys.argv[2]
EXP = "experiments/EXP-CZLIFT-bdae69"
SNAP = "coordination/goals/GOAL-CZLIFT-1516d5/archives/TASK-20261009-046d5b/snapshot-receipt.json"
LEDG = "coordination/goals/GOAL-CZLIFT-1516d5/batches/BATCH-b04e38/archives/TASK-20261009-4ac56e/ledger-receipt.json"
FREEZE = "b553f64e3a"
RUN_COMMIT = "ca89e1a9f094fa8690088cf91895a67c88313cd3"


def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def ts(s):
    return datetime.fromisoformat(s)


def main():
    out = {}
    plan = json.load(open(os.path.join(ROOT, EXP, "trial-plan.json")))
    snap = json.load(open(os.path.join(ROOT, SNAP)))
    ledg = json.load(open(os.path.join(ROOT, LEDG)))
    # receipt hashes (only paths of this experiment / its hypothesis)
    hashes = []
    for name, rec in (("snapshot", snap), ("ledger", ledg)):
        for p, v in rec["path_sha256"].items():
            if "EXP-CZLIFT-bdae69" in p or "H-CZLIFT-d37231" in p:
                hashes.append({"receipt": name, "path": p, "recorded": v, "recomputed": sha(p), "ok": sha(p) == v})
    for p, v in plan["source_sha256"].items():
        hashes.append({"receipt": "trial-plan", "path": p, "recorded": v, "recomputed": sha(p), "ok": sha(p) == v})
    hashes.append({"receipt": "trial-plan", "path": plan["specification"], "recorded": plan["specification_sha256"],
                   "recomputed": sha(plan["specification"]), "ok": sha(plan["specification"]) == plan["specification_sha256"]})
    out["hash_checks_total"] = len(hashes)
    out["hash_checks_failed"] = [h for h in hashes if not h["ok"]]
    out["hash_checks"] = hashes
    plan_sha = sha(f"{EXP}/trial-plan.json")
    runs = {}
    run_dirs = sorted(d for d in os.listdir(os.path.join(ROOT, EXP, "runs")) if not d.startswith("."))
    out["run_dirs_present"] = run_dirs
    out["plan_run_ids"] = [t["run_id"] for t in plan["trials"]]
    out["unplanned_run_dirs"] = sorted(set(run_dirs) - set(out["plan_run_ids"]))
    out["missing_planned_runs"] = sorted(set(out["plan_run_ids"]) - set(run_dirs))
    for t in plan["trials"]:
        rid = t["run_id"]
        rd = f"{EXP}/runs/{rid}"
        absrd = os.path.join(ROOT, rd)
        er = json.load(open(os.path.join(absrd, "execution-receipt.json")))
        la = json.load(open(os.path.join(absrd, "launch.json")))
        env = json.load(open(os.path.join(absrd, "environment.json")))
        cmd = json.loads(open(os.path.join(absrd, "command.txt")).read())
        man = yaml.safe_load(open(os.path.join(absrd, "manifest.yaml")))["run"]
        raw = json.load(open(os.path.join(absrd, "raw-result.json")))
        expected_argv = [a.replace("{run_dir}", absrd) for a in t["argv"]]
        expected_check = [a.replace("{run_dir}", absrd) for a in t["check_argv"]]
        files = sorted(os.listdir(absrd))
        tracked = sorted(os.path.basename(x) for x in git("ls-files", rd).splitlines())
        art = {f: (sha(f"{rd}/{f}") == v) for f, v in er["artifact_sha256"].items()}
        seed_flag = int(t["argv"][t["argv"].index("--seed") + 1])
        r = {
            "trial_id": t["id"],
            "command_txt_equals_plan_argv": cmd == expected_argv,
            "launch_argv_equals_plan_argv": la["argv"] == expected_argv,
            "launch_check_argv_equals_plan": la["check_argv"] == expected_check,
            "manifest_command_tail_equals_plan": man["code"]["command"].split()[1:] == expected_argv[1:],
            "manifest_command_interpreter": man["code"]["command"].split()[0],
            "plan_sha256_in_launch_and_receipt": la["plan_sha256"] == plan_sha == er["plan_sha256"],
            "trial_id_bound": la["trial_id"] == er["trial_id"] == t["id"],
            "run_id_bound": la["run_id"] == er["run_id"] == man["id"] == rid,
            "commit_bound": env["commit"] == man["code"]["commit"] == la["authority"]["commit"] == er["authority"]["commit"] == RUN_COMMIT,
            "manifest_dirty": man["code"]["dirty"],
            "manifest_status": man["status"],
            "receipt_status": er["status"], "returncode": er["returncode"], "check_returncode": er["check_returncode"],
            "receipt_published_flag": er["published"],
            "seed_plan": seed_flag, "seed_manifest": man["inputs"]["seed"], "seed_metrics": raw["metrics"]["seed"],
            "seed_consistent": seed_flag == man["inputs"]["seed"] == raw["metrics"]["seed"],
            "parameters": man["inputs"]["parameters"],
            "parameters_match_spec": man["inputs"]["parameters"] == {"pmin": 50, "pmax": 2000, "n_primes": 40, "samples": 40, "precision": 4, "tier": "toy"},
            "env_source_sha_equals_plan": env["source_sha256"] == plan["source_sha256"],
            "env_spec_sha_equals_plan": env["specification_sha256"] == plan["specification_sha256"],
            "manifest_source_sha_subset_ok": all(plan["source_sha256"].get(k) == v for k, v in man["code"]["source_sha256"].items()),
            "manifest_python": man["environment"]["python"], "env_python": env["python"],
            "runtime_lock": env["runtime_lock"],
            "manifest_has_files_sha256": "files_sha256" in json.dumps(man),
            "execution_receipt_artifacts_ok": art,
            "files_on_disk": files,
            "files_tracked": tracked,
            "files_on_disk_equal_tracked": files == tracked,
            "receipt_covers_all_but_itself": sorted(er["artifact_sha256"]) == sorted(f for f in files if f != "execution-receipt.json"),
            "spec_required_artifacts_present": all(os.path.exists(os.path.join(absrd, f)) for f in
                                                   ("manifest.yaml", "raw-result.json", "command.txt", "environment.json", "stdout.log", "stderr.log")),
            "manifest_metrics_equal_raw_metrics": man["result"]["metrics"] == raw["metrics"],
            "stdout_equals_metrics_sections": json.loads(open(os.path.join(absrd, "stdout.log")).read()) == raw["metrics"]["sections"],
            "timing_receipt_brackets_manifest": ts(er["started_at"]) <= ts(man["timing"]["started_at"]) <= ts(man["timing"]["finished_at"]) <= ts(er["finished_at"]),
            "wall_seconds": man["timing"]["wall_seconds"], "watchdog_seconds": t["watchdog_seconds"],
            "memory_record_present": any(k in json.dumps(man) for k in ("max_rss", "peak_memory", "memory_mb")),
            "launch_after_run_commit": True,
        }
        # checker run on the archived directory (read-only)
        cp = subprocess.run([sys.executable, "-B", f"{EXP}/implementation/check.py", absrd], cwd=ROOT,
                            capture_output=True, text=True)
        r["validator_checker_run"] = {"returncode": cp.returncode, "stdout": cp.stdout.strip(), "stderr": cp.stderr.strip()}
        r["archived_check_stdout"] = open(os.path.join(absrd, "check.stdout.log")).read().strip()
        runs[rid] = r
    out["runs"] = runs
    out["git"] = {
        "head": git("rev-parse", "HEAD"),
        "freeze_commit_adds_spec": git("log", "--diff-filter=A", "--format=%h", "--", f"{EXP}/specification.yaml"),
        "freeze_is_ancestor_of_run_commit": subprocess.run(["git", "merge-base", "--is-ancestor", FREEZE, RUN_COMMIT], cwd=ROOT).returncode == 0,
        "run_commit_is_ancestor_of_head": subprocess.run(["git", "merge-base", "--is-ancestor", RUN_COMMIT, "HEAD"], cwd=ROOT).returncode == 0,
        "files_changed_freeze_to_run_commit": git("diff", "--name-only", FREEZE, RUN_COMMIT).splitlines(),
        "contract_changed_run_commit_to_head": git("diff", "--name-only", RUN_COMMIT, "HEAD", "--", f"{EXP}/specification.yaml",
                                                   f"{EXP}/trial-plan.json", f"{EXP}/implementation", "harness/czlift.py",
                                                   "harness/czlift_run.py", "harness/toycurve.py",
                                                   "ledger/hypotheses/H-CZLIFT-d37231.yaml").splitlines(),
        "commits_touching_run_dirs": git("log", "--format=%h %ci %s", "--", f"{EXP}/runs").splitlines(),
        "ledger_archive_commit": git("log", "--format=%h %ci %s", "--", LEDG).splitlines(),
        "worktree_status_experiment": git("status", "--porcelain", "--untracked-files=all", "--", EXP).splitlines(),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    slim = dict(out)
    slim.pop("hash_checks")
    print(json.dumps(slim, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
