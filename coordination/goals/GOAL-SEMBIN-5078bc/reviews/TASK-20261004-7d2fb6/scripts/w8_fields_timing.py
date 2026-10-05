#!/usr/bin/env python3
"""w8_fields_timing.py -- joint W8 (4) and (6). (4): per-D process-wide fields: checkpoint_resumes / elimination_faults per record against the true resume history, and wall_s (post-resume only?).
(6): resource claims against timing: manifest timing.workers vs scheduler log and the lane progress logs; recorded peak memory; the 8 GiB / 5400 s advisory budgets. Read-only."""
import json, glob, os, re, datetime, yaml
REPO = "/home/user/crypto-autoresearcher"; WS = os.environ["WS"]
R = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e"
man = yaml.safe_load(open(f"{R}/manifest.yaml"))["run"]
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
print("(4) per-D process-wide counters:")
for lane in sorted(glob.glob(f"{R}/closure_m2_n4*")):
    for l in open(f"{lane}/cells/results.jsonl"):
        r = json.loads(l)
        if r["instrument"] != "closure_certificate": continue
        print(f"  {r['instance_id'][:34]:34s} per-D (D: resumes, faults, wall_s):", [(p["D"], p.get("checkpoint_resumes"), p.get("elimination_faults"), round(p.get("wall_s", 0))) for p in r["per_D"]])
print("\n(6) timing: manifest timing.workers vs the lane's own progress log and the scheduler log")
sched = open(f"{R}/schedulers/window_sched.log").read().splitlines()
for lane in sorted(glob.glob(f"{R}/closure_m2_n4*")):
    name = os.path.basename(lane); n = int(name[-2:])
    prog = [l for l in open(f"{lane}/cells/progress.log").read().splitlines()]
    starts = [ts(re.match(r"\[(\S+)\]", l)[1]) for l in prog if " start out_dir=" in l]
    ends = [ts(re.match(r"\[(\S+)\]", l)[1]) for l in prog if l.endswith(" done")]
    mw = man["timing"]["workers"][name]
    first, last = starts[0], ends[-1]
    d4 = [(re.search(r"(ch_\S+) closure D=4", l)[1][-12:], float(re.search(r"([\d.]+)s$", l)[1])) for l in prog if "closure D=4" in l]
    print(f"  {name}: manifest started {mw['started_at'][:19]} finished {mw['finished_at'][:19]} wall {mw['wall_seconds']:.0f}s | first launch in progress.log {first:%Y-%m-%dT%H:%M:%S} .. done {last:%Y-%m-%dT%H:%M:%S} = {(last-first).total_seconds():.0f}s elapsed incl. restarts/pauses; launches: {len(starts)}; D=4 wall_s in records: {d4}")
print("\nrecorded peak memory anywhere in the 5ed13e records?", any("peak" in l.lower() and "rss" in l.lower() for lane in glob.glob(f"{R}/closure_m2_n4*/cells/results.jsonl") for l in open(lane) if '"peak_rss_bytes": null' not in l and 'peak_rss' in l and '"peak_rss_bytes": ' in l and '"peak_rss_bytes": null' not in l))
rec_keys = set()
for lane in glob.glob(f"{R}/closure_m2_n4*/cells/results.jsonl"):
    for l in open(lane):
        r = json.loads(l)
        if r["instrument"] == "closure_certificate":
            for p in r["per_D"]: rec_keys |= set(p)
print("closure per-D fields:", sorted(rec_keys))
print("fields mentioning memory:", [k for k in sorted(rec_keys) if "mem" in k or "rss" in k or "rows" in k])
print("manifest has resources block:", "resources" in man, "| manifest timing keys:", list(man["timing"].keys()))
