#!/usr/bin/env python3
"""
Aggregation step for TASK-20260921-51bc02. Reads the two per-(cell,curve)
worker outputs under work/*.out.json and produces the declared artifacts:
metrics.json, cost-model.json, certificates.json, fixtures.json.

Keeps `measured`, `modelled` and `derived_from_measured` as three mutually
exclusive top-level objects in both metrics.json and cost-model.json
(specification.yaml metrics.measured_modelled_separation, IR-6). This task
computes no new MODELLED sizing numbers (the frozen q^{d_j}/c model was
already exercised for these two cells in RUN-FROB-91ee9c-7119f2's
cost-model.json against curve index 0 and the cell-level modelled inputs
(field, factor degrees, cofactor c) are curve-independent within a cell);
`modelled` is therefore an explicit empty object with a stated reason rather
than an omitted key.
"""
import json
import os

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(RUN_DIR, "work")

TARGETS = [
    ("FROB-SPLIT-q11n5", 11, 5, 1, 2, 10061),
    ("FROB-EQDEG-q19n5", 19, 5, 1, 1, 117991),
]

SEEDS = [2026091401, 2026091402]


def load(cell):
    with open(os.path.join(WORK, f"{cell}.out.json")) as f:
        lines = f.read().splitlines()
    return json.loads(lines[1])


def strip_cost_ratio(rec):
    r = {k: v for k, v in rec.items() if k != "cost_ratio_neg"}
    return r


def strip_list(lst):
    return [strip_cost_ratio(r) for r in lst]


def derived_list(lst):
    out = []
    for r in lst:
        d = {"partition_blocks": r["partition_blocks"], "slot_dims": r["slot_dims"],
             "status": r["status"]}
        if r["status"] == "ok":
            d["cost_ratio_neg"] = r["cost_ratio_neg"]
            d["formula"] = "(U_neg + 1 + extra) / p_m"
        out.append(d)
    return out


def lt(a, b):
    """a, b: [num,den] pairs. Returns bool a < b using exact cross-multiplication."""
    an, ad = a
    bn, bd = b
    return an * bd < bn * ad


def main():
    measured = {}
    derived = {}
    certificates = {"cells": {}}

    for cell, q, n, A, B, N in TARGETS:
        data = load(cell)
        assert data["cell_status"] == "ok", f"{cell}: cell_status={data['cell_status']} reason={data.get('cell_status_reason')}"

        measured[cell] = {
            "target_curve": data["target_curve"],
            "field_modulus": data["field_modulus"],
            "factorisation": data["factorisation"],
            "achievable_multiset_table": data["achievable_multiset_table"],
            "divisor_lattice_dims": data["divisor_lattice_dims"],
            "curve_recomputed": data["curve_recomputed"],
            "object_arm_partitions": strip_list(data["object_arm_partitions"]),
            "C2_raw": data["C2_raw"],
            "C2_arm_partitions": strip_list(data["C2_arm_partitions"]),
            "C3_arm_by_seed": {s: strip_list(p) for s, p in data["C3_arm_by_seed"].items()},
            "C4_meta": {k: v for k, v in data["C4"].items()
                        if k not in ("partitions_by_seed", "spread_by_seed")},
            "C4_rejected_count": len(data["C4_rejected"]),
            "C4_partitions_by_seed": {s: strip_list(p) for s, p in data["C4"]["partitions_by_seed"].items()},
            "timing": data["timing"],
            "peak_rss_bytes_self": data["peak_rss_bytes_self"],
            "cpu_seconds_self": data["cpu_seconds_self"],
        }

        obj_spread = data["object_arm_summary"]["spread"]
        c2_spread = data["C2_spread_summary"]["spread"]
        c3_spreads = {s: v["spread"] for s, v in data["C3_spread_by_seed"].items()}
        c4_spreads = {s: v["spread"] for s, v in data["C4"]["spread_by_seed"].items()}

        derived[cell] = {
            "object_arm": {
                "partitions": derived_list(data["object_arm_partitions"]),
                "summary": data["object_arm_summary"],
            },
            "object_arm_consistency_check": data["object_arm_consistency_check"],
            "C2_arm": {
                "partitions": derived_list(data["C2_arm_partitions"]),
                "spread_summary": data["C2_spread_summary"],
            },
            "C3_arm_by_seed": {
                s: {"partitions": derived_list(p), "spread_summary": data["C3_spread_by_seed"][s]}
                for s, p in data["C3_arm_by_seed"].items()
            },
            "C4_arm_by_seed": {
                s: {"partitions": derived_list(p), "spread_summary": data["C4"]["spread_by_seed"][s]}
                for s, p in data["C4"]["partitions_by_seed"].items()
            },
            "verdicts": {
                "object_arm_spread": obj_spread,
                "C2_spread": c2_spread,
                "C2_spread_strictly_smaller_than_object": lt(c2_spread, obj_spread),
                "C3_spread_by_seed": c3_spreads,
                "C3_spread_strictly_smaller_than_object_by_seed":
                    {s: lt(v, obj_spread) for s, v in c3_spreads.items()},
                "C4_spread_by_seed": c4_spreads,
                "C4_spread_strictly_smaller_than_object_by_seed":
                    {s: lt(v, obj_spread) for s, v in c4_spreads.items()},
            },
        }

        certificates["cells"][cell] = {
            "target_curve": data["target_curve"],
            "curve_recomputed": data["curve_recomputed"],
            "object_arm_consistency_check": data["object_arm_consistency_check"],
            "C4_null_curve": {k: v for k, v in data["C4"].items()
                               if k not in ("partitions_by_seed", "spread_by_seed")},
            "certificate_kind": "none",
            "certificate_note": ("Pure combinatorial measurement; no discrete log solved, no key "
                                  "recovered. The witnesses re-verified independently by checker.py "
                                  "are: field modulus reproduction, curve order/eligibility "
                                  "(N || #E(F_q^n), exponent 1), generator order = N, non-pi-stable "
                                  "witness for C2, and every reported rational cost-ratio identity."),
        }

    modelled = {}
    modelled_note = (
        "No new MODELLED sizing numbers are computed in this run. The frozen "
        "modelled_|B_j| = q^{d_j}/c sizing (specification.yaml preregistered_prediction "
        "and metrics.secondary) is a per-CELL model keyed only on q, the atomic factor "
        "degrees d_j, and the cofactor c = #E(F_q^n)/N; c is curve-dependent, and this "
        "task's curve-recomputed cofactors are recorded above under measured."
        "curve_recomputed.cofactor for anyone who wants to evaluate that formula, but no "
        "modelled_cost_ratio table is built here because the amendment's scope is the "
        "already-defined C2/C3/C4 control battery and the object-arm consistency check "
        "only, not a new modelled-vs-measured discrepancy table."
    )

    metrics = {
        "measured": measured,
        "modelled": modelled,
        "modelled_note": modelled_note,
        "derived_from_measured": derived,
    }
    cost_model = {
        "measured": {cell: {"target_curve": measured[cell]["target_curve"],
                             "curve_recomputed": measured[cell]["curve_recomputed"],
                             "object_arm_partitions": measured[cell]["object_arm_partitions"],
                             "C2_arm_partitions": measured[cell]["C2_arm_partitions"],
                             "C3_arm_by_seed": measured[cell]["C3_arm_by_seed"],
                             "C4_partitions_by_seed": measured[cell]["C4_partitions_by_seed"]}
                     for cell in measured},
        "modelled": modelled,
        "modelled_note": modelled_note,
        "derived_from_measured": {cell: derived[cell] for cell in derived},
    }

    with open(os.path.join(RUN_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    with open(os.path.join(RUN_DIR, "cost-model.json"), "w") as f:
        json.dump(cost_model, f, indent=2, default=str)
    with open(os.path.join(RUN_DIR, "certificates.json"), "w") as f:
        json.dump(certificates, f, indent=2, default=str)

    fixtures = {
        "specification_sha256": "9d66c4f7914250a09a5083a3e97c85af9f26ba04755b906105c200d41c75daa4",
        "specification_path": "experiments/EXP-FROB-91ee9c/specification.yaml",
        "amendment_id": "DEC-20260921-e81e25",
        "amendment_path": "experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-e81e25.yaml",
        "prior_run_id": "RUN-FROB-91ee9c-7119f2",
        "prior_run_path": "experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/",
        "seeds": SEEDS,
        "targets": [
            {"cell": cell, "q": q, "n": n, "A": A, "B": B, "N": N}
            for cell, q, n, A, B, N in TARGETS
        ],
        "field_construction_reused_from_prior_run": {
            "FROB-SPLIT-q11n5": "x^5 + 2*x^4 + 1",
            "FROB-EQDEG-q19n5": "x^5 + 3*x^4 + 1",
        },
        "field_construction_independently_reproduced_this_run": {
            cell: measured[cell]["field_modulus"] for cell, *_ in TARGETS
        },
        "out_of_scope": [
            "FROB-NOLATTICE-q13n5 second curve (field-level {0,4} lattice fact, per amendment)",
            "FROB-EXT-q13n7 (not_run_resource, unchanged per SR-4)",
        ],
    }
    with open(os.path.join(RUN_DIR, "fixtures.json"), "w") as f:
        json.dump(fixtures, f, indent=2, default=str)

    print("Aggregation complete.")
    for cell, *_ in TARGETS:
        v = derived[cell]["verdicts"]
        print(cell, "object_spread", v["object_arm_spread"],
              "C2<obj", v["C2_spread_strictly_smaller_than_object"],
              "C3<obj", v["C3_spread_strictly_smaller_than_object_by_seed"],
              "C4<obj", v["C4_spread_strictly_smaller_than_object_by_seed"])


if __name__ == "__main__":
    main()
