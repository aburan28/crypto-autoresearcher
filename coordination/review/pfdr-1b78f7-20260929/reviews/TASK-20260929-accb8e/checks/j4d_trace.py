"""J4(d): raw/summary agreement. Every number in each raw-result.json (canonical, attempt and
IE-1 locations; R10, R13 roots) is recomputed from the rows it summarises; the execution
report's per-run G4-G7 counts, run wall/peak figures and the j0 cell table are traced to
rows, jobs-index.json and execution.json. R15's raw-result.json was already byte-reproduced
(J4(a)); its outcome values are checked in J3. No A7 value is read."""
import collections, glob, gzip, json, os, sys
import yaml
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
RUNS = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs")


def rows_at(d):
    p = os.path.join(d, "rows.jsonl.gz")
    if os.path.exists(p):
        rl.opened(p, "J4(d): rows for raw-result trace")
        return [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
    out = []
    for jd in sorted(glob.glob(os.path.join(d, "jobs", "*"))) + ([os.path.join(d, "b26-c0")] if os.path.isdir(os.path.join(d, "b26-c0")) else []):
        pj = os.path.join(jd, "rows.jsonl.gz")
        if os.path.exists(pj):
            out += [json.loads(l) for l in gzip.open(pj, "rt") if l.strip()]
    rl.log(d, "J4(d): job rows under this attempt for raw-result trace")
    return out


def summarize(rows):
    s = {"by": collections.Counter(), "cert": collections.Counter(), "solved": 0, "verified": 0,
         "harvest_instances": 0, "g6g7": collections.Counter(), "G5_fail": 0}
    for r in rows:
        if r.get("method") == "rho":
            s["by"][f"{r.get('panel')}|rho|-|{r.get('status')}"] += 1
            if r.get("status") == "completed_valid":
                s["solved"] += 1
                s["verified"] += bool(r.get("ok"))
            continue
        s["by"][f"{r.get('panel')}|{r.get('arm')}|{r.get('mode')}|{r.get('status')}"] += 1
        if r.get("status") != "completed_valid":
            continue
        if r.get("k_found"):
            s["solved"] += 1
            s["verified"] += bool(r.get("k_verified"))
        h = r.get("harvest")
        if h:
            s["harvest_instances"] += 1
            for c in ("SS", "TB", "TT"):
                st = h[c]["at_stop"]
                s["cert"][f"{c}_cert_pass"] += st["cert_pass"]
                s["cert"][f"{c}_cert_fail"] += st["cert_fail"]
                s["cert"][f"{c}_rows_emitted"] += st["rows_emitted"]
            if not h["ss_store"].get("identity_ok"):
                s["G5_fail"] += 1
        for k, v in (r.get("checks") or {}).items():
            s["g6g7"][f"{k}|{'pass' if v is True else 'fail'}"] += 1
    return s


def cmp(tag, a, b, res):
    ok = a == b
    res.append({"item": tag, "recomputed": a, "recorded": b, "agree": ok})
    return ok


def main():
    locs = ["RUN-PFDR-1b78f7-census-m3", "RUN-PFDR-1b78f7-census-m4", "RUN-PFDR-1b78f7-census-m4/merged",
            "RUN-PFDR-1b78f7-census-m4/attempt-2", "RUN-PFDR-1b78f7-census-m4/attempt-2/invocation-check",
            "RUN-PFDR-1b78f7-census-m5", "RUN-PFDR-1b78f7-census-m5/attempt-1", "RUN-PFDR-1b78f7-rho",
            "RUN-PFDR-1b78f7-j0", "RUN-PFDR-1b78f7-j0/attempt-1", "RUN-PFDR-1b78f7-stage-r",
            "RUN-PFDR-1b78f7-stage-r/attempt-1"]
    out = {"raw_result": {}, "execution_report": []}
    sums = {}
    for loc in locs:
        d = os.path.join(RUNS, loc)
        rr = json.load(open(rl.opened(os.path.join(d, "raw-result.json"), "J4(d): raw-result.json traced")))
        rows = rows_at(d)
        s = summarize(rows)
        sums[loc] = s
        res = []
        by = rr.get("by_panel_arm_mode_status") or rr.get("by_status") or {}
        if by and isinstance(by, dict) and all("|" in k for k in by):
            mine = {k: v for k, v in s["by"].items()}
            # rho rows: the producer may key them differently; compare the non-rho part exactly
            cmp("by_panel_arm_mode_status (non-rho keys)", {k: v for k, v in mine.items() if "|rho|" not in k},
                {k: v for k, v in by.items() if "rho" not in k}, res)
        cert = rr.get("certificate") or {}
        hc = cert.get("harvested_row_check") or {}
        if hc:
            cmp("harvested_row_check", dict(s["cert"]), {k: hc[k] for k in hc}, res)
        if "solved_instances" in cert:
            cmp("certificate.solved_instances", s["solved"], cert["solved_instances"], res)
        if "verified" in cert and not isinstance(cert["verified"], bool):
            cmp("certificate.verified (count)", s["verified"], cert["verified"], res)
        g = rr.get("gates") or {}
        if "harvest_instances" in g:
            cmp("gates.harvest_instances", s["harvest_instances"], g["harvest_instances"], res)
        if "G6_G7_check_counts" in g:
            cmp("gates.G6_G7_check_counts", dict(s["g6g7"]), g["G6_G7_check_counts"], res)
        if "G4" in g:
            G4 = g["G4"]
            if "solved_instances" in G4:
                cmp("gates.G4.solved_instances", s["solved"], G4["solved_instances"], res)
            if "solved_verified" in G4:
                cmp("gates.G4.solved_verified", s["verified"], G4["solved_verified"], res)
        if "G5" in g and "identity_failures" in g["G5"]:
            v = g["G5"]["identity_failures"]
            cmp("gates.G5.identity_failures", s["G5_fail"], v if isinstance(v, int) else len(v), res)
        inst = rr.get("instances") or {}
        if "present" in inst:
            cmp("instances.present", len(rows), inst["present"], res)
        out["raw_result"][loc] = {"checks": res, "all_agree": all(x["agree"] for x in res), "n_checks": len(res)}
    # execution report
    er = yaml.safe_load(open(rl.opened(os.path.join(WT, "experiments/EXP-PFDR-1b78f7/execution-report-amd430f44.yaml"), "J4(d): execution report numbers traced (loaded programmatically; A7 not accessed)")))["execution_report"]
    pr = er["gates"]["per_run_G4_G7_counts"]
    mapping = {"R11_merged": "RUN-PFDR-1b78f7-census-m4/merged", "R11_IE-1_check": "RUN-PFDR-1b78f7-census-m4/attempt-2/invocation-check",
               "R12": "RUN-PFDR-1b78f7-census-m5", "R14": "RUN-PFDR-1b78f7-j0", "R16": "RUN-PFDR-1b78f7-stage-r", "R13": "RUN-PFDR-1b78f7-rho"}
    res = out["execution_report"]
    for k, loc in mapping.items():
        s = sums[loc]
        e = pr[k]
        cmp(f"{k}.harvest_instances", s["harvest_instances"], e["harvest_instances"], res)
        if isinstance(e.get("G4_row_certificates"), dict):
            cmp(f"{k}.G4_row_certificates", dict(s["cert"]), e["G4_row_certificates"], res)
        sv = e.get("G4_solved_instances_kP_eq_Q_verified")
        if isinstance(sv, str) and "/" in sv:
            a, b = sv.split("/")
            cmp(f"{k}.G4 solved verified", f"{s['verified']}/{s['solved']}", f"{a}/{b}", res)
        if isinstance(e.get("G6_G7_check_counts"), dict):
            cmp(f"{k}.G6_G7_check_counts", dict(s["g6g7"]), e["G6_G7_check_counts"], res)
    # run wall/peak figures
    for rid, loc, key in [("R11", "RUN-PFDR-1b78f7-census-m4/attempt-2", 2), ("R12", "RUN-PFDR-1b78f7-census-m5/attempt-1", 0),
                          ("R14", "RUN-PFDR-1b78f7-j0/attempt-1", 0), ("R16", "RUN-PFDR-1b78f7-stage-r/attempt-1", 0)]:
        ji = json.load(open(os.path.join(RUNS, loc, "jobs-index.json")))
        run = [x for x in er["runs"]["completed"] if x["id"] == rid][0]
        att = [a for a in run["attempts"] if a["attempt"] == loc.split("/")[-1]][0]
        cmp(f"{rid} {loc.split('/')[-1]} wall_seconds (report, 1 dp)", round(ji["wall_seconds"], 1), att.get("wall_seconds"), res)
        if "peak_job_rss_bytes" in att:
            cmp(f"{rid} peak_job_rss_bytes", max(j["peak_rss_bytes"] for j in ji["jobs"]), att["peak_job_rss_bytes"], res)
    r13 = [x for x in er["runs"]["completed"] if x["id"] == "R13"][0]
    ex13 = json.load(open(os.path.join(RUNS, "RUN-PFDR-1b78f7-rho/execution.json")))
    cmp("R13 wall_seconds", round(ex13.get("wall_seconds"), 3), r13.get("wall_seconds"), res)
    # j0 cell table vs R14 rows
    rows14 = [json.loads(l) for l in gzip.open(os.path.join(RUNS, "RUN-PFDR-1b78f7-j0/rows.jsonl.gz"), "rt")]
    cells = {}
    for r in rows14:
        cells[(r["bits"], r["curve"])] = r
    bad = []
    for c in er["j0_cells"]["cells"]:
        r = cells[(c["bits"], c["curve"])]
        gen = r["j0_generation"]
        fin = [x for x in gen if "prime_draws" in x][0]
        sk = [x for x in gen if "reason" in x]
        if (r["p"], r["b"], r["N"], fin["prime_draws"], sk) != (c["p"], c["b"], c["N"], c["prime_draws"], c["skipped_primes"]):
            bad.append([c["bits"], c["curve"]])
    cmp("j0_cells table == R14 rows (p, b, N, prime_draws, skipped_primes) for all 35", [], bad, res)
    cmp("j0 skipped_primes_total", sum(len([x for x in r["j0_generation"] if "reason" in x]) for r in cells.values()), er["j0_cells"]["skipped_primes_total"], res)
    with open(os.path.join(W, "checks", "out", "j4d-trace.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    for loc, v in out["raw_result"].items():
        print(loc, "checks", v["n_checks"], "all agree", v["all_agree"], [x["item"] for x in v["checks"] if not x["agree"]])
    print("execution report checks", len(res), "disagree:", [x for x in res if not x["agree"]])


if __name__ == "__main__":
    main()
