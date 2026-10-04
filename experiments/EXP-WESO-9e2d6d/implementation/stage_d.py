"""EXP-WESO-9e2d6d STAGE-D (RUN-WESO-0b4b33): FG-D pilot at p_D = 5*2^248 - 1,
then (only if FG-D passes) the Stage-C procedure at p_D with N_D = 10^5, NULL-1,
NULL-2, SEED-1, SEED-2, spot-check, TC-1..TC-4.  Pilot samples are archived in
fg_d_pilot.jsonl.gz and excluded from every Stage-D statistic.

FG-D projection (MODELED, not measured): projected wall at 4 workers =
  (10^5 * mean pilot per-sample wall + 10^5 * mean pilot NULL-1 factorisation
   wall + 10^5 * mean pilot NULL-2 factorisation wall) / 4,
assuming linear scaling with workers.  The pilot null integers (1000 each,
seed D-PILOT, arms PILOT-NULL1 / PILOT-NULL2) exist only to measure null cost
for this projection and are archived with the pilot.

The --session-limit-seconds argument implements the dispatching session's
instruction (not a spec rule): if the projection at the workers actually
available exceeds it, Stage D is checkpointed as an infrastructure/deferred
outcome with the measured pilot cost; that is never evidence.
"""
import argparse
import json
import math
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analysis  # noqa: E402
import common  # noqa: E402
import report  # noqa: E402
import rho as rhomod  # noqa: E402
import sampling  # noqa: E402
import stage_c  # noqa: E402
from run_stage import tree_rss  # noqa: E402

STAGE_B_RUN = "RUN-WESO-f37773"
STAGE_C_RUN = "RUN-WESO-e65afd"
N_PILOT = 1000
N_D = 100000
FACTOR_WD = 600
FGD_LIMIT = 172800


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--max-workers", type=int, default=3)
    ap.add_argument("--session-limit-seconds", type=int, default=10800)
    a = ap.parse_args()
    rd = a.run_dir
    t_start = time.time()
    bdir = os.path.join(common.EXP_DIR, "runs", STAGE_B_RUN)
    cdir = os.path.join(common.EXP_DIR, "runs", STAGE_C_RUN)
    braw = json.load(open(os.path.join(bdir, "raw-result.json")))
    craw = json.load(open(os.path.join(cdir, "raw-result.json")))
    cstat = json.load(open(os.path.join(cdir, "status.json")))
    raw = {"experiment_id": "EXP-WESO-9e2d6d", "run_id": "RUN-WESO-0b4b33", "stage": "STAGE-D",
           "gating": {"gate_G_B": braw["gate_G_B"]["verdict"], "stage_C_status": cstat["status"],
                      "stage_C_validity": cstat["validity"], "stage_C_outcome": craw.get("stage_outcome")}}
    freeze = json.load(open(os.path.join(bdir, "analysis_freeze.json")))["analysis_freeze"]
    now = common.impl_hashes()
    raw["analysis_freeze_check"] = {"unchanged": freeze == now,
                                    "changed_files": sorted(k for k in set(freeze) | set(now) if freeze.get(k) != now.get(k))}
    if braw["gate_G_B"]["verdict"] != "PASS" or cstat["validity"] != "valid":
        common.write_json(os.path.join(rd, "status.json"), {"status": "failed", "validity": "invalid",
                                                            "failure_class": "specification_error",
                                                            "reason": "Stage D gating not met", "stage_outcome": "NOT_RUN"})
        return
    W = craw["DET-1"]["workers_used_after"] if craw["DET-1"]["verdict"] == "PASS" else 1
    W = min(W, a.max_workers)
    ch = stage_c.c_hat_exact(braw)
    gp = common.GP()
    info = stage_c.gp_prime_info(gp, "q=5*2^248-1")
    info["rule"] = "p_D = 5*2^248 - 1 (spec inputs.primes.stage_D); isprime flag 0 = proven"
    kc = stage_c.k_C(ch, int(info["p"]))
    info["k_C"] = kc
    raw["prime"] = info
    raw["c_hat"] = float(ch)
    raw["workers"] = W
    p = int(info["p"])
    X = int(info["X_max"])
    common.log("p_D", info)
    if info["isprime_flag0"] != "1" or info["p_mod_4"] != "3":
        common.write_json(os.path.join(rd, "status.json"), {"status": "failed", "validity": "invalid", "failure_class": "implementation_error",
                                                            "reason": "p_D not proven prime / not 3 mod 4", "stage_outcome": "STOPPED"})
        return
    raw["V-RHO"] = rhomod.validate()

    # ------------------------------ FG-D pilot ------------------------------
    peak = {"rss": 0}
    stop = threading.Event()

    def mon():
        while not stop.is_set():
            peak["rss"] = max(peak["rss"], tree_rss(os.getpid()))
            stop.wait(1.0)
    th = threading.Thread(target=mon, daemon=True)
    th.start()
    ctx = {"p": p, "start_basis": "O0basis()", "Kmax": kc + 2, "factor_watchdog_s": FACTOR_WD}
    tp0 = time.time()
    ptasks = sampling.make_tasks(common.SEEDS["D-PILOT"], "D", p, "PILOT", N_PILOT, kc)
    pilot = sampling.run_draws(ctx, ptasks, W)
    tp1 = time.time()
    n1t, n2t = [], []
    for i, r in enumerate(pilot):
        b = int(r["delta"]).bit_length()
        sd = common.draw_seed(common.SEEDS["D-PILOT"], "D", p, "PILOT-NULL1", i)
        n1t.append({"arm": "PILOT-NULL1", "index": i, "seed": sd, "n": (1 << (b - 1)) + common.Stream(sd).randbelow(1 << (b - 1))})
        sd = common.draw_seed(common.SEEDS["D-PILOT"], "D", p, "PILOT-NULL2", i)
        n2t.append({"arm": "PILOT-NULL2", "index": i, "seed": sd, "n": 1 + common.Stream(sd).randbelow(X)})
    pn1 = sampling.run_nulls(n1t, W, watchdog=FACTOR_WD)
    pn2 = sampling.run_nulls(n2t, W, watchdog=FACTOR_WD)
    tp2 = time.time()
    stop.set()
    th.join()
    common.write_jsonl_gz(os.path.join(rd, "fg_d_pilot.jsonl.gz"),
                          [dict(r, p=str(p)) for r in pilot] + [dict(r, p=str(p)) for r in pn1 + pn2])
    ms = sum(r["wall_s"] for r in pilot) / N_PILOT
    m1 = sum(r["wall_s"] for r in pn1) / N_PILOT
    m2 = sum(r["wall_s"] for r in pn2) / N_PILOT
    fails = sum(1 for r in pilot if r["fac_ok"] == 0)
    wdh = sum(1 for r in pilot if r["fac_ok"] == -1)
    nfails = sum(1 for r in pn1 + pn2 if r["fac_ok"] != 1)
    bound_ok = all(int(r["delta"]) <= X for r in pilot)
    proj4 = (N_D * ms + N_D * m1 + N_D * m2) / 4
    projW = (N_D * ms + N_D * m1 + N_D * m2) / W
    fgd_pass = (fails == 0 and wdh == 0 and bound_ok and proj4 <= FGD_LIMIT)
    fgd = {"pilot_samples": N_PILOT, "seed": common.SEEDS["D-PILOT"], "k_C": kc, "workers_during_pilot": W,
           "measured": {"mean_wall_s_per_sample": ms, "max_wall_s_per_sample": max(r["wall_s"] for r in pilot),
                        "mean_wall_s_per_null1_factorisation": m1, "mean_wall_s_per_null2_factorisation": m2,
                        "pilot_samples_elapsed_s": round(tp1 - tp0, 2), "pilot_nulls_elapsed_s": round(tp2 - tp1, 2),
                        "peak_rss_process_tree_bytes_sampled_1s": peak["rss"],
                        "factorisation_failures": fails, "factorisation_watchdog_hits": wdh,
                        "pilot_null_factorisation_failures_or_watchdog": nfails,
                        "every_pilot_delta_le_X": bound_ok, "X_max": str(X),
                        "max_pilot_delta": str(max(int(r["delta"]) for r in pilot)),
                        "C-2_flags_not_1": sum(1 for r in pilot if r["c2"] != 1),
                        "U-2_failures": sum(1 for r in pilot if r["u2"] != 1)},
           "modeled": {"projected_wall_s_at_4_workers": proj4, "projected_wall_s_at_session_workers": projW,
                       "assumption": "linear scaling in workers; per-sample and per-null wall times as measured in the pilot "
                                     "with %d concurrent workers" % W, "limit_s": FGD_LIMIT},
           "verdict": "PASS" if fgd_pass else "FAIL (INFEASIBLE_AT_DECLARED_RESOURCES)"}
    raw["FG-D"] = fgd
    common.log("FG-D", fgd["verdict"], "mean s/sample %.4f proj4 %.0f s projW %.0f s" % (ms, proj4, projW))
    devs = []
    if a.max_workers != 4:
        devs.append("Stage D ran with %d workers (host shared; dispatching session cap 3), not 4; the FG-D projection is "
                    "nevertheless evaluated at 4 workers as frozen (modeled, linear scaling)." % W)
    devs.append("FG-D projection needs null factorisation cost; 1000 PILOT-NULL1 and 1000 PILOT-NULL2 integers (seed D-PILOT) "
                "were factored to measure it and are archived in fg_d_pilot.jsonl.gz, excluded from every statistic.")
    status = None
    if not fgd_pass:
        raw["stage_outcome"] = "FG-D INFEASIBLE_AT_DECLARED_RESOURCES (SR-6; infrastructure outcome, never evidence)"
        status = {"status": "completed_valid", "validity": "valid", "failure_class": None,
                  "reason": "FG-D failed; Stage D checkpointed", "stage_outcome": raw["stage_outcome"]}
    elif projW > a.session_limit_seconds:
        raw["stage_outcome"] = ("DEFERRED (session limit): FG-D PASSES as frozen, but the projected wall time at the %d workers "
                                "available (%.0f s, modeled) exceeds this session's %d s; Stage D main phase not run here. "
                                "Infrastructure outcome, never evidence." % (W, projW, a.session_limit_seconds))
        status = {"status": "failed", "validity": "invalid", "failure_class": "resource_exhaustion",
                  "reason": "session time limit (dispatching session instruction)", "stage_outcome": raw["stage_outcome"]}
    if status is not None:
        gp.close()
        raw["elapsed_seconds"] = round(time.time() - t_start, 1)
        common.write_json(os.path.join(rd, "raw-result.json"), raw)
        common.write_json(os.path.join(rd, "status.json"), status)
        common.write_json(os.path.join(rd, "manifest_extra.json"), {
            "seeds_used": {"D-PILOT": common.SEEDS["D-PILOT"]}, "workers": W, "prime": info, "FG-D": fgd})
        common.write_exec_report(rd, "RUN-WESO-0b4b33", "STAGE-D", {
            "protocol_deviations": devs, "FG-D": fgd, "stage_outcome": raw["stage_outcome"],
            "runs": {"completed": ["RUN-WESO-0b4b33"] if status["validity"] == "valid" else [], "invalid": [],
                     "failed": [] if status["validity"] == "valid" else ["RUN-WESO-0b4b33"]},
            "stages_not_run": ["STAGE-D main phase (10^5 samples at p_D)"], "anomalies": [],
            "executor_assessment": {"protocol_complete": True, "data_quality": "good", "requires_rerun": False}})
        return

    # ------------------------------ main phase ------------------------------
    adm = analysis.admissible_table(p, N_D)
    adm["X_max"] = str(X)
    adm["recorded_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    adm["recorded_before_first_sample"] = True
    common.write_json(os.path.join(rd, "admissible_cells.pD.json"), adm)
    common.log("[pD] admissible-cell table recorded before sampling: admissible u = %s" % [c["u"] for c in adm["cells"] if c["admissible"]])
    masters = {"R1": common.SEEDS["D-R1"], "R2": common.SEEDS["D-R2"], "NULL": common.SEEDS["D-NULL"]}
    res = stage_c.heuristic_prime("pD", p, kc, N_D, masters, "D", W, rd, adm, [], "O0basis()",
                                  extra_ctx={"factor_watchdog_s": FACTOR_WD})
    gp.close()
    raw["per_prime"] = [res]
    raw["admissible_tables"] = {"pD": adm}
    if res.get("STOP_SR5"):
        raw["stage_outcome"] = "STOPPED (SR-5 unresolved C-2 violation at p_D)"
    else:
        ci = res["criteria_inputs"]
        ig_parts = dict(craw.get("criteria", {}).get("IG_parts", {}))
        ig_parts["NULL-2_bounds_pD"] = res["NULL-2_bounds"]["verdict"] == "PASS"
        ig_parts["no_unresolved_C-2_pD"] = res["C-2_violations"] == 0
        ig = all(ig_parts.values())
        row = ig and res["prime_valid"] and ci["a_every_admissible_wilson_upper_ge_rho"] and ci["b_pass"] and ci["c_pass"]
        raw["criteria"] = {"IG_parts": ig_parts, "IG": ig, "p_D_valid": res["prime_valid"],
                           "a": ci["a_every_admissible_wilson_upper_ge_rho"], "b": ci["b_pass"], "c": ci["c_pass"],
                           "row_meets_success_a_b_c": row, "TC-4": res.get("TC-4"),
                           "scope": "separate crypto-tier row, p = 5*2^248 - 1 only"}
        if not ig:
            raw["stage_outcome"] = "FC-VOID (instrument gate failed at Stage D)"
        elif not res["prime_valid"]:
            raw["stage_outcome"] = "P_D_INVALID (%s)" % res["prime_invalid_reasons"]
        else:
            raw["stage_outcome"] = "STAGE-D ROW: (a) %s, (b) %s, (c) %s -> row_meets_success_a_b_c = %s" % (
                "PASS" if ci["a_every_admissible_wilson_upper_ge_rho"] else "FAIL",
                "PASS" if ci["b_pass"] else "FAIL", "PASS" if ci["c_pass"] else "FAIL", row)
    raw["elapsed_seconds"] = round(time.time() - t_start, 1)
    raw["sample_files"] = {f: common.sha256_file(os.path.join(rd, f)) for f in sorted(os.listdir(rd))
                           if f.startswith(("samples.", "nulls.", "fg_d_pilot"))}
    common.write_json(os.path.join(rd, "raw-result.json"), raw)
    import subprocess
    subprocess.run([sys.executable, "-B", os.path.join(common.IMPL_DIR, "checker.py"), "--run-dir", rd], capture_output=True, text=True)
    cp = os.path.join(rd, "checker_result.json")
    chk = json.load(open(cp)) if os.path.exists(cp) else {"verdict": "ERROR"}
    iv5 = not raw["analysis_freeze_check"]["unchanged"]
    invalid = res.get("IV-3_run_invalid") or chk.get("verdict") != "PASS" or iv5
    status = {"status": "completed_valid" if not invalid else "completed_invalid",
              "validity": "valid" if not invalid else "invalid", "failure_class": None if not invalid else "invalid_measurement",
              "reason": "Stage D executed; outcome %s; checker %s; analysis_freeze unchanged %s" % (raw["stage_outcome"], chk.get("verdict"), not iv5),
              "stage_outcome": raw["stage_outcome"]}
    common.write_json(os.path.join(rd, "status.json"), status)
    common.write_json(os.path.join(rd, "manifest_extra.json"), {
        "seeds_used": {k: common.SEEDS[k] for k in ("D-PILOT", "D-R1", "D-R2", "D-NULL")},
        "seed_derivation": "per-draw seed = SHA-256('<master>|D|<p>|<arm>|<index>'); stream = SHA-256(seed||ctr64be)",
        "workers": W, "prime": info, "c_hat": float(ch), "FG-D": fgd,
        "admissible_cell_table": "admissible_cells.pD.json", "analysis_freeze_check": raw["analysis_freeze_check"],
        "reproduction_spot_check": res.get("spot_check", {}).get("verdict"), "checker": chk.get("verdict"),
        "inputs": {"stage_B_run": STAGE_B_RUN, "stage_C_run": STAGE_C_RUN}})
    devs.append("Per-sample/per-null records are named samples.pD.jsonl.gz / nulls.pD.jsonl.gz (Stage C naming).")
    report.write_stage_report(rd, "RUN-WESO-0b4b33", "STAGE-D", raw, chk, status,
                              extra={"protocol_deviations": devs, "anomalies": [], "FG-D": fgd,
                                     "stages_not_run": [], "prime_D": info})
    common.log("STAGE-D outcome:", raw["stage_outcome"], "elapsed", raw["elapsed_seconds"])


if __name__ == "__main__":
    main()
