"""J1(d): seeds, cells and counts from the rows (canonical sets as archived: R10 root,
R11 merged/, R12/R14/R16 roots, R13 root). Seeds that the rows do not record (random-arm
and solver seeds; fb_params strips 'seed' by the CLI's row format, __main__.py line 653)
are checked statically in __main__.py and dynamically by J4(c)."""
import collections, gzip, json, os, sys
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
RUNS = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs")
MAIN_ARMS = ["subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
             "random_dick_r0", "random_dick_r1", "random_dick_r2"]


def load(rel, note):
    p = os.path.join(RUNS, rel)
    rl.opened(p, note)
    return [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]


def m_of(r):
    return r.get("m") if r.get("m") is not None else (int(r["method"][4:]) if str(r.get("method", "")).startswith("ic_m") else None)


def main():
    R = {"R10": load("RUN-PFDR-1b78f7-census-m3/rows.jsonl.gz", "J1(d): R10 rows"),
         "R11": load("RUN-PFDR-1b78f7-census-m4/merged/rows.jsonl.gz", "J1(d): R11 merged rows"),
         "R12": load("RUN-PFDR-1b78f7-census-m5/rows.jsonl.gz", "J1(d): R12 rows"),
         "R13": load("RUN-PFDR-1b78f7-rho/rows.jsonl.gz", "J1(d): R13 rows"),
         "R14": load("RUN-PFDR-1b78f7-j0/rows.jsonl.gz", "J1(d): R14 rows"),
         "R16": load("RUN-PFDR-1b78f7-stage-r/rows.jsonl.gz", "J1(d): R16 rows")}
    out = {"counts": {k: len(v) for k, v in R.items()}, "problems": []}
    P = out["problems"]
    curves = {}  # (bits, c) -> (p, a, b, N)
    j0curves = {}
    for lab, rows in R.items():
        keys = collections.Counter()
        for r in rows:
            cv = (r.get("p"), r.get("a"), r.get("b"), r.get("N"))
            if r.get("panel") in ("main", "rho"):
                old = curves.setdefault((r["bits"], r["curve"]), cv)
                if old != cv:
                    P.append([lab, "curve differs across runs", r["bits"], r["curve"]])
            else:
                old = j0curves.setdefault((r["bits"], r["curve"]), cv)
                if old != cv:
                    P.append([lab, "j0 curve differs between rows", r["bits"], r["curve"]])
            if r.get("method") == "rho":
                keys[("rho", r["bits"], r["curve"])] += 1
                continue
            m = m_of(r)
            keys[(m, r["bits"], r["curve"], r["arm"], r["mode"])] += 1
            if r.get("target_label") != "census":
                P.append([lab, "target_label", r["bits"], r["curve"], r["arm"], r["mode"], r.get("target_label")])
            if r.get("harvest", {}).get("target_label") != "census":
                P.append([lab, "harvest.target_label", r["bits"], r["curve"], r["arm"], r["mode"]])
            if r.get("harvest", {}).get("mode") != r.get("mode"):
                P.append([lab, "harvest.mode != mode", r["bits"], r["curve"], r["arm"], r["mode"]])
            if r["arm"] == "known_log" and not (m == 3 and r["bits"] <= 24):
                P.append([lab, "known_log outside m=3, bits<=24", r["bits"], r["curve"]])
        dup = [k for k, n in keys.items() if n > 1]
        if dup:
            P.append([lab, "duplicate keys", dup[:5]])
        out[f"{lab}_curves"] = sorted(set(k[2] if k[0] != "rho" else k[2] for k in keys))
        out[f"{lab}_bits"] = sorted(set(k[1] for k in keys))
        out[f"{lab}_modes"] = sorted(set(k[4] for k in keys if k[0] != "rho"))
        out[f"{lab}_arms"] = sorted(set(k[3] for k in keys if k[0] != "rho"))
        out[f"{lab}_m"] = sorted(set(k[0] for k in keys if k[0] != "rho"), key=str)
    # A_fix = s_sub on every arm of a main job; = s (j0_coset size) on j0 jobs
    for lab in ["R10", "R11", "R12", "R16"]:
        jobs = collections.defaultdict(dict)
        for r in R[lab]:
            if r.get("method") == "rho":
                continue
            jobs[(m_of(r), r["bits"], r["curve"])][(r["arm"], r["mode"])] = r
        for jk, d in jobs.items():
            ssub = None
            for (arm, mode), r in d.items():
                if arm.startswith("random_sub"):
                    ssub = r["fb_size"]
            if ssub is None:  # R16 dickson cells: s_sub not in the job; A_fix must equal across arms
                vals = set(r["harvest"]["attempt_budget_A_fix"] for r in d.values())
                if len(vals) != 1:
                    P.append([lab, "A_fix differs within job", jk])
                continue
            for (arm, mode), r in d.items():
                if r["harvest"]["attempt_budget_A_fix"] != ssub:
                    P.append([lab, "A_fix != s_sub", jk, arm, mode])
    for r in R["R14"]:
        if r.get("method") == "rho":
            continue
    j0jobs = collections.defaultdict(dict)
    for r in R["R14"]:
        if r.get("method") != "rho":
            j0jobs[(r["bits"], r["curve"])][(r["arm"], r["mode"])] = r
    for jk, d in j0jobs.items():
        s = d[("j0_coset", "census")]["fb_size"]
        for (arm, mode), r in d.items():
            if r["harvest"]["attempt_budget_A_fix"] != s or r["fb_size"] != s:
                P.append(["R14", "A_fix or |F| != s", jk, arm, mode])
    # expected counts
    exp = {"R10": 990 + 70, "R11": 990, "R12": 990, "R13": 110, "R14": 280 + 35, "R16": 160}
    out["expected_counts"] = exp
    out["counts_match"] = {k: out["counts"][k] == v for k, v in exp.items()}
    out["main_panel_total"] = out["counts"]["R10"] + out["counts"]["R11"] + out["counts"]["R12"]
    # R16 curves = R13 curves 5..9 at the same bits (replication curves are the rho curves 5..9)
    out["distinct_main_curves"] = len(curves)
    out["distinct_j0_curves"] = len(j0curves)
    # distinct primes per rung (main panel, 10 curves; j0 5 curves)
    for name, cmap, nper in [("main", curves, 10), ("j0", j0curves, 5)]:
        byb = collections.defaultdict(list)
        for (b, c), cv in cmap.items():
            byb[b].append(cv[0])
        out[f"{name}_distinct_primes_per_rung"] = {b: (len(set(v)), len(v)) for b, v in sorted(byb.items())}
    with open(os.path.join(W, "checks", "out", "j1d-cells.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "problems"}, default=str)[:3000])
    print("problems:", len(P), P[:10])


if __name__ == "__main__":
    main()
