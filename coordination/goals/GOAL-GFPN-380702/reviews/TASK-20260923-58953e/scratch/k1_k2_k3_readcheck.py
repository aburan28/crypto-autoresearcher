#!/usr/bin/env python3
"""
TASK-20260923-58953e -- reading-only checks for joints K1, K2, K3.
Reads archived run packages of EXP-GFPN-05ff43 and recomputes the aggregate
RUN-GFPN-ca7b88 from its 30 input raw-result.json files with this
validator's own code (no producer module is imported). Runs no solver.
Output: JSON on stdout.
"""
import json, os, glob, sys, hashlib
import yaml

REPO = sys.argv[1]
RUNS = os.path.join(REPO, "experiments/EXP-GFPN-05ff43/runs")
AGG = "RUN-GFPN-ca7b88"


def load(rid, name):
    return json.load(open(os.path.join(RUNS, rid, name))) if name.endswith(".json") else \
        yaml.safe_load(open(os.path.join(RUNS, rid, name)))


out = {}
# ---------------------------------------------------------------- K2 (c)
cmd = open(os.path.join(RUNS, AGG, "command.txt")).read().split("--runs ")[1].split()[0]
inputs = cmd.split(",")
all_runs = sorted(os.path.basename(d) for d in glob.glob(os.path.join(RUNS, "RUN-GFPN-*")))
outside = sorted(set(all_runs) - set(inputs) - {AGG})
out["n_packages"] = len(all_runs)
out["aggregate_inputs"] = len(inputs)
out["outside_aggregate"] = {r: load(r, "raw-result.json").get("kind") for r in outside}

cells, excluded = {}, []
for rid in inputs:
    raw = load(rid, "raw-result.json")
    mt = raw.get("metrics") or {}
    par = raw.get("parameters") or {}
    if raw.get("kind") not in ("cell", "raw"):
        excluded.append((rid, "kind " + str(raw.get("kind"))))
        continue
    arm, shape, m, p = mt.get("arm") or par.get("arm"), mt.get("curve_shape") or par.get("curve_shape"), \
        mt.get("m") or par.get("m"), mt.get("p") or par.get("p")
    if None in (arm, shape, m, p):
        excluded.append((rid, "no cell identity in raw-result (status %s)" % raw.get("run_status")))
        continue
    tk = mt.get("target_kind") or par.get("target_kind") or "random"
    # independent evidence of target kind: seeds string
    seeds = json.dumps(raw.get("seeds"))
    tk_seed = "constructed_solvable" if "solvable" in seeds else ("random" if "targets" in seeds else "unknown")
    key = (arm, shape, m, p, tk)
    if key in cells:
        out.setdefault("key_collisions", []).append([rid, cells[key]["run"]])
    # recompute D and success from per-target rows
    rows = raw.get("targets") or []
    meas = [r for r in rows if r.get("status") == "measured"]
    Ds = [r.get("D") for r in meas if r.get("D") is not None]
    succ = sum(1 for r in meas if (r.get("n_relations_verified") or 0) > 0)
    cells[key] = {"run": rid, "status": raw.get("run_status"), "D_recorded": mt.get("ideal_degree_D"),
                  "D_recomputed": (Ds[0] if Ds and all(d == Ds[0] for d in Ds) else None),
                  "n_measured_rows": len(meas), "n_target_rows": len(rows),
                  "succ_recomputed": succ,
                  "decomposition_success_rate": mt.get("decomposition_success_rate"),
                  "success_rate_by_construction": mt.get("success_rate_by_construction"),
                  "target_kind_metrics": mt.get("target_kind"), "target_kind_params": par.get("target_kind"),
                  "target_kind_from_seeds": tk_seed, "targets_attempted_field": mt.get("targets_attempted"),
                  "m5_timeout_count": mt.get("m5_timeout_count"),
                  "lifted_verified_points_total": mt.get("lifted_verified_points_total"),
                  "n_certificates": len(raw.get("certificates") or [])}
out["n_cells_recomputed"] = len(cells)
out["excluded_recomputed"] = excluded

# heur_dflat per frozen statement: m = 5, random targets, >=3 primes spanning >=12 bits
dflat = {}
for arm in ("raw", "S5", "torsion_S5"):
    for shape in ("ecgfp5_shaped", "random_2torsion", "random_no2torsion"):
        pts = [(k[3], c["D_recomputed"]) for k, c in cells.items()
               if k[0] == arm and k[1] == shape and k[2] == 5 and k[4] == "random" and c["D_recomputed"] is not None]
        attempted = [c["run"] for k, c in cells.items() if k[0] == arm and k[1] == shape and k[2] == 5]
        dflat["%s|%s" % (arm, shape)] = {"completed_m5_cells_with_D": len(pts), "m5_runs_attempted": attempted,
                                         "value_by_frozen_rule": "not_applicable (insufficient m=5 D)" if len(pts) < 3 else "decidable"}
out["heur_dflat_recomputed"] = dflat
agg_raw = load(AGG, "raw-result.json")
out["heur_dflat_recorded"] = agg_raw["metrics"]["heur_dflat_pass"]
out["cost_band_recorded"] = agg_raw["cost_band"]["arms"]
out["comparisons_recorded"] = agg_raw["comparisons"]
out["matched_control_check_F4_recorded"] = agg_raw["matched_control_check_F4"]
out["excluded_recorded"] = agg_raw["excluded_runs"]
out["metrics_recorded"] = {k: agg_raw["metrics"][k] for k in ("n_runs", "n_cells", "n_excluded_runs")}

# ---------------------------------------------------------------- K3 (a)
# every place a constructed-solvable value appears, and whether it is labelled
k3 = []
for key, c in sorted(cells.items()):
    if c["target_kind_from_seeds"] != "constructed_solvable" and key[4] != "constructed_solvable":
        continue
    rid = c["run"]
    man = load(rid, "manifest.yaml")["run"]
    mm = man["result"]["metrics"]
    lt = load(rid, "ladder-table.yaml")["ladder_table"]
    hd = load(rid, "heur-dflat.yaml")["heur_dflat"]
    ltrow = (lt.get("rows") or [{}])[0]
    k3.append({"run": rid, "arm": key[0], "m": key[2], "p": key[3],
               "manifest_target_kind": mm.get("target_kind") or man["inputs"]["parameters"].get("target_kind"),
               "manifest_decomposition_success_rate": mm.get("decomposition_success_rate"),
               "manifest_success_rate_by_construction": mm.get("success_rate_by_construction"),
               "manifest_ideal_degree_D": mm.get("ideal_degree_D"),
               "ladder_table_row_has_target_kind": "target_kind" in ltrow,
               "ladder_table_row_D": ltrow.get("D"), "ladder_table_row_success_rate": ltrow.get("success_rate"),
               "ladder_table_note": lt.get("note"),
               "heur_dflat_cell_D": hd.get("cell_D"), "heur_dflat_file_has_target_kind": "target_kind" in json.dumps(hd)})
out["k3_constructed_solvable_occurrences"] = k3
agg_rows = agg_raw["ladder_rows"]
out["k3_aggregate_rows_constructed"] = [{"run": r["run"], "arm": r["arm"], "m": r["m"], "target_kind": r["target_kind"],
                                          "success_rate": r["success_rate"],
                                          "success_rate_by_construction": r["success_rate_by_construction"], "D": r["D"]}
                                         for r in agg_rows if r["target_kind"] == "constructed_solvable"]

# K3 (b): supplementary D vs msolve outputs; raw m=3 certificate duplication
dup = {}
for rid in ("RUN-GFPN-cdf887", "RUN-GFPN-d3f21e", "RUN-GFPN-d4415d", "RUN-GFPN-49f7c5", "RUN-GFPN-5f9840"):
    raw = load(rid, "raw-result.json")
    per_t = {}
    for crec in raw.get("certificates") or []:
        cert = json.load(open(os.path.join(RUNS, rid, crec["path"])))
        pts = cert.get("points") or cert.get("relation", {}).get("points")
        if pts is None:
            pts = [v for k, v in cert.items() if "point" in k.lower() and isinstance(v, list)]
        signs = cert.get("signs")
        per_t.setdefault(crec["target"], []).append(
            hashlib.sha256(json.dumps(sorted(json.dumps([p, s]) for p, s in zip(pts, signs or [None] * len(pts)))).encode()).hexdigest()[:16])
    n_sol = [r.get("n_rational_solutions") for r in raw.get("targets") or []]
    dup[rid] = {"targets": len(per_t), "certs_per_target": sorted({len(v) for v in per_t.values()}),
                "distinct_signed_point_multisets_per_target": sorted({len(set(v)) for v in per_t.values()}),
                "n_rational_solutions_per_target": sorted(set(n_sol)),
                "D_values": sorted(set(r.get("D") for r in raw.get("targets") or []))}
out["k3_certificate_multiplicity"] = dup

# ---------------------------------------------------------------- K1 (a): exhausted cells
k1 = {}
for rid in all_runs:
    man = load(rid, "manifest.yaml")["run"]
    if man["status"] == "failed" and man.get("failure_class") == "resource_exhaustion" or \
            (man["result"].get("not_measured") or []):
        raw = load(rid, "raw-result.json")
        mt = man["result"]["metrics"] or {}
        nm = man["result"]["not_measured"] or []
        k1[rid] = {"status": man["status"], "failure_class": man.get("failure_class"),
                   "arm": (man["inputs"]["parameters"] or {}).get("arm"), "m": (man["inputs"]["parameters"] or {}).get("m"),
                   "p": (man["inputs"]["parameters"] or {}).get("p"),
                   "shape": (man["inputs"]["parameters"] or {}).get("curve_shape"),
                   "D": mt.get("ideal_degree_D"), "certificate_kind": man["result"]["certificate"]["kind"],
                   "n_not_measured": len(nm),
                   "not_measured_attempted": sum(1 for x in nm if "outcome" in x),
                   "not_measured_unattempted_with_reason": sum(1 for x in nm if "outcome" not in x and x.get("reason") and x.get("class")),
                   "outcomes": sorted({x.get("outcome") for x in nm if x.get("outcome")}),
                   "msolve_logs": len(glob.glob(os.path.join(RUNS, rid, "*.ms.log"))),
                   "targets_attempted_field": mt.get("targets_attempted"),
                   "m5_timeout_count_field": mt.get("m5_timeout_count"),
                   "memory_cap_gb_parameters": (man["inputs"]["parameters"] or {}).get("memory_cap_gb"),
                   "memory_cap_gb_resources": man["resources"].get("memory_cap_gb")}
out["k1_exhausted_or_not_measured"] = k1
print(json.dumps(out, indent=1, default=str))
