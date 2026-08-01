# EXP-SIG-005 driver — cascade-law falsifiable checks
# (H-SIG-001; dispatched by DEC-20260718-020 next_actions, handoff
# TASK-20260718-SIGCHK).
#
# Reuses the EXP-SIG-001/002/003/004 instrument BIT-IDENTICALLY
# (src/h013_f5_signatures.sage sha256
# 1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087).
# The pinned instrument is loaded, never modified. full_reduce is copied
# VERBATIM from EXP-SIG-003 SIG3_run.sage / EXP-SIG-004 SIG4_run.sage
# (canonical, rank-exact).
#
# P1 (mode p1, cells n:seed:arm): n=24 D4 residual check, verbatim
#   EXP-SIG-004 both-reduction construction: residual_canonical/pinned =
#   extra_4 - rank(v3 multiples mod K4), union cross-check, filter fields,
#   null-arm controls. Predictions (standard sem cells): residual_canonical
#   == 17, D4 deficit == 64, D3 non-Koszul count == 1, null residual 0.
#
# P2 (mode p2, single cell): D6 residual-birth measurement at n=12:
#   residual_6 = extra_6 - A5, A5 = rank mod K6 of the multiplication
#   closure of ALL lower-degree non-model syzygies:
#     F3 = images(kernel3 extras, mults deg <= 3)
#     F4 = images(kernel4 extras, mults deg <= 2)
#     F5 = images(kernel5 extras, mults deg <= 1)
#   A3_6 = rank(F3), A4_6 = rank(F3 u F4), A5 = rank(F3 u F4 u F5) mod K6.
#   Extra bases are the canonical full_reduce quotient reps of each kernel
#   mod its K_D (exact; the K_D part's images lie in K_{D+1}...K_6 by the
#   Koszul/principal composition argument of EXP-SIG-003). Closure ranks
#   computed TWO ways (incremental-merged pivots; independent
#   full_reduce-mod-K6 family ranks) plus a reduction-free union echelon
#   cross-check (control C6). Continuity anchors (C9): EXP-SIG-003's
#   n=12 seed 2 D3/D4/D5 counts, residual_4 == 9, A3_5 == 242, A4_5 == 444,
#   residual_5 == 878 — verified BEFORE the expensive D6 stage.
#   Birth prediction: residual_6 > 0.
#
# Checkpoint/kill rule (spec stopping_rules): the driver checks a soft cap
# (default 520 s) before every stage/cell, and wraps the D6 classification
# and closure-rank stages in a driver-level SIGALRM timer. A firing timer
# records the stage as censored_timeout (infrastructure censoring, AGENTS
# rule 5 — NOT evidence) and the run ends cleanly with everything completed
# flushed. The instrument itself is untouched.
#
# Usage (from repo root):
#   sage experiments/EXP-SIG-005/SIG5_run.sage --mode gate \
#        --out experiments/EXP-SIG-005/runs/RUN-EXP-SIG-005-a/raw.json
#   sage experiments/EXP-SIG-005/SIG5_run.sage --mode p1 \
#        --cells 24:1:sem,24:1:null --out .../raw.json
#   sage experiments/EXP-SIG-005/SIG5_run.sage --mode p2 --n 12 --seed 2 \
#        --arm sem --out .../raw.json

import sys, os, time, json, argparse, platform, datetime, itertools, hashlib
import signal, gc
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--mode', required=True, choices=['gate', 'p1', 'p2'])
p.add_argument('--out', required=True)
p.add_argument('--cells', default='',
               help='p1: comma list of n:seed:arm, arm in {sem,null}')
p.add_argument('--n', type=int, default=12)
p.add_argument('--seed', type=int, default=2)
p.add_argument('--arm', default='sem', choices=['sem', 'null'])
p.add_argument('--soft-cap', type=int, default=520,
               help='do not start a new stage/cell after this many seconds')
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

out = {
    "experiment": "EXP-SIG-006",
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


class StageTimeout(Exception):
    pass


def _alarm_handler(signum, frame):
    raise StageTimeout()


def stage_timer(seconds):
    """Arm a driver-level SIGALRM for at most `seconds` (>=1)."""
    signal.signal(signal.SIGALRM, _alarm_handler)
    signal.setitimer(signal.ITIMER_REAL, max(1.0, float(seconds)))


def cancel_timer():
    signal.setitimer(signal.ITIMER_REAL, 0)


def full_reduce(v, piv):
    """Canonical reduction of v modulo the echelon pivot family piv (lead ->
    vector, lead = highest set bit). Unlike the instrument's reduce_against
    (which stops at the topmost non-pivot bit and is exact only for
    membership testing), this clears EVERY pivot-lead bit top-down, so the
    result is the unique canonical remainder: full_reduce(v) = 0 iff v is in
    the span, and full_reduce is LINEAR. Consequently
    rank(full_reduce(family)) == the family's TRUE rank mod span(piv).
    (Copied verbatim from experiments/EXP-SIG-003/SIG3_run.sage.)"""
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


def multiplier_sets(nb, maxdeg):
    ms = [frozenset()]
    for md in range(1, maxdeg + 1):
        for combo in itertools.combinations(range(nb), md):
            ms.append(frozenset(combo))
    return ms


def images_of(kernel_basis, rows_src, tag2idx, mults):
    """Monomial multiples of kernel-basis syzygies embedded in the target
    row space. Returns (list of GF(2) bitmasks over target row indices,
    miss count). Verbatim EXP-SIG-003 construction."""
    imgs = []
    misses = 0
    for kv in kernel_basis:
        pos = bits_to_positions(kv)
        tags = [rows_src[pp][0] for pp in pos]
        for nu in mults:
            img = 0
            for (i, mu) in tags:
                ix = tag2idx.get((i, mu | nu))
                if ix is None:
                    misses += 1
                else:
                    img = img ^^ (1 << ix)
            if img:
                imgs.append(int(img))
    return imgs, misses


def quotient_basis(kernel, kpiv):
    """Independent canonical basis of span(kernel) mod span(kpiv): full_reduce
    each kernel vector, drop zeros, echelon. Exact (full_reduce is linear)."""
    red = [full_reduce(kv, kpiv) for kv in kernel]
    red = [r for r in red if r]
    r, pr = vec_echelon(red)
    return list(pr.values()), r


def rank_reduced(vecs, piv):
    red = [full_reduce(v, piv) for v in vecs]
    red = [r for r in red if r]
    return vec_echelon(red)


def strip_timing(o):
    if isinstance(o, dict):
        return {k: strip_timing(v) for k, v in o.items()
                if k not in ("sec", "wall_s", "wall_seconds", "elapsed_s_so_far")}
    if isinstance(o, list):
        return [strip_timing(v) for v in o]
    return o


def halt(code, reason, cell=None):
    if cell is not None and cell not in out["cells"]:
        out["cells"].append(cell)
    out["halt"] = {"reason": reason, "cell": cell,
                   "at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out["wall_seconds"] = round(time.time() - t_start, 2)
    flush()
    print("HALT: %s" % reason, flush=True)
    sys.exit(code)


# ==========================================================================
# P1 cell: verbatim EXP-SIG-004 both-reduction D4 residual measurement
# ==========================================================================
def measure_p1_cell(n, seed, arm):
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

    # ---- v3 multiples at D4: VERBATIM EXP-SIG-002/004 construction
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

    # ---- pinned (early-break) semantics — continuity anchor
    red_old = [reduce_against(v, kpiv4) for v in v3_mults]
    red_old = [r for r in red_old if r]
    rank_old, _ = vec_echelon(red_old)
    residual_old = int(rec4["extra"] - rank_old)

    # ---- canonical full_reduce semantics — primary measure
    red_new = [full_reduce(v, kpiv4) for v in v3_mults]
    red_new = [r for r in red_new if r]
    rank_new, _ = vec_echelon(red_new)
    residual_new = int(rec4["extra"] - rank_new)

    # ---- C6: reduction-free exact cross-check
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

    ctl = {
        "c6_union_crosscheck_eq_canonical": bool(union_check == rank_new),
        "residual_new_nonneg": bool(residual_new >= 0),
        "rank_new_le_extra4": bool(rank_new <= rec4["extra"]),
    }
    if arm == "sem":
        ctl.update({
            "d4_deficit_recorded": int(rec4["deficit"]),
            "d4_extra_recorded": int(rec4["extra"]),
            "prediction_law_2n_over_3_plus_1": int((2 * n) // 3 + 1),
            "prediction_law_8n_over_3": int((8 * n) // 3),
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

    if not ctl["c6_union_crosscheck_eq_canonical"]:
        out["cells"].append(cell)
        halt(3, "C6 union cross-check mismatch (driver bug): canonical rank %d "
                "!= union-minus-rankK %d" % (rank_new, union_check),
             cell={"n": n, "seed": seed, "arm": arm})
    return cell


# ==========================================================================
# P2 cell: D6 residual-birth closure measurement
# ==========================================================================
SIG3_ANCHORS = {  # n=12 seed 2 sem, EXP-SIG-003 receipt values
    (12, 2): {"d3_deficit": 1, "d3_extra": 1, "d4_deficit": 32, "d4_extra": 32,
              "residual4_canonical": 9, "d5_rank": 28097, "d5_deficit": 1321,
              "d5_extra": 1322, "A3_5": 242, "A4_5": 444, "residual_5": 878},
}


def measure_p2_cell(n, seed, arm):
    t0 = time.time()
    stage_times = {}
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
    # append early + flush after every stage: a killed or censored invocation
    # still leaves a complete receipt of everything measured so far
    out["cells"].append(cell)
    stage_times["build_s"] = round(time.time() - t0, 2)
    print("  built: nb=%d n_eqs=%d hist=%s standard=%s (%.1fs)" % (
        nb, meta.get("n_eqs"), meta.get("eq_degs_hist"), standard,
        stage_times["build_s"]), flush=True)
    flush()

    ms = monosets
    if arm == "null":
        rng = random.Random(stable_seed("null", n, 3, seed))
        ms = boolean_null(monosets, nb, rng)

    # ---- D3 / D4 (extract=True on sem for the closure bases; count-only null)
    t1 = time.time()
    rec3, rows3, kernel3, kpiv3 = analyze_syzygy_space(
        ms, nb, 3, extract=(arm == "sem"), block_size=n)
    rec4, rows4, kernel4, kpiv4 = analyze_syzygy_space(
        ms, nb, 4, extract=(arm == "sem"), block_size=n)
    rec3.pop("extra_reps", None); rec3.pop("kernel_vectors", None)
    rec4.pop("extra_reps", None); rec4.pop("kernel_vectors", None)
    cell["D3"] = rec3
    cell["D4"] = rec4
    stage_times["d3d4_s"] = round(time.time() - t1, 2)
    print("  D3: def=%d extra=%d rankK=%d kernel=%d | D4: def=%d extra=%d "
          "rankK=%d kernel=%d (%.1fs)" % (
              rec3["deficit"], rec3["extra"], rec3["rankK"], rec3["kernel_dim"],
              rec4["deficit"], rec4["extra"], rec4["rankK"], rec4["kernel_dim"],
              stage_times["d3d4_s"]), flush=True)
    cell["stage_times"] = stage_times
    flush()

    # ---- D5 (extract=True on sem; count-only null)
    if softcap_hit():
        cell["status"] = "censored_softcap_before_D5"
        cell["stage_times"] = stage_times
        return cell
    t1 = time.time()
    rec5, rows5, kernel5, kpiv5 = analyze_syzygy_space(
        ms, nb, 5, extract=(arm == "sem"), block_size=n)
    rec5.pop("extra_reps", None); rec5.pop("kernel_vectors", None)
    cell["D5"] = rec5
    stage_times["d5_s"] = round(time.time() - t1, 2)
    print("  D5: nrows=%d rank=%d pred=%d deficit=%d kernel=%d rankK=%d "
          "extra=%d (%.1fs)" % (
              rec5["nrows"], rec5["rank"], rec5["sr_pred"], rec5["deficit"],
              rec5["kernel_dim"], rec5["rankK"], rec5["extra"],
              stage_times["d5_s"]), flush=True)
    cell["stage_times"] = stage_times
    flush()

    if arm == "null":
        # Null closure is empty iff all lower extras are 0; then residual_6
        # == extra_6 and the control requires extra_6 == 0. Check D3..D5
        # first, then the D6 count-only stage under the timer.
        low_ok = (rec3["extra"] == 0 and rec4["extra"] == 0 and rec5["extra"] == 0
                  and rec3["rank"] == rec3["sr_pred"]
                  and rec4["rank"] == rec4["sr_pred"]
                  and rec5["rank"] == rec5["sr_pred"])
        cell["null_lower_degrees_ok"] = bool(low_ok)
        if not low_ok:
            cell["status"] = "completed"
            cell["controls"] = {"c5_null_zero_d3d4d5": False}
            cell["stage_times"] = stage_times
            return cell
        if softcap_hit():
            cell["status"] = "censored_softcap_before_D6"
            cell["stage_times"] = stage_times
            return cell
        t1 = time.time()
        budget_left = args.soft_cap - (time.time() - t_start)
        try:
            stage_timer(budget_left)
            rec6, rows6, _, kpiv6 = analyze_syzygy_space(
                ms, nb, 6, extract=False, block_size=n)
            cancel_timer()
        except StageTimeout:
            cancel_timer()
            cell["status"] = "censored_timeout_D6_classification"
            cell["stage_times"] = stage_times
            cell["d6_elapsed_before_timeout_s"] = round(time.time() - t1, 2)
            return cell
        rec6.pop("extra_reps", None)
        cell["D6"] = rec6
        stage_times["d6_s"] = round(time.time() - t1, 2)
        del rows6, kpiv6
        gc.collect()
        c6ok = (rec6["extra"] == 0 and rec6["rank"] == rec6["sr_pred"])
        cell["link_D6"] = {"closure_rank_A5": 0, "extra_6": rec6["extra"],
                           "residual_6": int(rec6["extra"]),
                           "note": "null arm: lower-degree extras all 0 -> "
                                   "closure empty; residual_6 == extra_6"}
        cell["controls"] = {
            "c5_null_zero_d3d4d5": True,
            "c5_null_zero_d6_extra_and_rank": bool(c6ok),
            "c5_null_residual6_zero": bool(rec6["extra"] == 0),
        }
        cell["stage_times"] = stage_times
        print("  D6 null: nrows=%d rank=%d pred=%d deficit=%d extra=%d -> %s "
              "(%.1fs)" % (rec6["nrows"], rec6["rank"], rec6["sr_pred"],
                           rec6["deficit"], rec6["extra"],
                           "ok" if c6ok else "FAIL", stage_times["d6_s"]),
              flush=True)
        return cell

    # ================= sem arm =================
    # ---- residual_4 canonical (both reductions recorded)
    t1 = time.time()
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
    red_new = [full_reduce(v, kpiv4) for v in v3_mults]
    red_new = [r for r in red_new if r]
    rank_new4, _ = vec_echelon(red_new)
    residual4 = int(rec4["extra"] - rank_new4)
    cell["residual_4_canonical"] = residual4
    stage_times["residual4_s"] = round(time.time() - t1, 2)

    # ---- D5 closure continuity (C9, cheap): A3_5 / A4_5 / residual_5 from
    # the EXTRA bases (rank-identical to EXP-SIG-003's full-kernel images)
    t1 = time.time()
    B3, rB3 = quotient_basis(kernel3, kpiv3)
    B4, rB4 = quotient_basis(kernel4, kpiv4)
    B5, rB5 = quotient_basis(kernel5, kpiv5)
    tag2idx5 = {tag: ix for ix, (tag, _) in enumerate(rows5)}
    m1 = multiplier_sets(nb, 1)
    m2 = multiplier_sets(nb, 2)
    v3_imgs5, miss3_5 = images_of(B3, rows3, tag2idx5, m2)
    v4_imgs5, miss4_5 = images_of(B4, rows4, tag2idx5, m1)
    A3_5, _ = rank_reduced(v3_imgs5, kpiv5)
    A4_5, _ = rank_reduced(v4_imgs5, kpiv5)
    # A4_5 from extras only == A4 from full kernel4 (K4 images lie in K5);
    # A3_5's span is inside A4_5's (D3 mults land in ker M4), so
    # rank(F3 u F4) == A4_5 as in EXP-SIG-003.
    residual5 = int(rec5["extra"] - A4_5)
    cell["d5_closure_continuity"] = {
        "B3": rB3, "B4": rB4, "B5": rB5,
        "A3_5": int(A3_5), "A4_5": int(A4_5), "residual_5": residual5,
        "miss3": miss3_5, "miss4": miss4_5,
    }
    stage_times["d5_continuity_s"] = round(time.time() - t1, 2)
    cell["stage_times"] = stage_times
    flush()
    print("  continuity: B3=%d B4=%d B5=%d | A3_5=%d A4_5=%d residual_5=%d "
          "residual_4=%d (%.1fs)" % (rB3, rB4, rB5, A3_5, A4_5, residual5,
                                     residual4, stage_times["d5_continuity_s"]),
          flush=True)

    anch = SIG3_ANCHORS.get((n, seed))
    if anch is not None:
        c9 = (rec3["deficit"] == anch["d3_deficit"] and rec3["extra"] == anch["d3_extra"]
              and rec4["deficit"] == anch["d4_deficit"] and rec4["extra"] == anch["d4_extra"]
              and residual4 == anch["residual4_canonical"]
              and rec5["rank"] == anch["d5_rank"] and rec5["deficit"] == anch["d5_deficit"]
              and rec5["extra"] == anch["d5_extra"]
              and A3_5 == anch["A3_5"] and A4_5 == anch["A4_5"]
              and residual5 == anch["residual_5"])
        cell["c9_continuity_anchors"] = {"expected": anch, "pass": bool(c9)}
        flush()
        if not c9:
            halt(4, "C9 continuity-anchor mismatch vs EXP-SIG-003 at n=%d "
                    "seed=%d (instrument drift, not evidence)" % (n, seed),
                 cell={"n": n, "seed": seed, "arm": arm})

    # ---- D6 count-only classification (the expensive stage, timed)
    if softcap_hit():
        cell["status"] = "censored_softcap_before_D6"
        cell["stage_times"] = stage_times
        return cell
    t1 = time.time()
    budget_left = args.soft_cap - (time.time() - t_start)
    try:
        stage_timer(budget_left)
        rec6, rows6, _, kpiv6 = analyze_syzygy_space(ms, nb, 6,
                                                     extract=False, block_size=n)
        cancel_timer()
    except StageTimeout:
        cancel_timer()
        cell["status"] = "censored_timeout_D6_classification"
        cell["stage_times"] = stage_times
        cell["d6_elapsed_before_timeout_s"] = round(time.time() - t1, 2)
        return cell
    rec6.pop("extra_reps", None)
    cell["D6"] = rec6
    stage_times["d6_s"] = round(time.time() - t1, 2)
    print("  D6: nrows=%d ncols=%d rank=%d pred=%d deficit=%d kernel=%d "
          "rankK=%d extra=%d (%.1fs)" % (
              rec6["nrows"], rec6["ncols"], rec6["rank"], rec6["sr_pred"],
              rec6["deficit"], rec6["kernel_dim"], rec6["rankK"],
              rec6["extra"], stage_times["d6_s"]), flush=True)
    cell["stage_times"] = stage_times
    flush()
    tag2idx6 = {tag: ix for ix, (tag, _) in enumerate(rows6)}
    del rows6
    gc.collect()

    # ---- closure images at D6
    if softcap_hit():
        cell["status"] = "censored_softcap_before_closure"
        cell["stage_times"] = stage_times
        return cell
    t1 = time.time()
    m3 = multiplier_sets(nb, 3)
    F3, miss3 = images_of(B3, rows3, tag2idx6, m3)
    F4, miss4 = images_of(B4, rows4, tag2idx6, m2)
    F5, miss5 = images_of(B5, rows5, tag2idx6, m1)
    stage_times["images_s"] = round(time.time() - t1, 2)
    cell["stage_times"] = stage_times
    cell["image_counts"] = {"F3": len(F3), "F4": len(F4), "F5": len(F5),
                            "miss3": miss3, "miss4": miss4, "miss5": miss5}
    flush()
    print("  images: F3=%d F4=%d F5=%d misses=%d/%d/%d (%.1fs)" % (
        len(F3), len(F4), len(F5), miss3, miss4, miss5,
        stage_times["images_s"]), flush=True)

    # ---- closure ranks, two exact ways + union cross-check (timed)
    t1 = time.time()
    budget_left = args.soft_cap - (time.time() - t_start)
    try:
        stage_timer(budget_left)
        # (i) incremental-merged: start from kpiv6, insert reduced remainders
        merged = dict(kpiv6)
        fam_cum = {}
        cum = 0
        for name, fam in (("F3", F3), ("F4", F4), ("F5", F5)):
            for v in fam:
                r = full_reduce(v, merged)
                if r:
                    lead = r.bit_length() - 1
                    merged[lead] = r
                    cum += 1
            fam_cum[name] = cum
        A3_6 = fam_cum["F3"]
        A4_6 = fam_cum["F4"]
        A5 = fam_cum["F5"]
        cancel_timer()
    except StageTimeout:
        cancel_timer()
        cell["status"] = "censored_timeout_closure_ranks"
        cell["stage_times"] = stage_times
        cell["closure_elapsed_before_timeout_s"] = round(time.time() - t1, 2)
        return cell
    stage_times["ranks_s"] = round(time.time() - t1, 2)

    t1 = time.time()
    budget_left = args.soft_cap - (time.time() - t_start)
    xchk = {"skipped": False}
    try:
        stage_timer(budget_left)
        # (ii) independent family ranks mod K6 (SIG-003 style)
        iA3, _ = rank_reduced(F3, kpiv6)
        iA4, _ = rank_reduced(F3 + F4, kpiv6)
        iA5, _ = rank_reduced(F3 + F4 + F5, kpiv6)
        # (iii) reduction-free union echelon cross-check
        rank_union, _ = vec_echelon(list(kpiv6.values()) + F3 + F4 + F5)
        union_check = int(rank_union - rec6["rankK"])
        xchk = {"skipped": False, "A3_6_indep": int(iA3), "A4_6_indep": int(iA4),
                "A5_indep": int(iA5), "union_crosscheck_A5": union_check}
        cancel_timer()
    except StageTimeout:
        cancel_timer()
        xchk = {"skipped": "censored_timeout_crosscheck"}
    stage_times["crosscheck_s"] = round(time.time() - t1, 2)

    residual6 = int(rec6["extra"] - A5)
    cell["link_D6"] = {
        "reduction_semantics": "canonical full_reduce (exact mod-K6 ranks)",
        "n_F3_imgs": len(F3), "n_F4_imgs": len(F4), "n_F5_imgs": len(F5),
        "miss3": miss3, "miss4": miss4, "miss5": miss5,
        "B3": rB3, "B4": rB4, "B5": rB5,
        "A3_6": int(A3_6), "A4_6": int(A4_6), "A5": int(A5),
        "extra_6": rec6["extra"], "deficit_6": rec6["deficit"],
        "rankK6": rec6["rankK"],
        "residual_6": residual6,
        "coverage_vs_deficit6": (A5 / rec6["deficit"]) if rec6["deficit"] else None,
        "crosscheck": xchk,
        "sanity": {
            "A3_le_A4_le_A5": bool(A3_6 <= A4_6 <= A5),
            "A5_le_extra6": bool(A5 <= rec6["extra"]),
            "no_missing_rows": bool(miss3 == 0 and miss4 == 0 and miss5 == 0),
            "residual6_nonneg": bool(residual6 >= 0),
        },
    }
    if not xchk.get("skipped"):
        cell["link_D6"]["sanity"].update({
            "c6_indep_eq_merged": bool(iA3 == A3_6 and iA4 == A4_6 and iA5 == A5),
            "c6_union_eq_merged": bool(union_check == A5),
        })
    cell["controls"] = {
        "c7_cascade_sanity_all": all(cell["link_D6"]["sanity"].values()),
        "c9_continuity_pass": (True if anch is None else
                               bool(cell["c9_continuity_anchors"]["pass"])),
        "c8_standard_instance": bool(standard),
    }
    cell["stage_times"] = stage_times
    print("  LINK D6: A3_6=%d A4_6=%d A5=%d | extra_6=%d deficit_6=%d "
          "residual_6=%d | xchk=%s (ranks %.1fs, xchk %.1fs)" % (
              A3_6, A4_6, A5, rec6["extra"], rec6["deficit"], residual6,
              xchk, stage_times["ranks_s"], stage_times["crosscheck_s"]),
          flush=True)
    if not cell["controls"]["c7_cascade_sanity_all"]:
        halt(5, "C7 cascade sanity failed (driver bug, not evidence)",
             cell={"n": n, "seed": seed, "arm": arm})
    return cell


# ==========================================================================
if args.mode == 'gate':
    print("=== EXP-SIG-005 GATE: C1 null residual, C2 injected, C3 T2 anchor, "
          "C4a in-run determinism + n=24 filter probe ===", flush=True)
    gate_checks = []
    if not instrument_ok:
        print("  INSTRUMENT sha256 MISMATCH vs pinned set: %s" % instrument_hashes,
              flush=True)
        out["cells"].append({"kind": "instrument_hash", "pass": False,
                             "hashes": instrument_hashes})
        out["gate"] = "FAIL"
        flush()
        sys.exit(1)
    out["cells"].append({"kind": "instrument_hash", "pass": True,
                         "hashes": instrument_hashes})
    flush()

    # ---- C1: support-matched null must have residual 0 under BOTH reductions
    for n in (9, 12):
        c = measure_p1_cell(n, 1, "null")
        c["kind"] = "C1_null_residual"
        v3 = c["v3_multiples_at_D4"]
        cond = (c["D3"]["extra"] == 0 and c["D4"]["extra"] == 0
                and c["D3"]["rank"] == c["D3"]["sr_pred"]
                and c["D4"]["rank"] == c["D4"]["sr_pred"]
                and v3["residual_pinned"] == 0 and v3["residual_canonical"] == 0
                and c["controls"]["c6_union_crosscheck_eq_canonical"])
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
    inj[c0] = null_ms[q0] ^^ null_ms[q1]
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
                         "rec": {k: v for k, v in rec.items()
                                 if k != "kernel_vectors"},
                         "detected": det, "detected_rep": det_rep,
                         "pass": bool(cond)})
    gate_checks.append(cond)
    flush()

    # ---- C3: T2 anchor continuity at n=15 seed 1 (EXP-SIG-001/002/004 certified)
    c = measure_p1_cell(15, 1, "sem")
    c["kind"] = "C3_t2_anchor"
    v3 = c["v3_multiples_at_D4"]
    cond = (c["D3"]["deficit"] == 1 and c["D3"]["extra"] == 1
            and c["D4"]["deficit"] == 40 and c["D4"]["extra"] == 40
            and v3["residual_pinned"] == 10
            and v3["residual_canonical"] == 11
            and c["controls"]["c6_union_crosscheck_eq_canonical"])
    c["pass"] = bool(cond)
    gate_checks.append(cond)
    print("  C3 T2 anchor n=15 s1: D3 def=%d D4 def=%d residual pinned=%d canonical=%d -> %s (%.1fs)" % (
        c["D3"]["deficit"], c["D4"]["deficit"], v3["residual_pinned"],
        v3["residual_canonical"], "ok" if cond else "FAIL", c["wall_s"]), flush=True)
    out["cells"].append(c)
    flush()

    # ---- C4a: in-run determinism — n=15 seed 3 sem computed twice
    c1 = measure_p1_cell(15, 3, "sem")
    c2 = measure_p1_cell(15, 3, "sem")
    same = (json.dumps(jsonsafe(strip_timing(c1)), sort_keys=True)
            == json.dumps(jsonsafe(strip_timing(c2)), sort_keys=True))
    out["cells"].append({"kind": "C4a_rerun_check", "n": 15, "seed": 3, "arm": "sem",
                         "comparison": "all fields except sec/wall_s",
                         "identical": bool(same)})
    print("  [C4a in-run determinism n=15 seed=3 sem] identical (modulo timing): %s" % same, flush=True)
    gate_checks.append(same)
    flush()

    # ---- n=24 filter probe (build-only; picks the P1 standard seed set)
    probe = []
    for seed in (1, 2, 3, 4, 5, 6):
        if softcap_hit():
            probe.append({"n": 24, "seed": seed, "status": "not_run: soft cap"})
            continue
        t0 = time.time()
        monosets, nb, meta = build_boolean_semaev(24, 3, seed)
        if monosets is None:
            probe.append({"n": 24, "seed": seed,
                          "status": "skipped: no decomposable R", "meta": meta})
            continue
        rx_zero = str(meta.get("R_x", "")).strip() == "0"
        has_lin = int(meta.get("eq_degs_hist", {}).get("1", 0)) > 0
        probe.append({"n": 24, "seed": seed, "status": "built",
                      "nb": int(nb), "meta": meta,
                      "filter": {"rx_zero": bool(rx_zero),
                                 "has_linear_eq": bool(has_lin),
                                 "standard": bool((not rx_zero) and (not has_lin))},
                      "build_s": round(time.time() - t0, 2)})
        print("  probe n=24 seed=%d: standard=%s hist=%s (%.1fs)" % (
            seed, probe[-1]["filter"]["standard"], meta.get("eq_degs_hist"),
            probe[-1]["build_s"]), flush=True)
        flush()
    out["cells"].append({"kind": "n24_filter_probe", "probe": probe})
    flush()

    out["gate"] = "PASS" if all(gate_checks) else "FAIL"
    print("=== GATE: %s ===" % out["gate"], flush=True)

# ==========================================================================
elif args.mode == 'p1':
    tokens = []
    for tok in args.cells.split(','):
        tok = tok.strip()
        if not tok:
            continue
        nn, ss, aa = tok.split(':')
        tokens.append((int(nn), int(ss), aa))
    print("=== EXP-SIG-005 P1 cells: %d cells: %s ===" % (len(tokens), tokens), flush=True)
    control_failures = []
    for (nn, ss, aa) in tokens:
        if softcap_hit():
            out["cells"].append({"n": nn, "seed": ss, "arm": aa,
                                 "status": "not_run: soft budget cap"})
            flush()
            continue
        cell = measure_p1_cell(nn, ss, aa)
        out["cells"].append(cell)
        if cell.get("status") != "completed":
            print("  [n=%d seed=%d %s] %s" % (nn, ss, aa, cell.get("status")), flush=True)
            flush()
            continue
        v3 = cell["v3_multiples_at_D4"]
        ctl = cell["controls"]
        standard = cell["filter"]["standard"]
        fail = [k for k, v in ctl.items()
                if isinstance(v, bool) and v is False]
        if fail:
            control_failures.append({"n": nn, "seed": ss, "arm": aa, "failed": fail})
        print("  [n=%d seed=%d %s]%s D3: def=%d extra=%d | D4: def=%d extra=%d rankK=%d | "
              "imgs=%d rank_old=%d rank_new=%d union=%d | residual old=%d new=%d (delta %+d)%s (%.1fs)" % (
                  nn, ss, aa, "" if standard else " [FILTERED]",
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

# ==========================================================================
elif args.mode == 'p2':
    print("=== EXP-SIG-005 P2 D6 closure cell: n=%d seed=%d arm=%s ==="
          % (args.n, args.seed, args.arm), flush=True)
    cell = measure_p2_cell(args.n, args.seed, args.arm)
    if cell not in out["cells"]:
        out["cells"].append(cell)
    flush()

out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
