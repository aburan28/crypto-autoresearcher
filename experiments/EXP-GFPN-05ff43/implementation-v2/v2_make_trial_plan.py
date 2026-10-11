#!/usr/bin/env python3
"""Writes experiments/EXP-GFPN-05ff43/trial-plan-v2.json (amendment DC-6 R-2; card EC-2).

usage: python3 -B v2_make_trial_plan.py <file with one minted RUN-GFPN-* id per line> [--out PATH]

The ids are minted beforehand with `python3 tools/allocate_id.py --next run --area GFPN` and each is
confirmed free with `--check`; they are consumed IN FILE ORDER, one per package. This script only lays
out the plan: packages in execution order, every (arm, curve_shape, p', m, target_kind) cell with its
disposition, watchdogs declared uniformly per (arm, m) (AC-6), the gate, and the ceiling (<= 48).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, ".."))

PRIMES = [4111, 262151, 16777291]
SHAPES = ["ecgfp5_shaped", "random_2torsion", "random_no2torsion"]
A6_REASON = ("predicted D_raw ~ 2^26.9 (P-2), 2^6.9 above the S_5 shape that exhausted 11 GiB at the degree-33 round "
             "(RUN-GFPN-8f1b50); 17^5-node grid interpolation")

WATCHDOGS = {
    "rule": ("AC-6: any per-target wall-clock watchdog is declared here before phase A, UNIFORMLY per (arm, m): every package, "
             "fixture, control and cell that solves arm A at m uses the same values. Expiry is not_measured (timeout), never "
             "evidence that D is large. The per-cell watchdog applies ONLY while a cell has no measured target, so it never "
             "reduces the sample of a measured cell (A-7: any cell with a measured target continues to 20 targets)."),
    "per_arm_m": {},
    "builder_timeout_s": {"m3": 1800, "m4": 7200, "m5": 86400},
    "callgrind_timeout_s": {"m3": 1800, "m4": 14400},
    "comparator_timeout_s": 3600,
}
for arm in ("raw_x", "raw_u", "S3", "S3_rescaled", "torsion_S3_norm", "torsion_S3_rq", "identity"):
    WATCHDOGS["per_arm_m"]["%s|m3" % arm] = {"per_target_timeout_s": 1800, "per_cell_no_measurement_watchdog_s": None}
for arm in ("raw", "S4", "S4_rescaled", "torsion_S4_rq", "torsion_S4_norm"):
    WATCHDOGS["per_arm_m"]["%s|m4" % arm] = {"per_target_timeout_s": 7200, "per_cell_no_measurement_watchdog_s": 86400}
for arm in ("S5", "S5_rescaled", "torsion_S5_rq", "torsion_S5_norm"):
    WATCHDOGS["per_arm_m"]["%s|m5" % arm] = {"per_target_timeout_s": 43200, "per_cell_no_measurement_watchdog_s": 172800}
WATCHDOGS["per_arm_m"]["raw|m5"] = {"per_target_timeout_s": None, "per_cell_no_measurement_watchdog_s": None,
                                    "note": "raw at m = 5 is not_attempted by design (DC-7 A-6); no watchdog is needed"}


def cells_m5(shape, p):
    rq_note = None
    if shape == "random_no2torsion":
        rq_note = "expected recorded refusal: no rational 2-torsion (R-6, R-9)"
    elif shape == "ecgfp5_shaped" and p == 16777291:
        rq_note = ("expected recorded refusal: b-square class mismatch -- ladder.json records b_is_square_in_Fq true for this "
                   "curve (y^2 = x(x^2 + 2x + 59z), cofactor 4); flagged in implementation-v2.md for the Coordinator")
    out = [
        {"arm": "torsion_S5_rq", "disposition": "run", "expected_refusal": rq_note},
        {"arm": "S5", "disposition": "run"},
        {"arm": "S5_rescaled", "disposition": "run", "expected_refusal": rq_note,
         "note": "run unconditionally on the 2-torsion shapes so the matched control is discharged at every prime (R-9)"},
        {"arm": "torsion_S5_norm", "disposition": "run", "condition": "measured_in_this_package:S5",
         "expected_refusal": "expected recorded refusal: no rational 2-torsion" if shape == "random_no2torsion" else None,
         "note": "labelled negative control; run only where arm (ii) on the same targets completes (DC-3 nearby_object_control (3)); group order 3840"},
        {"arm": "raw", "disposition": "not_attempted", "reason": A6_REASON},
    ]
    return out


def cells_m4(shape):
    no2 = shape == "random_no2torsion"
    ref = "expected recorded refusal: no rational 2-torsion" if no2 else None
    return [
        {"arm": "raw", "disposition": "run", "note": "raw at m <= 4 at every ladder prime (R-9); overdetermined at n = 5, so D is undefined on a non-decomposable target"},
        {"arm": "torsion_S4_rq", "disposition": "run", "condition": "m5_not_measured:torsion_S5_rq", "expected_refusal": ref,
         "note": "stopping rule 3 fallback: decomposition-test cost only (DC-3 m4_fallback)"},
        {"arm": "S4", "disposition": "run", "condition": "m5_not_measured:S5"},
        {"arm": "S4_rescaled", "disposition": "run", "condition": "m5_not_measured:S5_rescaled", "expected_refusal": ref},
        {"arm": "torsion_S4_norm", "disposition": "run", "condition": "m5_not_measured:torsion_S5_norm", "expected_refusal": ref},
    ]


def builds(p):
    out = []
    for m in (5, 4):
        for shape in SHAPES:
            for arm in ("S%d" % m, "S%d_rescaled" % m, "torsion_S%d_rq" % m, "torsion_S%d_norm" % m):
                out.append({"shape": shape, "arm": arm, "m": m})
    return out


def main():
    ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(EXP, "trial-plan-v2.json")
    for i in ids:
        assert re.fullmatch(r"RUN-GFPN-[0-9a-f]{6}", i), i
    assert len(set(ids)) == len(ids)
    v1_text = open(os.path.join(EXP, "trial-plan.json")).read()
    v1_ids = sorted(set(re.findall(r"RUN-GFPN-[0-9a-f]{6}", v1_text)) | {d for d in os.listdir(os.path.join(EXP, "runs")) if d.startswith("RUN-")} | {"RUN-GFPN-bb78e5"})
    assert not set(ids) & set(v1_ids), "a v1 id would be reused"
    it = iter(ids)
    pk = []

    def add(**kw):
        kw["order"] = len(pk) + 1
        kw["run_id"] = next(it)
        kw["requires"] = [pk[-1]["run_id"]] if pk and kw["kind"] != "contingency" else []
        pk.append(kw)
        return kw

    add(label="F-1..F-3 fixture, n = m = 3, p' = 4111", kind="fixture", blocking=True, gate_required=False, p=4111,
        driver_args=["fixture", "--p", "4111"], watchdogs="per_arm_m keys *|m3",
        content="curves, beta and 2 regression x_R of square_analogue_n3.json (data only) + 2 fresh seeded known-scalar targets (+ recorded replacements) + >= 2 planted square targets for F-2(b); arms raw_x, raw_u, S3, S3_rescaled, torsion_S3_norm, torsion_S3_rq")
    add(label="F-1..F-3 fixture, n = m = 3, p' = 16777291", kind="fixture", blocking=True, gate_required=False, p=16777291,
        driver_args=["fixture", "--p", "16777291"], watchdogs="per_arm_m keys *|m3", content="as package 1")
    add(label="jv_anchor_system_trace_identity, p' = 16777291, n = 5, m = 4 (rulings.DC-5)", kind="anchor", blocking=True, gate_required=False,
        p=16777291, driver_args=["anchor-identity"], watchdogs="S4|m4 (uniform with every S4 cell) and comparator_timeout_s",
        content="k4a_anchor_system.py RUN as the independent comparator (Sage python, capped child, not copied); our S4 system on its random x_R and on 3 v2 seeded targets; msolve 0.6.5 -g 1 -t 1 traces vs archived RUN-GFPN-61bba9 logs; wall-clock ratio vs 17.01 s reported NON-BLOCKING")
    add(label="frozen controls: degenerate_symmetrization_identity, orbit_lifting_verifier, known_scalar_instances", kind="controls",
        blocking=True, gate_required=False, driver_args=["controls"], watchdogs="per_arm_m keys *|m3 and builder_timeout_s",
        content="identity == raw (coefficients, D, solutions) at n = m = 3 and coefficient identity at n = 5, m = 3, 4; planted m < n instrument checks of the lifting path for S3, S3_rescaled, torsion_S3_rq, torsion_S3_norm (never degree evidence); verifier negative tests including missing beta/lam/relation_mod_T and a torsion certificate on a curve without 2-torsion; rq refusal on random_no2torsion; independent known-scalar recheck at every ladder prime and shape")
    gate_ids = [p["run_id"] for p in pk]
    add(label="F-4 secondary fixture, n = m = 4, GF(4111^4), b a square (NOT blocking)", kind="fixture4", blocking=False, gate_required=True,
        p=4111, driver_args=["fixture4"], watchdogs="per_arm_m keys *|m4",
        content="S4, S4_rescaled, torsion_S4_norm, torsion_S4_rq on 2 fresh seeded targets; red-team values reported next to measured D; beta = 1 from the data file (different construction path)")
    m5_ids = {}
    for p in PRIMES:
        add(label="build p' = %d (m = 5 and m = 4; all shapes; refusal rows)" % p, kind="build", blocking=False, gate_required=True, p=p,
            driver_args=["build", "--p", str(p)], builds=builds(p), watchdogs="builder_timeout_s m5 / m4")
        for shape in SHAPES:
            k = add(label="cells p' = %d, %s, m = 5" % (p, shape), kind="cells", blocking=False, gate_required=True, p=p, shape=shape, m=5,
                    targets_per_cell=20, target_kind="random", driver_args=["cells", "--p", str(p), "--shape", shape, "--m", "5"],
                    cells=cells_m5(shape, p), watchdogs="per_arm_m keys *|m5")
            m5_ids[(p, shape)] = k["run_id"]
        for shape in SHAPES:
            add(label="cells p' = %d, %s, m = 4" % (p, shape), kind="cells", blocking=False, gate_required=True, p=p, shape=shape, m=4,
                targets_per_cell=20, target_kind="random",
                driver_args=["cells", "--p", str(p), "--shape", shape, "--m", "4", "--prior-run", m5_ids[(p, shape)]],
                cells=cells_m4(shape), watchdogs="per_arm_m keys *|m4")
    cell_ids = [p["run_id"] for p in pk if p["kind"] == "cells"]
    add(label="aggregate: ladder table, like-for-like scoring, HEUR-GFPN-DFLAT, F4, band (B-3)", kind="aggregate", blocking=False,
        gate_required=True, driver_args=["aggregate", "--runs", ",".join(cell_ids)])
    for j in range(4):
        add(label="contingency %d" % (j + 1), kind="contingency", blocking=False, gate_required=True,
            content="used only under contingency_rule; unused ids stay unused and are reported as such")
    leftover = list(it)
    assert not leftover, "unused minted ids: %s" % leftover
    enum = []
    for p_ in pk:
        if p_["kind"] == "cells":
            for c in p_["cells"]:
                enum.append({"run_id": p_["run_id"], "order": p_["order"], "arm": c["arm"], "curve_shape": p_["shape"], "p": p_["p"], "m": p_["m"],
                             "n": 5, "target_kind": "random", "disposition": c["disposition"], "condition": c.get("condition"),
                             "expected_refusal": c.get("expected_refusal"), "reason": c.get("reason")})
    plan = {
        "schema": "crypto.autoresearch.trial_plan.v2",
        "experiment_id": "EXP-GFPN-05ff43", "protocol_version": 2, "task_id": "TASK-20260923-cd932c",
        "amendment": {"id": "AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii",
                      "path": "experiments/EXP-GFPN-05ff43/amendments/v1_to_v2_reanchor_and_arm_iii.yaml",
                      "sha256": "e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3"},
        "approval_decision": "DEC-20260923-e788a1", "written_at": "2026-09-23", "written_in": "stage 1 (implement, do not run); no v2 run package exists",
        "archived_by": "TASK-20260923-0fa03f phase A (Coordinator)",
        "package_ceiling": 48, "package_count": len(pk),
        "package_count_note": "31 packages: 27 planned + 4 contingency ids; counted separately from v1's 48 (DC-7 A-7)",
        "id_minting": "each id minted with `python3 tools/allocate_id.py --next run --area GFPN` and confirmed free with `--check` before this file was written",
        "v1_ids_never_reused": v1_ids,
        "gate": {"blocking_packages": gate_ids,
                 "rule": ("EC-3: packages 1-4 run first and each is recorded pass or fail. Only when all four have run_status completed_valid "
                          "and gate_pass true does ANY later package run (v2_run_wrapper.py W-6). A failure ends the task at the gate "
                          "and is classified per AC-5; the repair is a successor task under a new Coordinator decision."),
                 "F-4": "package 5 runs after the gate and is NOT blocking"},
        "targets_per_cell": 20,
        "target_streams": "random.Random('2026092001:v2:targets:<p>:<shape>'): the SAME targets for every arm and for m = 5 and m = 4 of a (p', shape)",
        "envelope": {"child_rlimit_as_bytes": 10737418240, "source": "AC-1 (DP-4: no dispatcher guard process reported; cap stays 10 GiB)",
                     "driver_rss_limit_bytes": 1073741824, "task_envelope_gb": 11, "msolve_threads": 1, "one_memory_heavy_process_at_a_time": True,
                     "host_at_stage_1": {"mem_total_kB": 16481980, "swap_total_kB": 0}},
        "early_stop": "A-7 pre-declared: an m = 5 cell that records 2 consecutive memory_exhausted outcomes at the same F4 degree records its remaining targets not_attempted with the stop reason",
        "watchdogs": WATCHDOGS,
        "instruction_measurement": {
            "rule": "DC-4 C-1. Labelled 'measured work proxy (instructions)'; never converted to F_p operations; never compared to 2^36",
            "perf": "perf_event_open(instructions:u) is attempted on every msolve child; on the stage-1 host it returns ENOENT (no hardware counter), recorded per row",
            "callgrind": "valgrind callgrind (total Ir and inclusive Ir of the F4 core, libneogb core_f4) on every fixture (n = m = 3) system and on target 0 of every m <= 4 cell",
            "not_measured": ("m = 5 rows, and m <= 4 cell targets other than target 0: not_measured, reason 'callgrind not affordable at this "
                             "shape/count (declared here before any run)'. Anchor, frozen-control and F-4 systems: perf attempt only (the anchor's "
                             "-g 1 wall time is not perturbed; controls and F-4 are not cost cells)"),
        },
        "contingency_rule": ("A contingency id may be used ONLY via `v2_run_wrapper.py <contingency id> --replaces <run id>` to re-run, with the "
                             "identical driver arguments, a NON-GATE package whose manifest records failure_class infrastructure_error. Never "
                             "for implementation_error, resource_exhaustion, invalid_measurement, a failed gate or an unfavourable result. Each "
                             "package is replaced at most once. The replaced package stays in the ledger; the aggregate names both. Unused "
                             "contingency ids are reported unused."),
        "known_issue_flags": [{
            "id": "KI-1",
            "text": ("ladder.json (v1, frozen) records b_is_square_in_Fq TRUE for the ecgfp5_shaped curve at p' = 16777291 "
                     "(y^2 = x(x^2 + 2x + 59z), order 4 * prime); re-checked in stage 1 by the norm criterion N(59z) = 59^5 * 2 "
                     "a square mod p'. DC-3 requires b a non-square at odd n, so torsion_S5_rq and S5_rescaled record a "
                     "'b-square class mismatch' refusal there, and arm iii' on EcGFp5-shaped curves can reach at most two ladder "
                     "primes (13 and 19 bits, span 6), below the frozen 3-prime / 12-bit rule. The amendment's premise 'ladder.json "
                     "records b_is_square_in_Fq false' holds at 4111 and 262151 only. Flagged for a Coordinator decision; this plan "
                     "does not change the ladder.")}],
        "packages": pk,
        "cells_enumeration": enum,
        "n_cells_enumerated": len(enum),
    }
    assert plan["package_count"] <= 48
    with open(out, "w") as fh:
        json.dump(plan, fh, indent=1)
        fh.write("\n")
    print("wrote %s with %d packages and %d enumerated cells" % (out, len(pk), len(enum)))


if __name__ == "__main__":
    main()
