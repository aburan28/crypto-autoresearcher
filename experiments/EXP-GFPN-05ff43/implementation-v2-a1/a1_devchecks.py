#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2-a1 -- STAGE-1B DEVELOPMENT CHECKS (addendum A1-7 (a)-(f); card S1B-5).

usage: python3 -B a1_devchecks.py {a,c,d,e,f} --out SCRATCH_DIR

Development checks create NO run package and report NO number as a result. Every output goes to
SCRATCH_DIR (the session scratchpad), never under experiments/. Every msolve / PARI / builder child runs
under v2_solver.run_child (RLIMIT_AS set in the child and read back with getrlimit; one at a time; -t 1).
Check (b) is a1_health.py's own CLI (run at 1073741831 and, for AA-3, at 16777291).

  c  PARI ellcard recheck of the three 31-bit orders and the norm-criterion class of b (parameter verification).
  d  flint (v2_field) and pure-Python (v2_verify_independent) arithmetic at p' = 1073741831 on SYNTHETIC
     PLANTED relations (no solver): group-law agreement, positive certificates for every factor-base kind,
     relation_mod_T, and the verifier's negative cases.
  e  a1_run_wrapper.py refusal dry-runs: every A-1..A-12 refusal, including unreserved / v1 / v2 ids, watchdog
     mismatch, uncommitted trees and the shared 48 ceiling; nothing may be written.
  f  confirmation that no v1 or v2 stream key uses p' = 1073741831 (source and plan text search).
  a  toy-ladder integration: plan, ladder and runs redirected to SCRATCH_DIR; controls_a1 -> build -> cells ->
     aggregate_a1 through a1_run_wrapper.py at a TOY prime (never a ladder prime), with synthetic v2 rows at the
     v2 primes; the A1-3 triple logic on synthetic 3- and 4-rung inputs; the AA-4 figure; the A1-4 labels;
     a1_check_run.py on every toy package.
NO ladder curve, cell system or fixture system is solved at ANY prime by any of these checks.
"""
import argparse
import copy
import json
import os
import random
import re
import shutil
import sys

sys.dont_write_bytecode = True
import a1_common as AC                                   # noqa: E402

TOY_P = 1021          # toy characteristic for check (a); 1021 = 1 mod 5; not a ladder prime


def _dump(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


# ============================================================================ (c)
def dev_c(out):
    import a1_pari as P
    lad = [r for r in AC.load_json(AC.LADDER_PATH) if r["p"] == AC.P_RUNG31][0]
    p = lad["p"]
    mod = [(-lad["cmod"]) % p, 0, 0, 0, 0, 1]
    curves = [dict(label=s, a2=lad["curves"][s]["a2"], a4=lad["curves"][s]["a4"], a6=lad["curves"][s]["a6"],
                   cofactor=lad["curves"][s]["cofactor"]) for s in AC.SHAPES]
    r = P.curve_facts(p, mod, curves, os.path.join(out, "pari"), "pari_31bit")
    r["gp_version"] = P.gp_version()
    cmp = {}
    for s in AC.SHAPES:
        f, cv = r["curves"][s], lad["curves"][s]
        d = {"ellcard_equals_ladder_order": f.get("N") == int(cv["order"]), "N_mod_4": f.get("N_mod_4"), "cofactor_ladder": cv["cofactor"],
             "N_over_cofactor_equals_ladder_subgroup_prime": f.get("N") is not None and f["N"] // cv["cofactor"] == int(cv["subgroup_prime"]),
             "N_over_cofactor_isprime_PARI": f.get("N_over_h_isprime") == 1, "rational_2torsion_roots": f.get("rational_2torsion_roots"),
             "b_is_square_by_norm_criterion": f.get("b_is_square_in_Fq_by_norm_criterion"), "ladder_b_is_square_in_Fq": cv.get("b_is_square_in_Fq"),
             "norm_pari_equals_pure_python": f.get("norm_b_agrees_pari_vs_pure_python")}
        if s != "random_no2torsion":
            d["double_odd_facts"] = f.get("N_mod_4") == 2 and cv["cofactor"] == 2 and f.get("b_is_square_in_Fq_by_norm_criterion") is False
        cmp[s] = d
    r["comparison_with_ladder_json"] = cmp
    ok = r["complete"] and all(d["ellcard_equals_ladder_order"] and d["N_over_cofactor_isprime_PARI"] for d in cmp.values()) \
        and cmp["ecgfp5_shaped"]["double_odd_facts"] and cmp["random_2torsion"]["double_odd_facts"] and cmp["random_no2torsion"]["rational_2torsion_roots"] == 0
    r["pass"] = ok
    _dump(os.path.join(out, "devcheck_c.json"), r)
    print(json.dumps(cmp, indent=1))
    print("child:", r["child"])
    print("DEV CHECK (c): %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


# ============================================================================ (d)
def dev_d(out):
    C = AC.redirect_v2()
    import v2_arms as A
    import v2_lift as L
    import v2_verify_independent as VI
    p = AC.P_RUNG31
    rung = C.ladder_entry(p)
    F = C.ladder_field(rung)
    rng = random.Random("stage1b-dev:d:%d" % p)
    checks = []

    def rec(name, ok, detail=None):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        print(name, "PASS" if ok else "FAIL")

    def conv(P):
        return None if P is None else (tuple(F.coeffs(P[0])), tuple(F.coeffs(P[1])))

    Fi = VI.FqP(p, F.modulus)
    for shape in AC.SHAPES:
        E, cv = C.ladder_curve(F, rung, shape)
        Ei = VI.CurveP(Fi, F.coeffs(E.a2), F.coeffs(E.a4), F.coeffs(E.a6))
        agree, n = True, 0
        for _ in range(4):
            P1, P2 = E.random_point(rng), E.random_point(rng)
            k = rng.randrange(1, 1 << 80)
            agree &= Ei.on_curve(conv(P1)) and Ei.on_curve(conv(P2))
            agree &= conv(E.add(P1, P2)) == Ei.add(conv(P1), conv(P2))
            agree &= conv(E.add(P1, P1)) == Ei.add(conv(P1), conv(P1))
            agree &= conv(E.mul(k, P1)) == Ei.mul(k, conv(P1))
            n += 3
        Pr = E.random_point(rng)
        order_ok = Ei.mul(int(cv["order"]), conv(Pr)) is None and E.mul(int(cv["order"]), Pr) is None
        rec("group_law_flint_equals_pure_python_%s" % shape, agree and order_ok, {"operations_compared": n, "N_times_random_point_is_O": order_ok})
        if E.a6 == 0:
            nrm = Fi.pow(Fi.norm(F.coeffs(E.a4)), (p ** 5 - 1) // (p - 1))
            leg = 1 if pow(nrm[0], (p - 1) // 2, p) == 1 else -1
            rec("is_square_flint_equals_norm_criterion_pure_python_%s" % shape, F.is_square(E.a4) == (leg == 1),
                {"flint_is_square": F.is_square(E.a4), "norm_legendre": leg})
    # planted relations on the ecgfp5_shaped and random_2torsion 31-bit curves, every factor-base kind; no solver
    good = {}
    for shape in ("ecgfp5_shaped", "random_2torsion"):
        E, cv = C.ladder_curve(F, rung, shape)
        rs = A.rescaling(E)
        nsub = int(cv["subgroup_prime"])
        lam = rs["lam_obj"]
        lam2beta = Fi.mul(Fi.mul(tuple(F.coeffs(lam)), tuple(F.coeffs(lam))), (rs["beta"], 0, 0, 0, 0)) == tuple(F.coeffs(E.a4))
        rec("rescaling_lam2_beta_equals_b_pure_python_%s" % shape, lam2beta and rs["beta_is_nonsquare_in_Fp"], A.public_rescaling(rs))
        pools = {"S": A.pool_x(E, 200), "S_rescaled": A.pool_u(E, lam, 200), "rq": A.pool_u(E, lam, 200), "norm": A.pool_t(E, 200)}
        for arm in ("S3", "S3_rescaled", "torsion_S3_rq", "torsion_S3_norm"):
            kind, _ = A.parse_arm(arm)
            prng = random.Random("stage1b-dev:d:planted:%d:%s:%s" % (p, shape, arm))
            found = None
            for _ in range(400):
                pool = pools[kind]
                sel = prng.sample(sorted(pool) if isinstance(pool, dict) else pool, 3)
                if kind == "S":
                    pts = [E.lift_x(F(x)) for x in sel]
                elif kind == "norm":
                    pts = [E.lift_x(pool[t]) for t in sel]
                else:
                    pts = [E.lift_x(lam * F(u)) for u in sel]
                if any(P is None for P in pts):
                    continue
                signs = [prng.choice((1, -1)) for _ in pts]
                R = None
                for P, s in zip(pts, signs):
                    R = E.add(R, P if s == 1 else E.neg(P))
                if R is not None and E.mul(nsub, R) is None:
                    found = (sel, pts, signs, R)
                    break
            if found is None:
                rec("planted_relation_found_%s_%s" % (shape, arm), False)
                continue
            sel, pts, signs, R = found
            rel = {"points": pts, "signs": signs, "relation_mod_T": False, "u_values": list(sel) if A.base_of(kind) == "x_over_lam_in_Fp" else None}
            cert = L.make_certificate(F, cv, shape, arm, kind, 3, rs if A.base_of(kind) == "x_over_lam_in_Fp" else None, nsub, R, 1, R, rel,
                                      "stage1b-dev-no-run-package", "planted", 0, "planted_instrument_check_m_lt_n")
            ok, npts, reasons = VI.verify(cert)
            rec("planted_certificate_verifies_%s_%s" % (shape, arm), ok, {"reasons": reasons, "lifted_points": npts})
            good[(shape, arm)] = (cert, rs)

    def neg(name, cert, expect):
        ok, _, reasons = VI.verify(cert)
        rec("verifier_rejects_%s" % name, (not ok) and any(expect in r for r in reasons), {"reasons": reasons})

    for (shape, arm), (cert, rs) in good.items():
        tag = "%s_%s" % (shape, arm)
        c1 = copy.deepcopy(cert); c1["k"] = cert["k"] + 1
        neg("wrong_scalar_" + tag, c1, "R != [k]G")
        c2 = copy.deepcopy(cert); c2["signs"] = [-s for s in cert["signs"]]
        neg("flipped_signs_" + tag, c2, "sum of signed points")
        c4 = copy.deepcopy(cert); del c4["relation_mod_T"]
        neg("missing_relation_mod_T_" + tag, c4, "relation_mod_T field missing")
        if cert["factor_base"]["kind"] == "x_over_lam_in_Fp":
            for fld in ("beta", "lam", "u_values"):
                c5 = copy.deepcopy(cert); del c5["factor_base"][fld]
                neg("missing_%s_%s" % (fld, tag), c5, "factor_base.%s missing" % fld)
            c6 = copy.deepcopy(cert); c6["factor_base"]["beta"] = 1
            neg("square_beta_at_odd_n_" + tag, c6, "non-square")
            c7 = copy.deepcopy(cert); c7["factor_base"]["lam"] = [(v + 1) % p for v in cert["factor_base"]["lam"]]
            neg("wrong_lam_" + tag, c7, "lam^2 * beta != b")
        if arm.startswith("torsion"):
            c8 = copy.deepcopy(cert); c8["curve"]["a6"] = [1, 0, 0, 0, 0]
            neg("torsion_certificate_on_curve_without_2torsion_" + tag, c8, "no rational 2-torsion")
            # relation_mod_T: shift point 0 by T = (0, 0); accepted with the flag, rejected without it
            E, _ = C.ladder_curve(F, rung, shape)
            P0 = (F.from_coeffs(cert["points"][0][0]), F.from_coeffs(cert["points"][0][1]))
            P0T = E.add(P0, (F.zero, F.zero))
            cm = copy.deepcopy(cert)
            cm["points"][0] = [F.coeffs(P0T[0]), F.coeffs(P0T[1])]
            if cm["factor_base"]["kind"] == "x_over_lam_in_Fp":
                cm["factor_base"]["u_values"][0] = F.coeffs(P0T[0] / rs["lam_obj"])[0]
            cm["relation_mod_T"] = True
            okm, _, rm = VI.verify(cm)
            rec("verifier_accepts_relation_mod_T_" + tag, okm, {"reasons": rm})
            cn = copy.deepcopy(cm); cn["relation_mod_T"] = False
            neg("R_plus_T_without_flag_" + tag, cn, "sum of signed points != R")
        else:
            c9 = copy.deepcopy(cert); c9["relation_mod_T"] = True
            neg("relation_mod_T_on_non_T_arm_" + tag, c9, "not a T-quotient arm")
    # refusals: rq on the curve without rational 2-torsion
    E_no, _ = C.ladder_curve(F, rung, "random_no2torsion")
    r_no = A.rescaling(E_no)
    rec("rq_refuses_random_no2torsion_31bit", r_no["refused"] and r_no["reason"] == "no rational 2-torsion", A.public_rescaling(r_no))
    ok = all(c["pass"] for c in checks)
    _dump(os.path.join(out, "devcheck_d.json"), {"p": p, "solver_used": False, "checks": checks, "pass": ok})
    print("DEV CHECK (d): %s (%d/%d)" % ("PASS" if ok else "FAIL", sum(c["pass"] for c in checks), len(checks)))
    return 0 if ok else 1


# ============================================================================ (f)
def dev_f(out):
    exp = AC.EXP_DIR
    srcs = {"v1_code": sorted(os.path.join(exp, "implementation", f) for f in os.listdir(os.path.join(exp, "implementation")) if f.endswith(".py")),
            "v1_plan": [os.path.join(exp, "trial-plan.json")],
            "v1_ladder": [AC.LADDER_PATH],
            "v2_code": sorted(os.path.join(exp, "implementation-v2", f) for f in os.listdir(os.path.join(exp, "implementation-v2")) if f.endswith(".py")),
            "v2_plan": [AC.V2_PLAN_PATH]}
    hits = {}
    for fam, files in srcs.items():
        for f in files:
            for i, line in enumerate(open(f, errors="replace"), 1):
                if "1073741831" in line:
                    hits.setdefault(fam, []).append({"file": os.path.relpath(f, AC.REPO), "line": i, "text": line.strip()[:200]})
    stream_patterns = {}
    for fam in ("v1_code", "v2_code"):
        pats = set()
        for f in srcs[fam]:
            for line in open(f, errors="replace"):
                for m in re.finditer(r"random\.Random\((f?[\"'][^\"']*[\"'](?:\s*%\s*\([^)]*\))?)", line):
                    pats.add(m.group(1))
        stream_patterns[fam] = sorted(pats)
    v2 = AC.load_json(AC.V2_PLAN_PATH)
    v2_primes = sorted({int(a) for pk in v2["packages"] for i, a in enumerate(pk.get("driver_args") or []) if i > 0 and pk["driver_args"][i - 1] == "--p"}
                       | {int(pk["p"]) for pk in v2["packages"] if pk.get("p")})
    v1 = AC.load_json(os.path.join(exp, "trial-plan.json"))
    a1_streams = ["2026092001:v2:targets:1073741831:%s" % s for s in AC.SHAPES] + \
                 ["2026092002:v2:basepoint:1073741831:%s" % s for s in AC.SHAPES] + \
                 ["2026092002:v2:build:1073741831:", "2026092002:v2:grid:1073741831:", "2026092001:v2a1:", "2026092002:v2a1:"]
    a1_in_sources = {s: [os.path.relpath(f, AC.REPO) for fam, files in srcs.items() for f in files if s in open(f, errors="replace").read()] for s in a1_streams}
    v2_stream_primes = {"trial_plan_v2_primes_passed_to_the_driver": v2_primes,
                        "v2_driver_cmd_controls_literal_primes": [4111, 262151, 16777291],
                        "v2_fixture_primes": [4111, 16777291]}
    v2_ok = AC.P_RUNG31 not in v2_primes and not hits.get("v2_code") and not hits.get("v2_plan")
    v1_hits_are_selection_only = all(("ladder" in h["text"] or '"p": 1073741831' in h["text"] or "seed_stream" in h["text"] or "field" in h["text"])
                                     for h in hits.get("v1_ladder", [])) and not hits.get("v1_code")
    res = {"literal_1073741831_occurrences": hits, "stream_constructors": stream_patterns, "v2_stream_primes": v2_stream_primes,
           "v1_trial_plan_31bit_entries": [x for x in json.dumps(v1).split("{") if "1073741831" in x],
           "addendum_stream_strings_in_v1_v2_sources": a1_in_sources,
           "observations": {
               "v2": "no v2 source or plan contains 1073741831; every v2 stream is keyed by a prime passed from trial-plan-v2.json or a literal in {4111, 262151, 16777291}: %s" % v2_ok,
               "v1": ("v1 code contains no literal 1073741831; v1 streams are keyed by the prime they are called with. The v1 ladder file records the "
                      "rung's CURVE-SELECTION stream random.Random('2026092002:ladder:1073741831') (ladder_select.py line 84), which selected the "
                      "three frozen curves; v1 trial-plan.json lists the rung as 'selected_unused'. That selection stream is not a target, "
                      "basepoint, build, grid, fixture or control stream, and no v2-a1 stream string equals it (every v2-a1 string carries ':v2:' or ':v2a1:')."),
               "v1_run_packages": "not read (card S1B-8); v1 implementation.md line 245 records the 31-bit rung 'selected but never used'"},
           "addendum_streams_absent_from_v1_v2_sources": all(not v for v in a1_in_sources.values())}
    res["pass"] = v2_ok and v1_hits_are_selection_only and res["addendum_streams_absent_from_v1_v2_sources"]
    _dump(os.path.join(out, "devcheck_f.json"), res)
    print(json.dumps({k: res[k] for k in ("literal_1073741831_occurrences", "addendum_streams_absent_from_v1_v2_sources")}, indent=1))
    print("DEV CHECK (f): %s" % ("PASS" if res["pass"] else "FAIL"))
    return 0 if res["pass"] else 1


# ============================================================================ (e)
def dev_e(out):
    import a1_run_wrapper as W
    import v2_solver as V
    real = {k: getattr(AC, k) for k in ("PLAN_A1_PATH", "V2_PLAN_PATH", "ADDENDUM_PATH", "V2_AMENDMENT_PATH", "RECEIPT_V2_PHASE_A", "RECEIPT_A1_PHASE_A")}
    real_runs, real_git, real_other = W.RUNS, W.git_tree_state, V.other_solver_processes
    plan = AC.load_json(AC.PLAN_A1_PATH)
    ids = [p["run_id"] for p in plan["packages"]]
    controls, build_id, cell1 = ids[0], ids[1], ids[2]
    cont1, cont2 = ids[9], ids[10]
    sd = os.path.join(out, "e_scratch")
    os.makedirs(sd, exist_ok=True)

    def listing():
        """Top-level names of runs/ only (S1B-8: nothing inside a run directory is read), plus every file of the
        addendum's own paths with its mtime."""
        snap = {os.path.join(AC.RUNS_DIR, d): "entry" for d in os.listdir(AC.RUNS_DIR)}
        for dp, _dn, fn in os.walk(AC.HERE):
            snap[dp] = "dir"
            for f in fn:
                fp = os.path.join(dp, f)
                snap[fp] = os.path.getmtime(fp)
        for fp in (real["PLAN_A1_PATH"], os.path.join(AC.EXP_DIR, "implementation-v2-a1.md")):
            snap[fp] = os.path.getmtime(fp) if os.path.exists(fp) else "absent"
        return snap

    def restore():
        for k, v in real.items():
            setattr(AC, k, v)
        W.RUNS, W.git_tree_state, V.other_solver_processes = real_runs, real_git, real_other

    results = []

    def case(name, rid, expect, replaces=None, setup=None):
        restore()
        if setup:
            setup()
        before = listing()
        existed = os.path.exists(os.path.join(real_runs, rid))
        refusals, _info = W.preflight(rid, replaces)
        rc = W.main([rid] + (["--replaces", replaces] if replaces else []) + ["--dry-run"]) if refusals else None
        after = listing()
        restore()
        hit = [r for r in refusals if expect in r]
        wrote = sorted(set(after) - set(before)) + sorted(k for k in before if k in after and before[k] != after[k])
        ok = bool(hit) and rc == 2 and not wrote and (existed or not os.path.exists(os.path.join(real_runs, rid)))
        results.append({"case": name, "run_id": rid, "replaces": replaces, "expected_substring": expect, "matched": hit, "exit": rc,
                        "all_refusals": refusals, "bytes_written": wrote, "pass": ok})
        print("%-58s %s" % (name, "REFUSED as expected, nothing written" if ok else "UNEXPECTED: %s" % refusals))

    # --- fixtures for redirected cases (all in scratch)
    def scratch_plan(mut, name):
        pth = os.path.join(sd, name)
        d = copy.deepcopy(plan)
        mut(d)
        _dump(pth, d)
        return pth

    wd_bad = scratch_plan(lambda d: d["watchdogs"]["per_arm_m"]["S5|m5"].__setitem__("per_target_timeout_s", 43201), "plan_watchdog_mismatch.json")
    meta_bad = scratch_plan(lambda d: d.__setitem__("protocol_version", 2), "plan_wrong_protocol_version.json")
    big = scratch_plan(lambda d: (d.__setitem__("package_count", 30),
                                  d["packages"].extend({"label": "synthetic %d" % i, "kind": "cells", "run_id": "RUN-GFPN-f%05x" % i, "requires": [],
                                                        "order": 12 + i, "gate_required": False} for i in range(19))), "plan_ceiling.json")
    add_bad = os.path.join(sd, "addendum_altered.yaml")
    shutil.copy(AC.ADDENDUM_PATH, add_bad)
    with open(add_bad, "a") as fh:
        fh.write("# altered copy for dev check (e)\n")
    rc_bad = os.path.join(sd, "receipt_v2_altered.json")
    r = AC.load_json(AC.RECEIPT_V2_PHASE_A)
    k0 = sorted(r["path_sha256"])[0]
    r["path_sha256"][k0] = "0" * 64
    _dump(rc_bad, r)
    a1_files = sorted(os.path.relpath(os.path.join(dp, f), AC.REPO) for dp, _dn, fn in os.walk(AC.HERE) for f in fn)
    rc_a1 = os.path.join(sd, "receipt_a1_synthetic_mismatch.json")
    _dump(rc_a1, {"synthetic": "dev check (e) only", "path_sha256": {**{f: "0" * 64 for f in a1_files},
                                                                     AC.A1_PATHS_REL[1]: "0" * 64, AC.A1_PATHS_REL[2]: "0" * 64}})

    def runs_dir(name, dirs, raws=None, manifests=None):
        base = os.path.join(sd, name)
        if os.path.exists(base):
            shutil.rmtree(base)
        os.makedirs(base)
        for d in dirs:
            os.makedirs(os.path.join(base, d), exist_ok=True)
        for rid, raw in (raws or {}).items():
            os.makedirs(os.path.join(base, rid), exist_ok=True)
            _dump(os.path.join(base, rid, "raw-result.json"), raw)
        for rid, man in (manifests or {}).items():
            os.makedirs(os.path.join(base, rid), exist_ok=True)
            import yaml
            with open(os.path.join(base, rid, "manifest.yaml"), "w") as fh:
                yaml.safe_dump({"run": man}, fh)
        return base

    v2 = AC.load_json(AC.V2_PLAN_PATH)
    v2ids = [p["run_id"] for p in v2["packages"]]
    gates_ok = {g: {"run_status": "completed_valid", "gate_pass": True} for g in AC.V2_GATE_PACKAGES}
    gates_bad = dict(gates_ok, **{AC.V2_GATE_PACKAGES[2]: {"run_status": "failed", "gate_pass": False}})
    runs_gate_bad = runs_dir("runs_v2_gate_failed", [], gates_bad)
    runs_ctl_bad = runs_dir("runs_controls_failed", [], dict(gates_ok, **{controls: {"run_status": "failed", "gate_pass": False}}))
    runs_exists = runs_dir("runs_dir_exists", [controls])
    runs_ceiling = runs_dir("runs_ceiling", v2ids + ids[:6] + ["RUN-GFPN-f%05x" % i for i in range(11)])
    runs_cont = runs_dir("runs_contingency", [], gates_ok, {cell1: {"failure_class": "resource_exhaustion"}, build_id: {"failure_class": "infrastructure_error"},
                                                            cont2: {"package": {"replaces": build_id}, "failure_class": None}})

    def setp(**kw):
        def f():
            for k, v in kw.items():
                if k == "RUNS":
                    W.RUNS = v
                elif k == "git":
                    W.git_tree_state = v
                elif k == "other":
                    V.other_solver_processes = v
                else:
                    setattr(AC, k, v)
        return f

    def git_v2_dirty(paths):
        tr, dirty = real_git(paths)
        if paths == AC.V2_PATHS_REL:
            return tr, [" M experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py (SIMULATED by dev check (e); no byte written)"]
        return tr, dirty

    case("A-2 unreserved id", "RUN-GFPN-000000", "not reserved in trial-plan-v2-a1.json")
    case("A-2 v1 id (RUN-GFPN-61bba9)", "RUN-GFPN-61bba9", "is a v1 run id")
    case("A-2 v1 id never run (RUN-GFPN-bb78e5)", "RUN-GFPN-bb78e5", "is a v1 run id")
    case("A-2 v2 id (gate RUN-GFPN-ac4487)", "RUN-GFPN-ac4487", "is a v2 run id")
    case("A-2 v2 contingency id (RUN-GFPN-e26e4b)", "RUN-GFPN-e26e4b", "is a v2 run id")
    case("A-5 uncommitted addendum tree (real state)", controls, "not all committed")
    case("A-5 addendum phase-A receipt absent (real state)", controls, "phase-A receipt absent")
    case("A-8 watchdog mismatch", controls, "A-8 watchdog", setup=setp(PLAN_A1_PATH=wd_bad))
    case("A-10 shared 48 ceiling", ids[6], "A-10 shared ceiling", setup=setp(PLAN_A1_PATH=big, RUNS=runs_ceiling))
    case("A-1 addendum sha256 mismatch", controls, "A-1 addendum sha256 mismatch", setup=setp(ADDENDUM_PATH=add_bad))
    case("A-3 run directory exists", controls, "A-3 run directory exists", setup=setp(RUNS=runs_exists))
    case("A-4 v2 bytes differ from the 0fa03f receipt", controls, "differ from the TASK-20260923-0fa03f", setup=setp(RECEIPT_V2_PHASE_A=rc_bad))
    case("A-4 v2 tree dirty (simulated git state)", controls, "A-4 v2 paths are dirty", setup=setp(git=git_v2_dirty))
    case("A-5 addendum bytes differ from the 4ff597 receipt", controls, "differ from the TASK-20260923-4ff597", setup=setp(RECEIPT_A1_PHASE_A=rc_a1))
    case("A-6 v2 gate package not run (real state)", controls, "A-6 v2 gate package RUN-GFPN-ac4487 has not run")
    case("A-6 v2 gate package failed", controls, "did not pass", setup=setp(RUNS=runs_gate_bad))
    case("A-6 controls_a1 not run", build_id, "A-6 controls_a1")
    case("A-6 controls_a1 failed", build_id, "A-6 controls_a1 %s did not pass" % controls, setup=setp(RUNS=runs_ctl_bad))
    case("A-7 predecessor has no manifest", cell1, "A-7 required earlier package")
    case("A-9 another solver-like process (simulated scan result)", controls, "A-9 another solver-like process",
         setup=setp(other=lambda own_pids=(): [{"pid": 0, "argv0": "msolve", "cmdline": "SIMULATED by dev check (e)"}]))
    case("A-11 contingency without --replaces", cont1, "must name the package it replaces")
    case("A-11 contingency replacing the blocking controls_a1", cont1, "never replaced", replaces=controls, setup=setp(RUNS=runs_cont))
    case("A-11 contingency replacing a resource_exhaustion package", cont1, "only an infrastructure_error package", replaces=cell1, setup=setp(RUNS=runs_cont))
    case("A-11 contingency replacing a v2 package", cont1, "planned, non-contingency ADDENDUM package", replaces="RUN-GFPN-0c7483")
    case("A-11 package already replaced once", cont1, "already replaced once", replaces=build_id, setup=setp(RUNS=runs_cont))
    case("A-11 --replaces on a non-contingency id", build_id, "--replaces is only valid", replaces=cell1)
    case("A-12 plan metadata wrong", controls, "A-12 the plan does not record", setup=setp(PLAN_A1_PATH=meta_bad))
    restore()
    ok = all(r["pass"] for r in results)
    _dump(os.path.join(out, "devcheck_e.json"), {"cases": results, "pass": ok,
                                                 "note": "every case evaluated through a1_run_wrapper.preflight() and main(--dry-run); redirections are in-process and point at scratch copies; nothing under experiments/ was written"})
    print("DEV CHECK (e): %s (%d/%d cases)" % ("PASS" if ok else "FAIL", sum(r["pass"] for r in results), len(results)))
    return 0 if ok else 1


# ============================================================================ (a)
from a1_toy import dev_a                                  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("check", choices=["a", "c", "d", "e", "f"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out.startswith(AC.EXP_DIR):
        raise SystemExit("REFUSING: development outputs never go under experiments/")
    os.makedirs(out, exist_ok=True)
    return {"a": dev_a, "c": dev_c, "d": dev_d, "e": dev_e, "f": dev_f}[a.check](out)


if __name__ == "__main__":
    sys.exit(main())
