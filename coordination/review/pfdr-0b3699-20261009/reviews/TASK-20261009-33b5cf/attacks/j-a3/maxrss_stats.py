"""J-A3 supplementary: size and shape of harvest.worker_maxrss_bytes differences.
TASK-20261009-33b5cf. Standard library only. For each job and source pair, over rows
matched by (bits, curve, m, arm, mode): rows equal, median and max |difference| in
bytes, whether every value is a multiple of 4096, and whether the value is
non-decreasing in file order within a source (a process high-water mark should be).
No seeds. Usage: python maxrss_stats.py <repo> <scratch> <out.json>
"""
import gzip
import json
import os
import statistics
import sys

KEY = ("bits", "curve", "m", "arm", "mode")


def load(path):
    out = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out.append((tuple(r.get(k) for k in KEY), r["harvest"]["worker_maxrss_bytes"],
                            r["seconds"], r["harvest"]["harvest_seconds"]))
    return out


def main():
    repo, scratch, outp = sys.argv[1:4]
    rep = {}
    for job in ("4-b30-c10", "4-b32-c10"):
        src = {"ARCH": f"{repo}/experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-table/attempt-1/jobs/{job}",
               "R1": f"{scratch}/j-a3/{job}/run1", "R2": f"{scratch}/j-a3/{job}/run2",
               "EC": f"{repo}/experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-repro/attempt-1/jobs/{job}"}
        data = {s: load(os.path.join(d, "rows.jsonl.gz")) for s, d in src.items()}
        jr = {"per_source": {}, "pairs": {}}
        for s, rows in data.items():
            v = [x[1] for x in rows]
            jr["per_source"][s] = {
                "all_multiple_of_4096": all(x % 4096 == 0 for x in v),
                "non_decreasing_in_file_order": all(v[i] <= v[i + 1] for i in range(len(v) - 1)),
                "first": v[0], "last": v[-1],
                "seconds_sum": round(sum(x[2] for x in rows), 3)}
        for a, b in [("ARCH", "R1"), ("ARCH", "R2"), ("R1", "R2"), ("ARCH", "EC"), ("EC", "R1"), ("EC", "R2")]:
            ma = {x[0]: x for x in data[a]}
            mb = {x[0]: x for x in data[b]}
            ks = sorted(set(ma) & set(mb), key=str)
            d = [abs(ma[k][1] - mb[k][1]) for k in ks]
            jr["pairs"][f"{a}_vs_{b}"] = {
                "matched": len(ks),
                "worker_maxrss_equal": sum(1 for x in d if x == 0),
                "worker_maxrss_absdiff_median": statistics.median(d),
                "worker_maxrss_absdiff_max": max(d),
                "seconds_equal": sum(1 for k in ks if ma[k][2] == mb[k][2]),
                "harvest_seconds_equal": sum(1 for k in ks if ma[k][3] == mb[k][3])}
        rep[job] = jr
    json.dump(rep, open(outp, "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
