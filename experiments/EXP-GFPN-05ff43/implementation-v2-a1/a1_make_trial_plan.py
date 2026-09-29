#!/usr/bin/env python3
"""Writes experiments/EXP-GFPN-05ff43/trial-plan-v2-a1.json (addendum A1-2; card S1B-4).

usage: python3 -B a1_make_trial_plan.py IDS_FILE [--out PATH] [--branch 31-bit|FB-1] [--fb1-c C]

IDS_FILE holds one RUN-GFPN-* id per line, each minted with `python3 tools/allocate_id.py --next run
--area GFPN` and confirmed free with `--check`; they are consumed IN FILE ORDER, one per package.

31-bit plan (A1-2), 11 packages in this order:
  1 controls_a1 (blocking; checks (a)-(f))   2 build p' = 1073741831
  3-5 cells m = 5 (ecgfp5_shaped, random_2torsion, random_no2torsion)
  6-8 cells m = 4 (same shape order)          9 aggregate_a1          10-11 contingency
FB-1 plan (A1-9), 7 packages: controls_a1 (c_fb1), build (c_fb1 only), cells m = 5, cells m = 4,
aggregate_a1, 2 contingency. Written only if AA-3 fired (it did not in stage 1b).

The cell set and dispositions are v2's own (v2_make_trial_plan.cells_m5 / cells_m4 / builds, imported
read-only), so they are exactly A1-1's. Watchdogs, builder and callgrind timeouts are COPIED VERBATIM
from trial-plan-v2.json's "watchdogs" object (its lines 95-177), never retyped. (beta, lam) is fixed
per (curve, p') by v2's rule (v2_arms.rescaling) and recorded here before any target is drawn.
"""
import copy
import json
import re
import sys

sys.dont_write_bytecode = True
import a1_common as AC                                   # noqa: E402

import v2_arms as A                                      # noqa: E402
import v2_common as C                                    # noqa: E402
import v2_make_trial_plan as MP                          # noqa: E402

CONTROLS_A1_CONTENT = (
    "A1-2 (a)-(f) at p' = %d: (a) known_scalar_instances independent recheck for all three shapes; (b) PARI ellcard recheck of "
    "the three orders against ladder.json with the double-odd facts for ecgfp5_shaped and random_2torsion (order mod 4 = 2, "
    "cofactor 2, b a non-square by the norm criterion); (c) (beta, lam) for both 2-torsion shapes, compared with this plan, and "
    "the rq refusal on random_no2torsion; (d) the msolve characteristic check on the synthetic systems of A1-7 (b) (a1_health.py); "
    "(e) planted m < n instrument checks of the lifting path for torsion_S3_rq and S3_rescaled on the ecgfp5_shaped curve "
    "(n = 5), every certificate passing the independent verifier -- never degree evidence; (f) single-flip and held-out checks "
    "on every polynomial it builds")


def watchdogs_verbatim():
    v2 = AC.load_json(AC.V2_PLAN_PATH)
    return copy.deepcopy(v2["watchdogs"]), v2


def canonical_sha256(obj):
    import hashlib
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rescaling_record(p):
    rung = C.ladder_entry(p)
    F = C.ladder_field(rung)
    out = {}
    for shape in AC.SHAPES:
        E, _cv = C.ladder_curve(F, rung, shape)
        rs = A.rescaling(E)
        out[shape] = A.public_rescaling(rs)
    return out


def main():
    ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else AC.PLAN_A1_PATH
    branch = sys.argv[sys.argv.index("--branch") + 1] if "--branch" in sys.argv else "31-bit"
    if branch != "31-bit":
        raise SystemExit("only the 31-bit plan is implemented as a writer; the FB-1 plan is written only if AA-3 fires "
                         "(it did not in stage 1b: see implementation-v2-a1.md)")
    for i in ids:
        assert re.fullmatch(r"RUN-GFPN-[0-9a-f]{6}", i), i
    assert len(set(ids)) == len(ids) == 11, "the 31-bit plan reserves exactly 11 ids"
    wd, v2 = watchdogs_verbatim()
    v1_ids = sorted(v2["v1_ids_never_reused"])
    v2_ids = sorted(p["run_id"] for p in v2["packages"])
    assert not set(ids) & set(v1_ids), "a v1 id would be reused"
    assert not set(ids) & set(v2_ids), "a v2 id would be reused"
    p = AC.P_RUNG31
    it = iter(ids)
    pk = []

    def add(**kw):
        kw["order"] = len(pk) + 1
        kw["run_id"] = next(it)
        kw["requires"] = [pk[-1]["run_id"]] if pk and kw["kind"] != "contingency" else []
        pk.append(kw)
        return kw

    add(label="controls_a1, p' = %d (BLOCKING for the addendum)" % p, kind="controls_a1", blocking=True, gate_required=True,
        controls_a1_gate_required=False, p=p, driver_args=["controls-a1", "--p", str(p)],
        watchdogs="per_arm_m keys *|m3 and builder_timeout_s m3 (uniform with v2)", content=CONTROLS_A1_CONTENT % p)
    controls_id = pk[-1]["run_id"]
    add(label="build p' = %d (m = 5 and m = 4; all shapes; refusal rows)" % p, kind="build", blocking=False, gate_required=True,
        controls_a1_gate_required=True, p=p, driver_args=["build", "--p", str(p)], builds=MP.builds(p),
        watchdogs="builder_timeout_s m5 / m4", build_list_note="identical to v2's per-prime build package list (v2_make_trial_plan.builds)")
    m5 = {}
    for shape in AC.SHAPES:
        k = add(label="cells p' = %d, %s, m = 5" % (p, shape), kind="cells", blocking=False, gate_required=True, controls_a1_gate_required=True,
                p=p, shape=shape, m=5, targets_per_cell=20, target_kind="random",
                driver_args=["cells", "--p", str(p), "--shape", shape, "--m", "5"], cells=MP.cells_m5(shape, p), watchdogs="per_arm_m keys *|m5")
        m5[shape] = k["run_id"]
    for shape in AC.SHAPES:
        add(label="cells p' = %d, %s, m = 4" % (p, shape), kind="cells", blocking=False, gate_required=True, controls_a1_gate_required=True,
            p=p, shape=shape, m=4, targets_per_cell=20, target_kind="random",
            driver_args=["cells", "--p", str(p), "--shape", shape, "--m", "4", "--prior-run", m5[shape]], cells=MP.cells_m4(shape),
            watchdogs="per_arm_m keys *|m4")
    a1_cells = [x["run_id"] for x in pk if x["kind"] == "cells"]
    v2_cells = [x["run_id"] for x in v2["packages"] if x["kind"] == "cells"]
    v2_agg = [x["run_id"] for x in v2["packages"] if x["kind"] == "aggregate"]
    assert len(v2_agg) == 1
    add(label="aggregate_a1 (A1-5 (i)-(v); A1-3; A1-4; DEC-20260923-8b2dbf AA-4)", kind="aggregate_a1", blocking=False, gate_required=True,
        controls_a1_gate_required=True,
        driver_args=["aggregate-a1", "--a1-runs", ",".join(a1_cells), "--v2-runs", ",".join(v2_cells), "--v2-aggregate", v2_agg[0]],
        content="reads the v2 cell packages and RUN-GFPN-8f86cc from their phase-B-archived bytes (TASK-20260923-0fa03f post-run receipt) and the addendum packages; never edits a v2 manifest")
    for j in range(2):
        add(label="contingency a1-%d" % (j + 1), kind="contingency", blocking=False, gate_required=True, controls_a1_gate_required=True,
            content="used only under contingency_rule (trial-plan-v2.json, verbatim), for ADDENDUM packages only; unused ids stay unused and are reported as such")
    assert not list(it)
    enum = []
    for x in pk:
        if x["kind"] == "cells":
            for c in x["cells"]:
                enum.append({"run_id": x["run_id"], "order": x["order"], "arm": c["arm"], "curve_shape": x["shape"], "p": x["p"], "m": x["m"],
                             "n": 5, "target_kind": "random", "disposition": c["disposition"], "condition": c.get("condition"),
                             "expected_refusal": c.get("expected_refusal"), "reason": c.get("reason")})
    resc = rescaling_record(p)
    plan = {
        "schema": "crypto.autoresearch.trial_plan.v2a1",
        "experiment_id": AC.EXPERIMENT_ID,
        "protocol_version": AC.PROTOCOL_VERSION,
        "task_id": AC.TASK_ID_RUNS,
        "task_id_note": "the task that RUNS this plan (stage 2b); written by stage 1b under TASK-20260923-4c64b5",
        "written_by_task": AC.TASK_ID_STAGE_1B,
        "addendum": {"id": AC.ADDENDUM_ID, "path": "experiments/EXP-GFPN-05ff43/amendments/v2_addendum_rung31.yaml",
                     "sha256": AC.ADDENDUM_SHA256, "approval_decision": AC.ADDENDUM_APPROVAL},
        "v2_amendment": {"id": AC.V2_AMENDMENT_ID, "path": "experiments/EXP-GFPN-05ff43/amendments/v1_to_v2_reanchor_and_arm_iii.yaml",
                         "sha256": AC.V2_AMENDMENT_SHA256, "approval_decision": AC.V2_APPROVAL},
        "written_at": "2026-09-23",
        "written_in": "stage 1b (implement, do not run); no v2 and no addendum run package exists",
        "archived_by": "TASK-20260923-4ff597 phase A (Coordinator)",
        "plan_branch": "31-bit",
        "plan_branch_evidence": ("DEC-20260923-8b2dbf AA-3: development check A1-7 (b) PASSED at p' = 1073741831 on both seeded systems "
                                 "((2,2,2) D = 8, (4,4,4) D = 64) and the identical harness PASSED at p' = 16777291; the FB-1 trigger "
                                 "requires both 1073741831 systems to FAIL, so FB-1 did not fire. Recorded in implementation-v2-a1.md."),
        "package_ceiling_shared": AC.MAX_PACKAGES_SHARED,
        "package_count": len(pk),
        "package_count_note": "11 packages: 9 planned + 2 contingency. v2 has 31 (trial-plan-v2.json); 31 + 11 = 42 <= 48 (DC-7 A-7 shared ceiling; AA-5 (e)); 6 unreserved",
        "v2_package_count": len(v2["packages"]),
        "id_minting": "each id minted with `python3 tools/allocate_id.py --next run --area GFPN` and confirmed free with `--check` (0 occurrences) before this file was written",
        "v1_ids_never_reused": v1_ids,
        "v2_ids_never_reused": v2_ids,
        "gate": {
            "v2_blocking_packages": list(AC.V2_GATE_PACKAGES),
            "addendum_blocking_package": controls_id,
            "rule": ("A1-2 gates: controls_a1 runs only after all four v2 gate packages have run_status completed_valid and gate_pass true. "
                     "Packages 2-9 (and any contingency) additionally require controls_a1 completed_valid with gate_pass true. A controls_a1 "
                     "failure ends the addendum's run at its gate; remaining packages are recorded not_attempted with the reason; the failure "
                     "is an infrastructure or implementation signal, never a result; the repair is a successor task under a new Coordinator "
                     "decision. If the v2 gate fails, no addendum package runs (AC-5). Enforced by a1_run_wrapper.py.")},
        "targets_per_cell": 20,
        "target_streams": "random.Random('2026092001:v2:targets:1073741831:<shape>'): v2's own pattern keyed by (p', shape); the SAME targets for every arm and for m = 5 and m = 4 of a (p', shape) (A1-1)",
        "target_stream_strings": {s: "random.Random('2026092001:v2:targets:%d:%s')" % (p, s) for s in AC.SHAPES},
        "other_streams": {
            "basepoint": "random.Random('2026092002:v2:basepoint:1073741831:<shape>') (v2 pattern)",
            "build_samples": "random.Random('2026092002:v2:build:1073741831:<shape>:<arm>:<m>') (v2 pattern)",
            "grid": "random.Random('2026092002:v2:grid:1073741831:<shape>:<arm>:<m>:<target>') (v2 pattern)",
            "controls_a1_builds": "random.Random('2026092002:v2a1:build:1073741831:ecgfp5_shaped:<arm>:3:controls_a1')",
            "controls_a1_planted": "random.Random('2026092001:v2a1:controls_a1:planted:1073741831:<arm>')",
            "controls_a1_known_scalar": "C.ladder_targets (v2 target pattern), first 3 targets per shape, checked by independent arithmetic",
            "controls_a1_health": "random.Random('2026092001:v2a1:health:1073741831') and ':2' (A1-7 (b))",
        },
        "rescaling_parameters": {
            "rule": "beta = smallest non-square mod p'; lam = sqrt(b/beta) in F_q, the root with the lexicographically smaller coefficient vector (implementation-v2.md 2.2; v2_arms.rescaling). Fixed per (curve, p') BEFORE any target is drawn; cells recompute and compare, a difference invalidates the cell.",
            "p": p, "per_shape": resc},
        "envelope": {"child_rlimit_as_bytes": AC.CAP_BYTES,
                     "source": "AC-1; DP-4 of the stage-1b launch: dispatcher memory-guard threshold MemAvailable < 2621440 kB (about 13.2 GB in use) is above 12.0 GB, so the cap is not lowered",
                     "driver_rss_limit_bytes": 1073741824, "task_envelope_gb": 11, "msolve_threads": 1, "one_memory_heavy_process_at_a_time": True,
                     "host_at_stage_1b": {"mem_total_kB": 16481980, "swap_total_kB": 0}},
        "early_stop": v2["early_stop"],
        "watchdogs": wd,
        "watchdogs_source": "trial-plan-v2.json \"watchdogs\" object (its lines 95-177), copied verbatim by a1_make_trial_plan.py; a1_run_wrapper.py refuses any package if this object differs from trial-plan-v2.json's (AC-6)",
        "watchdogs_canonical_sha256": canonical_sha256(wd),
        "instruction_measurement": copy.deepcopy(v2["instruction_measurement"]),
        "contingency_rule": v2["contingency_rule"],
        "contingency_rule_scope": ("the rule above is trial-plan-v2.json's, verbatim; under this plan it applies to ADDENDUM packages only, "
                                   "invoked as `a1_run_wrapper.py <contingency id> --replaces <addendum run id>`; controls_a1 is the addendum's "
                                   "blocking gate package and is never replaced; v2's four contingency ids apply to v2 packages only"),
        "reading_rules": {
            "A1-4_off_shape": {"label": AC.OFF_SHAPE_LABEL, "applies_to": {"p": 16777291, "curve_shape": "ecgfp5_shaped", "c": 59},
                               "section_title": AC.OFF_SHAPE_TITLE},
            "A1-3_evaluation_sets": {
                "ecgfp5_shaped": {"arms": ["torsion_S5_rq", "S5", "S5_rescaled", "torsion_S5_norm"], "S": [4111, 262151, 1073741831], "raw": "not_applicable"},
                "random_2torsion": {"arms": ["torsion_S5_rq", "S5", "S5_rescaled", "torsion_S5_norm"], "S": [4111, 262151, 16777291, 1073741831], "raw": "not_applicable"},
                "random_no2torsion": {"arms": ["S5"], "S": [4111, 262151, 16777291, 1073741831],
                                      "not_applicable_arms": ["torsion_S5_rq", "S5_rescaled", "torsion_S5_norm", "raw"]},
                "off_shape_non_double_odd": "NOT EVALUATED",
                "rule": "eligible triple = any 3 rungs of S spanning >= 12 bits (bit_length difference); TRUE iff >= 1 eligible triple has D at all three rungs and EVERY such triple has relative variation < 0.10 (v2_scoring.heur_dflat unchanged); FALSE iff any such triple fails; not_applicable iff none has D at all three rungs"},
            "AA-4_matched_triple": {"triple": [4111, 262151, 1073741831], "for": {"random_2torsion": ["torsion_S5_rq", "S5", "S5_rescaled", "torsion_S5_norm"],
                                                                                 "random_no2torsion": ["S5"]},
                                    "label": "matched-triple figure (same rungs as the primary set); descriptive; not a verdict"},
        },
        "known_issue_flags": [],
        "packages": pk,
        "cells_enumeration": enum,
        "n_cells_enumerated": len(enum),
    }
    assert len(v2["packages"]) + plan["package_count"] <= AC.MAX_PACKAGES_SHARED
    assert plan["watchdogs"] == v2["watchdogs"]
    txt = json.dumps(plan, indent=1)
    assert AC.FORBIDDEN_TASK_ID not in txt
    with open(out, "w") as fh:
        fh.write(txt + "\n")
    print("wrote %s with %d packages and %d enumerated cells" % (out, len(pk), len(enum)))


if __name__ == "__main__":
    main()
