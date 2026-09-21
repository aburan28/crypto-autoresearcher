#!/usr/bin/env python3
"""Executor driver for EXP-ECRANK-73275e v2 replication round.

TASK-20260908-5291f8 / BATCH-e3cf55. Seven enumerated runs R9-R15 in the
amendment's fixed order (control admission first: R9, R10, R11, R15, then
readings R12, R13, R14). Observations only. Interprets nothing. Changes no
hypothesis or goal status. Selects no interpretation branch.

The control-admission stop (R9 IV-1R or R15 IV-4R failure stops the batch
before R12/R13/R14) is orchestrated by the executor launching runs in
sequence and inspecting results; each run is a separate process invocation.
"""

import argparse
import json
import os
import random
import sys
import time
import traceback
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
V1_SRC = os.path.join(HERE, "..", "source")
sys.path.insert(0, os.path.abspath(V1_SRC))
sys.path.insert(0, HERE)
os.environ.setdefault("ECRANK_REPO_ROOT",
                      os.path.abspath(os.path.join(HERE, "..", "..", "..")))

import ecrank_engine as E
import certify76 as C
import construct
import null_family as NF
import v2_common as RC
import certify_ladder as CL
import plant_builder as PB
import construct_v2 as CV2
import n2r

RUNS = {
    "R9": "RUN-ECRANK-73275e-R9-known-false-v2",
    "R10": "RUN-ECRANK-73275e-R10-planted-elliptic-n6",
    "R11": "RUN-ECRANK-73275e-R11-planted-n8",
    "R12": "RUN-ECRANK-73275e-R12-construct-n6-replication",
    "R13": "RUN-ECRANK-73275e-R13-construct-n6-replay",
    "R14": "RUN-ECRANK-73275e-R14-construct-n8-rescoped",
    "R15": "RUN-ECRANK-73275e-R15-null-v2",
}

SEEDS = {"R9": 760912, "R10": 760908, "R11": 760914,
         "R12": 760906, "R13": 760906, "R14": 760910, "R15": 760916}
LADDER = [1500, 10000, 100000]
N_B_N6 = 10000
N_B_N8 = 10000
H6 = [100, 1000, 10000]
H8 = [100, 1000]
OPS_CAP_DEFAULT = 1.0e8
OPS_CAP_R14 = 2.0e9
WALL_CAP = 7200.0

# IC-732-3 box disclosure, carried verbatim into every R14 raw result
# (N3R box_convention_disclosure).
BOX_DISCLOSURE = (
    "n=8 Bézout enumeration is exhaustive on the integer (a,b) coefficient "
    "box [-min(H,20), min(H,20)]^2 with c solved exactly; non-integer (a,b) "
    "are outside this run's enumerated scope and are not claimed empty. "
    "Full rational height-H lattice enumeration at n=8 is NOT attempted and "
    "is recorded as unmeasured scope."
)


def _tee_logs(run_dir):
    stdout_path = os.path.join(run_dir, "stdout.log")
    stderr_path = os.path.join(run_dir, "stderr.log")
    return open(stdout_path, "w"), open(stderr_path, "w")


def _d1_coset():
    cosets = E.eligible_cosets()
    return next(c for c in cosets
                if 1 in [E.class_value(m) for m in c["members"]])


# --------------------------------------------------------------------------
# R9: amended known-false d=(1..1) control (IV-1R n=6 + IV-1C ladder n=8)
# --------------------------------------------------------------------------

def run_r9():
    run_id = RUNS["R9"]
    seed = SEEDS["R9"]
    params = {"run_kind": "known_false_v2", "seed": seed,
              "IV": ["IV-1R", "IV-1C"], "n_b_per_n": 8,
              "ladder": LADDER, "expected_n8_closed_form": 7}
    argv = [sys.argv[0], "--run", "R9"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    try:
        E.reset_ops()
        E.start_counting()
        ec, digest = E.load_exact_certify(RC.REPO_ROOT)
        assert digest == E.EXACT_CERTIFY_SHA
        coset = _d1_coset()
        rng = random.Random(seed)
        B_INTS = construct.B_INTS
        results = {}
        # ---- n=6: IV-1R conic rejection ----
        n6_per = []
        certified_total_n6 = 0
        for bi in range(8):
            rest = rng.sample(B_INTS, 4)
            b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
            p, g, s = E.mestre_polys(list(b))
            r = [E.peval(g, x) for x in b]
            s2 = s[2] if len(s) > 2 else Fr(0)
            inst, why = E.build_instance(list(b), [1] * 6, r, 6)
            if inst is None:
                n6_per.append({"b_index": bi, "built": False, "reason": why,
                               "x2_coeff": str(s2),
                               "x2_nonzero": bool(s2 != 0)})
            else:
                cert = CL.certify_instance_ladder(inst, coset, ec,
                                                  max_prime=1500)
                certified_total_n6 += cert.get("aggregate_total", 0)
                n6_per.append({"b_index": bi, "built": True, "reason": None,
                               "x2_coeff": str(s2),
                               "x2_nonzero": bool(s2 != 0),
                               "aggregate_total": cert.get("aggregate_total")})
        results["6"] = {
            "per_b": n6_per,
            "all_rejected_degenerate_deg_s_2": all(
                (not x["built"]) and x["reason"] == "degenerate_deg_s_2"
                for x in n6_per),
            "all_x2_nonzero": all(x["x2_nonzero"] for x in n6_per),
            "certified_total_n6": certified_total_n6,
        }
        # ---- n=8: IV-1C fixed ladder ----
        n8_per = []
        for bi in range(8):
            rest = rng.sample(B_INTS, 6)
            b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
            p, g, s = E.mestre_polys(list(b))
            r = [E.peval(g, x) for x in b]
            inst, why = E.build_instance(list(b), [1] * 8, r, 8)
            if inst is None:
                n8_per.append({"b_index": bi, "built": False, "reason": why})
                continue
            rungs = []
            for bound in LADDER:
                ops_before = E.ops_count()
                cert = CL.certify_instance_ladder(inst, coset, ec,
                                                  max_prime=bound)
                ops_after = E.ops_count()
                rungs.append({"bound": bound,
                              "aggregate_total": cert.get("aggregate_total"),
                              "verdict": cert.get("verdict"),
                              "ops_cost": ops_after - ops_before})
            n8_per.append({"b_index": bi, "built": True,
                           "deg_s": inst["deg_s"], "rungs": rungs})
        top_totals = [x["rungs"][-1]["aggregate_total"]
                      for x in n8_per if x.get("built")]
        all_seven = (len(top_totals) == 8
                     and all(t == 7 for t in top_totals))
        results["8"] = {
            "per_b": n8_per,
            "top_rung_bound": LADDER[-1],
            "top_rung_totals": top_totals,
            "all_certify_7_at_top_rung": all_seven,
            "graded_outcome": "PASS" if all_seven else "CERTIFIER_LIMITED",
        }
        iv1r_pass = (results["6"]["all_rejected_degenerate_deg_s_2"]
                     and results["6"]["all_x2_nonzero"]
                     and results["6"]["certified_total_n6"] == 0)
        raw = {"parameters": params, "results": results,
               "iv1r_pass": iv1r_pass,
               "iv1c_graded_outcome": results["8"]["graded_outcome"],
               "ops": E.ops_count()}
        so.write(json.dumps({"iv1r_pass": iv1r_pass,
                             "iv1c_graded_outcome":
                                 results["8"]["graded_outcome"],
                             "n6_certified_total":
                                 results["6"]["certified_total_n6"],
                             "n8_top_rung_totals": top_totals},
                            indent=2) + "\n")
        reason = ("known-false v2 recorded; IV-1R pass=%s; IV-1C %s; "
                  "n8 top-rung totals=%s"
                  % (iv1r_pass, results["8"]["graded_outcome"], top_totals))
        RC.finalize_run(run_dir, header, t0, "completed", reason, raw)
        return "completed", reason
    except Exception as exc:
        se.write(traceback.format_exc())
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "implementation_error: %s" % exc, {"error": str(exc)})
        return "failed_infrastructure", str(exc)
    finally:
        so.close()
        se.close()


# --------------------------------------------------------------------------
# R10: planted ELLIPTIC n=6 detection control (IV-3R)
# --------------------------------------------------------------------------

def _planted_decade_ratios(plants, H_levels=(100, 1000, 10000)):
    """Per-decade ratios of the planted yield (cumulative count of plants by
    h_A). DESCRIPTIVE; no pass/fail band applied here (the [5,20] window is
    recorded for the Coordinator)."""
    H_sorted = sorted(int(H) for H in H_levels)
    cum = {H: 0 for H in H_sorted}
    for pl in plants:
        hA = pl["h_A"]
        for H in H_sorted:
            if hA <= H:
                cum[H] += 1
    ratios = []
    for lo, hi in zip(H_sorted[:-1], H_sorted[1:]):
        if cum[lo] > 0:
            ratios.append({"from_H": lo, "to_H": hi, "N_from": cum[lo],
                           "N_to": cum[hi], "ratio": cum[hi] / cum[lo]})
    spans_decades = len({H for H in H_sorted if cum[H] > 0}) > 1
    return {"cumulative_counts": {str(H): cum[H] for H in H_sorted},
            "decade_ratios": ratios,
            "spans_decades": spans_decades,
            "window": [5, 20]}


def run_r10():
    run_id = RUNS["R10"]
    seed = SEEDS["R10"]
    params = {"run_kind": "planted_elliptic_n6", "seed": seed, "IV": "IV-3R",
              "n_plants": 9, "exponent_window": [0.699, 1.301],
              "per_decade_window": [5, 20], "H_box": 10000}
    argv = [sys.argv[0], "--run", "R10"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    try:
        E.reset_ops()
        E.start_counting()
        plants, coset, build_ledger = PB.build_plants_n6(E, seed, n_plants=9)
        n_built = len(plants)
        recovered = []
        for pl in plants:
            b = [Fr(x) for x in pl["b"]]
            dpat = pl["d_pattern"]
            kept, near, meta = construct.solve_n6(E, b, dpat, 10 ** 4)
            plant_r = pl["r"]
            hit = any(inst["r"] == plant_r for inst in kept)
            hA, hB = pl["h_A"], pl["h_B"]
            hr = (hA / hB) if hB else None
            in_win = (hr is not None and 0.699 <= hr <= 1.301)
            recovered.append({
                "index": pl["index"],
                "b_stream_position": pl["b_stream_position"],
                "h_A": hA, "h_B": hB,
                "height_ratio_hA_over_hB": hr,
                "exponent_gate_in_window": in_win,
                "recovered": hit,
                "n_solutions": len(kept),
                "meta": meta,
            })
        n_rec = sum(1 for r in recovered if r["recovered"])
        detection = {"recovered": n_rec, "denominator": n_built,
                     "ratio": (n_rec / n_built) if n_built else None}
        rec_plants = [r for r in recovered if r["recovered"]]
        exp_gate = {
            "window": [0.699, 1.301],
            "definition": ("height_ratio = h_A / h_B = recorded r_height / "
                           "rat_height(solved free coordinate t = r_0)"),
            "per_plant": [{"index": r["index"],
                           "height_ratio": r["height_ratio_hA_over_hB"],
                           "in_window": r["exponent_gate_in_window"]}
                          for r in rec_plants],
            "all_in_window": (all(r["exponent_gate_in_window"]
                                  for r in rec_plants)
                              if rec_plants else None),
        }
        per_decade = _planted_decade_ratios(plants)
        if not per_decade["spans_decades"]:
            per_decade["clause"] = "not_applicable_single_decade"
            per_decade["per_plant_ratios"] = [
                r["height_ratio_hA_over_hB"] for r in rec_plants]
        # Aggregate log-log slope of the planted yield (IC-7 "exponent gate"
        # reading; recorded for context, not gated per-plant).
        import math
        pts = []
        for H in (100, 1000, 10000):
            c = sum(1 for pl in plants if pl["h_A"] <= H)
            if c > 0:
                pts.append((math.log10(H), math.log10(c)))
        slope = None
        if len(pts) >= 2:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            nn = len(pts)
            mx, my = sum(xs) / nn, sum(ys) / nn
            den = sum((x - mx) ** 2 for x in xs)
            slope = (sum((x - mx) * (y - my) for x, y in pts) / den
                     if den else None)
        per_decade["log_log_slope"] = slope
        per_decade["log_log_slope_window"] = [0.699, 1.301]
        raw = {
            "parameters": params,
            "coset_V": list(coset["V"]),
            "plants": [{k: v for k, v in pl.items() if k != "instance"}
                       for pl in plants],
            "build_ledger": build_ledger,
            "recovered": recovered,
            "detection": detection,
            "exponent_gate": exp_gate,
            "per_decade": per_decade,
            "ops": E.ops_count(),
        }
        so.write(json.dumps({"n_plants_built": n_built, "recovered": n_rec,
                             "detection_ratio": detection["ratio"]},
                            indent=2) + "\n")
        reason = ("planted elliptic n=6 recorded; built=%d recovered=%d/%d"
                  % (n_built, n_rec, n_built))
        RC.finalize_run(run_dir, header, t0, "completed", reason, raw)
        return "completed", reason
    except Exception as exc:
        se.write(traceback.format_exc())
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "implementation_error: %s" % exc, {"error": str(exc)})
        return "failed_infrastructure", str(exc)
    finally:
        so.close()
        se.close()


# --------------------------------------------------------------------------
# R11: planted n=8 control, R7 family, certifier ladder applied
# --------------------------------------------------------------------------

def run_r11():
    run_id = RUNS["R11"]
    seed = SEEDS["R11"]
    params = {"run_kind": "planted_n8_r7_family", "seed": seed,
              "n_plants": 9, "ladder": LADDER,
              "expected_closed_form": 7}
    argv = [sys.argv[0], "--run", "R11"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    try:
        E.reset_ops()
        E.start_counting()
        ec, digest = E.load_exact_certify(RC.REPO_ROOT)
        assert digest == E.EXACT_CERTIFY_SHA
        coset = _d1_coset()
        plants, build_ledger = PB.build_plants_n8_r7(E, seed, n_plants=9)
        n_built = len(plants)
        per = []
        for pl in plants:
            inst = pl["instance"]
            rungs = []
            for bound in LADDER:
                ops_before = E.ops_count()
                cert = CL.certify_instance_ladder(inst, coset, ec,
                                                  max_prime=bound)
                ops_after = E.ops_count()
                rungs.append({"bound": bound,
                              "aggregate_total": cert.get("aggregate_total"),
                              "verdict": cert.get("verdict"),
                              "ops_cost": ops_after - ops_before})
            per.append({"index": pl["index"],
                        "b_stream_position": pl["b_stream_position"],
                        "b": pl["b"], "deg_s": pl["deg_s"],
                        "h_A": pl["h_A"], "rungs": rungs})
        top_totals = [x["rungs"][-1]["aggregate_total"] for x in per]
        raw = {
            "parameters": params,
            "coset_V": list(coset["V"]),
            "plants": [{k: v for k, v in pl.items() if k != "instance"}
                       for pl in plants],
            "build_ledger": build_ledger,
            "per_plant_ladder": per,
            "top_rung_bound": LADDER[-1],
            "top_rung_totals": top_totals,
            "all_certify_7_at_top_rung": (
                len(top_totals) == 9 and all(t == 7 for t in top_totals)),
            "ops": E.ops_count(),
        }
        so.write(json.dumps({"n_plants_built": n_built,
                             "top_rung_totals": top_totals}, indent=2) + "\n")
        reason = ("planted n=8 R7 family recorded; built=%d top-rung totals=%s"
                  % (n_built, top_totals))
        RC.finalize_run(run_dir, header, t0, "completed", reason, raw)
        return "completed", reason
    except Exception as exc:
        se.write(traceback.format_exc())
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "implementation_error: %s" % exc, {"error": str(exc)})
        return "failed_infrastructure", str(exc)
    finally:
        so.close()
        se.close()


# --------------------------------------------------------------------------
# R12: construct-n6 fresh-seed replication + N2R reconciliation
# --------------------------------------------------------------------------

def run_r12():
    run_id = RUNS["R12"]
    seed = SEEDS["R12"]
    params = {"run_kind": "construct_n6_replication", "seed": seed,
              "n_b": N_B_N6, "H_levels": H6, "N2R": True}
    argv = [sys.argv[0], "--run", "R12"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    t_start = time.monotonic()
    try:
        E.reset_ops()
        E.start_counting()
        # N2R: record BOTH exact predicates verbatim BEFORE any count.
        predicates = n2r.verbatim_predicates(RC.REPO_ROOT)
        ec, digest = E.load_exact_certify(RC.REPO_ROOT)
        assert digest == E.EXACT_CERTIFY_SHA
        raw = CV2.construct_arm_v2(
            E, 6, seed, N_B_N6, H6, certifier=C, ec=ec,
            ops_cap=OPS_CAP_DEFAULT, wall_clock_cap=WALL_CAP, t_start=t_start)
        # N2R reconciliation (descriptive; no interpretation).
        recon = n2r.reconcile(raw["found"], H6)
        raw["n2r"] = {
            "verbatim_predicates": predicates,
            "reconciliation": recon,
        }
        ckpt = os.path.join(run_dir, "checkpoints")
        os.makedirs(ckpt, exist_ok=True)
        RC.write_json(os.path.join(ckpt, "ckpt-001-final.json"),
                      {"ops": raw["ops"], "found": len(raw["found"]),
                       "counts_per_H": raw["counts_per_H"]})
        so.write(json.dumps({"n": 6, "feasible": raw["feasible_tuples"],
                             "counts": raw["counts_per_H"],
                             "found": len(raw["found"]),
                             "exhaustion": raw["exhaustion"],
                             "ops": raw["ops"],
                             "N2R_N_per_H_A": recon["N_per_H_convention_A"],
                             "N2R_N_per_H_B": recon["N_per_H_convention_B"]},
                            indent=2) + "\n")
        reason = ("construct-n6 replication recorded; found=%d feasible=%d "
                  "exhaustion=%s"
                  % (len(raw["found"]), raw["feasible_tuples"],
                     raw["exhaustion"]))
        RC.finalize_run(run_dir, header, t0, "completed", reason, raw,
                        ops_cap=OPS_CAP_DEFAULT)
        return "completed", reason
    except Exception as exc:
        se.write(traceback.format_exc())
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "implementation_error: %s" % exc, {"error": str(exc)},
                        ops_cap=OPS_CAP_DEFAULT)
        return "failed_infrastructure", str(exc)
    finally:
        so.close()
        se.close()


# --------------------------------------------------------------------------
# R13: determinism replay of R12 (IV-2R, RD-2 canonical comparison)
# --------------------------------------------------------------------------

def _canonical(obj):
    """Canonical serialization: string-keyed, sorted (RD-2)."""
    return json.dumps(obj, sort_keys=True, default=str)


def run_r13():
    run_id = RUNS["R13"]
    seed = SEEDS["R13"]
    params = {"run_kind": "construct_n6_replay", "seed": seed,
              "n_b": N_B_N6, "H_levels": H6, "replay_of": "R12",
              "IV": "IV-2R"}
    argv = [sys.argv[0], "--run", "R13"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    t_start = time.monotonic()
    try:
        E.reset_ops()
        E.start_counting()
        ec, digest = E.load_exact_certify(RC.REPO_ROOT)
        assert digest == E.EXACT_CERTIFY_SHA
        raw = CV2.construct_arm_v2(
            E, 6, seed, N_B_N6, H6, certifier=C, ec=ec,
            ops_cap=OPS_CAP_DEFAULT, wall_clock_cap=WALL_CAP, t_start=t_start)
        # IV-2R: bit-for-bit replay of R12.
        orig_path = os.path.join(RC.REPO_ROOT, RC.EXP_DIR, "runs",
                                 RUNS["R12"], "raw-result.json")
        with open(orig_path) as f:
            orig = json.load(f)
        raw["iv2r_instance_list_identical"] = (
            _canonical(raw.get("found")) == _canonical(orig.get("found")))
        # RD-2: counts-identity on canonically serialized (string-keyed,
        # sorted) dicts AFTER JSON serialization.
        raw["iv2r_counts_identical"] = (
            _canonical(raw.get("counts_per_H"))
            == _canonical(orig.get("counts_per_H")))
        raw["iv2r_counts_comparison_basis"] = (
            "canonically serialized (string-keyed, sorted) dicts after JSON "
            "serialization (RD-2)")
        raw["iv2r_ops_r12"] = orig.get("ops")
        raw["iv2r_ops_r13"] = raw.get("ops")
        raw["iv2r_ops_identical"] = (orig.get("ops") == raw.get("ops"))
        ckpt = os.path.join(run_dir, "checkpoints")
        os.makedirs(ckpt, exist_ok=True)
        RC.write_json(os.path.join(ckpt, "ckpt-001-final.json"),
                      {"ops": raw["ops"], "found": len(raw["found"]),
                       "counts_per_H": raw["counts_per_H"]})
        so.write(json.dumps({"iv2r_instance_list_identical":
                                 raw["iv2r_instance_list_identical"],
                             "iv2r_counts_identical":
                                 raw["iv2r_counts_identical"],
                             "iv2r_ops_identical": raw["iv2r_ops_identical"]},
                            indent=2) + "\n")
        reason = ("construct-n6 replay recorded; instance_list_identical=%s "
                  "counts_identical=%s ops_identical=%s"
                  % (raw["iv2r_instance_list_identical"],
                     raw["iv2r_counts_identical"],
                     raw["iv2r_ops_identical"]))
        RC.finalize_run(run_dir, header, t0, "completed", reason, raw,
                        ops_cap=OPS_CAP_DEFAULT)
        return "completed", reason
    except Exception as exc:
        se.write(traceback.format_exc())
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "implementation_error: %s" % exc, {"error": str(exc)},
                        ops_cap=OPS_CAP_DEFAULT)
        return "failed_infrastructure", str(exc)
    finally:
        so.close()
        se.close()


# --------------------------------------------------------------------------
# R14: construct-n8 rescoped (N3R; cap 2.0e9; disclosed box)
# --------------------------------------------------------------------------

def run_r14():
    run_id = RUNS["R14"]
    seed = SEEDS["R14"]
    params = {"run_kind": "construct_n8_rescoped", "seed": seed,
              "n_b": N_B_N8, "H_levels": H8, "ops_cap": OPS_CAP_R14,
              "N3R": True, "N2R": True}
    argv = [sys.argv[0], "--run", "R14"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params,
                                      ops_cap=OPS_CAP_R14)
    so, se = _tee_logs(run_dir)
    t_start = time.monotonic()
    try:
        E.reset_ops()
        E.start_counting()
        predicates = n2r.verbatim_predicates(RC.REPO_ROOT)
        ec, digest = E.load_exact_certify(RC.REPO_ROOT)
        assert digest == E.EXACT_CERTIFY_SHA
        # solve_n8 (v1) reads the module global construct.OPS_CAP internally;
        # set it to the R14 rescoped cap for the duration of the arm.
        old_cap = construct.OPS_CAP
        construct.OPS_CAP = int(OPS_CAP_R14)
        try:
            raw = CV2.construct_arm_v2(
                E, 8, seed, N_B_N8, H8, certifier=C, ec=ec,
                ops_cap=OPS_CAP_R14, wall_clock_cap=WALL_CAP, t_start=t_start)
        finally:
            construct.OPS_CAP = old_cap
        # N3R: box disclosure verbatim in every R14 raw result.
        raw["n3r_box_disclosure"] = BOX_DISCLOSURE
        # N2R reconciliation (counts under both conventions).
        recon = n2r.reconcile(raw["found"], H8)
        raw["n2r"] = {"verbatim_predicates": predicates,
                      "reconciliation": recon}
        ckpt = os.path.join(run_dir, "checkpoints")
        os.makedirs(ckpt, exist_ok=True)
        RC.write_json(os.path.join(ckpt, "ckpt-001-final.json"),
                      {"ops": raw["ops"], "found": len(raw["found"]),
                       "counts_per_H": raw["counts_per_H"],
                       "exhaustion": raw["exhaustion"]})
        so.write(json.dumps({"n": 8, "feasible": raw["feasible_tuples"],
                             "counts": raw["counts_per_H"],
                             "found": len(raw["found"]),
                             "exhaustion": raw["exhaustion"],
                             "ops": raw["ops"],
                             "N2R_N_per_H_A": recon["N_per_H_convention_A"],
                             "N2R_N_per_H_B": recon["N_per_H_convention_B"]},
                            indent=2) + "\n")
        reason = ("construct-n8 rescoped recorded; found=%d feasible=%d "
                  "exhaustion=%s ops=%d"
                  % (len(raw["found"]), raw["feasible_tuples"],
                     raw["exhaustion"], raw["ops"]))
        RC.finalize_run(run_dir, header, t0, "completed", reason, raw,
                        ops_cap=OPS_CAP_R14)
        return "completed", reason
    except Exception as exc:
        se.write(traceback.format_exc())
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "implementation_error: %s" % exc, {"error": str(exc)},
                        ops_cap=OPS_CAP_R14)
        return "failed_infrastructure", str(exc)
    finally:
        so.close()
        se.close()


# --------------------------------------------------------------------------
# R15: null object re-run (IV-4R + RD-1 non-destructive proof)
# --------------------------------------------------------------------------

def run_r15():
    run_id = RUNS["R15"]
    seed = SEEDS["R15"]
    n_b = 64  # matching v1 R6 sample size
    params = {"run_kind": "null_v2", "seed": seed, "n_b": n_b,
              "H_levels": [10000], "IV": "IV-4R", "RD": "RD-1"}
    argv = [sys.argv[0], "--run", "R15"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    try:
        E.reset_ops()
        E.start_counting()
        rng = random.Random(seed)
        H_top = 10000
        proof_ledger = []   # append-only per-b_index ledger (RD-1)
        total_solutions = 0
        per = []
        for bi in range(n_b):
            b = construct.sample_b(rng, 6)
            dpat = [1] * 6
            A, B, C = NF.d1_quadratic_coeffs(E, b)
            C_null = NF.null_constant(A, B, C)
            kept, near, meta = construct.solve_n6(E, b, dpat, H_top,
                                                  null_override=(A, B, C_null))
            proof = NF.infeasible_proof(A, B, C_null)
            # RD-1: append-only; b_index-0 record written first, never
            # overwritten.
            proof_ledger.append({"b_index": bi, "proof": proof})
            total_solutions += len(kept)
            per.append({"b_index": bi, "n_solutions": len(kept),
                        "disc_negative": proof["disc_negative"],
                        "no_real_root": proof["no_real_root"]})
        # RD-1: retain the b_index-0 proof bytes (hash) in the raw result.
        import hashlib
        proof0_bytes = json.dumps(proof_ledger[0]["proof"], sort_keys=True)
        proof0_sha256 = hashlib.sha256(proof0_bytes.encode()).hexdigest()
        # IV-4R: exactly 0 solutions AND the infeasibility flag raised.
        # The infeasibility flag is no_real_root (the quadratic has no real
        # root, hence no rational in-box root). For the d=(1..1) family at
        # n=6 the ellipticity quadratic is degenerate (A = B = 0, the
        # objects are conics with no x^5 condition), so the null family is
        # the "1 = 0" sentinel: infeasible via no_real_root = True (the
        # A == 0 and C_null != 0 and B == 0 branch), NOT via a negative
        # discriminant (disc = 0). disc_negative is recorded as a detail.
        iv4r_pass = (total_solutions == 0
                     and all(p["no_real_root"] for p in per))
        raw = {
            "parameters": params,
            "proof_ledger": proof_ledger,
            "proof_first_b_index_0": proof_ledger[0]["proof"],
            "proof_first_b_index_0_sha256": proof0_sha256,
            "per_b": per,
            "total_solutions": total_solutions,
            "iv4r_exactly_zero_solutions": (total_solutions == 0),
            "iv4r_infeasibility_flag_raised": all(
                p["no_real_root"] for p in per),
            "iv4r_infeasibility_flag_note": (
                "infeasibility flag = no_real_root (the null quadratic has "
                "no real root, hence no rational in-box root). For the "
                "d=(1..1) family at n=6 the ellipticity quadratic is "
                "degenerate (A = B = 0; conic, no x^5 condition), so the "
                "null family is the '1 = 0' sentinel, infeasible via "
                "no_real_root = True, not via a negative discriminant "
                "(disc = 0). disc_negative is recorded per tuple as a "
                "detail."),
            "iv4r_all_disc_negative": all(p["disc_negative"] for p in per),
            "iv4r_pass": iv4r_pass,
            "ops": E.ops_count(),
        }
        so.write(json.dumps({"total_solutions": total_solutions,
                             "iv4r_pass": iv4r_pass}, indent=2) + "\n")
        reason = ("null v2 recorded; total_solutions=%d iv4r_pass=%s"
                  % (total_solutions, iv4r_pass))
        RC.finalize_run(run_dir, header, t0, "completed", reason, raw)
        return "completed", reason
    except Exception as exc:
        se.write(traceback.format_exc())
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "implementation_error: %s" % exc, {"error": str(exc)})
        return "failed_infrastructure", str(exc)
    finally:
        so.close()
        se.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", choices=list(RUNS) + ["all"], default="all")
    args = ap.parse_args()
    order = list(RUNS) if args.run == "all" else [args.run]
    results = {}
    for key in order:
        print("=== %s %s ===" % (key, RUNS[key]), flush=True)
        if key == "R9":
            results[key] = run_r9()
        elif key == "R10":
            results[key] = run_r10()
        elif key == "R11":
            results[key] = run_r11()
        elif key == "R12":
            results[key] = run_r12()
        elif key == "R13":
            results[key] = run_r13()
        elif key == "R14":
            results[key] = run_r14()
        elif key == "R15":
            results[key] = run_r15()
        print(results[key], flush=True)
    print(json.dumps({k: list(v) for k, v in results.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
