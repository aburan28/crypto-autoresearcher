#!/usr/bin/env python3
"""
Aggregation step for TASK-20260921-819bc0. Reads the two per-(cell,curve)
worker outputs under work/*.out.json and produces the declared artifacts:
metrics.json, cost-model.json, certificates.json, fixtures.json.

Keeps `measured`, `modelled` and `derived_from_measured` as three mutually
exclusive top-level objects in both metrics.json and cost-model.json
(specification.yaml metrics.measured_modelled_separation, IR-6). This task
computes no new MODELLED sizing numbers; `modelled` is an explicit empty
object with a stated reason.

Per the handoff (TASK-20260921-819bc0) and amendment DEC-20260921-2f89d4,
also embeds the OLD (defective, cited from RUN-FROB-91ee9c-51bc02) and NEW
(measured here, corrected construction) C2 [2,2]-partition values side by
side, so the delta is directly readable without cross-referencing a second
run's files. The OLD values below are copied verbatim (not recomputed) from
RUN-FROB-91ee9c-51bc02's work/*.out.json and metrics.json (immutable,
read-only reference; that run is never touched by this task).
"""
import json
import os

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(RUN_DIR, "work")

TARGETS = [
    ("FROB-SPLIT-q11n5", 11, 5, 1, 2, 10061),
    ("FROB-EQDEG-q19n5", 19, 5, 1, 1, 117991),
]

# Cited verbatim from RUN-FROB-91ee9c-51bc02 (immutable, defective-construction
# C2 result for the [2,2] partition), per handoff requirement to report old
# and new side by side. Source: work/<cell>.out.json's C2_arm_partitions entry
# with slot_dims == [2, 2] and status == "ok".
OLD_C2_2_2 = {
    "FROB-SPLIT-q11n5": {
        "source_run": "RUN-FROB-91ee9c-51bc02",
        "source_path": "experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/work/FROB-SPLIT-q11n5.out.json",
        "partition_blocks": [[0, 2], [1, 3]],
        "slot_dims": [2, 2],
        "U_neg": [6, 2],
        "p_m": [18, 10060],
        "block_sizes": [6, 6],
        "cost_ratio_neg_extra0": [20120, 9],
        "spread": [4365, 1936],
        "spread_strictly_smaller_than_object": True,
        "defect_note": ("Both slots used the SAME cached subspace (basis_indices [0,1] "
                         "reused for both), summing a non-pi-stable subspace with ITSELF."),
    },
    "FROB-EQDEG-q19n5": {
        "source_run": "RUN-FROB-91ee9c-51bc02",
        "source_path": "experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/work/FROB-EQDEG-q19n5.out.json",
        "partition_blocks": [[0], [1]],
        "slot_dims": [2, 2],
        "U_neg": [24, 2],
        "p_m": [288, 117990],
        "block_sizes": [24, 24],
        "cost_ratio_neg_extra0": [85215, 16],
        "spread": [24632, 2223],
        "spread_strictly_smaller_than_object": False,
        "defect_note": ("Both slots used the SAME cached subspace (basis_indices [0,1] "
                         "reused for both), summing a non-pi-stable subspace with ITSELF."),
    },
}


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
    """a, b: [num,den] pairs. Returns bool a < b using exact cross-multiplication."""
    an, ad = a
    bn, bd = b
    return an * bd < bn * ad


def find_2_2_ok(parts):
    for r in parts:
        if r.get("slot_dims") == [2, 2] and r.get("status") == "ok":
            return r
    return None


def main():
    measured = {}
    derived = {}
    certificates = {"cells": {}}
    old_vs_new = {}

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
            "timing": data["timing"],
            "peak_rss_bytes_self": data["peak_rss_bytes_self"],
            "cpu_seconds_self": data["cpu_seconds_self"],
        }

        obj_spread = data["object_arm_summary"]["spread"]
        c2_spread = data["C2_spread_summary"]["spread"]

        new_2_2 = find_2_2_ok(data["C2_arm_partitions"])
        old_2_2 = OLD_C2_2_2[cell]
        old_vs_new[cell] = {
            "partition_slot_dims": [2, 2],
            "old_defective": {
                "source_run": old_2_2["source_run"],
                "source_path": old_2_2["source_path"],
                "partition_blocks": old_2_2["partition_blocks"],
                "U_neg": old_2_2["U_neg"],
                "p_m": old_2_2["p_m"],
                "block_sizes": old_2_2["block_sizes"],
                "cost_ratio_neg_extra0": old_2_2["cost_ratio_neg_extra0"],
                "spread": old_2_2["spread"],
                "spread_strictly_smaller_than_object": old_2_2["spread_strictly_smaller_than_object"],
                "defect_note": old_2_2["defect_note"],
            },
            "new_corrected": {
                "source_run": "RUN-FROB-91ee9c-819bc0",
                "partition_blocks": new_2_2["partition_blocks"],
                "U_neg": new_2_2["U_neg"],
                "p_m": new_2_2["p_m"],
                "block_sizes": new_2_2["block_sizes"],
                "cost_ratio_neg_extra0": new_2_2["cost_ratio_neg"]["0"]["value"],
                "spread": c2_spread,
                "spread_strictly_smaller_than_object": lt(c2_spread, obj_spread),
                "basis_indices_used": [
                    data["C2_raw"]["2"]["pool"][0]["basis_indices"],
                    data["C2_raw"]["2"]["pool"][1]["basis_indices"],
                ],
                "two_slots_use_distinct_subspaces": (
                    data["C2_raw"]["2"]["pool"][0]["basis_indices"] !=
                    data["C2_raw"]["2"]["pool"][1]["basis_indices"]
                ),
                "fix_note": ("The two slots of dimension 2 now draw the FIRST and SECOND "
                              "entries of the per-dimension pool (distinct index tuples), "
                              "per DEC-20260921-2f89d4."),
            },
            "object_arm_spread": obj_spread,
            "strictly_smaller_verdict_changed": (
                old_2_2["spread_strictly_smaller_than_object"] != lt(c2_spread, obj_spread)
            ),
        }

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
            "C2_old_vs_new_2_2_partition": old_vs_new[cell],
            "verdicts": {
                "object_arm_spread": obj_spread,
                "C2_spread": c2_spread,
                "C2_spread_strictly_smaller_than_object": lt(c2_spread, obj_spread),
            },
        }

        certificates["cells"][cell] = {
            "target_curve": data["target_curve"],
            "curve_recomputed": data["curve_recomputed"],
            "object_arm_consistency_check": data["object_arm_consistency_check"],
            "certificate_kind": "none",
            "certificate_note": ("Pure combinatorial measurement; no discrete log solved, no key "
                                  "recovered. The witnesses re-verified independently by checker.py "
                                  "are: field modulus reproduction, curve order/eligibility "
                                  "(N || #E(F_q^n), exponent 1), generator order = N, non-pi-stable "
                                  "witnesses for each C2 pool entry, pairwise distinctness of the "
                                  "C2 pool's basis_indices per dimension, and every reported "
                                  "rational cost-ratio identity."),
        }

    modelled = {}
    modelled_note = (
        "No new MODELLED sizing numbers are computed in this run. This task's scope "
        "(per DEC-20260921-2f89d4) is the object-arm consistency check and a corrected "
        "recomputation of control C2 only; C3 and C4 are explicitly out of scope."
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
                             "C2_arm_partitions": measured[cell]["C2_arm_partitions"]}
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
        "amendment_ids": ["DEC-20260921-e81e25", "DEC-20260921-2f89d4"],
        "amendment_paths": [
            "experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-e81e25.yaml",
            "experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-2f89d4.yaml",
        ],
        "prior_run_id": "RUN-FROB-91ee9c-51bc02",
        "prior_run_path": "experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/",
        "correction_id": "CORR-20260921-9dc350",
        "correction_path": "ledger/corrections/CORR-20260921-9dc350.yaml",
        "seeds": [2026091401, 2026091402],
        "seeds_note": ("Accepted for invocation-signature parity with the reference "
                        "implementation but not consumed by any construction in this "
                        "scoped run: C2 is fully deterministic and C3/C4 are out of scope."),
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
            "C3_random_matched_cardinality (unchanged construction, not re-run)",
            "C4_matched_null_curve (unchanged construction, not re-run)",
            "FROB-NOLATTICE-q13n5 second curve",
            "FROB-EXT-q13n7 (not_run_resource, unchanged per SR-4)",
        ],
    }
    with open(os.path.join(RUN_DIR, "fixtures.json"), "w") as f:
        json.dump(fixtures, f, indent=2, default=str)

    print("Aggregation complete.")
    for cell, *_ in TARGETS:
        v = derived[cell]["verdicts"]
        ov = old_vs_new[cell]
        print(cell, "object_spread", v["object_arm_spread"],
              "old_C2_spread", ov["old_defective"]["spread"],
              "old_C2<obj", ov["old_defective"]["spread_strictly_smaller_than_object"],
              "new_C2_spread", v["C2_spread"],
              "new_C2<obj", v["C2_spread_strictly_smaller_than_object"],
              "verdict_changed", ov["strictly_smaller_verdict_changed"])


if __name__ == "__main__":
    main()
