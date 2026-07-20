# EXP-SIG-002 driver — growth resolution of the residual non-rewritable D4
# syzygy family (H-SIG-001; dispatched by DEC-20260718-015).
#
# Reuses the EXP-SIG-001 instrument BIT-IDENTICALLY (src/h013_f5_signatures.sage
# sha256 1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087).
#
# Usage (from repo root):
#   sage experiments/EXP-SIG-002/SIG2_run.sage --mode gate|boolean|d5 \
#        --out experiments/EXP-SIG-002/runs/RUN-EXP-SIG-002-X/raw.json [opts]
#
# Modes:
#   gate    — V1 null control (n=9,12; D=3,4), V2 injected-syzygy detection,
#             V3 T2-anchor sanity at n=15 seed 1 (D3 deficit 1, D4 deficit 40),
#             determinism rerun-check (n=15 seed 2 computed twice, compared
#             modulo timing fields only).
#   boolean — per n: probe seeds in order, record EVERY probed cell, flag
#             degenerate R_x = 0 instances (retained as observations, excluded
#             from the growth series), continue probing until
#             --required-nondegenerate non-degenerate cells are collected
#             (cap --max-probed-seeds). Null control evaluated on every cell.
#   d5      — D=5 count-only cells (sem; matched null too unless --d5-null 0),
#             launched in the order given (ascending n recommended) under the
#             soft cap so censoring hits the expensive tail first.
import sys, os, time, json, argparse, platform, datetime
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--mode', required=True, choices=['gate', 'boolean', 'd5'])
p.add_argument('--out', required=True)
p.add_argument('--n-list', default='9,12')
p.add_argument('--seeds', default='1,2,3')
p.add_argument('--required-nondegenerate', type=int, default=3)
p.add_argument('--max-probed-seeds', type=int, default=8)
p.add_argument('--d5-cells', default='', help='comma list of n:seed for D=5 count-only')
p.add_argument('--d5-null', default='1', help='1 = also measure matched null at D=5')
p.add_argument('--soft-cap', type=int, default=480,
               help='stop launching new cells after this many seconds')
args = p.parse_args()

EXPDIR = Path(args.out).resolve().parents[2]
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
from sage.all import GF, PolynomialRing, EllipticCurve, set_random_seed
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

t_start = time.time()
started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

out = {
    "experiment": "EXP-SIG-002",
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

def is_degenerate(meta):
    """R_x = 0 (2-torsion decomposition target) — the EXP-SIG-001 n=12 seed-1
    anomaly. Detected from the recorded R_x string."""
    return str(meta.get("R_x", "")).strip() == "0"

def strip_timing(rec):
    """Determinism comparison modulo timing fields only."""
    if isinstance(rec, dict):
        return {k: strip_timing(v) for k, v in rec.items()
                if k not in ("sec", "wall_s", "elapsed_s_so_far")}
    if isinstance(rec, list):
        return [strip_timing(v) for v in rec]
    return rec

# ==========================================================================
if args.mode == 'gate':
    print("=== EXP-SIG-002 GATE: V1 null, V2 injected, V3 T2 anchor, determinism ===", flush=True)
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

    # ---- V3: T2 anchor at n=15 seed 1 (certified in EXP-SIG-001):
    # D3 deficit = extra = 1, D4 deficit = extra = 8n/3 = 40, null extras 0.
    cell15 = classify_cell(15, 3, 1, [3, 4])
    d3 = cell15["sem"]["3"]; d4 = cell15["sem"]["4"]
    cond = (d3["deficit"] == 1 and d3["extra"] == 1
            and d4["deficit"] == 40 and d4["extra"] == 40
            and cell15["null"]["3"]["extra"] == 0 and cell15["null"]["4"]["extra"] == 0
            and cell15["v3_multiples_at_D4"]["residual_new_at_D4"] == 10)
    print("  V3 T2-anchor semaev n=15 seed 1: def(3)=%d extra(3)=%d def(4)=%d extra(4)=%d residual=%d null-extra=%d/%d -> %s" % (
        d3["deficit"], d3["extra"], d4["deficit"], d4["extra"],
        cell15["v3_multiples_at_D4"]["residual_new_at_D4"],
        cell15["null"]["3"]["extra"], cell15["null"]["4"]["extra"],
        "ok" if cond else "FAIL"), flush=True)
    out["cells"].append({"kind": "V3_t2_anchor", "cell": cell15, "pass": bool(cond)})
    gate_checks.append(cond)
    flush()

    # ---- determinism: n=15 seed 2 computed twice, identical modulo timing
    c1 = classify_cell(15, 3, 2, [3, 4])
    c2 = classify_cell(15, 3, 2, [3, 4])
    same = (json.dumps(jsonsafe(strip_timing(c1)), sort_keys=True)
            == json.dumps(jsonsafe(strip_timing(c2)), sort_keys=True))
    out["cells"].append({"kind": "rerun_check", "n": 15, "seed": 2,
                         "comparison": "all fields except sec/wall_s",
                         "identical": bool(same)})
    print("  [rerun-check n=15 seed=2] identical (modulo timing): %s" % same, flush=True)
    gate_checks.append(same)
    flush()

    out["gate"] = "PASS" if all(gate_checks) else "FAIL"
    print("=== GATE: %s ===" % out["gate"], flush=True)

# ==========================================================================
elif args.mode == 'boolean':
    n_list = [int(x) for x in args.n_list.split(',')]
    seeds = [int(x) for x in args.seeds.split(',')]
    seed_candidates = list(dict.fromkeys(
        seeds + list(range(1, args.max_probed_seeds + 1))))
    print("=== EXP-SIG-002 boolean arm: n=%s seed candidates=%s (need %d non-degenerate per size) ===" % (
        n_list, seed_candidates, args.required_nondegenerate), flush=True)
    null_violations = []
    for n in n_list:
        collected = 0
        probed = 0
        for seed in seed_candidates:
            if collected >= args.required_nondegenerate:
                break
            if probed >= args.max_probed_seeds:
                out["cells"].append({"kind": "boolean", "n": n,
                                     "status": "seed probe cap reached with %d non-degenerate" % collected})
                flush()
                break
            if softcap_hit():
                out["cells"].append({"kind": "boolean", "n": n, "seed": seed,
                                     "status": "not_run: soft budget cap"})
                flush()
                continue
            probed += 1
            t0 = time.time()
            cell = classify_cell(n, 3, seed, [3, 4])
            cell["kind"] = "boolean"
            cell["wall_s"] = round(time.time() - t0, 2)
            if cell.get("skipped"):
                cell["status"] = "skipped: no decomposable R"
                out["cells"].append(cell)
                flush()
                continue
            degen = is_degenerate(cell["meta"])
            cell["degenerate_rx_zero"] = bool(degen)
            s3 = cell["sem"].get("3", {})
            s4 = cell["sem"].get("4", {})
            n3 = cell["null"].get("3", {})
            n4 = cell["null"].get("4", {})
            # per-cell controls
            null_ok = (n3.get("extra") == 0 and n4.get("extra") == 0
                       and n3.get("rank") == n3.get("sr_pred")
                       and n4.get("rank") == n4.get("sr_pred"))
            cell["controls"] = {
                "null_extra_zero": bool(null_ok),
                "t2_d4_deficit_eq_8n_over_3": bool(s4.get("deficit") == (8 * n) // 3),
                "t2_d3_deficit_eq_1": bool(s3.get("deficit") == 1),
            }
            if not null_ok:
                null_violations.append({"n": n, "seed": seed})
            if not degen:
                collected += 1
            v3m = cell.get("v3_multiples_at_D4", {})
            print("  [n=%d seed=%d]%s nb=%s R_x=%s | D3: def=%s extra=%s rankK=%s | D4: def=%s extra=%s rankK=%s residual=%s | null extra=%s/%s (%.1fs)" % (
                n, seed, " [DEGENERATE R_x=0]" if degen else "",
                cell["meta"].get("nb"), str(cell["meta"].get("R_x"))[:24],
                s3.get("deficit"), s3.get("extra"), s3.get("rankK"),
                s4.get("deficit"), s4.get("extra"), s4.get("rankK"),
                v3m.get("residual_new_at_D4"),
                n3.get("extra"), n4.get("extra"), cell["wall_s"]), flush=True)
            out["cells"].append(cell)
            flush()
        out.setdefault("growth_series", {})[str(n)] = {
            "nondegenerate_cells": collected, "seeds_probed": probed}
        flush()
    out["controls"] = {
        "null_extra_zero_all_cells": (len(null_violations) == 0),
        "null_violations": null_violations,
    }
    flush()

# ==========================================================================
elif args.mode == 'd5':
    cells_req = []
    for tok in args.d5_cells.split(','):
        tok = tok.strip()
        if not tok:
            continue
        nn, ss = tok.split(':')
        cells_req.append((int(nn), int(ss)))
    do_null = args.d5_null == '1'
    print("=== EXP-SIG-002 D=5 count-only arm: cells=%s null=%s ===" % (
        cells_req, do_null), flush=True)
    d5_null_violations = []
    for (nn, ss) in cells_req:
        # sem cell
        if softcap_hit():
            out["cells"].append({"kind": "boolean_d5", "n": nn, "seed": ss,
                                 "status": "not_run: soft budget cap"})
            flush()
        else:
            t0 = time.time()
            monosets, nb, meta = build_boolean_semaev(nn, 3, ss)
            if monosets is None:
                out["cells"].append({"kind": "boolean_d5", "n": nn, "seed": ss,
                                     "status": "skipped: no decomposable R", "meta": meta})
                flush()
                continue
            rec5, _, _, _ = analyze_syzygy_space(monosets, nb, 5, extract=False, block_size=nn)
            rec5.pop("extra_reps", None)
            degen = is_degenerate(meta)
            out["cells"].append({"kind": "boolean_d5", "n": nn, "seed": ss, "meta": meta,
                                 "degenerate_rx_zero": bool(degen),
                                 "sem5": rec5, "wall_s": round(time.time() - t0, 2)})
            print("  [D5 sem n=%d seed=%d]%s nrows=%d rank=%d pred=%d deficit=%d kernel=%d rankK=%d extra=%d (%.1fs)" % (
                nn, ss, " [DEGENERATE]" if degen else "", rec5["nrows"], rec5["rank"],
                rec5["sr_pred"], rec5["deficit"], rec5["kernel_dim"], rec5["rankK"],
                rec5["extra"], time.time() - t0), flush=True)
            flush()
        # matched null cell
        if do_null:
            if softcap_hit():
                out["cells"].append({"kind": "null_d5", "n": nn, "seed": ss,
                                     "status": "not_run: soft budget cap"})
                flush()
            else:
                t0 = time.time()
                monosets, nb, meta = build_boolean_semaev(nn, 3, ss)
                rng = random.Random(stable_seed("null", nn, 3, ss))
                null_ms = boolean_null(monosets, nb, rng)
                recn5, _, _, _ = analyze_syzygy_space(null_ms, nb, 5, extract=False, block_size=nn)
                recn5.pop("extra_reps", None)
                ok = (recn5["extra"] == 0 and recn5["rank"] == recn5["sr_pred"])
                if not ok:
                    d5_null_violations.append({"n": nn, "seed": ss})
                out["cells"].append({"kind": "null_d5", "n": nn, "seed": ss,
                                     "null5": recn5, "controls": {"null_extra_zero": bool(ok)},
                                     "wall_s": round(time.time() - t0, 2)})
                print("  [D5 null n=%d seed=%d] nrows=%d rank=%d pred=%d deficit=%d kernel=%d rankK=%d extra=%d -> %s (%.1fs)" % (
                    nn, ss, recn5["nrows"], recn5["rank"], recn5["sr_pred"],
                    recn5["deficit"], recn5["kernel_dim"], recn5["rankK"],
                    recn5["extra"], "ok" if ok else "FAIL", time.time() - t0), flush=True)
                flush()
    out["controls"] = {
        "null_extra_zero_all_d5_cells": (len(d5_null_violations) == 0),
        "null_violations": d5_null_violations,
    }
    flush()

out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
