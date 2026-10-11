"""TASK-20261002-1069c1 bookkeeping helper: raw-result.json for R11 attempt-3 (RUN-PFDR-011cd0-p0-design).
Copies fields that p0 and the v5 harness wrote; computes no quantity.  Usage: r11_raw_v5.py <attempt_dir>"""
import hashlib, json, os, sys

ad = sys.argv[1]
H = "experiments/EXP-PFDR-011cd0/amd-594eab/"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


ex = json.load(open(os.path.join(ad, "execution.json")))
files = {f: (sha(os.path.join(ad, f)) if os.path.exists(os.path.join(ad, f)) else None)
         for f in ("curves.jsonl.gz", "design.json", "power.json", "p0x-report.json")}
raw = {"run_id": "RUN-PFDR-011cd0-p0-design", "location": ad, "attempt": 3,
       "exec_exit_code": ex["exit_code"], "watchdog_expired": ex["watchdog_expired"],
       "files_sha256": files,
       "analysis_file": {"path": "experiments/EXP-PFDR-011cd0/amd-280481/analyze_relcensus.py",
                         "sha256": sha("experiments/EXP-PFDR-011cd0/amd-280481/analyze_relcensus.py")}}
if files["p0x-report.json"]:
    p = json.load(open(os.path.join(ad, "p0x-report.json")))
    raw["P0X"] = {"pass": p.get("pass"), "compared": p.get("compared"),
                  "difference_count": p.get("difference_count"), "parsed_arms": p.get("parsed_arms")}
if files["design.json"]:
    d = json.load(open(os.path.join(ad, "design.json")))
    raw["design"] = {"design_stop": d["design_stop"], "final_n": d["final_n"], "declared_n": d["declared_n"],
                     "raised": [{k: r[k] for k in ("panel", "m", "declared_b30", "declared_b32", "chosen_multiplier",
                                                   "final_b30", "final_b32", "raised", "raise_reason",
                                                   "target_unattainable_by_design")} for r in d["rule"]],
                     "target_unattainable_by_design": d["target_unattainable_by_design"],
                     "t_star_plan": d["t_star_plan"].get("t"), "p0x_pass": d["p0x_pass"],
                     "p0_estimation": d["p0_estimation"],
                     "jobs": {k: len(v) for k, v in d["jobs"].items()},
                     "expected_disk_total_bytes_modeled": d["expected_disk"].get("total_bytes_modeled")}
checks = {}
for name in ("r11-curves-check.json", "r11-p0x-check.json"):
    p = H + name
    if os.path.exists(p):
        c = json.load(open(p))
        checks[name] = {"pass": c["pass"], "sha256": sha(p),
                        **({"difference_count": c["difference_count"], "listed_and_excluded_fields": c["listed_and_excluded_fields"]}
                           if "difference_count" in c else {}),
                        **({"container_equal": c["container_equal"], "H11_applied": c.get("H11_applied", False)}
                           if "container_equal" in c else {})}
raw["C5_checks"] = checks
raw["certificate"] = {"instances_claimed": 0, "note": "R11 is a measurement/design run; it claims no solve (kind none)"}
out = os.path.join(ad, "raw-result.json")
if os.path.exists(out):
    raise SystemExit("raw-result.json exists")
json.dump(raw, open(out, "x"), indent=1)
print(json.dumps({"written": out, "exec_exit_code": ex["exit_code"], "files": files}))
