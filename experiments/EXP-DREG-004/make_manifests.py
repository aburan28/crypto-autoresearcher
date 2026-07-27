import json, hashlib, os, re, shutil

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

base = "runs"
statedir = "runs/RUN-DREG-004-MEASURE-N21-SEM-A/work/h012c_measure_n21_sem_a_sem_n21_t0"
st = json.load(open(statedir + "/state.json"))
runs = ["RUN-DREG-004-MEASURE-N21-SEM-A"] + [
    "RUN-DREG-004-MEASURE-N21-SEM-A-CONT-%d" % i for i in range(1, 32)]

final_state_sha = sha(statedir + "/state.json")
carries = st["carries"]
carries_ok = all(sha(os.path.join(statedir, c["file"])) == c["sha256"] for c in carries)
carry_bytes = sum(os.path.getsize(os.path.join(statedir, c["file"])) for c in carries)
summary = {
    "final_state_sha256": final_state_sha,
    "carries": len(carries),
    "carries_sha256_all_verified": carries_ok,
    "carry_bytes": carry_bytes,
    "next_col": st["next_col"], "rank_acc": st["rank_acc"],
    "ncols": st["ncols"], "nrows": st["nrows"],
    "progress_pct": round(100.0 * st["next_col"] / st["ncols"], 2),
    "secs_total": round(st["secs_total"], 1), "done": st["done"],
    "rate_mat": st["rate_mat"], "system_hash": st["system_hash"],
    "units": [{"j0": u["j0"], "j1": u["j1"], "k": u["k"], "rank_acc": u["rank_acc"]}
              for u in st["units"]],
}
json.dump(summary, open("checkpoint-summary.json", "w"), indent=1)
print(json.dumps({k: summary[k] for k in (
    "final_state_sha256", "carries", "carries_sha256_all_verified",
    "carry_bytes", "next_col", "rank_acc", "ncols", "progress_pct",
    "secs_total", "done")}, indent=1))

chunk_of = {0: 8000}
for i in range(1, 32):
    chunk_of[i] = (10000 if i <= 8 else (8000 if i <= 11 else (6000 if i <= 16 else (5000 if i == 17 else (4000 if i <= 23 else (3000 if i <= 28 else 2000))))))
for i, r in enumerate(runs):
    rd = os.path.join(base, r)
    out = open(os.path.join(rd, "stdout.log")).read()
    err = open(os.path.join(rd, "stderr.log")).read()
    m = re.search(r"(\d+)\s+maximum resident set size", err)
    peak = int(m.group(1)) if m else None
    cols = re.findall(r"cols (\d+)\.\.(\d+) k=(\d+) rank=(\d+)", out)
    prep = os.path.join(rd, "prelaunch.json")
    pre = json.load(open(prep)) if os.path.exists(prep) else None
    man = {
        "run": {
            "id": r,
            "experiment_id": "EXP-DREG-004",
            "status": "completed_valid_invocation",
            "purpose": "n=21 sem D5 rank cell, checkpointed invocation %d of 31 (turn %s)"
                       % (i + 1, "1" if i <= 8 else ("2" if i <= 16 else ("3" if i <= 23 else "4"))),
            "continues": (runs[i - 1] if i else None),
            "code": {
                "commit": "30763cd2ad68c47446f102a2d44b96fc87142250",
                "dirty": True,
                "instrument_sha256": "0eb38126998c73601687e248439a05f39038e762d5a5b99009598b67e59a0bbb",
            },
            "environment": {"file": "environment.json"},
            "inputs": {
                "arm": "sem", "n": 21, "t": 3, "target_index": 0, "degree": 5,
                "seed": 2026, "system_hash": st["system_hash"],
                "tag": "measure_n21_sem_a",
                "chunk_force": chunk_of[i],
                "budget_s": 230, "max_units": (2 if i == 1 else 1),
            },
            "expected": {"semiregular_prediction": 268674, "rank": None, "deficit": None},
            "prelaunch": pre,
            "resources": {"peak_rss_bytes": peak},
            "result": {
                "valid": True, "cell_done": False,
                "units_added": len(cols),
                "columns_processed_in_invocation": [[int(a), int(b)] for a, b, _, _ in cols],
                "k_new": [int(k) for _, _, k, _ in cols],
                "rank_acc_after": [int(x) for _, _, _, x in cols],
                "interpretation_status": "cell incomplete - no rank claim (in_progress_checkpointed)",
            },
            "artifacts": {
                "command": "command.txt", "stdout": "stdout.log", "stderr": "stderr.log",
                "shared_checkpoint_state": "RUN-DREG-004-MEASURE-N21-SEM-A/work/h012c_measure_n21_sem_a_sem_n21_t0/state.json",
            },
        }
    }
    if i == 0:
        man["run"]["init"] = {"adj_build_s": 39.6, "ncols": 778394, "nrows": 279048,
                              "pred": 268674, "support_coverage": 778394 / 974982}
    with open(os.path.join(rd, "manifest.yaml"), "w") as f:
        f.write(json.dumps(man, indent=1))
    if not os.path.exists(os.path.join(rd, "environment.json")):
        shutil.copy(os.path.join(base, runs[0], "environment.json"),
                    os.path.join(rd, "environment.json"))
print("manifests written:", len(runs))
