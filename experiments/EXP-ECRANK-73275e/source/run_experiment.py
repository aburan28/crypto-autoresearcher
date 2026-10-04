#!/usr/bin/env python3
"""Executor driver for EXP-ECRANK-73275e -- TASK-20260907-2a3331.

Eight enumerated runs. Observations only. Interprets nothing.
Changes no hypothesis or goal status.
"""

import argparse
import json
import os
import random
import sys
import traceback
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("ECRANK_REPO_ROOT", os.path.abspath(os.path.join(HERE, "../../..")))

import ecrank_engine as E
import certify76 as C
import run_common as RC
import audit
import construct
import null_family as NF

RUNS = {
    "R1": "RUN-ECRANK-73275e-R1-audit-smoke",
    "R2": "RUN-ECRANK-73275e-R2-draw-support",
    "R3": "RUN-ECRANK-73275e-R3-construct-n6",
    "R4": "RUN-ECRANK-73275e-R4-construct-n6-replay",
    "R5": "RUN-ECRANK-73275e-R5-construct-n8",
    "R6": "RUN-ECRANK-73275e-R6-null",
    "R7": "RUN-ECRANK-73275e-R7-known-false",
    "R8": "RUN-ECRANK-73275e-R8-planted",
}

N_B_N6 = 10000
N_B_N8 = 10000
H6 = [100, 1000, 10000]
H8 = [100, 1000]


def _tee_logs(run_dir):
    stdout_path = os.path.join(run_dir, "stdout.log")
    stderr_path = os.path.join(run_dir, "stderr.log")
    return open(stdout_path, "w"), open(stderr_path, "w")


def run_r1():
    run_id = RUNS["R1"]
    params = {"run_kind": "audit_smoke", "IV": "IV-5"}
    argv = [sys.argv[0], "--run", "R1"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    try:
        E.reset_ops()
        E.start_counting()
        raw = audit.run_audit(smoke_only=True)
        so.write(json.dumps({
            "mismatches": raw["b_tuple_mismatches"],
            "inbox_fraction": raw["inbox"]["in_box_fraction"],
            "replay": raw["reconstruction_bit_identical_replay"],
            "plant_meets": raw["r1_planted_2d"]["meets_observed"],
        }, indent=2) + "\n")
        ok = (
            raw["b_tuple_mismatches"] == []
            and raw["reconstruction_bit_identical_replay"]
            and raw["inbox"]["in_box_fraction"] == 1.0
            and raw["r1_planted_2d"]["meets_observed"] >= 1
        )
        status = "completed" if ok else "completed"
        reason = "IV-5 smoke checks recorded; mismatches=%s inbox=%s plant_meets=%s" % (
            raw["b_tuple_mismatches"], raw["inbox"]["in_box_fraction"],
            raw["r1_planted_2d"]["meets_observed"])
        RC.finalize_run(run_dir, header, t0, status, reason, raw)
        return status, reason
    except Exception as exc:
        se.write(traceback.format_exc())
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "implementation_error: %s" % exc, {"error": str(exc)})
        return "failed_infrastructure", str(exc)
    finally:
        so.close()
        se.close()


def run_r2():
    run_id = RUNS["R2"]
    params = {"run_kind": "draw_support_audit", "AT": ["AT-0", "AT-1", "AT-2"]}
    argv = [sys.argv[0], "--run", "R2"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    try:
        E.reset_ops()
        E.start_counting()
        raw = audit.run_audit(smoke_only=False)
        so.write(json.dumps({
            "mismatches": raw["b_tuple_mismatches"],
            "inbox": raw["inbox"],
            "plants": [{"at": p["at"], "meets": p["meets_observed"],
                        "expected": p["expected_meets"], "plant": p["plant"]}
                       for p in raw["r2_plants"]],
        }, indent=2) + "\n")
        reason = "audit AT-0/1/2 recorded; inbox_fraction=%s mismatches=%d" % (
            raw["inbox"]["in_box_fraction"], len(raw["b_tuple_mismatches"]))
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


def _construct(run_key, n, seed, n_b, H_levels, replay_of=None, null_family=False):
    run_id = RUNS[run_key]
    params = {
        "run_kind": "construct_n%d%s" % (n, "_null" if null_family else ""),
        "n": n, "seed": seed, "n_b": n_b, "H_levels": H_levels,
        "replay_of": replay_of, "null_family": null_family,
    }
    argv = [sys.argv[0], "--run", run_key]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    try:
        E.reset_ops()
        E.start_counting()
        ec, digest = E.load_exact_certify(RC.REPO_ROOT)
        assert digest == E.EXACT_CERTIFY_SHA
        raw = construct.construct_arm(
            E, n, seed, n_b, H_levels,
            certifier=None if null_family else C,
            ec=None if null_family else ec,
            null_family=null_family,
        )
        if replay_of:
            orig_path = os.path.join(RC.REPO_ROOT, RC.EXP_DIR, "runs",
                                     RUNS["R3"], "raw-result.json")
            orig = json.load(open(orig_path))
            # bit-for-bit on instance list + counts (IV-2)
            a = json.dumps(raw.get("found"), sort_keys=True)
            b = json.dumps(orig.get("found"), sort_keys=True)
            raw["iv2_instance_list_identical"] = (a == b)
            raw["iv2_counts_identical"] = (
                raw.get("counts_per_H") == orig.get("counts_per_H"))
            raw["iv2_ops_r3"] = orig.get("ops")
            raw["iv2_ops_r4"] = raw.get("ops")
        so.write(json.dumps({
            "n": n, "feasible": raw["feasible_tuples"],
            "counts": raw["counts_per_H"], "found": len(raw["found"]),
            "exhaustion": raw["exhaustion"], "ops": raw["ops"],
        }, indent=2) + "\n")
        ckpt = os.path.join(run_dir, "checkpoints")
        os.makedirs(ckpt, exist_ok=True)
        RC.write_json(os.path.join(ckpt, "ckpt-001-final.json"),
                      {"ops": raw["ops"], "found": len(raw["found"])})
        reason = "construction n=%d recorded; found=%d feasible=%d exhaustion=%s" % (
            n, len(raw["found"]), raw["feasible_tuples"], raw["exhaustion"])
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


def run_r7():
    run_id = RUNS["R7"]
    params = {"run_kind": "known_false_d_all_ones", "seed": 760812,
              "expected": {6: 5, 8: 7}, "n_b_per_n": 8}
    argv = [sys.argv[0], "--run", "R7"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    try:
        E.reset_ops()
        E.start_counting()
        ec, digest = E.load_exact_certify(RC.REPO_ROOT)
        cosets = E.eligible_cosets()
        coset = next(c for c in cosets
                     if 1 in [E.class_value(m) for m in c["members"]])
        rng = random.Random(760812)
        B_INTS = construct.B_INTS
        results = {}
        for n, expected in ((6, 5), (8, 7)):
            per = []
            for bi in range(8):
                rest = rng.sample(B_INTS, n - 2)
                b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
                p, g, s = E.mestre_polys(list(b))
                r = [E.peval(g, x) for x in b]
                inst, why = E.build_instance(list(b), [1] * n, r, n)
                if inst is None:
                    per.append({"b_index": bi, "built": False, "reason": why})
                    continue
                cert = C.certify_instance(inst, coset, ec)
                per.append({
                    "b_index": bi, "built": True,
                    "aggregate_total": cert.get("aggregate_total"),
                    "expected": expected,
                    "matches_n_minus_1": cert.get("aggregate_total") == expected,
                    "n_classes": len(cert.get("classes", {})),
                })
            totals = [x.get("aggregate_total") for x in per if x.get("built")]
            results[str(n)] = {
                "expected": expected,
                "per_b": per,
                "all_match": all(t == expected for t in totals) and len(totals) == 8,
            }
        raw = {"parameters": params, "results": results, "ops": E.ops_count()}
        so.write(json.dumps(results, indent=2) + "\n")
        reason = "known-false d=(1..1) recorded; n6_all_match=%s n8_all_match=%s" % (
            results["6"]["all_match"], results["8"]["all_match"])
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


def run_r8():
    run_id = RUNS["R8"]
    params = {"run_kind": "planted_yield", "seed": 760808,
              "exponent_window": [0.699, 1.301], "per_decade": [5, 20]}
    argv = [sys.argv[0], "--run", "R8"]
    run_dir, header, t0 = RC.open_run(run_id, argv, params)
    so, se = _tee_logs(run_dir)
    try:
        E.reset_ops()
        E.start_counting()
        rng = random.Random(760808)
        B_INTS = construct.B_INTS
        plants = []
        # Distinct (b, pattern) pairs; no shared h0 (IV-9). Heights ~ 10, 20, ...
        used_h0 = set()
        for i in range(9):
            rest = rng.sample(B_INTS, 4)
            b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
            p, g, s = E.mestre_polys(list(b))
            r = [E.peval(g, x) for x in b]
            inst, why = E.build_instance(list(b), [1] * 6, r, 6)
            h0 = inst["r_height"] if inst else None
            if h0 in used_h0:
                # re-draw rest until h0 distinct
                for _ in range(20):
                    rest = rng.sample(B_INTS, 4)
                    b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
                    p, g, s = E.mestre_polys(list(b))
                    r = [E.peval(g, x) for x in b]
                    inst, why = E.build_instance(list(b), [1] * 6, r, 6)
                    h0 = inst["r_height"] if inst else None
                    if h0 not in used_h0:
                        break
            if inst:
                used_h0.add(h0)
            plants.append({
                "index": i, "b": [str(x) for x in b], "pattern": [1] * 6,
                "h0": h0, "built": inst is not None, "reason": why,
                "r": [str(x) for x in r] if inst else None,
            })
        # Recover by construction solver at the planted b, d=(1..1)
        recovered = []
        for pl in plants:
            if not pl["built"]:
                continue
            b = [Fr(x) for x in pl["b"]]
            kept, near, meta = construct.solve_n6(E, b, [1] * 6, 10 ** 4)
            hit = any(inst["r_height"] == pl["h0"] for inst in kept)
            recovered.append({
                "index": pl["index"], "h0": pl["h0"], "recovered": hit,
                "n_solutions": len(kept), "meta": meta,
            })
        # decade ratios of recovered counts in H cells
        cells = {100: 0, 1000: 0, 10000: 0}
        for rec, pl in zip(recovered, [p for p in plants if p["built"]]):
            if rec["recovered"] and pl["h0"] is not None:
                for H in cells:
                    if pl["h0"] <= H:
                        cells[H] += 1
        ratios = {}
        if cells[100] > 0:
            ratios["1000/100"] = cells[1000] / cells[100]
        if cells[1000] > 0:
            ratios["10000/1000"] = cells[10000] / cells[1000]
        import math
        slope = None
        pts = [(math.log10(H), math.log10(c)) for H, c in cells.items() if c > 0]
        if len(pts) >= 2:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            n = len(pts)
            mx, my = sum(xs) / n, sum(ys) / n
            den = sum((x - mx) ** 2 for x in xs)
            slope = (sum((x - mx) * (y - my) for x, y in pts) / den) if den else None
        raw = {
            "parameters": params,
            "plants": plants,
            "recovered": recovered,
            "cells": cells,
            "decade_ratios": ratios,
            "log_log_slope": slope,
            "exponent_window": [0.699, 1.301],
            "per_decade_window": [5, 20],
            "ops": E.ops_count(),
            "iv9_distinct_h0": len(used_h0) == sum(1 for p in plants if p["built"]),
        }
        so.write(json.dumps({
            "n_plants": len(plants), "recovered": sum(1 for r in recovered if r["recovered"]),
            "cells": cells, "slope": slope, "ratios": ratios,
        }, indent=2) + "\n")
        reason = "planted yield recorded; recovered=%d/%d slope=%s" % (
            sum(1 for r in recovered if r["recovered"]),
            len(recovered), slope)
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
        if key == "R1":
            results[key] = run_r1()
        elif key == "R2":
            results[key] = run_r2()
        elif key == "R3":
            results[key] = _construct("R3", 6, 760806, N_B_N6, H6)
        elif key == "R4":
            results[key] = _construct("R4", 6, 760806, N_B_N6, H6, replay_of="R3")
        elif key == "R5":
            results[key] = _construct("R5", 8, 760810, N_B_N8, H8)
        elif key == "R6":
            # null family already frozen in null_family.py before this step
            results[key] = _construct("R6", 6, 760806, 64, [10000],
                                      null_family=True)
        elif key == "R7":
            results[key] = run_r7()
        elif key == "R8":
            results[key] = run_r8()
        print(results[key], flush=True)
    print(json.dumps({k: list(v) for k, v in results.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
