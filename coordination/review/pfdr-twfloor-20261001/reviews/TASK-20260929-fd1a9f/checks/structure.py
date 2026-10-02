"""Structure of the permitted pre-seal row inputs: key sets, counts by status and
terminated_by, on-mode block keys. Computes NO ratio and no floor quantity.
TASK-20260929-fd1a9f (validator-breakthrough)."""
import gzip, json, sys, collections, os
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = WT + "/experiments/EXP-PFDR-1b78f7/runs"
FILES = {
    "R10": RUNS + "/RUN-PFDR-1b78f7-census-m3/rows.jsonl.gz",
    "R11": RUNS + "/RUN-PFDR-1b78f7-census-m4/merged/rows.jsonl.gz",
    "R12": RUNS + "/RUN-PFDR-1b78f7-census-m5/rows.jsonl.gz",
    "R13": RUNS + "/RUN-PFDR-1b78f7-rho/rows.jsonl.gz",
    "R14": RUNS + "/RUN-PFDR-1b78f7-j0/rows.jsonl.gz",
    "R16": RUNS + "/RUN-PFDR-1b78f7-stage-r/rows.jsonl.gz",
}
out = {}
for tag, p in FILES.items():
    rows = [json.loads(l) for l in gzip.open(p, "rt")]
    keys = collections.Counter()
    hkeys = collections.Counter()
    onkeys = collections.Counter()
    status = collections.Counter()
    term = collections.Counter()
    methods = collections.Counter()
    for r in rows:
        keys[tuple(sorted(r.keys()))] += 1
        methods[(r.get("panel"), r.get("method"), r.get("arm"), r.get("mode"))] += 0
        status[(r.get("panel"), r.get("method"), r.get("mode"), r.get("status"), r.get("status_reason"))] += 1
        h = r.get("harvest")
        if isinstance(h, dict):
            hkeys[tuple(sorted(h.keys()))] += 1
            term[(r.get("mode"), r.get("arm") if r.get("arm") == "known_log" else "other", h.get("terminated_by"))] += 1
            if "on" in h:
                on = h["on"]
                onkeys[json.dumps({k: (sorted(v.keys()) if isinstance(v, dict) else type(v).__name__) for k, v in on.items()}, sort_keys=True)] += 1
    out[tag] = {
        "n_rows": len(rows),
        "row_key_sets": [[list(k), c] for k, c in keys.items()],
        "harvest_key_sets": [[list(k), c] for k, c in hkeys.items()],
        "on_block_shapes": [[k, c] for k, c in onkeys.items()],
        "status": [[list(map(str, k)), c] for k, c in sorted(status.items(), key=lambda kv: str(kv[0]))],
        "terminated_by": [[list(map(str, k)), c] for k, c in sorted(term.items(), key=lambda kv: str(kv[0]))],
    }
json.dump(out, open(sys.argv[1], "w"), indent=1)
print("written", sys.argv[1])
