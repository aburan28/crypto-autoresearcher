"""R11 raw-result writer (TASK-20261001-7f7a33): attempt-2 and run root.  Reads execution.json,
p0x-report.json (gate result only) and stderr tails; computes nothing else."""
import json, sys, hashlib, os
which, d = sys.argv[1], sys.argv[2]
ex = json.load(open(f"{d}/execution.json"))
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
err_tail = open(f"{d}/stderr.log").read()[-1500:]
raw = {"run_id": "RUN-PFDR-011cd0-p0-design", "location": d, "attempt": which,
       "exit_code": ex["exit_code"], "peak_rss_bytes": ex["peak_rss_bytes_max_descendant"],
       "wall_seconds": ex["wall_seconds"], "stderr_tail": err_tail,
       "curves": {"file": f"{d}/curves.jsonl.gz", "sha256": sha(f"{d}/curves.jsonl.gz"), "records": 12500},
       "outputs_present": sorted(f for f in ("p0x-report.json", "design.json", "power.json") if os.path.exists(f"{d}/{f}")),
       "certificate": {"instances_claimed": 0, "note": "P0 claims no solve"}}
if os.path.exists(f"{d}/p0x-report.json"):
    p = json.load(open(f"{d}/p0x-report.json"))
    raw["P0X"] = {"pass": p["pass"], "compared": p["compared"], "difference_count": p["difference_count"],
                  "skipped": p["skipped"], "completeness_flag_differences": len(p["completeness_flag_differences"]),
                  "parsed_arms": p["parsed_arms"], "report_sha256": sha(f"{d}/p0x-report.json")}
json.dump(raw, open(f"{d}/raw-result.json", "w"), indent=1)
print(json.dumps({k: raw[k] for k in ("attempt", "exit_code", "outputs_present")} | ({"P0X": raw["P0X"]} if "P0X" in raw else {})))
