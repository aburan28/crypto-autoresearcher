#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- driver. Every subcommand runs inside a run package created by
v2_run_wrapper.py (which sets GFPN_RUN_DIR and GFPN_V2_PACKAGE) and writes raw-result.json,
ladder-table.yaml, heur-dflat.yaml, cost-band-p64.yaml and certificates/.

The driver is LIGHT: every memory-heavy step (msolve, polynomial interpolation, raw grids, the Sage
comparator, callgrind) is a separate capped child (v2_solver.run_child; AC-1).

Subcommands (card EC-3 order):
  fixture  --p P            F-1, F-2, F-3 at n = m = 3 (blocking), p' in {4111, 16777291}
  anchor-identity           rulings.DC-5 jv_anchor_system_trace_identity at p' = 16777291 (blocking)
  controls                  degenerate_symmetrization_identity, orbit_lifting_verifier,
                            known_scalar_instances (frozen, blocking)
  fixture4                  F-4 at n = m = 4 (NOT blocking)
  build    --p P            arm polynomials for the n = 5 ladder at P (m = 5 and m = 4), refusal rows (R-6)
  cells    --p P --shape S --m M [--prior-run RUN]   all planned arms of one (p', shape, m) on the SAME targets
  aggregate --runs RUN,...  ladder table, like-for-like scoring (DC-2), HEUR-GFPN-DFLAT, F4, band (B-3)
"""
import argparse
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                                     # noqa: E402

import flint                                           # noqa: E402
flint.ctx.threads = 1

import v2_arms as A                                    # noqa: E402
import v2_common as C                                  # noqa: E402
import v2_lift as L                                    # noqa: E402
import v2_scoring as SC                                # noqa: E402
import v2_solver as V                                  # noqa: E402
import v2_verify_independent as VI                     # noqa: E402
from v2_child import load_poly                         # noqa: E402
from v2_field import OpCount, self_test as field_self_test   # noqa: E402

CAP = int(os.environ.get("GFPN_V2_CAP_BYTES", str(V.CAP_BYTES_DEFAULT)))
RETAIN_MAX_BYTES = 50 * 1024 * 1024
A6_NOT_ATTEMPTED_RAW_M5 = ("predicted D_raw ~ 2^26.9 (P-2), 2^6.9 above the S_5 shape that exhausted 11 GiB at the "
                           "degree-33 round (RUN-GFPN-8f1b50); 17^5-node grid interpolation")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class Ctx:
    def __init__(self):
        self.rd = C.run_dir()
        self.rid = C.run_id()
        self.plan = C.load_plan()
        self.pkg = C.plan_package(self.plan, self.rid)
        if self.pkg["kind"] == "contingency":
            rep = os.environ.get("GFPN_V2_REPLACES")
            base = C.plan_package(self.plan, rep)
            self.pkg = dict(base, run_id=self.rid, contingency_for=rep)
        self.host = C.host_record()
        self.msolve_version = C.msolve_version()
        self.cap = CAP
        for d in ("solver", "certificates", "child", "polynomials"):
            os.makedirs(os.path.join(self.rd, d), exist_ok=True)
        self.events = []

    def event(self, what, **kw):
        e = {"at": C.now(), "event": what}
        e.update(kw)
        self.events.append(e)
        log(what, kw if kw else "")


def finish(ctx, raw, ladder_rows=None, dflat=None, band=None, note=None):
    raw.setdefault("package", ctx.pkg)
    raw.setdefault("host", ctx.host)
    raw.setdefault("events", ctx.events)
    raw.setdefault("envelope", {"cap_bytes": ctx.cap, "threads": 1, "msolve_version": ctx.msolve_version,
                                "driver_rss_limit_bytes": V.DRIVER_RSS_LIMIT})
    raw.setdefault("scoring_reference", SC.reference_block())
    C.write_json(os.path.join(ctx.rd, "raw-result.json"), raw)
    C.write_yaml(os.path.join(ctx.rd, "ladder-table.yaml"), {"ladder_table": {"note": note or "see raw-result.json", "rows": ladder_rows or []}})
    C.write_yaml(os.path.join(ctx.rd, "heur-dflat.yaml"), {"heur_dflat": dflat or {"heuristic": "HEUR-GFPN-DFLAT", "decided_in_this_run": False, "note": note}})
    C.write_yaml(os.path.join(ctx.rd, "cost-band-p64.yaml"), {"cost_band_p64": band or {"status": "not_applicable_in_this_run", "note": note,
                                                                                        "F3": SC.UNDECIDABLE_F3}})


# ============================================================================ child jobs
def child_job(ctx, spec, tag, timeout_s):
    cd = os.path.join(ctx.rd, "child")
    spec = dict(spec)
    spec["cap_bytes"] = ctx.cap
    spec["out"] = os.path.join(C.CACHE_DIR if spec.get("to_cache") else cd, tag)
    os.makedirs(os.path.dirname(spec["out"]), exist_ok=True)
    sp = os.path.join(cd, tag + ".spec.json")
    C.write_json(sp, spec)
    argv = [sys.executable, "-B", os.path.join(HERE, "v2_child.py"), sp]
    rec = V.run_child(argv, os.path.join(cd, tag + ".stdout"), os.path.join(cd, tag + ".stderr"),
                      cap_bytes=ctx.cap, timeout_s=timeout_s, count_instructions=False)
    meta = None
    mp = spec["out"] + ".meta.json"
    if rec.get("outcome") == "ok" and os.path.exists(mp):
        meta = json.load(open(mp))
    return rec, meta, spec["out"]


def field_spec(F):
    return {"p": F.p, "modulus": list(F.modulus)}


def curve_spec(F, E):
    return {"a2": F.coeffs(E.a2), "a4": F.coeffs(E.a4), "a6": F.coeffs(E.a6), "label": E.label}


def build_poly(ctx, F, E, arm, m, seed, tag, timeout_s, beta_override=None, to_cache=False):
    kind, _ = A.parse_arm(arm)
    spec = {"job": "build_poly", "field": field_spec(F), "curve": curve_spec(F, E), "kind": kind, "m": m,
            "sample_seed": seed, "beta_override": beta_override, "to_cache": to_cache}
    rec, meta, out = child_job(ctx, spec, tag, timeout_s)
    if meta is None:
        return None, {"outcome": rec.get("outcome"), "child": _slim(rec), "reason": rec.get("refusal_reason")}
    if meta.get("refused"):
        return None, {"outcome": "refused", "reason": meta["reason"], "child": _slim(rec)}
    pol = load_poly(out + ".npz", F)
    info = {"outcome": "ok", "child": _slim(rec), "meta": {k: v for k, v in meta.items() if k != "support_exponents"},
            "npz": out + ".npz", "npz_sha256": C.sha256_file(out + ".npz"), "npz_bytes": os.path.getsize(out + ".npz")}
    return pol, info


def raw_grid(ctx, F, E, kind, m, x_R, nodes, tag, timeout_s, beta_override=None):
    spec = {"job": "raw_grid", "field": field_spec(F), "curve": curve_spec(F, E), "kind": kind, "m": m,
            "x_R": F.coeffs(x_R), "nodes": list(nodes), "beta_override": beta_override}
    rec, meta, out = child_job(ctx, spec, tag, timeout_s)
    if meta is None or meta.get("refused"):
        return None, None, {"outcome": rec.get("outcome") if meta is None else "refused", "child": _slim(rec),
                            "reason": (meta or {}).get("reason") or rec.get("refusal_reason")}
    Cg = np.load(out + ".npz")["C"]
    monos = A.monomials_box(m, 2 ** (m - 1))
    eqs = A.descend(Cg.reshape(-1, F.n), monos, F.n, F.p)
    try:
        os.remove(out + ".npz")
    except OSError:
        pass
    return eqs, Cg, {"outcome": "ok", "child": _slim(rec), "meta": meta}


def _slim(rec):
    keys = ("outcome", "wall_seconds", "returncode", "timed_out", "rlimit_as_child_getrlimit", "rlimit_as_proc_limits_after_exec",
            "peak_rss_bytes", "peak_vm_bytes", "refusal_reason", "driver_rss_bytes_before_launch", "rusage", "timeout_s", "argv",
            "memory_exhausted_basis", "other_processes")
    return {k: rec.get(k) for k in keys if k in rec}


# ============================================================================ solving one system
def solve(ctx, names, eqs, tag, timeout_s, retain_input, gb_only=False, callgrind_timeout=None):
    p = ctx._p
    sd = os.path.join(ctx.rd, "solver")
    inp = os.path.join(sd, tag + ".ms")
    wi = A.write_msolve_input(inp, names, p, eqs)
    res = {"tag": tag, "input": {"sha256": C.sha256_file(inp), "bytes": os.path.getsize(inp), **wi}}
    out = os.path.join(sd, tag + ".ms.out")
    argv = V.msolve_argv(inp, out, threads=1, gb_only=gb_only)
    rec = V.run_child(argv, os.path.join(sd, tag + ".ms.log"), os.path.join(sd, tag + ".ms.err"), cap_bytes=ctx.cap, timeout_s=timeout_s)
    res["solver"] = _slim(rec)
    res["solver"]["instructions"] = rec.get("instructions")
    res["threads_executed"] = V.threads_from_argv(argv)
    text = ""
    for ext in (".ms.log", ".ms.err"):
        try:
            text += open(os.path.join(sd, tag + ext), errors="replace").read() + "\n"
        except OSError:
            pass
    st = V.parse_msolve_log(text)
    res["f4_rounds"] = st["f4_rounds"]
    res["f4_summary"] = st["f4_summary"]
    res["timings"] = st["timings"]
    res["n_f4_computations"] = text.count("INPUT DATA")
    res["last_f4_round"] = st["f4_rounds"][-1] if st["f4_rounds"] else None
    res["dimension_of_quotient_printed"] = st["dimension_of_quotient"]
    res["no_solution_reported"] = st["no_solution"]
    if rec.get("outcome") == "refused_to_start":
        res.update(outcome="refused_to_start", reason=rec.get("refusal_reason"), D=None, D_defined=False, solutions=[])
        return _retain(res, inp, out, retain_input)
    if gb_only:
        res.update(outcome=rec["outcome"], reason=None, D=None, D_defined=False, solutions=[])
        return _retain(res, inp, out, retain_input)
    kind = payload = None
    sols, sinfo, nfail = [], None, 0
    if rec["outcome"] == "ok":
        kind, payload = V.parse_msolve_param(out)
        if kind == "param":
            sols, sinfo = V.rational_solutions(payload, p, len(names))
            nfail = sum(1 for s in sols if not V.substitute(eqs, s, p))
    outcome, reason = V.classify_solve(rec, st, kind, payload, sinfo, nfail)
    res.update(outcome=outcome, reason=reason, parse_kind=kind, solution_info=sinfo, substitution_failures=nfail)
    if outcome == "ok":
        D = st["dimension_of_quotient"]
        if kind == "none" or (st["no_solution"] and not D):
            res.update(D=None, D_defined=False, D_reason="unit ideal / no solution over the algebraic closure (msolve [-1])", solutions=[])
        else:
            res.update(D=D, D_defined=D is not None, solutions=[s for s in sols if V.substitute(eqs, s, p)])
    else:
        res.update(D=None, D_defined=False, solutions=[])
    if callgrind_timeout and outcome == "ok":
        cg_out = os.path.join(sd, tag + ".cg.ms.out")
        res["instructions_callgrind"] = V.callgrind_instructions(V.msolve_argv(inp, cg_out, threads=1, gb_only=gb_only), sd, tag, ctx.cap, callgrind_timeout)
        try:
            os.remove(cg_out)
        except OSError:
            pass
    return _retain(res, inp, out, retain_input)


def _retain(res, inp, out, retain_input):
    """R-10: keep the msolve input where required (sha256 always recorded); drop large outputs."""
    if not retain_input or os.path.getsize(inp) > RETAIN_MAX_BYTES:
        res["input"]["retained"] = False
        os.remove(inp)
    else:
        res["input"]["retained"] = True
    if os.path.exists(out):
        res["output_sha256"] = C.sha256_file(out)
        if os.path.getsize(out) > RETAIN_MAX_BYTES:
            os.remove(out)
            res["output_retained"] = False
        else:
            res["output_retained"] = True
    return res


# ============================================================================ lifting + certificates
def lift_and_certify(ctx, F, E, cv, shape, arm, kind, m, rs, nsub, G, k, R, sols, target, target_kind, counter, extra=None):
    rels, diags, certs = [], [], []
    saved = E.counter
    for s in sols:
        rr, dg = L.lift(kind, s, E, rs, R, counter)
        diags.append(dg)
        rels += rr
    E.counter = saved
    # deduplicate across solutions (R-3)
    seen, uniq = set(), []
    for r in rels:
        key = tuple(sorted((tuple(F.coeffs(P[0])), tuple(F.coeffs(P[1] if s == 1 else -P[1]))) for P, s in zip(r["points"], r["signs"])))
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    verified = 0
    for j, r in enumerate(uniq):
        cert = L.make_certificate(F, cv, shape, arm, kind, m, rs, nsub, G, k, R, r, ctx.rid, target, j, target_kind, extra)
        ok, npts, reasons = VI.verify(cert)
        cert["independent_verification"] = {"verifier": "experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py",
                                             "pass": ok, "lifted_points": npts, "reasons": reasons}
        name = "decomposition_%s_t%s_r%d.json" % (arm, target, j)
        C.write_json(os.path.join(ctx.rd, "certificates", name), cert)
        certs.append({"path": "certificates/" + name, "target": target, "verified": ok, "lifted_points": npts,
                      "relation_mod_T": r["relation_mod_T"]})
        verified += ok
    return {"n_relations": len(uniq), "n_relations_verified": verified, "lift_diagnostics": diags[:40], "certificates": certs,
            "n_relation_mod_T": sum(1 for r in uniq if r["relation_mod_T"])}


# ============================================================================ FIXTURE F-1..F-3 (n = m = 3)
FIXTURE_EXPECTED = {"raw_x": 384, "raw_u": 384, "S3": 64, "S3_rescaled": 64, "torsion_S3_norm": 64, "torsion_S3_rq": 16}
FIXTURE_STRUCTURE_EXPECTED = {"norm_support_count": 35, "norm_total_degree": 4, "rq_deg_A_sigma": 2, "rq_deg_B_sigma": 1,
                              "rq_n_monomials_A_plus_wB": 14}


def fixture_arms(m):
    return ["raw_x", "raw_u", "S%d" % m, "S%d_rescaled" % m, "torsion_S%d_norm" % m, "torsion_S%d_rq" % m]


def cmd_fixture(args):
    ctx = Ctx()
    field_self_test()
    fx = C.fixture_n3(args.p)
    raw = fixture_core(ctx, fx, 3, FIXTURE_EXPECTED, FIXTURE_STRUCTURE_EXPECTED, "fixture_n3")
    finish(ctx, raw, ladder_rows=[{"fixture": "n=m=3", "p": fx["F"].p, "gate_pass": raw.get("gate_pass"), "target_kind": "fixture"}],
           note="fixture package (n = m = 3); not a ladder cell")


def fixture_core(ctx, fx, m, expected, structure_expected, shape_label):
    """F-1, F-2(a), F-2(b), F-3 on one prime. Generic in m so that its code path can be exercised on a toy
    object during development WITHOUT solving the fixture's own n = m = 3 systems."""
    t0 = time.time()
    F, E, cv = fx["F"], fx["E"], fx["cv"]
    ctx._p = F.p
    arms = fixture_arms(m)
    a_S, a_Sr, a_norm, a_rq = arms[2], arms[3], arms[4], arms[5]
    g2 = 2 ** (m - 1) * math.factorial(m)
    raw = {"kind": "fixture_F1_F3", "p": F.p, "n": F.n, "m": m, "field": F.describe(), "curve": cv.get("model"),
           "data_source": {"path": fx.get("source"), "sha256": fx.get("source_sha256"),
                           "use": "curves, beta, target x_R and expected values only (AC-4)"},
           "expected_fixture_F1": expected, "expected_structure": structure_expected}
    # (beta, lam) FIXED BEFORE ANY TARGET IS DRAWN (quantifier order)
    rs = A.rescaling(E, beta_override=fx["beta"])
    raw["rescaling"] = A.public_rescaling(rs)
    raw["rescaling_fixed_at"] = C.now()
    raw["beta_equals_smallest_nonsquare"] = fx["beta"] == A.smallest_nonsquare(F.p)
    raw["curve_checks"] = {"b_is_square_in_Fq": F.is_square(E.a4), "a2sq_minus_4b_is_square_in_Fq": F.is_square(E.a2 * E.a2 - 4 * E.a4),
                           "json_b_is_square": fx.get("json_b_is_square"), "json_disc_is_square": fx.get("json_disc_is_square")}
    if rs["refused"]:
        raw.update(run_status="failed", failure_class="specification_error", gate_pass=False,
                   reason="fixture curve refused the DC-3 rescaling: %s" % rs["reason"])
        return raw
    N = C.curve_order_pari(F, E)
    G = E.random_point(random.Random("%d:v2:fixture:%d:basepoint" % (C.SEED_CURVES, F.p)))
    raw["group"] = {"order_pari_ellcard": N, "N_times_G_is_O": E.mul(N, G) is None}
    wd = {a: C.watchdog(ctx.plan, a, m) for a in arms}
    btime = ctx.plan["watchdogs"]["builder_timeout_s"]["m%d" % m]
    cgtime = ctx.plan["watchdogs"]["callgrind_timeout_s"].get("m%d" % m)
    pols, builds = {}, {}
    for arm in (a_S, a_Sr, a_norm, a_rq):
        seed = "%d:v2:build:%d:%s:%s:%d" % (C.SEED_CURVES, F.p, shape_label, arm, m)
        pol, info = build_poly(ctx, F, E, arm, m, seed, "fixture_%s" % arm, btime, beta_override=fx["beta"])
        pols[arm], builds[arm] = pol, info
        if pol is not None:
            np.savez_compressed(os.path.join(ctx.rd, "polynomials", "fixture_%s.npz" % arm), C=pol.C, monos=np.array(pol.monos))
    raw["builds"] = builds
    if any(p_ is None for p_ in pols.values()):
        raw.update(run_status="failed", failure_class="infrastructure_error", gate_pass=False, reason="a fixture polynomial build did not complete")
        return raw
    struct = {
        "norm_support_equals_S_support": sorted(map(tuple, pols[a_norm].support)) == sorted(map(tuple, pols[a_S].support)),
        "norm_support_count": len(pols[a_norm].support), "S_support_count": len(pols[a_S].support),
        "norm_total_degree": pols[a_norm].meta["support_total_degree"],
        "rq_deg_A_sigma": pols[a_rq].meta.get("deg_A_sigma"), "rq_deg_B_sigma": pols[a_rq].meta.get("deg_B_sigma"),
        "rq_n_monomials_A_plus_wB": pols[a_rq].meta.get("n_monomials_A_plus_wB"),
        "single_flip_pass": {a: builds[a]["meta"]["single_flip_test"]["pass"] for a in builds},
        "held_out_mismatches": {a: builds[a]["meta"]["held_out_mismatches"] for a in builds}}
    struct["pass"] = (struct["norm_support_equals_S_support"] and all(struct[k] == v for k, v in (structure_expected or {}).items())
                      and all(struct["single_flip_pass"].values()) and all(v == 0 for v in struct["held_out_mismatches"].values()))
    raw["structure_checks"] = struct
    px = A.pool_x(E, 400)
    pu = A.pool_u(E, rs["lam_obj"], 400)
    K1 = 2 ** (m - 1) + 1

    def run_target(t):
        out = {"target": t["label"], "kind": t["kind"], "x_R": F.coeffs(t["x_R"]), "arms": {}}
        for arm in arms:
            kind, _ = A.parse_arm(arm)
            ctr = OpCount(F.n)
            tag = "fx_%s_%s" % (t["label"], arm)
            if kind in ("raw_x", "raw_u"):
                nodes = sorted(random.Random("%d:v2:grid:%d:%s:%s:%d:%s" % (C.SEED_CURVES, F.p, shape_label, arm, m, t["label"])).sample(px if kind == "raw_x" else pu, K1))
                eqs, _Cg, ginfo = raw_grid(ctx, F, E, kind, m, t["x_R"], nodes, tag, btime, beta_override=fx["beta"])
                if eqs is None:
                    out["arms"][arm] = {"outcome": "infrastructure_error", "reason": ginfo}
                    continue
                names = A.varnames(kind, m)
                cons = ginfo["meta"]["construction_ops"]
            else:
                val = t["x_R"] if kind != "norm" else t["x_R"] + E.a4 / t["x_R"]
                names, eqs = A.system_for_target(pols[arm], val, rs, ctr)
                cons = ctr.as_dict()
            r = solve(ctx, names, eqs, tag, wd[arm]["per_target_timeout_s"], retain_input=True, callgrind_timeout=cgtime)
            row = {k: r.get(k) for k in ("outcome", "reason", "D", "D_defined", "D_reason", "threads_executed", "input", "solver", "f4_summary",
                                         "timings", "n_f4_computations", "last_f4_round", "instructions_callgrind", "substitution_failures",
                                         "dimension_of_quotient_printed", "parse_kind", "solution_info")}
            row["construction_ops"] = cons
            row["n_rational_solutions"] = len(r["solutions"])
            row["_solutions"] = r["solutions"]
            out["arms"][arm] = row
        return out

    rows, replaced = [], []
    for t in fx["regression"]:
        t = dict(t, label="reg%d" % t["index"])
        rows.append(run_target(t))
    rngF = random.Random("%d:v2:fixture:%d:fresh" % (C.SEED_TARGETS, F.p))
    fresh_ok, draws = 0, 0
    while fresh_ok < 2 and draws < 12:
        k = rngF.randrange(1, N)
        R = E.mul(k, G)
        draws += 1
        if R is None or R[0] == 0:
            continue
        t = {"label": "fresh%d" % draws, "kind": "fresh_random", "k": k, "R": R, "x_R": R[0], "index": draws}
        row = run_target(t)
        nongeneric = [a for a, v in row["arms"].items() if v.get("outcome") in ("positive_dimensional", "degenerate_parametrisation")]
        if nongeneric:
            row["replaced"] = True
            row["replaced_reason"] = "non-generic system in arm(s) %s (DC-6 R-5); reported, replaced by the next seeded target, neither pass nor fail" % nongeneric
            replaced.append(row)
            continue
        row["replaced"] = False
        row["_t"] = t
        rows.append(row)
        fresh_ok += 1
    rngP = random.Random("%d:v2:fixture:%d:planted" % (C.SEED_TARGETS, F.p))
    planted_rows = []
    for j in range(2):
        R, us = None, None
        for _try in range(400):
            us = rngP.sample(pu, m)
            pts = [E.lift_x(rs["lam_obj"] * F(u)) for u in us]
            if any(P is None for P in pts):
                continue
            R = None
            for P in pts:
                R = E.add(R, P)
            if R is not None and R[0] != 0:
                break
            R = None
        if R is None:
            planted_rows.append({"target": "planted%d" % j, "kind": "planted_square_nm", "arms": {}, "reason": "no planted sum found in 400 tries"})
            continue
        t = {"label": "planted%d" % j, "kind": "planted_square_nm", "k": 1, "R": R, "x_R": R[0], "index": j}
        row = run_target(t)
        row["planted_u"] = us
        pk_sigma, pk_w = L.g2_orbit_key_of_u(us, rs["beta"], F.p)
        row["planted_orbit_key"] = {"sigma": list(pk_sigma), "w": pk_w}
        row["_t"] = t
        planted_rows.append(row)
    # lifting + certificates on fresh (known scalar k, G) and planted (G := R, k := 1) targets, every arm
    for row in rows + planted_rows:
        t = row.get("_t")
        if t is None:
            for a in row["arms"].values():
                a["lifting"] = "not applicable: regression target is an x_R value only (no known scalar)"
            continue
        Gt, kt = (G, t["k"]) if t["kind"] == "fresh_random" else (t["R"], 1)
        for arm, a in row["arms"].items():
            if a.get("outcome") != "ok":
                continue
            kind, _ = A.parse_arm(arm)
            ctr = OpCount(F.n)
            note = ("k = 1 and G := R for a planted target (v1 constructed-solvable rule); admissible here only because n = m (DC-3 F-2(b))"
                    if t["kind"] == "planted_square_nm" else None)
            lc = lift_and_certify(ctx, F, E, cv, shape_label, arm, kind, m, rs if A.base_of(kind) == "x_over_lam_in_Fp" else None,
                                  N, Gt, kt, t["R"], a["_solutions"], row["target"], t["kind"], ctr, extra={"known_scalar_note": note})
            lc["lifting_ops"] = ctr.as_dict()
            a["lifting"] = lc
    f1 = []
    for row in rows:
        per = {arm: row["arms"][arm].get("D") for arm in arms}
        exp = expected or {}
        f1.append({"target": row["target"], "kind": row["kind"], "D": per, "pass": bool(exp) and all(per[a] == exp.get(a) for a in arms),
                   "mismatch_arms": [a for a in arms if per[a] != exp.get(a)]})
    f2a, f3 = [], []
    for row in rows:
        Du, Dq, Dsr = row["arms"]["raw_u"].get("D"), row["arms"][a_rq].get("D"), row["arms"][a_Sr].get("D")
        f2a.append({"target": row["target"], "D_raw_u": Du, "D_rq": Dq, "G2_order": g2, "pass": bool(Du and Dq and Du == g2 * Dq),
                    "nonfreeness_G2_D_rq_over_D_raw_u": (g2 * Dq / Du) if Du and Dq else None})
        f3.append({"target": row["target"], "D_S_rescaled": Dsr, "D_rq": Dq, "ratio": (Dsr / Dq) if Dsr and Dq else None,
                   "expected_ratio": 2 ** (m - 1), "pass": bool(Dsr and Dq and Dsr == 2 ** (m - 1) * Dq)})
    lfl = SC.score_like_for_like({"raw_x": {r["target"]: r["arms"]["raw_x"].get("D") for r in rows},
                                  "raw_u": {r["target"]: r["arms"]["raw_u"].get("D") for r in rows},
                                  "S": {r["target"]: r["arms"][a_S].get("D") for r in rows},
                                  "S_rescaled": {r["target"]: r["arms"][a_Sr].get("D") for r in rows},
                                  "rq": {r["target"]: r["arms"][a_rq].get("D") for r in rows},
                                  "norm": {r["target"]: r["arms"][a_norm].get("D") for r in rows}}, m)
    f2b = []
    for row in planted_rows:
        if "_t" not in row:
            f2b.append({"target": row["target"], "pass": False, "reason": row.get("reason")})
            continue
        ru, rq_ = row["arms"]["raw_u"], row["arms"][a_rq]
        raw_keys, zero_u = {}, 0
        for s in ru.get("_solutions") or []:
            if any(v % F.p == 0 for v in s):
                zero_u += 1
                continue
            key = L.g2_orbit_key_of_u(s, rs["beta"], F.p)
            raw_keys[key] = raw_keys.get(key, 0) + 1
        rq_keys, rq_rej = set(), []
        for s in rq_.get("_solutions") or []:
            _rels, dg = L.lift("rq", s, E, rs, row["_t"]["R"])
            if dg.get("reject", "").startswith(("step1", "step2", "w_sign")):
                rq_rej.append({"solution": s, "reject": dg["reject"]})
                continue
            rq_keys.add((tuple(s[:m]), s[m]))
        table = [{"sigma": list(key[0]), "w": key[1], "raw_u_rational_solutions_in_orbit": raw_keys.get(key, 0), "rq_solution_lifts": key in rq_keys}
                 for key in sorted(set(raw_keys) | rq_keys)]
        planted_key = L.g2_orbit_key_of_u(row["planted_u"], rs["beta"], F.p)
        ok = ru.get("outcome") == "ok" and rq_.get("outcome") == "ok" and set(raw_keys) == rq_keys and planted_key in rq_keys
        f2b.append({"target": row["target"], "pass": ok, "bijection_table": table, "raw_u_solutions_with_u_zero_excluded": zero_u,
                    "rq_solutions_rejected_in_lifting_steps_1_3": rq_rej, "planted_orbit_present": planted_key in rq_keys,
                    "D_raw_u": ru.get("D"), "D_rq": rq_.get("D")})
    n_fresh = len([r for r in rows if r["kind"] == "fresh_random"])
    gate = (struct["pass"] and n_fresh == 2 and all(x["pass"] for x in f1) and all(x["pass"] for x in f2a)
            and len(f2b) >= 2 and all(x["pass"] for x in f2b) and all(x["pass"] for x in f3))
    certs = [c for row in rows + planted_rows for a in row["arms"].values() if isinstance(a.get("lifting"), dict) for c in a["lifting"]["certificates"]]
    all_cert_ok = all(c["verified"] for c in certs)
    infra = [(row["target"], arm) for row in rows + planted_rows for arm, a in row["arms"].items()
             if a.get("outcome") in ("refused_to_start", "crashed", "infrastructure_error", "timeout", "memory_exhausted")]
    mism = sorted({a for x in f1 for a in x["mismatch_arms"]})
    if infra:
        status, fclass = "failed", "infrastructure_error"
    elif certs and not all_cert_ok:
        status, fclass = "invalid", "invalid_measurement"
    elif gate:
        status, fclass = "completed_valid", None
    else:
        status, fclass = "failed", "implementation_error"
    for row in rows + planted_rows + replaced:
        row.pop("_t", None)
        for a in row["arms"].values():
            a.pop("_solutions", None)
    raw.update({
        "run_status": status, "failure_class": fclass, "gate_pass": gate,
        "ac5_reading": (("implementation or derivation: the mismatch is confined to raw_u and/or %s, the two Coordinator-derived expected "
                         "values (AC-5 names both explanations)" % a_Sr) if mism and set(mism) <= {"raw_u", a_Sr} and not infra else
                        ("implementation signal (DC-3 gate); never a mathematical result about the quotient" if not gate and not infra else
                         ("infrastructure signal; never a mathematical result" if infra else None))),
        "infrastructure_rows": infra, "targets": rows, "replaced_fresh_targets": replaced, "planted_targets": planted_rows,
        "fixture_F1": f1, "fixture_F2a": f2a, "fixture_F2b": f2b, "fixture_F3": f3, "like_for_like_T2_T3_exercised": lfl,
        "certificate": ({"kind": "decomposition", "verified": all_cert_ok, "count": len(certs),
                         "verifier": "experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py"} if certs else
                        {"kind": "none", "verified": None, "verifier": None, "note": "no relation lifted on this fixture"}),
        "metrics": {"gate_pass": gate, "structure_pass": struct["pass"], "fixture_F1_pass": all(x["pass"] for x in f1),
                    "fixture_F2a_pass": all(x["pass"] for x in f2a), "fixture_F2b_pass": bool(f2b) and all(x["pass"] for x in f2b),
                    "fixture_F3_pass": all(x["pass"] for x in f3), "n_targets_F1": len(f1), "n_fresh": n_fresh, "n_planted": len(f2b),
                    "n_replaced_fresh": len(replaced), "wall_seconds": round(time.time() - t0, 1)},
        "seeds": {"fresh_targets": "random.Random('%d:v2:fixture:%d:fresh')" % (C.SEED_TARGETS, F.p),
                  "planted_targets": "random.Random('%d:v2:fixture:%d:planted')" % (C.SEED_TARGETS, F.p),
                  "basepoint": "random.Random('%d:v2:fixture:%d:basepoint')" % (C.SEED_CURVES, F.p),
                  "builds": "random.Random('%d:v2:build:%d:%s:<arm>:%d')" % (C.SEED_CURVES, F.p, shape_label, m),
                  "grid_nodes": "random.Random('%d:v2:grid:%d:%s:<arm>:%d:<target>')" % (C.SEED_CURVES, F.p, shape_label, m)},
    })
    return raw

# ============================================================================ F-4 (n = m = 4), NOT blocking
def cmd_fixture4(args):
    ctx = Ctx()
    t0 = time.time()
    fx = C.fixture_n4()
    F, E, cv = fx["F"], fx["E"], fx["cv"]
    ctx._p = F.p
    raw = {"kind": "fixture_F4_secondary", "blocking": False, "p": F.p, "n": F.n, "m": 4, "field": F.describe(), "curve": cv["model"],
           "data_source": {"path": fx["source"], "sha256": fx["source_sha256"]}, "expected_red_team": fx["expected"],
           "construction_path_note": ("even n with b a square and beta = 1 from the data file: a DIFFERENT construction path from DC-3's odd-n "
                                      "non-square beta (review-report.yaml lines 717-721); reported, not blocking")}
    rs = A.rescaling(E, beta_override=fx["beta"])
    raw["rescaling"] = A.public_rescaling(rs)
    if rs["refused"]:
        raw.update(run_status="failed", failure_class="specification_error", reason=rs["reason"])
        finish(ctx, raw, note="F-4 refused")
        return
    N = C.curve_order_pari(F, E)
    G = E.random_point(random.Random("%d:v2:fixture4:%d:basepoint" % (C.SEED_CURVES, F.p)))
    rng = random.Random("%d:v2:fixture4:%d:fresh" % (C.SEED_TARGETS, F.p))
    arms = ["S4", "S4_rescaled", "torsion_S4_norm", "torsion_S4_rq"]
    pols, builds = {}, {}
    for arm in arms:
        pol, info = build_poly(ctx, F, E, arm, 4, "%d:v2:build:%d:fixture_n4:%s:4" % (C.SEED_CURVES, F.p, arm), "f4_%s" % arm,
                               ctx.plan["watchdogs"]["builder_timeout_s"]["m4"], beta_override=fx["beta"])
        pols[arm], builds[arm] = pol, info
    raw["builds"] = builds
    rows = []
    for i in range(2):
        k = rng.randrange(1, N)
        R = E.mul(k, G)
        row = {"target": i, "k": k, "x_R": F.coeffs(R[0]), "arms": {}}
        for arm in arms:
            if pols[arm] is None:
                row["arms"][arm] = {"outcome": "not_attempted", "reason": "build did not complete"}
                continue
            kind, _ = A.parse_arm(arm)
            val = R[0] if kind != "norm" else R[0] + E.a4 / R[0]
            ctr = OpCount(F.n)
            names, eqs = A.system_for_target(pols[arm], val, rs, ctr)
            r = solve(ctx, names, eqs, "f4_t%d_%s" % (i, arm), C.watchdog(ctx.plan, arm, 4)["per_target_timeout_s"], retain_input=True)
            row["arms"][arm] = {k2: r.get(k2) for k2 in ("outcome", "reason", "D", "D_defined", "threads_executed", "input", "solver", "timings", "last_f4_round")}
            row["arms"][arm]["construction_ops"] = ctr.as_dict()
        rows.append(row)
    match = {arm: all(r["arms"][arm].get("D") == fx["expected"][arm] for r in rows) for arm in fx["expected"]}
    outs = [a.get("outcome") for r in rows for a in r["arms"].values()]
    allok = all(o == "ok" for o in outs)
    fcl = None if allok else ("resource_exhaustion" if any(o in ("timeout", "memory_exhausted") for o in outs) else
                              ("infrastructure_error" if any(o in ("crashed", "refused_to_start", "not_attempted") for o in outs) else "implementation_error"))
    raw.update(run_status="completed_valid" if allok else "failed", failure_class=fcl,
               targets=rows, matches_red_team_values=match,
               metrics={"matches_red_team_values": match, "wall_seconds": round(time.time() - t0, 1)},
               certificate={"kind": "none", "verified": None, "verifier": None, "note": "degree-only secondary fixture"})
    finish(ctx, raw, note="F-4 secondary fixture (not blocking)")


# ============================================================================ ANCHOR IDENTITY (rulings.DC-5)
def _parse_ms_file(path):
    """Read a comparator msolve input file as DATA (names, p, equations)."""
    txt = open(path).read()
    head, rest = txt.split("\n", 1)
    names = head.strip().split(",")
    pline, body = rest.split("\n", 1)
    p = int(pline.strip())
    eqs = []
    for eqtxt in body.replace("\n", "").split(","):
        eq = {}
        for term in eqtxt.split("+"):
            term = term.strip()
            if not term:
                continue
            parts = term.split("*")
            c = int(parts[0]) if parts[0].lstrip("-").isdigit() else 1
            mono = parts[1:] if parts[0].lstrip("-").isdigit() else parts
            e = [0] * len(names)
            for f in mono:
                if "^" in f:
                    v, k = f.split("^")
                    e[names.index(v)] += int(k)
                else:
                    e[names.index(f)] += 1
            eq[tuple(e)] = (eq.get(tuple(e), 0) + c) % p
        eqs.append({k: v for k, v in eq.items() if v})
    return names, p, eqs


def _fq_poly_from_descended(eqs, F):
    """Reassemble the F_q polynomial sum_j eq_j z^j (inverse of the Weil descent split)."""
    out = {}
    for j, eq in enumerate(eqs):
        for a, c in eq.items():
            out.setdefault(a, [0] * F.n)[j] = c
    return {a: F.from_coeffs(cs) for a, cs in out.items()}


def _proportional(P, Q, F):
    if set(P) != set(Q):
        return False, "different supports"
    a0 = next(iter(P))
    lam = P[a0] / Q[a0]
    return all(P[a] == lam * Q[a] for a in P), None


def cmd_anchor_identity(args):
    ctx = Ctx()
    t0 = time.time()
    p = 16777291
    rung = C.ladder_entry(p)
    F = C.ladder_field(rung)
    ctx._p = p
    shape = "random_no2torsion"
    E, cv = C.ladder_curve(F, rung, shape)
    raw = {"kind": "anchor_identity", "control": "jv_anchor_system_trace_identity (amendment rulings.DC-5 (2))",
           "p": p, "n": 5, "m": 4, "arm": "S4", "curve_shape": shape, "curve": {k: cv[k] for k in ("a2", "a4", "a6", "order")},
           "msolve_version": ctx.msolve_version}
    wa = C.watchdog(ctx.plan, "S4", 4)          # uniform per (arm, m): the same S4|m4 watchdog as every S4 cell (AC-6)
    # the anchor curve must be the curve of the archived anchor (RUN-GFPN-61bba9) and of the comparator's CURVES
    a61 = json.load(open(os.path.join(C.ARCHIVED_ANCHOR_RUN, "raw-result.json")))["parameters"]
    curve_identity = {"archived_a4": a61["a4"], "archived_a6": a61["a6"], "ladder_a4": cv["a4"], "ladder_a6": cv["a6"],
                      "equal": a61["a4"] == cv["a4"] and a61["a6"] == cv["a6"] and a61["p"] == p}
    raw["curve_identity_with_archived_anchor"] = curve_identity
    # (1) the independent comparator, RUN (not imported, not copied), under the cap
    cdir = os.path.join(ctx.rd, "comparator")
    os.makedirs(cdir, exist_ok=True)
    comp = {"script": os.path.relpath(C.COMPARATOR, C.REPO), "script_sha256": C.sha256_file(C.COMPARATOR), "python": C.SAGE_PYTHON}
    rec = V.run_child([C.SAGE_PYTHON, C.COMPARATOR, cdir], os.path.join(cdir, "stdout.log"), os.path.join(cdir, "stderr.log"),
                      cap_bytes=ctx.cap, timeout_s=ctx.plan["watchdogs"]["comparator_timeout_s"], count_instructions=False)
    comp["child"] = _slim(rec)
    res_path = os.path.join(cdir, "k4a_results.json")
    comp_ok = rec.get("outcome") == "ok" and os.path.exists(res_path)
    raw["comparator"] = comp
    if not comp_ok:
        raw.update(run_status="failed", failure_class="infrastructure_error", gate_pass=False, reason="comparator did not complete")
        finish(ctx, raw, note="anchor identity: comparator failed")
        return
    cres = json.load(open(res_path))
    c61 = cres.get("RUN-GFPN-61bba9", {})
    comp["comparator_reported_error"] = c61.get("error")
    comp_ms = os.path.join(cdir, "anchor25_random.ms")
    if c61.get("error") is not None or "random_target_x_R" not in c61 or not os.path.exists(comp_ms):
        raw.update(run_status="failed", failure_class="infrastructure_error", gate_pass=False,
                   reason="comparator output lacks the RUN-GFPN-61bba9 random target or its .ms file")
        finish(ctx, raw, note="anchor identity: comparator output incomplete")
        return
    xR_comp = F.from_coeffs(c61["random_target_x_R"])
    # (2) our system: S4 polynomial on the x-base (capped build child)
    pol, binfo = build_poly(ctx, F, E, "S4", 4, "%d:v2:build:%d:%s:S4:4:anchor" % (C.SEED_CURVES, p, shape), "anchor_S4",
                            ctx.plan["watchdogs"]["builder_timeout_s"]["m4"])
    raw["build"] = binfo
    if pol is None:
        raw.update(run_status="failed", failure_class="infrastructure_error", gate_pass=False, reason="S4 build did not complete")
        finish(ctx, raw, note="anchor identity: build failed")
        return
    G = C.base_point(E, int(cv["subgroup_prime"]), int(cv["cofactor"]), p, shape)
    own = C.ladder_targets(E, G, int(cv["subgroup_prime"]), p, shape, 3)
    targets = [{"label": "comparator_random", "x_R": xR_comp, "k": None}] + [{"label": "v2_t%d" % t["index"], "x_R": t["R"][0], "k": t["k"]} for t in own]
    archived = []
    for i in range(5):
        lp = os.path.join(C.ARCHIVED_ANCHOR_RUN, "anchor_t%d.ms.log" % i)
        archived.append({"log": os.path.relpath(lp, C.REPO), "sha256": C.sha256_file(lp),
                         "trace": V.trace_tuple(V.parse_msolve_log(open(lp).read())),
                         "summary": V.parse_msolve_log(open(lp).read())["f4_summary"]})
    ref_trace = archived[0]["trace"]
    raw["archived_traces"] = [{k: v for k, v in a.items() if k != "trace"} | {"n_rounds": len(a["trace"]), "identical_to_t0": a["trace"] == ref_trace} for a in archived]
    rows = []
    for t in targets:
        names, eqs = A.system_for_target(pol, t["x_R"], None)
        degs = [max((sum(a) for a in eq), default=0) for eq in eqs]
        r = solve(ctx, names, eqs, "anchor_%s" % t["label"], wa["per_target_timeout_s"], retain_input=True, gb_only=True)
        tr = [(x["deg"], x["pairs"], x["rows"], x["cols"], x["new"], x["zero"]) for x in r["f4_rounds"]]
        row = {"target": t["label"], "k": t["k"], "x_R": F.coeffs(t["x_R"]), "n_variables": len(names), "n_equations": len(eqs),
               "total_degrees": degs, "union_support": r["input"]["union_support"], "n_terms": r["input"]["n_terms"],
               "outcome": r["outcome"], "threads_executed": r["threads_executed"], "wall_seconds": r["solver"].get("wall_seconds"),
               "msolve_cpu": r["timings"].get("overall_cpu"), "pairs_reduced": r["f4_summary"].get("pairs_reduced"),
               "trace_identical_to_archived": tr == ref_trace, "n_rounds": len(tr), "input": r["input"], "solver": r["solver"],
               "sel_column_identical_to_archived": [x["sel"] for x in r["f4_rounds"]] == [x["sel"] for x in V.parse_msolve_log(open(os.path.join(C.ARCHIVED_ANCHOR_RUN, "anchor_t0.ms.log")).read())["f4_rounds"]],
               "_trace": tr}
        row["structure_pass"] = (len(names) == 4 and len(eqs) == 5 and all(d == 8 for d in degs) and row["union_support"] == 495)
        if t["label"] == "comparator_random":
            cn, cp, ceqs = _parse_ms_file(comp_ms)
            ours_q = _fq_poly_from_descended(eqs, F)
            theirs_q = _fq_poly_from_descended(ceqs, F)
            prop, why = _proportional(ours_q, theirs_q, F)
            cterms = sum(len(e) for e in ceqs)
            row["comparator_system"] = {"file_sha256": C.sha256_file(comp_ms), "n_terms": cterms, "varnames": cn,
                                        "same_term_count": cterms == row["n_terms"], "Fq_polynomial_proportional": prop, "why_not": why}
            rc = solve(ctx, cn, ceqs, "anchor_comparator_system", wa["per_target_timeout_s"], retain_input=True, gb_only=True)
            trc = [(x["deg"], x["pairs"], x["rows"], x["cols"], x["new"], x["zero"]) for x in rc["f4_rounds"]]
            row["comparator_system"]["trace_identical_to_archived"] = trc == ref_trace
            row["comparator_system"]["outcome"] = rc["outcome"]
            row["comparator_system"]["_trace"] = trc
            row["comparator_system"]["input"] = rc["input"]
            row["structure_pass"] = row["structure_pass"] and prop and cterms == row["n_terms"]
        rows.append(row)
    walls = sorted(r["wall_seconds"] for r in rows if r["outcome"] == "ok" and r["wall_seconds"] is not None)
    med = walls[len(walls) // 2] if walls else None
    substitution = None
    if ctx.msolve_version != "0.6.5":
        substitution = ("solver build %s differs from msolve 0.6.5: trace identity is read against the fresh run of the comparator's "
                        "system on the same build (rulings.DC-5 (2)); recorded" % ctx.msolve_version)
        ref = rows[0]["comparator_system"].get("_trace")
        for r in rows:
            r["trace_identical_to_reference"] = r.pop("_trace", None) == ref
        trace_ok = all(r["trace_identical_to_reference"] for r in rows)
    else:
        for r in rows:
            r["trace_identical_to_reference"] = r["trace_identical_to_archived"]
            r.pop("_trace", None)
        trace_ok = all(r["trace_identical_to_archived"] for r in rows) and rows[0]["comparator_system"]["trace_identical_to_archived"]
    rows[0]["comparator_system"].pop("_trace", None)
    gate = (all(r["structure_pass"] for r in rows) and trace_ok and curve_identity["equal"]
            and len([r for r in rows if r["target"] != "comparator_random"]) >= 3)
    infra = [r["target"] for r in rows if r["outcome"] != "ok"]
    raw.update(run_status="failed" if infra else ("completed_valid" if gate else "failed"),
               failure_class="infrastructure_error" if infra else (None if gate else "implementation_error"),
               gate_pass=gate, targets=rows, solver_substitution=substitution,
               wall_clock_ratio_NON_BLOCKING={"median_wall_seconds_msolve_g1_t1": med, "JV_own_C_F4_25bit_s": 17.01,
                                              "ratio": (med / 17.01) if med else None,
                                              "reference": "inputs/JOUX-VITSE-2010-157/paper_fulltext.md lines 696-698 (2.6 GHz Core 2 Duo, line 684)",
                                              "host": ctx.host, "blocking": False},
               v1_outcome_note="v1 n4_published_timing_anchor stays FAILED on its literal band (RUN-GFPN-61bba9, ratio 0.470); not re-scored",
               metrics={"gate_pass": gate, "n_targets": len(rows), "median_wall_seconds": med, "wall_seconds": round(time.time() - t0, 1)},
               certificate={"kind": "none", "verified": None, "verifier": None, "note": "system and trace identity control; no decomposition accepted"})
    finish(ctx, raw, note="anchor identity control (blocking)")


# ============================================================================ FROZEN CONTROLS
def cmd_controls(args):
    ctx = Ctx()
    t0 = time.time()
    checks = []

    def rec(name, ok, detail=None):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        log(name, "PASS" if ok else "FAIL")

    field_self_test()
    rec("field_self_test_evaluators_agree_n3_n4_n5", True)
    # --- degenerate_symmetrization_identity at n = m = 3 (fixture field, 4111) and n = 5, m = 3, 4 (ladder 4111)
    fx = C.fixture_n3(4111)
    F, E = fx["F"], fx["E"]
    ctx._p = F.p
    px = A.pool_x(E, 400)
    pol, info = build_poly(ctx, F, E, "identity", 3, "%d:v2:build:%d:fixture_n3:identity:3" % (C.SEED_CURVES, F.p), "ctl_identity_n3",
                           ctx.plan["watchdogs"]["builder_timeout_s"]["m3"])
    rngc = random.Random("%d:v2:controls:identity" % C.SEED_TARGETS)
    N = C.curve_order_pari(F, E)
    G = E.random_point(random.Random("%d:v2:fixture:%d:basepoint" % (C.SEED_CURVES, F.p)))
    Rr = E.mul(rngc.randrange(1, N), G)
    Rp = None
    while Rp is None or Rp[0] == 0:
        xs = rngc.sample(px, 3)
        Rp = None
        for x in xs:
            Rp = E.add(Rp, E.lift_x(F(x)))
    for label, R in (("random", Rr), ("planted", Rp)):
        nodes = sorted(random.Random("ctl:%s" % label).sample(px, 5))
        eqs_raw, Cg, ginfo = raw_grid(ctx, F, E, "raw_x", 3, R[0], nodes, "ctl_raw_%s" % label, ctx.plan["watchdogs"]["builder_timeout_s"]["m3"])
        same_coeffs = pol is not None and Cg is not None and A.raw_coefficients_equal_identity(Cg, pol, R[0])
        names, eqs_id = A.system_for_target(pol, R[0], None) if pol is not None else (None, None)
        wd = C.watchdog(ctx.plan, "identity", 3)["per_target_timeout_s"]
        s_id = solve(ctx, A.varnames("identity", 3), eqs_id, "ctl_identity_%s" % label, wd, retain_input=True) if eqs_id else None
        s_raw = solve(ctx, A.varnames("raw_x", 3), eqs_raw, "ctl_rawx_%s" % label, wd, retain_input=True) if eqs_raw else None
        ok = (same_coeffs and s_id and s_raw and s_id["outcome"] == s_raw["outcome"] == "ok" and s_id["D"] == s_raw["D"]
              and sorted(s_id["solutions"]) == sorted(s_raw["solutions"]))
        if label == "planted":
            ok = ok and sorted(xs) in [sorted(s) for s in s_raw["solutions"]]
        rec("degenerate_symmetrization_identity_n3_%s_target" % label, ok,
            {"coefficients_equal": same_coeffs, "D_identity": s_id and s_id["D"], "D_raw": s_raw and s_raw["D"],
             "same_solution_set": bool(s_id and s_raw and sorted(s_id["solutions"]) == sorted(s_raw["solutions"])),
             "outcomes": [s_id and s_id["outcome"], s_raw and s_raw["outcome"]]})
    rung = C.ladder_entry(4111)
    F5 = C.ladder_field(rung)
    E5, cv5 = C.ladder_curve(F5, rung, "ecgfp5_shaped")
    px5 = A.pool_x(E5, 400)
    for m in (3, 4):
        pol5, _ = build_poly(ctx, F5, E5, "identity", m, "%d:v2:build:4111:ecgfp5_shaped:identity:%d" % (C.SEED_CURVES, m), "ctl_identity_n5_m%d" % m,
                             ctx.plan["watchdogs"]["builder_timeout_s"]["m4"])
        xR = E5.random_point(random.Random("ctl:n5:%d" % m))[0]
        nodes = sorted(random.Random("ctl:n5:nodes:%d" % m).sample(px5, 2 ** (m - 1) + 1))
        _e, Cg5, _i = raw_grid(ctx, F5, E5, "raw_x", m, xR, nodes, "ctl_raw_n5_m%d" % m, ctx.plan["watchdogs"]["builder_timeout_s"]["m4"])
        rec("degenerate_symmetrization_identity_coefficients_n5_m%d" % m, pol5 is not None and Cg5 is not None and A.raw_coefficients_equal_identity(Cg5, pol5, xR))
    # --- orbit_lifting_verifier: planted relations through the full solver path at n = 5, m = 3 (INSTRUMENT
    #     CHECK: m < n, so the planted D is an orbit size and is never read as a degree; CORR-20260923-57177b)
    ctx._p = F5.p
    rs5 = A.rescaling(E5)
    nsub5 = int(cv5["subgroup_prime"])
    pools5 = {"S": px5, "S_rescaled": A.pool_u(E5, rs5["lam_obj"], 400), "rq": A.pool_u(E5, rs5["lam_obj"], 400), "norm": A.pool_t(E5, 400)}
    good_certs = {}
    for arm in ("S3", "S3_rescaled", "torsion_S3_rq", "torsion_S3_norm"):
        kind, _ = A.parse_arm(arm)
        polc, _ = build_poly(ctx, F5, E5, arm, 3, "%d:v2:build:4111:ecgfp5_shaped:%s:3:controls" % (C.SEED_CURVES, arm), "ctl_%s" % arm,
                             ctx.plan["watchdogs"]["builder_timeout_s"]["m3"])
        rngp = random.Random("ctl:planted:%s" % arm)
        Rp5 = None
        for _ in range(400):
            sel = rngp.sample(sorted(pools5[kind]) if isinstance(pools5[kind], dict) else pools5[kind], 3)
            if kind == "norm":
                pts = [E5.lift_x(pools5["norm"][t]) for t in sel]
            elif kind == "S":
                pts = [E5.lift_x(F5(x)) for x in sel]
            else:
                pts = [E5.lift_x(rs5["lam_obj"] * F5(u)) for u in sel]
            if any(P is None for P in pts):
                continue
            S = None
            for P in pts:
                S = E5.add(S, P)
            if S is not None and E5.mul(nsub5, S) is None:
                Rp5 = S
                break
        if polc is None or Rp5 is None:
            rec("orbit_lifting_path_%s" % arm, False, {"reason": "build failed or no planted sum in the prime-order subgroup"})
            continue
        val = Rp5[0] if kind != "norm" else Rp5[0] + E5.a4 / Rp5[0]
        names, eqs = A.system_for_target(polc, val, rs5)
        s = solve(ctx, names, eqs, "ctl_planted_%s" % arm, C.watchdog(ctx.plan, arm, 3)["per_target_timeout_s"], retain_input=True)
        lc = lift_and_certify(ctx, F5, E5, cv5, "ecgfp5_shaped", arm, kind, 3, rs5 if A.base_of(kind) == "x_over_lam_in_Fp" else None,
                              nsub5, Rp5, 1, Rp5, s["solutions"], "ctl_planted", "planted_instrument_check_m_lt_n", OpCount(5),
                              extra={"instrument_check": "m < n planted target: D is a planted-orbit size, never a degree (CORR-20260923-57177b)"})
        rec("orbit_lifting_path_%s" % arm, s["outcome"] == "ok" and lc["n_relations_verified"] >= 1 and lc["n_relations_verified"] == lc["n_relations"],
            {"outcome": s["outcome"], "n_rational_solutions": len(s["solutions"]), "n_relations": lc["n_relations"], "verified": lc["n_relations_verified"]})
        if lc["certificates"]:
            good_certs[arm] = json.load(open(os.path.join(ctx.rd, lc["certificates"][0]["path"])))
    # --- verifier negative tests (every one must FAIL)
    def neg(name, cert, expect):
        ok, _, reasons = VI.verify(cert)
        rec("verifier_rejects_%s" % name, (not ok) and any(expect in r for r in reasons), {"reasons": reasons})
    for arm, cert in good_certs.items():
        c1 = json.loads(json.dumps(cert)); c1["k"] = cert["k"] + 1
        neg("wrong_scalar_%s" % arm, c1, "R != [k]G")
        c2 = json.loads(json.dumps(cert)); c2["signs"] = [-s for s in cert["signs"]]
        neg("flipped_signs_%s" % arm, c2, "sum of signed points")
        c3 = json.loads(json.dumps(cert)); c3["points"][0] = cert["G"]
        neg("non_factor_base_point_%s" % arm, c3, "")
        c4 = json.loads(json.dumps(cert)); del c4["relation_mod_T"]
        neg("missing_relation_mod_T_%s" % arm, c4, "relation_mod_T field missing")
        if cert["factor_base"]["kind"] == "x_over_lam_in_Fp":
            for fld in ("beta", "lam", "u_values"):
                c5 = json.loads(json.dumps(cert)); del c5["factor_base"][fld]
                neg("missing_%s_%s" % (fld, arm), c5, "factor_base.%s missing" % fld)
            c6 = json.loads(json.dumps(cert)); c6["factor_base"]["beta"] = 1
            neg("square_beta_at_odd_n_%s" % arm, c6, "non-square")
            c7 = json.loads(json.dumps(cert)); c7["factor_base"]["lam"] = [(v + 1) % F5.p for v in cert["factor_base"]["lam"]]
            neg("wrong_lam_%s" % arm, c7, "lam^2 * beta != b")
        if arm.startswith("torsion"):
            c8 = json.loads(json.dumps(cert)); c8["curve"]["a6"] = [1, 0, 0, 0, 0]
            neg("torsion_certificate_on_curve_without_2torsion_%s" % arm, c8, "no rational 2-torsion")
        else:
            c9 = json.loads(json.dumps(cert)); c9["relation_mod_T"] = True
            neg("relation_mod_T_on_non_T_arm_%s" % arm, c9, "not a T-quotient arm")
    # relation_mod_T: shift one point of a verified T-quotient relation by T, so the signed sum is R + T. The verifier must
    # ACCEPT it with relation_mod_T true and REJECT the same points with relation_mod_T false.
    for arm in ("torsion_S3_rq", "torsion_S3_norm"):
        if arm not in good_certs:
            continue
        cert = json.loads(json.dumps(good_certs[arm]))
        P0 = (F5.from_coeffs(cert["points"][0][0]), F5.from_coeffs(cert["points"][0][1]))
        P0T = E5.add(P0, (F5.zero, F5.zero))
        cm = json.loads(json.dumps(cert))
        cm["points"][0] = [F5.coeffs(P0T[0]), F5.coeffs(P0T[1])]
        if cm["factor_base"]["kind"] == "x_over_lam_in_Fp":
            cm["factor_base"]["u_values"][0] = F5.coeffs(P0T[0] / rs5["lam_obj"])[0]
        cm["relation_mod_T"] = True
        okm, _, rm = VI.verify(cm)
        rec("verifier_accepts_relation_mod_T_%s" % arm, okm, {"reasons": rm})
        cn_ = json.loads(json.dumps(cm)); cn_["relation_mod_T"] = False
        neg("R_plus_T_without_flag_%s" % arm, cn_, "sum of signed points != R")
    # nearby object: rq must REFUSE on a curve without rational 2-torsion (recorded refusal, not a crash)
    E_no, _ = C.ladder_curve(F5, rung, "random_no2torsion")
    r_no = A.rescaling(E_no)
    rec("rq_refuses_curve_without_2torsion", r_no["refused"] and r_no["reason"] == "no rational 2-torsion", A.public_rescaling(r_no))
    # --- known_scalar_instances: base point order and R = [k]G re-checked by the INDEPENDENT arithmetic
    ks = []
    for p in (4111, 262151, 16777291):
        rg = C.ladder_entry(p)
        Fp = C.ladder_field(rg)
        for shape in ("ecgfp5_shaped", "random_2torsion", "random_no2torsion"):
            Ex, cvx = C.ladder_curve(Fp, rg, shape)
            nx = int(cvx["subgroup_prime"])
            Gx = C.base_point(Ex, nx, int(cvx["cofactor"]), p, shape)
            tg = C.ladder_targets(Ex, Gx, nx, p, shape, 3)
            Fi = VI.FqP(p, Fp.modulus)
            Ei = VI.CurveP(Fi, Fp.coeffs(Ex.a2), Fp.coeffs(Ex.a4), Fp.coeffs(Ex.a6))
            Gi = (tuple(Fp.coeffs(Gx[0])), tuple(Fp.coeffs(Gx[1])))
            ok = Ei.mul(nx, Gi) is None and all(Ei.mul(t["k"], Gi) == (tuple(Fp.coeffs(t["R"][0])), tuple(Fp.coeffs(t["R"][1]))) for t in tg)
            ks.append({"p": p, "shape": shape, "pass": ok})
    rec("known_scalar_instances_independent_recheck", all(x["pass"] for x in ks), ks)
    allok = all(c["pass"] for c in checks)
    infra_classes = {"refused_to_start", "crashed", "timeout", "memory_exhausted", "infrastructure_error"}
    infra = [c["check"] for c in checks if not c["pass"] and isinstance(c.get("detail"), dict)
             and (c["detail"].get("outcome") in infra_classes or any(o in infra_classes for o in (c["detail"].get("outcomes") or [])))]
    cdir = os.path.join(ctx.rd, "certificates")
    cfiles = sorted(f for f in os.listdir(cdir) if f.endswith(".json"))
    cver = [json.load(open(os.path.join(cdir, f)))["independent_verification"]["pass"] for f in cfiles]
    status = "completed_valid" if allok else "failed"
    fclass = None if allok else ("infrastructure_error" if infra else "implementation_error")
    if cfiles and not all(cver):
        status, fclass = "invalid", "invalid_measurement"
    raw = {"kind": "frozen_controls", "run_status": status, "failure_class": fclass, "gate_pass": allok, "checks": checks,
           "infrastructure_checks": infra,
           "metrics": {"n_checks": len(checks), "n_pass": sum(c["pass"] for c in checks), "wall_seconds": round(time.time() - t0, 1)},
           "certificate": ({"kind": "decomposition", "verified": all(cver), "count": len(cfiles),
                            "verifier": "experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py",
                            "note": "instrument-check certificates on planted m < n targets (k = 1, G := R); never degree evidence"}
                           if cfiles else {"kind": "none", "verified": None, "verifier": None, "note": "no certificate emitted"})}
    finish(ctx, raw, note="frozen controls (blocking)")


# ============================================================================ BUILD (n = 5 ladder)
def cmd_build(args):
    ctx = Ctx()
    t0 = time.time()
    p = args.p
    rung = C.ladder_entry(p)
    F = C.ladder_field(rung)
    rows = []
    for item in ctx.pkg["builds"]:
        shape, arm, m = item["shape"], item["arm"], item["m"]
        E, cv = C.ladder_curve(F, rung, shape)
        kind, _ = A.parse_arm(arm)
        row = {"shape": shape, "arm": arm, "m": m, "kind": kind}
        if kind in ("rq", "norm", "S_rescaled"):
            has, at0 = A.two_torsion_status(E)
            if not has or not at0:
                row.update(outcome="refused", reason="no rational 2-torsion")
                rows.append(row)
                continue
            if kind in ("rq", "S_rescaled"):
                rs = A.rescaling(E)
                if rs["refused"]:
                    row.update(outcome="refused", reason=rs["reason"], detail=rs.get("detail"))
                    rows.append(row)
                    continue
                row["rescaling"] = A.public_rescaling(rs)
        seed = "%d:v2:build:%d:%s:%s:%d" % (C.SEED_CURVES, p, shape, arm, m)
        pol, info = build_poly(ctx, F, E, arm, m, seed, "build_%d_%s_%s_m%d" % (p, shape, arm, m),
                               ctx.plan["watchdogs"]["builder_timeout_s"]["m%d" % m], to_cache=True)
        row.update(outcome=info["outcome"], seed=seed, info=info)
        if pol is not None:
            if info["npz_bytes"] <= 5 * 1024 * 1024:
                dst = os.path.join(ctx.rd, "polynomials", os.path.basename(info["npz"]))
                with open(info["npz"], "rb") as a, open(dst, "wb") as b:
                    b.write(a.read())
                with open(info["npz"][:-4] + ".meta.json", "rb") as a, open(dst[:-4] + ".meta.json", "wb") as b:
                    b.write(a.read())
                row["retained_in_package"] = os.path.relpath(dst, ctx.rd)
            row["pass"] = info["meta"]["held_out_mismatches"] == 0 and info["meta"]["single_flip_test"]["pass"]
        rows.append(row)
    ok = all(r["outcome"] in ("ok", "refused") and r.get("pass", True) for r in rows)
    infra = [r for r in rows if r["outcome"] not in ("ok", "refused")]
    raw = {"kind": "build", "p": p, "run_status": "completed_valid" if ok else "failed",
           "failure_class": None if ok else ("resource_exhaustion" if any(r["outcome"] in ("timeout", "memory_exhausted") for r in infra)
                                             else ("infrastructure_error" if infra else "implementation_error")),
           "polynomials": rows, "refusals": [r for r in rows if r["outcome"] == "refused"],
           "metrics": {"n_items": len(rows), "n_built": sum(r["outcome"] == "ok" for r in rows), "n_refused": sum(r["outcome"] == "refused" for r in rows),
                       "wall_seconds": round(time.time() - t0, 1)},
           "cache_dir": C.CACHE_DIR,
           "certificate": {"kind": "none", "verified": None, "verifier": None, "note": "construction run; exact interpolation verified on held-out rows"}}
    finish(ctx, raw, ladder_rows=[{"build": r["arm"], "shape": r["shape"], "m": r["m"], "outcome": r["outcome"], "reason": r.get("reason")} for r in rows],
           note="construction package")


# ============================================================================ CELLS
def _load_build(plan, p, shape, arm, m):
    """Find the build record for (p, shape, arm, m) in the committed build package's raw-result.json."""
    for pk in plan["packages"]:
        if pk["kind"] == "build" and pk["p"] == p:
            brid = C.resolve_replacement(plan, pk["run_id"])
            pk = dict(pk, run_id=brid)
            rp = os.path.join(C.EXP_DIR, "runs", brid, "raw-result.json")
            if not os.path.exists(rp):
                return None, "build package %s has no raw-result.json" % pk["run_id"]
            data = json.load(open(rp))
            for r in data["polynomials"]:
                if r["shape"] == shape and r["arm"] == arm and r["m"] == m:
                    return r, pk["run_id"]
            return None, "no build record for this arm in %s" % pk["run_id"]
    return None, "no build package planned for p = %d" % p


def _prior_cells(run):
    if not run:
        return {}
    run = C.resolve_replacement(C.load_plan(), run)
    rp = os.path.join(C.EXP_DIR, "runs", run, "raw-result.json")
    if not os.path.exists(rp):
        return {}
    return {c["arm"]: c for c in json.load(open(rp)).get("cells", [])}


def cmd_cells(args):
    ctx = Ctx()
    t0 = time.time()
    p, shape, m = args.p, args.shape, args.m
    rung = C.ladder_entry(p)
    F = C.ladder_field(rung)
    ctx._p = p
    E, cv = C.ladder_curve(F, rung, shape)
    nsub = int(cv["subgroup_prime"])
    G = C.base_point(E, nsub, int(cv["cofactor"]), p, shape)
    T = ctx.pkg["targets_per_cell"]
    targets = C.ladder_targets(E, G, nsub, p, shape, T)
    prior = _prior_cells(args.prior_run)
    cells = []
    measured_by_arm = {}
    for spec in ctx.pkg["cells"]:
        arm, kind = spec["arm"], A.parse_arm(spec["arm"])[0]
        cell = {"arm": arm, "kind": kind, "curve_shape": shape, "p": p, "p_bits": p.bit_length(), "m": m, "n": 5,
                "target_kind": "random", "group": A.group_label(kind, m), "group_order": A.group_order(kind, m),
                "planned_as": spec, "targets": [], "terminal": None}
        # ---- pre-declared, recorded non-runs
        if spec.get("disposition") == "not_attempted":
            cell["terminal"] = {"status": "not_attempted", "reason": spec["reason"]}
            cell["targets"] = [{"target": t["index"], "status": "not_attempted", "reason": spec["reason"]} for t in targets]
            cells.append(cell)
            continue
        # ---- refusals are COMPUTED here, at cell level, before any condition (DC-6 R-6)
        rs = None
        if A.base_of(kind) == "x_over_lam_in_Fp":
            rs = A.rescaling(E)
            if rs["refused"]:
                cell["terminal"] = {"status": "refused", "reason": rs["reason"], "detail": rs.get("detail"),
                                    "class": "recorded_refusal (DC-6 R-6); a nearby-object outcome, not a measurement"}
                cells.append(cell)
                continue
            cell["rescaling"] = A.public_rescaling(rs)
        elif kind == "norm":
            has, at0 = A.two_torsion_status(E)
            if not (has and at0):
                cell["terminal"] = {"status": "refused", "reason": "no rational 2-torsion",
                                    "class": "recorded_refusal (DC-6 R-6); a nearby-object outcome, not a measurement"}
                cells.append(cell)
                continue
        cond = spec.get("condition")
        if cond:
            met, why = _condition_met(cond, measured_by_arm, prior)
            cell["condition"] = {"text": cond, "met": met, "why": why}
            if not met:
                cell["terminal"] = {"status": "not_attempted", "reason": "condition not met: %s (%s)" % (cond, why)}
                cell["targets"] = [{"target": t["index"], "status": "not_attempted", "reason": cell["terminal"]["reason"]} for t in targets]
                cells.append(cell)
                continue
        pol = None
        if kind not in ("raw_x", "raw_u"):
            brec, bsrc = _load_build(ctx.plan, p, shape, arm, m)
            if brec is None or brec.get("outcome") != "ok":
                why = bsrc if brec is None else "build outcome %s (%s)" % (brec.get("outcome"), brec.get("reason"))
                cell["terminal"] = {"status": "not_attempted", "reason": "polynomial unavailable: %s" % why}
                cells.append(cell)
                continue
            npz = brec["info"]["npz"]
            if not os.path.exists(npz) or C.sha256_file(npz) != brec["info"]["npz_sha256"]:
                cell["terminal"] = {"status": "not_attempted", "reason": "cached polynomial missing or sha256 mismatch against build %s" % bsrc,
                                    "class": "infrastructure_error"}
                cells.append(cell)
                continue
            pol = load_poly(npz, F)
            if rs is not None and brec.get("rescaling") and (brec["rescaling"]["beta"], brec["rescaling"]["lam"]) != (rs["beta"], F.coeffs(rs["lam_obj"])):
                cell["terminal"] = {"status": "invalid", "reason": "(beta, lam) differs from the build record: invalidates the cell (amendment `unchanged`)"}
                cells.append(cell)
                continue
            cell["polynomial"] = {"build_run": bsrc, "sha256": brec["info"]["npz_sha256"], "support": brec["info"]["meta"]["support_nonzero_monomials"]}
        wd = C.watchdog(ctx.plan, arm, m)
        cg_timeout = ctx.plan["watchdogs"]["callgrind_timeout_s"].get("m%d" % m) if m <= 4 else None
        _run_cell(ctx, cell, F, E, cv, shape, kind, arm, m, rs, pol, targets, G, nsub, wd, cg_timeout)
        measured_by_arm[arm] = cell
        cells.append(cell)
    raw = {"kind": "cells", "p": p, "curve_shape": shape, "m": m, "n": 5, "cells": cells,
           "targets": [{"index": t["index"], "k": t["k"], "x_R": F.coeffs(t["R"][0])} for t in targets],
           "seeds": {"targets": "random.Random('%d:v2:targets:%d:%s')" % (C.SEED_TARGETS, p, shape),
                     "basepoint": "random.Random('%d:v2:basepoint:%d:%s')" % (C.SEED_CURVES, p, shape),
                     "grid_nodes": "random.Random('%d:v2:grid:%d:%s:<arm>:%d:<target>')" % (C.SEED_CURVES, p, shape, m)}}
    certs = [c for cl in cells for t in cl["targets"] if isinstance(t.get("lifting"), dict) for c in t["lifting"]["certificates"]]
    all_ok = all(c["verified"] for c in certs)
    any_meas = any(cl.get("metrics", {}).get("targets_measured") for cl in cells)
    raw["run_status"] = "invalid" if (certs and not all_ok) else ("completed_valid" if any_meas or all(cl["terminal"]["status"] in ("refused", "not_attempted") for cl in cells) else "failed")
    raw["failure_class"] = "invalid_measurement" if (certs and not all_ok) else (None if raw["run_status"] == "completed_valid" else "resource_exhaustion")
    raw["certificate"] = ({"kind": "decomposition", "verified": all_ok, "count": len(certs),
                           "verifier": "experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py"} if certs else
                          {"kind": "none", "verified": None, "verifier": None, "note": "no relation lifted in this package (degree measurement only)"})
    raw["metrics"] = {"cells": {cl["arm"]: cl.get("metrics") for cl in cells}, "wall_seconds": round(time.time() - t0, 1)}
    finish(ctx, raw, ladder_rows=[_ladder_row(cl) for cl in cells], note="one (p', shape, m) package; ladder-wide decisions in the aggregate")


def _condition_met(cond, measured_by_arm, prior):
    """Conditions are declared in trial-plan-v2.json. Two forms:
       'measured_in_this_package:<arm>'  the arm's cell in THIS package has >= 1 measured target;
       'm5_not_measured:<arm>'           the arm's m = 5 cell in the prior package ran and has 0 measured targets."""
    kind, arm = cond.split(":", 1)
    if kind == "measured_in_this_package":
        c = measured_by_arm.get(arm)
        n = (c or {}).get("metrics", {}).get("targets_measured", 0)
        return n > 0, "%s measured targets in this package: %s" % (arm, n)
    if kind == "m5_not_measured":
        c = prior.get(arm)
        if c is None:
            return False, "no m = 5 cell for %s in the prior package" % arm
        st = (c.get("terminal") or {}).get("status")
        n = (c.get("metrics") or {}).get("targets_measured", 0)
        ran = st in ("not_measured", "measured")
        return ran and n == 0, "prior m = 5 cell terminal %s with %s measured targets" % (st, n)
    raise ValueError(cond)


def _run_cell(ctx, cell, F, E, cv, shape, kind, arm, m, rs, pol, targets, G, nsub, wd, cg_timeout):
    counts = {k: 0 for k in ("ok", "timeout", "memory_exhausted", "crashed", "positive_dimensional", "degenerate_parametrisation",
                             "refused_to_start", "not_attempted")}
    attempted = 0
    early_stop = None
    last_mem_deg = None
    consec_mem = 0
    t_cell = time.time()
    per_D = {}
    successes = 0
    lifted_points = 0
    for t in targets:
        i, R = t["index"], t["R"]
        row = {"target": i, "k": t["k"]}
        if early_stop:
            row.update(status="not_attempted", reason=early_stop)
            counts["not_attempted"] += 1
            cell["targets"].append(row)
            continue
        if wd.get("per_cell_no_measurement_watchdog_s") and not per_D and time.time() - t_cell > wd["per_cell_no_measurement_watchdog_s"]:
            early_stop = "per-cell watchdog (%ss, applies only while the cell has no measured target) fired" % wd["per_cell_no_measurement_watchdog_s"]
            row.update(status="not_attempted", reason=early_stop)
            counts["not_attempted"] += 1
            cell["targets"].append(row)
            continue
        ctr = OpCount(F.n)
        tc = time.time()
        tag = "%s_t%d" % (arm, i)
        if kind in ("raw_x", "raw_u"):
            pool = A.pool_x(E, 400) if kind == "raw_x" else A.pool_u(E, rs["lam_obj"], 400)
            nodes = sorted(random.Random("%d:v2:grid:%d:%s:%s:%d:%d" % (C.SEED_CURVES, F.p, shape, arm, m, i)).sample(pool, 2 ** (m - 1) + 1))
            eqs, _Cg, ginfo = raw_grid(ctx, F, E, kind, m, R[0], nodes, "grid_" + tag, ctx.plan["watchdogs"]["builder_timeout_s"]["m%d" % m])
            if eqs is None:
                row.update(status="not_measured", outcome=ginfo["outcome"], reason="raw grid child: %s" % ginfo.get("reason"))
                counts[ginfo["outcome"] if ginfo["outcome"] in counts else "crashed"] += 1
                cell["targets"].append(row)
                continue
            names = A.varnames(kind, m)
            row["construction_ops"] = ginfo["meta"]["construction_ops"]
        else:
            val = R[0] if kind != "norm" else R[0] + E.a4 / R[0]
            names, eqs = A.system_for_target(pol, val, rs, ctr)
            row["construction_ops"] = ctr.as_dict()
        row["construction_seconds"] = round(time.time() - tc, 3)
        r = solve(ctx, names, eqs, tag, wd["per_target_timeout_s"], retain_input=(i == 0),
                  callgrind_timeout=(cg_timeout if (cg_timeout and i == 0) else None))
        attempted += 1
        out = r["outcome"]
        counts[out if out in counts else "crashed"] += 1
        row.update({k: r.get(k) for k in ("outcome", "reason", "D", "D_defined", "D_reason", "threads_executed", "input", "solver", "timings",
                                          "f4_summary", "n_f4_computations", "last_f4_round", "instructions_callgrind", "substitution_failures",
                                          "dimension_of_quotient_printed", "parse_kind", "solution_info")})
        row["instructions_note"] = ("perf counter per row in solver.instructions; callgrind only on target 0 of an m <= 4 cell; "
                                    "otherwise not_measured: callgrind not affordable at this shape/count (declared in trial-plan-v2.json)")
        if out != "ok" or not r.get("D_defined") and r.get("D_reason") is None:
            row["status"] = "not_measured"
            row["class"] = {"timeout": "resource_exhaustion", "memory_exhausted": "resource_exhaustion", "crashed": "infrastructure_error",
                            "refused_to_start": "infrastructure_error", "positive_dimensional": "non_generic_system (R-5)",
                            "degenerate_parametrisation": "non_generic_system (R-5)"}.get(out, "infrastructure_error")
            last = r.get("last_f4_round") or {}
            row["envelope"] = V.envelope_tuple(r["solver"], {"MemTotal_kB": ctx.host["mem_total_kB"], "SwapTotal_kB": ctx.host["swap_total_kB"]},
                                               arm, "%s (%s)" % (kind, A.group_label(kind, m)), F.p, m, F.n, r["threads_executed"],
                                               ctx.msolve_version, last.get("deg"))
            row["rule"] = "a timeout, OOM or crash is NOT MEASURED and never evidence about D (specification stopping rule 3; DC-6 R-5)"
            if out == "memory_exhausted" and m == 5:
                deg = last.get("deg")
                consec_mem = consec_mem + 1 if (deg == last_mem_deg or consec_mem == 0) else 1
                last_mem_deg = deg
                if consec_mem >= 2:
                    early_stop = ("A-7 pre-declared early stop: 2 consecutive memory_exhausted outcomes at the same F4 degree (%s) "
                                  "in an m = 5 cell; remaining targets not_attempted. Never evidence about D." % deg)
            else:
                consec_mem = 0
            cell["targets"].append(row)
            continue
        consec_mem = 0
        row["status"] = "measured"
        if r.get("D_defined"):
            per_D[i] = r["D"]
        lctr = OpCount(F.n)
        lc = lift_and_certify(ctx, F, E, cv, shape, arm, kind, m, rs, nsub, G, t["k"], R, r["solutions"], i, "random", lctr)
        row["lifting_ops"] = lctr.as_dict()
        row["counted_ops_mult_equivalent_total"] = row["construction_ops"]["fp_mult_equivalent"] + lctr.mult_equivalent_fp()
        row["n_rational_solutions"] = len(r["solutions"])
        row["lifting"] = lc
        if lc["n_relations_verified"]:
            successes += 1
            lifted_points += lc["n_relations_verified"] * m
        cell["targets"].append(row)
    measured = [x for x in cell["targets"] if x.get("status") == "measured"]
    Dcell, why = SC.cell_D(per_D)
    certs = [c for x in measured for c in x["lifting"]["certificates"]]
    cell["metrics"] = {
        "targets_planned": len(targets), "targets_attempted": attempted, "targets_measured": len(measured),
        "outcome_counts": counts, "m5_timeout_count": counts["timeout"] if m == 5 else 0,
        "ideal_degree_D": Dcell, "D_reason": why, "D_per_target": {str(k): v for k, v in per_D.items()},
        "decomposition_success_rate": (successes / len(measured)) if measured else None,
        "targets_with_verified_relation": successes, "lifted_verified_points_total": lifted_points,
        "lifted_verified_points_per_success": (lifted_points / successes) if successes else None,
        "certificate_verify_pass_rate": (sum(c["verified"] for c in certs) / len(certs)) if certs else None,
        "early_stop_reason": early_stop, "wall_seconds_per_cell": round(time.time() - t_cell, 1),
        "peak_memory_bytes": max([x.get("solver", {}).get("peak_rss_bytes") or 0 for x in cell["targets"] if x.get("solver")], default=None),
        "instructions": "perf counters unavailable on host where recorded as such; callgrind on target 0 of each m <= 4 cell only (declared in trial-plan-v2.json); m = 5 not_measured",
        "target_kind": "random",
    }
    cell["terminal"] = {"status": "measured" if measured else "not_measured",
                        "reason": None if measured else "no target measured (see per-target classes and envelope tuples)"}


def _ladder_row(cl):
    mt = cl.get("metrics") or {}
    return {"arm": cl["arm"], "group": cl["group"], "group_order": cl["group_order"], "curve_shape": cl["curve_shape"], "p": cl["p"],
            "m": cl["m"], "target_kind": cl["target_kind"], "terminal": cl["terminal"], "D": mt.get("ideal_degree_D"),
            "D_per_target": mt.get("D_per_target"), "targets_measured": mt.get("targets_measured"), "outcome_counts": mt.get("outcome_counts"),
            "decomposition_success_rate": mt.get("decomposition_success_rate"), "label": "measured" if mt.get("targets_measured") else cl["terminal"]["status"]}


# ============================================================================ AGGREGATE
def cmd_aggregate(args):
    ctx = Ctx()
    t0 = time.time()
    runs, replaced = {}, {}
    for rid0 in args.runs.split(","):
        rid = C.resolve_replacement(ctx.plan, rid0)
        if rid != rid0:
            replaced[rid0] = rid          # the replaced infrastructure_error package stays in the ledger, named here
        rp = os.path.join(C.EXP_DIR, "runs", rid, "raw-result.json")
        runs[rid] = json.load(open(rp)) if os.path.exists(rp) else None
    rows, groups = [], {}
    for rid, r in runs.items():
        if not r or r.get("kind") != "cells":
            continue
        for cl in r["cells"]:
            row = _ladder_row(cl)
            row["run"] = rid
            rows.append(row)
            groups.setdefault((cl["curve_shape"], cl["p"], cl["m"], cl["target_kind"]), {})[cl["kind"]] = {
                int(k): v for k, v in ((cl.get("metrics") or {}).get("D_per_target") or {}).items()}
    # every planned cell must have a terminal row (R-2)
    planned = [(C.resolve_replacement(ctx.plan, pk["run_id"]), c["arm"], pk["shape"], pk["p"], pk["m"])
               for pk in ctx.plan["packages"] if pk["kind"] == "cells" for c in pk["cells"]]
    present = {(r["run"], r["arm"]) for r in rows}
    missing = [{"run": a, "arm": b, "shape": c, "p": d, "m": e, "status": "not_attempted",
                "reason": "package not run or no row written (recorded here, never silently absent)"} for (a, b, c, d, e) in planned if (a, b) not in present]
    scoring = []
    for (shape, p, m, tk), g in sorted(groups.items()):
        s = SC.score_like_for_like(g, m)
        s.update({"curve_shape": shape, "p": p, "m": m, "target_kind": tk})
        if shape != "ecgfp5_shaped":
            for br in ("F1", "F1_prime"):
                s[br] = dict(s[br], fires=None, scoreable=False, not_applicable_reason="F1/F1' are read on EcGFp5-shaped cells only")
        scoring.append(s)
    dflat = {"heuristic": "HEUR-GFPN-DFLAT", "frozen_statement": "relative D variation < 10% across >= 3 primes spanning >= 12 bits (per arm, m = 5)", "arms": {}}
    cellD = {}
    for r in rows:
        if r["m"] == 5 and r["target_kind"] == "random" and r["D"]:
            cellD.setdefault((r["arm"], r["curve_shape"]), []).append((r["p"], r["D"]))
    for arm in ("S5", "S5_rescaled", "torsion_S5_rq", "torsion_S5_norm", "raw"):
        for shape in ("ecgfp5_shaped", "random_2torsion", "random_no2torsion"):
            dflat["arms"].setdefault(arm, {})[shape] = SC.heur_dflat(cellD.get((arm, shape), []))
    matched = []
    for (arm, shape), pts in cellD.items():
        if shape != "ecgfp5_shaped":
            continue
        for p, D in pts:
            o = [d for (pp, d) in cellD.get((arm, "random_2torsion"), []) if pp == p]
            if o:
                matched.append({"arm": arm, "p": p, **SC.matched_F4(D, o[0])})
    band = {"p_crypto": str(SC.P64), "label": "MODELED; not a security finding (EC-8)", "F3": SC.UNDECIDABLE_F3, "tail_check_2_36": SC.UNDECIDABLE_F3, "arms": {}}
    for arm in ("S5", "S5_rescaled", "torsion_S5_rq", "torsion_S5_norm", "raw"):
        d = dflat["arms"][arm]["ecgfp5_shaped"]
        kind = A.parse_arm(arm)[0]
        succ = att = 0
        for rid, r in runs.items():
            if r and r.get("kind") == "cells" and r["curve_shape"] == "ecgfp5_shaped" and r["m"] == 5:
                for cl in r["cells"]:
                    if cl["arm"] == arm and cl.get("metrics"):
                        succ += cl["metrics"]["targets_with_verified_relation"]
                        att += cl["metrics"]["targets_measured"]
        Dmax = max(d.get("D_per_prime", {}).values(), default=None) if d.get("heur_dflat_pass") is True else None
        band["arms"][arm] = SC.band_for_arm(kind, d, Dmax, succ, att)
        if att and not succ:
            band["arms"][arm]["measured_success_note"] = ("0/%d measured successes: the model's inverse success probability is used; a 0 rate "
                                                          "does not enter the band (B-3)" % att)
    raw = {"kind": "aggregate", "run_status": "completed_valid", "failure_class": None, "runs": list(runs), "replaced_packages": replaced,
           "missing_runs": [rid for rid, r in runs.items() if r is None], "ladder_rows": rows, "planned_cells_without_row": missing,
           "like_for_like_scoring": scoring, "heur_dflat": dflat, "matched_control_check_F4": matched, "cost_band": band,
           "metrics": {"n_rows": len(rows), "n_planned_without_row": len(missing),
                       "heur_dflat_pass": {a: {s: v["heur_dflat_pass"] for s, v in d.items()} for a, d in dflat["arms"].items()},
                       "wall_seconds": round(time.time() - t0, 1)},
           "certificate": {"kind": "none", "verified": None, "verifier": None, "note": "aggregation; no new decomposition claimed"},
           "statement": "observations and comparison statistics only; no supported/refuted conclusion and no security level (EC-8)"}
    C.write_json(os.path.join(ctx.rd, "raw-result.json"), dict(raw, package=ctx.pkg, host=ctx.host, events=ctx.events, scoring_reference=SC.reference_block()))
    C.write_yaml(os.path.join(ctx.rd, "ladder-table.yaml"), {"ladder_table": {"rows": rows, "planned_cells_without_row": missing,
                                                                                 "like_for_like_scoring": scoring, "matched_control_check_F4": matched}})
    C.write_yaml(os.path.join(ctx.rd, "heur-dflat.yaml"), {"heur_dflat": dflat})
    C.write_yaml(os.path.join(ctx.rd, "cost-band-p64.yaml"), {"cost_band_p64": band})


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("fixture")
    a.add_argument("--p", type=int, required=True)
    sub.add_parser("fixture4")
    sub.add_parser("anchor-identity")
    sub.add_parser("controls")
    b = sub.add_parser("build")
    b.add_argument("--p", type=int, required=True)
    c = sub.add_parser("cells")
    c.add_argument("--p", type=int, required=True)
    c.add_argument("--shape", required=True)
    c.add_argument("--m", type=int, required=True)
    c.add_argument("--prior-run", default=None)
    g = sub.add_parser("aggregate")
    g.add_argument("--runs", required=True)
    args = ap.parse_args()
    {"fixture": cmd_fixture, "fixture4": cmd_fixture4, "anchor-identity": cmd_anchor_identity, "controls": cmd_controls,
     "build": cmd_build, "cells": cmd_cells, "aggregate": cmd_aggregate}[args.cmd](args)


if __name__ == "__main__":
    main()
