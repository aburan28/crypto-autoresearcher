#!/usr/bin/env python3
"""Assemble RESULTS.json for TASK-20260802-9dcca8 from the immutable run outputs.
Reads runs/run_ledger.jsonl and runs/<name>.json. Records only measured values.
"""
import json, os, subprocess, glob, hashlib, sys

D = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/crypto-autoresearcher"

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=REPO).stdout.strip()

ledger = []
with open(os.path.join(D, "runs/run_ledger.jsonl")) as f:
    for line in f:
        line = line.strip()
        if line:
            ledger.append(json.loads(line))

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

arms = {}
for e in ledger:
    if "run" not in e:
        continue
    name = e["run"]
    rec = dict(e)
    p = os.path.join(D, "runs", name + ".json")
    rec["parsed"] = None
    if e.get("status") == "completed" and os.path.exists(p) and os.path.getsize(p) > 0:
        try:
            rec["parsed"] = json.load(open(p))
        except Exception as ex:
            rec["parse_error"] = str(ex)
    # last write wins for a re-run name, but names are unique here
    arms[name] = rec

def diag_rows(name, rec):  # noqa
    out = []
    d = rec.get("parsed")
    if not d:
        return out
    for x in d["diagonals"]:
        out.append({
            "run": name,
            "mode": d["mode"],
            "rounds": d["rounds"],
            "seed": d["seed"],
            "hint_key": d["hint_key"],
            "nwrong_requested": d["nwrong_requested"],
            "segment": rec.get("segment", 1),
            "machine_conditions": rec.get("machine", "contended: up to 3 producer tasks on 4 cores, load average 12 measured at 17:31:18Z"),
            "threads": rec.get("threads", 4),
            "hint_bytes_actually_differing_from_true": x["hint_bytes_actually_differing"],
            "diagonal": x["d"],
            "survivor_count": x["survivor_count"],
            "survivors": x["survivors"],
            "true_byte": x["true_byte"],
            "hintkey_byte": x["hintkey_byte"],
            "unique_survivor": bool(x["unique"]),
            "unique_survivor_is_true_byte": bool(x["unique_survivor_is_true_byte"]),
            "unique_survivor_is_hintkey_byte": bool(x["unique_survivor_is_hintkey_byte"]),
            "true_byte_among_survivors": bool(x["true_byte_among_survivors"]),
            "hintkey_byte_among_survivors": bool(x["hintkey_byte_among_survivors"]),
        })
    return out

rows = []
for name, rec in arms.items():
    rows.extend(diag_rows(name, rec))

def summarise(pred):
    sel = [r for r in rows if pred(r)]
    return {
        "diagonals_measured": len(sel),
        "survivor_count_histogram": {str(k): sum(1 for r in sel if r["survivor_count"] == k)
                                     for k in sorted(set(r["survivor_count"] for r in sel))},
        "diagonals_with_unique_survivor": sum(1 for r in sel if r["unique_survivor"]),
        "diagonals_unique_and_equal_true_byte": sum(1 for r in sel if r["unique_survivor_is_true_byte"]),
        "diagonals_unique_and_equal_hintkey_byte": sum(1 for r in sel if r["unique_survivor_is_hintkey_byte"]),
        "diagonals_with_true_byte_anywhere_in_survivor_set": sum(1 for r in sel if r["true_byte_among_survivors"]),
        "diagonals_with_hintkey_byte_anywhere_in_survivor_set": sum(1 for r in sel if r["hintkey_byte_among_survivors"]),
        "runs": sorted(set(r["run"] for r in sel)),
    }

env = {
    "git_commit": sh("git rev-parse HEAD"),
    "git_dirty_tree": sh("git status --porcelain") != "",
    "git_status_porcelain": sh("git status --porcelain"),
    "uname": sh("uname -a"),
    "cpu_model": sh("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2-").strip(),
    "nproc": sh("nproc"),
    "mem_total_kb": sh("grep MemTotal /proc/meminfo").split()[1],
    "gcc_version": sh("gcc --version | head -1"),
    "python_version": sh("python3 --version"),
    "build_command": "gcc -O3 -maes -msse4.1 -pthread -o sq_null sq_null.c",
    "load_average_at_assembly": open("/proc/loadavg").read().strip(),
    "concurrency_note": ("Other GOAL-AES-003 BATCH-002 producer tasks ran on the same 4-core "
                         "machine throughout (load average 12 measured at 17:31:18Z). Wall-clock "
                         "timings in this task are therefore NOT comparable to BATCH-001's and are "
                         "not used as cost measurements."),
}

files = {}
for p in ["sq_null.c", "sq_null", "PREREGISTRATION.md", "driver.sh", "driver2.sh", "one.sh",
          "wrong_keys.txt", "make_results.py"]:
    fp = os.path.join(D, p)
    if os.path.exists(fp):
        files[p] = {"sha256": sha(fp), "bytes": os.path.getsize(fp)}
files["BATCH-001 sq.c (input, unmodified)"] = {
    "path": "coordination/goals/GOAL-AES-003/batches/BATCH-001/tasks/attack/sq.c",
    "sha256": sha(os.path.join(REPO, "coordination/goals/GOAL-AES-003/batches/BATCH-001/tasks/attack/sq.c")),
}
print(json.dumps({"rows": rows, "env": env, "files": files,
                  "ledger": ledger}, indent=1))
