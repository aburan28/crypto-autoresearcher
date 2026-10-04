#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2-a1 -- development check A1-7 (a): TOY-LADDER INTEGRATION (stage 1b only).

Called as `python3 -B a1_devchecks.py a --out SCRATCH_DIR`. Everything it writes goes under SCRATCH_DIR/toy.

  1. A1-3 triple logic on SYNTHETIC 3- and 4-rung inputs (TRUE / FALSE / not_applicable, the eligible-triple
     count, agreement with v2_scoring.heur_dflat when S has exactly three rungs), the AA-4 matched-triple
     figure and the A1-4 labels. Pure functions; no solver.
  2. A toy ladder at the TOY characteristic p = 1021 (n = 5, F_p[z]/(z^5 - c)), three curves chosen by PARI
     in a capped child (ecgfp5-model with N = 2q and b a non-square; a random 2-torsion curve with N = 2q and b
     a non-square; a random curve without rational 2-torsion with N = h q). NOT a ladder prime.
  3. A toy addendum plan mirroring trial-plan-v2-a1.json's 11-package layout at the toy prime, with the
     m = 5 / m = 4 roles played by m = 3 / m = 2 (as v2 DN-8), and toy-only watchdog keys for m = 2 added to
     BOTH the toy addendum plan and the toy copy of trial-plan-v2.json (so the wrapper's A-8 equality check
     runs unmodified on the toy pair).
  4. SYNTHETIC v2 packages in the toy runs directory: the four v2 gate packages (completed_valid), the 18 v2
     cell packages with synthetic per-target D values at the v2 primes (labelled synthetic), and the v2
     aggregate RUN-GFPN-8f86cc produced by v2_driver.cmd_aggregate itself on those synthetic rows; a synthetic
     phase-B receipt binding them.
  5. controls_a1 -> build -> 6 cell packages -> aggregate_a1 through a1_run_wrapper.main() with the plan,
     ladder and runs redirected to scratch, then a1_check_run on every toy package.
Redirections are module-level constants inside this process and inside a scratch shim that launches
a1_driver.py. ONE in-process stub is used: a1_run_wrapper.git_tree_state returns the real `git ls-files` list
plus the uncommitted addendum files as tracked and clean, because the addendum tree is not committed in
stage 1b (the real git refusal is exercised by check (e)). A synthetic TASK-20260923-4ff597 receipt in scratch
binds the addendum files as they are at the time of the check.
NO ladder curve, cell system or fixture system is solved at any prime: every solve is at p = 1021.
"""
import copy
import json
import os
import random
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
import a1_common as AC                                   # noqa: E402

TOY_P = 1021
M_ROLE = {5: 3, 4: 2}


def _dump(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


# ============================================================================ 1. synthetic reading-rule tests
def reading_rule_tests():
    import a1_reading as RD
    import v2_scoring as SC
    res = []

    def t(name, ok, detail=None):
        res.append({"test": name, "pass": bool(ok), "detail": detail})
        print("  %-70s %s" % (name, "PASS" if ok else "FAIL"))

    S3 = [4111, 262151, 1073741831]
    S4 = [4111, 262151, 16777291, 1073741831]
    b = RD.a1_3_verdict(S3, {4111: 1000, 262151: 1000, 1073741831: 1000})
    t("3-rung flat -> TRUE, 1 eligible triple evaluated", b["heur_dflat_pass"] is True and len(b["eligible_triples"]) == 1 and len(b["triples_evaluated"]) == 1, b["eligible_triples"])
    b = RD.a1_3_verdict(S3, {4111: 1000, 262151: 1000, 1073741831: 1200})
    t("3-rung 20% at 31 bits -> FALSE", b["heur_dflat_pass"] is False)
    b = RD.a1_3_verdict(S3, {4111: 1000, 262151: 1000, 1073741831: None})
    t("3-rung, 31-bit D undefined -> not_applicable (never FALSE)", b["heur_dflat_pass"] == "not_applicable" and b["triples_not_evaluable"][0]["missing_D_at"] == [1073741831])
    for cD in ({4111: 1000, 262151: 1000, 1073741831: 1050}, {4111: 1000, 262151: 1000, 1073741831: 1200}, {4111: 1000, 262151: 1000}, {}):
        a13 = RD.a1_3_verdict(S3, cD)["heur_dflat_pass"]
        v2 = SC.heur_dflat([(p, d) for p, d in cD.items() if d])["heur_dflat_pass"]
        t("3-rung A1-3 == v2_scoring.heur_dflat for %s" % sorted(cD.items()), a13 == v2, {"a1_3": a13, "v2": v2})
    b = RD.a1_3_verdict(S4, {4111: 500, 262151: 500, 16777291: 500, 1073741831: 500})
    t("4-rung flat -> TRUE with 4 eligible triples evaluated", b["heur_dflat_pass"] is True and len(b["eligible_triples"]) == 4 and len(b["triples_evaluated"]) == 4,
      [(e["triple"], e["span_bits"]) for e in b["triples_evaluated"]])
    t("4-rung triple spans are 12, 18, 18, 12 bits", sorted(e["span_bits"] for e in b["triples_evaluated"]) == [12, 12, 18, 18])
    b = RD.a1_3_verdict(S4, {4111: 600, 262151: 500, 16777291: 500, 1073741831: 500})
    t("4-rung 13-bit rung 20% off -> FALSE; triple {19,25,31} still passes", b["heur_dflat_pass"] is False and
      [e["below_threshold"] for e in b["triples_evaluated"] if 4111 not in e["triple"]] == [True])
    b = RD.a1_3_verdict(S4, {262151: 500, 16777291: 500, 1073741831: 520})
    t("4-rung 13-bit D missing -> only {19,25,31} evaluated -> TRUE; 3 triples not evaluable",
      b["heur_dflat_pass"] is True and len(b["triples_evaluated"]) == 1 and len(b["triples_not_evaluable"]) == 3)
    b = RD.a1_3_verdict(S4, {4111: 500, 1073741831: 500})
    t("4-rung two rungs missing -> not_applicable", b["heur_dflat_pass"] == "not_applicable")
    b = RD.a1_3_verdict(S4, {4111: 500, 262151: 500, 16777291: 600, 1073741831: 500})
    t("4-rung 25-bit rung 20% off -> FALSE", b["heur_dflat_pass"] is False)
    t("all-points figure present and labelled descriptive", b["all_points_figure"]["label"] == RD.ALL_POINTS_LABEL)
    m = RD.matched_triple_figure({4111: 500, 262151: 510, 1073741831: 505, 16777291: 9999})
    t("AA-4 figure emitted on {4111, 262151, 1073741831}; ignores 16777291; carries no pass key",
      m["status"] == "emitted" and "heur_dflat_pass" not in m and "below_threshold" not in m and m["label"] == RD.MATCHED_LABEL and "16777291" not in m["D"])
    m = RD.matched_triple_figure({4111: 500, 262151: 510})
    t("AA-4 figure not_applicable when a rung lacks D", m["status"] == "not_applicable")
    t("A1-4 label on (16777291, ecgfp5_shaped)", RD.reading_label(16777291, "ecgfp5_shaped") == AC.OFF_SHAPE_LABEL)
    t("A1-4 label NOT on (16777291, random_2torsion) or (1073741831, ecgfp5_shaped)",
      RD.reading_label(16777291, "random_2torsion") == "random_2torsion" and RD.reading_label(1073741831, "ecgfp5_shaped") == "ecgfp5_shaped")
    ev = RD.evaluate_all({("S5", "ecgfp5_shaped"): {4111: 7, 262151: 7, 1073741831: 7}})
    t("evaluate_all: off-shape set NOT EVALUATED; no2torsion rq not_applicable (refusal)",
      ev[AC.OFF_SHAPE_LABEL]["status"] == "NOT EVALUATED" and ev["random_no2torsion"]["torsion_S5_rq"]["heur_dflat_pass"] == "not_applicable"
      and ev["ecgfp5_shaped"]["S5"]["heur_dflat_pass"] is True)
    return res


# ============================================================================ 2. toy ladder (PARI, capped child)
def toy_ladder(tdir):
    import a1_pari as P
    import flint
    p = TOY_P
    cmod = next(c for c in range(2, p) if pow(c, (p - 1) // 5, p) != 1)
    mod = [(-cmod) % p, 0, 0, 0, 0, 1]
    rec = {"p": p, "p_bits": p.bit_length(), "cmod": cmod, "field": "F_%d[z]/(z^5 - %d)" % (p, cmod), "role": "TOY (stage-1b dev check (a)); not a ladder rung",
           "selection": {}, "curves": {}}
    # ecgfp5-model: smallest c with N = 2q, q prime, b = c z a non-square
    cands = [{"label": "c%d" % c, "a2": [2], "a4": [0, c], "a6": [0], "cofactor": 2} for c in range(1, 401)]
    r = P.curve_facts(p, mod, cands, os.path.join(tdir, "pari"), "toy_ecgfp5")
    rec["selection"]["ecgfp5_shaped"] = {"child": r["child"], "tried": len(cands)}
    for c in cands:
        f = r["curves"].get(c["label"], {})
        if f.get("cofactor_divides") == 1 and f.get("N_over_h_isprime") == 1 and f.get("b_is_square_in_Fq_by_norm_criterion") is False:
            rec["curves"]["ecgfp5_shaped"] = {"model": "y^2 = x(x^2 + 2x + %d*z)" % c["a4"][1], "a2": c["a2"], "a4": c["a4"], "a6": c["a6"],
                                              "c": c["a4"][1], "order": f["N"], "cofactor": 2, "subgroup_prime": f["N"] // 2,
                                              "b_is_square_in_Fq": False, "has_rational_2torsion": True}
            break
    rng = random.Random("stage1b-dev:a:toy-ladder:%d:random_2torsion" % p)
    cands = [{"label": "r%d" % i, "a2": [rng.randrange(p) for _ in range(5)], "a4": [rng.randrange(p) for _ in range(5)], "a6": [0], "cofactor": 2} for i in range(400)]
    r = P.curve_facts(p, mod, cands, os.path.join(tdir, "pari"), "toy_r2t")
    rec["selection"]["random_2torsion"] = {"child": r["child"], "tried": len(cands)}
    for c in cands:
        f = r["curves"].get(c["label"], {})
        if f.get("cofactor_divides") == 1 and f.get("N_over_h_isprime") == 1 and f.get("b_is_square_in_Fq_by_norm_criterion") is False:
            rec["curves"]["random_2torsion"] = {"model": "y^2 = x(x^2 + a x + b)", "a2": c["a2"], "a4": c["a4"], "a6": [0], "order": f["N"], "cofactor": 2,
                                                "subgroup_prime": f["N"] // 2, "b_is_square_in_Fq": False, "has_rational_2torsion": True}
            break
    rng = random.Random("stage1b-dev:a:toy-ladder:%d:random_no2torsion" % p)
    cands = [{"label": "n%d" % i, "a2": [0], "a4": [rng.randrange(p) for _ in range(5)], "a6": [rng.randrange(p) for _ in range(5)], "cofactor": 1} for i in range(400)]
    r = P.curve_facts(p, mod, cands, os.path.join(tdir, "pari"), "toy_n2t")
    rec["selection"]["random_no2torsion"] = {"child": r["child"], "tried": len(cands)}
    for c in cands:
        f = r["curves"].get(c["label"], {})
        if f.get("rational_2torsion_roots") != 0 or not f.get("N"):
            continue
        N = f["N"]
        h = next((h for h in range(1, 17) if N % h == 0 and flint.fmpz(N // h).is_prime()), None)
        if h is not None and h % 2 == 1:
            rec["curves"]["random_no2torsion"] = {"model": "y^2 = x^3 + a x + b", "a2": [0], "a4": c["a4"], "a6": c["a6"], "order": N, "cofactor": h,
                                                  "subgroup_prime": N // h, "has_rational_2torsion": False}
            break
    ok = all(s in rec["curves"] for s in AC.SHAPES)
    rec["complete"] = ok
    return rec


# ============================================================================ 3. toy plans
def toy_cells(shape, m_role, p):
    import v2_make_trial_plan as MP
    m = M_ROLE[m_role]
    src = MP.cells_m5(shape, p) if m_role == 5 else MP.cells_m4(shape)
    out = []
    for c in src:
        c = copy.deepcopy(c)
        c["arm"] = c["arm"].replace("S%d" % m_role, "S%d" % m)
        if c.get("condition"):
            c["condition"] = c["condition"].replace("S%d" % 5, "S%d" % M_ROLE[5])
        out.append(c)
    return out


def toy_plans(tdir, ladder_path):
    """Toy addendum plan + toy copy of trial-plan-v2.json (toy-only m = 2 watchdog keys added to both)."""
    real_a1 = AC.load_json(AC.PLAN_A1_PATH)
    v2 = AC.load_json(AC.V2_PLAN_PATH)
    wd = copy.deepcopy(v2["watchdogs"])
    for arm in ("raw", "S2", "S2_rescaled", "torsion_S2_rq", "torsion_S2_norm"):
        wd["per_arm_m"]["%s|m2" % arm] = {"per_target_timeout_s": 1800, "per_cell_no_measurement_watchdog_s": None, "note": "TOY-ONLY key (dev check (a))"}
    wd["per_arm_m"]["raw|m3"] = {"per_target_timeout_s": None, "per_cell_no_measurement_watchdog_s": None, "note": "TOY-ONLY key: raw at the m = 5 role is not_attempted"}
    wd["builder_timeout_s"]["m2"] = 1800
    v2t = copy.deepcopy(v2)
    v2t["watchdogs"] = wd
    v2t["toy_note"] = "TOY copy of trial-plan-v2.json for dev check (a): toy-only m = 2 watchdog keys added"
    p = TOY_P
    ids = ["RUN-TOYA1-%02d" % i for i in range(1, 12)]
    it = iter(ids)
    pk = []

    def add(**kw):
        kw["order"] = len(pk) + 1
        kw["run_id"] = next(it)
        kw["requires"] = [pk[-1]["run_id"]] if pk and kw["kind"] != "contingency" else []
        pk.append(kw)
        return kw

    add(label="TOY controls_a1", kind="controls_a1", blocking=True, gate_required=True, controls_a1_gate_required=False, p=p,
        driver_args=["controls-a1", "--p", str(p)], watchdogs="*|m3")
    builds = [{"shape": s, "arm": a % m, "m": m} for m in (3, 2) for s in AC.SHAPES for a in ("S%d", "S%d_rescaled", "torsion_S%d_rq", "torsion_S%d_norm")]
    add(label="TOY build", kind="build", blocking=False, gate_required=True, controls_a1_gate_required=True, p=p, driver_args=["build", "--p", str(p)], builds=builds)
    m5 = {}
    for s in AC.SHAPES:
        k = add(label="TOY cells %s m=3 (m = 5 role)" % s, kind="cells", blocking=False, gate_required=True, controls_a1_gate_required=True, p=p, shape=s, m=3,
                targets_per_cell=20, target_kind="random", driver_args=["cells", "--p", str(p), "--shape", s, "--m", "3"], cells=toy_cells(s, 5, p))
        m5[s] = k["run_id"]
    for s in AC.SHAPES:
        add(label="TOY cells %s m=2 (m = 4 role)" % s, kind="cells", blocking=False, gate_required=True, controls_a1_gate_required=True, p=p, shape=s, m=2,
            targets_per_cell=20, target_kind="random", driver_args=["cells", "--p", str(p), "--shape", s, "--m", "2", "--prior-run", m5[s]], cells=toy_cells(s, 4, p))
    a1_cells = [x["run_id"] for x in pk if x["kind"] == "cells"]
    v2_cells = [x["run_id"] for x in v2["packages"] if x["kind"] == "cells"]
    add(label="TOY aggregate_a1", kind="aggregate_a1", blocking=False, gate_required=True, controls_a1_gate_required=True,
        driver_args=["aggregate-a1", "--a1-runs", ",".join(a1_cells), "--v2-runs", ",".join(v2_cells), "--v2-aggregate", "RUN-GFPN-8f86cc"])
    for j in range(2):
        add(label="TOY contingency %d" % (j + 1), kind="contingency", blocking=False, gate_required=True, controls_a1_gate_required=True)
    # (beta, lam) at the toy prime by v2's rule, before any target is drawn
    C = AC.redirect_v2(ladder_path=ladder_path)
    import v2_arms as A
    rung = C.ladder_entry(p)
    F = C.ladder_field(rung)
    resc = {s: A.public_rescaling(A.rescaling(C.ladder_curve(F, rung, s)[0])) for s in AC.SHAPES}
    plan = copy.deepcopy(real_a1)
    plan.update({"toy_note": "TOY addendum plan (dev check (a)); layout of trial-plan-v2-a1.json at p = %d with m = 3 / 2 roles" % p,
                 "packages": pk, "package_count": len(pk), "watchdogs": wd, "cells_enumeration": [], "n_cells_enumerated": 0,
                 "gate": dict(real_a1["gate"], addendum_blocking_package=ids[0]),
                 "rescaling_parameters": dict(real_a1["rescaling_parameters"], p=p, per_shape=resc)})
    return plan, v2t


# ============================================================================ 4. synthetic v2 packages
SYN = "SYNTHETIC (dev check (a) only): per-target D values chosen by the check; never a measurement"


def synthetic_D(p, shape, arm):
    if shape == "ecgfp5_shaped":
        if p == 16777291:
            return None if arm in ("torsion_S5_rq", "S5_rescaled") else 5000       # off-shape: would move a primary verdict if it leaked
        return {"torsion_S5_rq": 100}.get(arm, 1000)
    if shape == "random_2torsion":
        return {"torsion_S5_rq": {4111: 100, 262151: 100, 16777291: 130}[p]}.get(arm, 1000)
    if shape == "random_no2torsion":
        return {4111: 1000, 262151: 1000, 16777291: 1050}[p] if arm == "S5" else None
    return None


def write_synthetic_v2(runs, v2plan):
    import yaml
    for g in AC.V2_GATE_PACKAGES:
        os.makedirs(os.path.join(runs, g), exist_ok=True)
        _dump(os.path.join(runs, g, "raw-result.json"), {"kind": "synthetic_gate", "run_status": "completed_valid", "gate_pass": True, "synthetic": SYN})
        with open(os.path.join(runs, g, "manifest.yaml"), "w") as fh:
            yaml.safe_dump({"run": {"id": g, "status": "completed_valid", "synthetic": SYN}}, fh)
    import v2_arms as A
    for pk in v2plan["packages"]:
        if pk["kind"] != "cells":
            continue
        cells = []
        for c in pk["cells"]:
            kind = A.parse_arm(c["arm"])[0]
            cell = {"arm": c["arm"], "kind": kind, "curve_shape": pk["shape"], "p": pk["p"], "p_bits": pk["p"].bit_length(), "m": pk["m"], "n": 5,
                    "target_kind": "random", "group": A.group_label(kind, pk["m"]), "group_order": A.group_order(kind, pk["m"]), "planned_as": c, "targets": [],
                    "synthetic": SYN}
            D = synthetic_D(pk["p"], pk["shape"], c["arm"]) if (pk["m"] == 5 and c["disposition"] == "run") else None
            if c["disposition"] != "run":
                cell["terminal"] = {"status": "not_attempted", "reason": c.get("reason")}
            elif c.get("expected_refusal"):
                cell["terminal"] = {"status": "refused", "reason": c["expected_refusal"], "synthetic": SYN}
            elif pk["m"] == 5 and D:
                per = {"0": D, "1": D, "2": D}
                cell["metrics"] = {"targets_planned": 20, "targets_attempted": 3, "targets_measured": 3, "outcome_counts": {"ok": 3}, "ideal_degree_D": D,
                                   "D_reason": None, "D_per_target": per, "decomposition_success_rate": 0.0, "targets_with_verified_relation": 0}
                cell["terminal"] = {"status": "measured", "reason": None}
            else:
                cell["terminal"] = {"status": "not_attempted", "reason": "SYNTHETIC toy row"}
            cells.append(cell)
        d = os.path.join(runs, pk["run_id"])
        os.makedirs(d, exist_ok=True)
        _dump(os.path.join(d, "raw-result.json"), {"kind": "cells", "p": pk["p"], "curve_shape": pk["shape"], "m": pk["m"], "n": 5, "cells": cells,
                                                   "run_status": "completed_valid", "synthetic": SYN})


V2_AGG_SHIM = r'''
import os, sys, argparse
sys.dont_write_bytecode = True
sys.path.insert(0, %(v2dir)r)
import v2_common as C
C.EXP_DIR = %(exp)r
C.PLAN_PATH = %(v2plan)r
import v2_driver as D
D.cmd_aggregate(argparse.Namespace(runs=%(runs)r))
'''

A1_DRIVER_SHIM = r'''
import os, sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, %(a1dir)r)
cfg = json.load(open(%(cfg)r))
import a1_common as AC
for k, v in cfg["AC"].items():
    setattr(AC, k, v)
import a1_driver as DR
AC.redirect_v2(plan_path=cfg["AC"]["PLAN_A1_PATH"], ladder_path=cfg["ladder"], exp_dir=cfg["exp"])
DR.main()
'''


# ============================================================================ 5. the integration
def dev_a(out):
    tdir = os.path.join(out, "toy")
    if os.path.exists(tdir):
        shutil.rmtree(tdir)
    exp = os.path.join(tdir, "exp")
    runs = os.path.join(exp, "runs")
    os.makedirs(runs)
    cache = os.path.join(tdir, "cache")
    os.makedirs(cache)
    report = {"toy_p": TOY_P, "no_ladder_curve_cell_or_fixture_system_solved": True}
    print("(a).1 A1-3 / AA-4 / A1-4 on synthetic inputs")
    report["reading_rule_tests"] = rr = reading_rule_tests()
    print("(a).2 toy ladder at p = %d (PARI, capped child)" % TOY_P)
    lad = toy_ladder(tdir)
    report["toy_ladder"] = lad
    if not lad["complete"]:
        _dump(os.path.join(out, "devcheck_a.json"), dict(report, pass_=False))
        print("DEV CHECK (a): FAIL (toy ladder incomplete)")
        return 1
    ladder_path = os.path.join(tdir, "toy-ladder.json")
    _dump(ladder_path, [lad])
    print("(a).3 toy plans")
    plan, v2t = toy_plans(tdir, ladder_path)
    plan_path, v2_path = os.path.join(tdir, "toy-trial-plan-v2-a1.json"), os.path.join(tdir, "toy-trial-plan-v2.json")
    _dump(plan_path, plan)
    _dump(v2_path, v2t)
    print("(a).4 synthetic v2 packages + v2 aggregate by v2_driver.cmd_aggregate")
    write_synthetic_v2(runs, v2t)
    agg_dir = os.path.join(runs, "RUN-GFPN-8f86cc")
    os.makedirs(agg_dir)
    v2cells = [x["run_id"] for x in v2t["packages"] if x["kind"] == "cells"]
    shim = os.path.join(tdir, "v2_aggregate_shim.py")
    with open(shim, "w") as fh:
        fh.write(V2_AGG_SHIM % {"v2dir": AC.V2_DIR, "exp": exp, "v2plan": v2_path, "runs": ",".join(v2cells)})
    env = dict(os.environ, GFPN_RUN_DIR=agg_dir, PYTHONDONTWRITEBYTECODE="1")
    pr = subprocess.run([sys.executable, "-B", shim], env=env, capture_output=True, text=True)
    report["v2_aggregate_shim"] = {"returncode": pr.returncode, "stderr_tail": pr.stderr[-2000:]}
    rel = lambda ap: os.path.relpath(ap, AC.REPO)                                   # noqa: E731
    pb = {"synthetic": SYN, "commit_sha": "toy-synthetic-not-a-commit",
          "path_sha256": {rel(os.path.join(runs, r, "raw-result.json")): AC.sha256_file(os.path.join(runs, r, "raw-result.json"))
                          for r in v2cells + ["RUN-GFPN-8f86cc"]}}
    pb_path = os.path.join(tdir, "toy-post-run-receipt.json")
    _dump(pb_path, pb)
    a1_rel = [AC.A1_PATHS_REL[0], AC.A1_PATHS_REL[1], rel(plan_path)]
    a1_files = sorted(os.path.relpath(os.path.join(dp, f), AC.REPO) for dp, _dn, fn in os.walk(AC.HERE) for f in fn)
    ra = {"synthetic": SYN, "commit_sha": "toy-synthetic-not-a-commit",
          "path_sha256": {**{f: AC.sha256_file(os.path.join(AC.REPO, f)) for f in a1_files + a1_rel[1:]}}}
    ra_path = os.path.join(tdir, "toy-a1-phase-a-receipt.json")
    _dump(ra_path, ra)
    ac_over = {"PLAN_A1_PATH": plan_path, "V2_PLAN_PATH": v2_path, "RUNS_DIR": runs, "RECEIPT_V2_PHASE_B": pb_path,
               "RECEIPT_A1_PHASE_A": ra_path, "A1_PATHS_REL": a1_rel}
    cfg_path = os.path.join(tdir, "toy-cfg.json")
    _dump(cfg_path, {"AC": ac_over, "ladder": ladder_path, "exp": exp})
    dshim = os.path.join(tdir, "a1_driver_shim.py")
    with open(dshim, "w") as fh:
        fh.write(A1_DRIVER_SHIM % {"a1dir": AC.HERE, "cfg": cfg_path})
    # ---- in-process redirection of the wrapper
    for k, v in ac_over.items():
        setattr(AC, k, v)
    import a1_run_wrapper as W
    W.RUNS, W.DRIVER = runs, dshim
    real_git = W.git_tree_state

    def git_stub(paths):
        if paths == AC.A1_PATHS_REL:
            return a1_files + a1_rel[1:], []
        return real_git(paths)
    W.git_tree_state = git_stub
    os.environ["GFPN_V2_CACHE_DIR"] = cache
    print("(a).5 addendum packages through a1_run_wrapper.main() (toy)")
    pkgs = []
    for pk in plan["packages"]:
        if pk["kind"] == "contingency":
            continue
        rc = W.main([pk["run_id"]])
        man = None
        mp = os.path.join(runs, pk["run_id"], "manifest.yaml")
        if os.path.exists(mp):
            import yaml
            man = yaml.safe_load(open(mp))["run"]
        pkgs.append({"run_id": pk["run_id"], "kind": pk["kind"], "wrapper_rc": rc, "status": man and man["status"],
                     "failure_class": man and man["failure_class"], "getrlimit": man and man["resources"]["child_rlimit_as_read_back_by_getrlimit"],
                     "threads": man and man["resources"]["msolve_threads_executed"]})
        print("   %s %-13s rc=%s status=%s" % (pk["run_id"], pk["kind"], rc, man and man["status"]))
    report["packages"] = pkgs
    # contingency refusal inside the toy: a completed_valid package may not be replaced
    refs, _ = W.preflight(plan["packages"][9]["run_id"], plan["packages"][2]["run_id"])
    report["toy_contingency_refusal"] = refs
    # ---- completion-gate checker on every toy package
    import a1_check_run as K
    K.C.EXP_DIR = exp
    K.C.LADDER_PATH = ladder_path
    K.C.PLAN_PATH = plan_path
    checks = []
    for x in pkgs:
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = K.main(os.path.join(runs, x["run_id"]))
        checks.append({"run_id": x["run_id"], "rc": rc, "output": buf.getvalue()})
        print("   check %s rc=%s" % (x["run_id"], rc))
    report["checker"] = checks
    agg = AC.load_json(os.path.join(runs, plan["packages"][8]["run_id"], "raw-result.json"))
    sec = {"phase_B_check": agg.get("v2_bytes_phase_B_check", {}).get("status"),
           "A1_3_pass": agg["metrics"]["heur_dflat_pass_A1_3"],
           "off_shape_rows": len(agg["section_iii_off_shape_descriptive"]["rows"]),
           "primary_scoring_groups": [(s["p"], s["m"]) for s in agg["section_i_primary_shape_reading"]["like_for_like_scoring"]],
           "AA_4": {sh: {a: v.get("status") for a, v in blk.items()} for sh, blk in agg["section_ii_control_reading"]["AA_4_matched_triple"].items()},
           "reconciliation_marked": sorted(k for k, v in agg["section_iv_reconciliation_with_v2_aggregate"]["figures"]["heur_dflat"].items() if "mark" in v),
           "planned_cells_without_row": len(agg["section_v_planned_cells_without_row"])}
    report["aggregate_a1_summary"] = sec
    print(json.dumps(sec, indent=1))
    exp_primary = {"S5": "not_applicable", "torsion_S5_rq": "not_applicable"}
    ok = (all(t["pass"] for t in rr) and all(x["status"] == "completed_valid" for x in pkgs) and all(c["rc"] == 0 for c in checks)
          and sec["phase_B_check"] == "verified" and all(sec["A1_3_pass"]["ecgfp5_shaped"][a] == v for a, v in exp_primary.items())
          and sec["A1_3_pass"]["random_2torsion"]["torsion_S5_rq"] is False and sec["A1_3_pass"]["random_2torsion"]["S5"] is True
          and sec["A1_3_pass"]["random_no2torsion"]["S5"] is True and sec["off_shape_rows"] > 0 and 16777291 not in [g[0] for g in sec["primary_scoring_groups"]]
          and bool(report["toy_contingency_refusal"]))
    report["expected_toy_readings"] = ("primary set {4111, 262151, 1073741831}: 31-bit rung absent in the toy -> not_applicable for every arm "
                                       "(the synthetic off-shape D = 5000 at 16777291 must NOT enter); random_2torsion torsion_S5_rq: synthetic 30% "
                                       "variation at 16777291 -> FALSE on the triple {4111, 262151, 16777291}; random_2torsion S5 and random_no2torsion "
                                       "S5 (5%) -> TRUE; toy-rung rows (p = 1021) belong to no A1-3 set")
    report["pass"] = ok
    _dump(os.path.join(out, "devcheck_a.json"), report)
    print("DEV CHECK (a): %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1
