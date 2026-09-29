#!/usr/bin/env python3
# analyze742.py -- TASK-20260901-74271d RUN 7 (decision analysis).
# Applies the PREREGISTRATION.md section-6 decision rule to the run receipts.
# No hypothesis-status interpretation, no strength assignment, no promotion.
import json, os, sys, datetime

TASKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(TASKDIR)

FILES = [
    "runs/build_pins.json",
    "runs/draw_bij.json",
    "runs/J4_rbij_arm.json",
    "runs/J3_affine_rerun.json",
    "runs/J2_keyed_bridge.json",
    "runs/J1_census_ext.json",
    "runs/J1_keyed_r16.json",
    "runs/GUARD_c_detcheck.json",
    "runs/GUARD_c_stream_xchk.json",
    "runs/GUARD_feistel_bridge.json",
]
parsed = {}
parse_report = {}
for fp in FILES:
    try:
        with open(fp) as f:
            parsed[fp] = json.load(f)
        parse_report[fp] = "parsed_whole_ok"
    except FileNotFoundError:
        parse_report[fp] = "MISSING"
    except Exception as e:
        parse_report[fp] = f"PARSE_ERROR: {e}"

N30 = 2 ** 30
arms = {}

bp = parsed.get("runs/build_pins.json", {})
j4 = parsed.get("runs/J4_rbij_arm.json", {})
j3 = parsed.get("runs/J3_affine_rerun.json", {})
j2 = parsed.get("runs/J2_keyed_bridge.json", {})
j1c = parsed.get("runs/J1_census_ext.json", {})
j1k = parsed.get("runs/J1_keyed_r16.json", {})
gd = parsed.get("runs/GUARD_feistel_bridge.json", {})
gdc = parsed.get("runs/GUARD_c_detcheck.json", {})
gxc = parsed.get("runs/GUARD_c_stream_xchk.json", {})

pinbij = {}
for st in bp.get("steps", []):
    if isinstance(st.get("json"), dict) and st["json"].get("mode") == "pinbij":
        pinbij = st["json"]

frozen_ok = (j4.get("sbox_table_hex") == pinbij.get("sbox_table_hex")
             and j4.get("pi_table_hex") == pinbij.get("pi_table_hex")
             and j4.get("sbox_draw_seed") == pinbij.get("draw_seed") == 46064002
             and j4.get("sbox_table_hex") == parsed.get("runs/draw_bij.json", {}).get("sbox_table_hex"))

hits = j4.get("W_ge1_nontrivial")
if hits is None:
    j4_band = "missing_receipt"
elif hits <= 8:
    j4_band = "DEAD"
elif hits >= 100:
    j4_band = "ALIVE"
else:
    j4_band = "GRAY"
arms["J4"] = {
    "control": "red_team_report joints.J4 (LOAD-BEARING)",
    "arm": j4.get("arm"), "seed": j4.get("seed"), "arm_id": j4.get("arm_id"),
    "sbox_draw_seed": j4.get("sbox_draw_seed"),
    "trials": j4.get("trials"), "trivial_swaps_excluded": j4.get("trivial_swaps_excluded"),
    "hits_W_ge1": hits,
    "whist": j4.get("whist"),
    "analytic_null_expectation": round((j4.get("nontrivial_trials", N30)) * 4.0 / 2 ** 32, 6),
    "excess_ratio_vs_frozen_excessE_2p30": None if hits is None else hits / N30,
    "frozen_table_byte_identity_pinbij_vs_arm_vs_python": frozen_ok,
    "preregistered_expectation": "DEAD/absence like AES at r=6: hits <= 8; ALIVE trigger hits >= 100 kills the nonlinearity-driven wording; 9..99 gray = inconclusive",
    "reading": j4_band,
    "meets_expectation": j4_band == "DEAD" and frozen_ok,
    "verdict_level_consequence": {
        "DEAD": "sealed-at-J4: the r=6 death tracks nonlinearity beyond the AES table within the tested nibble-wise-bijection subclass; the single-factor-contrast reading generalizes (scoped per PREREGISTRATION.md section 1 deviation disclosure)",
        "ALIVE": "KILLED-AT-J4: the 'nonlinearity-driven' wording dies; the reading reverts to the factor-contrast with the AES S-box named specifically (DEC-20260901-f41451 outcome clause)",
        "GRAY": "inconclusive-at-J4: neither sealed nor killed; exact count reported for the coordinator",
        "missing_receipt": "arm missing -- battery incomplete (scope statement, never a reading)",
    }[j4_band],
}

j3_hits = j3.get("W_ge1_nontrivial")
j3_ok = (j3_hits is not None and j3_hits >= N30 - 8
         and j3.get("whist") == [0, 0, 0, j3.get("nontrivial_trials"), 0]
         and j3.get("nontrivial_trials") is not None
         and j3.get("nontrivial_trials") + j3.get("trivial_swaps_excluded") == N30
         and all(w in (0, j3.get("nontrivial_trials")) for w in j3.get("W_ge1_by_word", [])))
arms["J3"] = {
    "control": "red_team report joints.J3",
    "seed": j3.get("seed"), "arm_id": j3.get("arm_id"), "trials": j3.get("trials"),
    "key_hex": j3.get("key_hex"),
    "trivial_swaps_excluded": j3.get("trivial_swaps_excluded"),
    "hits_W_ge1": j3_hits, "whist": j3.get("whist"),
    "W_ge1_by_word": j3.get("W_ge1_by_word"),
    "excess_ratio_vs_frozen_excessE_2p30": None if j3_hits is None else j3_hits / N30,
    "preregistered_expectation": "hits = 2^30 (T=0), W=3 on 100% nontrivial (deterministic law); band hits >= 2^30-8",
    "meets_expectation": bool(j3_ok),
    "verdict_level_consequence": ("sealed-at-J3: seed-variance confound discharged for the affine arm at this exposure"
                                  if j3_ok else
                                  "F2-class instrument indictment at J3: the alive side of the contrast is voided at this batch (repair route, never a mechanism reading)"),
}

j2_cells = {c["cell_id"]: c for c in j2.get("cells", [])}
j2_ok = (j2.get("bridge_pass") is True
         and all(j2_cells[k].get("identity_law_100pct") and j2_cells[k].get("W_law_100pct")
                 for k in ("J2-R3", "J2-R7") if k in j2_cells)
         and len(j2_cells) == 2)
arms["J2"] = {
    "control": "red_team report joints.J2",
    "seed": j2.get("seed"), "cells": j2.get("cells"),
    "preregistered_expectation": "identity law + W law (W=3) on 500/500 in BOTH cells r=3 and r=7",
    "meets_expectation": bool(j2_ok),
    "verdict_level_consequence": ("sealed-at-J2: empirical law coverage widened to r in {2,3,5,6,7} within the probe geometry"
                                  if j2_ok else
                                  "F2/F3-class defect verdict at J2 (deviation in a derivation-only round count; repair route)"),
}

j1_guards_ok = all(g.get("DrMr_is_I") and g.get("MrDr_is_I")
                   for r, g in (j1c.get("per_r_port_guards_DrMr_and_MrDr_both_I128") or {}).items()
                   if 11 <= int(r) <= 16)
j1_flat_ok = j1c.get("flat_law_ok_extension_r11_r16") is True
j1_rho_lineage_ok = j1c.get("lineage_window_r1_r10_rho_mismatch_count") == 0
j1k_cell = (j1k.get("cells") or [{}])[0]
j1k_ok = (j1k.get("bridge_pass") is True and j1k_cell.get("identity_law_100pct")
          and j1k_cell.get("W_law_100pct"))
j1_ok = j1_guards_ok and j1_flat_ok and j1_rho_lineage_ok and j1k_ok
arms["J1"] = {
    "control": "red_team report joints.J1",
    "census_extension": {
        "n_cell_instances": j1c.get("n_cell_instances"),
        "flat_law_ok_r11_r16": j1_flat_ok,
        "port_guards_ok_r11_r16": j1_guards_ok,
        "lineage_window_r1_r10_rho_mismatches": j1c.get("lineage_window_r1_r10_rho_mismatch_count"),
        "r_star_aff": (j1c.get("r_star_aff") or {}).get("value"),
        "rho_r11_r16_reported_as_data": True,
    },
    "keyed_r16_cell": j1k_cell,
    "preregistered_expectation": "flat per the r-free derivation (D_rM_r=M_rD_r=I_128, word maps, W law) at r=11..16; identity law + W=3 at the r=16 keyed cell",
    "meets_expectation": bool(j1_ok),
    "verdict_level_consequence": ("sealed-at-J1: the r-free derivation survives its extension window at r=11..16 (census) and at r=16 (cipher-touching keyed cell); 'alive at every r<=10' window empirically widened"
                                  if j1_ok else
                                  "F3/F2-class defect verdict at J1 (non-flat extension or guard failure; repair route)"),
}

parity = gd.get("c_python_port_parity") or {}
gd_det_ok = (gd.get("detcheck") or {}).get("deterministic") is True
gc_det_ok = gdc.get("deterministic") is True
idfrac = (gd.get("identity_law_read_first_500") or {}).get("identity_law_holds_frac")
guard_ok = (gd.get("guard_pass") is True and parity.get("parity_pass") is True
            and gd_det_ok and gc_det_ok)
arms["GUARD"] = {
    "control": "red_team report proves_too_much.objects[0].residual_risk",
    "dead_instance_key_hex": (gd.get("dead_instance") or {}).get("key_hex"),
    "key_matches_committed_M1_receipt": (gd.get("dead_instance") or {}).get("key_matches_committed_M1_receipt"),
    "c_detcheck_deterministic": gc_det_ok,
    "python_detcheck_deterministic": gd_det_ok,
    "c_python_port_parity": parity,
    "identity_law_read_first_500": gd.get("identity_law_read_first_500"),
    "preregistered_expectation": "the identity law FAILS on most trials (holds on < 50% of the 500)",
    "meets_expectation": bool(guard_ok and idfrac is not None and idfrac < 0.5),
    "verdict_level_consequence": ("sealed-at-GUARD: the proves-too-much non-transfer to the dead Feistel substitute is now empirically sealed at this exposure (was derivation-only)"
                                  if (guard_ok and idfrac is not None and idfrac < 0.5) else
                                  ("GUARD FAIL: the identity law holds on the known-dead substitute -- it does not discriminate alive from dead; the skeleton/death contrast proves too much"
                                   if (idfrac is not None and idfrac >= 0.5) else
                                   "GUARD invalid_measurement: parity/detcheck failure -- non-transfer stays derivation-only (rule 5, never a reading)")),
}

all_met = all(a["meets_expectation"] for a in arms.values())
if arms["J4"]["reading"] == "ALIVE":
    battery = "KILLED-AT-J4"
elif all_met:
    battery = "ALL-SEALED"
elif arms["J4"]["reading"] == "GRAY":
    battery = "INCONCLUSIVE-AT-J4"
else:
    failed = [k for k, a in arms.items() if not a["meets_expectation"]]
    battery = "DEVIATION-AT:" + ",".join(failed)

pr_mtime = os.path.getmtime("PREREGISTRATION.md")
run_mtimes = {fp: os.path.getmtime(fp) for fp in FILES if os.path.exists(fp)}
mtime_order_ok = all(m > pr_mtime for m in run_mtimes.values()) if run_mtimes else False

out = {
    "schema": "crypto.autoresearch.decision_analysis.v1",
    "task_id": "TASK-20260901-74271d",
    "run": "RUN 7 (decision analysis per PREREGISTRATION.md section 6)",
    "verdict_under_test": "EV-AES-ec53f1 (scope-narrowed CONFIRMED-MISMATCH-ALIVE)",
    "frozen_comparator_convention": "AES dead at r=6 under frozen excess_E = 2^30 (carried from EV-AES-d33b1c OBS-B2-5; unchanged; not re-measured)",
    "preregistration_mtime_order_ok": mtime_order_ok,
    "preregistration_mtime_epoch": pr_mtime,
    "run_mtimes_epoch": run_mtimes,
    "parse_report_all_artifacts": parse_report,
    "parse_all_ok": all(v == "parsed_whole_ok" for v in parse_report.values()),
    "arms": arms,
    "battery_level_outcome": battery,
    "battery_consequence_statement": {
        "ALL-SEALED": "all five preregistered controls met their expectations within their declared scopes; the scope-narrowed verdict of EV-AES-ec53f1 survives this battery",
        "KILLED-AT-J4": "the J4 random-bijection arm read ALIVE at r=6; the 'nonlinearity-driven' wording is killed per the preregistered rule",
        "INCONCLUSIVE-AT-J4": "the J4 arm landed in the preregistered gray zone; the battery neither seals nor kills the reading at J4",
    }.get(battery, "one or more arms deviated from preregistered expectations; per-arm consequences above; defect routing per PREREGISTRATION.md section 6"),
    "deviations_and_unexpected": "see RESULTS.json; no deviation is silently discarded (rule 8)",
    "no_status_interpretation": True,
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "parse_attestation": "this file is machine-generated JSON; parsed whole with python3 json.load before task completion (stated in RESULTS.json)",
    "inference": {
        "policy": "executor-implementation",
        "requested_policy": "executor-implementation",
        "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
        "model_verified": False,
        "fallback_used": True,
        "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
        "degraded_requirements": [],
        "amendment": "DEC-20260831-0d1eeb",
        "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
    },
}
with open("runs/decision_analysis.json", "w") as f:
    f.write(json.dumps(out, indent=1))
print(json.dumps({"battery_level_outcome": battery,
                  "per_arm": {k: a["meets_expectation"] for k, a in arms.items()},
                  "J4_reading": arms["J4"]["reading"],
                  "parse_all_ok": out["parse_all_ok"],
                  "preregistration_mtime_order_ok": mtime_order_ok}, indent=1))
sys.exit(0)
