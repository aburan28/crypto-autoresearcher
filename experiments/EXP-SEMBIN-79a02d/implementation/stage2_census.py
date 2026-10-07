"""EXP-SEMBIN-79a02d Stage 2 -- SOLV-D / d_ff / Macaulay rank-vs-nrows census
with dual GF(2) rank (arm A row-insertion, arm B Four-Russians) and two
independent enumerations, per stage0/definitions.md (frozen).

usage: stage2_census.py <n> <phase> <run_dir>
  phase "main": every family x seeds 0..7 (+ DREG anchor): enumeration, d_ff
                (D=2..4), Macaulay D=4 (and D=5 when n == 12), SOLV-2/3/4.
  phase "d5":   Macaulay D=5 only, in the frozen priority order, until the
                wall-clock allowance in env D5_WALL (seconds) is used.
Instances are rebuilt deterministically from the frozen seeds; the field
modulus and DREG anchor come from the Stage-1 run directory (env STAGE1_RUN).
"""
import json, os, random, sys, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from semaev_core import *
from harness import write_gens, run_tool

SCRATCH = os.environ.get("SCRATCH", "/tmp")
FAMILIES = ["planted", "uniform_z", "null", "known_false_a", "known_false_b"]
SEEDS = list(range(8))
B_CURVE = 2  # alpha (DREG convention)


def rng_for(arm, n, s):
    return random.Random(f"EXP-SEMBIN-79a02d|{arm}|n={n}|s={s}")


def build_instance(n, fam, s, mod, anchor=None):
    """Returns dict with polys, N, k, enumeration-support info, provenance."""
    F = GF2n(n, mod)
    k = (n + 2) // 3
    E = Curve(F, 1, B_CURVE)
    info = {"n": n, "family": fam, "seed": s, "k_diag": k}
    if fam == "anchor":
        L = Layout(n, k); z = anchor["z_int"]
        polys = build_system(F, L, B_CURVE, z)
        info.update(k=k, z=z, construction="DREG-matched instance from Stage 1")
        return info, polys, L, F, {"z": z, "corrupt": None, "field_enum": True}
    if fam in ("planted", "null", "known_false_a"):
        L = Layout(n, k)
        rng = rng_for("planted", n, s)
        z, pts = planted_z(F, E, k, rng)
        polys = build_system(F, L, B_CURVE, z)
        info.update(k=k, z=z, planted_points=[list(p) for p in pts])
        if fam == "planted":
            return info, polys, L, F, {"z": z, "corrupt": None, "field_enum": True}
        if fam == "null":
            nrng = rng_for("null", n, s)
            npolys = boolean_null(polys, L.N, nrng)
            info["construction"] = "support-matched null of planted seed s"
            return info, npolys, L, F, {"z": None, "corrupt": None, "field_enum": False}
        # known_false_a: flip one constant term, redraw until both enumerations say UNSAT
        krng = rng_for("known_false_a", n, s)
        draws = []
        for attempt in range(16):
            j = krng.randrange(2); l = krng.randrange(n)
            cp = build_system(F, L, B_CURVE, z, corrupt=(j, l))
            e1 = enumerate_field(F, L, B_CURVE, z, corrupt=(j, l))
            draws.append({"eq": j, "l": l, "E1_count": len(e1)})
            if not e1:
                info.update(corruption={"eq": j, "l": l}, corruption_draws=draws)
                return info, cp, L, F, {"z": z, "corrupt": (j, l), "field_enum": True}
        info.update(corruption=None, corruption_draws=draws, construction_failed=True)
        return info, None, L, F, None
    if fam == "uniform_z":
        L = Layout(n, k)
        rng = rng_for("uniform_z", n, s)
        z = rng.randrange(1, 1 << n)
        info.update(k=k, z=z)
        return info, build_system(F, L, B_CURVE, z), L, F, {"z": z, "corrupt": None, "field_enum": True}
    if fam == "known_false_b":
        kb = k + 1
        L = Layout(n, kb)
        rng = rng_for("known_false_b", n, s)
        z, pts = planted_z(F, E, kb, rng)
        info.update(k=kb, z=z, planted_points=[list(p) for p in pts], construction="off-diagonal k'=ceil(n/3)+1, planted")
        return info, build_system(F, L, B_CURVE, z), L, F, {"z": z, "corrupt": None, "field_enum": True}
    raise ValueError(fam)


def eval_rank_points(points, N, D):
    """rank of evaluation map B_{<=D} -> F_2^points (python ints)."""
    from itertools import combinations
    vecs = []
    for pt in points:
        v = 0; idx = 0
        for d in range(D + 1):
            for c in combinations(range(N), d):
                m = 0
                for x in c:
                    m |= 1 << x
                if (pt & m) == m:
                    v |= 1 << idx
                idx += 1
        vecs.append(v)
    piv = {}
    for v in vecs:
        while v:
            lb = v.bit_length() - 1
            if lb in piv:
                v ^= piv[lb]
            else:
                piv[lb] = v
                break
    return len(piv)


def soundness_check(basis_path, points):
    """Independent evaluation of every final W_D basis vector at every point."""
    import numpy as np
    with open(basis_path, "rb") as f:
        nc = int(np.frombuffer(f.read(8), dtype=np.int64)[0])
        r = int(np.frombuffer(f.read(8), dtype=np.int64)[0])
        mono = np.frombuffer(f.read(8 * nc), dtype=np.uint64)
        W = (nc + 63) // 64
        rows = np.frombuffer(f.read(8 * W * r), dtype=np.uint64).reshape(r, W) if r else np.zeros((0, W), np.uint64)
    bad = 0
    for pt in points:
        ptv = np.uint64(pt)
        true_cols = ((mono & ptv) == mono)
        mask = np.zeros(W * 64, dtype=bool); mask[:nc] = true_cols
        words = np.zeros(W, dtype=np.uint64)
        idx = np.nonzero(mask)[0]
        np.bitwise_or.at(words, idx // 64, (np.uint64(1) << (idx % 64).astype(np.uint64)))
        x = rows & words
        cnt = np.zeros(r, dtype=np.int64)
        for w in range(W):
            col = x[:, w]
            # popcount parity
            c = col.copy()
            c ^= c >> np.uint64(32); c ^= c >> np.uint64(16); c ^= c >> np.uint64(8)
            c ^= c >> np.uint64(4); c ^= c >> np.uint64(2); c ^= c >> np.uint64(1)
            cnt ^= (c & np.uint64(1)).astype(np.int64)
        bad += int(cnt.sum())
    return {"rows_checked": r, "points": len(points), "nonvanishing_evaluations": bad, "pass": bad == 0}


def ff_from_hist(macs):
    """macs: {D: armA-result} for D = 2..4. Returns d_ff_ic, d_ff_sem."""
    d_ic = None; d_sem = None
    prev_rank = 0
    for D in sorted(macs):
        h = macs[D]["pivots_by_degree"]
        if d_ic is None and (h[0] + h[1]) > 0:
            d_ic = D
        low = sum(h[:D])  # dim U_D ∩ B_{<=D-1}
        if d_sem is None and low > prev_rank:
            d_sem = D
        prev_rank = macs[D]["rank"]
    return d_ic, d_sem


def process(task):
    n, fam, s, mod, anchor, phase, d5 = task
    t0 = time.time()
    rec = {"n": n, "family": fam, "seed": s}
    try:
        info, polys, L, F, encinfo = build_instance(n, fam, s, mod, anchor)
        rec["instance"] = info
        if polys is None:
            rec["status"] = "construction_failed"; return rec
        N = L.N
        rec["N"] = N
        degs = [poly_deg(f) for f in polys]
        rec["generator_degree_hist"] = {str(d): degs.count(d) for d in sorted(set(degs))}
        rec["n_quadratic"] = degs.count(2)
        g = os.path.join(SCRATCH, f"s2_n{n}_{fam}_{s}_{os.getpid()}.gens")
        write_gens(g, polys, N)
        if phase == "d5":
            a = run_tool(["gf2_armA", "mac", g, 5], 20000); b = run_tool(["gf2_armB", "mac", g, 5], 20000)
            pred, _ = semireg_rank_pred(degs, N, 5)
            rec["mac"] = {"5": {"A": a, "B": b, "pred": pred[5], "dual_agree": a["rank"] == b["rank"] and a["fingerprint"] == b["fingerprint"] and a["nrows"] == b["nrows"]}}
            rec["status"] = "ok"; rec["seconds"] = round(time.time() - t0, 1)
            os.remove(g); return rec
        # --- enumeration
        enum = {}
        if encinfo["field_enum"]:
            sols1 = enumerate_field(F, L, B_CURVE, encinfo["z"], corrupt=encinfo["corrupt"])
            enum["E1"] = {"count": len(sols1), "solutions": [format(x, "x") for x in sols1[:64]]}
            enum["E1_solutions_satisfy_generators"] = all(all(eval_poly(f, p) == 0 for f in polys) for p in sols1)
        if N <= 30:
            e2 = run_tool(["enum_bool", g], 3000)
            enum["E2"] = {"count": e2["count"], "solutions": e2["solutions"][:64], "seconds": e2["seconds"]}
        counts = [enum[k]["count"] for k in ("E1", "E2") if k in enum]
        enum["agree"] = len(set(counts)) == 1
        if "E1" in enum and "E2" in enum:
            enum["agree"] = enum["agree"] and sorted(enum["E1"]["solutions"]) == sorted(enum["E2"]["solutions"])
        enum["routes"] = [k for k in ("E1", "E2") if k in enum]
        V = counts[0] if counts else None
        rec["enumeration"] = enum
        rec["V_count"] = V
        rec["sat"] = (V or 0) > 0
        pts = None
        if "E2" in enum:
            pts = [int(x, 16) for x in e2["solutions"]]
        elif "E1" in enum:
            pts = sols1
        # --- Macaulay / d_ff
        Dlist = [2, 3, 4] + ([5] if n == 12 else [])
        macs = {}; rec["mac"] = {}
        for D in Dlist:
            a = run_tool(["gf2_armA", "mac", g, D], 6000); b = run_tool(["gf2_armB", "mac", g, D], 6000)
            pred, _ = semireg_rank_pred(degs, N, D)
            agree = a["rank"] == b["rank"] and a["fingerprint"] == b["fingerprint"] and a["nrows"] == b["nrows"] and a["pivots_by_degree"] == b["pivots_by_degree"]
            rec["mac"][str(D)] = {"A": a, "B": b, "pred": pred[D], "dual_agree": agree}
            macs[D] = a
        d_ic, d_sem = ff_from_hist({D: macs[D] for D in (2, 3, 4)})
        rec["d_ff_ic"] = d_ic if d_ic is not None else ">4"
        rec["d_ff_sem"] = d_sem if d_sem is not None else ">4"
        # --- SOLV-D closures
        rec["solv"] = {}
        for D in (2, 3, 4):
            bp = os.path.join(SCRATCH, f"basis_n{n}_{fam}_{s}_{D}_{os.getpid()}.bin") if (pts and V and V <= 4096) else None
            a = run_tool(["gf2_armA", "closure", g, D] + ([bp] if bp else []), 20000)
            b = run_tool(["gf2_armB", "closure", g, D], 20000)
            keys = ("dim_W", "codim", "one_in_W", "iterations", "level0_rank", "level0_fingerprint", "level0_rows")
            agree = all(a[k] == b[k] for k in keys)
            cell = {"A": a, "B": b, "dual_agree": agree}
            if V is not None:
                cell["solv_holds"] = a["codim"] == V
                cell["r_V"] = eval_rank_points(pts, N, D) if (pts and len(pts) <= 64) else (0 if V == 0 else None)
                c2 = []
                if a["one_in_W"] and V > 0:
                    c2.append("one_in_W_but_SAT")
                if cell["r_V"] is not None and a["codim"] < cell["r_V"]:
                    c2.append("codim_below_r_V")
                if not enum["agree"]:
                    c2.append("enumerations_disagree")
                if bp:
                    sc = soundness_check(bp, pts[:64]); os.remove(bp)
                    cell["soundness"] = sc
                    if not sc["pass"]:
                        c2.append("soundness_certificate_failed")
                cell["c2_disagreements"] = c2
            rec["solv"][str(D)] = cell
        ds = [D for D in (2, 3, 4) if rec["solv"][str(D)].get("solv_holds")]
        rec["d_solv"] = min(ds) if ds else ">4"
        rec["status"] = "ok"
        os.remove(g)
    except Exception as e:
        rec["status"] = "failed_infrastructure"
        rec["error"] = repr(e)[:800]
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def main():
    n = int(sys.argv[1]); phase = sys.argv[2]; rd = sys.argv[3]
    st1 = os.environ["STAGE1_RUN"]
    s1 = json.load(open(os.path.join(st1, "raw-result.json")))
    assert s1["builder_equality_pass"], "Stage-1 gate not passed"
    anchor = None
    ap = os.path.join(st1, f"anchor_n{n}.json")
    if os.path.exists(ap):
        anchor = json.load(open(ap)); mod = anchor["modulus_int"]
    else:
        mod = CONWAY[n]
    tasks = []
    if anchor:
        tasks.append((n, "anchor", 0, mod, anchor, phase, None))
    if phase == "main":
        for fam in FAMILIES:
            for s in SEEDS:
                tasks.append((n, fam, s, mod, anchor, phase, None))
    else:
        order = ["planted", "uniform_z", "null", "known_false_a", "known_false_b"]
        for s in SEEDS:
            for fam in order:
                tasks.append((n, fam, s, mod, anchor, phase, None))
    wall = float(os.environ.get("D5_WALL", "1e9"))
    workers = int(os.environ.get("WORKERS", "4"))
    t0 = time.time()
    out = {"schema": "EXP-SEMBIN-79a02d.stage2.raw.v1", "n": n, "phase": phase, "modulus_int": mod,
           "modulus_source": "Stage-1 hash-matched" if anchor else "CONWAY candidate (unverified)", "records": [],
           "not_started": []}
    with Pool(workers) as pool:
        pending = []
        it = iter(tasks)
        launched = 0
        for t in it:
            if time.time() - t0 > wall:
                out["not_started"].append({"family": t[1], "seed": t[2], "reason": "wall-clock allowance reached (censored, O-IMPEDIMENT-type, not evidence)"})
                continue
            pending.append(pool.apply_async(process, (t,)))
            launched += 1
            # throttle: keep at most `workers` outstanding so the wall check is meaningful
            while len([p for p in pending if not p.ready()]) >= workers:
                time.sleep(0.5)
        for p in pending:
            r = p.get()
            out["records"].append(r)
            print(json.dumps({k: r.get(k) for k in ("n", "family", "seed", "status", "V_count", "d_ff_ic", "d_solv", "seconds")}), flush=True)
    ok = [r for r in out["records"] if r.get("status") == "ok"]
    out["manifest_summary"] = {"status": "completed_valid" if ok else "failed_infrastructure",
                               "validity_reason": f"{len(ok)}/{len(out['records'])} instance records ok; {len(out['not_started'])} censored by wall allowance",
                               "records_ok": len(ok), "records_total": len(out["records"]), "censored": len(out["not_started"])}
    json.dump(out, open(os.path.join(rd, "raw-result.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
