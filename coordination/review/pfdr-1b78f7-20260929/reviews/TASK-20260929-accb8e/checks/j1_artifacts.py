"""J1(b): required artifacts of R01, R01a, R02-R16 (roots, attempts, jobs, merged/) as
specification.yaml required_artifacts + AMD-20260929-430f44 M-1/M-5/M-6 define them, and
every checksums.sha256 verified against its files (listed entries hash-checked; files in
its directory scope that it does not list are reported)."""
import glob, hashlib, json, os, sys
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
RUNS = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs")
PER_RUN = ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json",
           "checksums.sha256"]
RUNMAP = {
    "R01": ("RUN-PFDR-1b78f7-tests", ["junit.xml"]),
    "R01a": ("RUN-PFDR-1b78f7-tests-amd1de84f", ["junit.xml"]),
    "R02": ("RUN-PFDR-1b78f7-reg-off-sweep-20260924", ["rows.jsonl.gz", "regression-report.json"]),
    "R03": ("RUN-PFDR-1b78f7-reg-off-sweep-mitm-20260926", ["rows.jsonl.gz", "regression-report.json"]),
    "R04": ("RUN-PFDR-1b78f7-reg-off-sweep-arity-20260926", ["rows.jsonl.gz", "regression-report.json"]),
    "R05": ("RUN-PFDR-1b78f7-reg-off-sweep-minfill-20260926", ["rows.jsonl.gz", "regression-report.json"]),
    "R06": ("RUN-PFDR-1b78f7-reg-off-sweep-arity-minfill-20260926", ["rows.jsonl.gz", "regression-report.json"]),
    "R07": ("RUN-PFDR-1b78f7-reg-off-sweep-arity67-20260928", ["rows.jsonl.gz", "regression-report.json"]),
    "R08": ("RUN-PFDR-1b78f7-reg-census-sweep-minfill-20260926", ["rows.jsonl.gz", "regression-report.json"]),
    "R09": ("RUN-PFDR-1b78f7-reg-census-sweep-arity-minfill-20260926", ["rows.jsonl.gz", "regression-report.json"]),
    "R10": ("RUN-PFDR-1b78f7-census-m3", ["rows.jsonl.gz", "harvest-rows.jsonl.gz", "staircase.jsonl.gz"]),
    "R11": ("RUN-PFDR-1b78f7-census-m4", ["rows.jsonl.gz", "harvest-rows.jsonl.gz", "staircase.jsonl.gz"]),
    "R12": ("RUN-PFDR-1b78f7-census-m5", ["rows.jsonl.gz", "staircase.jsonl.gz", "execution.json", "merge-report.json"]),
    "R13": ("RUN-PFDR-1b78f7-rho", ["rows.jsonl.gz"]),
    "R14": ("RUN-PFDR-1b78f7-j0", ["rows.jsonl.gz", "staircase.jsonl.gz", "execution.json", "merge-report.json"]),
    "R15": ("RUN-PFDR-1b78f7-analysis", ["analysis.json", "kappa-cells.jsonl", "fits.json", "view-map.json"]),
    "R16": ("RUN-PFDR-1b78f7-stage-r", ["rows.jsonl.gz", "staircase.jsonl.gz", "execution.json", "merge-report.json",
                                        "analysis.json", "view-map-stage-r.json"]),
}
ATTEMPT = ["jobs-index.json", "manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log",
           "checksums.sha256", "raw-result.json"]
JOB = ["rows.jsonl.gz", "harvest-rows.jsonl.gz", "staircase.jsonl.gz", "command.txt", "stdout.log", "stderr.log",
       "execution.json"]
MERGED = ["rows.jsonl.gz", "staircase.jsonl.gz", "execution.json", "merge-report.json", "manifest.yaml",
          "raw-result.json", "checksums.sha256"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def verify_checksums(d):
    cf = os.path.join(d, "checksums.sha256")
    res = {"dir": os.path.relpath(d, WT), "entries": 0, "ok": 0, "bad": [], "missing": [], "unlisted": []}
    if not os.path.exists(cf):
        res["absent"] = True
        return res
    rl.opened(cf, "J1(b): checksums.sha256 verified")
    listed = set()
    for line in open(cf):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        h, _, name = line.partition("  ")
        name = name.lstrip("*")
        res["entries"] += 1
        fp = os.path.normpath(os.path.join(d, name))
        listed.add(fp)
        if not os.path.exists(fp):
            res["missing"].append(name)
        elif sha(fp) != h:
            res["bad"].append(name)
        else:
            res["ok"] += 1
    # scope: every file under d that is not under a subdirectory holding its own checksums.sha256
    for root, dirs, files in os.walk(d):
        if root != d and os.path.exists(os.path.join(root, "checksums.sha256")):
            dirs[:] = []
            continue
        for fn in files:
            fp = os.path.normpath(os.path.join(root, fn))
            if fn == "checksums.sha256" and root == d:
                continue
            if fp not in listed:
                res["unlisted"].append(os.path.relpath(fp, d))
    return res


def main():
    out = {"required": {}, "checksums": []}
    for rid, (name, data) in RUNMAP.items():
        rd = os.path.join(RUNS, name)
        miss = [f for f in PER_RUN + data if not os.path.exists(os.path.join(rd, f))]
        ent = {"run_dir": name, "missing": miss}
        if rid == "R11":
            ent["merged_missing"] = [f for f in MERGED if not os.path.exists(os.path.join(rd, "merged", f))]
        for att in sorted(glob.glob(os.path.join(rd, "attempt-*"))):
            am = [f for f in ATTEMPT if not os.path.exists(os.path.join(att, f))]
            jobs = sorted(glob.glob(os.path.join(att, "jobs", "*")))
            jm = {os.path.basename(j): [f for f in JOB if not os.path.exists(os.path.join(j, f))] for j in jobs}
            jm = {k: v for k, v in jm.items() if v}
            ent[os.path.basename(att)] = {"missing": am, "jobs": len(jobs), "jobs_missing": jm}
            ic = os.path.join(att, "invocation-check")
            if os.path.isdir(ic):
                ent[os.path.basename(att) + "/invocation-check"] = {
                    "missing": [f for f in ATTEMPT if not os.path.exists(os.path.join(ic, f))],
                    "job_missing": [f for f in JOB if not os.path.exists(os.path.join(ic, "b26-c0", f))]}
        out["required"][rid] = ent
    for cf in sorted(glob.glob(os.path.join(RUNS, "**", "checksums.sha256"), recursive=True)):
        out["checksums"].append(verify_checksums(os.path.dirname(cf)))
    with open(os.path.join(W, "checks", "out", "j1b-artifacts.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    for rid, e in out["required"].items():
        flat = {k: v for k, v in e.items() if k != "run_dir"}
        print(rid, json.dumps(flat)[:300])
    for c in out["checksums"]:
        flag = "" if (not c["bad"] and not c["missing"] and not c.get("absent")) else "  <-- PROBLEM"
        print(f"{c['dir']}: entries {c['entries']} ok {c['ok']} bad {c['bad']} missing {c['missing']} unlisted {c['unlisted'][:6]}{flag}")


if __name__ == "__main__":
    main()
