#!/usr/bin/env python3
"""Validator re-run of a sample of RUN-ECDLP-502ae2-01 with the COMMITTED launcher (snapshot 1d008fd8e6).
Calls msolve_grid.run_instance unmodified except: tempfiles go to a per-job kept directory and are not
deleted (so the validator can post-check the .gb / .sol outputs). msolve flags, timeouts, and instance
construction are the launcher's own.
Usage: rerun.py SNAPSHOT_LAUNCHER OUT_DIR"""
import importlib.util, json, os, sys, types, tempfile, hashlib, time, platform, subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
LAUNCHER, OUT = sys.argv[1], sys.argv[2]
SAMPLE = [(3, i) for i in range(6)] + [(4, 0), (4, 3), (4, 4)]
ARMS = ["A", "B"]
def load():
    spec = importlib.util.spec_from_file_location("grid", LAUNCHER)
    g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g); return g
def work(job):
    g = load()
    d = os.path.join(OUT, "files", f"L{job['L']}-inst{job['inst']}")
    os.makedirs(d, exist_ok=True)
    tempfile.tempdir = d
    shim = types.ModuleType("os_shim"); shim.__dict__.update(os.__dict__); shim.unlink = lambda f: None
    g.os = shim
    t0 = time.time()
    r = g.run_instance(job)
    r["validator_elapsed_s"] = round(time.time() - t0, 2)
    r["validator_files"] = sorted(os.listdir(d))
    return r
def main():
    os.makedirs(OUT, exist_ok=True)
    plan = json.load(open(os.path.join(os.path.dirname(LAUNCHER), "trial-plan.json")))
    env = dict(python=platform.python_version(), platform=platform.platform(), cpus=os.cpu_count(),
               msolve=subprocess.run(["dpkg-query", "-W", "-f=${Version}", "msolve"], capture_output=True, text=True).stdout,
               launcher_sha256=hashlib.sha256(open(LAUNCHER, "rb").read()).hexdigest(), sample=SAMPLE, arms=ARMS,
               workers=4, timeout_s=plan["timeout_s"], started=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    rows = []
    with ProcessPoolExecutor(4) as ex:
        for L in sorted({L for L, _ in SAMPLE}):
            jobs = []
            for (LL, inst) in SAMPLE:
                if LL != L: continue
                kind = "planted" if inst < plan["planted_per_cell"] else "random"
                seed = int(hashlib.sha256(f"{plan['seed']}|3|{L}|{inst}".encode()).hexdigest()[:12], 16)
                jobs.append(dict(m=3, L=L, inst=inst, kind=kind, seed=seed, timeout=plan["timeout_s"], arms=list(ARMS)))
            for f in as_completed([ex.submit(work, j) for j in jobs]):
                r = f.result(); rows.append(r)
                print(r["L"], r["inst"], {a: (v.get("status"), v.get("gb_wall_s"), v.get("solve_wall_s"), v.get("quotient_dim"), v.get("planted_in_variety")) for a, v in r["results"].items()}, flush=True)
    env["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rows.sort(key=lambda r: (r["L"], r["inst"]))
    with open(os.path.join(OUT, "rerun-raw.jsonl"), "w") as fh:
        for r in rows: fh.write(json.dumps(r) + "\n")
    json.dump(env, open(os.path.join(OUT, "rerun-environment.json"), "w"), indent=1)
if __name__ == "__main__":
    main()
