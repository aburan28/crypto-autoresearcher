"""J2b (after the seal), part 2: my sealed J2a lists against each merge-report.json; the
view maps (view-map.json of R15, view-map-stage-r.json of R16) against the archived
files, with DEV-B's declared exceptions; the M-5 execution.json aggregates against the
per-attempt / per-job records."""
import glob, gzip, hashlib, json, os, sys, collections
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
RUNS = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs")
EXP = "experiments/EXP-PFDR-1b78f7/runs"
LOC = {"R11": "RUN-PFDR-1b78f7-census-m4/merged", "R12": "RUN-PFDR-1b78f7-census-m5",
       "R14": "RUN-PFDR-1b78f7-j0", "R16": "RUN-PFDR-1b78f7-stage-r"}
READ_BY_ANALYSIS = ("rows.jsonl.gz", "staircase.jsonl.gz", "execution.json", "raw-result.json", "regression-report.json")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def main():
    out = {"merge_reports": {}, "view_maps": {}, "execution_aggregates": {}}
    mine = json.load(open(rl.opened(os.path.join(W, "rederivation/out/j2a-report.json"), "J2b: my sealed j2a-report.json")))
    for lab, loc in LOC.items():
        d = os.path.join(RUNS, loc)
        mr = json.load(open(rl.opened(os.path.join(d, "merge-report.json"), f"J2b: merge-report {lab} (blind_from)")))
        me = mine[lab]
        r = {"U_size": [me["U_size"], mr.get("U_size")]}
        src = collections.Counter(v.get("attempt") for v in (mr.get("per_key_source") or {}).values())
        r["per_key_source_counts"] = [me["counts_by_source"], dict(src)]
        ph = mr.get("placeholders")
        r["placeholders"] = [len(me["placeholders"]), len(ph) if isinstance(ph, (list, dict)) else ph]
        nc = mr.get("non_cell_rows_excluded")
        nck = sorted(json.dumps(x.get("key") if isinstance(x, dict) else x) for x in (nc or [])) if isinstance(nc, list) else nc
        mk = sorted(json.dumps(x["key"]) for x in me["noncell_rows"])
        r["noncell"] = {"mine": len(mk), "theirs": len(nc) if isinstance(nc, list) else nc,
                        "key_sets_equal": (mk == nck) if isinstance(nck, list) else None}
        if lab == "R11":
            rs = mr.get("resume_set", {})
            theirs = sorted(rs.get("jobs", []))
            mine_rs = sorted(f"b{b}-c{c}" for b, c in me["resume_set"])
            r["resume_set_equal"] = (theirs == mine_rs) or (sorted(map(str, theirs)) == sorted(map(str, [[b, c] for b, c in me["resume_set"]])))
            r["resume_set_asserted_equal_to_M2"] = rs.get("asserted_equal_to_M2")
        # canonical file hashes recorded vs archived
        can = mr.get("canonical_files_sha256") or mr.get("canonical_sha256") or {}
        chk = {}
        for fn in ("rows.jsonl.gz", "staircase.jsonl.gz"):
            rec = can.get(fn) if isinstance(can, dict) else None
            chk[fn] = {"recorded": rec, "archived": sha(os.path.join(d, fn)), "equal": rec == sha(os.path.join(d, fn))}
        r["canonical_hashes"] = chk
        r["counts_by_status"] = [me["counts_by_status"], mr.get("counts_by_status")]
        inp = mr.get("inputs") or []
        r["inputs"] = {"n": len(inp), "all_match_receipt": all(x.get("matches_receipt") in (True, None) for x in inp),
                       "not_matching": [x.get("path") for x in inp if x.get("matches_receipt") is False]}
        # verify each input hash against the archived file now
        bad = []
        for x in inp:
            p = os.path.join(WT, x["path"]) if x.get("path") and not os.path.isabs(x["path"]) else x.get("path")
            if p and os.path.exists(p) and x.get("sha256") and sha(p) != x["sha256"]:
                bad.append(x["path"])
        r["inputs_rehashed_mismatch"] = bad
        r["top_keys"] = sorted(mr.keys())
        out["merge_reports"][lab] = r
    # view maps
    for name, p in [("view-map.json (R15)", os.path.join(RUNS, "RUN-PFDR-1b78f7-analysis/view-map.json")),
                    ("view-map-stage-r.json (R16)", os.path.join(RUNS, "RUN-PFDR-1b78f7-stage-r/view-map-stage-r.json"))]:
        vm = json.load(open(rl.opened(p, f"J2b: {name} (blind_from)")))
        res = {"entries": len(vm["entries"]), "target_rule_violations": [], "hash_mismatches": [], "missing_files": [],
               "unlisted_files_now": {}}
        for e in vm["entries"]:
            link, tgt = e["link"], e["target"]
            run_root = f"{EXP}/{link}"
            expect = f"{run_root}/merged" if os.path.isdir(os.path.join(WT, run_root, "merged")) else run_root
            if tgt.rstrip("/") != expect:
                res["target_rule_violations"].append([link, tgt, expect])
            td = os.path.join(WT, tgt)
            for fn, h in e["files_sha256"].items():
                fp = os.path.join(td, fn)
                if not os.path.exists(fp):
                    res["missing_files"].append(f"{tgt}/{fn}")
                elif sha(fp) != h:
                    res["hash_mismatches"].append(f"{tgt}/{fn}")
            now = set()
            for root, dirs, files in os.walk(td):
                for fn in files:
                    now.add(os.path.relpath(os.path.join(root, fn), td))
            extra = sorted(now - set(e["files_sha256"]))
            if extra:
                res["unlisted_files_now"][tgt] = extra[:10] + ([f"... {len(extra)}"] if len(extra) > 10 else [])
        res["links"] = sorted(e["link"] for e in vm["entries"])
        res["mismatch_files_read_by_analysis"] = [x for x in res["hash_mismatches"] if x.endswith(READ_BY_ANALYSIS)]
        out["view_maps"][name] = res
    rl.log(RUNS, "J2b: rehashed every file listed in both view maps and every merge-report input")
    # execution.json aggregates
    for lab, loc in LOC.items():
        d = os.path.join(RUNS, loc)
        ex = json.load(open(rl.opened(os.path.join(d, "execution.json"), f"J2b: M-5 aggregated execution.json {lab}")))
        root = os.path.join(RUNS, loc.split("/")[0])
        peaks, cpus, walls = [], [], []
        parts = []
        if lab == "R11":
            a1 = json.load(open(rl.opened(os.path.join(root, "execution.json"), "J2b: R11 attempt-1 root execution.json")))
            parts.append(("attempt-1", a1.get("peak_rss_bytes_max_descendant"), a1.get("cpu_seconds_descendants"), a1.get("wall_seconds")))
        for att in sorted(glob.glob(os.path.join(root, "attempt-*"))):
            ji = json.load(open(rl.opened(os.path.join(att, "jobs-index.json"), f"J2b: {lab} jobs-index for aggregate")))
            jp = [j.get("peak_rss_bytes") or 0 for j in ji["jobs"]]
            jc = [j.get("cpu_seconds") or 0 for j in ji["jobs"]]
            # per-job execution.json cross-check
            jx = []
            for j in ji["jobs"]:
                pe = os.path.join(WT, j["job_dir"], "execution.json")
                if os.path.exists(pe):
                    jx.append(json.load(open(pe)))
            parts.append((os.path.basename(att), max(jp) if jp else None, sum(jc), ji.get("wall_seconds")))
            out["execution_aggregates"].setdefault(lab, {})[f"{os.path.basename(att)}_job_execution_json_read"] = len(jx)
            out["execution_aggregates"][lab][f"{os.path.basename(att)}_job_exec_peak_max"] = max((x.get("peak_rss_bytes_max_descendant") or x.get("peak_rss_bytes") or 0) for x in jx) if jx else None
        rl.log(root, f"J2b: {lab} per-job execution.json files read for the aggregate cross-check")
        agg_peak = max(p for _, p, _, _ in parts if p is not None)
        agg_cpu = sum(c for _, _, c, _ in parts if c is not None)
        agg_wall = sum(w for _, _, _, w in parts if w is not None)
        out["execution_aggregates"][lab].update({
            "recorded": {k: ex.get(k) for k in ("peak_rss_bytes_max_descendant", "cpu_seconds_descendants", "wall_seconds", "label")},
            "recomputed": {"peak": agg_peak, "cpu": round(agg_cpu, 3), "wall": round(agg_wall, 3)}, "parts": parts,
            "peak_equal": ex.get("peak_rss_bytes_max_descendant") == agg_peak,
            "cpu_close": abs((ex.get("cpu_seconds_descendants") or 0) - agg_cpu) < 0.01,
            "wall_close": abs((ex.get("wall_seconds") or 0) - agg_wall) < 0.01})
    with open(os.path.join(W, "checks", "out", "j2b-views.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    for lab, r in out["merge_reports"].items():
        print(lab, {k: v for k, v in r.items() if k not in ("top_keys",)})
    for n, r in out["view_maps"].items():
        print(n, {k: v for k, v in r.items() if k != "links"})
    for lab, r in out["execution_aggregates"].items():
        print(lab, {k: r[k] for k in ("recorded", "recomputed", "peak_equal", "cpu_close", "wall_close")})


if __name__ == "__main__":
    main()
