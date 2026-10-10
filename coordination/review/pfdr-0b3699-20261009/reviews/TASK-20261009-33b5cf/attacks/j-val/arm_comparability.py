"""J-VAL comparability across arms, EXP-PFDR-0b3699 RA-04. TASK-20261009-33b5cf.
Standard library only. Over every census row of the run-root rows.jsonl.gz: the set of
values of engine, table_arity, la_pivot, method, accelerated, mode, target_label,
p_filter, relcount_version, harvest.retain, harvest.terminated_by, status, panel; and per
curve, the set of arms present (8 expected) and one job per curve for all arms
(merge-report per_key_source). Also the concurrency of RA-04 job processes from their
execution.json start/finish times (machine protection, maximum_workers 4).
No seeds. Usage: python arm_comparability.py <repo> <out.json>
"""
import datetime as dt
import gzip
import json
import os
import sys
from collections import defaultdict

T = "experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-table"
F = ["engine", "table_arity", "la_pivot", "method", "accelerated", "mode", "target_label", "p_filter",
     "relcount_version", "status", "panel"]


def main():
    repo, outp = sys.argv[1:3]
    vals = defaultdict(set)
    arms = defaultdict(set)
    with gzip.open(os.path.join(repo, T, "rows.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            for f in F:
                vals[f].add(json.dumps(r.get(f)))
            vals["harvest.retain"].add(json.dumps(r["harvest"].get("retain")))
            vals["harvest.terminated_by"].add(json.dumps(r["harvest"].get("terminated_by")))
            arms[(r["bits"], r["curve"])].add(r["arm"])
    mr = json.load(open(os.path.join(repo, T, "merge-report.json")))
    jobs_per_curve = defaultdict(set)
    for k, v in mr["per_key_source"].items():
        kk = json.loads(k)
        jobs_per_curve[(kk[0], kk[1])].add(v["job"])
    ev = []
    jd = os.path.join(repo, T, "attempt-1", "jobs")
    for j in os.listdir(jd):
        ex = json.load(open(os.path.join(jd, j, "execution.json")))
        ev.append((dt.datetime.fromisoformat(ex["started_at"]).timestamp(), 1))
        ev.append((dt.datetime.fromisoformat(ex["finished_at"]).timestamp(), -1))
    cur = mx = 0
    for _, d in sorted(ev, key=lambda x: (x[0], x[1])):
        cur += d
        mx = max(mx, cur)
    out = {"distinct_values": {k: sorted(v) for k, v in vals.items()},
           "curves": len(arms), "curves_with_8_arms": sum(1 for v in arms.values() if len(v) == 8),
           "curves_with_one_job_for_all_arms": sum(1 for v in jobs_per_curve.values() if len(v) == 1),
           "max_concurrent_job_processes": mx}
    json.dump(out, open(outp, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
