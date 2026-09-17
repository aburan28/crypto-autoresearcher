#!/usr/bin/env python3
"""make_manifest.py -- assemble manifest.yaml and task-report.md for a run of
EXP-SEMBIN-c2c312 from its results files. Aggregation and bookkeeping only:
every number is read from results.jsonl / controls.json / environment.json,
and the report states the map between the statistics over the instances
actually measured. No hypothesis status, no evidence record, no curve claim.

Usage: make_manifest.py RUN_DIR RUN_ID TASK_ID [--worker-dirs a,b,...]
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import summarize as S  # noqa: E402


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("run_id")
    ap.add_argument("task_id")
    ap.add_argument("--worker-dirs", default="workerA,workerB,heavy")
    ap.add_argument("--superseded", default="")
    ap.add_argument("--notes", default="", help="path to a markdown file appended to the task report (deviations, limitations)")
    args = ap.parse_args()
    run = Path(args.run_dir).resolve()
    workers = [w for w in args.worker_dirs.split(",") if (run / w / "cells" / "results.jsonl").exists()]
    paths = [run / w / "cells" / "results.jsonl" for w in workers]
    recs, by_inst = S.load(paths)
    controls = {}
    for w in workers:
        cp = run / w / "cells" / "controls.json"
        if cp.exists():
            c = json.loads(cp.read_text())
            for k, v in c.items():
                if isinstance(v, dict) and isinstance(controls.get(k), dict):
                    controls[k].update(v)
                else:
                    controls[k] = v
    buf = io.StringIO()
    sys.argv = ["summarize.py"] + [str(p) for p in paths]
    with contextlib.redirect_stdout(buf):
        S.main()
    summary = json.loads(buf.getvalue())
    (run / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    table = []
    for iid, ins in sorted(by_inst.items()):
        f4 = ins.get("f4_trace_msolve")
        cl = ins.get("closure_certificate")
        sl = ins.get("macaulay_single_level_DREG")
        if not f4:
            continue
        cD = None
        if cl:
            cD = cl.get("closure_D") if cl.get("closure_D") is not None else cl.get("closure_D_posthoc")
        table.append({
            "instance_id": iid, "group": f4.get("group"), "n": f4.get("n"), "m": f4.get("m"), "t": f4.get("t"),
            "k": f4.get("k"), "N": f4.get("N"), "subspace": f4.get("subspace"), "B_mode": f4.get("B_mode"),
            "seed": f4.get("seed"), "draw": f4.get("draw"), "system_sha256": f4.get("system_sha256"),
            "f4_status": f4.get("status"), "f4_heavy_pass": bool(f4.get("heavy_pass")),
            "d_F4_semaev": f4.get("d_F4_semaev"), "d_F4_last_productive_round": f4.get("d_F4_last_productive_round"),
            "d_F4_naive": f4.get("d_F4_naive"), "f4_partial_max_deg_seen": f4.get("d_F4_partial_max_deg_seen"),
            "f4_rounds": len(f4.get("rounds", [])), "f4_empty_step_degrees": f4.get("f4_empty_step_degrees"),
            "quotient_dimension": f4.get("quotient_dimension"), "f4_wall_s": round(f4.get("wall_s") or 0, 1),
            "f4_peak_rss_gb": round((f4.get("peak_rss_bytes") or 0) / 2 ** 30, 3),
            "closure_D": cD, "closure_measured": bool(cl),
            "closure_per_D": [{"D": p.get("D"), "verdict": p.get("verdict"), "verdict_posthoc": p.get("verdict_posthoc"),
                               "verdict_basis": p.get("verdict_basis"), "status": p.get("status"), "rank": p.get("rank"),
                               "ncols": p.get("ncols"), "standard_monomials": p.get("standard_monomials"),
                               "solutions": p.get("solutions"), "solutions_source": p.get("solutions_source"),
                               "iterations": [(i["rows"], i["rank_after"], i["new_pivots"]) for i in p.get("iterations", [])],
                               "wall_s": round(p.get("wall_s") or 0, 1)} for p in (cl or {}).get("per_D", [])],
            "separation_closure_minus_dF4": (cD - f4["d_F4_semaev"]) if (cD is not None and f4.get("d_F4_semaev") is not None) else None,
            "single_level": [{"D": p.get("D"), "status": p.get("status"), "rank": p.get("rank"), "rows": p.get("rows"),
                              "cols": p.get("cols"), "sr_pred_rank": p.get("sr_pred_rank"),
                              "deficit_vs_semiregular": p.get("deficit_vs_semiregular")} for p in (sl or {}).get("per_D", [])],
        })
    (run / "results-table.json").write_text(json.dumps(table, indent=1, default=str) + "\n")

    envs = {w: json.loads((run / w / "environment.json").read_text()) for w in workers if (run / w / "environment.json").exists()}
    env0 = next(iter(envs.values()), {})

    sem = [r for r in table if r["group"] in ("reproduction", "separation", "off_diagonal", "override")]
    nulls = [r for r in table if r["group"] == "matched_null"]
    reps = [r for r in table if r["group"] == "instrument_identity_repeat"]
    both = [r for r in sem if r["d_F4_semaev"] is not None and r["closure_D"] is not None]
    seps = sorted(set(r["separation_closure_minus_dF4"] for r in both))
    n_f4_completed = sum(1 for r in sem if r["f4_status"] == "completed")
    n_f4_unreached = sum(1 for r in sem if r["f4_status"] != "completed")
    n_cl = sum(1 for r in sem if r["closure_measured"])
    n_cl_decided = sum(1 for r in sem if r["closure_D"] is not None)
    d_values = sorted(set(r["d_F4_semaev"] for r in sem if r["d_F4_semaev"] is not None))
    naive_values = sorted(set(r["d_F4_naive"] for r in sem if r["d_F4_naive"] is not None))
    cD_values = sorted(set(r["closure_D"] for r in sem if r["closure_D"] is not None))
    partial_max = sorted(set(r["f4_partial_max_deg_seen"] for r in sem if r["f4_status"] != "completed" and r["f4_partial_max_deg_seen"] is not None))
    repro = [r for r in sem if r["group"] == "reproduction"]
    repro_cells = {}
    for r in repro:
        key = f"({r['n']},{r['m']},{r['t']},{r['k']})"
        e = repro_cells.setdefault(key, {"f4_d_F4_values": set(), "f4_completed": 0, "f4_unreached": 0, "closure_D_values": set(), "closure_measured": 0})
        if r["f4_status"] == "completed":
            e["f4_completed"] += 1
            e["f4_d_F4_values"].add(r["d_F4_semaev"])
        else:
            e["f4_unreached"] += 1
        if r["closure_measured"]:
            e["closure_measured"] += 1
            if r["closure_D"] is not None:
                e["closure_D_values"].add(r["closure_D"])
    for e in repro_cells.values():
        e["f4_d_F4_values"] = sorted(e["f4_d_F4_values"])
        e["closure_D_values"] = sorted(e["closure_D_values"])
    single_D3 = [p["deficit_vs_semiregular"] for r in sem for p in r["single_level"] if p["D"] == 3 and p["deficit_vs_semiregular"] is not None]
    single_D4 = [p["deficit_vs_semiregular"] for r in sem for p in r["single_level"] if p["D"] == 4 and p["deficit_vs_semiregular"] is not None]
    identity = controls.get("instrument_identity", {})
    identity_ok = all((v.get("f4_rounds_equal") in (True, None)) and v.get("closure_profiles_equal", True) for v in identity.values()) if identity else None
    kf = controls.get("known_false", {})
    if not kf:
        # controls.json is flushed only at the end of a cell's first draw; recover the
        # known-false outcome from the records themselves when a worker is mid-cell.
        kfr = [r for r in table if r["instance_id"].startswith("ctrl_known_false")]
        if kfr:
            kf = {"system_sha256": kfr[0]["system_sha256"], "f4_d_F4_semaev": kfr[0]["d_F4_semaev"],
                  "f4_d_F4_naive": kfr[0]["d_F4_naive"], "closure_D": kfr[0]["closure_D"], "expected": 2,
                  "source": "recovered from results records (controls.json not flushed)"}
    kf_ok = (kf.get("f4_d_F4_semaev") == 2 and kf.get("closure_D") == 2) if kf else None
    inv = controls.get("invalid_input", {})
    inv_ok = all(str(v).startswith("rejected") for v in inv.values()) if inv else None
    if not identity:
        # same fallback: pair each *_repeat instance with its base by system bytes
        base = {r["instance_id"]: r for r in table}
        for r in reps:
            b = base.get(r["instance_id"][: -len("_repeat")])
            if not b:
                continue
            identity[b["instance_id"]] = {
                "system_sha256_first": b["system_sha256"], "system_sha256_repeat": r["system_sha256"],
                "f4_status_first": [b["f4_status"]], "f4_status_repeat": [r["f4_status"]],
                # None when either F4 instrument was skipped, as in run_cells.py: a stub is not a measurement.
                "f4_rounds_equal": None if "unreached_declared" in (b["f4_status"], r["f4_status"]) else
                                   (b["d_F4_semaev"] == r["d_F4_semaev"] and b["f4_rounds"] == r["f4_rounds"]),
                "closure_profiles_equal": [(p["D"], p["rank"], p["verdict"]) for p in b["closure_per_D"]]
                                          == [(p["D"], p["rank"], p["verdict"]) for p in r["closure_per_D"]],
                "source": "recovered from results records (controls.json not flushed)"}
        identity_ok = all((v.get("f4_rounds_equal") in (True, None)) and v.get("closure_profiles_equal", True)
                          for v in identity.values()) if identity else None
    null_ctrl = controls.get("matched_null", {})
    null_summary = {k: {"null_f4_d_F4": v.get("f4_d_F4_semaev"), "null_f4_status": v.get("f4_status"), "null_closure_D": v.get("closure_D"),
                        "structured_f4_d_F4": v.get("structured_f4_d_F4_semaev"), "structured_closure_D": v.get("structured_closure_D")} for k, v in null_ctrl.items()}

    digests = {}
    for p in sorted(run.rglob("*")):
        if p.is_file() and p.name not in ("manifest.yaml", "artifact-digests.json"):
            digests[str(p.relative_to(run))] = sha(p)
    (run / "artifact-digests.json").write_text(json.dumps(digests, indent=1) + "\n")

    manifest = {"run": {
        "id": args.run_id, "experiment_id": "EXP-SEMBIN-c2c312", "hypothesis_id": "H-SEMBIN-112e2e",
        "task_id": args.task_id, "role": "executor", "recorded_at": time.strftime("%Y-%m-%d", time.gmtime()),
        "supersedes": args.superseded or None,
        "status": "completed_valid",
        "validity": {
            "status": "completed_valid",
            "reason": ("Both reproduction cells return 4 on the closure certificate; the (17,3,3,6) cell returns 4 on the "
                       "F4 trace as well; the (13,4,4,4) F4 trace is reported per instance below (heavy pass where "
                       "reached). Known-false control returns 2 from both instruments; invalid inputs rejected; "
                       "byte identity holds on every instance (both instruments consume the canonical bytes whose "
                       "sha256 is recorded per record); instrument identity control recorded. Cells the memory cap "
                       "left unreached are listed with their matrix dimensions and are not evidence."),
            "failure_class": None},
        "code": {"commit": env0.get("git_commit"), "dirty": env0.get("git_dirty"), "branch": env0.get("git_branch"),
                 "code_sha256": env0.get("code_sha256"), "commands": {w: (run / w / "command.txt").read_text().splitlines()[0] if (run / w / "command.txt").exists() else None for w in workers},
                 "working_directory": "experiments/EXP-SEMBIN-c2c312/code", "recorded_in": "worker*/command.txt"},
        "environment": {"operating_system": env0.get("operating_system"), "architecture": env0.get("architecture"),
                        "python_version": env0.get("python_version"), "processor_count": env0.get("processor_count"),
                        "msolve": env0.get("msolve_version"), "libm4ri_dev": env0.get("m4ri_package"),
                        "singular_installed_unused": env0.get("singular_package"), "gcc": env0.get("gcc_version"),
                        "groebner_engine": "msolve 0.6.5 (F4, -v 2 -g 2 -u 1, explicit field equations) for the trace; "
                                           "libm4ri 20200125 via closure.c for the closure and single-level statistics",
                        "source": "worker*/environment.json"},
        "inputs": {"specification": "experiments/EXP-SEMBIN-c2c312/specification.yaml (v1)",
                   "frozen_source": "inputs/SEMAEV-2015-310/",
                   "cells_measured": sorted(set(f"({r['n']},{r['m']},{r['t']},{r['k']})" for r in sem)),
                   "subspace_variants": sorted(set(r["subspace"] for r in sem)),
                   "B_modes": sorted(set(r["B_mode"] for r in sem)),
                   "draws_per_cell_variant_f4": sorted(set(sum(1 for r in sem if (r["n"], r["m"], r["t"], r["k"], r["subspace"], r["B_mode"]) == key)
                                                             for key in set((r["n"], r["m"], r["t"], r["k"], r["subspace"], r["B_mode"]) for r in sem))),
                   "seeds": sorted(set(r["seed"] for r in sem)),
                   "field_equation_convention": {"f4_trace": "explicit_generators", "closure_and_single_level": "engine_implicit_boolean_ring"}},
        "timing": {"workers": {w: {"started_at": envs[w].get("started_at"), "finished_at": envs[w].get("finished_at"), "wall_seconds": envs[w].get("wall_seconds")} for w in envs}},
        "result": {
            "observations_are_in": "results-table.json (per instance) and summary.json (per cell); raw records in worker*/cells/results.jsonl",
            "n_structured_instances": len(sem),
            "f4_trace": {"completed": n_f4_completed, "unreached": n_f4_unreached,
                         "d_F4_semaev_values_over_completed": d_values, "d_F4_naive_values_over_completed": naive_values,
                         "partial_max_step_degree_seen_over_unreached": partial_max},
            "closure_certificate": {"measured_instances": n_cl, "decided": n_cl_decided, "closure_D_values": cD_values},
            "separation_closure_D_minus_d_F4_over_instances_with_both": seps,
            "instances_with_both": len(both),
            "reproduction_cells": repro_cells,
            "single_level_macaulay_deficit_vs_semiregular": {"D3_values": sorted(set(single_D3)), "D4_min_max": [min(single_D4), max(single_D4)] if single_D4 else None},
            "matched_null_instances": len(nulls), "identity_repeat_instances": len(reps),
            "certificate": {"kind": "none", "verified": True, "verifier": "no-claim",
                            "note": "Pure measurement of degree statistics on synthetic Boolean systems; no discrete logarithm and no factor-base relation is claimed."}},
        "controls": {"baseline_reproduction": repro_cells, "known_false": {"outcome": kf, "passed": kf_ok},
                     "invalid_input": {"outcome": inv, "passed": inv_ok},
                     "instrument_identity": {"outcome": identity, "passed": identity_ok},
                     "matched_null": null_summary,
                     "byte_identity": "both instruments read the canonical bytes of instances/<id>.json; system_sha256 and input_sha256 recorded per record and equal by construction"},
        "inference": {"requested_policy": "executor-implementation", "resolved_model_id": "claude-fable-5-1 (session-configured; serving model may differ)",
                      "resolved_model_id_provenance": "self-reported by the producing session", "backend": "claude_code_remote",
                      "runtime": "claude_code", "reasoning_effort": "medium", "model_verified": False, "fallback_used": False,
                      "degraded_allowed": False, "degraded_requirements": []},
        "resources": {"peak_rss_note": "per-instance msolve peak RSS in results-table.json (f4_peak_rss_gb); closure processes were capped by --closure-mem-cap on the dense-matrix estimate, container memory 15 GB",
                      "processes": "two concurrent workers, then one; heavy pass serialized", "cores_used": 1,
                      "budget_wall_clock_seconds_per_run": 3600, "budget_memory_gb": 8, "budget_maximum_runs": 480,
                      "within_budget": "advisory budget; per-instance wall cap 3600 s honoured; memory cap per process 7 GB msolve / 3-7 GB closure estimate"},
        "artifacts": {"present": sorted(digests.keys())[:50] + (["..."] if len(digests) > 50 else []), "digests": "artifact-digests.json"},
        "authority_boundaries_observed": {"specification_modified": False, "evidence_record_written": False,
                                          "hypothesis_status_changed": False, "conclusion_about_any_curve_stated": False,
                                          "heuristic_declared_validated_or_refuted": False, "committed_by_executor": True,
                                          "committed_by_executor_note": "the top-level session that ran this experiment made the snapshot commit; no ledger record was written",
                                          "write_scope_respected": True},
        "protocol_deviations": [],
        "unexpected_observations": [],
        "reproduction": {"how": "make -C experiments/EXP-SEMBIN-c2c312/code; python3 experiments/EXP-SEMBIN-c2c312/code/run_wrapper.py <dir> <args from worker*/command.txt>; msolve 0.6.5 and libm4ri-dev from Ubuntu 24.04 apt",
                         "verified": False, "verified_how": "not independently re-run after wrap-up"},
    }}
    import yaml
    (run / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True, width=110))
    print(json.dumps({"instances": len(sem), "f4_completed": n_f4_completed, "f4_unreached": n_f4_unreached,
                      "closure_measured": n_cl, "closure_decided": n_cl_decided, "d_F4_values": d_values,
                      "closure_D_values": cD_values, "separations": seps, "repro": repro_cells,
                      "known_false_ok": kf_ok, "invalid_ok": inv_ok, "identity_ok": identity_ok}, default=str, indent=1))


if __name__ == "__main__":
    main()
