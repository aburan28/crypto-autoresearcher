#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2-a1 -- addendum driver. Runs inside a run package created by
a1_run_wrapper.py (which sets GFPN_RUN_DIR and GFPN_V2_PACKAGE) and writes raw-result.json,
ladder-table.yaml, heur-dflat.yaml, cost-band-p64.yaml and certificates/.

REUSE OF v2, ADDITIVELY (A1-7 (1); DEC-20260923-8b2dbf AA-5 (c)):
  * a1_common.redirect_v2() sets, IN THIS PROCESS ONLY, v2_common.PLAN_PATH = trial-plan-v2-a1.json and
    v2_common.TASK_ID = TASK-20260923-6c7f55. v2_driver.cmd_build / cmd_cells then read their package from
    the addendum plan and are reused unchanged for p' = 1073741831. No v2 function is replaced.
  * v2_driver.cmd_controls hard-codes (4111, 262151, 16777291) and is NEVER called here. controls_a1 is
    this file's own entry point (A1-2 (a)-(f)).
  * aggregate_a1 is this file's own entry point (A1-5 (i)-(v), A1-3, A1-4, AA-4).

Subcommands:
  controls-a1  --p P                       A1-2 (a)-(f) at P (blocking for the addendum)
  build        --p P                       = v2_driver.cmd_build on the addendum plan's build package
  cells        --p P --shape S --m M [--prior-run RUN]   = v2_driver.cmd_cells on the addendum plan
  aggregate-a1 --a1-runs R,.. --v2-runs R,.. --v2-aggregate RUN
"""
import argparse
import json
import os
import random
import sys
import time

sys.dont_write_bytecode = True
import a1_common as AC                                   # noqa: E402

C = AC.redirect_v2()                                     # PLAN_PATH -> trial-plan-v2-a1.json; TASK_ID -> 6c7f55

import v2_arms as A                                      # noqa: E402
import v2_driver as D                                    # noqa: E402
import v2_scoring as SC                                  # noqa: E402
import v2_verify_independent as VI                       # noqa: E402
from v2_field import OpCount, self_test as field_self_test   # noqa: E402

import a1_health as H                                    # noqa: E402
import a1_pari as P                                      # noqa: E402
import a1_reading as RD                                  # noqa: E402

log = D.log


def _protocol_block():
    return {"protocol_version": AC.PROTOCOL_VERSION, "addendum_id": AC.ADDENDUM_ID, "addendum_sha256": AC.ADDENDUM_SHA256,
            "task_id": AC.TASK_ID_RUNS}


def _check_package_p(ctx, p):
    if int(ctx.pkg.get("p") or -1) != int(p):
        raise SystemExit("REFUSING: --p %s does not match the plan package's p %s" % (p, ctx.pkg.get("p")))


# ============================================================================ controls_a1 (A1-2 (a)-(f))
def cmd_controls_a1(args):
    ctx = D.Ctx()
    _check_package_p(ctx, args.p)
    t0 = time.time()
    p = args.p
    checks = []

    def rec(name, ok, detail=None):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        log(name, "PASS" if ok else "FAIL")

    field_self_test()
    rung = C.ladder_entry(p)
    F = C.ladder_field(rung)
    ctx._p = p
    # (a) known_scalar_instances: base point order and R = [k]G re-checked by the INDEPENDENT arithmetic, all three shapes
    ks = []
    for shape in AC.SHAPES:
        Ex, cvx = C.ladder_curve(F, rung, shape)
        nx = int(cvx["subgroup_prime"])
        Gx = C.base_point(Ex, nx, int(cvx["cofactor"]), p, shape)
        tg = C.ladder_targets(Ex, Gx, nx, p, shape, 3)
        Fi = VI.FqP(p, F.modulus)
        Ei = VI.CurveP(Fi, F.coeffs(Ex.a2), F.coeffs(Ex.a4), F.coeffs(Ex.a6))
        Gi = (tuple(F.coeffs(Gx[0])), tuple(F.coeffs(Gx[1])))
        ok = (Ei.on_curve(Gi) and Ei.mul(nx, Gi) is None
              and all(Ei.mul(t["k"], Gi) == (tuple(F.coeffs(t["R"][0])), tuple(F.coeffs(t["R"][1]))) for t in tg))
        ks.append({"p": p, "shape": shape, "pass": ok, "n_targets_checked": len(tg)})
    rec("a_known_scalar_instances_independent_recheck", all(x["pass"] for x in ks), ks)
    # (b) PARI ellcard recheck against ladder.json, double-odd facts (capped gp child)
    pari_dir = os.path.join(ctx.rd, "pari")
    curves = [{"label": s, "a2": rung["curves"][s]["a2"], "a4": rung["curves"][s]["a4"], "a6": rung["curves"][s]["a6"],
               "cofactor": rung["curves"][s]["cofactor"]} for s in AC.SHAPES]
    pr = P.curve_facts(p, list(F.modulus), curves, pari_dir, "controls_a1_pari")
    pr["gp_version"] = P.gp_version()
    detail_b = {"pari": pr, "per_shape": {}}
    ok_b = pr["complete"]
    for s in AC.SHAPES:
        f, cv = pr["curves"].get(s, {}), rung["curves"][s]
        d = {"ellcard_equals_ladder_order": f.get("N") == int(cv["order"]),
             "N_over_cofactor_is_ladder_subgroup_prime": f.get("N") is not None and f["N"] // int(cv["cofactor"]) == int(cv["subgroup_prime"]) and f["N"] % int(cv["cofactor"]) == 0,
             "N_over_cofactor_isprime_PARI": f.get("N_over_h_isprime") == 1, "N_mod_4": f.get("N_mod_4"),
             "rational_2torsion_roots": f.get("rational_2torsion_roots")}
        ok_s = d["ellcard_equals_ladder_order"] and d["N_over_cofactor_is_ladder_subgroup_prime"] and d["N_over_cofactor_isprime_PARI"]
        if s in ("ecgfp5_shaped", "random_2torsion"):
            d.update({"double_odd_order_mod_4_is_2": f.get("N_mod_4") == 2, "cofactor_is_2": int(cv["cofactor"]) == 2,
                      "b_nonsquare_by_norm_criterion": f.get("b_is_square_in_Fq_by_norm_criterion") is False,
                      "norm_pari_equals_pure_python": f.get("norm_b_agrees_pari_vs_pure_python") is True,
                      "ladder_json_b_is_square_in_Fq": cv.get("b_is_square_in_Fq")})
            ok_s = ok_s and d["double_odd_order_mod_4_is_2"] and d["cofactor_is_2"] and d["b_nonsquare_by_norm_criterion"] and d["norm_pari_equals_pure_python"]
        else:
            d["no_rational_2torsion"] = f.get("rational_2torsion_roots") == 0
            ok_s = ok_s and d["no_rational_2torsion"]
        d["pass"] = ok_s
        detail_b["per_shape"][s] = d
        ok_b = ok_b and ok_s
    rec("b_pari_ellcard_recheck_and_double_odd_facts", ok_b, detail_b)
    # (c) (beta, lam) for both 2-torsion shapes, compared with the plan; rq refusal on random_no2torsion
    planned = (ctx.plan.get("rescaling_parameters") or {}).get("per_shape", {})
    det_c = {}
    ok_c = True
    for s in ("ecgfp5_shaped", "random_2torsion"):
        E, _ = C.ladder_curve(F, rung, s)
        rs = A.public_rescaling(A.rescaling(E))
        same = (not rs["refused"]) and planned.get(s, {}).get("beta") == rs["beta"] and planned.get(s, {}).get("lam") == rs["lam"]
        det_c[s] = {"rescaling": rs, "equals_plan": same}
        ok_c = ok_c and same
    E_no, _ = C.ladder_curve(F, rung, "random_no2torsion")
    r_no = A.public_rescaling(A.rescaling(E_no))
    det_c["random_no2torsion"] = {"rescaling": r_no, "refusal_as_required": r_no.get("refused") is True and r_no.get("reason") == "no rational 2-torsion"}
    ok_c = ok_c and det_c["random_no2torsion"]["refusal_as_required"]
    rec("c_beta_lam_recorded_and_rq_refusal_on_random_no2torsion", ok_c, det_c)
    # (d) msolve characteristic check on the synthetic systems of A1-7 (b)
    hr = H.run(p, os.path.join(ctx.rd, "health"), cap=ctx.cap)
    rec("d_msolve_characteristic_check_synthetic", hr["pass"],
        {"report": "health/health-%d.json" % p, "per_pattern": [{"pattern": e["pattern"], "pass": e["pattern_pass"],
                                                                  "D": e["first"]["dimension_of_quotient_printed"],
                                                                  "getrlimit": e["first"]["child"].get("rlimit_as_child_getrlimit")} for e in hr["systems"]]})
    # (e) planted m < n instrument checks of the lifting path: torsion_S3_rq and S3_rescaled on ecgfp5_shaped (n = 5)
    E5, cv5 = C.ladder_curve(F, rung, "ecgfp5_shaped")
    rs5 = A.rescaling(E5)
    nsub5 = int(cv5["subgroup_prime"])
    built = {}
    if rs5["refused"]:
        rec("e_orbit_lifting_path_prerequisite_rescaling", False, A.public_rescaling(rs5))
    else:
        pool_u = A.pool_u(E5, rs5["lam_obj"], 400)
        for arm in ("torsion_S3_rq", "S3_rescaled"):
            kind, _ = A.parse_arm(arm)
            seed = "%d:v2a1:build:%d:ecgfp5_shaped:%s:3:controls_a1" % (C.SEED_CURVES, p, arm)
            polc, info = D.build_poly(ctx, F, E5, arm, 3, seed, "ctl_a1_%s" % arm, ctx.plan["watchdogs"]["builder_timeout_s"]["m3"])
            built[arm] = info
            rngp = random.Random("%d:v2a1:controls_a1:planted:%d:%s" % (C.SEED_TARGETS, p, arm))
            Rp5 = None
            for _ in range(400):
                sel = rngp.sample(pool_u, 3)
                pts = [E5.lift_x(rs5["lam_obj"] * F(u)) for u in sel]
                if any(Pt is None for Pt in pts):
                    continue
                S = None
                for Pt in pts:
                    S = E5.add(S, Pt)
                if S is not None and E5.mul(nsub5, S) is None:
                    Rp5 = S
                    break
            if polc is None or Rp5 is None:
                rec("e_orbit_lifting_path_%s" % arm, False, {"reason": "build failed or no planted sum in the prime-order subgroup",
                                                             "build": {k: info.get(k) for k in ("outcome", "reason")}})
                continue
            names, eqs = A.system_for_target(polc, Rp5[0], rs5)
            s = D.solve(ctx, names, eqs, "ctl_a1_planted_%s" % arm, C.watchdog(ctx.plan, arm, 3)["per_target_timeout_s"], retain_input=True)
            lc = D.lift_and_certify(ctx, F, E5, cv5, "ecgfp5_shaped", arm, kind, 3, rs5, nsub5, Rp5, 1, Rp5, s["solutions"], "ctl_a1_planted",
                                    "planted_instrument_check_m_lt_n", OpCount(5),
                                    extra={"instrument_check": "m < n planted target: D is a planted-orbit size, never a degree (CORR-20260923-57177b)",
                                           **{"a1_" + k: v for k, v in _protocol_block().items()}})
            rec("e_orbit_lifting_path_%s" % arm, s["outcome"] == "ok" and lc["n_relations_verified"] >= 1 and lc["n_relations_verified"] == lc["n_relations"],
                {"outcome": s["outcome"], "n_rational_solutions": len(s["solutions"]), "n_relations": lc["n_relations"],
                 "verified": lc["n_relations_verified"], "threads_executed": s.get("threads_executed"),
                 "solver_getrlimit": (s.get("solver") or {}).get("rlimit_as_child_getrlimit"),
                 "note": "instrument check only; the planted D is never read as a degree"})
    # (f) single-flip and held-out checks on every polynomial built here
    det_f = {}
    ok_f = bool(built)
    for arm, info in built.items():
        meta = (info or {}).get("meta") or {}
        sf = (meta.get("single_flip_test") or {}).get("pass")
        ho = meta.get("held_out_mismatches")
        det_f[arm] = {"build_outcome": (info or {}).get("outcome"), "single_flip_pass": sf, "held_out_mismatches": ho,
                      "build_getrlimit": ((info or {}).get("child") or {}).get("rlimit_as_child_getrlimit")}
        ok_f = ok_f and (info or {}).get("outcome") == "ok" and sf is True and ho == 0
    rec("f_single_flip_and_held_out_on_every_built_polynomial", ok_f, det_f)
    allok = all(c["pass"] for c in checks)
    infra_classes = {"refused_to_start", "crashed", "timeout", "memory_exhausted", "infrastructure_error"}
    infra = []
    for c in checks:
        if c["pass"]:
            continue
        d = c.get("detail") or {}
        outs = []
        if isinstance(d, dict):
            outs.append(d.get("outcome"))
            outs.append(((d.get("pari") or {}).get("child") or {}).get("outcome"))
            outs += [(v or {}).get("build_outcome") for v in d.values() if isinstance(v, dict)]
        if any(o in infra_classes for o in outs if o):
            infra.append(c["check"])
    cdir = os.path.join(ctx.rd, "certificates")
    cfiles = sorted(f for f in os.listdir(cdir) if f.endswith(".json"))
    cver = [json.load(open(os.path.join(cdir, f)))["independent_verification"]["pass"] for f in cfiles]
    status = "completed_valid" if allok else "failed"
    fclass = None if allok else ("infrastructure_error" if infra else "implementation_error")
    if cfiles and not all(cver):
        status, fclass = "invalid", "invalid_measurement"
    raw = {"kind": "controls_a1", "p": p, **_protocol_block(), "run_status": status, "failure_class": fclass, "gate_pass": allok,
           "checks": checks, "infrastructure_checks": infra,
           "metrics": {"n_checks": len(checks), "n_pass": sum(c["pass"] for c in checks), "wall_seconds": round(time.time() - t0, 1)},
           "certificate": ({"kind": "decomposition", "verified": all(cver), "count": len(cfiles),
                            "verifier": "experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py",
                            "note": "instrument-check certificates on planted m < n targets (k = 1, G := R); never degree evidence"}
                           if cfiles else {"kind": "none", "verified": None, "verifier": None, "note": "no certificate emitted"})}
    D.finish(ctx, raw, note="controls_a1 (blocking for the addendum; A1-2)")


# ============================================================================ build / cells: v2 code on the addendum plan
def cmd_build(args):
    ctx_pkg = C.plan_package(C.load_plan(), C.run_id())
    if ctx_pkg["kind"] == "contingency":
        ctx_pkg = C.plan_package(C.load_plan(), os.environ.get("GFPN_V2_REPLACES"))
    if int(ctx_pkg.get("p") or -1) != int(args.p):
        raise SystemExit("REFUSING: --p %s does not match the plan package's p %s" % (args.p, ctx_pkg.get("p")))
    D.cmd_build(args)


def cmd_cells(args):
    ctx_pkg = C.plan_package(C.load_plan(), C.run_id())
    if ctx_pkg["kind"] == "contingency":
        ctx_pkg = C.plan_package(C.load_plan(), os.environ.get("GFPN_V2_REPLACES"))
    if (int(ctx_pkg.get("p") or -1), ctx_pkg.get("shape"), int(ctx_pkg.get("m") or -1)) != (int(args.p), args.shape, int(args.m)):
        raise SystemExit("REFUSING: arguments do not match the plan package")
    D.cmd_cells(args)


# ============================================================================ aggregate_a1 (A1-5)
def _load_raw(rid):
    rp = os.path.join(C.EXP_DIR, "runs", rid, "raw-result.json")
    return (json.load(open(rp)), rp) if os.path.exists(rp) else (None, rp)


def _resolve(plan, rid):
    """contingency replacement resolved against the plan that RESERVED rid (v2 ids: trial-plan-v2.json)."""
    for pk in plan["packages"]:
        if pk["kind"] != "contingency":
            continue
        mp = os.path.join(C.EXP_DIR, "runs", pk["run_id"], "manifest.yaml")
        if os.path.exists(mp):
            import yaml
            man = yaml.safe_load(open(mp))["run"]
            if (man.get("package") or {}).get("replaces") == rid:
                return pk["run_id"]
    return rid


def phase_b_check(paths_read):
    """A1-5: v2 packages are read from their phase-B-archived bytes (TASK-20260923-0fa03f post-run receipt)."""
    if not os.path.exists(AC.RECEIPT_V2_PHASE_B):
        return {"status": "receipt_absent", "receipt": os.path.relpath(AC.RECEIPT_V2_PHASE_B, AC.REPO)}
    bound = AC.receipt_paths(AC.load_json(AC.RECEIPT_V2_PHASE_B))
    per, bad, unbound = [], [], []
    for ap in paths_read:
        rel = os.path.relpath(ap, AC.REPO)
        if rel not in bound:
            unbound.append(rel)
            continue
        ok = AC.sha256_file(ap) == bound[rel]
        per.append({"path": rel, "matches_receipt": ok})
        if not ok:
            bad.append(rel)
    return {"status": "mismatch" if bad else ("unbound_paths" if unbound else "verified"), "receipt": os.path.relpath(AC.RECEIPT_V2_PHASE_B, AC.REPO),
            "per_path": per, "mismatched": bad, "not_bound_by_receipt": unbound}


def cmd_aggregate_a1(args):
    ctx = D.Ctx()
    t0 = time.time()
    v2plan = AC.load_json(AC.V2_PLAN_PATH)
    a1plan = ctx.plan
    runs, sources, replaced, v2_paths = {}, {}, {}, []
    for rid0 in [r for r in args.v2_runs.split(",") if r]:
        rid = _resolve(v2plan, rid0)
        if rid != rid0:
            replaced[rid0] = rid
        raw, rp = _load_raw(rid)
        runs[rid], sources[rid] = raw, "v2"
        if raw is not None:
            v2_paths.append(rp)
    for rid0 in [r for r in args.a1_runs.split(",") if r]:
        rid = _resolve(a1plan, rid0)
        if rid != rid0:
            replaced[rid0] = rid
        runs[rid], sources[rid] = _load_raw(rid)[0], "addendum"
    v2agg, v2agg_path = _load_raw(args.v2_aggregate)
    if v2agg is not None:
        v2_paths.append(v2agg_path)
    pb = phase_b_check(v2_paths)
    # ---- rows, with the A1-4 reading label (never written into a v2 byte)
    rows, groups = [], {}
    for rid, r in runs.items():
        if not r or r.get("kind") != "cells":
            continue
        for cl in r["cells"]:
            row = D._ladder_row(cl)
            row.update(run=rid, source=sources[rid], reading_label=RD.reading_label(cl["p"], cl["curve_shape"]),
                       read_as_primary_shape=(cl["curve_shape"] == "ecgfp5_shaped" and not RD.is_off_shape(cl["p"], cl["curve_shape"])))
            rows.append(row)
            groups.setdefault((cl["curve_shape"], cl["p"], cl["m"], cl["target_kind"]), {})[cl["kind"]] = {
                int(k): v for k, v in ((cl.get("metrics") or {}).get("D_per_target") or {}).items()}
    cellD = {}
    for r in rows:
        if r["m"] == 5 and r["target_kind"] == "random" and r["reading_label"] != AC.OFF_SHAPE_LABEL and r["D"]:
            cellD.setdefault((r["arm"], r["curve_shape"]), {})[int(r["p"])] = r["D"]
    # ---- (v) every planned v2 and addendum cell with its terminal row (R-2)
    planned = []
    for plan, src in ((v2plan, "v2"), (a1plan, "addendum")):
        for pk in plan["packages"]:
            if pk["kind"] == "cells":
                for c in pk["cells"]:
                    planned.append((_resolve(plan, pk["run_id"]), c["arm"], pk["shape"], pk["p"], pk["m"], src))
    present = {(r["run"], r["arm"]) for r in rows}
    missing = [{"run": a, "arm": b, "shape": c, "p": d, "m": e, "source": s, "status": "not_attempted",
                "reason": "package not run or no row written (recorded here, never silently absent)",
                "reading_label": RD.reading_label(d, c)} for (a, b, c, d, e, s) in planned if (a, b) not in present]
    # ---- (i) primary-shape reading
    evalsets = RD.evaluate_all(cellD)
    primary_scoring = []
    for (shape, p, m, tk), g in sorted(groups.items()):
        if shape != "ecgfp5_shaped" or RD.is_off_shape(p, shape) or p not in RD.EVAL_SETS["ecgfp5_shaped"]["S"]:
            continue
        s = SC.score_like_for_like(g, m)
        s.update({"curve_shape": shape, "p": p, "m": m, "target_kind": tk, "reading_label": shape})
        primary_scoring.append(s)
    band = {"p_crypto": str(SC.P64), "label": "MODELED; not a security finding (EC-8)", "F3": SC.UNDECIDABLE_F3, "tail_check_2_36": SC.UNDECIDABLE_F3,
            "rule": "A1-3 band clause: emitted only if the arm's primary-shape heur_dflat_pass is TRUE under A1-3; v2_scoring.band_for_arm unchanged, fed only with primary-shape rows of S",
            "arms": {}}
    S_primary = RD.EVAL_SETS["ecgfp5_shaped"]["S"]
    for arm in RD.M5_ARMS_2T + ["raw"]:
        blk = evalsets["ecgfp5_shaped"][arm]
        kind = A.parse_arm(arm)[0]
        succ = att = 0
        for r in rows:
            if r["arm"] == arm and r["read_as_primary_shape"] and r["m"] == 5 and int(r["p"]) in S_primary and r["targets_measured"]:
                src = runs[r["run"]]
                for cl in src["cells"]:
                    if cl["arm"] == arm and cl.get("metrics"):
                        succ += cl["metrics"]["targets_with_verified_relation"]
                        att += cl["metrics"]["targets_measured"]
        Dmax = max(blk.get("D_per_prime", {}).values(), default=None) if blk.get("heur_dflat_pass") is True else None
        band["arms"][arm] = SC.band_for_arm(kind, blk, Dmax, succ, att)
    primary = {"shape": "ecgfp5_shaped", "rungs": S_primary,
               "cell_D_per_rung": {arm: {str(p): cellD.get((arm, "ecgfp5_shaped"), {}).get(p) for p in S_primary} for arm in RD.M5_ARMS_2T},
               "like_for_like_scoring": primary_scoring, "heur_dflat_A1_3": evalsets["ecgfp5_shaped"], "band_B3": band}
    # ---- (ii) control reading
    f4 = []
    for arm in RD.M5_ARMS_2T:
        for p in S_primary:
            De = cellD.get((arm, "ecgfp5_shaped"), {}).get(p)
            Dr = cellD.get((arm, "random_2torsion"), {}).get(p)
            f4.append({"arm": arm, "p": p, **(SC.matched_F4(De, Dr) if (De and Dr) else
                                             {"status": "not_applicable", "reason": "cell D not defined for both shapes at this rung"})})
    control = {"heur_dflat_A1_3": {"random_2torsion": evalsets["random_2torsion"], "random_no2torsion": evalsets["random_no2torsion"]},
               "matched_control_check_F4_at_primary_rungs": f4, "AA_4_matched_triple": RD.matched_triples(cellD)}
    # ---- (iii) off-shape descriptive section
    off = {"title": AC.OFF_SHAPE_TITLE, "label": AC.OFF_SHAPE_LABEL, "verdict": None,
           "rows": [r for r in rows if r["reading_label"] == AC.OFF_SHAPE_LABEL],
           "rule": "A1-4: run as planned and recorded as produced; never primary-shape rows; the b-square class mismatch refusals are construction-precondition refusals, never evidence about D"}
    # ---- (iv) reconciliation with the v2 aggregate
    recon = reconcile_v2_aggregate(v2agg, evalsets)
    data_ok = pb["status"] == "verified"
    status = "completed_valid" if data_ok else ("invalid" if pb["status"] == "mismatch" else "failed")
    fclass = None if data_ok else ("invalid_measurement" if pb["status"] == "mismatch" else "infrastructure_error")
    raw = {"kind": "aggregate", "aggregate_variant": "aggregate_a1", **_protocol_block(), "run_status": status, "failure_class": fclass,
           "v2_bytes_phase_B_check": pb, "runs": list(runs), "sources": sources, "replaced_packages": replaced,
           "missing_runs": [rid for rid, r in runs.items() if r is None], "v2_aggregate": args.v2_aggregate,
           "ladder_rows": rows,
           "section_i_primary_shape_reading": primary,
           "section_ii_control_reading": control,
           "section_iii_off_shape_descriptive": off,
           "section_iv_reconciliation_with_v2_aggregate": recon,
           "section_v_planned_cells_without_row": missing,
           "metrics": {"n_rows": len(rows), "n_planned_without_row": len(missing),
                       "heur_dflat_pass_A1_3": {sh: {a: v.get("heur_dflat_pass") for a, v in blk.items()} for sh, blk in evalsets.items() if isinstance(blk, dict) and sh != AC.OFF_SHAPE_LABEL},
                       "wall_seconds": round(time.time() - t0, 1)},
           "certificate": {"kind": "none", "verified": None, "verifier": None, "note": "aggregation; no new decomposition claimed"},
           "statement": "observations and comparison statistics only; no supported/refuted conclusion and no security level (EC-8)"}
    C.write_json(os.path.join(ctx.rd, "raw-result.json"), dict(raw, package=ctx.pkg, host=ctx.host, events=ctx.events, scoring_reference=SC.reference_block()))
    C.write_yaml(os.path.join(ctx.rd, "ladder-table.yaml"), {"ladder_table": {"rows": rows, "planned_cells_without_row": missing,
                                                                                 "primary_like_for_like_scoring": primary_scoring,
                                                                                 "matched_control_check_F4": f4}})
    C.write_yaml(os.path.join(ctx.rd, "heur-dflat.yaml"), {"heur_dflat_A1_3": evalsets, "AA_4_matched_triple": control["AA_4_matched_triple"]})
    C.write_yaml(os.path.join(ctx.rd, "cost-band-p64.yaml"), {"cost_band_p64": band})


def reconcile_v2_aggregate(v2agg, evalsets):
    """A1-5 (iv): every figure of RUN-GFPN-8f86cc reproduced, labelled 'as-planned (v2)'; figures using an off-shape row
    marked. Nothing in the v2 package is edited or superseded as a record."""
    if v2agg is None:
        return {"status": "v2 aggregate not available", "label": "as-planned (v2)"}
    OFF = "includes off-shape rung; not read for the primary shape"
    out = {"label": "as-planned (v2)", "source_run": "RUN-GFPN-8f86cc", "figures": {}}
    dfl = (v2agg.get("heur_dflat") or {}).get("arms", {})
    fd = {}
    for arm, shapes in dfl.items():
        for shape, blk in shapes.items():
            uses_off = shape == "ecgfp5_shaped" and "16777291" in (blk.get("D_per_prime") or {})
            e = {"figure": blk, "label": "as-planned (v2)"}
            if uses_off:
                e["mark"] = OFF
            if shape in ("random_2torsion", "random_no2torsion"):
                a13 = (evalsets.get(shape) or {}).get(arm) or {}
                trip = sorted(int(p) for p in (blk.get("D_per_prime") or {}))
                e["is_one_of_the_A1_3_eligible_triples"] = trip in [sorted(t) for t in a13.get("eligible_triples", [])] if len(trip) == 3 else False
            fd["%s|%s" % (arm, shape)] = e
    out["figures"]["heur_dflat"] = fd
    lfl = []
    for s in v2agg.get("like_for_like_scoring") or []:
        e = {"figure": s, "label": "as-planned (v2)"}
        if RD.is_off_shape(s.get("p"), s.get("curve_shape")):
            e["mark"] = OFF
        lfl.append(e)
    out["figures"]["like_for_like_scoring"] = lfl
    f4 = []
    for s in v2agg.get("matched_control_check_F4") or []:
        e = {"figure": s, "label": "as-planned (v2)"}
        if int(s.get("p", 0)) == 16777291:
            e["mark"] = OFF
        f4.append(e)
    out["figures"]["matched_control_check_F4"] = f4
    band = (v2agg.get("cost_band") or {}).get("arms", {})
    out["figures"]["cost_band"] = {arm: {"figure": b, "label": "as-planned (v2)",
                                         **({"mark": OFF} if "16777291" in ((dfl.get(arm) or {}).get("ecgfp5_shaped", {}).get("D_per_prime") or {}) else {})}
                                   for arm, b in band.items()}
    lr = []
    for r in v2agg.get("ladder_rows") or []:
        e = dict(r, reproduced_label="as-planned (v2)", reading_label=RD.reading_label(r.get("p", 0), r.get("curve_shape")))
        lr.append(e)
    out["figures"]["ladder_rows"] = lr
    out["figures"]["planned_cells_without_row"] = v2agg.get("planned_cells_without_row")
    out["figures"]["metrics"] = {"figure": v2agg.get("metrics"), "label": "as-planned (v2)"}
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("controls-a1")
    a.add_argument("--p", type=int, required=True)
    b = sub.add_parser("build")
    b.add_argument("--p", type=int, required=True)
    c = sub.add_parser("cells")
    c.add_argument("--p", type=int, required=True)
    c.add_argument("--shape", required=True)
    c.add_argument("--m", type=int, required=True)
    c.add_argument("--prior-run", default=None)
    g = sub.add_parser("aggregate-a1")
    g.add_argument("--a1-runs", required=True)
    g.add_argument("--v2-runs", required=True)
    g.add_argument("--v2-aggregate", required=True)
    args = ap.parse_args()
    {"controls-a1": cmd_controls_a1, "build": cmd_build, "cells": cmd_cells, "aggregate-a1": cmd_aggregate_a1}[args.cmd](args)


if __name__ == "__main__":
    main()
