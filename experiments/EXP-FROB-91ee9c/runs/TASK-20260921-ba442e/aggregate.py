#!/usr/bin/env python3
"""
Aggregation step for TASK-20260921-ba442e. Reads the single-cell worker
output under work/FROB-EXT-q13n7.out.json and produces the declared
artifacts: metrics.json, cost-model.json, certificates.json, fixtures.json.

Keeps `measured`, `modelled` and `derived_from_measured` as three mutually
exclusive top-level objects (specification.yaml metrics.measured_modelled_
separation, IR-6). This task computes no new MODELLED sizing numbers;
`modelled` is an explicit empty object with a stated reason (same convention
as TASK-20260921-819bc0's aggregate.py).
"""
import json
import os

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(RUN_DIR, "work")

CELL = "FROB-EXT-q13n7"
Q, N_EXT, A, B, N = 13, 7, 0, 1, 5230261


def load(cell):
    with open(os.path.join(WORK, f"{cell}.out.json")) as f:
        lines = f.read().splitlines()
    return json.loads(lines[1])


def strip_cost_ratio(rec):
    return {k: v for k, v in rec.items() if k != "cost_ratio_neg"}


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
    an, ad = a
    bn, bd = b
    return an * bd < bn * ad


def main():
    data = load(CELL)
    with open(os.path.join(WORK, "checker-report.json")) as f:
        checker = json.load(f)

    if data.get("cell_status") != "ok":
        # not_run_resource / instrument_invalidation path -- still produce
        # the declared artifacts, honestly reflecting the terminal status.
        measured = {CELL: {k: v for k, v in data.items()
                            if k not in ("object_arm_partitions", "C2_arm_partitions",
                                         "C3_arm_by_seed", "C4")}}
        metrics = {"measured": measured, "modelled": {},
                   "modelled_note": "Cell did not reach cell_status=ok; see status/reason.",
                   "derived_from_measured": {}}
        cost_model = {"measured": measured, "modelled": {}, "derived_from_measured": {}}
        certificates = {"cells": {CELL: {"certificate_kind": "none",
                                          "cell_status": data.get("cell_status"),
                                          "cell_status_reason": data.get("cell_status_reason")}}}
        for name, obj in (("metrics.json", metrics), ("cost-model.json", cost_model),
                           ("certificates.json", certificates)):
            with open(os.path.join(RUN_DIR, name), "w") as f:
                json.dump(obj, f, indent=2, default=str)
        fixtures = {"cell": CELL, "cell_status": data.get("cell_status"),
                    "cell_status_reason": data.get("cell_status_reason")}
        with open(os.path.join(RUN_DIR, "fixtures.json"), "w") as f:
            json.dump(fixtures, f, indent=2, default=str)
        print("Aggregation complete (non-ok terminal status).", data.get("cell_status"))
        return

    measured = {
        CELL: {
            "target_curve": data["target_curve"] if "target_curve" in data else
                             {"A": data["curve_recomputed"]["A"], "B": data["curve_recomputed"]["B"],
                              "N": data["curve_recomputed"]["N"]},
            "expected_target_curve": data["expected_target_curve"],
            "curve_search_matches_prior_probe": data["curve_search_matches_prior_probe"],
            "mu_scalar_condition": data["mu_scalar_condition"],
            "field_modulus": data["field_modulus"],
            "factorisation": data["factorisation"],
            "achievable_multiset_table": data["achievable_multiset_table"],
            "divisor_lattice_dims": data["divisor_lattice_dims"],
            "curve_recomputed": data["curve_recomputed"],
            "generator_point": data["generator_point"],
            "object_arm_partitions": strip_list(data["object_arm_partitions"]),
            "C1": data["C1"],
            "C2_raw": data["C2_raw"],
            "C2_max_multiplicity_by_dim": data["C2_max_multiplicity_by_dim"],
            "C2_dim2_pool_combos": data["C2_dim2_pool_combos"],
            "C2_dim2_pool_pairwise_distinct": data["C2_dim2_pool_pairwise_distinct"],
            "C2_arm_partitions": strip_list(data["C2_arm_partitions"]),
            "C2_222_three_subspaces_distinct": data["C2_222_three_subspaces_distinct"],
            "C3_arm_by_seed": {s: strip_list(p) for s, p in data["C3_arm_by_seed"].items()},
            "C4": {**{k: v for k, v in data["C4"].items() if k not in ("partitions_by_seed",)},
                   "partitions_by_seed": ({s: strip_list(p) for s, p in data["C4"]["partitions_by_seed"].items()}
                                          if data["C4"].get("status") == "ok" else None)},
            "C5": data["C5"],
            "C6": data["C6"],
            "C7": data["C7"],
            "timing": data["timing"],
            "peak_rss_bytes_self": data["peak_rss_bytes_self"],
            "cpu_seconds_self": data["cpu_seconds_self"],
        }
    }

    obj_spread = data["object_arm_summary"]["spread"]
    c2_spread = data["C2_spread_summary"]["spread"]
    c3_spreads = {s: data["C3_spread_by_seed"][s]["spread"] for s in data["C3_spread_by_seed"]}
    c4_spreads = ({s: v["spread"] for s, v in data["C4"]["spread_by_seed"].items()}
                  if data["C4"].get("status") == "ok" else {})

    verdicts = {
        "object_arm_spread": obj_spread,
        "C2_spread": c2_spread,
        "C2_spread_strictly_smaller_than_object": lt(c2_spread, obj_spread) if c2_spread else None,
        "C3_spreads_by_seed": c3_spreads,
        "C3_strictly_smaller_by_seed": {s: (lt(v, obj_spread) if v else None) for s, v in c3_spreads.items()},
        "C4_spreads_by_seed": c4_spreads,
        "C4_strictly_smaller_by_seed": {s: (lt(v, obj_spread) if v else None) for s, v in c4_spreads.items()},
    }

    derived = {
        CELL: {
            "object_arm": {
                "partitions": derived_list(data["object_arm_partitions"]),
                "summary": data["object_arm_summary"],
            },
            "C2_arm": {
                "partitions": derived_list(data["C2_arm_partitions"]),
                "spread_summary": data["C2_spread_summary"],
            },
            "C3_arm_by_seed": {s: {"partitions": derived_list(p), "spread_summary": data["C3_spread_by_seed"][s]}
                                for s, p in data["C3_arm_by_seed"].items()},
            "C4": ({"partitions_by_seed": {s: derived_list(p) for s, p in data["C4"]["partitions_by_seed"].items()},
                    "spread_by_seed": data["C4"]["spread_by_seed"]}
                   if data["C4"].get("status") == "ok" else {"status": data["C4"].get("status")}),
            "verdicts": verdicts,
        }
    }

    modelled = {}
    modelled_note = (
        "No new MODELLED sizing numbers are computed in this run. This task's scope "
        "(per DEC-20260921-f93b43) is full completion of the MEASURED object arm and "
        "control battery for FROB-EXT-q13n7's curve index 0 only."
    )

    metrics = {
        "measured": measured,
        "modelled": modelled,
        "modelled_note": modelled_note,
        "derived_from_measured": derived,
    }
    cost_model = {
        "measured": {CELL: {"target_curve": measured[CELL]["curve_recomputed"],
                             "object_arm_partitions": measured[CELL]["object_arm_partitions"],
                             "C2_arm_partitions": measured[CELL]["C2_arm_partitions"],
                             "C3_arm_by_seed": measured[CELL]["C3_arm_by_seed"],
                             "C4": measured[CELL]["C4"]}},
        "modelled": modelled,
        "modelled_note": modelled_note,
        "derived_from_measured": derived,
    }
    certificates = {
        "cells": {
            CELL: {
                "target_curve": data["curve_recomputed"],
                "curve_search_matches_prior_probe": data["curve_search_matches_prior_probe"],
                "mu_scalar_condition": data["mu_scalar_condition"],
                "certificate_kind": "none",
                "certificate_note": (
                    "Pure combinatorial measurement; no discrete log solved, no key "
                    "recovered. The witnesses re-verified independently by checker.py "
                    "(no Sage, no import of implementation.py) are: field modulus "
                    "reproduction; N primality and N || recomputed-order exponent 1; "
                    "N*G == O and pi(G) == mu*G via independent double-and-add scalar "
                    "arithmetic (ord(G)=N, ord_N(mu)=n); every reported rational "
                    "cost-ratio identity across object/C2/C3/C4 arms; the C2 pool's "
                    "pairwise basis_indices distinctness per dimension, including the "
                    "[2,2,2] partition's three-way distinctness; and C1/C6/C7's raw "
                    "closed-form/refusal/denominator-zero facts."
                ),
                "checker_all_independent_checks_pass": checker.get("all_independent_checks_pass"),
            }
        }
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
        "amendment_ids": ["DEC-20260921-e81e25", "DEC-20260921-2f89d4", "DEC-20260921-f93b43"],
        "amendment_paths": [
            "experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-e81e25.yaml",
            "experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-2f89d4.yaml",
            "experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-f93b43.yaml",
        ],
        "prior_probe_run_id": "RUN-FROB-91ee9c-7119f2",
        "prior_probe_path": "experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work/FROB-EXT-q13n7.probe.json",
        "correction_id": "CORR-20260921-9dc350",
        "correction_path": "ledger/corrections/CORR-20260921-9dc350.yaml",
        "seeds": [2026091401, 2026091402],
        "target": {"cell": CELL, "q": Q, "n": N_EXT, "A": A, "B": B, "N": N},
        "field_construction_independently_reproduced_this_run": data["field_modulus"],
        "achievable_multiset_table": data["achievable_multiset_table"],
        "curve_index_1_out_of_scope": True,
        "out_of_scope": [
            "FROB-EXT-q13n7 curve index 1 (explicitly out of scope per DEC-20260921-f93b43)",
        ],
    }
    with open(os.path.join(RUN_DIR, "fixtures.json"), "w") as f:
        json.dump(fixtures, f, indent=2, default=str)

    print("Aggregation complete.")
    v = derived[CELL]["verdicts"]
    print(CELL, "object_spread", v["object_arm_spread"],
          "C2_spread", v["C2_spread"], "C2<obj", v["C2_spread_strictly_smaller_than_object"],
          "C3<obj", v["C3_strictly_smaller_by_seed"], "C4<obj", v["C4_strictly_smaller_by_seed"])


if __name__ == "__main__":
    main()
