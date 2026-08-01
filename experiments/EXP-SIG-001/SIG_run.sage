# EXP-SIG-001 driver — runs the h013_f5_signatures instrument per mode.
# Usage (from repo root):
#   sage experiments/EXP-SIG-001/SIG_run.sage --mode gate|boolean|panel \
#        --out experiments/EXP-SIG-001/runs/RUN-EXP-SIG-001-X/raw.json [opts]
import sys, os, time, json, argparse, platform, datetime
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--mode', required=True, choices=['gate', 'boolean', 'panel'])
p.add_argument('--out', required=True)
p.add_argument('--n-list', default='9,12')
p.add_argument('--seeds', default='1,2,3')
p.add_argument('--t-list', default='3')
p.add_argument('--d5', default='', help='comma list of n:seed for D=5 count-only (sem only)')
p.add_argument('--rerun-check', default='', help='n:seed cell to compute twice (determinism control)')
p.add_argument('--p', type=int, default=1000003)
p.add_argument('--soft-cap', type=int, default=480, help='stop launching new cells after this many seconds')
args = p.parse_args()

EXPDIR = Path(args.out).resolve().parents[2]
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
from sage.all import GF, PolynomialRing, EllipticCurve, set_random_seed
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

t_start = time.time()
started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

out = {
    "experiment": "EXP-SIG-001",
    "mode": args.mode,
    "args": vars(args),
    "environment": {
        "sage_version": str(sage.version.version),
        "python_version": sys.version.split()[0],
        "os": platform.platform(),
        "machine": platform.machine(),
    },
    "started_at": started_at,
    "cells": [],
}

def flush():
    out["elapsed_s_so_far"] = round(time.time() - t_start, 2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(jsonsafe(out), fh, indent=1)

def softcap_hit():
    return (time.time() - t_start) > args.soft_cap

# ==========================================================================
if args.mode == 'gate':
    print("=== EXP-SIG-001 GATE: Koszul-validation (V1 null, V2 injected, V3 sanity) ===", flush=True)
    gate_checks = []

    # ---- V1: support-matched random null must classify as fully rewritable
    for n in (9, 12):
        monosets, nb, meta = build_boolean_semaev(n, 3, 1)
        rng = random.Random(stable_seed("null", n, 3, 1))
        null_ms = boolean_null(monosets, nb, rng)
        cell = {"kind": "V1_null", "n": n, "nb": nb, "per_D": {}}
        ok = True
        for D in (3, 4):
            rec, rows, kernel, kpiv = analyze_syzygy_space(null_ms, nb, D, extract=False, block_size=n)
            rec.pop("extra_reps", None)
            cell["per_D"][str(D)] = rec
            cond = (rec["extra"] == 0) and (rec["rank"] == rec["sr_pred"])
            ok = ok and cond
            print("  V1 n=%d D=%d: rank=%d pred=%d kernel=%d rankK=%d extra=%d -> %s" % (
                n, D, rec["rank"], rec["sr_pred"], rec["kernel_dim"], rec["rankK"],
                rec["extra"], "ok" if cond else "FAIL"), flush=True)
        cell["pass"] = bool(ok)
        gate_checks.append(ok)
        out["cells"].append(cell)
        flush()

    # ---- V2: injected KNOWN non-Koszul linear syzygy must be detected
    n = 9
    monosets, nb, meta = build_boolean_semaev(n, 3, 1)
    rng = random.Random(stable_seed("null", n, 3, 1))
    null_ms = boolean_null(monosets, nb, rng)
    degs = [max(mono_deg(m) for m in f) for f in null_ms]
    q = [i for i, d in enumerate(degs) if d == 2]
    c = [i for i, d in enumerate(degs) if d == 3]
    q0, q1, c0 = q[0], q[1], c[0]
    inj = list(null_ms)
    inj[c0] = null_ms[q0] ^^ null_ms[q1]   # f_c0' := f_q0 + f_q1  =>  f_q0+f_q1+f_c0' = 0
    rec, rows, kernel, kpiv = analyze_syzygy_space(inj, nb, 3, extract=True, block_size=n)
    det = False
    det_rep = None
    for rep in rec.get("extra_reps", []):
        if rep["n_generators"] == 3 and rep["mult_degrees"] == [0]:
            det = True
            det_rep = rep
            break
    cond = rec["extra"] >= 1 and det
    print("  V2 injected (gens %d,%d,%d): extra=%d, detected 3-generator constant-multiplier rep: %s -> %s" % (
        q0, q1, c0, rec["extra"], det, "ok" if cond else "FAIL"), flush=True)
    out["cells"].append({"kind": "V2_injected", "n": n, "gens": [q0, q1, c0],
                         "rec": rec, "detected": det, "detected_rep": det_rep, "pass": bool(cond)})
    gate_checks.append(cond)
    flush()

    # ---- V3: Semaev n=9 seed 1 pipeline sanity (assert D3 anchor only; D4 count
    # is RECORDED, not asserted: T2 measured 8n/3 only for n>=12; at n=9 the
    # observed value is 41 != 24, a genuine observation, not an instrument bug)
    cell9 = classify_cell(9, 3, 1, [3, 4])
    d3 = cell9["sem"]["3"]; d4 = cell9["sem"]["4"]
    cond = (d3["deficit"] == 1 and d3["extra"] == 1
            and cell9["null"]["3"]["extra"] == 0 and cell9["null"]["4"]["extra"] == 0)
    print("  V3 semaev n=9: deficit(3)=%d extra(3)=%d deficit(4)=%d extra(4)=%d null-extra=%d/%d -> %s (D4 recorded, not asserted)" % (
        d3["deficit"], d3["extra"], d4["deficit"], d4["extra"],
        cell9["null"]["3"]["extra"], cell9["null"]["4"]["extra"], "ok" if cond else "FAIL"), flush=True)
    out["cells"].append({"kind": "V3_semaev_sanity", "cell": cell9, "pass": bool(cond)})
    gate_checks.append(cond)
    flush()

    out["gate"] = "PASS" if all(gate_checks) else "FAIL"
    print("=== GATE: %s ===" % out["gate"], flush=True)

# ==========================================================================
elif args.mode == 'boolean':
    if out.get("gate") not in (None, "PASS"):
        raise SystemExit("gate not passed in this run; run --mode gate first")
    n_list = [int(x) for x in args.n_list.split(',')]
    seeds = [int(x) for x in args.seeds.split(',')]
    t_list = [int(x) for x in args.t_list.split(',')]
    d5_cells = []
    if args.d5:
        for tok in args.d5.split(','):
            nn, ss = tok.split(':')
            d5_cells.append((int(nn), int(ss)))
    print("=== EXP-SIG-001 boolean arm: n=%s seeds=%s t=%s ===" % (n_list, seeds, t_list), flush=True)
    for t in t_list:
        for n in n_list:
            for seed in seeds:
                if softcap_hit():
                    out["cells"].append({"kind": "boolean", "t": t, "n": n, "seed": seed,
                                         "status": "not_run: soft budget cap"})
                    flush()
                    continue
                t0 = time.time()
                cell = classify_cell(n, t, seed, [3, 4])
                cell["kind"] = "boolean"
                cell["wall_s"] = round(time.time() - t0, 2)
                out["cells"].append(cell)
                s3 = cell["sem"].get("3", {})
                s4 = cell["sem"].get("4", {})
                print("  [t=%d n=%d seed=%d] nb=%s | D3: rank=%s pred=%s def=%s extra=%s | D4: def=%s extra=%s rankK=%s | null extra=%s/%s (%.1fs)" % (
                    t, n, seed, cell["meta"].get("nb"),
                    s3.get("rank"), s3.get("sr_pred"), s3.get("deficit"), s3.get("extra"),
                    s4.get("deficit"), s4.get("extra"), s4.get("rankK"),
                    cell["null"].get("3", {}).get("extra"), cell["null"].get("4", {}).get("extra"),
                    cell["wall_s"]), flush=True)
                flush()
    # D=5 count-only cells
    for (nn, ss) in d5_cells:
        if softcap_hit():
            out["cells"].append({"kind": "boolean_d5", "n": nn, "seed": ss, "status": "not_run: soft budget cap"})
            flush()
            continue
        t0 = time.time()
        monosets, nb, meta = build_boolean_semaev(nn, 3, ss)
        rec5, _, _, _ = analyze_syzygy_space(monosets, nb, 5, extract=False, block_size=nn)
        rec5.pop("extra_reps", None)
        out["cells"].append({"kind": "boolean_d5", "n": nn, "seed": ss, "meta": meta,
                             "sem5": rec5, "wall_s": round(time.time() - t0, 2)})
        print("  [D5 count n=%d seed=%d] nrows=%d rank=%d pred=%d deficit=%d kernel=%d rankK=%d extra=%d (%.1fs)" % (
            nn, ss, rec5["nrows"], rec5["rank"], rec5["sr_pred"], rec5["deficit"],
            rec5["kernel_dim"], rec5["rankK"], rec5["extra"], time.time() - t0), flush=True)
        flush()
    # determinism control: compute one cell twice, require identical metrics
    if args.rerun_check:
        nn, ss = [int(x) for x in args.rerun_check.split(':')]
        c1 = classify_cell(nn, 3, ss, [3, 4])
        c2 = classify_cell(nn, 3, ss, [3, 4])
        strip = lambda c: {k: v for k, v in c["sem"].items()}
        same = json.dumps(jsonsafe(c1["sem"]), sort_keys=True) == json.dumps(jsonsafe(c2["sem"]), sort_keys=True)
        out["cells"].append({"kind": "rerun_check", "n": nn, "seed": ss, "identical": bool(same)})
        print("  [rerun-check n=%d seed=%d] identical outputs: %s" % (nn, ss, same), flush=True)
        flush()

# ==========================================================================
elif args.mode == 'panel':
    print("=== EXP-SIG-001 Yokoyama panel arm (p=%d) ===" % args.p, flush=True)
    F = GF(args.p)
    panel, isos = build_panel(args.p)
    out["panel_curves"] = [{"label": lab, "a4": str(a), "a6": str(b),
                            "order": str(E.cardinality())} for (a, b, lab, E) in panel]
    out["iso_curves"] = [{"label": lab, "a4": str(a), "a6": str(b),
                          "order": str(E.cardinality())} for (a, b, lab, E) in isos]
    for r in out["panel_curves"]:
        print("  panel: %-16s #E=%s" % (r["label"], r["order"]), flush=True)
    for r in out["iso_curves"]:
        print("  iso:   %-16s #E=%s" % (r["label"], r["order"]), flush=True)
    flush()

    # ---- #G* cells (REDUCED SCOPE per coordinator): minimum seeds (1).
    # Panel = the spec's 7 families: generic + CM {j=0, 1728, -3375, 8000,
    # -32768} + isogenous-of-generic (same-order control). m=2: d in {4,6};
    # m=3: d=4 (cost-capped).
    plan = []
    families = list(panel) + [isos[0]]   # isos[0] = iso(generic), the 7th family
    for (a, b, lab, E) in families:
        for d in (4, 6):
            plan.append((E, lab, 2, d, 1, "decomp"))
    for (a, b, lab, E) in families:
        plan.append((E, lab, 3, 4, 1, "decomp"))
    out["plan_size"] = len(plan)
    for (E, lab, m, d, seed, tk) in plan:
        if softcap_hit():
            out["cells"].append({"kind": "gstar", "curve": lab, "m": m, "d": d,
                                 "seed": seed, "status": "not_run: soft budget cap"})
            flush()
            continue
        res = gstar_cell(E, m, d, seed, xR_kind=tk, time_limit=55)
        res["kind"] = "gstar"
        res["curve"] = lab
        out["cells"].append(res)
        if "gstar" in res:
            print("  [gstar] %-16s m=%d d=%d s=%d | #G*=%d scale=%d ratio=%.2f #NS=%d zero=%d maxdeg=%d (%.1fs)" % (
                lab, m, d, seed, res["gstar"], res["scale_mdm1"], res["ratio_scale"],
                res["nNS"], res["zero_red"], res["max_deg"], res["sec"]), flush=True)
        else:
            print("  [gstar] %-16s m=%d d=%d s=%d | CENSORED %s" % (lab, m, d, seed, res.get("censored")), flush=True)
        flush()

    # ---- gstar determinism control: same cell twice
    E0 = panel[0][3]
    r1 = gstar_cell(E0, 2, 6, 1)
    r2 = gstar_cell(E0, 2, 6, 1)
    same = json.dumps(jsonsafe(r1), sort_keys=True) == json.dumps(jsonsafe(r2), sort_keys=True)
    out["cells"].append({"kind": "gstar_rerun_check", "identical": bool(same),
                         "gstar_1": r1.get("gstar"), "gstar_2": r2.get("gstar")})
    print("  [gstar rerun-check] identical: %s" % same, flush=True)
    flush()

    # ---- Betti (REDUCED SCOPE): CHAIN t=3 per family vs T11 null;
    # YOKO m=2 d=4 per family. t=4 growth arm and the boolean Betti probe are
    # dropped under the reduced-scope directive (recorded as deviations).
    import random as _rnd
    for (a, b, lab, E) in panel:
        for t in (3,):
            if softcap_hit():
                out["cells"].append({"kind": "betti_chain", "curve": lab, "t": t,
                                     "status": "not_run: soft budget cap"})
                flush()
                continue
            nv = 2 * t - 2
            names = ['x%d' % i for i in range(1, t + 1)] + ['u%d' % i for i in range(1, t - 1)]
            Rng = PolynomialRing(F, names, order='degrevlex')
            rng = _rnd.Random(stable_seed("betti", lab, t))
            set_random_seed(stable_seed("betti", lab, t))
            xR = F.random_element()
            sem = chained_gens_prime(Rng, t, a, b, xR)
            t0 = time.time()
            Bs, rs, ps = betti_table_homog(sem, Rng)
            nulls = []
            for nd in range(2):
                nullp = [randomize_on_support(Rng, f, rng) for f in sem]
                Bn, rn, pn = betti_table_homog(nullp, Rng)
                nulls.append({"betti": Bn, "reg": rn, "l1_vs_sem": betti_l1(Bs, Bn)})
            rec = {"kind": "betti_chain", "curve": lab, "t": t, "betti_sem": Bs,
                   "reg_sem": rs, "pdim_sem": ps, "nulls": nulls,
                   "wall_s": round(time.time() - t0, 2)}
            out["cells"].append(rec)
            print("  [betti CHAIN] %-16s t=%d reg=%s pdim=%s L1null=%s (%.1fs)" % (
                lab, t, rs, ps, [n["l1_vs_sem"] for n in nulls], rec["wall_s"]), flush=True)
            flush()
    for (a, b, lab, E) in panel:
        if softcap_hit():
            out["cells"].append({"kind": "betti_yoko", "curve": lab, "status": "not_run: soft budget cap"})
            flush()
            continue
        R2 = PolynomialRing(F, ['x1', 'x2'], order='degrevlex')
        x1, x2 = R2.gens()
        rng = _rnd.Random(stable_seed("bettiy", lab))
        set_random_seed(stable_seed("bettiy", lab))
        d = 4
        base = []
        while len(base) < d:
            Pt = E.random_point()
            if Pt[0] not in base:
                base.append(Pt[0])
        xR = F.random_element()
        sem = [prod(x1 - r for r in base), prod(x2 - r for r in base),
               S3_odd(x1, x2, xR, a, b)]
        t0 = time.time()
        Bs, rs, ps = betti_table_homog(sem, R2)
        nullp = [randomize_on_support(R2, f, rng) for f in sem]
        Bn, rn, pn = betti_table_homog(nullp, R2)
        rec = {"kind": "betti_yoko", "curve": lab, "d": d, "betti_sem": Bs, "reg_sem": rs,
               "betti_null": Bn, "reg_null": rn, "l1": betti_l1(Bs, Bn),
               "wall_s": round(time.time() - t0, 2)}
        out["cells"].append(rec)
        print("  [betti YOKO] %-16s d=%d reg=%s/%s L1=%d (%.1fs)" % (lab, d, rs, rn, rec["l1"], rec["wall_s"]), flush=True)
        flush()

    # boolean Betti probe: dropped under the reduced-scope directive
    # (graded resolution of 36+18 generators over GF(2) is the one cell with
    # blow-up risk; the D3/D4 kernel classification supersedes it here).
    out["cells"].append({"kind": "betti_boolean_probe",
                         "status": "not_run: reduced scope (coordinator directive)"})
    flush()

out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
