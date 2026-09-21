# EXP-SIG-007 driver — n=21 residual_5 attempt, memory-safe staged instrument
# (H-SIG-001; handoff TASK-20260724-SIGN21).
#
# Reuses the EXP-SIG-001..005 instrument BIT-IDENTICALLY
# (src/h013_f5_signatures.sage sha256
# 1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087).
# The pinned instrument is loaded, never modified. full_reduce /
# multiplier_sets / images_of / quotient_basis copied VERBATIM from
# EXP-SIG-005 SIG5_run.sage (canonical, rank-exact).
#
# STAGING (no tracked Python-int echelon at D5 — that is what OOM'd
# EXP-SIG-005 RUN-n):
#   S0  build + filter + D3/D4 (extract) + residual_4 (canonical+pinned)
#       + quotient bases B3/B4 + matched null D3/D4 control  [cheap]
#   S1  D5 tagged rows + colidx (nrows/ncols record), K5 family vectors,
#       closure images F3/F4 — all stored as compact POSITION LISTS;
#       column adjacency pickle for the staircase engine            [heavy]
#   S2  exact ranks via the REDUCTION-FREE UNION method on dense m4ri:
#       rankK5 = rank(K5); A3_5 = rank(K5 u F3) - rankK5;
#       A4_5 = rank(K5 u F3 u F4) - rankK5. (The C6 union identity —
#       verified against canonical full_reduce on every EXP-SIG-003/005
#       cell — used as the primary method here.)                    [heavy]
#   S3  rank(M5) via checkpointed block-staircase m4ri (algorithm of
#       src/h012c_block_m4ri.py — reference copy in src/ — re-driven over
#       the SIG instrument's own systems/rows). Resumable across
#       invocations; sha256-pinned carries. Then
#       extra_5 = (nrows - rank) - rankK5; residual_5 = extra_5 - A4_5.
#
# Modes:
#   gate      C1 null residual (n=9,12, D3/D4, both reductions), C2
#             injected syzygy, C3 T2 anchor n=15 s1, C4a in-run determinism.
#   anchor    C9a staged-path anchors (--cells 12:2,15:1[,18:1]) +
#             C9b staircase validation at n=12 seed 2 (two chunk sizes +
#             resume) when --staircase-validate 1.
#   cell      n=21 sem stages S0/S1/S2 for --seed, checkpointed in --work.
#   rank5     S3 staircase continuation for --seed (loads cell adjacency).
#
# Kill rule: --soft-cap (default 235 s) checked before every stage/chunk;
# every stage checkpoints to disk before the cap can fire.
#
# Usage (from repo root):
#   sage experiments/EXP-SIG-007/SIG7_run.sage --mode gate \
#        --out experiments/EXP-SIG-007/runs/RUN-EXP-SIG-007-a/raw.json
#   sage ... --mode anchor --cells 12:2,15:1 --staircase-validate 1 --out ...
#   sage ... --mode anchor --cells 18:1 --out ...
#   sage ... --mode cell --n 21 --seed 1 --work experiments/EXP-SIG-007/work/n21_s1 --out ...
#   sage ... --mode rank5 --n 21 --seed 1 --work experiments/EXP-SIG-007/work/n21_s1 \
#        --budget 230 --out ...

import sys, os, time, json, argparse, platform, datetime, itertools, hashlib
import pickle, gc
from array import array
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--mode', required=True, choices=['gate', 'anchor', 'cell', 'rank5'])
p.add_argument('--out', required=True)
p.add_argument('--work', default='', help='checkpoint dir (cell/rank5 modes)')
p.add_argument('--cells', default='', help='anchor: comma list of n:seed (sem)')
p.add_argument('--staircase-validate', type=int, default=0)
p.add_argument('--n', type=int, default=21)
p.add_argument('--seed', type=int, default=1)
p.add_argument('--budget', type=float, default=230.0,
               help='rank5: stop starting new chunks after this many seconds')
p.add_argument('--soft-cap', type=int, default=235,
               help='do not start a new stage after this many seconds')
p.add_argument('--max-units', type=int, default=0)
p.add_argument('--chunk-force', type=int, default=0)
p.add_argument('--fresh', type=int, default=0,
               help='cell: ignore existing stage state (determinism rerun)')
args = p.parse_args()

EXPDIR = Path(args.out).resolve().parents[2]
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
from sage.all import GF, matrix, set_random_seed
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

F2 = GF(2)
t_start = time.time()
started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()


def fsafe(o):
    """JSON-safe conversion that also handles sage Integer/RealNumber/Rational
    (the .sage preparser coerces numeric literals)."""
    if isinstance(o, dict):
        return {str(k): fsafe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [fsafe(v) for v in o]
    if isinstance(o, bool) or o is None or isinstance(o, (int, float, str)):
        return o
    try:
        from sage.rings.integer import Integer as _SageInteger
        if isinstance(o, _SageInteger):
            return int(o)
    except Exception:
        pass
    try:
        from sage.rings.rational import Rational as _SageRational
        from sage.rings.real_mpfr import RealNumber as _SageReal
        if isinstance(o, (_SageRational, _SageReal)):
            return float(o)
    except Exception:
        pass
    try:
        return int(o)
    except Exception:
        try:
            return float(o)
        except Exception:
            return str(o)


def sha256(pth):
    return hashlib.sha256(Path(pth).read_bytes()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


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
instrument_hashes = {f.name: sha256(f) for f in sorted((EXPDIR / 'src').iterdir())
                     if f.name in PINNED_HASHES}
instrument_ok = all(instrument_hashes.get(k) == v for k, v in PINNED_HASHES.items())

out = {
    "experiment": "EXP-SIG-007",
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
        json.dump(fsafe(out), fh, indent=1)


def softcap_hit():
    return (time.time() - t_start) > args.soft_cap


def log(msg):
    print("[sig7 %s] %s" % (time.strftime('%H:%M:%S'), msg), flush=True)


def halt(code, reason, cell=None):
    if cell is not None and cell not in out["cells"]:
        out["cells"].append(cell)
    out["halt"] = {"reason": reason,
                   "at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out["wall_seconds"] = round(time.time() - t_start, 2)
    flush()
    print("HALT: %s" % reason, flush=True)
    sys.exit(code)


# ==========================================================================
# verbatim EXP-SIG-005 helpers (canonical semantics)
# ==========================================================================
def full_reduce(v, piv):
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
    """Verbatim EXP-SIG-003 construction (bitmask images over target rows)."""
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
    red = [full_reduce(kv, kpiv) for kv in kernel]
    red = [r for r in red if r]
    r, pr = vec_echelon(red)
    return list(pr.values()), r


def strip_timing(o):
    if isinstance(o, dict):
        return {k: strip_timing(v) for k, v in o.items()
                if k not in ("sec", "wall_s", "wall_seconds", "elapsed_s_so_far")}
    if isinstance(o, list):
        return [strip_timing(v) for v in o]
    return o


# ==========================================================================
# staged-path helpers (new, memory-safe)
# ==========================================================================
def positions_list(bitmask_vecs):
    """bitmask ints -> list of sorted position lists (compact storage)."""
    return [array("I", bits_to_positions(v)) for v in bitmask_vecs]


def m4ri_from_positions(pos_lists, ncols):
    M = matrix(F2, len(pos_lists), ncols)
    for i, pl in enumerate(pos_lists):
        for j in pl:
            M[i, j] = 1
    return M


def union_ranks(k5_pos, f3_pos, f4_pos, nrows_target):
    """Reduction-free exact closure ranks (C6 union method as primary):
    rankK5 = rank(K5); A3_5 = rank(K5 u F3)-rankK5;
    A4_5 = rank(K5 u F3 u F4)-rankK5. Dense m4ri; staged so each
    echelon reuses the previous rref basis rows."""
    tm = {}
    t0 = time.time()
    M = m4ri_from_positions(k5_pos, nrows_target)
    M.echelonize()
    rankK5 = int(M.rank())
    tm["ech_k5"] = round(time.time() - t0, 2)
    # keep only the nonzero rref rows as the carried basis
    t0 = time.time()
    base = M.matrix_from_rows(list(range(rankK5)))
    del M
    gc.collect()
    B = m4ri_from_positions(f3_pos, nrows_target)
    C = base.stack(B)
    del B
    gc.collect()
    C.echelonize()
    rank_f3 = int(C.rank())
    A3_5 = rank_f3 - rankK5
    tm["ech_f3"] = round(time.time() - t0, 2)
    t0 = time.time()
    base = C.matrix_from_rows(list(range(rank_f3)))
    del C
    gc.collect()
    B = m4ri_from_positions(f4_pos, nrows_target)
    C = base.stack(B)
    del B
    gc.collect()
    C.echelonize()
    rank_f4 = int(C.rank())
    A4_5 = rank_f4 - rankK5
    tm["ech_f4"] = round(time.time() - t0, 2)
    del C
    gc.collect()
    return rankK5, A3_5, A4_5, tm


def monosets_hash(monosets):
    """Identity binding (copied from src/h012c_block_m4ri.py)."""
    h = hashlib.sha256()
    for f in monosets:
        encoded = sorted(tuple(sorted(int(v) for v in m)) for m in f)
        h.update(len(encoded).to_bytes(8, "big"))
        for mono in encoded:
            h.update(len(mono).to_bytes(4, "big"))
            for v in mono:
                h.update(v.to_bytes(4, "big"))
    return h.hexdigest()


def build_d5_stage1(monosets, nb, rows3, B3, rows4, B4):
    """S1 core: D5 rows + K5 + images + adjacency. Returns dict of compact
    payloads (position lists) + adjacency col_rows + counts."""
    rows5, colidx5 = tagged_macaulay(monosets, nb, 5)
    nrows5 = len(rows5)
    ncols5 = len(colidx5)
    tag2idx5 = {tag: ix for ix, (tag, _) in enumerate(rows5)}
    # K5 family (Koszul + principal + vanishing-multiple units)
    kvecs = koszul_principal_vectors(monosets, nb, 5, tag2idx5)
    n_vanish = 0
    for ix, (tag, prod) in enumerate(rows5):
        if not prod:
            kvecs.append(int(1 << ix))
            n_vanish += 1
    k5_pos = positions_list(kvecs)
    del kvecs
    gc.collect()
    # closure images (verbatim EXP-SIG-003/005 construction)
    m1 = multiplier_sets(nb, 1)
    m2 = multiplier_sets(nb, 2)
    f3_imgs, miss3 = images_of(B3, rows3, tag2idx5, m2)
    f4_imgs, miss4 = images_of(B4, rows4, tag2idx5, m1)
    f3_pos = positions_list(f3_imgs)
    f4_pos = positions_list(f4_imgs)
    del f3_imgs, f4_imgs
    gc.collect()
    # column adjacency for the staircase engine
    col_rows = [array("I") for _ in range(ncols5)]
    for ri, (tag, prod) in enumerate(rows5):
        for m in prod:
            col_rows[colidx5[m]].append(ri)
    return {
        "nrows5": nrows5, "ncols5": ncols5, "n_vanish": n_vanish,
        "k5_pos": k5_pos, "f3_pos": f3_pos, "f4_pos": f4_pos,
        "miss3": miss3, "miss4": miss4, "col_rows": col_rows,
    }


# ==========================================================================
# block-staircase rank engine (algorithm of src/h012c_block_m4ri.py)
# ==========================================================================
def process_subchunk(col_rows, j0, j1, nrows, carries):
    """Copied algorithmically from h012c_block_m4ri.process_subchunk."""
    c = j1 - j0
    tm = {}
    t0 = time.time()
    A = matrix(F2, c, nrows)
    for jj in range(c):
        for r in col_rows[j0 + jj]:
            A[jj, r] = 1
    tm["fill"] = time.time() - t0
    t0 = time.time()
    B = A.transpose()
    del A
    gc.collect()
    tm["tr1"] = time.time() - t0
    t0 = time.time()
    for (P, H) in carries:
        Y = B.matrix_from_rows(P)
        B += H * Y
        del Y
    tm["reduce"] = time.time() - t0
    t0 = time.time()
    Bc = B.transpose()
    del B
    gc.collect()
    Bc.echelonize()
    tm["ech"] = time.time() - t0
    t0 = time.time()
    r = int(Bc.rank())
    P_new = []
    rows_keep = []
    for i in range(r):
        nz = Bc.row(i).nonzero_positions()
        if nz:
            P_new.append(int(nz[0]))
            rows_keep.append(i)
    k = len(P_new)
    H_new = None
    if k:
        H_new = Bc.matrix_from_rows(rows_keep).transpose()
        import random as _r
        rr = _r.Random(int(1))  # int(): sage preparser would pass Integer
        for _ in range(min(256, k * k)):
            i, j = rr.randrange(k), rr.randrange(k)
            assert int(H_new[P_new[j], i]) == (1 if i == j else 0), "NOT RREF"
    del Bc
    gc.collect()
    tm["post"] = time.time() - t0
    tm["c"] = c
    return k, P_new, H_new, tm


def save_carry(d, idx, P, H):
    nrows, k = H.dimensions()
    blk = max(1000, int(1.9e9) // nrows)
    entries = []
    for b0 in range(0, k, blk):
        b1 = min(k, b0 + blk)
        Hb = H.matrix_from_columns(list(range(b0, b1)))
        fn = "carry_%03d_%03d.pkl" % (idx, b0 // blk)
        tmp = d / (fn + ".tmp")
        final = d / fn
        with open(tmp, "wb") as f:
            pickle.dump((P[b0:b1], Hb), f, protocol=4)
        os.replace(tmp, final)
        entries.append({"file": fn, "npiv": b1 - b0, "sha256": file_hash(final)})
        del Hb
        gc.collect()
    return entries


def load_carries(d, st):
    outc = []
    for c in st["carries"]:
        pth = d / c["file"]
        if file_hash(pth) != c["sha256"]:
            raise RuntimeError("checkpoint hash mismatch: %s" % pth)
        with open(pth, "rb") as f:
            P_block, H_block = pickle.load(f)
        outc.append((P_block, H_block))
    return outc


def staircase_run(col_rows, nrows, ncols, workdir, budget, max_units=0,
                  chunk_force=0, tag="rank5"):
    """Resumable block-staircase rank. Returns final state dict."""
    d = Path(workdir)
    d.mkdir(parents=True, exist_ok=True)
    sp = d / "state.json"
    if sp.exists():
        with open(sp) as f:
            st = json.load(f)
        assert st["nrows"] == nrows and st["ncols"] == ncols, "state identity mismatch"
    else:
        st = {"tag": tag, "nrows": nrows, "ncols": ncols, "next_col": 0,
              "rank_acc": 0, "carries": [], "done": False,
              "rate_mat": 2.0e12, "secs_total": 0.0, "units": []}
    carries = load_carries(d, st)
    t0 = time.time()
    units = 0
    while st["next_col"] < st["ncols"]:
        if units > 0 and (time.time() - t0) > budget:
            break
        if max_units and units >= max_units:
            break
        rank = max(st["rank_acc"], 2000)
        c = int(110.0 * st["rate_mat"] / (st["nrows"] * rank * 0.7))
        c = max(4000, min(24000, c, st["ncols"] - st["next_col"]))
        if chunk_force:
            c = min(chunk_force, st["ncols"] - st["next_col"])
        j0, j1 = st["next_col"], st["next_col"] + c
        k, P_new, H_new, tm = process_subchunk(col_rows, j0, j1, st["nrows"],
                                               carries)
        unit_secs = sum(tm[k2] for k2 in ("fill", "tr1", "reduce", "ech", "post"))
        if st["rank_acc"] > 0 and tm["reduce"] > 1.0:
            meas = st["nrows"] * st["rank_acc"] * tm["c"] * 0.7 / tm["reduce"]
            st["rate_mat"] = 0.5 * st["rate_mat"] + 0.5 * meas
        if k:
            entries = save_carry(d, len(st["carries"]), P_new, H_new)
            carries.append((P_new, H_new))
            st["carries"].extend(entries)
            del H_new
        st["rank_acc"] += k
        st["next_col"] = j1
        st["secs_total"] += unit_secs
        st["units"].append({"j0": j0, "j1": j1, "k": k,
                            "rank_acc": st["rank_acc"],
                            "tm": {k2: round(v, 2) for k2, v in tm.items()}})
        with open(d / "state.tmp", "w") as f:
            json.dump(fsafe(st), f)
        os.replace(d / "state.tmp", sp)
        units += 1
        log("staircase cols %d..%d k=%d rank=%d fill=%.1f red=%.1f ech=%.1f" % (
            j0, j1, k, st["rank_acc"], tm["fill"], tm["reduce"], tm["ech"]))
        gc.collect()
    if st["next_col"] >= st["ncols"]:
        st["done"] = True
        with open(d / "state.tmp", "w") as f:
            json.dump(fsafe(st), f)
        os.replace(d / "state.tmp", sp)
    st["secs_total"] = round(st["secs_total"], 1)
    return st


# ==========================================================================
# small cells: full staged closure measurement (anchors)
# ==========================================================================
CLOSURE_ANCHORS = {  # EV-SIG-003 / EV-SIG-005 receipt values (canonical method)
    (12, 2): {"rank5": 28097, "extra_5": 1322, "rankK5": 2093,
              "A3_5": 242, "A4_5": 444, "residual_5": 878, "B3": 1, "B4": 32},
    (15, 1): {"rank5": 69073, "extra_5": 1863, "rankK5": 3944,
              "A3_5": 392, "A4_5": 705, "residual_5": 1158, "B3": 1, "B4": 40},
    (18, 1): {"rank5": 143882, "extra_5": 2000, "rankK5": 6650,
              "A3_5": 578, "A4_5": 1026, "residual_5": 974, "B3": 1, "B4": 48},
}


def measure_anchor_cell(n, seed):
    t0 = time.time()
    stage_times = {}
    monosets, nb, meta = build_boolean_semaev(n, 3, seed)
    if monosets is None:
        return {"n": n, "seed": seed, "status": "skipped: no decomposable R",
                    "meta": meta}
    rx_zero = str(meta.get("R_x", "")).strip() == "0"
    has_lin = int(meta.get("eq_degs_hist", {}).get("1", 0)) > 0
    cell = {"n": n, "seed": seed, "arm": "sem", "nb": int(nb), "meta": meta,
            "filter": {"rx_zero": bool(rx_zero), "has_linear_eq": bool(has_lin),
                       "standard": bool((not rx_zero) and (not has_lin))},
            "status": "completed"}
    stage_times["build_s"] = round(time.time() - t0, 2)

    t1 = time.time()
    rec3, rows3, kernel3, kpiv3 = analyze_syzygy_space(monosets, nb, 3,
                                                       extract=True, block_size=n)
    rec4, rows4, kernel4, kpiv4 = analyze_syzygy_space(monosets, nb, 4,
                                                       extract=True, block_size=n)
    rec3.pop("extra_reps", None); rec3.pop("kernel_vectors", None)
    rec4.pop("extra_reps", None); rec4.pop("kernel_vectors", None)
    cell["D3"] = rec3
    cell["D4"] = rec4
    stage_times["d3d4_s"] = round(time.time() - t1, 2)
    B3, rB3 = quotient_basis(kernel3, kpiv3)
    B4, rB4 = quotient_basis(kernel4, kpiv4)
    cell["B3"] = rB3
    cell["B4"] = rB4
    log("anchor n=%d s=%d: D3 def=%d D4 def=%d B3=%d B4=%d (%.1fs)" % (
        n, seed, rec3["deficit"], rec4["deficit"], rB3, rB4,
        stage_times["d3d4_s"]))
    flush()
    if softcap_hit():
        cell["status"] = "censored_softcap_before_S1"
        cell["stage_times"] = stage_times
        return cell

    t1 = time.time()
    st1 = build_d5_stage1(monosets, nb, rows3, B3, rows4, B4)
    stage_times["s1_s"] = round(time.time() - t1, 2)
    cell["D5"] = {"D": 5, "nb": int(nb), "nrows": st1["nrows5"],
                  "ncols": st1["ncols5"], "n_vanish": st1["n_vanish"],
                  "n_k5_family": len(st1["k5_pos"]),
                  "n_F3": len(st1["f3_pos"]), "n_F4": len(st1["f4_pos"]),
                  "miss3": st1["miss3"], "miss4": st1["miss4"]}
    log("anchor n=%d s=%d: S1 nrows=%d ncols=%d K5=%d F3=%d F4=%d (%.1fs)" % (
        n, seed, st1["nrows5"], st1["ncols5"], len(st1["k5_pos"]),
        len(st1["f3_pos"]), len(st1["f4_pos"]), stage_times["s1_s"]))
    flush()
    if softcap_hit():
        cell["status"] = "censored_softcap_before_S2"
        cell["stage_times"] = stage_times
        return cell

    t1 = time.time()
    rankK5, A3_5, A4_5, tm = union_ranks(st1["k5_pos"], st1["f3_pos"],
                                         st1["f4_pos"], st1["nrows5"])
    stage_times["s2_s"] = round(time.time() - t1, 2)
    cell["closure"] = {"rankK5": int(rankK5), "A3_5": int(A3_5),
                       "A4_5": int(A4_5), "m4ri_times": tm,
                       "method": "reduction-free union rank (dense m4ri): "
                                 "rank(K5 u F)-rank(K5)"}
    anch = CLOSURE_ANCHORS.get((n, seed))
    if anch is not None:
        c9a = (rankK5 == anch["rankK5"] and A3_5 == anch["A3_5"]
               and A4_5 == anch["A4_5"] and rB3 == anch["B3"]
               and rB4 == anch["B4"])
        cell["c9a_anchor"] = {"expected": anch, "pass": bool(c9a),
                              "residual_5_implied": int(anch["extra_5"] - A4_5)}
    else:
        c9a = None
    cell["stage_times"] = stage_times
    log("anchor n=%d s=%d: rankK5=%d A3_5=%d A4_5=%d c9a=%s (%.1fs)" % (
        n, seed, rankK5, A3_5, A4_5, c9a, stage_times["s2_s"]))
    del st1
    gc.collect()

    # ---- C9b: staircase engine validation at n=12 seed 2 (two chunk sizes)
    if args.staircase_validate and (n, seed) == (12, 2):
        for chunk, label in ((4000, "c4000_resume"), (12000, "c12000")):
            if softcap_hit():
                cell.setdefault("staircase_validation", {})[label] = \
                    "censored_softcap"
                continue
            t1 = time.time()
            rows5, colidx5 = tagged_macaulay(monosets, nb, 5)
            nrows5, ncols5 = len(rows5), len(colidx5)
            col_rows = [array("I") for _ in range(ncols5)]
            for ri, (tag, prod) in enumerate(rows5):
                for m in prod:
                    col_rows[colidx5[m]].append(ri)
            del rows5
            gc.collect()
            wd = Path(args.work) / ("val_n%d_s%d_%s" % (n, seed, label)) \
                if args.work else Path("/tmp") / ("sig7_val_%s" % label)
            if label == "c4000_resume":
                # run 2 units, then resume in-process to completion:
                # exercises the checkpoint/resume identity path
                st_pre = staircase_run(col_rows, nrows5, ncols5, wd,
                                       budget=1e9, max_units=2,
                                       chunk_force=chunk, tag=label)
                st = staircase_run(col_rows, nrows5, ncols5, wd,
                                   budget=1e9, chunk_force=chunk, tag=label)
                resumed = True
            else:
                st = staircase_run(col_rows, nrows5, ncols5, wd,
                                   budget=1e9, chunk_force=chunk, tag=label)
                resumed = False
            ok = bool(st["done"] and st["rank_acc"] == CLOSURE_ANCHORS[(n, seed)]["rank5"])
            cell.setdefault("staircase_validation", {})[label] = {
                "rank": st["rank_acc"], "expected": CLOSURE_ANCHORS[(n, seed)]["rank5"],
                "done": st["done"], "resumed_mid_run": resumed,
                "chunk_force": chunk, "n_units": len(st["units"]),
                "secs_total": st["secs_total"], "pass": ok}
            log("staircase-validation %s: rank=%d pass=%s (%.1fs)" % (
                label, st["rank_acc"], ok, time.time() - t1))
            del col_rows
            gc.collect()
            flush()
    cell["stage_times"] = stage_times
    cell["wall_s"] = round(time.time() - t0, 2)
    return cell


# ==========================================================================
# n=21 cell: staged, checkpointed
# ==========================================================================
def cell_state_path():
    return Path(args.work) / "cell_state.json"


def load_cell_state():
    sp = cell_state_path()
    if sp.exists() and not args.fresh:
        with open(sp) as f:
            return json.load(f)
    return {"n": args.n, "seed": args.seed, "arm": "sem", "stages": {}}


def save_cell_state(st):
    sp = cell_state_path()
    sp.parent.mkdir(parents=True, exist_ok=True)
    with open(sp.with_suffix(".tmp"), "w") as f:
        json.dump(fsafe(st), f, indent=1)
    os.replace(sp.with_suffix(".tmp"), sp)


def run_cell():
    n, seed = args.n, args.seed
    st = load_cell_state()
    assert st["n"] == n and st["seed"] == seed, "cell state identity mismatch"
    stages = st["stages"]

    # ---------------- S0 ----------------
    if "S0" not in stages:
        t0 = time.time()
        monosets, nb, meta = build_boolean_semaev(n, 3, seed)
        if monosets is None:
            st["status"] = "skipped: no decomposable R"
            save_cell_state(st)
            out["cells"].append(st)
            return
        rx_zero = str(meta.get("R_x", "")).strip() == "0"
        has_lin = int(meta.get("eq_degs_hist", {}).get("1", 0)) > 0
        standard = bool((not rx_zero) and (not has_lin))
        rec3, rows3, kernel3, kpiv3 = analyze_syzygy_space(
            monosets, nb, 3, extract=True, block_size=n)
        rec4, rows4, kernel4, kpiv4 = analyze_syzygy_space(
            monosets, nb, 4, extract=True, block_size=n)
        rec3.pop("extra_reps", None); rec3.pop("kernel_vectors", None)
        rec4.pop("extra_reps", None); rec4.pop("kernel_vectors", None)
        # residual_4 canonical + pinned (verbatim EXP-SIG-004/005)
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
        red_old = [reduce_against(v, kpiv4) for v in v3_mults]
        red_old = [r for r in red_old if r]
        rank_old, _ = vec_echelon(red_old)
        red_new = [full_reduce(v, kpiv4) for v in v3_mults]
        red_new = [r for r in red_new if r]
        rank_new, _ = vec_echelon(red_new)
        B3, rB3 = quotient_basis(kernel3, kpiv3)
        B4, rB4 = quotient_basis(kernel4, kpiv4)
        # matched null D3/D4 control (cheap)
        rng = random.Random(stable_seed("null", n, 3, seed))
        null_ms = boolean_null(monosets, nb, rng)
        nrec3, _, _, _ = analyze_syzygy_space(null_ms, nb, 3, extract=False,
                                              block_size=n)
        nrec4, _, _, _ = analyze_syzygy_space(null_ms, nb, 4, extract=False,
                                              block_size=n)
        nrec3.pop("extra_reps", None)
        nrec4.pop("extra_reps", None)
        stages["S0"] = {
            "meta": meta, "nb": int(nb),
            "filter": {"rx_zero": bool(rx_zero), "has_linear_eq": bool(has_lin),
                       "standard": standard},
            "D3": rec3, "D4": rec4,
            "residual_4_pinned": int(rec4["extra"] - rank_old),
            "residual_4_canonical": int(rec4["extra"] - rank_new),
            "B3": rB3, "B4": rB4,
            "null_D3": nrec3, "null_D4": nrec4,
            "c5_null_d3d4_ok": bool(nrec3["extra"] == 0 and nrec4["extra"] == 0
                                    and nrec3["rank"] == nrec3["sr_pred"]
                                    and nrec4["rank"] == nrec4["sr_pred"]),
            "wall_s": round(time.time() - t0, 2),
        }
        save_cell_state(st)
        log("cell n=%d s=%d S0: standard=%s D3 def=%d D4 def=%d res4=%d/%d "
            "B3=%d B4=%d null_ok=%s (%.1fs)" % (
                n, seed, standard, rec3["deficit"], rec4["deficit"],
                stages["S0"]["residual_4_canonical"],
                stages["S0"]["residual_4_pinned"], rB3, rB4,
                stages["S0"]["c5_null_d3d4_ok"], stages["S0"]["wall_s"]))
        out["cells"].append(dict(st))
        flush()
        del monosets, rows3, kernel3, kpiv3, rows4, kernel4, kpiv4
        gc.collect()
    else:
        out["cells"].append(dict(st))
        log("cell n=%d s=%d S0: resumed (done)" % (n, seed))

    # ---------------- S1 ----------------
    if "S1" not in stages:
        if softcap_hit():
            st["status"] = "censored_softcap_before_S1"
            save_cell_state(st)
            out["cells"][-1] = dict(st)
            flush()
            return
        t0 = time.time()
        monosets, nb, meta = build_boolean_semaev(n, 3, seed)
        rec3, rows3, kernel3, kpiv3 = analyze_syzygy_space(
            monosets, nb, 3, extract=True, block_size=n)
        rec4, rows4, kernel4, kpiv4 = analyze_syzygy_space(
            monosets, nb, 4, extract=True, block_size=n)
        B3, rB3 = quotient_basis(kernel3, kpiv3)
        B4, rB4 = quotient_basis(kernel4, kpiv4)
        assert rB3 == stages["S0"]["B3"] and rB4 == stages["S0"]["B4"], \
            "S1 rebuild identity mismatch (instrument drift)"
        st1 = build_d5_stage1(monosets, nb, rows3, B3, rows4, B4)
        sys_hash = monosets_hash(monosets)
        payload = {"nrows5": st1["nrows5"], "ncols5": st1["ncols5"],
                   "n_vanish": st1["n_vanish"],
                   "n_k5_family": len(st1["k5_pos"]),
                   "n_F3": len(st1["f3_pos"]), "n_F4": len(st1["f4_pos"]),
                   "miss3": st1["miss3"], "miss4": st1["miss4"],
                   "system_hash": sys_hash,
                   "wall_s": round(time.time() - t0, 2)}
        # checkpoint the compact payloads
        wd = Path(args.work)
        wd.mkdir(parents=True, exist_ok=True)
        with open(wd / "s1_vectors.pkl", "wb") as f:
            pickle.dump({"k5_pos": st1["k5_pos"], "f3_pos": st1["f3_pos"],
                         "f4_pos": st1["f4_pos"], "nrows5": st1["nrows5"],
                         "system_hash": sys_hash}, f, protocol=4)
        payload["s1_vectors_sha256"] = file_hash(wd / "s1_vectors.pkl")
        with open(wd / "s1_adjacency.pkl", "wb") as f:
            pickle.dump({"col_rows": st1["col_rows"], "ncols": st1["ncols5"],
                         "nrows": st1["nrows5"], "system_hash": sys_hash},
                        f, protocol=4)
        payload["s1_adjacency_sha256"] = file_hash(wd / "s1_adjacency.pkl")
        stages["S1"] = payload
        save_cell_state(st)
        log("cell n=%d s=%d S1: nrows=%d ncols=%d K5=%d F3=%d F4=%d (%.1fs)" % (
            n, seed, st1["nrows5"], st1["ncols5"], len(st1["k5_pos"]),
            len(st1["f3_pos"]), len(st1["f4_pos"]), payload["wall_s"]))
        out["cells"][-1] = dict(st)
        flush()
        del st1, monosets, rows3, kernel3, kpiv3, rows4, kernel4, kpiv4
        gc.collect()
    else:
        log("cell n=%d s=%d S1: resumed (done)" % (n, seed))

    # ---------------- S2 ----------------
    if "S2" not in stages:
        if softcap_hit():
            st["status"] = "censored_softcap_before_S2"
            save_cell_state(st)
            out["cells"][-1] = dict(st)
            flush()
            return
        t0 = time.time()
        wd = Path(args.work)
        with open(wd / "s1_vectors.pkl", "rb") as f:
            vecs = pickle.load(f)
        assert vecs["system_hash"] == stages["S1"]["system_hash"]
        rankK5, A3_5, A4_5, tm = union_ranks(vecs["k5_pos"], vecs["f3_pos"],
                                             vecs["f4_pos"], vecs["nrows5"])
        stages["S2"] = {"rankK5": int(rankK5), "A3_5": int(A3_5),
                        "A4_5": int(A4_5), "m4ri_times": tm,
                        "method": "reduction-free union rank (dense m4ri)",
                        "wall_s": round(time.time() - t0, 2)}
        save_cell_state(st)
        log("cell n=%d s=%d S2: rankK5=%d A3_5=%d A4_5=%d (%.1fs)" % (
            n, seed, rankK5, A3_5, A4_5, stages["S2"]["wall_s"]))
        out["cells"][-1] = dict(st)
        flush()
        del vecs
        gc.collect()
    else:
        log("cell n=%d s=%d S2: resumed (done)" % (n, seed))

    st["status"] = "S0_S2_complete_S3_pending"
    save_cell_state(st)
    out["cells"][-1] = dict(st)
    flush()


# ==========================================================================
# rank5 mode: staircase continuation for one cell
# ==========================================================================
def run_rank5():
    n, seed = args.n, args.seed
    wd = Path(args.work)
    with open(wd / "s1_adjacency.pkl", "rb") as f:
        adj = pickle.load(f)
    col_rows = adj["col_rows"]
    nrows, ncols = adj["nrows"], adj["ncols"]
    st = staircase_run(col_rows, nrows, ncols, wd / "rank5",
                       budget=args.budget, max_units=args.max_units,
                       chunk_force=args.chunk_force, tag="n%d_s%d" % (n, seed))
    res = {"n": n, "seed": seed, "arm": "sem",
           "status": "completed_valid" if st["done"] else "censored_budget_checkpointed",
           "nrows": nrows, "ncols": ncols,
           "sr_pred": 268674 if (n == 21) else None,
           "rank_acc": st["rank_acc"], "next_col": st["next_col"],
           "cols_fraction": round(float(st["next_col"]) / float(ncols), 6),
           "secs_total": st["secs_total"], "n_units": len(st["units"]),
           "done": st["done"], "checkpoint_dir": str(wd / "rank5"),
           "resume_command": (
               "sage experiments/EXP-SIG-007/SIG7_run.sage --mode rank5 "
               "--n %d --seed %d --work %s --budget 230 --out <RUN>/raw.json"
               % (n, seed, wd))}
    if st["done"]:
        res["rank"] = st["rank_acc"]
        res["deficit"] = (res["sr_pred"] - st["rank_acc"]
                          if res["sr_pred"] else None)
    out["cells"].append(res)
    flush()
    log("rank5 n=%d s=%d: %s rank_acc=%d cols=%d/%d work=%.0fs" % (
        n, seed, res["status"], st["rank_acc"], st["next_col"], ncols,
        st["secs_total"]))


# ==========================================================================
# gate (C1/C2/C3/C4a, verbatim EXP-SIG-005 semantics)
# ==========================================================================
def measure_gate_p1_cell(n, seed, arm):
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
    rec3.pop("extra_reps", None); rec3.pop("kernel_vectors", None)
    rec4.pop("extra_reps", None); rec4.pop("kernel_vectors", None)
    cell["D3"] = rec3
    cell["D4"] = rec4
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
    red_old = [reduce_against(v, kpiv4) for v in v3_mults]
    red_old = [r for r in red_old if r]
    rank_old, _ = vec_echelon(red_old)
    residual_old = int(rec4["extra"] - rank_old)
    red_new = [full_reduce(v, kpiv4) for v in v3_mults]
    red_new = [r for r in red_new if r]
    rank_new, _ = vec_echelon(red_new)
    residual_new = int(rec4["extra"] - rank_new)
    rank_union, _ = vec_echelon(list(kpiv4.values()) + v3_mults)
    union_check = int(rank_union - rec4["rankK"])
    cell["v3_multiples_at_D4"] = {
        "rank_mod_K4_pinned": int(rank_old), "residual_pinned": residual_old,
        "rank_mod_K4_canonical": int(rank_new), "residual_canonical": residual_new,
        "union_crosscheck_rank": union_check}
    cell["controls"] = {
        "c6_union_crosscheck_eq_canonical": bool(union_check == rank_new)}
    if arm == "null":
        cell["controls"].update({
            "c5_null_extra_zero_d3d4": bool(rec3["extra"] == 0 and rec4["extra"] == 0),
            "c5_null_rank_eq_sr_pred": bool(rec3["rank"] == rec3["sr_pred"]
                                            and rec4["rank"] == rec4["sr_pred"]),
            "c5_null_residual_pinned_zero": bool(residual_old == 0),
            "c5_null_residual_canonical_zero": bool(residual_new == 0)})
    cell["wall_s"] = round(time.time() - t0, 2)
    return cell


if args.mode == 'gate':
    log("=== EXP-SIG-007 GATE: C1/C2/C3/C4a ===")
    gate_checks = []
    if not instrument_ok:
        out["cells"].append({"kind": "instrument_hash", "pass": False,
                             "hashes": instrument_hashes})
        out["gate"] = "FAIL"
        flush()
        sys.exit(1)
    out["cells"].append({"kind": "instrument_hash", "pass": True,
                         "hashes": instrument_hashes})
    flush()
    for n in (9, 12):
        c = measure_gate_p1_cell(n, 1, "null")
        c["kind"] = "C1_null_residual"
        v3 = c["v3_multiples_at_D4"]
        cond = (c["D3"]["extra"] == 0 and c["D4"]["extra"] == 0
                and c["D3"]["rank"] == c["D3"]["sr_pred"]
                and c["D4"]["rank"] == c["D4"]["sr_pred"]
                and v3["residual_pinned"] == 0 and v3["residual_canonical"] == 0
                and c["controls"]["c6_union_crosscheck_eq_canonical"])
        c["pass"] = bool(cond)
        gate_checks.append(cond)
        log("C1 null n=%d: extra=%d/%d residual=%d/%d -> %s (%.1fs)" % (
            n, c["D3"]["extra"], c["D4"]["extra"], v3["residual_pinned"],
            v3["residual_canonical"], "ok" if cond else "FAIL", c["wall_s"]))
        out["cells"].append(c)
        flush()
    n = 9
    monosets, nb, meta = build_boolean_semaev(n, 3, 1)
    rng = random.Random(stable_seed("null", n, 3, 1))
    null_ms = boolean_null(monosets, nb, rng)
    degs = [max(mono_deg(m) for m in f) for f in null_ms]
    q = [i for i, d in enumerate(degs) if d == 2]
    cc = [i for i, d in enumerate(degs) if d == 3]
    q0, q1, c0 = q[0], q[1], cc[0]
    inj = list(null_ms)
    inj[c0] = null_ms[q0] ^^ null_ms[q1]
    rec, rows, kernel, kpiv = analyze_syzygy_space(inj, nb, 3, extract=True,
                                                   block_size=n)
    det = False
    det_rep = None
    for rep in rec.get("extra_reps", []):
        if rep["n_generators"] == 3 and rep["mult_degrees"] == [0]:
            det = True
            det_rep = rep
            break
    cond = rec["extra"] >= 1 and det
    log("C2 injected: extra=%d detected=%s -> %s" % (rec["extra"], det,
                                                     "ok" if cond else "FAIL"))
    out["cells"].append({"kind": "C2_injected", "n": n, "gens": [q0, q1, c0],
                         "detected": det, "pass": bool(cond)})
    gate_checks.append(cond)
    flush()
    c = measure_gate_p1_cell(15, 1, "sem")
    c["kind"] = "C3_t2_anchor"
    v3 = c["v3_multiples_at_D4"]
    cond = (c["D3"]["deficit"] == 1 and c["D3"]["extra"] == 1
            and c["D4"]["deficit"] == 40 and c["D4"]["extra"] == 40
            and v3["residual_pinned"] == 10 and v3["residual_canonical"] == 11
            and c["controls"]["c6_union_crosscheck_eq_canonical"])
    c["pass"] = bool(cond)
    gate_checks.append(cond)
    log("C3 T2 anchor n=15 s1: D3 def=%d D4 def=%d residual=%d/%d -> %s (%.1fs)" % (
        c["D3"]["deficit"], c["D4"]["deficit"], v3["residual_pinned"],
        v3["residual_canonical"], "ok" if cond else "FAIL", c["wall_s"]))
    out["cells"].append(c)
    flush()
    c1 = measure_gate_p1_cell(15, 3, "sem")
    c2 = measure_gate_p1_cell(15, 3, "sem")
    same = (json.dumps(jsonsafe(strip_timing(c1)), sort_keys=True)
            == json.dumps(jsonsafe(strip_timing(c2)), sort_keys=True))
    out["cells"].append({"kind": "C4a_rerun_check", "n": 15, "seed": 3,
                         "arm": "sem", "identical": bool(same)})
    log("C4a in-run determinism: identical=%s" % same)
    gate_checks.append(same)
    flush()
    out["gate"] = "PASS" if all(gate_checks) else "FAIL"
    log("=== GATE: %s ===" % out["gate"])

elif args.mode == 'anchor':
    tokens = []
    for tok in args.cells.split(','):
        tok = tok.strip()
        if tok:
            nn, ss = tok.split(':')
            tokens.append((int(nn), int(ss)))
    log("=== EXP-SIG-007 ANCHORS: %s ===" % tokens)
    for (nn, ss) in tokens:
        cell = measure_anchor_cell(nn, ss)
        out["cells"].append(cell)
        flush()
        if cell.get("c9a_anchor") and not cell["c9a_anchor"]["pass"]:
            halt(4, "C9a staged-path anchor mismatch at n=%d seed=%d "
                    "(instrument drift, not evidence)" % (nn, ss),
                 cell={"n": nn, "seed": ss})
        sv = cell.get("staircase_validation", {})
        for label, res in sv.items():
            if isinstance(res, dict) and not res.get("pass"):
                halt(5, "C9b staircase validation failed (%s)" % label,
                     cell={"n": nn, "seed": ss})

elif args.mode == 'cell':
    run_cell()

elif args.mode == 'rank5':
    run_rank5()

out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
