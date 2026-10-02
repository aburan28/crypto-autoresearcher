"""Declare the F1 job list (RS-1 + C-a, C-b, C-c) with seeds BEFORE any job runs.
RS-1 = the sealed frozen-convention firing set (equal to the plan's 73 keys)."""
import json, os, collections, yaml
HERE = os.path.dirname(os.path.abspath(__file__))
recs = [json.loads(l) for l in open(os.path.join(HERE, "..", "rederivation", "out", "instances.jsonl"))]
FZ = "frozen|S3|c2"
rs1 = sorted(tuple(r["key"]) for r in recs if r["set"] == "S15" and r["eval"][FZ]["state"] == "ok" and r["eval"][FZ]["lt09"])
assert len(rs1) == 73
MAIN_ARMS = ("subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
             "random_dick_r0", "random_dick_r1", "random_dick_r2", "known_log")
J0_ARMS = ("j0_coset", "j0_random_r0", "j0_random_r1", "j0_random_r2")
jobs = collections.OrderedDict()
for panel, bits, c, m, arm, mode in rs1:
    jk = (panel, bits, c, m)
    j = jobs.setdefault(jk, {"arms": set(), "rs1_keys": [], "controls": []})
    j["arms"].add(arm)
    j["rs1_keys"].append([panel, bits, c, m, arm, mode])
    if arm == "known_log":
        j["arms"].add("random_sub_r0")
        j["controls"].append("known_log cap supplier random_sub_r0 (census and on)")
    if panel == "j0":
        j["arms"].add("j0_random_r0")
        j["controls"].append("C-c j0_random_r0 (census and on)")
    j["controls"].append(f"C-a census twin of {arm}")
for m in (3, 4, 5):
    jobs[("main", 32, 0, m)] = {"arms": {"random_sub_r0"}, "rs1_keys": [], "controls": ["C-b random_sub_r0 both modes at 32 bits, curve 0"]}

def seeds(panel, c, arms):
    s = {"curve_seed": c, "target_seed": 0, "target_log_rule": f"random.Random('target|<bits>|{c}|0').randrange(1, N)",
         "solver_seed": c, "target_stream": f"random.Random('ic|p|a|b|m|census|{c}')"}
    base = {}
    for a in arms:
        base[a] = {"subgroup": f"FactorBase.subgroup(E, size0, {c})", "dickson": f"FactorBase.dickson(E, size0, {c})",
                   "small_x": "FactorBase.small_x(E, s_sub)", "random_sub_r0": f"random seed {c}",
                   "random_sub_r1": f"random seed {c + 1000}", "random_sub_r2": f"random seed {c + 2000}",
                   "random_dick_r0": f"random seed {c + 3000}", "random_dick_r1": f"random seed {c + 4000}",
                   "random_dick_r2": f"random seed {c + 5000}", "known_log": "known_log(E, P, s_sub) (logs 1..s_sub)",
                   "j0_coset": f"FactorBase.subgroup(E, size0, {c}, divisor_multiple_of=3)",
                   "j0_random_r0": f"random seed {c}"}[a]
    s["bases"] = base
    return s

out = []
SCR = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/rv-fd1a9f/jobs"
for (panel, bits, c, m), j in jobs.items():
    order = MAIN_ARMS if panel == "main" else J0_ARMS
    arms = [a for a in order if a in j["arms"]]
    label = f"{panel}-m{m}-b{bits}-c{c}-" + "+".join(arms)
    d = f"{SCR}/{label}"
    argv = ["census", "--panel", panel, "--m", str(m), "--bits", str(bits), "--curve-offset", str(c), "--curves", "1"]
    if panel == "main":
        argv += ["--known-log-max-bits", "24" if m == 3 else "0"]
    else:
        argv += ["--rho-curves", "5"]
    argv += ["--workers", "1", "--arms"] + arms + ["--out", f"{d}/rows.jsonl", "--rows-out", f"{d}/harvest-rows.jsonl",
                                                  "--staircase-out", f"{d}/staircase.jsonl"]
    out.append({"label": label, "jobdir": d, "argv": argv, "rs1_keys": j["rs1_keys"], "controls": sorted(set(j["controls"])),
                "seeds": seeds(panel, c, arms), "cost_rank": (bits if m != 4 else bits + 8)})
out.sort(key=lambda e: (e["cost_rank"], e["label"]))
doc = {"declared_by": "TASK-20260929-fd1a9f", "declared_before_any_job_ran": True,
       "rule": "RS-1 = 73 keys (the sealed frozen firing set = the plan's list); one job per (panel, bits, curve, m); --arms restricted; known_log jobs add random_sub_r0 (cap); j0 jobs add j0_random_r0 (C-c); C-a census twins come from the same job; C-b adds (main, 32, 0, m, random_sub_r0) for m = 3, 4, 5. M-1 flags: --curves 1 --workers 1, --known-log-max-bits 24 at m = 3 (R10 frozen value) and 0 at m = 4, 5; j0: --rho-curves 5. Default --instance-watchdog 7200. Each job at most twice (a second identical run only to separate nondeterminism from a defect).",
       "interpreter": "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python (3.11.15, numpy 2.4.6)",
       "env": "PYTHONPATH=<detached worktree>/src PYTHONDONTWRITEBYTECODE=1 OMP/OPENBLAS/MKL_NUM_THREADS=1, nice 19, RSS stop 2.0e9 (checks/guard.py)",
       "command_template": "guard.py --label F1-<label> -- <python> resolve/driver.py <jobdir>/captures.jsonl <argv>",
       "n_jobs": len(out), "n_rs1_keys": sum(len(e["rs1_keys"]) for e in out), "jobs": out}
yaml.safe_dump(doc, open(os.path.join(HERE, "commands.yaml"), "w"), sort_keys=False, width=250)
print(len(out), "jobs;", doc["n_rs1_keys"], "RS-1 keys")
for e in out: print(e["label"])
