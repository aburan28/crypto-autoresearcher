"""Independent spot check of a7_blind.py on five instances, written separately:
frozen ratio straight from the canonical row, and the distinct-relation count
with a DIFFERENT canonical form (scale so the LAST nonzero entry is 1).
TASK-20260929-fd1a9f, pre-seal."""
import gzip, json, math, glob
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = WT + "/experiments/EXP-PFDR-1b78f7/runs"
CASES = [
    ("main", 30, 4, 4, "small_x", RUNS + "/RUN-PFDR-1b78f7-census-m4/merged/rows.jsonl.gz", RUNS + "/RUN-PFDR-1b78f7-census-m4/harvest-rows.jsonl.gz"),
    ("main", 24, 1, 4, "random_dick_r0", RUNS + "/RUN-PFDR-1b78f7-census-m4/merged/rows.jsonl.gz", RUNS + "/RUN-PFDR-1b78f7-census-m4/attempt-2/jobs/b24-c1/harvest-rows.jsonl.gz"),
    ("main", 16, 0, 5, "random_dick_r2", RUNS + "/RUN-PFDR-1b78f7-census-m5/rows.jsonl.gz", RUNS + "/RUN-PFDR-1b78f7-census-m5/attempt-1/jobs/b16-c0/harvest-rows.jsonl.gz"),
    ("j0", 22, 0, 3, "j0_coset", RUNS + "/RUN-PFDR-1b78f7-j0/rows.jsonl.gz", RUNS + "/RUN-PFDR-1b78f7-j0/attempt-1/jobs/b22-c0/harvest-rows.jsonl.gz"),
    ("main", 14, 0, 3, "known_log", RUNS + "/RUN-PFDR-1b78f7-census-m3/rows.jsonl.gz", RUNS + "/RUN-PFDR-1b78f7-census-m3/harvest-rows.jsonl.gz"),
]
for panel, bits, c, m, arm, rows_p, h_p in CASES:
    row = None
    for l in gzip.open(rows_p, "rt"):
        r = json.loads(l)
        if r.get("panel") == panel and r["bits"] == bits and r["curve"] == c and r.get("method") == f"ic_m{m}" and r["arm"] == arm and r["mode"] == "on":
            row = r
    N, S = row["N"], row["s3_solves"]
    fed = row["harvest"]["on"]["rows_fed"]
    r_frozen = row["relations"] + fed["TT"] + fed["TB"] + fed["SS"]
    ratio = 2 * S / math.sqrt(r_frozen * N)
    tt, tb, ss = [], [], []
    for l in gzip.open(h_p, "rt"):
        if f'"bits": {bits}, "curve": {c}, "m": {m}, "arm": "{arm}", "mode": "on"' not in l:
            continue
        d = json.loads(l)
        vec = {}
        for i, x in d["coeffs"]:
            vec[("b", i)] = (vec.get(("b", i), 0) + x) % N
        vec[("z", "k")] = d["kcoef"] % N
        vec[("z", "r")] = d["rhs"] % N
        items = sorted((k, v) for k, v in vec.items() if v)
        if not items:
            canon = None
        else:
            inv = pow(items[-1][1], -1, N)
            canon = tuple((k, v * inv % N) for k, v in items)
        {"TT": tt, "TB": tb, "SS": ss}[d["class"]].append(canon)
    fed_rows = tt + tb + ss[: fed["SS"]]
    dist = len({x for x in fed_rows if x is not None})
    r_d = row["relations"] + dist
    print(panel, bits, c, m, arm, "| S", S, "N", N, "r_frozen", r_frozen, "ratio %.6f" % ratio,
          "| retained", len(tt), len(tb), len(ss), "fed", fed, "| distinct", dist, "r_distinct", r_d, "ratio_d %.6f" % (2 * S / math.sqrt(r_d * N)))
