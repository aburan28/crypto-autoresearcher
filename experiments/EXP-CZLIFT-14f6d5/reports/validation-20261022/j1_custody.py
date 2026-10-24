#!/usr/bin/env python3
"""J1 custody check for EXP-CZLIFT-14f6d5 (TASK-20261022-a846f4).

Recomputes every recorded artifact hash from the committed snapshot
(git show <SNAP>:path), compares with the execution receipts, the ledger
archive receipt and the dispatch-queue archive blocks, checks the source and
contract hashes at the contract-freeze, run and snapshot commits, commit
ancestry, command/argv against the frozen trial plan, and trial coverage.
Usage: j1_custody.py REPO OUT_JSON
"""
import hashlib
import json
import subprocess
import sys

SNAP = "5c3cfdeef76cee2953e46697e37522daab4febda"   # snapshot named by the task card
FREEZE = "b553f64e3a4e59eaefd97cc8d2240acc11609b43"  # queue archive block, TASK-20261009-046d5b
RUNC = "08ee02a39141e74aeb9e0934e58e13254461f3e4"    # manifest code.commit / environment commit
LEDGER = "53709b0ab53decca25118b56f80986d0ed8a1fef"  # queue archive block, TASK-20261009-4ac56e
EXP = "experiments/EXP-CZLIFT-14f6d5"
RUNS = {"ladder-h1e5": "RUN-CZLIFT-ca7450", "ladder-h3e5": "RUN-CZLIFT-b1dce4"}
QUEUE = "coordination/goals/GOAL-CZLIFT-1516d5/batches/BATCH-b04e38/dispatch_queue.json"
SNAPREC = "coordination/goals/GOAL-CZLIFT-1516d5/archives/TASK-20261009-046d5b/snapshot-receipt.json"
LEDREC = "coordination/goals/GOAL-CZLIFT-1516d5/batches/BATCH-b04e38/archives/TASK-20261009-4ac56e/ledger-receipt.json"


def git(repo, *args, binary=False):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    return r.stdout if binary else r.stdout.decode(), r.returncode


def blob_sha(repo, rev, path):
    data, rc = git(repo, "show", f"{rev}:{path}", binary=True)
    return hashlib.sha256(data).hexdigest() if rc == 0 else None


def wt_sha(repo, path):
    try:
        return hashlib.sha256(open(f"{repo}/{path}", "rb").read()).hexdigest()
    except FileNotFoundError:
        return None


def main():
    repo, out = sys.argv[1], sys.argv[2]
    findings, problems = {}, []
    queue = json.loads(git(repo, "show", f"{SNAP}:{QUEUE}")[0])
    qarch = {t["id"]: t.get("archive", {}) for t in queue["tasks"]}
    snap_q, led_q = qarch["TASK-20261009-046d5b"], qarch["TASK-20261009-4ac56e"]
    if snap_q.get("commit_sha") != FREEZE or led_q.get("commit_sha") != LEDGER:
        problems.append("queue archive commit_sha differs from constants")
    snaprec = json.loads(git(repo, "show", f"{SNAP}:{SNAPREC}")[0])
    ledrec = json.loads(git(repo, "show", f"{SNAP}:{LEDREC}")[0])
    plan = json.loads(git(repo, "show", f"{SNAP}:{EXP}/trial-plan.json")[0])

    # Receipts' own hashes against the queue archive blocks
    rec = {}
    for p, blk in ((SNAPREC, snap_q), (LEDREC, led_q)):
        rec[p] = {"snapshot": blob_sha(repo, SNAP, p), "queue": blk["path_sha256"].get(p),
                  "at_archive_commit": blob_sha(repo, blk["commit_sha"], p)}
        if not (rec[p]["snapshot"] == rec[p]["queue"] == rec[p]["at_archive_commit"]):
            problems.append(f"receipt hash mismatch {p}")
    findings["archive_receipts"] = rec

    # Ancestry
    anc = {}
    for a, b in ((FREEZE, RUNC), (RUNC, LEDGER), (LEDGER, SNAP), (FREEZE, SNAP)):
        anc[f"{a[:10]} <= {b[:10]}"] = git(repo, "merge-base", "--is-ancestor", a, b)[1] == 0
    findings["ancestry"] = anc
    if not all(anc.values()):
        problems.append("ancestry")

    # Contract and source files at freeze / run / ledger / snapshot commits and working tree
    contract = [f"{EXP}/specification.yaml", f"{EXP}/trial-plan.json", f"{EXP}/implementation/run.py",
                f"{EXP}/implementation/check.py", "experiments/EXP-CZLIFT-a255fc/implementation/run.py",
                "harness/czlift_run.py"]
    csrc = {}
    for p in contract:
        row = {rev[:10]: blob_sha(repo, rev, p) for rev in (FREEZE, RUNC, LEDGER, SNAP)}
        row["worktree"] = wt_sha(repo, p)
        row["trial_plan_source_sha256"] = plan["source_sha256"].get(p)
        row["snapshot_receipt"] = snaprec["path_sha256"].get(p)
        row["queue_snapshot_block"] = snap_q["path_sha256"].get(p)
        if p.endswith("specification.yaml"):
            row["trial_plan_specification_sha256"] = plan["specification_sha256"]
        vals = {v for k, v in row.items() if v is not None}
        row["all_equal"] = len(vals) == 1
        if not row["all_equal"]:
            problems.append(f"contract/source hash disagreement {p}: {row}")
        csrc[p] = row
    findings["contract_and_sources"] = csrc

    # Run packages
    runs = {}
    for trial in plan["trials"]:
        rid = trial["run_id"]
        d = f"{EXP}/runs/{rid}"
        listed, _ = git(repo, "ls-tree", "-r", "--name-only", SNAP, d + "/")
        files = sorted(x.split("/")[-1] for x in listed.split())
        er = json.loads(git(repo, "show", f"{SNAP}:{d}/execution-receipt.json")[0])
        env = json.loads(git(repo, "show", f"{SNAP}:{d}/environment.json")[0])
        launch = json.loads(git(repo, "show", f"{SNAP}:{d}/launch.json")[0])
        cmd = json.loads(git(repo, "show", f"{SNAP}:{d}/command.txt")[0])
        rows = {}
        for f in files:
            p = f"{d}/{f}"
            row = {"snapshot": blob_sha(repo, SNAP, p), "ledger_commit": blob_sha(repo, LEDGER, p),
                   "worktree": wt_sha(repo, p), "execution_receipt": er["artifact_sha256"].get(f),
                   "ledger_receipt": ledrec["path_sha256"].get(p), "queue_ledger_block": led_q["path_sha256"].get(p)}
            vals = {v for v in row.values() if v is not None}
            row["all_equal"] = len(vals) == 1
            row["recorded_somewhere"] = any(row[k] for k in ("execution_receipt", "ledger_receipt", "queue_ledger_block"))
            if not row["all_equal"] or not row["recorded_somewhere"]:
                problems.append(f"artifact hash {p}: {row}")
            rows[f] = row
        unlisted = sorted(set(files) - set(er["artifact_sha256"]) - {"execution-receipt.json"})
        missing = sorted(set(er["artifact_sha256"]) - set(files))
        required = ["manifest.yaml", "raw-result.json", "command.txt", "environment.json", "stdout.log", "stderr.log"]
        req_missing = [r for r in required if r not in files]
        expect_argv = [a.replace("{run_dir}", f"/home/user/crypto-autoresearcher/{d}") for a in trial["argv"]]
        expect_check = [a.replace("{run_dir}", f"/home/user/crypto-autoresearcher/{d}") for a in trial["check_argv"]]
        plan_sha = blob_sha(repo, SNAP, f"{EXP}/trial-plan.json")
        runs[rid] = {
            "trial_id": trial["id"], "files": files, "hashes": rows,
            "files_not_in_execution_receipt": unlisted, "receipt_entries_without_file": missing,
            "required_artifacts_missing": req_missing,
            "command_equals_plan_argv": cmd == expect_argv, "launch_argv_equals_plan": launch["argv"] == expect_argv,
            "launch_check_argv_equals_plan": launch["check_argv"] == expect_check,
            "receipt_trial_id": er["trial_id"], "launch_trial_id": launch["trial_id"],
            "receipt_status": er["status"], "returncode": er["returncode"], "check_returncode": er["check_returncode"],
            "plan_sha256_in_receipt": er["plan_sha256"], "plan_sha256_in_launch": launch["plan_sha256"],
            "plan_sha256_recomputed": plan_sha,
            "environment_commit": env["commit"], "environment_spec_sha256": env["specification_sha256"],
            "environment_source_sha256_matches_plan": all(
                env["source_sha256"].get(k) == v for k, v in plan["source_sha256"].items()),
            "authority_commit": er["authority"]["commit"],
        }
        for k in ("command_equals_plan_argv", "launch_argv_equals_plan", "launch_check_argv_equals_plan"):
            if not runs[rid][k]:
                problems.append(f"{rid} {k}")
        if er["trial_id"] != trial["id"] or launch["trial_id"] != trial["id"]:
            problems.append(f"{rid} trial id")
        if er["plan_sha256"] != plan_sha or launch["plan_sha256"] != plan_sha:
            problems.append(f"{rid} plan sha")
        if env["commit"] != RUNC or er["authority"]["commit"] != RUNC:
            problems.append(f"{rid} commit")
        if unlisted or missing or req_missing:
            problems.append(f"{rid} unlisted/missing {unlisted} {missing} {req_missing}")
    findings["runs"] = runs
    run_dirs, _ = git(repo, "ls-tree", "--name-only", SNAP, f"{EXP}/runs/")
    findings["run_dirs_at_snapshot"] = run_dirs.split()
    extra = [x for x in run_dirs.split() if x.split("/")[-1] not in set(RUNS.values()) | {".gitkeep"}]
    findings["unplanned_run_dirs"] = extra
    if extra:
        problems.append(f"unplanned run dirs {extra}")
    findings["problems"] = problems
    json.dump(findings, open(out, "w"), indent=1)
    print(json.dumps({"problems": problems, "ancestry": anc,
                      "contract_all_equal": {k: v["all_equal"] for k, v in csrc.items()},
                      "runs": {k: {kk: vv for kk, vv in v.items() if kk not in ("hashes",)} for k, v in runs.items()},
                      "unplanned_run_dirs": extra}, indent=1))


if __name__ == "__main__":
    main()
