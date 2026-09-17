#!/usr/bin/env python3
"""assemble.py -- build the immutable run package for a run of EXP-SEMBIN-7e1371
from the workers' results.jsonl files.

Aggregation and bookkeeping only: every number here is copied from a record a
worker wrote, and nothing is interpreted.  Produces, at the run root:

  results-table.json   one row per (instance, instrument), keyed by the
                       contract's (n, m, t, k, family, subspace, B, seed)
  summary.json         per-cell rollup: verdicts, deficiency profiles in k and
                       in n, unreached cells with their column counts
  manifest.yaml        the run record (schema of RUN-SEMBIN-b6eb9f/manifest.yaml)
  artifact-digests.json sha256 of every file in the package
  command.txt, environment.json, stdout.log, stderr.log, raw-result.json
                       run-root aggregates required by tools/validate_ledger.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def load(run: Path):
    recs, workers = [], []
    for res in sorted(run.glob("*/cells/results.jsonl")):
        workers.append(res.parent.parent.name)
        for line in res.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                r["_worker"] = res.parent.parent.name
                recs.append(r)
    return recs, workers


def dedupe(recs):
    """First record wins for a repeated (instance, instrument); a later record is
    kept only if the earlier one did not complete."""
    best, dups = {}, 0
    for r in recs:
        key = (r["instance_id"], r["instrument"])
        if key not in best:
            best[key] = r
            continue
        dups += 1
        prev = best[key]
        prev_ok = prev.get("status") in ("completed", "not_applicable") or prev.get("closure_D")
        now_ok = r.get("status") in ("completed", "not_applicable") or r.get("closure_D")
        if now_ok and not prev_ok:
            best[key] = r
    return list(best.values()), dups


def cell_of(r):
    return (r.get("n"), r.get("m"), r.get("t"), r.get("k"))


def summarize(recs):
    by_inst: dict = {}
    for r in recs:
        by_inst.setdefault(r["instance_id"], {})[r["instrument"]] = r
    cells: dict = {}
    for iid, insts in by_inst.items():
        any_rec = next(iter(insts.values()))
        fam = any_rec.get("family")
        key = f"{cell_of(any_rec)}|{fam}"
        c = cells.setdefault(key, {
            "cell": list(cell_of(any_rec)), "family": fam, "instances": 0,
            "N": any_rec.get("N"), "n_equations": any_rec.get("n_equations"),
            "degree4_columns": any_rec.get("degree4_columns"),
            "max_generator_degree": any_rec.get("max_generator_degree"),
            "degree4_sufficiency_verdicts": {}, "closure_D_values": [],
            "single_level_D4_rank": [], "single_level_D4_deficiency_vs_columns": [],
            "single_level_D4_deficit_vs_semiregular": [], "single_level_D4_status": {},
            "exact_solution_counts": [], "f4_status": {}, "d_F4_semaev": [],
            "d_F4_naive": [], "f4_quotient_dimension": [],
            "closure_standard_monomials": [], "peak_rss_bytes_f4": [],
            "wall_seconds_closure": [], "unreached": []})
        c["instances"] += 1
        cl = insts.get("closure_certificate")
        if cl:
            v = cl.get("degree4_sufficiency_verdict")
            c["degree4_sufficiency_verdicts"][str(v)] = c["degree4_sufficiency_verdicts"].get(str(v), 0) + 1
            if cl.get("closure_D") is not None:
                c["closure_D_values"].append(cl["closure_D"])
            for p in cl.get("per_D", []):
                if p.get("D") == 4 and p.get("standard_monomials") is not None:
                    c["closure_standard_monomials"].append(p["standard_monomials"])
                if p.get("status") in ("unreached_declared", "hit_cap", "unreached"):
                    c["unreached"].append({"instrument": "closure", "D": p.get("D"),
                                           "ncols": p.get("ncols"), "reason": p.get("reason")})
                if p.get("wall_s") is not None:
                    c["wall_seconds_closure"].append(round(p["wall_s"], 1))
        sl = insts.get("macaulay_single_level")
        if sl:
            for p in sl.get("per_D", []):
                if p.get("D") != 4:
                    continue
                c["single_level_D4_status"][str(p.get("status"))] = \
                    c["single_level_D4_status"].get(str(p.get("status")), 0) + 1
                if p.get("rank") is not None:
                    c["single_level_D4_rank"].append(p["rank"])
                if p.get("deficiency_vs_columns") is not None:
                    c["single_level_D4_deficiency_vs_columns"].append(p["deficiency_vs_columns"])
                if p.get("deficit_vs_semiregular") is not None:
                    c["single_level_D4_deficit_vs_semiregular"].append(p["deficit_vs_semiregular"])
                if p.get("status") in ("unreached_declared",):
                    c["unreached"].append({"instrument": "single_level", "D": 4,
                                           "ncols": p.get("cols"), "reason": p.get("reason")})
        sc = insts.get("exhaustive_solution_count")
        if sc and sc.get("solutions") is not None:
            c["exact_solution_counts"].append(sc["solutions"])
        f4 = insts.get("f4_trace_msolve")
        if f4:
            c["f4_status"][str(f4.get("status"))] = c["f4_status"].get(str(f4.get("status")), 0) + 1
            for field, dest in (("d_F4_semaev", "d_F4_semaev"), ("d_F4_naive", "d_F4_naive"),
                                ("quotient_dimension", "f4_quotient_dimension"),
                                ("peak_rss_bytes", "peak_rss_bytes_f4")):
                if f4.get(field) is not None:
                    c[dest].append(f4[field])
            if f4.get("status") not in ("completed",):
                c["unreached"].append({"instrument": "f4_trace", "status": f4.get("status"),
                                       "reason": f4.get("unreached_reason"),
                                       "partial_max_step_degree": f4.get("d_F4_partial_max_deg_seen")})
    for c in cells.values():
        for kk in list(c):
            if isinstance(c[kk], list) and kk not in ("cell", "unreached"):
                c[kk] = sorted(set(c[kk]), key=lambda x: (x is None, x))
    return cells


def sha256_file(p: Path):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=REPO).stdout.strip()
    except Exception as exc:
        return f"error: {exc}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--status", default="completed_valid")
    ap.add_argument("--validity-reason", required=True)
    args = ap.parse_args()
    run = Path(args.run_dir).resolve()

    recs, workers = load(run)
    recs, dups = dedupe(recs)
    cells = summarize(recs)

    rows = []
    for r in sorted(recs, key=lambda x: (str(x.get("family")), x.get("n") or 0, x.get("k") or 0,
                                         x["instance_id"], x["instrument"])):
        rows.append({k: v for k, v in r.items() if k not in ("rounds", "per_D", "iterations")}
                    | {"per_D": r.get("per_D"), "f4_round_count": len(r.get("rounds", []) or [])})
    (run / "results-table.json").write_text(json.dumps(rows, indent=1, sort_keys=True, default=str) + "\n")

    controls = {}
    for cf in sorted(run.glob("*/cells/controls.json")):
        controls[cf.parent.parent.name] = json.loads(cf.read_text())

    scale = json.loads(subprocess.run([sys.executable, str(HERE / "crypto_scale.py")],
                                      capture_output=True, text=True, check=True).stdout)
    (run / "crypto-scale-arithmetic.json").write_text(json.dumps(scale, indent=1) + "\n")

    summary = {"run_id": args.run_id, "experiment_id": "EXP-SEMBIN-7e1371",
               "n_records": len(recs), "duplicate_records_resolved": dups,
               "workers": workers, "cells": cells, "controls": controls,
               "crypto_scale_arithmetic": "crypto-scale-arithmetic.json (derived from the paper's "
                                          "formulas; NOT a measurement of this run)"}
    (run / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n")

    envs = {}
    for ef in sorted(run.glob("*/environment.json")):
        envs[ef.parent.name] = json.loads(ef.read_text())
    first = next(iter(envs.values()), {})
    commands = {}
    for cf in sorted(run.glob("*/command.txt")):
        commands[cf.parent.name] = cf.read_text().splitlines()[0]
    (run / "command.txt").write_text(
        "\n".join(f"{k}: {v}" for k, v in commands.items()) + "\n")
    (run / "environment.json").write_text(json.dumps(envs, indent=2, sort_keys=True) + "\n")
    for name in ("stdout.log", "stderr.log"):
        parts = []
        for f in sorted(run.glob(f"*/{name}")):
            parts.append(f"===== {f.parent.name} =====\n" + f.read_text())
        (run / name).write_text("".join(parts) or f"(no {name} produced by any worker)\n")
    (run / "raw-result.json").write_text(json.dumps(
        {"note": "aggregate of every worker's raw records; per-instrument records are in "
                 "results-table.json and the workers' cells/results.jsonl",
         "n_records": len(recs), "workers": workers, "controls": controls}, indent=1, default=str) + "\n")

    manifest = {"run": {
        "id": args.run_id, "experiment_id": "EXP-SEMBIN-7e1371", "hypothesis_id": "H-SEMBIN-2d7708",
        "task_id": args.task_id, "role": "executor",
        "recorded_at": sh(["date", "-u", "+%Y-%m-%d"]),
        "status": args.status,
        "validity": {"status": args.status, "reason": args.validity_reason, "failure_class": None},
        "code": {
            "commit": sh(["git", "rev-parse", "HEAD"]),
            "dirty": bool(sh(["git", "status", "--porcelain"])),
            "branch": sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
            "code_sha256": {p.name: sha256_file(p) for p in sorted(HERE.iterdir())
                            if p.is_file() and p.suffix in (".py", ".c", ".so")},
            "code_sha256_by_worker": {k: v.get("code_sha256") for k, v in envs.items()},
            "code_changed_during_run": len({json.dumps(v.get("code_sha256"), sort_keys=True)
                                            for v in envs.values()}) > 1,
            "code_change_note": ("run_cert.py gained options while the run was in flight "
                                 "(--draw-list, --no-single, and the chained-system exact counter). "
                                 "Each worker's environment.json records the hash of the code it "
                                 "actually ran; a worker launched before a change did not see it. "
                                 "The changes are additive -- no instrument's arithmetic was altered "
                                 "-- but the per-worker hashes are published rather than flattened."),
            "command": next(iter(commands.values()), "see command.txt"),
            "command_note": "this run was produced by several worker processes; every command is in "
                            "command.txt at the run root and in each worker's own command.txt",
            "commands": commands,
            "working_directory": "experiments/EXP-SEMBIN-7e1371/code",
            "recorded_in": "command.txt, */command.txt"},
        "environment": {
            "operating_system": first.get("operating_system"),
            "architecture": first.get("architecture"),
            "python_version": first.get("python_version"),
            "processor_count": first.get("processor_count"),
            "libm4ri_dev": first.get("m4ri_package"),
            "gcc": first.get("gcc_version"),
            "groebner_engine": "msolve 0.6.5 (F4, -v 2 -g 2 -u 1, explicit field equations) for the "
                               "trace; libm4ri 20200125 via closure.c for the closure and single-level "
                               "blocks; count_m2.c (no solver) for the exact solution counts",
            "source": "*/environment.json"},
        "inputs": {
            "specification": "experiments/EXP-SEMBIN-7e1371/specification.yaml (v1)",
            "frozen_source": "inputs/SEMAEV-2015-310/",
            "cells_measured": sorted({str(tuple(c["cell"])) for c in cells.values()}),
            "families": sorted({c["family"] for c in cells.values()}),
            "seeds": [20260913101, 20260913102, 20260913103, 20260913104, 20260913105],
            "field_equation_convention": {
                "f4_trace": "explicit_generators",
                "closure_and_single_level": "engine_implicit_boolean_ring",
                "exact_count": "not applicable (enumeration over V, no polynomial system solved)"}},
        "timing": {"workers": {k: {"started_at": v.get("started_at"), "finished_at": v.get("finished_at"),
                                   "wall_seconds": v.get("wall_seconds")} for k, v in envs.items()}},
        "result": {
            "observations_are_in": "results-table.json (per instance), summary.json (per cell); raw "
                                   "records in */cells/results.jsonl",
            "n_structured_instances": len({r["instance_id"] for r in recs}),
            "duplicate_records_resolved": dups,
            "certificate": {"kind": "none", "verified": True, "verifier": "no-claim",
                            "note": "Pure measurement of degree statistics and exact solution counts on "
                                    "synthetic Boolean systems; no discrete logarithm and no factor-base "
                                    "relation is claimed."}},
        "controls": controls,
    }}
    (run / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False, width=110,
                                                      default_flow_style=False))
    digests = {}
    for p in sorted(run.rglob("*")):
        if p.is_file() and p.name != "artifact-digests.json":
            digests[str(p.relative_to(run))] = sha256_file(p)
    (run / "artifact-digests.json").write_text(json.dumps(digests, indent=1, sort_keys=True) + "\n")
    print(f"records={len(recs)} instances={len({r['instance_id'] for r in recs})} cells={len(cells)} "
          f"duplicates_resolved={dups} files={len(digests)}")


if __name__ == "__main__":
    main()
