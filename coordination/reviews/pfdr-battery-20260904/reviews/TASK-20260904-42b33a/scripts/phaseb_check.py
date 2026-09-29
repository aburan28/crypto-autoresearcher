"""PHASE B: joints V2 (run-set validity / pinning / seeds), V3 (manifest side) and
V4 (CTRL-DFF-AGREEMENT and cross-engine coverage) from the manifests, sidecars and
the meter package only.

Files listed in review_plan.blind_rederivation.blind_from are NEVER opened here.
raw-result.json and stdout.log are HASHED (never read) to verify package-sha256.json;
that is the same allowance the plan grants for stage1-closure-convention.md.
"""
import hashlib
import json
import os
import sys
import yaml

REPO = "/home/user/crypto-autoresearcher/"
EXP = REPO + "experiments/EXP-PFDR-cbdefb/"
OUT = (REPO + "coordination/reviews/pfdr-battery-20260904/reviews/"
              "TASK-20260904-42b33a/tables/phaseb_checks.json")

CONTRACT = {
    "curve_seeds": [3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108],
    "target_seeds": [1, 2, 3, 4, 5],
    "null_seeds": [7, 11, 13, 17, 19],
    "D_max": 7,
    "plant_window": 4,
    "commit": "3029ff1466011c8a8b93e8614ebe3dc1201e08e1",
    "wall_clock_seconds_per_run": 7200,
    "maximum_runs": 48,
    "total_cpu_hours": 48,
    "memory_gb": 8,
}
REQUIRED_FILES = ["manifest.yaml", "command.txt", "environment.json", "stdout.log",
                  "stderr.log", "raw-result.json", "package-sha256.json"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def main():
    runs = sorted(os.listdir(EXP + "runs"))
    out = {"n_run_dirs": len(runs), "runs": {}, "aggregate": {}}
    conv_sha_actual = sha(EXP + "stage1-closure-convention.md")   # hashed, NOT opened
    out["stage1_closure_convention_sha256_recomputed"] = conv_sha_actual
    out["stage1_closure_convention_opened"] = False

    closure_hashes, runner_hashes, commits, conv_hashes = {}, {}, {}, {}
    wall_total, cpu_total = 0.0, 0.0
    for rid in runs:
        rd = EXP + "runs/" + rid + "/"
        rec = {"files_present": {}, "missing": [], "sidecar": {}, "checks": {}}
        for fn in REQUIRED_FILES:
            ok = os.path.exists(rd + fn)
            rec["files_present"][fn] = ok
            if not ok:
                rec["missing"].append(fn)
        extra = sorted(set(os.listdir(rd)) - set(REQUIRED_FILES))
        rec["extra_files"] = extra
        m = yaml.safe_load(open(rd + "manifest.yaml"))["run"]
        # ---- sidecar hashes
        pk = json.load(open(rd + "package-sha256.json"))
        side = pk.get("files", pk)
        bad = []
        for fn, want in sorted(side.items()):
            if not isinstance(want, str):
                want = want.get("sha256")
            got = sha(rd + os.path.basename(fn)) if os.path.exists(rd + os.path.basename(fn)) else None
            if got != want:
                bad.append({"file": fn, "declared": want, "recomputed": got})
        rec["sidecar"] = {"n_declared": len(side), "mismatches": bad,
                          "all_match": not bad,
                          "covers_manifest": any("manifest" in k for k in side)}
        # ---- status / pinning
        rec["checks"]["status"] = m["status"]
        rec["checks"]["commit"] = m["code"]["commit"]
        rec["checks"]["dirty"] = m["code"]["dirty"]
        rec["checks"]["command"] = m["code"]["command"]
        cmd_txt = open(rd + "command.txt").read().strip()
        rec["checks"]["command_txt_matches_manifest"] = (cmd_txt == m["code"]["command"].strip())
        src = m["code"]["source"]["files"]
        ch = src.get("experiments/EXP-PFDR-cbdefb/closure.py", {}).get("sha256")
        rh = src.get("experiments/EXP-PFDR-cbdefb/run_cbdefb.py", {}).get("sha256")
        rec["checks"]["closure_py_sha256"] = ch
        rec["checks"]["run_cbdefb_py_sha256"] = rh
        closure_hashes.setdefault(ch, []).append(rid)
        runner_hashes.setdefault(rh, []).append(rid)
        commits.setdefault(m["code"]["commit"], []).append(rid)
        rec["checks"]["all_pinned"] = m["code"]["source"].get("all_pinned")
        rec["checks"]["modified_files"] = m["code"]["source"].get("modified")
        params = m["inputs"]["parameters"]
        cs = params.get("closure_convention", {})
        declared_conv = params.get("closure_convention_sha256") or cs.get("sha256")
        conv_hashes.setdefault(declared_conv, []).append(rid)
        rec["checks"]["closure_convention_sha256_declared"] = declared_conv
        rec["checks"]["closure_convention_sha256_matches_file"] = (declared_conv == conv_sha_actual)
        rec["checks"]["convention_id"] = cs.get("convention_id")
        rec["checks"]["D_max"] = params.get("D_max")
        rec["checks"]["plant_window"] = params.get("plant_window")
        rec["checks"]["curve_seeds"] = params.get("curve_seeds")
        rec["checks"]["target_seeds"] = params.get("target_seeds")
        rec["checks"]["null_seeds"] = params.get("null_seeds")
        rec["checks"]["engine_policy"] = params.get("engine_policy")
        rec["checks"]["budget"] = params.get("budget")
        si = params.get("session_inference", {})
        rec["checks"]["session_inference"] = {
            k: si.get(k) for k in ("requested_policy", "requested_reasoning_effort",
                                   "runtime_reported_model", "model_verified",
                                   "fallback_used", "degraded", "independent_session",
                                   "no_bedrock")}
        # meter pinning
        meter = params.get("meter", {})
        rec["checks"]["meter_commit"] = meter.get("meter_commit")
        rec["checks"]["meter_files_sha256"] = meter.get("files_sha256")
        # timing / resources / stderr
        t = m.get("timing", {})
        rec["checks"]["timing_source"] = t.get("timing_source")
        rec["checks"]["wall_seconds"] = t.get("wall_seconds")
        rec["checks"]["started_at"] = t.get("started_at")
        rec["checks"]["finished_at"] = t.get("finished_at")
        res = m.get("resources", {})
        rec["checks"]["peak_rss_bytes"] = res.get("peak_rss_bytes")
        rec["checks"]["cpu_seconds"] = res.get("cpu_seconds")
        rec["checks"]["stderr_bytes"] = os.path.getsize(rd + "stderr.log")
        rec["checks"]["valid"] = m["result"].get("valid")
        rec["checks"]["invalid_reason"] = m["result"].get("invalid_reason")
        rec["checks"]["certificate"] = m["result"].get("certificate")
        wall_total += t.get("wall_seconds") or 0.0
        cpu_total += res.get("cpu_seconds") or 0.0
        # env
        env = json.load(open(rd + "environment.json"))
        rec["environment"] = env
        # metrics used by V4
        met = m["result"]["metrics"]
        rec["metrics_summary"] = {}
        cell = met.get("cell", {})
        rec["metrics_summary"]["cell"] = {k: cell.get(k) for k in
                                          ("m", "d", "s", "n", "primes", "D_max",
                                           "window", "engine", "columns_at_Dmax")}
        for arm in ("semaev", "null1", "null2", "null3", "noncurve"):
            a = met.get(arm)
            if not a:
                continue
            rec["metrics_summary"][arm] = {
                "n": a.get("n"),
                "d_ff_set": sorted({str(x) for x in (a.get("d_ff_values") or [])}),
                "d_lf_set": sorted({str(x) for x in (a.get("d_lf_values") or [])}),
                "right_censored": a.get("right_censored"),
                "no_fall_in_window": a.get("no_fall_in_window"),
                "min_iteration_count_at_falls": a.get("min_iteration_count_at_falls"),
                "fall_with_iteration_count_1": a.get("fall_with_iteration_count_1"),
                "closure_dff_equals_graded_dff_all": a.get("closure_dff_equals_graded_dff_all"),
                "cross_check_agree_all": a.get("cross_check_agree_all"),
                "cross_checked": a.get("cross_checked"),
            }
        for k in ("P1_closure_dff_equals_graded_dff_all_semaev", "certificates_all_verified",
                  "engine_cross_check_all_agree", "s_poly_crosscheck_all",
                  "not_plantable_draws", "not_computed_wall_guard",
                  "null3_minus_semaev_dff", "null3_minus_semaev_dlf",
                  "semaev_pairs", "noncurve_pairs",
                  "null1_band_offsets_uncensored", "null2_band_offsets_uncensored"):
            if k in met:
                rec["metrics_summary"][k] = met[k]
        if "soundness_subsample" in met:
            rec["metrics_summary"]["soundness_subsample"] = met["soundness_subsample"]
        if "agreement" in met:
            rec["metrics_summary"]["agreement"] = met["agreement"]
        out["runs"][rid] = rec

    out["aggregate"] = {
        "closure_py_sha256_versions": {k: v for k, v in closure_hashes.items()},
        "run_cbdefb_py_sha256_versions": {k: v for k, v in runner_hashes.items()},
        "commits": {k: len(v) for k, v in commits.items()},
        "closure_convention_sha256_declared": {k: len(v) for k, v in conv_hashes.items()},
        "wall_seconds_total": round(wall_total, 3),
        "cpu_seconds_total": round(cpu_total, 3),
        "max_wall_seconds_single_run": max(
            (r["checks"]["wall_seconds"] or 0) for r in out["runs"].values()),
        "n_runs": len(runs),
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print("wrote", OUT)
    ag = out["aggregate"]
    print("runs:", ag["n_runs"], " wall total:", ag["wall_seconds_total"],
          " cpu total:", ag["cpu_seconds_total"],
          " max single-run wall:", ag["max_wall_seconds_single_run"])
    print("commits:", ag["commits"])
    print("closure.py versions:")
    for h, rs in ag["closure_py_sha256_versions"].items():
        print(f"   {h}  x{len(rs)}: {rs}")
    print("run_cbdefb.py versions:")
    for h, rs in ag["run_cbdefb_py_sha256_versions"].items():
        print(f"   {h}  x{len(rs)}")
    print("convention hash declared:", ag["closure_convention_sha256_declared"])
    print("convention hash recomputed from file:", conv_sha_actual)
    bad = [r for r, v in out["runs"].items() if v["missing"] or not v["sidecar"]["all_match"]]
    print("runs with missing files or sidecar mismatch:", bad)
    print("statuses:", sorted({v["checks"]["status"] for v in out["runs"].values()}))
    print("dirty flags:", sorted({str(v["checks"]["dirty"]) for v in out["runs"].values()}))
    print("stderr sizes nonzero:", [r for r, v in out["runs"].items() if v["checks"]["stderr_bytes"]])


if __name__ == "__main__":
    main()
