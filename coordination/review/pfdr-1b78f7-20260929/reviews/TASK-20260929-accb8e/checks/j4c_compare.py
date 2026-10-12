"""J4(c): re-executed census jobs vs archived job directories: rows, staircase records and
harvest rows, record by record in emission order, after removing only M-3's excluded keys
(keys named seconds, ending _seconds, worker_maxrss_bytes, ru_maxrss_bytes, at any depth)."""
import gzip, json, os, sys
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks")); import rl
S = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/rv-accb8e"
R = os.path.join(rl.WT, "experiments/EXP-PFDR-1b78f7/runs")
def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if not (k == "seconds" or k.endswith("_seconds") or k in ("worker_maxrss_bytes", "ru_maxrss_bytes"))}
    if isinstance(o, list): return [strip(v) for v in o]
    return o
def load(p):
    op = gzip.open if p.endswith(".gz") else open
    return [json.loads(l) for l in op(p, "rt") if l.strip()]
out = {}
for name, arch in [("job-R16-m5-b16-c5", "RUN-PFDR-1b78f7-stage-r/attempt-1/jobs/m5-b16-c5"), ("job-R12-b16-c0", "RUN-PFDR-1b78f7-census-m5/attempt-1/jobs/b16-c0")]:
    res = {}
    for f in ("rows", "staircase", "harvest-rows"):
        a = load(os.path.join(S, name, f + ".jsonl"))
        b = load(rl.opened(os.path.join(R, arch, f + ".jsonl.gz"), f"J4(c): archived {arch}/{f}"))
        A = [json.dumps(strip(x), sort_keys=True) for x in a]; B = [json.dumps(strip(x), sort_keys=True) for x in b]
        diffs = [i for i, (x, y) in enumerate(zip(A, B)) if x != y]
        keys = set()
        for i in diffs[:20]:
            x, y = json.loads(A[i]), json.loads(B[i]); keys |= {k for k in set(x) | set(y) if x.get(k) != y.get(k)}
        res[f] = {"reexec": len(A), "archived": len(B), "equal_in_emission_order": A == B, "differing_records": len(diffs), "differing_keys": sorted(keys)}
    out[name] = res
json.dump(out, open(os.path.join(W, "checks/out/j4c-jobs.json"), "w"), indent=1, sort_keys=True)
for k, v in out.items(): print(k, v)
