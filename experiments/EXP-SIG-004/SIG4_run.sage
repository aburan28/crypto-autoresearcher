# EXP-SIG-004 driver — residual series re-anchor with canonical reduction
# (H-SIG-001; dispatched by DEC-20260718-019 next_actions, handoff TASK-20260718-SIG-F4).
#
# Reuses the EXP-SIG-001/002/003 instrument BIT-IDENTICALLY
# (src/h013_f5_signatures.sage sha256
# 1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087).
# All re-measurement logic lives in this driver; the pinned instrument is
# loaded, never modified. full_reduce is copied VERBATIM from
# experiments/EXP-SIG-003/SIG3_run.sage (canonical, rank-exact).
#
# Usage (from repo root):
#   sage experiments/EXP-SIG-004/SIG4_run.sage --mode gate \
#        --out experiments/EXP-SIG-004/runs/RUN-EXP-SIG-004-a/raw.json
#   sage experiments/EXP-SIG-004/SIG4_run.sage --mode cells \
#        --cells 9:1:sem,9:1:null --out .../raw.json
#
# Per cell (n, seed, arm):
#   D3/D4 classification with kernel bases (extract=True);
#   v3_mults = monomial multiples {x_j * kernel_3} embedded at D4 (VERBATIM
#     EXP-SIG-002 construction);
#   residual_old = extra_4 - rank mod K4 via the instrument's early-break
#     reduce_against (VERBATIM pinned semantics — continuity anchor);
#   residual_new = extra_4 - rank mod K4 via canonical full_reduce
#     (rank-exact — the corrected measure);
#   union_check  = rank(v3_mults u K4) - rank(K4) (reduction-free exact
#     quotient rank; MUST equal rank_v3mod_new — control C8);
#   continuity: rank_v3mod_new <= rank_v3mod_old must hold on every cell
#     (control C7); on a STANDARD sem cell, residual_new < residual_old
#     halts the driver at the cell boundary (mission stop rule).
#
# Instance filter (C9, input-side, verbatim EXP-SIG-002): standard :=
# (R_x != 0) AND (no degree-1 equation in eq_degs_hist).
#
# Controls: C1 null residual gate, C2 injected detection, C3 T2 anchor,
# C4 determinism (in-run + cross-invocation via RUN-g/RUN-h),
# C5 null residual == 0 on every cell, C6 T2 8n/3 at n >= 12,
# C7 continuity, C8 union cross-check.

import sys, os, time, json, argparse, platform, datetime, itertools, hashlib
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--mode', required=True, choices=['gate', 'cells'])
p.add_argument('--out', required=True)
p.add_argument('--cells', default='',
               help='comma list of n:seed:arm, arm in {sem,null}')
p.add_argument('--soft-cap', type=int, default=540,
               help='do not start a new cell after this many seconds')
args = p.parse_args()

EXPDIR = Path(args.out).resolve().parents[2]
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
from sage.all import GF, PolynomialRing, set_random_seed
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

t_start = time.time()
started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256(pth):
    return hashlib.sha256(Path(pth).read_bytes()).hexdigest()


PINNED_HASHES = {
    "h013_f5_signatures.sage":
        "1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087",
    "semaev_tree.py":
        "e9f1681b4e422f7a67176fffd3e5f91ab7a95c9fddc1eb925c2bb0a93a9becef",
    "ic_first_fall_fast.py":
        "f1c98bd8642df226760f43038d6687e73794d04b9c7a9073f244b8a0433fad61",
    "macaulay_export.py":
        "c00b8aad9ad47f8a3f09c39f6b65062a37562703bfd1c4f6159b1e54b1dbad97",
}
instrument_hashes = {f.name: sha256(f) for f in sorted((EXPDIR / 'src').iterdir())}
instrument_ok = all(instrument_hashes.get(k) == v for k, v in PINNED_HASHES.items())

# EXP-SIG-002 anchored per-cell residuals (pinned semantics), analysis.md §3.1.
OLD_RESIDUAL = {9: {1: 23, 2: 23, 3: 23},
                12: {2: 9, 4: 9, 5: 9, 6: 9, 7: 9},
                15: {1: 10, 3: 10, 4: 10, 5: 10, 6: 10},
                18: {1: 13, 2: 13, 3: 13},
                21: {1: 14, 2: 14, 3: 14}}
OLD_FILTERED = {(12, 1): 82, (12, 3): 0, (15, 2): 0}

out = {
    "experiment": "EXP-SIG-004",
    "mode": args.mode,
    "args": vars(args),
    "environment": {
        "sage_version": str(sage.version.version),
        "python_version": sys.version.split()[0],
        "os": platform.platform(),
        "machine": platform.machine(),
    },
    "instrument_sha256": instrument_hashes,
    "instrument_sha256_matches_pinned": bool(instrument_ok),
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


def full_reduce(v, piv):
    """Canonical reduction of v modulo the echelon pivot family piv (lead ->
    vector, lead = highest set bit). Unlike the instrument's reduce_against
    (which stops at the topmost non-pivot bit and is exact only for
    membership testing), this clears EVERY pivot-lead bit top-down, so the
    result is the unique canonical remainder: full_reduce(v) = 0 iff v is in
    the span, and full_reduce is LINEAR. Consequently
    rank(full_reduce(family)) == the family's TRUE rank mod span(piv).
    (Copied verbatim from experiments/EXP-SIG-003/SIG3_run.sage; the pilot
    RUN-EXP-SIG-003-a proved the early-break variant overestimates quotient
    ranks.)"""
    bb = int(v)
    out = 0
    while bb:
        lead = bb.bit_length() - 1
        if lead in piv:
            bb = bb ^^ piv[lead]
        else:
            out = out | (1 << lead)
            bb = bb ^^ (1 << lead)
    return out


def halt(code, reason, cell=None):
    """Mission stop rule (C7/C8): flush everything and exit at a checkpoint."""
    out["halt"] = {"reason": reason, "cell": cell,
                   "at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out["wall_seconds"] = round(time.time() - t_start, 2)
    flush()
    print("HALT: %s" % reason, flush=True)
    sys.exit(code)


def measure_cell(n, seed, arm):
    """Full both-reduction measurement of one (n, seed, arm) cell."""
    t0 = time.time()
    monosets, nb, meta = build_boolean_semaev(n, 3, seed)
    if monosets is None:
        return {"n": n, "seed": seed, "arm": arm,
                "status": "skipped: no decomposable R", "meta": meta}
    rx_zero = str(meta.get("R_x", "")).strip() == "0"
    has_lin = int(meta.get("eq_degs_hist", {}).get("1", 0)) > 0
    standard = (not rx_zero) and (not has_lin)
    cell = {"n": n, "seed": seed, "arm": arm, "nb": int(nb), "meta": meta,
            "filter": {"rx_zero": bool(rx_zero), "has_linear_eq": bool(has_lin),
                       "standard": bool(standard)},
            "status": "completed"}
    ms = monosets
    if arm == "null":
        rng = random.Random(stable_seed("null", n, 3, seed))
        ms = boolean_null(monosets, nb, rng)

    rec3, rows3, kernel3, kpiv3 = analyze_syzygy_space(ms, nb, 3,
                                                       extract=True, block_size=n)
    rec4, rows4, kernel4, kpiv4 = analyze_syzygy_space(ms, nb, 4,
                                                       extract=True, block_size=n)
    cell["D3"] = rec3
    cell["D4"] = rec4

    # ---- v3 multiples at D4: VERBATIM EXP-SIG-002 construction
    tag2idx4 = {tag: ix for ix, (tag, _) in enumerate(rows4)}
    v3_mults = []
    for kv in kernel3:
        pos3 = bits_to_positions(kv)
        tags3 = [rows3[pp][0] for pp in pos3]
        for j in range(nb):
            img = 0
            for (i, mu) in tags3:
                ix = tag2idx4.get((i, mu | {j}))
                if ix is not None:
                    img = img ^^ (1 << ix)
            if img:
                v3_mults.append(int(img))

    # ---- old (pinned, early-break) semantics — continuity anchor
    red_old = [reduce_against(v, kpiv4) for v in v3_mults]
    red_old = [r for r in red_old if r]
    rank_old, _ = vec_echelon(red_old)
    residual_old = int(rec4["extra"] - rank_old)

    # ---- new (canonical full_reduce) semantics — corrected measure
    red_new = [full_reduce(v, kpiv4) for v in v3_mults]
    red_new = [r for r in red_new if r]
    rank_new, _ = vec_echelon(red_new)
    residual_new = int(rec4["extra"] - rank_new)

    # ---- C8: reduction-free exact cross-check: rank mod K4 = rank(union) - rankK
    rank_union, _ = vec_echelon(list(kpiv4.values()) + v3_mults)
    union_check = int(rank_union - rec4["rankK"])

    cell["v3_multiples_at_D4"] = {
        "n_d3_syzygies": len(kernel3),
        "n_mult_images": len(v3_mults),
        "rank_mod_K4_pinned": int(rank_old),
        "residual_pinned": residual_old,
        "rank_mod_K4_canonical": int(rank_new),
        "residual_canonical": residual_new,
        "delta_corrected_minus_pinned": int(residual_new - residual_old),
        "union_crosscheck_rank": union_check,
        "reduction_semantics": ("pinned=instrument early-break reduce_against "
                                "(verbatim); canonical=full_reduce copied "
                                "verbatim from EXP-SIG-003 SIG3_run.sage"),
    }
    cell["d3_non_koszul_count"] = int(rec3["extra"])

    # ---- controls
    old_anchor = OLD_RESIDUAL.get(n, {}).get(seed)
    ctl = {
        "c7_continuity_new_le_old_rank": bool(rank_new <= rank_old),
        "c7_continuity_residual_new_ge_old": bool(residual_new >= residual_old),
        "c8_union_crosscheck_eq_canonical": bool(union_check == rank_new),
        "residual_new_nonneg": bool(residual_new >= 0),
        "rank_new_le_extra4": bool(rank_new <= rec4["extra"]),
    }
    if arm == "sem":
        ctl.update({
            "c6_t2_d4_deficit_eq_8n_over_3": bool(rec4["deficit"] == (8 * n) // 3),
            "c6_t2_d3_deficit_eq_1": bool(rec3["deficit"] == 1 and rec3["extra"] == 1),
            "d4_deficit_recorded": int(rec4["deficit"]),
            "exp_sig_002_anchor_residual": old_anchor,
            "pinned_reproduces_exp_sig_002": (None if old_anchor is None
                                              else bool(residual_old == old_anchor)),
        })
    else:
        ctl.update({
            "c5_null_extra_zero_d3d4": bool(rec3["extra"] == 0 and rec4["extra"] == 0),
            "c5_null_rank_eq_sr_pred": bool(rec3["rank"] == rec3["sr_pred"]
                                            and rec4["rank"] == rec4["sr_pred"]),
            "c5_null_residual_pinned_zero": bool(residual_old == 0),
            "c5_null_residual_canonical_zero": bool(residual_new == 0),
        })
    cell["controls"] = ctl
    cell["wall_s"] = round(time.time() - t0, 2)

    # ---- mission stop rules (checkpoint boundary; the violating cell's full
    # payload is appended BEFORE halting so no measurement is lost)
    if not ctl["c8_union_crosscheck_eq_canonical"]:
        out["cells"].append(cell)
        halt(3, "C8 union cross-check mismatch (driver bug): canonical rank %d "
                "!= union-minus-rankK %d" % (rank_new, union_check),
             cell={"n": n, "seed": seed, "arm": arm})
    if arm == "sem" and standard and residual_new < residual_old:
        out["cells"].append(cell)
        halt(2, "C7 CONTINUITY VIOLATION on a standard instance: corrected "
                "residual %d < pinned residual %d at n=%d seed=%d — "
                "contradicts the caveat direction; stop and report"
                % (residual_new, residual_old, n, seed),
             cell={"n": n, "seed": seed, "arm": arm})
    return cell


def strip_timing(o):
    if isinstance(o, dict):
        return {k: strip_timing(v) for k, v in o.items()
                if k not in ("sec", "wall_s", "wall_seconds", "elapsed_s_so_far")}
    if isinstance(o, list):
        return [strip_timing(v) for v in o]
    return o


# ==========================================================================
if args.mode == 'gate':
    print("=== EXP-SIG-004 GATE: C1 null residual, C2 injected, C3 T2 anchor, "
          "C4a in-run determinism ===", flush=True)
    gate_checks = []
    if not instrument_ok:
        print("  INstrument sha256 MISMATCH vs pinned set: %s" % instrument_hashes,
              flush=True)
        out["cells"].append({"kind": "instrument_hash", "pass": False,
                             "hashes": instrument_hashes})
        gate_checks.append(False)
        out["gate"] = "FAIL"
        flush()
        sys.exit(1)
    out["cells"].append({"kind": "instrument_hash", "pass": True,
                         "hashes": instrument_hashes})
    flush()

    # ---- C1: support-matched null must have residual 0 under BOTH reductions
    for n in (9, 12):
        c = measure_cell(n, 1, "null")
        c["kind"] = "C1_null_residual"
        v3 = c["v3_multiples_at_D4"]
        cond = (c["D3"]["extra"] == 0 and c["D4"]["extra"] == 0
                and c["D3"]["rank"] == c["D3"]["sr_pred"]
                and c["D4"]["rank"] == c["D4"]["sr_pred"]
                and v3["residual_pinned"] == 0 and v3["residual_canonical"] == 0
                and c["controls"]["c8_union_crosscheck_eq_canonical"])
        c["pass"] = bool(cond)
        gate_checks.append(cond)
        print("  C1 null n=%d: extra=%d/%d rank==pred=%s residual pinned/canon=%d/%d -> %s (%.1fs)" % (
            n, c["D3"]["extra"], c["D4"]["extra"],
            c["controls"]["c5_null_rank_eq_sr_pred"],
            v3["residual_pinned"], v3["residual_canonical"],
            "ok" if cond else "FAIL", c["wall_s"]), flush=True)
        out["cells"].append(c)
        flush()

    # ---- C2: injected KNOWN non-Koszul linear syzygy must be detected
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
    print("  C2 injected (gens %d,%d,%d): extra=%d, detected 3-generator constant-multiplier rep: %s -> %s" % (
        q0, q1, c0, rec["extra"], det, "ok" if cond else "FAIL"), flush=True)
    out["cells"].append({"kind": "C2_injected", "n": n, "gens": [q0, q1, c0],
                         "rec": rec, "detected": det, "detected_rep": det_rep,
                         "pass": bool(cond)})
    gate_checks.append(cond)
    flush()

    # ---- C3: T2 anchor continuity at n=15 seed 1 (EXP-SIG-001/002 certified)
    c = measure_cell(15, 1, "sem")
    c["kind"] = "C3_t2_anchor"
    v3 = c["v3_multiples_at_D4"]
    cond = (c["D3"]["deficit"] == 1 and c["D3"]["extra"] == 1
            and c["D4"]["deficit"] == 40 and c["D4"]["extra"] == 40
            and v3["residual_pinned"] == 10
            and c["controls"]["c7_continuity_residual_new_ge_old"]
            and c["controls"]["c8_union_crosscheck_eq_canonical"])
    c["pass"] = bool(cond)
    gate_checks.append(cond)
    print("  C3 T2 anchor n=15 s1: D3 def=%d D4 def=%d residual pinned=%d canonical=%d -> %s (%.1fs)" % (
        c["D3"]["deficit"], c["D4"]["deficit"], v3["residual_pinned"],
        v3["residual_canonical"], "ok" if cond else "FAIL", c["wall_s"]), flush=True)
    out["cells"].append(c)
    flush()

    # ---- C4a: in-run determinism — n=15 seed 3 sem computed twice
    c1 = measure_cell(15, 3, "sem")
    c2 = measure_cell(15, 3, "sem")
    same = (json.dumps(jsonsafe(strip_timing(c1)), sort_keys=True)
            == json.dumps(jsonsafe(strip_timing(c2)), sort_keys=True))
    out["cells"].append({"kind": "C4a_rerun_check", "n": 15, "seed": 3, "arm": "sem",
                         "comparison": "all fields except sec/wall_s",
                         "identical": bool(same)})
    print("  [C4a in-run determinism n=15 seed=3 sem] identical (modulo timing): %s" % same, flush=True)
    gate_checks.append(same)
    flush()

    out["gate"] = "PASS" if all(gate_checks) else "FAIL"
    print("=== GATE: %s ===" % out["gate"], flush=True)

# ==========================================================================
elif args.mode == 'cells':
    tokens = []
    for tok in args.cells.split(','):
        tok = tok.strip()
        if not tok:
            continue
        nn, ss, aa = tok.split(':')
        tokens.append((int(nn), int(ss), aa))
    print("=== EXP-SIG-004 cells arm: %d cells: %s ===" % (len(tokens), tokens), flush=True)
    control_failures = []
    for (nn, ss, aa) in tokens:
        if softcap_hit():
            out["cells"].append({"n": nn, "seed": ss, "arm": aa,
                                 "status": "not_run: soft budget cap"})
            flush()
            continue
        t0 = time.time()
        cell = measure_cell(nn, ss, aa)
        out["cells"].append(cell)
        if cell.get("status") != "completed":
            print("  [n=%d seed=%d %s] %s" % (nn, ss, aa, cell.get("status")), flush=True)
            flush()
            continue
        v3 = cell["v3_multiples_at_D4"]
        ctl = cell["controls"]
        standard = cell["filter"]["standard"]
        # C6 T2 anchors are controls on STANDARD cells only; on filtered
        # (recorded-observation) instances they are not control conditions.
        # At n=9 the D4 deficit 41 != 24 is a recorded observation, not a failure.
        ignore = {"c6_t2_d4_deficit_eq_8n_over_3"}
        if not standard:
            ignore |= {"c6_t2_d3_deficit_eq_1", "c6_t2_d4_deficit_eq_8n_over_3",
                       "pinned_reproduces_exp_sig_002"}
        fail = [k for k, v in ctl.items()
                if isinstance(v, bool) and v is False and k not in ignore]
        if (aa == "sem" and standard and nn >= 12
                and not ctl["c6_t2_d4_deficit_eq_8n_over_3"]):
            fail.append("c6_t2_d4_deficit_eq_8n_over_3")
        if aa == "sem" and cell["filter"]["standard"] and ctl.get("pinned_reproduces_exp_sig_002") is False:
            fail.append("pinned_reproduces_exp_sig_002")
        if fail:
            control_failures.append({"n": nn, "seed": ss, "arm": aa, "failed": fail})
        print("  [n=%d seed=%d %s]%s D3: def=%d extra=%d | D4: def=%d extra=%d rankK=%d | "
              "imgs=%d rank_old=%d rank_new=%d union=%d | residual old=%d new=%d (delta %+d)%s (%.1fs)" % (
                  nn, ss, aa, "" if cell["filter"]["standard"] else " [FILTERED]",
                  cell["D3"]["deficit"], cell["D3"]["extra"],
                  cell["D4"]["deficit"], cell["D4"]["extra"], cell["D4"]["rankK"],
                  v3["n_mult_images"], v3["rank_mod_K4_pinned"],
                  v3["rank_mod_K4_canonical"], v3["union_crosscheck_rank"],
                  v3["residual_pinned"], v3["residual_canonical"],
                  v3["delta_corrected_minus_pinned"],
                  " FAIL:" + ",".join(fail) if fail else "",
                  cell["wall_s"]), flush=True)
        flush()
    out["controls"] = {
        "all_cell_controls_pass": (len(control_failures) == 0),
        "control_failures": control_failures,
    }
    flush()

out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
