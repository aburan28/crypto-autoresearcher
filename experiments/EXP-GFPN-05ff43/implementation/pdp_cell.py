#!/usr/bin/env python3
"""EXP-GFPN-05ff43 driver.  Every subcommand runs under run_wrapper.py and writes
raw-result.json + ladder-table.yaml + heur-dflat.yaml + cost-band-p64.yaml into
$GFPN_RUN_DIR (certificates/ for accepted decompositions).

Subcommands
  validate                       instrument checks (evaluator cross-check, identity control, planted lifts,
                                 verifier negative tests) -- certificate.kind none
  anchor  --p P --shape S        n=4 (m=4, S_5) Joux-Vitse decomposition-test timing anchor (C-6)
  build   --p P                  construct all arm polynomials at prime P (m=5 and m=4), cached + hashed
  cell    --p P --shape S --arm A --m M [--targets N] [--target-timeout T] [--cell-watchdog W]
  raw     --p P --shape S --m M [--targets N] ...     arm (i), grid-interpolated raw system
  aggregate --runs RUN-ID,...    ladder table, HEUR-GFPN-DFLAT decision, cost band at p = 2^64
"""
import argparse, json, os, random, sys, time, glob
import numpy as np
import flint
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfpn5_core import Fq, Curve, S_poly_grp, S_poly_res, S_num_res, poly_eval, self_test as core_self_test
from symmetrize import *
from pdp_common import *
import verify_independent

MEM_CAP_GB = float(os.environ.get("GFPN_MEM_CAP_GB", "12"))
# Cap on how many factor-base x-values (resp. phi-coordinates t) are ENUMERATED to draw
# interpolation sample points from. This is an implementation limit on the sampling
# source, not a change to the factor base: the factor-base condition tested when a
# solution is lifted, and again when a certificate is re-verified, is "x in F_p" (resp.
# "x + b/x in F_p") over the whole field, never membership in this enumerated prefix.
# Without it, building the pool at the 25-bit rung scans 16.7M field elements.
POOL_LIMIT = int(os.environ.get("GFPN_POOL_LIMIT", "4000"))
THREADS = int(os.environ.get("GFPN_MSOLVE_THREADS", "4"))
flint.ctx.threads = 4
VARS = {5: ["e1", "e2", "e3", "e4", "e5"], 4: ["e1", "e2", "e3", "e4"], 3: ["e1", "e2", "e3"]}
XVARS = {5: ["x1", "x2", "x3", "x4", "x5"], 4: ["x1", "x2", "x3", "x4"], 3: ["x1", "x2", "x3"]}

def solvable_targets(E, cv, p, shape, arm, m, pool, T, count, n_sub):
    """Constructed-decomposable known-scalar targets (see module note).

    Returns [(i, k, R, G, n, planted_xs)] with R = [k]G, k = 1, G = R, [n]G = O.
    The planted points are used only to DEFINE the target; the solver is given
    nothing but the specialised system.
    """
    F = E.F
    out = []
    keys = sorted(pool) if isinstance(pool, dict) else list(pool)
    for i in range(count):
        rng = random.Random(f"{SEED_TARGETS}:solvable:{p}:{shape}:{arm}:{m}:{i}")
        for _ in range(500):
            sel = rng.sample(keys, m)
            pts = [E.lift_x(F(x)) for x in sel] if not isinstance(pool, dict) else [E.lift_x(pool[tv]) for tv in sel]
            S = None
            for Pt in pts:
                S = E.add(S, Pt)
            if S is None:
                continue
            if E.mul(n_sub, S) is not None:      # not in the prime-order subgroup
                continue
            out.append((i, 1, S, S, n_sub, sel))
            break
        else:
            log(f"solvable target {i}: no planted sum landed in the prime-order subgroup in 500 tries")
    return out

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)

def finish(rd, raw):
    json.dump(raw, open(os.path.join(rd, "raw-result.json"), "w"), indent=1, default=str)

def common_params(p, rung, shape, cv):
    return {"p": p, "p_bits": p.bit_length(), "field_bits": 5 * p.bit_length(), "cmod": rung["cmod"], "field": rung["field"],
            "extension_degree": 5, "curve_shape": shape, "curve_model": cv["model"] if cv else None,
            "a2": cv["a2"] if cv else None, "a4": cv["a4"] if cv else None, "a6": cv["a6"] if cv else None,
            "order": cv["order"] if cv else None, "cofactor": cv["cofactor"] if cv else None,
            "solver": "msolve 0.6.5 (F4 + FGLM/rational parametrization), threads=%d" % THREADS,
            "memory_cap_gb": MEM_CAP_GB}

SOURCES = [
    {"path": "inputs/PORNIN-2022-274-ECGFP5/paper_fulltext.md", "kn_lit": "KN-LIT-8aff72", "role": "EcGFp5 shape and raw-system floor"},
    {"path": "inputs/JOUX-VITSE-2010-157/paper_fulltext.md", "kn_lit": "KN-LIT-673219", "role": "m=4 fallback and n=4 timing anchor"},
    {"path": "research/equation-schemes-20260905/retrieved-pages/hal-00935050.txt", "kn_lit": None, "role": "FHJRV symmetrisation (arm iii)"},
]

# ============================================================== validate
def cmd_validate(args):
    rd = run_dir(); t0 = time.time()
    checks = []
    def rec(name, ok, detail=None):
        checks.append({"check": name, "pass": bool(ok), "detail": detail}); log(name, "PASS" if ok else "FAIL", detail)
    core_self_test(); rec("core_self_test_S4_S5_S6_evaluators_agree", True)
    p, cmod = 4111, 2
    rung = ladder_entry(p); F = Fq(p, cmod)
    E, cv = make_curve(F, rung, "ecgfp5_shaped"); T = (F.zero, F.zero)
    rng = random.Random("validate")
    pool_x = build_pool_x(E, rng, size_limit=POOL_LIMIT); pool_t = build_pool_t(E, rng, size_limit=POOL_LIMIT)
    rec("pools_built", len(pool_x) > 100 and len(pool_t) > 100, {"pool_x": len(pool_x), "pool_t": len(pool_t)})
    # identity control at m=3: raw grid == identity-interpolated polynomial coefficient-for-coefficient,
    # and msolve on both gives the same D and the same solutions (planted target)
    for m in (3, 4):
        xs = rng.sample(pool_x, m); pts = [E.lift_x(F(x)) for x in xs]
        R = None
        for P in pts: R = E.add(R, P)
        polI = build_arm_polynomial(E, "identity", m, rng, pool_x, extra_rows=8, holdout=8, log=log)
        Craw, nodes = build_raw_polynomial_at_target(E, m, R[0], pool=pool_x, rng=rng, log=log)
        spI = polI.specialise(F, R[0]).reshape([2 ** (m - 1) + 1] * m + [5])
        rec(f"identity_symmetrisation_equals_raw_grid_m{m}", np.array_equal(spI, Craw), {"n_coefficients": int(spI.size)})
        if m == 3:
            fI = os.path.join(rd, "identity_m3.ms"); fR = os.path.join(rd, "raw_m3.ms")
            descend_raw_and_write(spI, XVARS[m], p, fI); descend_raw_and_write(Craw, XVARS[m], p, fR)
            sI = run_msolve(fI, fI + ".out", 1800, MEM_CAP_GB, THREADS, fI + ".log")
            sR = run_msolve(fR, fR + ".out", 1800, MEM_CAP_GB, THREADS, fR + ".log")
            solI = sorted(rational_solutions(parse_msolve_param(fI + ".out", p), p, m)[0]) if not sI["no_solution"] else []
            solR = sorted(rational_solutions(parse_msolve_param(fR + ".out", p), p, m)[0]) if not sR["no_solution"] else []
            rec("identity_vs_raw_msolve_same_D_and_solutions_m3", sI["dimension_of_quotient"] == sR["dimension_of_quotient"] and solI == solR and sorted(xs) in [sorted(s) for s in solR],
                {"D_identity": sI["dimension_of_quotient"], "D_raw": sR["dimension_of_quotient"], "n_solutions": len(solR), "planted_x": sorted(xs), "wall_identity": sI["wall_seconds"], "wall_raw": sR["wall_seconds"]})
            # S_3-symmetrised (S3 arm) on the same planted target: D should be D_raw / |orbit| for free orbits
            polS = build_arm_polynomial(E, "S4" if m == 4 else "S5", m, rng, pool_x, log=log) if False else None
    # planted lifts through the full cell path (m=4, both arms) + certificates + independent verify + negative tests
    G, n = base_point(E, cv, p, "ecgfp5_shaped")
    for arm, pool in (("S4", pool_x), ("torsion_S4", pool_t)):
        m = 4
        pol = build_arm_polynomial(E, arm, m, rng, pool, T=T, log=log)
        if arm == "S4":
            xs = rng.sample(pool_x, m); pts = [E.lift_x(F(x)) for x in xs]
        else:
            ts = rng.sample(sorted(pool_t), m); pts = [E.lift_x(pool_t[t]) for t in ts]
        R = None
        for P in pts: R = E.add(R, P)
        val = R[0] if arm == "S4" else R[0] + E.a4 / R[0]
        sp = pol.specialise(F, val)
        fn = os.path.join(rd, f"planted_{arm}.ms")
        descend_and_write(sp, pol.monos, VARS[m], p, fn)
        st = run_msolve(fn, fn + ".out", 1800, MEM_CAP_GB, THREADS, fn + ".log")
        sols, _ = rational_solutions(parse_msolve_param(fn + ".out", p), p, m)
        cnt = OpCount()
        rels_all = []
        for s in sols:
            rels, diag = (lift_solution_S if arm == "S4" else lift_solution_T)(E, s, R, p, cnt) if arm == "S4" else lift_solution_T(E, s, R, T, p, cnt)
            rels_all += rels
        rec(f"planted_{arm}_D_and_lift", st["dimension_of_quotient"] == 1 and len(rels_all) >= 1, {"D": st["dimension_of_quotient"], "n_solutions": len(sols), "n_relations": len(rels_all)})
        # certificate for a planted relation is NOT a known-scalar target: label as instrument check (k unknown -> use k=None)
        if rels_all:
            # verifier positive test with a genuine known-scalar construction: R' = [k]G with k random and planted? not available;
            # instead verify the relation sum structurally (k check skipped by passing k such that R == [k]G is false -> must FAIL)
            cert = make_certificate(F, E, cv, p, cmod, arm, m, "ecgfp5_shaped", G, n, 1, R, rels_all[0], -1, 0, run_id_from_dir())
            ok, npts, reasons = verify_independent.verify(cert)
            rec(f"verifier_rejects_wrong_scalar_{arm}", (not ok) and "R != [k]G" in reasons, {"reasons": reasons})
            cert2 = dict(cert); cert2["signs"] = [-s for s in cert["signs"]]
            ok2, _, reasons2 = verify_independent.verify(cert2)
            rec(f"verifier_rejects_flipped_signs_{arm}", (not ok2) and "sum of signed points != R" in reasons2, {"reasons": reasons2})
    # genuine known-scalar positive test for the verifier: pick k, R = kG, and a relation from a random-target cell is not
    # guaranteed; so construct R = sum of planted points and set k by brute force? infeasible; instead test the verifier's
    # point/sum logic with the k-check on a trivial decomposition R = G (m points: G, P, -P, Q, -Q) with x(P), x(Q) in F_p.
    P = E.lift_x(F(pool_x[0])); Q = E.lift_x(F(pool_x[1]))
    # Genuine known-scalar POSITIVE fixture.  A factor-base decomposition of an arbitrary
    # target with a known scalar cannot be planted (that would be the DLP itself), so the
    # scalar is made known the only honest way: plant the relation first and define the
    # generator to be its sum.  Pick factor-base points P_1..P_5 (x in F_p) whose sum S
    # lies in the prime-order subgroup ([n]S = O); set G3 := S, k := 1, R := [k]G3 = S.
    # The verifier must accept with 5 lifted points, and must reject the same relation
    # when one point is replaced by a non-factor-base point.
    G3 = None; fb = None; attempt = 0
    for attempt in range(200):
        xs5 = rng.sample(pool_x, 5)
        ptsl = [E.lift_x(F(x)) for x in xs5]
        S = None
        for Pt in ptsl: S = E.add(S, Pt)
        if S is not None and E.mul(n, S) is None:
            G3, fb = S, ptsl; break
    if G3 is None:
        rec("verifier_accepts_valid_known_scalar_relation", False, {"reason": "no planted factor-base 5-sum landed in the prime-order subgroup in 200 tries"})
    else:
        cert = make_certificate(F, E, cv, p, cmod, "S5", 5, "ecgfp5_shaped", G3, n, 1, G3, (fb, [1] * 5), -1, 0, run_id_from_dir())
        okG, nptsG, reasonsG = verify_independent.verify(cert)
        rec("verifier_accepts_valid_known_scalar_relation", okG and nptsG == 5, {"reasons": reasonsG, "lifted_points": nptsG, "attempts": attempt + 1})
        cert_bad = make_certificate(F, E, cv, p, cmod, "S5", 5, "ecgfp5_shaped", G3, n, 1, G3, ([G] + fb[1:], [1] * 5), -1, 0, run_id_from_dir())
        okB, _, reasonsB = verify_independent.verify(cert_bad)
        rec("verifier_enforces_factor_base_condition", (not okB) and any("not in F_p" in r for r in reasonsB), {"reasons": reasonsB})
    # Same positive fixture for arm (iii), built from the phi-factor base (t = x + b/x in F_p).
    # NOTE: x in F_p does NOT imply x + b/x in F_p here, because b = c*z lies in F_q \ F_p;
    # an earlier revision of this suite asserted that and was wrong (recorded in
    # implementation.md and in RUN-GFPN-a0fb62, which failed on it).
    G4 = None; fbt = None
    for attemptT in range(200):
        ts5 = rng.sample(sorted(pool_t), 5)
        ptst = [E.lift_x(pool_t[tv]) for tv in ts5]
        S = None
        for Pt in ptst: S = E.add(S, Pt)
        if S is not None and E.mul(n, S) is None:
            G4, fbt = S, ptst; break
    if G4 is None:
        rec("verifier_accepts_valid_torsion_relation", False, {"reason": "no planted phi-factor-base 5-sum landed in the prime-order subgroup in 200 tries"})
    else:
        certT = make_certificate(F, E, cv, p, cmod, "torsion_S5", 5, "ecgfp5_shaped", G4, n, 1, G4, (fbt, [1] * 5), -1, 0, run_id_from_dir())
        okT, nptsT, reasonsT = verify_independent.verify(certT)
        rec("verifier_accepts_valid_torsion_relation", okT and nptsT == 5, {"reasons": reasonsT, "lifted_points": nptsT, "attempts": attemptT + 1})
        certTb = make_certificate(F, E, cv, p, cmod, "torsion_S5", 5, "ecgfp5_shaped", G4, n, 1, G4, ([G] + fbt[1:], [1] * 5), -1, 0, run_id_from_dir())
        okTb, _, reasonsTb = verify_independent.verify(certTb)
        rec("verifier_enforces_phi_factor_base_condition", (not okTb) and any("b/x" in r for r in reasonsTb), {"reasons": reasonsTb})
    ok_struct = verify_independent.CurveP(verify_independent.FqP(p, cmod), pad5(cv["a2"]), pad5(cv["a4"]), pad5(cv["a6"])).add((tuple(F.coeffs(P[0])), tuple(F.coeffs(P[1]))), (tuple(F.coeffs(Q[0])), tuple(F.coeffs(Q[1])))) == (tuple(F.coeffs(E.add(P, Q)[0])), tuple(F.coeffs(E.add(P, Q)[1])))
    rec("independent_group_law_matches_flint_group_law", ok_struct)
    allok = all(c["pass"] for c in checks)
    raw = {"run_status": "completed_valid" if allok else "failed", "failure_class": None if allok else "implementation_error",
           "kind": "validate", "parameters": common_params(p, rung, "ecgfp5_shaped", cv), "seeds": {"validate_stream": "random.Random('validate')"},
           "sources": SOURCES, "checks": checks, "metrics": {"n_checks": len(checks), "n_pass": sum(c["pass"] for c in checks), "wall_seconds": round(time.time() - t0, 1)},
           "certificate": {"kind": "none", "verified": None, "verifier": None, "note": "instrument validation run; planted relations are verifier controls, not known-scalar targets"}}
    placeholder_ladder_artifacts(rd, "validation run: no ladder cell measured")
    finish(rd, raw)

# ============================================================== anchor
def cmd_anchor(args):
    rd = run_dir(); t0 = time.time()
    p = args.p; rung = ladder_entry(p); F = Fq(p, rung["cmod"]); shape = args.shape
    E, cv = make_curve(F, rung, shape)
    rng = random.Random(f"{SEED_CURVES}:anchor:{p}:{shape}")
    pool = build_pool_x(E, rng, size_limit=POOL_LIMIT)
    m = 4
    pol = build_arm_polynomial(E, "S4", m, rng, pool, log=log)
    G, n = base_point(E, cv, p, shape)
    tg = targets(E, G, n, p, shape, args.targets)
    rows = []
    for i, k, R in tg:
        sp = pol.specialise(F, R[0])
        fn = os.path.join(rd, f"anchor_t{i}.ms")
        nterms = descend_and_write(sp, pol.monos, VARS[m], p, fn)
        # -g 1 prints the leading ideal and stops before FGLM: this is the like-for-like
        # comparison with the published Joux-Vitse figures, which time the F4 Groebner-basis
        # computation of the same system (5 equations, total degree 8, 4 variables over F_p),
        # and it also works at the 17-bit rung where msolve's parametrization step segfaults.
        # D is then recounted independently from the printed leading ideal (standard monomials).
        st = run_msolve(fn, fn + ".out", args.target_timeout, MEM_CAP_GB, 1, fn + ".log", extra=("-g", "1"))
        D_lead = None
        try:
            if not st["timed_out"] and os.path.getsize(fn + ".out") > 0:
                D_lead = count_standard_monomials(parse_leading_ideal(fn + ".out", VARS[m]), m)
        except Exception as e:
            log("leading-ideal parse failed:", e)
        rows.append({"target": i, "k": k, "terms": nterms, "wall_seconds": st["wall_seconds"], "msolve_cpu": st["timings"].get("overall_cpu"),
                     "linear_algebra_sec": st["timings"].get("linear_algebra_sec"), "D": D_lead, "D_source": "standard-monomial count from msolve -g 1 leading ideal",
                     "no_solution": st["no_solution"],
                     "f4_ops_proxy": st["f4_summary"].get("ops_proxy_reduction_total"), "max_matrix": st["f4_summary"].get("max_matrix"),
                     "returncode": st["returncode"], "timed_out": st["timed_out"], "maxrss_bytes": st["maxrss_children_bytes"]})
        rows[-1]["status"] = "measured" if st["outcome"] == "ok" else "not_measured"
        rows[-1]["outcome"] = st["outcome"]
        rows[-1]["peak_vm_bytes"] = st["peak_vm_bytes"]
        rows[-1]["failure_class"] = None if st["outcome"] == "ok" else ("resource_exhaustion" if st["outcome"] in ("timeout", "memory_exhausted") else "infrastructure_error")
        os.remove(fn)
        log("anchor target", i, rows[-1]["status"], rows[-1].get("failure_class") or "", st["wall_seconds"], "rc", st["returncode"])
    walls = [r["wall_seconds"] for r in rows if r["status"] == "measured"]
    med = sorted(walls)[len(walls) // 2] if walls else None
    published = {"JV_F4_own_C_16bit_s": 9.683, "JV_F4_own_C_25bit_s": 17.01, "JV_F4_own_C_32bit_s": 24.43,
                 "Magma_F4_16bit_s": 9.600, "Magma_F4_25bit_s": 119.1, "Magma_F4_32bit_s": 1046.0, "JV_F4prime_16bit_s": 3.979, "JV_F4prime_25bit_s": 5.002,
                 "hardware": "2.6 GHz Intel Core 2 Duo (2010), single core", "source": "inputs/JOUX-VITSE-2010-157/paper_fulltext.md section 4 table (F_{p^5}, 5 equations of total degree 8 in 4 variables)"}
    bits = p.bit_length()
    ref_key = "JV_F4_own_C_16bit_s" if bits <= 20 else ("JV_F4_own_C_25bit_s" if bits <= 28 else "JV_F4_own_C_32bit_s")
    ratio = (med / published[ref_key]) if med else None
    within2 = (ratio is not None and 0.5 <= ratio <= 2.0)
    Ds = [r["D"] for r in rows if r.get("D") is not None and r["status"] == "measured"]
    metrics = {"p": p, "p_bits": bits, "curve_shape": shape, "n_targets": len(rows), "median_wall_seconds": med,
               "ideal_degree_D_values": Ds, "ideal_degree_D": (Ds[0] if Ds and all(d == Ds[0] for d in Ds) else None),
               "msolve_mode": "-g 1 (F4 Groebner basis + leading ideal; no FGLM), matching the published F4 timings",
               "published_reference_key": ref_key, "published_reference_seconds": published[ref_key], "ratio_ours_over_published": ratio,
               "within_2x_literal": within2, "faster_than_published": (ratio is not None and ratio < 0.5),
               "ratio_vs_magma_same_bits": (med / published["Magma_F4_16bit_s" if bits <= 20 else "Magma_F4_25bit_s"]) if med else None,
               "msolve_threads": 1, "n_no_solution": sum(r["no_solution"] for r in rows), "n_with_solution": sum((not r["no_solution"]) and not r["timed_out"] for r in rows),
               "targets_measured": len(walls), "targets_not_measured": len(rows) - len(walls),
               "failure_classes": sorted({r["failure_class"] for r in rows if r["failure_class"]}),
               "wall_seconds": round(time.time() - t0, 1)}
    fclass_a = None if walls else ("infrastructure_error" if any(r["failure_class"] == "infrastructure_error" for r in rows) else "resource_exhaustion")
    raw = {"run_status": "completed_valid" if walls else "failed", "failure_class": fclass_a, "kind": "anchor",
           "parameters": {**common_params(p, rung, shape, cv), "m": 4, "arm": "S4", "system": "S_5(x_1..x_4, x_R) symmetrised in e_1..e_4, Weil-descended to 5 equations over F_p"},
           "seeds": {"targets": f"random.Random('{SEED_TARGETS}:targets:{p}:{shape}')", "sample_points": f"random.Random('{SEED_CURVES}:anchor:{p}:{shape}')"},
           "sources": SOURCES, "published": published, "polynomial_build": pol.meta, "targets": rows, "metrics": metrics,
           "certificate": {"kind": "none", "verified": None, "verifier": None, "note": "timing anchor on random known-scalar targets; no decomposition accepted"}}
    placeholder_ladder_artifacts(rd, "n=4 anchor run: no m=5 ladder cell measured")
    finish(rd, raw)

# ============================================================== build
def cmd_build(args):
    rd = run_dir(); t0 = time.time()
    p = args.p; rung = ladder_entry(p); F = Fq(p, rung["cmod"])
    shapes = args.shapes
    curves = {s: make_curve(F, rung, s) for s in shapes}
    built = []
    for m in args.m_list:
        for arm in ("S", "torsion"):
            armname = f"{arm}_S{m}".replace("S_S", "S") if arm == "torsion" else f"S{m}"
            armname = f"torsion_S{m}" if arm == "torsion" else f"S{m}"
            if arm == "S" and "S" not in args.arms: continue
            if arm == "torsion" and "torsion" not in args.arms: continue
            use_shapes = shapes if arm == "S" else [s for s in shapes if curves[s][1]["has_rational_2torsion"]]
            for s in use_shapes:
                E, cv = curves[s]
                path = cache_path(p, s, armname, m)
                if os.path.exists(path) and not args.force:
                    pol, h = load_polynomial(path)
                    built.append({"p": p, "shape": s, "arm": armname, "m": m, "cache": path, "sha256": h, "meta": pol.meta, "reused": True})
                    log("reused", path); continue
                rng = random.Random(f"{SEED_CURVES}:build:{p}:{s}:{armname}:{m}")
                pool = build_pool_x(E, rng, size_limit=POOL_LIMIT) if arm == "S" else build_pool_t(E, rng, size_limit=POOL_LIMIT)
                T = (F.zero, F.zero) if arm == "torsion" else None
                pol = build_arm_polynomial(E, armname, m, rng, pool, T=T, log=log)
                h = save_polynomial(pol, path)
                built.append({"p": p, "shape": s, "arm": armname, "m": m, "cache": path, "sha256": h, "meta": pol.meta, "reused": False,
                              "seed": f"random.Random('{SEED_CURVES}:build:{p}:{s}:{armname}:{m}')"})
                log("built", path, pol.meta)
    raw = {"run_status": "completed_valid", "failure_class": None, "kind": "build", "parameters": {**common_params(p, rung, None, None), "shapes": shapes, "m_list": args.m_list},
           "seeds": {"sample_points": f"random.Random('{SEED_CURVES}:build:{{p}}:{{shape}}:{{arm}}:{{m}}')"}, "sources": SOURCES, "polynomials": built,
           "metrics": {"n_polynomials": len(built), "n_built": sum(not b["reused"] for b in built), "all_held_out_pass": all(b["meta"]["held_out_mismatches"] == 0 for b in built),
                       "wall_seconds": round(time.time() - t0, 1), "max_support": max(b["meta"]["support_nonzero_monomials"] for b in built)},
           "certificate": {"kind": "none", "verified": None, "verifier": None, "note": "polynomial construction run; exact interpolation verified on held-out points"}}
    placeholder_ladder_artifacts(rd, "construction run: no ladder cell measured")
    finish(rd, raw)

# ============================================================== cell
def cmd_cell(args):
    rd = run_dir(); rid = run_id_from_dir(); t0 = time.time()
    p = args.p; rung = ladder_entry(p); F = Fq(p, rung["cmod"]); shape = args.shape; arm = args.arm; m = args.m
    E, cv = make_curve(F, rung, shape)
    T = (F.zero, F.zero) if arm.startswith("torsion") else None
    if T is not None:
        assert cv["has_rational_2torsion"] and E.a6 == 0
    path = cache_path(p, shape, arm, m)
    pol, h = load_polynomial(path)
    G, n = base_point(E, cv, p, shape)
    if args.target_kind == "constructed_solvable":
        rngp = random.Random(f"{SEED_CURVES}:pool:{p}:{shape}:{arm}")
        poolc = (build_pool_t(E, rngp, size_limit=POOL_LIMIT) if T is not None
                 else build_pool_x(E, rngp, size_limit=POOL_LIMIT))
        stg = solvable_targets(E, cv, p, shape, arm, m, poolc, T, args.targets, n)
        tg = [(i, k, R) for (i, k, R, _G, _n, _xs) in stg]
        planted = {i: xs for (i, _k, _R, _G, _n, xs) in stg}
        per_target_G = {i: Gi for (i, _k, _R, Gi, _n, _xs) in stg}
    else:
        tg = targets(E, G, n, p, shape, args.targets)
        planted = {}; per_target_G = {}
    rows = []; certs = []; not_measured = []
    cell_start = time.time(); watchdog_fired = False; early_stop = None; consec = 0
    n_success = 0; n_verified_rel = 0; n_lifted_pts = 0; n_rat_sols = 0
    for i, k, R in tg:
        if early_stop is not None:
            not_measured.append({"target": i, "reason": f"not attempted: {early_stop}", "class": "resource_exhaustion"}); continue
        if time.time() - cell_start > args.cell_watchdog:
            watchdog_fired = True
            not_measured.append({"target": i, "reason": "per-cell watchdog fired before this target", "class": "resource_exhaustion"}); continue
        cnt = OpCount()
        tcon = time.time()
        val = R[0] if T is None else R[0] + E.a4 / R[0]
        sp = pol.specialise(F, val, counter=cnt)
        fn = os.path.join(rd, f"cell_t{i}.ms")
        nterms = descend_and_write(sp, pol.monos, VARS[m], p, fn)
        t_con = time.time() - tcon
        st = run_msolve(fn, fn + ".out", args.target_timeout, MEM_CAP_GB, THREADS, fn + ".log")
        row = {"target": i, "k": k, "x_R": F.coeffs(R[0]), "terms": nterms, "construction_seconds": round(t_con, 3),
               "msolve": {kk: st[kk] for kk in ("wall_seconds", "returncode", "timed_out", "outcome", "dimension_of_quotient", "no_solution",
                                                "peak_rss_bytes", "peak_vm_bytes", "mem_cap_bytes", "maxrss_children_bytes", "timings", "f4_summary", "fglm")}}
        if st["outcome"] != "ok":
            row["status"] = "not_measured"
            row["failure_class"] = "resource_exhaustion" if st["outcome"] in ("timeout", "memory_exhausted") else "infrastructure_error"
            not_measured.append({"target": i, "outcome": st["outcome"], "class": row["failure_class"],
                                 "reason": (f"msolve outcome={st['outcome']} rc={st['returncode']} wall={st['wall_seconds']}s "
                                            f"peak_vm={st['peak_vm_bytes']}B of cap {st['mem_cap_bytes']}B "
                                            f"(last F4 round: {st['f4_rounds'][-1] if st['f4_rounds'] else 'none'})"),
                                 "rule": "specification stopping rule: an m=5 timeout or OOM is NOT MEASURED and is never evidence that D is large"})
            rows.append(row); os.remove(fn)
            consec += 1
            log("target", i, "NOT MEASURED", row["failure_class"], st["outcome"], st["wall_seconds"])
            if consec >= args.max_consecutive_not_measured:
                early_stop = (f"cell stopped early by the Executor after {consec} consecutive not_measured targets "
                              f"(outcome={st['outcome']}); each attempt costs about {st['wall_seconds']:.0f}s and the "
                              f"outcome was identical. This is resource exhaustion of the host, never evidence about D.")
                log("EARLY STOP:", early_stop)
            continue
        D = st["dimension_of_quotient"]
        row["D_independent_recount"] = None
        sols = []
        if not st["no_solution"] and os.path.exists(fn + ".out"):
            par = parse_msolve_param(fn + ".out", p)
            if par and "error" not in par:
                sols, _ = rational_solutions(par, p, m)
        n_rat_sols += len(sols)
        rels_all = []; diags = []
        for s in sols:
            rels, diag = lift_solution_S(E, s, R, p, cnt) if T is None else lift_solution_T(E, s, R, T, p, cnt)
            diags.append(diag); rels_all += rels
        verified = 0
        for j, rel in enumerate(rels_all):
            Gi = per_target_G.get(i, G)
            cert = make_certificate(F, E, cv, p, rung["cmod"], arm, m, shape, Gi, n, k, R, rel, i, j, rid)
            cert["target_kind"] = args.target_kind
            if args.target_kind == "constructed_solvable":
                cert["known_scalar_trivial"] = True
                cert["construction_note"] = ("SUPPLEMENTARY target: the target was built to be decomposable by "
                                             "summing m factor-base points, and the generator is defined to be "
                                             "that sum, so k = 1. No break is claimed and the decomposition "
                                             "success rate of such a cell is 1 by construction. The relation "
                                             "certified here was found by the solver, not planted into it.")
                cert["planted_defining_coordinates"] = planted.get(i)
            ok, npts, reasons = verify_independent.verify(cert)
            cert["independent_verification"] = {"verifier": "experiments/EXP-GFPN-05ff43/implementation/verify_independent.py", "pass": ok, "lifted_points": npts, "reasons": reasons}
            cp = os.path.join(rd, "certificates", f"decomposition_t{i}_r{j}.json")
            json.dump(cert, open(cp, "w"), indent=1)
            certs.append({"path": f"certificates/decomposition_t{i}_r{j}.json", "target": i, "verified": ok, "lifted_points": npts})
            if ok: verified += 1; n_lifted_pts += npts
        row.update({"status": "measured", "D": D, "n_rational_solutions": len(sols), "n_relations_lifted": len(rels_all), "n_relations_verified": verified,
                    "lift_diagnostics": diags[:20], "construction_ops": cnt.as_dict(),
                    "fp_ops_f4_proxy": st["f4_summary"].get("ops_proxy_reduction_total"), "fp_ops_f4_proxy_nnz_lower_bound": st["f4_summary"].get("ops_proxy_rows_cols_density"),
                    "fp_ops_fglm_proxy": st["fglm"].get("ops_proxy_sequence"), "fp_ops_fglm_reported_gops": st["fglm"].get("ops_from_reported_gops")})
        row["fp_ops_per_pdp_total_proxy"] = (row["fp_ops_f4_proxy"] or 0) + (row["fp_ops_fglm_proxy"] or 0) + cnt.fp_equiv_mults()
        if verified: n_success += 1
        consec = 0
        n_verified_rel += verified
        rows.append(row); os.remove(fn)
        for ext in (".out",):
            if os.path.exists(fn + ext) and os.path.getsize(fn + ext) > 50_000_000: os.remove(fn + ext)
        log("target", i, "D", D, "wall", st["wall_seconds"], "sols", len(sols), "rels", len(rels_all), "verified", verified)
    measured = [r for r in rows if r.get("status") == "measured"]
    Ds = [r["D"] for r in measured if r["D"] is not None]
    n_att = len(measured)
    pred = prediction_reference()
    metrics = {
        "p": p, "p_bits": p.bit_length(), "curve_shape": shape, "arm": arm, "m": m, "targets_planned": args.targets, "targets_attempted": n_att,
        "targets_not_measured": len(not_measured), "m5_timeout_count": sum(1 for x in not_measured if x["class"] == "resource_exhaustion") if m == 5 else 0,
        "ideal_degree_D": (Ds[0] if Ds and all(d == Ds[0] for d in Ds) else None), "D_values": Ds, "D_min": min(Ds) if Ds else None, "D_max": max(Ds) if Ds else None,
        "fp_operations_per_pdp": (float(np.median([r["fp_ops_per_pdp_total_proxy"] for r in measured])) if measured else None),
        "fp_ops_f4_proxy_median": (float(np.median([r["fp_ops_f4_proxy"] or 0 for r in measured])) if measured else None),
        "fp_ops_fglm_proxy_median": (float(np.median([r["fp_ops_fglm_proxy"] or 0 for r in measured])) if measured else None),
        "construction_ops_fp_mult_equiv_median": (float(np.median([r["construction_ops"]["fp_mult_equivalents"] for r in measured])) if measured else None),
        "target_kind": args.target_kind,
        "decomposition_success_rate": ((n_success / n_att) if n_att else None) if args.target_kind == "random" else None,
        "success_rate_by_construction": ((n_success / n_att) if n_att else None) if args.target_kind == "constructed_solvable" else None,
        "success_rate_note": ("random known-scalar targets: this is the measured decomposition probability"
                              if args.target_kind == "random" else
                              "constructed-solvable targets: every target is decomposable by construction, so this "
                              "number measures whether the solver and the lifting path RECOVER the decomposition, "
                              "not how often a random point decomposes"),
        "targets_with_verified_relation": n_success,
        "n_rational_solutions_total": n_rat_sols, "n_relations_verified_total": n_verified_rel, "lifted_verified_points_total": n_lifted_pts,
        "lifted_verified_points_per_success": (n_lifted_pts / n_success) if n_success else None,
        "certificate_verify_pass_rate": (sum(c["verified"] for c in certs) / len(certs)) if certs else None,
        "wall_seconds_per_cell": round(time.time() - t0, 1), "median_msolve_wall_seconds": (float(np.median([r["msolve"]["wall_seconds"] for r in measured])) if measured else None),
        "peak_memory_bytes": max([r["msolve"]["peak_rss_bytes"] for r in rows], default=None),
        "peak_vm_bytes": max([r["msolve"]["peak_vm_bytes"] for r in rows], default=None),
        "watchdog_fired": watchdog_fired, "early_stopped": early_stop is not None, "early_stop_reason": early_stop,
        "not_measured_outcomes": sorted({x.get("outcome") for x in not_measured if x.get("outcome")}),
        "solver_id": f"msolve-0.6.5/F4+FGLM/-t{THREADS}",
    }
    if Ds:
        Draw_pred = pred["D_raw_free_orbit"]; G_ = pred["group_orders"].get(arm.replace("S4", "S5"), None)
        if G_ and m == 5:
            metrics["ratio_Draw_pred_over_D"] = Draw_pred / metrics["D_max"]
            metrics["orbit_nonfreeness_ratio_vs_predicted_raw"] = metrics["D_max"] * G_ / Draw_pred
            metrics["orbit_nonfreeness_note"] = "D_sym*|G|/D_raw with D_raw = 2^20 (frozen free-orbit prediction; D_raw not measured at m=5)"
    status = "completed_valid" if measured else ("failed" if not rows or all(r.get("status") == "not_measured" for r in rows) else "completed_valid")
    fclass = None if measured else "resource_exhaustion"
    cert_block = ({"kind": "decomposition", "verified": all(c["verified"] for c in certs) and n_verified_rel > 0, "verifier": "experiments/EXP-GFPN-05ff43/implementation/verify_independent.py",
                   "count": len(certs), "note": "every accepted relation re-verified by independent pure-Python code; success counted in lifted verified points"}
                  if certs else {"kind": "none", "verified": None, "verifier": None, "note": "no rational solution lifted to a verified relation in this cell (degree measurement only)"})
    if certs and not all(c["verified"] for c in certs):
        status = "invalid"; fclass = "invalid_measurement"
    raw = {"run_status": status, "failure_class": fclass, "kind": "cell", "cell": f"p={p} shape={shape} arm={arm} m={m}",
           "parameters": {**common_params(p, rung, shape, cv), "m": m, "arm": arm, "n_targets": args.targets,
                          "target_kind": args.target_kind,
                          "target_kind_note": ("random: R = [k]G for random k, the contract's cell"
                                               if args.target_kind == "random" else
                                               "constructed_solvable: SUPPLEMENTARY cell; R is a sum of m factor-base "
                                               "points and G := R, k := 1. Not the contract's cell; reported separately"),
                          "target_timeout_s": args.target_timeout, "cell_watchdog_s": args.cell_watchdog,
                          "polynomial_cache": path, "polynomial_sha256": h, "polynomial_meta": pol.meta, "subgroup_order": n, "G": pt_json(F, G)},
           "watchdog": {"per_target_timeout_s": args.target_timeout, "per_cell_watchdog_s": args.cell_watchdog, "fired": watchdog_fired,
                        "max_consecutive_not_measured": args.max_consecutive_not_measured, "early_stop_reason": early_stop},
           "seeds": {"targets": (f"random.Random('{SEED_TARGETS}:targets:{p}:{shape}')" if args.target_kind == "random"
                                 else f"random.Random('{SEED_TARGETS}:solvable:{p}:{shape}:{arm}:{m}:<i>')"),
                     "basepoint": f"random.Random('{SEED_CURVES}:basepoint:{p}:{shape}')"},
           "sources": SOURCES, "prediction_reference": pred, "targets": rows, "certificates": certs, "not_measured": not_measured, "metrics": metrics, "certificate": cert_block}
    write_cell_artifacts(rd, raw)
    finish(rd, raw)

def write_cell_artifacts(rd, raw):
    mt = raw["metrics"]
    row = {"p": mt["p"], "p_bits": mt["p_bits"], "curve_shape": mt["curve_shape"], "arm": mt["arm"], "m": mt["m"], "D": mt.get("ideal_degree_D"), "D_values": mt.get("D_values"),
           "fp_operations_per_pdp_proxy": mt.get("fp_operations_per_pdp"), "success_rate": mt.get("decomposition_success_rate"), "targets_attempted": mt["targets_attempted"],
           "targets_not_measured": mt["targets_not_measured"], "lifted_verified_points_total": mt.get("lifted_verified_points_total"), "status": raw["run_status"], "label": "measured" if mt["targets_attempted"] else "not_measured"}
    placeholder_ladder_artifacts(rd, "single cell; ladder-wide decision in the aggregation run", rows=[row],
        dflat={"heuristic": "HEUR-GFPN-DFLAT", "cell_D": mt.get("ideal_degree_D"), "decision_scope": "ladder-wide decision is made in the aggregation run", "heur_dflat_pass": "not_decided_in_this_run"},
        band={"status": "not_applicable_in_this_run", "note": "cost band emitted by the aggregation run only when heur_dflat_pass is true for the arm"})

# ============================================================== raw arm
def cmd_raw(args):
    rd = run_dir(); rid = run_id_from_dir(); t0 = time.time()
    p = args.p; rung = ladder_entry(p); F = Fq(p, rung["cmod"]); shape = args.shape; m = args.m
    E, cv = make_curve(F, rung, shape)
    rng = random.Random(f"{SEED_CURVES}:raw:{p}:{shape}:{m}")
    pool = build_pool_x(E, rng, size_limit=POOL_LIMIT)
    G, n = base_point(E, cv, p, shape)
    if args.target_kind == "constructed_solvable":
        stg = solvable_targets(E, cv, p, shape, "raw", m, pool, None, args.targets, n)
        tg = [(i, k, R) for (i, k, R, _G, _n, _xs) in stg]
        per_target_G = {i: Gi for (i, _k, _R, Gi, _n, _xs) in stg}
    else:
        tg = targets(E, G, n, p, shape, args.targets)
        per_target_G = {}
    rows = []; not_measured = []; cell_start = time.time(); watchdog_fired = False; certs = []; early_stop = None; consec = 0
    for i, k, R in tg:
        if early_stop is not None:
            not_measured.append({"target": i, "reason": f"not attempted: {early_stop}", "class": "resource_exhaustion"}); continue
        if time.time() - cell_start > args.cell_watchdog:
            watchdog_fired = True; not_measured.append({"target": i, "reason": "per-cell watchdog fired", "class": "resource_exhaustion"}); continue
        tcon = time.time()
        C, nodes = build_raw_polynomial_at_target(E, m, R[0], pool=pool, rng=rng, log=log)
        fn = os.path.join(rd, f"raw_t{i}.ms")
        nterms = descend_raw_and_write(C, XVARS[m], p, fn)
        t_con = time.time() - tcon
        log("raw target", i, "terms", nterms, "construction %.1fs" % t_con, "file MB %.1f" % (os.path.getsize(fn) / 1e6))
        st = run_msolve(fn, fn + ".out", args.target_timeout, MEM_CAP_GB, THREADS, fn + ".log")
        row = {"target": i, "k": k, "terms": nterms, "construction_seconds": round(t_con, 1), "input_bytes": os.path.getsize(fn),
               "msolve": {kk: st[kk] for kk in ("wall_seconds", "returncode", "timed_out", "outcome", "dimension_of_quotient", "no_solution",
                                                "peak_rss_bytes", "peak_vm_bytes", "mem_cap_bytes", "maxrss_children_bytes", "timings", "f4_summary", "fglm")},
               "f4_rounds_completed": len(st["f4_rounds"]), "f4_rounds": st["f4_rounds"][:200]}
        os.remove(fn)
        if st["outcome"] != "ok":
            row["status"] = "not_measured"
            row["failure_class"] = "resource_exhaustion" if st["outcome"] in ("timeout", "memory_exhausted") else "infrastructure_error"
            not_measured.append({"target": i, "outcome": st["outcome"], "class": row["failure_class"],
                                 "reason": (f"msolve outcome={st['outcome']} rc={st['returncode']} wall={st['wall_seconds']}s "
                                            f"peak_vm={st['peak_vm_bytes']}B of cap {st['mem_cap_bytes']}B "
                                            f"(last F4 round: {st['f4_rounds'][-1] if st['f4_rounds'] else 'none'})"),
                                 "rule": "specification stopping rule: an m=5 timeout or OOM is NOT MEASURED and is never evidence that D is large"})
            log("raw target", i, "NOT MEASURED", row["failure_class"], st["outcome"]); rows.append(row)
            consec += 1
            if consec >= args.max_consecutive_not_measured:
                early_stop = (f"cell stopped early by the Executor after {consec} consecutive not_measured targets "
                              f"(outcome={st['outcome']}). Resource exhaustion of the host, never evidence about D.")
                log("EARLY STOP:", early_stop)
            continue
        D = st["dimension_of_quotient"]; sols = []
        if not st["no_solution"] and os.path.exists(fn + ".out"):
            par = parse_msolve_param(fn + ".out", p)
            if par and "error" not in par: sols, _ = rational_solutions(par, p, m)
        cnt = OpCount(); rels_all = []
        for s in sols:
            pts = [E.lift_x(F(x)) for x in s]
            if any(P is None for P in pts): continue
            rels_all += sign_search(E, pts, R, cnt)
        verified = 0
        for j, rel in enumerate(rels_all):
            cert = make_certificate(F, E, cv, p, rung["cmod"], "raw", m, shape, per_target_G.get(i, G), n, k, R, rel, i, j, rid)
            cert["target_kind"] = args.target_kind
            ok, npts, reasons = verify_independent.verify(cert)
            cert["independent_verification"] = {"verifier": "experiments/EXP-GFPN-05ff43/implementation/verify_independent.py", "pass": ok, "lifted_points": npts, "reasons": reasons}
            cp = os.path.join(rd, "certificates", f"decomposition_t{i}_r{j}.json"); json.dump(cert, open(cp, "w"), indent=1)
            certs.append({"path": f"certificates/decomposition_t{i}_r{j}.json", "target": i, "verified": ok, "lifted_points": npts}); verified += ok
        row.update({"status": "measured", "D": D, "n_rational_solutions": len(sols), "n_relations_verified": verified, "fp_ops_f4_proxy": st["f4_summary"].get("ops_proxy_reduction_total"), "fp_ops_f4_proxy_nnz_lower_bound": st["f4_summary"].get("ops_proxy_rows_cols_density"), "fp_ops_fglm_proxy": st["fglm"].get("ops_proxy_sequence")})
        rows.append(row); log("raw target", i, "D", D, "wall", st["wall_seconds"])
    measured = [r for r in rows if r.get("status") == "measured"]
    Ds = [r["D"] for r in measured]
    metrics = {"p": p, "p_bits": p.bit_length(), "curve_shape": shape, "arm": "raw", "m": m, "targets_planned": args.targets, "targets_attempted": len(measured), "targets_not_measured": len(not_measured),
               "m5_timeout_count": sum(1 for x in not_measured if x["class"] == "resource_exhaustion") if m == 5 else 0,
               "ideal_degree_D": (Ds[0] if Ds and all(d == Ds[0] for d in Ds) else None), "D_values": Ds,
               "fp_operations_per_pdp": (float(np.median([(r["fp_ops_f4_proxy"] or 0) + (r["fp_ops_fglm_proxy"] or 0) for r in measured])) if measured else None),
               "decomposition_success_rate": (sum(r["n_relations_verified"] > 0 for r in measured) / len(measured)) if measured else None,
               "lifted_verified_points_total": sum(c["lifted_points"] for c in certs if c["verified"]), "wall_seconds_per_cell": round(time.time() - t0, 1),
               "peak_memory_bytes": max([r["msolve"]["peak_rss_bytes"] for r in rows], default=None),
        "peak_vm_bytes": max([r["msolve"]["peak_vm_bytes"] for r in rows], default=None),
        "watchdog_fired": watchdog_fired, "early_stopped": early_stop is not None, "early_stop_reason": early_stop,
        "not_measured_outcomes": sorted({x.get("outcome") for x in not_measured if x.get("outcome")}), "solver_id": f"msolve-0.6.5/F4+FGLM/-t{THREADS}",
               "target_kind": args.target_kind,
               "f4_rounds_completed_max": max([r["f4_rounds_completed"] for r in rows], default=None), "raw_terms_per_equation_total": rows[0]["terms"] if rows else None}
    status = "completed_valid" if measured else "failed"; fclass = None if measured else "resource_exhaustion"
    cert_block = ({"kind": "decomposition", "verified": all(c["verified"] for c in certs), "verifier": "experiments/EXP-GFPN-05ff43/implementation/verify_independent.py", "count": len(certs)} if certs
                  else {"kind": "none", "verified": None, "verifier": None, "note": "no decomposition accepted (timeout / resource exhaustion or degree-only)"})
    raw = {"run_status": status, "failure_class": fclass, "kind": "raw", "cell": f"p={p} shape={shape} arm=raw m={m}",
           "parameters": {**common_params(p, rung, shape, cv), "m": m, "arm": "raw", "n_targets": args.targets, "target_timeout_s": args.target_timeout, "cell_watchdog_s": args.cell_watchdog, "subgroup_order": n},
           "watchdog": {"per_target_timeout_s": args.target_timeout, "per_cell_watchdog_s": args.cell_watchdog, "fired": watchdog_fired,
                        "max_consecutive_not_measured": args.max_consecutive_not_measured, "early_stop_reason": early_stop},
           "seeds": {"targets": f"random.Random('{SEED_TARGETS}:targets:{p}:{shape}')", "grid_nodes": f"random.Random('{SEED_CURVES}:raw:{p}:{shape}:{m}')"},
           "sources": SOURCES, "prediction_reference": prediction_reference(), "targets": rows, "certificates": certs, "not_measured": not_measured, "metrics": metrics, "certificate": cert_block,
           "rule": "timeouts are recorded not_measured / resource_exhaustion and are never evidence that D is large (specification stopping rule 3)"}
    write_cell_artifacts(rd, raw)
    finish(rd, raw)

# ============================================================== aggregate
def cmd_aggregate(args):
    rd = run_dir(); t0 = time.time()
    runs = {}
    for rid in args.runs.split(","):
        rp = os.path.join(EXP_DIR, "runs", rid, "raw-result.json")
        runs[rid] = json.load(open(rp))
    cells = {}; excluded = []
    for rid, r in runs.items():
        if r.get("kind") not in ("cell", "raw"):
            excluded.append({"run": rid, "kind": r.get("kind"), "reason": "not a cell run"}); continue
        mt = r.get("metrics") or {}
        if not all(k in mt for k in ("arm", "curve_shape", "m", "p")):
            # a run terminated before it could identify its own cell (closed out by
            # close_terminated_run.py); it is kept in the ledger and named here, but it
            # carries no measurement to aggregate
            excluded.append({"run": rid, "status": r.get("run_status"), "failure_class": r.get("failure_class"),
                             "reason": "terminated before any cell metric was written; no measurement to aggregate"})
            continue
        key = (mt["arm"], mt["curve_shape"], mt["m"], mt["p"], mt.get("target_kind", "random"))
        cells[key] = {"run": rid, **mt, "status": r["run_status"]}
    pred = prediction_reference()
    rows = [{"run": c["run"], "arm": a, "curve_shape": s, "m": m, "p": p, "target_kind": tk, "p_bits": c["p_bits"], "D": c.get("ideal_degree_D"), "D_values": c.get("D_values"),
             "fp_operations_per_pdp_proxy": c.get("fp_operations_per_pdp"), "success_rate": c.get("decomposition_success_rate"), "targets_attempted": c["targets_attempted"],
             "targets_not_measured": c["targets_not_measured"], "lifted_verified_points_total": c.get("lifted_verified_points_total"), "status": c["status"],
             "success_rate_by_construction": c.get("success_rate_by_construction"),
             "label": "measured" if c["targets_attempted"] else "not_measured"}
            for (a, s, m, p, tk), c in sorted(cells.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[0][3], kv[0][4]))]
    # HEUR-GFPN-DFLAT per arm on EcGFp5-shaped m=5 cells (and per shape as extra rows)
    dflat = {"heuristic": "HEUR-GFPN-DFLAT", "frozen_statement": "relative D variation < 10% across >=3 primes spanning >=12 bits (per arm, m=5)", "arms": {}}
    for arm in ("raw", "S5", "torsion_S5"):
        for shape in ("ecgfp5_shaped", "random_2torsion", "random_no2torsion"):
            pts = [(p, c.get("ideal_degree_D")) for (a, s, m, p, tk), c in cells.items()
                   if a == arm and s == shape and m == 5 and tk == "random" and c.get("ideal_degree_D") is not None]
            if not pts: 
                dflat["arms"].setdefault(arm, {})[shape] = {"heur_dflat_pass": "not_applicable", "reason": "no completed m=5 cell with a measured D", "n_cells": 0}; continue
            ps = sorted(p for p, _ in pts); Ds = [d for _, d in pts]
            span = max(ps).bit_length() - min(ps).bit_length()
            rel_var = (max(Ds) - min(Ds)) / (sum(Ds) / len(Ds))
            enough = len(pts) >= 3 and span >= 12
            dec = (rel_var < 0.10) if enough else "not_applicable"
            dflat["arms"].setdefault(arm, {})[shape] = {"heur_dflat_pass": dec, "n_cells": len(pts), "primes": ps, "bit_span": span, "D_per_prime": {str(p): d for p, d in sorted(pts)},
                                                       "D_relative_variation": rel_var, "D_max_over_min": max(Ds) / min(Ds), "reason": None if enough else "fewer than 3 primes or span < 12 bits"}
    # SUPPLEMENTARY flatness at the point counts this host can complete (m = 3, m = 4).
    # HEUR-GFPN-DFLAT is stated for m = 5 and is NOT decided by any of this; the same
    # statistic is computed on the completed cells so the ladder is not silent about the
    # p-dependence it could actually reach.
    supp = {"note": ("supplementary only: HEUR-GFPN-DFLAT as frozen concerns the m = 5 descended system. "
                     "These are the same statistics computed at the point counts that completed on this "
                     "host, and they decide nothing about the frozen heuristic."),
            "threshold_applied_for_reference": 0.10, "arms": {}}
    for (a, s, mm, pp, tk), c in sorted(cells.items()):
        if mm == 5 or c.get("ideal_degree_D") is None:
            continue
        key = f"{a}|{s}|m{mm}|{tk}"
        supp["arms"].setdefault(key, {"cells": []})["cells"].append(
            {"p": pp, "p_bits": c["p_bits"], "D": c["ideal_degree_D"],
             "fp_ops_per_pdp_proxy": c.get("fp_operations_per_pdp"),
             "lifted_verified_points_total": c.get("lifted_verified_points_total"), "run": c["run"]})
    for key, blk in supp["arms"].items():
        ds = [x["D"] for x in blk["cells"]]
        ps = [x["p"] for x in blk["cells"]]
        ops = [x["fp_ops_per_pdp_proxy"] for x in blk["cells"] if x["fp_ops_per_pdp_proxy"]]
        span = max(ps).bit_length() - min(ps).bit_length()
        blk["n_cells"] = len(ds); blk["primes"] = sorted(ps); blk["bit_span"] = span
        blk["D_relative_variation"] = (max(ds) - min(ds)) / (sum(ds) / len(ds))
        blk["D_identical_across_ladder"] = len(set(ds)) == 1
        blk["fp_ops_relative_variation"] = ((max(ops) - min(ops)) / (sum(ops) / len(ops))) if len(ops) > 1 else None
        blk["meets_3_primes_12_bits"] = len(ds) >= 3 and span >= 12
    # raw-vs-symmetrised degree ratio, measured, at each completed point count
    supp["degree_ratios_measured"] = []
    for (a, s, mm, pp, tk), c in sorted(cells.items()):
        if a == "raw" or mm == 5 or c.get("ideal_degree_D") is None:
            continue
        rawc = cells.get(("raw", s, mm, pp, tk))
        if not rawc or rawc.get("ideal_degree_D") is None:
            continue
        grp = {"S3": 6, "S4": 24, "S5": 120, "torsion_S3": 2 ** 2 * 6, "torsion_S4": 2 ** 3 * 24, "torsion_S5": 2 ** 4 * 120}.get(a)
        supp["degree_ratios_measured"].append(
            {"arm": a, "shape": s, "m": mm, "p": pp, "target_kind": tk,
             "D_raw": rawc["ideal_degree_D"], "D_sym": c["ideal_degree_D"],
             "ratio_D_raw_over_D_sym": rawc["ideal_degree_D"] / c["ideal_degree_D"],
             "free_orbit_group_order": grp,
             "orbit_nonfreeness_D_sym_times_G_over_D_raw": (c["ideal_degree_D"] * grp / rawc["ideal_degree_D"]) if grp else None,
             "fp_ops_ratio_raw_over_sym": ((rawc.get("fp_operations_per_pdp") or 0) / c["fp_operations_per_pdp"])
                                          if c.get("fp_operations_per_pdp") else None,
             "note": ("D_sym = 1 floors the ratio: a symmetrisation cannot reduce the degree below one, so a "
                      "ratio equal to D_raw is consistent with free orbits but cannot exhibit a group larger "
                      "than D_raw") if c["ideal_degree_D"] == 1 else None})

    # ratios and tail checks on EcGFp5-shaped m=5 cells
    comparisons = []
    for (a, s, m, p, tk), c in sorted(cells.items()):
        if m != 5 or c.get("ideal_degree_D") is None: continue
        G_ = pred["group_orders"].get(a)
        comparisons.append({"arm": a, "shape": s, "p": p, "D": c["ideal_degree_D"], "D_raw_pred_over_D": 2 ** 20 / c["ideal_degree_D"], "log2_ratio": float(np.log2(2 ** 20 / c["ideal_degree_D"])),
                            "min_required_log2": {"S5": 6, "torsion_S5": 9}.get(a), "ratio_meets_prediction": (2 ** 20 / c["ideal_degree_D"]) >= {"S5": 2 ** 6, "torsion_S5": 2 ** 9}.get(a, 0),
                            "orbit_nonfreeness_D_sym_G_over_Draw_pred": c["ideal_degree_D"] * G_ / 2 ** 20 if G_ else None, "tail_flag_nonfree_below_0_5": (c["ideal_degree_D"] * G_ / 2 ** 20 < 0.5) if G_ else None,
                            "fp_ops_per_pdp_proxy": c.get("fp_operations_per_pdp"), "fp_ops_log2": float(np.log2(c["fp_operations_per_pdp"])) if c.get("fp_operations_per_pdp") else None,
                            "tail_check_arm_iii_above_2_36": (c.get("fp_operations_per_pdp") or 0) > 2 ** 36 if a == "torsion_S5" else None})
    # F4 mechanism check: EcGFp5-shaped vs random_2torsion D within 10% on matched cells
    matched = []
    for (a, s, m, p, tk), c in cells.items():
        if s == "ecgfp5_shaped" and m == 5 and c.get("ideal_degree_D") is not None:
            o = cells.get((a, "random_2torsion", m, p, tk))
            if o and o.get("ideal_degree_D") is not None:
                matched.append({"arm": a, "p": p, "D_ecgfp5": c["ideal_degree_D"], "D_random_2torsion": o["ideal_degree_D"], "rel_diff": abs(c["ideal_degree_D"] - o["ideal_degree_D"]) / c["ideal_degree_D"], "differs_more_than_10pct": abs(c["ideal_degree_D"] - o["ideal_degree_D"]) / c["ideal_degree_D"] > 0.10})
    # cost band at p = 2^64 - 2^32 + 1 (arithmetic only, modeled) per arm where heur_dflat_pass is True on ecgfp5_shaped
    P64 = 2 ** 64 - 2 ** 32 + 1
    band = {"p_crypto": str(P64), "label": "MODELED (arithmetic-only projection; no wall time is extrapolated)", "design_note_floor_bits": 142, "arms": {}}
    for arm in ("S5", "torsion_S5", "raw"):
        d = dflat["arms"].get(arm, {}).get("ecgfp5_shaped", {})
        if d.get("heur_dflat_pass") is not True:
            band["arms"][arm] = {"band": None, "reason": "heur_dflat_failed" if d.get("heur_dflat_pass") is False else "heur_dflat_not_applicable", "heur_dflat_pass": d.get("heur_dflat_pass")}; continue
        Dvals = list(d["D_per_prime"].values()); D = max(Dvals)
        cs = [c for (a, s, m, p, tk), c in cells.items() if a == arm and s == "ecgfp5_shaped" and m == 5 and tk == "random" and c["targets_attempted"]]
        att = sum(c["targets_attempted"] for c in cs); succ = sum(c["targets_with_verified_relation"] if "targets_with_verified_relation" in c else round((c.get("decomposition_success_rate") or 0) * c["targets_attempted"]) for c in cs)
        s_meas = succ / att if att else None
        # 95% Clopper-Pearson-ish bounds via beta quantiles (simple normal fallback if scipy missing)
        try:
            from scipy.stats import beta
            lo = beta.ppf(0.025, succ, att - succ + 1) if succ > 0 else 0.0; hi = beta.ppf(0.975, succ + 1, att - succ) if succ < att else 1.0
        except Exception:
            lo, hi = None, None
        nominal = 1 / 120 if arm == "S5" else 2 / 120
        ops_meas = float(np.median([c["fp_operations_per_pdp"] for c in cs if c.get("fp_operations_per_pdp")]))
        Nrel = P64 ** (8 / 5)
        def bits(x): return float(np.log2(x))
        entry = {"heur_dflat_pass": True, "D_measured_max_over_ladder": D, "measured_fp_ops_per_pdp_proxy": ops_meas, "success_rate_measured": s_meas, "success_rate_95pct_interval": [lo, hi], "targets_attempted": att, "successes": succ,
                 "success_rate_nominal_free_orbit": nominal, "N_relations_design_note_p^(2-2/5)_bits": bits(Nrel),
                 "modeled": {"N_systems_bits_nominal_rate": bits(Nrel / nominal),
                             "N_systems_bits_measured_rate": bits(Nrel / s_meas) if s_meas else None,
                             "N_systems_bits_measured_rate_upper95": bits(Nrel / lo) if lo else None,
                             "C_pdp_bits_D2_floor": bits(D ** 2), "C_pdp_bits_5D3_nominal": bits(5 * D ** 3), "C_pdp_bits_measured_ops_proxy": bits(ops_meas),
                             "band_bits_nominal_rate": [bits(Nrel / nominal * D ** 2), bits(Nrel / nominal * 5 * D ** 3)],
                             "band_bits_measured_rate": [bits(Nrel / s_meas * D ** 2), bits(Nrel / s_meas * 5 * D ** 3)] if s_meas else None,
                             "point_estimate_bits_measured_ops_nominal_rate": bits(Nrel / nominal * ops_meas),
                             "point_estimate_bits_measured_ops_measured_rate": bits(Nrel / s_meas * ops_meas) if s_meas else None},
                 "optimistic_assumptions_restated": ["free-orbit degree drop (actual measured D used, gap reported as orbit_nonfreeness)", "FGLM exponent between 2 and 3 (both edges reported: D^2 and 5 D^3)",
                                                     "system count from design-note balancing p^(2-2/5) relations; measured success rate replaces 1/m! (binomial interval reported; with 20 targets per cell the rate is coarse)",
                                                     "linear algebra cost ~ p^(2-2/5) rows (Gaudry double-large-prime) not added; symmetrised-polynomial construction and orbit lifting charged in the measured ops proxy"],
                 "comparison_constant_bits": 142}
        band["arms"][arm] = entry
    metrics = {"n_runs": len(runs), "n_cells": len(cells), "n_excluded_runs": len(excluded),
               "supplementary_D_flat_arms": {k: v["D_identical_across_ladder"] for k, v in supp["arms"].items()}, "heur_dflat_pass": {a: {s: v["heur_dflat_pass"] for s, v in d.items()} for a, d in dflat["arms"].items()},
               "D_variation_across_ladder": {a: {s: v.get("D_relative_variation") for s, v in d.items()} for a, d in dflat["arms"].items()},
               "wall_seconds": round(time.time() - t0, 1)}
    raw = {"run_status": "completed_valid", "failure_class": None, "kind": "aggregate", "parameters": {"runs": list(runs)}, "seeds": None, "sources": SOURCES,
           "prediction_reference": pred, "excluded_runs": excluded, "ladder_rows": rows, "heur_dflat": dflat, "supplementary_flatness": supp,
           "comparisons": comparisons, "matched_control_check_F4": matched, "cost_band": band, "metrics": metrics,
           "certificate": {"kind": "none", "verified": None, "verifier": None, "note": "aggregation of measured cells; no new decomposition claimed"}}
    write_yaml(os.path.join(rd, "ladder-table.yaml"), {"ladder_table": {"rows": rows, "comparisons_vs_frozen_prediction": comparisons, "matched_control_check": matched, "supplementary_degree_ratios": supp["degree_ratios_measured"], "label_note": "D and fp ops are measured on toy p' (fp ops = proxy from msolve matrix statistics + counted construction/lifting ops)"}})
    write_yaml(os.path.join(rd, "heur-dflat.yaml"), {"heur_dflat": dflat, "supplementary_flatness_not_the_frozen_heuristic": supp})
    write_yaml(os.path.join(rd, "cost-band-p64.yaml"), {"cost_band_p64": band})
    finish(rd, raw)

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    a = sub.add_parser("anchor"); a.add_argument("--p", type=int, required=True); a.add_argument("--shape", default="random_no2torsion"); a.add_argument("--targets", type=int, default=5); a.add_argument("--target-timeout", type=int, default=3600); a.add_argument("--gb-only", action="store_true")
    b = sub.add_parser("build"); b.add_argument("--p", type=int, required=True); b.add_argument("--m-list", type=int, nargs="+", default=[5, 4]); b.add_argument("--force", action="store_true")
    b.add_argument("--shapes", nargs="+", default=["ecgfp5_shaped", "random_2torsion", "random_no2torsion"]); b.add_argument("--arms", nargs="+", default=["S", "torsion"])
    c = sub.add_parser("cell"); c.add_argument("--p", type=int, required=True); c.add_argument("--shape", required=True); c.add_argument("--arm", required=True); c.add_argument("--m", type=int, required=True)
    c.add_argument("--targets", type=int, default=20); c.add_argument("--target-timeout", type=int, default=3600); c.add_argument("--cell-watchdog", type=int, default=6 * 3600)
    c.add_argument("--max-consecutive-not-measured", type=int, default=3)
    c.add_argument("--target-kind", choices=["random", "constructed_solvable"], default="random")
    r = sub.add_parser("raw"); r.add_argument("--p", type=int, required=True); r.add_argument("--shape", required=True); r.add_argument("--m", type=int, required=True)
    r.add_argument("--targets", type=int, default=20); r.add_argument("--target-timeout", type=int, default=3600); r.add_argument("--cell-watchdog", type=int, default=2 * 3600)
    r.add_argument("--max-consecutive-not-measured", type=int, default=2)
    r.add_argument("--target-kind", choices=["random", "constructed_solvable"], default="random")
    g = sub.add_parser("aggregate"); g.add_argument("--runs", required=True)
    args = ap.parse_args()
    {"validate": cmd_validate, "anchor": cmd_anchor, "build": cmd_build, "cell": cmd_cell, "raw": cmd_raw, "aggregate": cmd_aggregate}[args.cmd](args)

if __name__ == "__main__":
    main()
