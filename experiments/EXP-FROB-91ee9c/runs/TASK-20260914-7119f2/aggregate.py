#!/usr/bin/env python3
"""Aggregator: reads work/*.out.json + checker-report.json and produces the
declared run artifacts. Plain python3, no sage needed."""
import json, os, sys, hashlib, subprocess, datetime
from fractions import Fraction

RUN = "/home/user/crypto-autoresearcher/experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2"
WORK = os.path.join(RUN, "work")
CELLS = ["FROB-SPLIT-q11n5", "FROB-NOLATTICE-q13n5", "FROB-EQDEG-q19n5"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def load_cell(cell):
    path = os.path.join(WORK, f"{cell}.out.json")
    lines = open(path).read().splitlines()
    return json.loads(lines[1])


def frac_str(fr):
    if fr is None:
        return None
    return f"{fr[0]}/{fr[1]}"


def frac_val(fr):
    if fr is None:
        return None
    if fr[1] == 0:
        return None
    return fr[0] / fr[1]


def build_raw_jsonl(cell_data, ext_data):
    lines = []
    for cell, data in cell_data.items():
        lines.append(json.dumps({"record_type": "cell_full_dump", "cell": cell, "data": data}, default=str))
    lines.append(json.dumps({"record_type": "cell_full_dump", "cell": "FROB-EXT-q13n7", "data": ext_data}, default=str))
    with open(os.path.join(RUN, "raw.jsonl"), "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    cell_data = {c: load_cell(c) for c in CELLS}
    ext_probe_path = os.path.join(WORK, "FROB-EXT-q13n7.probe.json")
    ext_data = json.load(open(ext_probe_path)) if os.path.exists(ext_probe_path) else {}
    checker_report = json.load(open(os.path.join(WORK, "checker-report.json")))

    build_raw_jsonl(cell_data, ext_data)

    # ---------------------------------------------------------- metrics.json
    measured = {}
    modelled = {}
    derived = {}
    for cell, data in cell_data.items():
        measured[cell] = {
            "cell_status": data["cell_status"],
            "cell_status_reason": data["cell_status_reason"],
            "factorisation": data["factorisation"],
            "C5_measured": {k: v for k, v in data["C5"].items()},
            "achievable_multiset_table": data["achievable_multiset_table"],
            "divisor_lattice_dims": data["divisor_lattice_dims"],
            "object_search": data["object_search"],
            "curves": [],
        }
        modelled[cell] = {"partitions": [], "formula_note":
                           "modelled_|B_j| = q^{d_j}/c ; modelled_U_neg = (1/2) sum_j modelled_|B_j| ; "
                           "modelled_p_m = min(1, prod_j modelled_|B_j| / (N-1)) ; "
                           "modelled_cost_ratio = (modelled_U_neg + 1 + extra) / modelled_p_m"}
        derived[cell] = {"object_arm": [], "C2_arm": [], "C3_arm": {}, "C4_arm": {}}

        q, n = data["q"], data["n"]
        for ci, c in enumerate(data["curves"]):
            curve = c["curve"]
            cofactor = curve["cofactor"]
            N = c["N"]
            measured_curve = {
                "curve": {k: v for k, v in curve.items()},
                "N": N,
                "object_arm_partitions_measured": [
                    {"partition_blocks": r["partition_blocks"], "slot_count_m": r["slot_count_m"],
                     "slot_dims": r["slot_dims"], "status": r["status"],
                     "p_m": r.get("p_m"), "U_neg": r.get("U_neg"),
                     "distinct_targets": r.get("distinct_targets"),
                     "prod_tuple_count": r.get("prod_tuple_count"),
                     "block_sizes": r.get("block_sizes"),
                     "B_union_size": r.get("B_union_size")}
                    for r in c["object_arm_partitions"]
                ],
            }
            if "C1" in c:
                measured_curve["C1"] = c["C1"]
            if "C6" in c:
                measured_curve["C6"] = c["C6"]
            measured[cell]["curves"].append(measured_curve)

            # derived_from_measured: cost_ratio_neg per partition per extra
            for r in c["object_arm_partitions"]:
                rec = {"curve_A": curve["A"], "curve_B": curve["B"],
                       "partition_blocks": r["partition_blocks"], "slot_dims": r["slot_dims"],
                       "status": r["status"]}
                if r["status"] == "ok":
                    rec["cost_ratio_neg"] = r["cost_ratio_neg"]
                    rec["formula"] = "(U_neg + 1 + extra) / p_m"
                derived[cell]["object_arm"].append(rec)

            # modelled: independent of measured B_j; uses q, d_j, cofactor, N.
            # All values are EXACT rationals (fractions.Fraction), per IR-1 --
            # "modelled" is not exempt from the no-floating-point rule.
            for r in c["object_arm_partitions"]:
                d_js = r["slot_dims"]
                model_Bj = [Fraction(q ** d, cofactor) for d in d_js]
                model_Uneg = sum(model_Bj, Fraction(0)) / 2
                prod = Fraction(1)
                for b in model_Bj:
                    prod *= b
                model_pm = min(Fraction(1), prod / (N - 1))
                model_ratios = {}
                for extra in (0, 8, 32):
                    if model_pm > 0:
                        val = (model_Uneg + 1 + extra) / model_pm
                        model_ratios[str(extra)] = [val.numerator, val.denominator]
                    else:
                        model_ratios[str(extra)] = None
                modelled[cell]["partitions"].append({
                    "curve_A": curve["A"], "curve_B": curve["B"],
                    "partition_blocks": r["partition_blocks"], "slot_dims": d_js,
                    "modelled_Bj": [[b.numerator, b.denominator] for b in model_Bj],
                    "modelled_U_neg": [model_Uneg.numerator, model_Uneg.denominator],
                    "modelled_p_m": [model_pm.numerator, model_pm.denominator],
                    "modelled_cost_ratio": model_ratios,
                    "note": "modelled_|B_j|=q^dj/c is an exact rational (Fraction); reported for "
                            "context/comparison only, per spec 'secondary' status, and NEVER combined "
                            "with a measured value in this same object.",
                })

            if ci == 0:
                if "C2_arm_partitions" in c:
                    for r in c["C2_arm_partitions"]:
                        rec = {"partition_blocks": r["partition_blocks"], "slot_dims": r["slot_dims"],
                               "status": r["status"]}
                        if r["status"] == "ok":
                            rec["cost_ratio_neg"] = r["cost_ratio_neg"]
                        derived[cell]["C2_arm"].append(rec)
                if "C3_arm_by_seed" in c:
                    for seed, parts in c["C3_arm_by_seed"].items():
                        derived[cell]["C3_arm"][seed] = [
                            {"partition_blocks": r["partition_blocks"], "slot_dims": r["slot_dims"],
                             "status": r["status"], "cost_ratio_neg": r.get("cost_ratio_neg")}
                            for r in parts
                        ]
        if "C4" in data and data["C4"].get("status") == "ok":
            for seed, parts in data["C4"]["partitions_by_seed"].items():
                derived[cell]["C4_arm"][seed] = [
                    {"partition_blocks": r["partition_blocks"], "slot_dims": r["slot_dims"],
                     "status": r["status"], "cost_ratio_neg": r.get("cost_ratio_neg")}
                    for r in parts
                ]
        measured[cell]["C4_curve"] = {k: v for k, v in data.get("C4", {}).items()
                                       if k not in ("partitions_by_seed",)}
        measured[cell]["C4_rejected_count"] = len(data.get("C4_rejected", []))

    measured["FROB-EXT-q13n7"] = ext_data
    metrics = {"measured": measured, "modelled": modelled, "derived_from_measured": derived,
               "checker_independent_reverification": checker_report}
    with open(os.path.join(RUN, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    # ------------------------------------------------------- cost-model.json
    cost_measured = {}
    cost_modelled = {}
    cost_derived = {}
    for cell, data in cell_data.items():
        cost_measured[cell] = {
            "curves": [
                {"A": c["curve"]["A"], "B": c["curve"]["B"], "N": c["N"],
                 "cofactor": c["curve"]["cofactor"],
                 "partitions_measured_U_p": [
                     {"slot_dims": r["slot_dims"], "status": r["status"],
                      "U_neg": r.get("U_neg"), "p_m": r.get("p_m")}
                     for r in c["object_arm_partitions"]
                 ]}
                for c in data["curves"]
            ]
        }
        cost_modelled[cell] = modelled[cell]
        # discrepancy: measured cost ratio vs modelled cost ratio at extra=0
        discrepancies = []
        for c in data["curves"]:
            for r in c["object_arm_partitions"]:
                if r["status"] != "ok":
                    continue
                meas_pair = r["cost_ratio_neg"]["0"].get("value") if not r["cost_ratio_neg"]["0"]["denominator_zero"] else None
                meas_val = Fraction(meas_pair[0], meas_pair[1]) if meas_pair else None
                model_entry = [m for m in modelled[cell]["partitions"]
                                if m["curve_A"] == c["curve"]["A"] and m["curve_B"] == c["curve"]["B"]
                                and m["partition_blocks"] == r["partition_blocks"]]
                model_pair = model_entry[0]["modelled_cost_ratio"]["0"] if model_entry else None
                model_val = Fraction(model_pair[0], model_pair[1]) if model_pair else None
                if meas_val is not None and model_val:
                    ratio = meas_val / model_val
                    ratio_out = [ratio.numerator, ratio.denominator]
                else:
                    ratio_out = None
                discrepancies.append({
                    "curve_A": c["curve"]["A"], "curve_B": c["curve"]["B"],
                    "partition_blocks": r["partition_blocks"], "slot_dims": r["slot_dims"],
                    "measured_cost_ratio_neg_extra0": frac_str(r["cost_ratio_neg"]["0"].get("value")),
                    "modelled_cost_ratio_extra0": model_pair,
                    "measured_over_modelled": ratio_out,
                    "formula": "measured_cost_ratio_neg / modelled_cost_ratio, both at extra=0 (exact rational)",
                })
        cost_derived[cell] = {"object_arm_cost_ratio_neg": derived[cell]["object_arm"],
                               "measured_vs_modelled_discrepancy": discrepancies}
    cost_model = {"measured": cost_measured, "modelled": cost_modelled, "derived_from_measured": cost_derived}
    with open(os.path.join(RUN, "cost-model.json"), "w") as f:
        json.dump(cost_model, f, indent=2, default=str)

    # -------------------------------------------------- memory-accounting.json
    mem = {}
    for cell, data in cell_data.items():
        c0 = data["curves"][0]
        N = c0["N"]
        s = len(data["factorisation"]["atomic_factors"])
        # analytic dominant structure per spec: entries = min(prod_j |B_j|, N-1);
        # use the m=1 (coarsest) configuration as the dominant one actually
        # materialised by this driver's construction (which enumerates the
        # WHOLE subgroup once into `by_mask`, not per-partition hit sets).
        entries_by_mask_table = N - 1  # driver's actual dominant structure: the by_mask dict over all N-1 points
        analytic_bytes_by_mask = 8 * entries_by_mask_table * 2  # load_factor 2 (exact int, per spec's 2.0)
        # secondary: subgroup table N entries * 16 bytes (not separately materialised
        # by this driver; it walks point-by-point without storing all N points)
        subgroup_table_bytes = 0  # driver never stores all N points simultaneously
        analytic_bytes_total = analytic_bytes_by_mask + subgroup_table_bytes
        measured_peak = data.get("peak_rss_bytes_self")
        ratio = Fraction(measured_peak, analytic_bytes_total) if analytic_bytes_total else None
        mem[cell] = {
            "N": N, "s_atomic_factors": s,
            "dominant_structure_note": "This driver's dominant resident structure is the by_mask dict "
                                        "(mask -> list of discrete logs) built once over the whole "
                                        "N-1-point subgroup, not a per-partition hit-set as in the "
                                        "reference sizing model; both are recorded.",
            "analytic_bytes_by_mask_table": analytic_bytes_by_mask,
            "analytic_bytes_total": analytic_bytes_total,
            "measured_peak_rss_bytes": measured_peak,
            "ratio_measured_over_analytic": [ratio.numerator, ratio.denominator] if ratio else None,
            "ratio_measured_over_analytic_approx": float(ratio) if ratio else None,
            "ratio_in_declared_band_0.5_to_4": (Fraction(1, 2) <= ratio <= 4) if ratio else None,
            "wall_seconds": data["timing"]["wall_seconds"],
            "cpu_seconds_self": data.get("cpu_seconds_self"),
        }
    mem["FROB-EXT-q13n7"] = {"status": "not_run_resource", "note": "no full enumeration attempted; no peak RSS to reconcile beyond the probe phase"}
    with open(os.path.join(RUN, "memory-accounting.json"), "w") as f:
        json.dump(mem, f, indent=2, default=str)

    # ---------------------------------------------------------- fixtures.json
    spec_path = os.path.join(os.path.dirname(os.path.dirname(RUN)), "specification.yaml")
    fixtures = {
        "specification_sha256": sha256_file(spec_path),
        "specification_path": spec_path,
        "seeds": [2026091401, 2026091402],
        "cell_execution_order": ["FROB-SPLIT-q11n5", "FROB-NOLATTICE-q13n5", "FROB-EQDEG-q19n5", "FROB-EXT-q13n7"],
        "cells": {
            cell: {"q": data["q"], "n": data["n"], "field_modulus": data["field_modulus"]}
            for cell, data in cell_data.items()
        },
        "extra_values_swept": [0, 8, 32],
        "object_selection_rule_ref": "specification.yaml inputs.object_selection",
        "eligibility_rule_ref": "specification.yaml inputs.object_selection (N>=17, exponent 1, N notdiv #E(F_q), ord_N(mu)=n)",
    }
    with open(os.path.join(RUN, "fixtures.json"), "w") as f:
        json.dump(fixtures, f, indent=2, default=str)

    # --------------------------------------------------------- certificates.json
    certs = {
        "certificate": {"kind": "none"},
        "note": "Pure measurement experiment; no discrete log solved, no key recovered. "
                "Relation identities and membership witnesses are re-verified independently "
                "by checker.py and recorded in metrics.json.checker_independent_reverification.",
        "witnesses": {
            cell: {
                "ord_G_equals_N_independently_confirmed": [
                    e for e in checker_report["tuple_sum_reverifications"] if e["cell"] == cell
                ],
                "orbit_divisibility_2n": [
                    e for e in checker_report["orbit_divisibility_checks"] if e["cell"] == cell
                ],
                "field_modulus_independently_reconstructed": [
                    e for e in checker_report["field_and_c5_checks"] if e["cell"] == cell
                ],
            }
            for cell in CELLS
        },
    }
    with open(os.path.join(RUN, "certificates.json"), "w") as f:
        json.dump(certs, f, indent=2, default=str)

    print("wrote metrics.json, cost-model.json, memory-accounting.json, fixtures.json, certificates.json, raw.jsonl")


if __name__ == "__main__":
    main()
