"""F1 (b): compare every re-executed row, harvest row and staircase record with
the archived canonical ones, after M-3's exclusions only (keys named seconds,
keys ending in _seconds, worker_maxrss_bytes, ru_maxrss_bytes, at any depth).
Archived sources: canonical rows (R10 root, R11 merged/, R12 root, R14 root);
harvest rows from the file that produced each instance (M-5 (8)); staircases
from the canonical staircase files. Harvest rows and staircases are compared as
an order-sensitive sha256 over the normalised records (json.dumps sort_keys),
plus counts; each archived source is streamed once.

usage: python3 compare_rows.py <out row-comparison.jsonl> <out summary.json>
"""
import collections
import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = WT + "/experiments/EXP-PFDR-1b78f7/runs"
M3, M4, M5, J0 = (RUNS + "/RUN-PFDR-1b78f7-census-m3", RUNS + "/RUN-PFDR-1b78f7-census-m4",
                  RUNS + "/RUN-PFDR-1b78f7-census-m5", RUNS + "/RUN-PFDR-1b78f7-j0")
R11_RESUME = {(b, c) for b in (12, 14, 16, 18, 20, 22) for c in range(5)} | {(24, 1), (24, 3), (24, 4)}


def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items()
                if not (k == "seconds" or k.endswith("_seconds") or k in ("worker_maxrss_bytes", "ru_maxrss_bytes"))}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x


def diffkeys(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(path + "/" + k + " (missing on one side)")
            else:
                out += diffkeys(a[k], b[k], path + "/" + k)
    elif a != b:
        out.append(path or "/")
    return out


def rkey(r):
    if str(r.get("method", "")).startswith("ic_m"):
        return (r["panel"], r["bits"], r["curve"], int(r["method"][4:]), r["arm"], r["mode"])
    return (r.get("panel"), r["bits"], r["curve"], r.get("method"))


class Digest:
    def __init__(self):
        self.h, self.n = hashlib.sha256(), 0

    def add(self, rec):
        self.h.update((json.dumps(strip(rec), sort_keys=True) + "\n").encode())
        self.n += 1

    def value(self):
        return [self.n, self.h.hexdigest()]


def sources(panel, m, bits, c):
    if panel == "j0":
        return J0 + f"/attempt-1/jobs/b{bits}-c{c}/harvest-rows.jsonl.gz", J0 + "/staircase.jsonl.gz"
    if m == 3:
        return M3 + "/harvest-rows.jsonl.gz", M3 + "/staircase.jsonl.gz"
    if m == 4:
        src = M4 + f"/attempt-2/jobs/b{bits}-c{c}/harvest-rows.jsonl.gz" if (bits, c) in R11_RESUME else M4 + "/harvest-rows.jsonl.gz"
        return src, M4 + "/merged/staircase.jsonl.gz"
    return M5 + f"/attempt-1/jobs/b{bits}-c{c}/harvest-rows.jsonl.gz", M5 + "/staircase.jsonl.gz"


def stream(path, panel, wanted, digests):
    with gzip.open(path, "rt") as f:
        for l in f:
            d = json.loads(l)
            k = (panel, d.get("bits"), d.get("curve"), d.get("m"), d.get("arm"), d.get("mode"))
            if k in wanted:
                digests[k].add(d)


def main():
    canon_rows = {}
    for p in (M3 + "/rows.jsonl.gz", M4 + "/merged/rows.jsonl.gz", M5 + "/rows.jsonl.gz", J0 + "/rows.jsonl.gz"):
        for l in gzip.open(p, "rt"):
            r = json.loads(l)
            canon_rows[rkey(r)] = r
    log = [json.loads(l) for l in open(os.path.join(HERE, "run-log.jsonl"))]
    jobs = []
    for a in log:
        d = a["dir"]
        if a["exit"] != 0 or not os.path.exists(os.path.join(d, "rows.jsonl")):
            jobs.append((a, None))
            continue
        rows = [json.loads(l) for l in open(os.path.join(d, "rows.jsonl"))]
        jobs.append((a, rows))
    # wanted archived instance keys per source file
    want_h, want_s = collections.defaultdict(dict), collections.defaultdict(dict)
    for a, rows in jobs:
        if rows is None:
            continue
        for r in rows:
            k = rkey(r)
            if len(k) != 6:
                continue
            hs, ss = sources(k[0], k[3], k[1], k[2])
            want_h[(hs, k[0])][k] = Digest()
            want_s[(ss, k[0])][k] = Digest()
    for (path, panel), dg in want_h.items():
        stream(path, panel, set(dg), dg)
    for (path, panel), dg in want_s.items():
        stream(path, panel, set(dg), dg)
    arch_h = {k: v.value() for dg in want_h.values() for k, v in dg.items()}
    arch_s = {k: v.value() for dg in want_s.values() for k, v in dg.items()}
    out, summary = [], collections.Counter()
    for a, rows in jobs:
        if rows is None:
            out.append({"job": a["label"], "attempt": a["attempt"], "outcome": "blocked", "reason": f"exit {a['exit']}"})
            summary["blocked_job|attempt%d" % a["attempt"]] += 1
            continue
        d = a["dir"]
        panel = rows[0]["panel"]
        hre, sre = collections.defaultdict(Digest), collections.defaultdict(Digest)
        for l in open(os.path.join(d, "harvest-rows.jsonl")):
            h = json.loads(l)
            hre[(panel, h["bits"], h["curve"], h["m"], h["arm"], h["mode"])].add(h)
        for l in open(os.path.join(d, "staircase.jsonl")):
            s = json.loads(l)
            sre[(panel, s["bits"], s["curve"], s["m"], s["arm"], s["mode"])].add(s)
        for r in rows:
            k = rkey(r)
            arch = canon_rows.get(k)
            rec = {"job": a["label"], "attempt": a["attempt"], "key": list(k)}
            if arch is None:
                rec |= {"outcome": "differs", "reason": "no archived row"}
            else:
                dk = diffkeys(strip(r), strip(arch))
                rec["row_differing_keys"] = dk
                ok = not dk
                if len(k) == 6:
                    rec["harvest_rows"] = {"reexec": hre[k].value(), "archived": arch_h.get(k)}
                    rec["staircase"] = {"reexec": sre[k].value(), "archived": arch_s.get(k)}
                    rec["harvest_rows_equal_in_order"] = rec["harvest_rows"]["reexec"] == rec["harvest_rows"]["archived"]
                    rec["staircase_equal_in_order"] = rec["staircase"]["reexec"] == rec["staircase"]["archived"]
                    ok = ok and rec["harvest_rows_equal_in_order"] and rec["staircase_equal_in_order"]
                    rec["reproduced_fields"] = {f: r.get(f) for f in ("s3_solves", "relations", "rank", "attempts", "k_found", "k_verified")}
                    rec["reproduced_fields"]["terminated_by"] = r["harvest"]["terminated_by"]
                    if r["mode"] == "on":
                        rec["reproduced_fields"]["rows_fed"] = r["harvest"]["on"]["rows_fed"]
                        rec["reproduced_fields"]["solver_rank_increments"] = r["harvest"]["on"]["solver_rank_increments"]
                else:
                    rec["reproduced_fields"] = {"walk_ops": r.get("walk_ops"), "setup_ops": r.get("setup_ops")}
                rec["outcome"] = "reproduced" if ok else "differs"
            out.append(rec)
            summary[f"{rec['outcome']}|attempt{a['attempt']}|{'solver' if len(k) == 6 else 'rho'}"] += 1
    with open(sys.argv[1], "w") as f:
        for r in out:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    js = {"by_outcome": dict(summary), "not_reproduced": [r for r in out if r.get("outcome") != "reproduced"]}
    json.dump(js, open(sys.argv[2], "w"), indent=1)
    print(json.dumps(js, indent=1)[:4000])


if __name__ == "__main__":
    main()
