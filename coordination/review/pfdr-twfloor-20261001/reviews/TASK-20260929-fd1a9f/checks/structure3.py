"""relations - rank (census) and the on-mode decomposition / rank-increment
bookkeeping by k_determined_by. No ratio. TASK-20260929-fd1a9f."""
import gzip, json, sys, collections
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = WT + "/experiments/EXP-PFDR-1b78f7/runs"
FILES = {"R10": "/RUN-PFDR-1b78f7-census-m3/rows.jsonl.gz", "R11": "/RUN-PFDR-1b78f7-census-m4/merged/rows.jsonl.gz",
         "R12": "/RUN-PFDR-1b78f7-census-m5/rows.jsonl.gz", "R14": "/RUN-PFDR-1b78f7-j0/rows.jsonl.gz",
         "R16": "/RUN-PFDR-1b78f7-stage-r/rows.jsonl.gz"}
c = collections.Counter()
for tag, f in FILES.items():
    for l in gzip.open(RUNS + f, "rt"):
        r = json.loads(l)
        if not str(r.get("method", "")).startswith("ic_m"): continue
        h = r["harvest"]
        kl = "known_log" if r["arm"] == "known_log" else "other"
        if r["mode"] == "census":
            c[("census", kl, h["terminated_by"], "relations-rank=%s" % min(r["relations"] - r["rank"], 3))] += 1
        else:
            on = h["on"]; inc = on["solver_rank_increments"]
            kd = on["k_determined_by"]
            c[("on", kl, kd, "rel-decomp_incr=%d" % (r["relations"] - inc["decomp"]),
               "fedSS-incrSS=%s" % ("0" if on["rows_fed"]["SS"] - inc["SS"] == 0 else ">0"))] += 1
for k, v in sorted(c.items(), key=str): print(v, k)
