"""execution_report.yaml writer for Stages C and D (observations only; frozen
outcome codes applied mechanically by stage_c.evaluate_criteria)."""
import common


def prime_block(r):
    if r.get("STOP_SR5"):
        return {"STOP_SR5": True, "C-2_unresolved": r["C-2_unresolved"]}
    cells = []
    for c in r["cells"]:
        cells.append({"u": c["u"], "B": round(c["B"], 3), "admissible": c["admissible"], "rho_u": c["rho_u"],
                      "S_delta": c["S_delta"], "f_emp": c["f_emp"], "wilson99": c["wilson99"],
                      "wilson_upper_ge_rho": c["wilson_upper_ge_rho"], "R_max": c["R_max"],
                      "T1": c["T1"], "T1_ci99": c["T1_ci99"], "S_null1": c["S_null1"],
                      "f_null2": c["f_null2"], "null2_over_rho": c["null2_over_rho"], "null2_bound_ok": c["null2_bound_ok"],
                      "u_pow_minus_u": c["u_pow_minus_u"], "R_uu": c["R_uu"],
                      "size_matched_prediction": c["size_matched_prediction"],
                      "S_delta_over_size_matched": c["S_delta_over_size_matched"]})
    blk = {"p": r["p"], "k_C": r["k_C"], "N": r["N"], "cells": cells,
           "TC-1": r["TC-1"], "TC-2": r["TC-2"], "TC-3": r["TC-3"],
           "SEED-1": {"reject": r["SEED-1"]["reject"], "rejected": r["SEED-1"]["rejected"],
                      "family_size": r["SEED-1"]["family_size"], "min_p": min(t["p_value"] for t in r["SEED-1"]["tests"])},
           "SEED-2": r["SEED-2"], "NULL-2_bounds": r["NULL-2_bounds"], "IV-1_unverified": r["IV-1_unverified_factorisations"],
           "C-2_violations": r["C-2_violations"], "U-2_failures": r["U-2_failures"], "delta_max": r["delta_max"],
           "reproduction_spot_check": {"verdict": r["spot_check"]["verdict"], "mismatches": r["spot_check"]["mismatches"]},
           "T1_trend": r["T1_trend"], "KS_ECDF_vs_prediction": r["KS_ECDF_vs_prediction"],
           "prime_valid": r["prime_valid"], "prime_invalid_reasons": r["prime_invalid_reasons"],
           "criteria_inputs": r["criteria_inputs"], "wall_seconds_per_sample": r["wall_seconds_per_sample"],
           "sampling_seconds": r["sampling_seconds"]}
    for k in ("KS-1", "START-2"):
        if k in r:
            blk[k] = {"verdict": r[k]["verdict"], "rejected": r[k]["rejected"], "family_size": r[k]["family_size"],
                      "tests": [{"test": t["test"], "p_value": t["p_value"]} for t in r[k]["tests"]]}
    if "PC-3" in r:
        blk["PC-3"] = r["PC-3"]
    if "TC-4" in r:
        blk["TC-4"] = r["TC-4"]
    return blk


def write_stage_report(rd, run_id, stage, raw, chk, status, extra=None):
    rel = "experiments/EXP-WESO-9e2d6d/runs/%s/" % run_id
    import os
    files = sorted(os.listdir(rd))
    body = {
        "protocol_deviations": (extra or {}).get("protocol_deviations", []),
        "runs": {"completed": [run_id] if status["validity"] == "valid" else [],
                 "invalid": [run_id] if status["validity"] != "valid" else [], "failed": []},
        "instrument_gates_and_controls": {
            k: raw.get(k) for k in ("V-RHO", "CLS-1", "DET-1") if k in raw},
        "analysis_freeze_check": raw.get("analysis_freeze_check"),
        "primes": raw.get("primes"),
        "per_prime": {r["label"]: prime_block(r) for r in raw.get("per_prime", [])},
        "criteria": raw.get("criteria"),
        "stage_outcome": raw.get("stage_outcome"),
        "IV-4_checker": {"verdict": chk.get("verdict"), "mismatches": chk.get("mismatches"),
                         "sympy_factorisation_failures_total": chk.get("sympy_factorisation_failures_total")},
        "observations_note": "Observations and mechanically evaluated gates/criteria only. No statement that Heuristic 1 "
                             "or HEUR-WESO-516558-2 is supported or refuted is made by the Executor.",
        "anomalies": (extra or {}).get("anomalies", []),
        "artifact_paths": [rel + f for f in files] + [rel + "manifest.yaml", rel + "execution_report.yaml"],
        "executor_assessment": {"protocol_complete": True, "data_quality": "good" if status["validity"] == "valid" else "invalid",
                                "requires_rerun": status["validity"] != "valid"},
    }
    if extra:
        for k, v in extra.items():
            if k not in ("protocol_deviations", "anomalies"):
                body[k] = v
    common.write_exec_report(rd, run_id, stage, body)
