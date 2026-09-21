# EXP-SIG-008 driver — validate the re-derived D6 null baseline at n=12 and
# decompose the sem-D5 deficit (support-induced vs genuine).
# (H-SIG-001; handoff TASK-20260724-006.)
#
# Reuses the EXP-SIG-001..007 pinned instrument BIT-IDENTICALLY
# (src/h013_f5_signatures.sage sha256
# 1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087 + 3 modules).
# The pinned instrument is loaded, never modified.
#
# Cell: boolean chained Semaev m = t = 3, n = 12 (nb = 24), seed 2 — the
# canonical recorded D5 closure cell (EV-SIG-003/005/007: rank5 28,097,
# deficit_5 1,321, extra_5 1,322, rankK5 2,093, A3_5 242, A4_5 444).
#
# Prediction on record (EV-SIG-006): D6 column-matched null VALID at n >= 12
# (freeze = n/3+3 = 7 at n=12), sr_pred(12,6) = 156,520.
#
# STAGES (every mode resumable; soft-cap checked between stages):
#   gate    instrument hashes; sem build + meta; sr_pred table (assert D6 ==
#           156,520, freeze == 7); pinned D3/D4 sem anchors (def 1/32);
#           int-mask row builder cross-check vs pinned at D3/D4; pickle
#           benchmark (carry-dir decision); BUILD1: sem D6 column set,
#           sextics, deg<=5 completeness, D5 colset == 46,709 assert,
#           safe pools + sextic upsets (numpy) -> work/build1.pkl
#   build2  seeded greedy cover + swap repair -> N1 with D6 column set ==
#           sem's EXACTLY; determinism rebuild; |V| (2^24); save n1_ms.
#   n1d345  N1 at D3/D4/D5 (m4ri ranks, K-family ranks, extra/deficit) +
#           sem D5 anchor reproduction (rank 28,097 / deficit 1,321 /
#           extra 1,322 / rankK5 2,093 — halt on mismatch). -> GATE-3 data.
#   n1s1    N1 D6 rows/adjacency (CSR) + K6 family + rankK6 (m4ri) ->
#           work/null_s1.pkl
#   rank6   checkpointed block-staircase rank of M6 for --arm null|sem
#   sems1   sem D6 rows/adjacency + K6 family + left-kernel quotient bases
#           B3/B4/B5 (m4ri, NO python extract echelon) + F3/F4/F5 images +
#           D5-closure anchor (A3_5 == 242, A4_5 == 444 via this exact
#           machinery — halt on mismatch) -> work/sem_s1.pkl
#   sems2   union ranks at D6: rankK6, A3_6, A4_6, A5 (dense m4ri staged)
#
# Kill rule: 300 s platform cap per invocation; --soft-cap 245 checked before
# every stage; every stage checkpoints to disk before the cap can fire.

import sys, os, time, json, argparse, platform, datetime, itertools, hashlib
import pickle, gc, random
from array import array
from pathlib import Path

import numpy as np

p = argparse.ArgumentParser()
p.add_argument('--mode', required=True,
               choices=['gate', 'build2', 'n1d345', 'n1s1', 'rank6',
                        'sems1', 'sems2'])
p.add_argument('--out', required=True)
p.add_argument('--work', default='experiments/EXP-SIG-008/work')
p.add_argument('--arm', default='null', choices=['null', 'sem'])
p.add_argument('--n', type=int, default=12)
p.add_argument('--seed', type=int, default=2)
p.add_argument('--budget', type=float, default=225.0,
               help='rank6: stop starting new chunks after this many seconds')
p.add_argument('--soft-cap', type=int, default=245)
p.add_argument('--chunk-force', type=int, default=12000)
p.add_argument('--carry-dir', default='',
               help='override carry checkpoint dir (benchmark decision)')
args = p.parse_args()

EXPDIR = Path(args.out).resolve().parents[2]
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
from sage.all import GF, matrix
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

F2 = GF(2)
ONE = int(1)
t_start = time.time()
WORK = Path(args.work)
WORK.mkdir(parents=True, exist_ok=True)

N, SEED = int(args.n), int(args.seed)


def fsafe(o):
    """JSON-safe conversion that also handles sage Integer/RealNumber/Rational."""
    if isinstance(o, dict):
        return {str(k): fsafe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [fsafe(v) for v in o]
    if isinstance(o, bool) or o is None or isinstance(o, (int, float, str)):
        return o
    try:
        from sage.rings.integer import Integer as _SI
        if isinstance(o, _SI):
            return int(o)
    except Exception:
        pass
    try:
        from sage.rings.rational import Rational as _SR
        from sage.rings.real_mpfr import RealNumber as _SReal
        if isinstance(o, (_SR, _SReal)):
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
    "experiment": "EXP-SIG-008",
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
    "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "git_commit": "f6fa31b08a6262760f50c19d6704fcf16d02d81a",
    "cells": [],
}


def flush():
    out["elapsed_s_so_far"] = round(time.time() - t_start, 2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(fsafe(out), fh, indent=1)


def softcap_hit(cap=None):
    return (time.time() - t_start) > (cap if cap is not None else args.soft_cap)


def log(msg):
    print("[sig8 %s] %s" % (time.strftime('%H:%M:%S'), msg), flush=True)


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
# sem build + int-mask monomial machinery
# ==========================================================================
_SEM_CACHE = {}


def get_sem():
    if "sem" not in _SEM_CACHE:
        t0 = time.time()
        monosets, nb, meta = build_boolean_semaev(N, 3, SEED)
        if monosets is None:
            halt(9, "no decomposable R at n=%d seed=%d" % (N, SEED))
        # frozenset monosets -> sorted lists of int masks
        ms = []
        for f in monosets:
            eq = []
            for m in f:
                mm = int(0)
                for v in m:
                    mm |= ONE << int(v)
                eq.append(mm)
            ms.append(sorted(eq))
        degs = [max(m.bit_count() for m in f) for f in ms]
        _SEM_CACHE["sem"] = (monosets, ms, nb, degs, meta)
        log("sem build n=%d seed=%d nb=%d eqs=%d (%.1fs)"
            % (N, SEED, nb, len(ms), time.time() - t0))
    return _SEM_CACHE["sem"]


COMBOS = {}       # md -> np.int64 array of masks (over nb vars)
COMBOS_LIST = {}  # md -> python list of ints


def init_combos(nb, maxd=6):
    for md in range(maxd + 1):
        lst = []
        for combo in itertools.combinations(range(nb), md):
            mm = int(0)
            for v in combo:
                mm |= ONE << v
            lst.append(mm)
        COMBOS_LIST[md] = lst
        COMBOS[md] = np.array(lst, dtype=np.int64)


def colset_of_int(ms, degs, nb, D):
    """cols(D) = up-closure of supports with degree slack (SIG6 law), int masks."""
    acc = []
    for i, S in enumerate(ms):
        di = degs[i]
        for mp in S:
            d = mp.bit_count()
            mdmax = min(D - di, D - d)
            for md in range(mdmax + 1):
                arr = COMBOS[md]
                sel = arr[np.bitwise_and(arr, mp) == 0]
                acc.append(np.bitwise_or(sel, mp))
    return set(np.concatenate(acc).tolist())


def colset_degree_hist(cols, D):
    h = {}
    for m in cols:
        d = m.bit_count()
        h[d] = h.get(d, 0) + 1
    return h


def sextics_of(cols):
    return np.array(sorted(m for m in cols if m.bit_count() == 6),
                    dtype=np.int64)


def build_rows(ms, degs, nb, D):
    """Tagged Macaulay rows (int-mask semantics == pinned tagged_macaulay):
    rows for every (i, mu) with |mu| <= D - deg_i; prod = boolean product
    (symmetric difference). Returns (tags, prod_masks_per_row, colidx)."""
    tags = []
    prods = []
    for i, S in enumerate(ms):
        di = degs[i]
        Sarr = np.array(S, dtype=np.int64)
        for md in range(D - di + 1):
            for mu in COMBOS_LIST[md]:
                pr = np.bitwise_or(Sarr, mu)
                u, c = np.unique(pr, return_counts=True)
                pz = u[c % 2 == 1]
                tags.append((i, mu))
                prods.append(pz)
    allcols = np.unique(np.concatenate([pz for pz in prods if len(pz)]))
    colidx = {int(m): k for k, m in enumerate(allcols.tolist())}
    return tags, prods, allcols, colidx


def k_family_rows(ms, degs, nb, D, tag2idx):
    """K_D model-syzygy family as position lists over row indices
    (semantics == pinned koszul_principal_vectors + vanishing units)."""
    vecs = []
    m = len(ms)
    for i in range(m):
        Si = ms[i]
        for j in range(i + 1, m):
            di, dj = degs[i], degs[j]
            if D - di - dj < 0:
                continue
            Sj = ms[j]
            for md in range(D - di - dj + 1):
                for mu in COMBOS_LIST[md]:
                    pos = [tag2idx[(i, mu | c)] for c in Sj]
                    pos += [tag2idx[(j, mu | c)] for c in Si]
                    u, c = np.unique(np.array(pos, dtype=np.int64),
                                     return_counts=True)
                    v = u[c % 2 == 1]
                    if len(v):
                        vecs.append(v.astype(np.int32))
    for i in range(m):
        di = degs[i]
        if D - 2 * di < 0:
            continue
        Si = ms[i]
        for md in range(D - 2 * di + 1):
            for mu in COMBOS_LIST[md]:
                pos = [tag2idx[(i, mu)]] + [tag2idx[(i, mu | c)] for c in Si]
                u, c = np.unique(np.array(pos, dtype=np.int64),
                                 return_counts=True)
                v = u[c % 2 == 1]
                if len(v):
                    vecs.append(v.astype(np.int32))
    return vecs


def m4ri_from_positions(pos_lists, ncols):
    M = matrix(F2, len(pos_lists), ncols)
    for i, pl in enumerate(pos_lists):
        for j in pl:
            M[i, int(j)] = 1
    return M


def rows_prods_to_positions(prods, colidx):
    return [np.array(sorted(colidx[int(m)] for m in pz), dtype=np.int32)
            if len(pz) else np.array([], dtype=np.int32) for pz in prods]


def images_of_int(kbasis_pos, tags_src, tag2idx_dst, mults):
    """F5-style images of row-syzygy basis vectors under multiplier sets
    (semantics == pinned images_of)."""
    imgs = []
    misses = 0
    for kv in kbasis_pos:
        tags = [tags_src[int(pp)] for pp in kv]
        for nu in mults:
            pos = []
            for (i, mu) in tags:
                ix = tag2idx_dst.get((i, mu | nu))
                if ix is None:
                    misses += 1
                else:
                    pos.append(ix)
            if pos:
                u, c = np.unique(np.array(pos, dtype=np.int64),
                                 return_counts=True)
                v = u[c % 2 == 1]
                if len(v):
                    imgs.append(v.astype(np.int32))
    return imgs, misses


def left_kernel_positions(M):
    """Basis of the LEFT kernel {v : v.M = 0} as position lists (dense m4ri)."""
    MT = M.transpose()
    K = MT.right_kernel_matrix()
    outk = []
    for r in K.rows():
        outk.append(np.array(r.nonzero_positions(), dtype=np.int32))
    return outk


def quotient_lift_positions(family_pos, kernel_pos, ncols):
    """Basis of kernel/family lifted to row vectors: rref rows beyond
    rank(family) in the stacked echelon. Their image span mod family-images
    == canonical quotient-basis image span (linear image map)."""
    A = m4ri_from_positions(family_pos, ncols)
    A.echelonize()
    rA = int(A.rank())
    B = m4ri_from_positions(kernel_pos, ncols)
    C = A.stack(B)
    del A, B
    gc.collect()
    C.echelonize()
    rt = int(C.rank())
    lifts = []
    for i in range(rA, rt):
        lifts.append(np.array(C.row(i).nonzero_positions(), dtype=np.int32))
    del C
    gc.collect()
    return rA, rt, lifts


# ==========================================================================
# BUILD1 helpers: safe pools + sextic upsets (numpy)
# ==========================================================================
def build1_path():
    return WORK / "build1.pkl"


def run_build1(cell):
    """sem D6 column set, sextics, deg<=5 completeness, D5 colset anchor,
    safe pools + upsets. Resumable via cell['build1_stage']."""
    monosets, ms, nb, degs, meta = get_sem()
    init_combos(nb, 6)
    st = cell.setdefault("build1", {})
    stage = st.get("stage", 0)

    if stage < 1:
        t0 = time.time()
        cols6 = colset_of_int(ms, degs, nb, 6)
        st["ncols_sem_D6"] = len(cols6)
        st["cols_sem_D6_degree_hist"] = {str(k): v for k, v in
                                         sorted(colset_degree_hist(cols6, 6).items())}
        st["build_s"] = round(time.time() - t0, 2)
        # degree<=5 completeness of the sem D6 column set
        all_le5 = set()
        for md in range(6):
            all_le5.update(COMBOS_LIST[md])
        missing_le5 = all_le5 - cols6
        st["deg_le5_total"] = len(all_le5)
        st["deg_le5_missing_in_sem_D6"] = len(missing_le5)
        st["deg_le5_complete"] = (len(missing_le5) == 0)
        sx = sextics_of(cols6)
        st["n_sextics_sem_D6"] = int(len(sx))
        # D5 colset anchor (recorded: sem ncols at D5 = 46,709; SIG7 C9b state)
        cols5 = colset_of_int(ms, degs, nb, 5)
        st["ncols_sem_D5"] = len(cols5)
        st["ncols_sem_D5_anchor_46709"] = bool(len(cols5) == 46709)
        log("build1 s1: ncols6=%d sextics=%d le5_missing=%d ncols5=%d (%.1fs)"
            % (len(cols6), len(sx), len(missing_le5), len(cols5),
               time.time() - t0))
        with open(build1_path(), "wb") as f:
            pickle.dump({"cols6": cols6, "sextics": sx}, f, protocol=4)
        st["build1_pkl_sha256"] = file_hash(build1_path())
        st["stage"] = int(1)
        flush()
    if softcap_hit():
        cell["status"] = "censored_softcap_build1_stage1"
        return cell

    if stage < 2:
        t0 = time.time()
        with open(build1_path(), "rb") as f:
            b1 = pickle.load(f)
        assert b1["sextics"].shape[0] == st["n_sextics_sem_D6"]
        sextics_sorted = b1["sextics"]

        def is_safe(mp, di):
            d = mp.bit_count()
            md = 6 - d
            if md > 6 - di:
                return True
            arr = COMBOS[md]
            sel = np.bitwise_or(arr[np.bitwise_and(arr, mp) == 0], mp)
            idx = np.searchsorted(sextics_sorted, sel)
            idx = np.minimum(idx, len(sextics_sorted) - 1)
            return bool((sextics_sorted[idx] == sel).all())

        pools = {}   # (di,d) -> np.int64 array of safe masks
        for di in (2, 3):
            for d in range(1, di + 1):
                safe = [mp for mp in COMBOS_LIST[d] if is_safe(mp, di)]
                pools[(di, d)] = np.array(sorted(safe), dtype=np.int64)
                log("pool(di=%d,d=%d): %d of %d safe"
                    % (di, d, len(safe), len(COMBOS_LIST[d])))
        st["pool_sizes"] = {"%d,%d" % k: int(len(v)) for k, v in pools.items()}
        st["build2_s"] = round(time.time() - t0, 2)
        with open(build1_path(), "wb") as f:
            pickle.dump({"cols6": b1["cols6"], "sextics": b1["sextics"],
                         "pools": pools}, f, protocol=4)
        st["build1_pkl_sha256"] = file_hash(build1_path())
        st["stage"] = int(2)
        flush()
    if softcap_hit():
        cell["status"] = "censored_softcap_build1_stage2"
        return cell

    if stage < 3:
        t0 = time.time()
        with open(build1_path(), "rb") as f:
            b1 = pickle.load(f)
        sextics_sorted = b1["sextics"]
        pools = b1["pools"]
        upsets = {}  # (di,d,mp) -> int32 indices into sextics_sorted
        for (di, d), parr in pools.items():
            md = 6 - d
            for mp in parr.tolist():
                if md > 6 - di:
                    upsets[(di, d, mp)] = np.array([], dtype=np.int32)
                    continue
                arr = COMBOS[md]
                sel = np.bitwise_or(arr[np.bitwise_and(arr, mp) == 0], mp)
                idx = np.searchsorted(sextics_sorted, sel)
                assert (sextics_sorted[idx] == sel).all(), "unsafe in upset"
                upsets[(di, d, mp)] = idx.astype(np.int32)
        st["n_upsets"] = len(upsets)
        st["upset_elems_total"] = int(sum(len(v) for v in upsets.values()))
        st["build3_s"] = round(time.time() - t0, 2)
        with open(build1_path(), "wb") as f:
            pickle.dump({"cols6": b1["cols6"], "sextics": b1["sextics"],
                         "pools": pools, "upsets": upsets}, f, protocol=4)
        st["build1_pkl_sha256"] = file_hash(build1_path())
        st["stage"] = int(3)
        flush()
    cell["status"] = "build1_complete"
    return cell


# ==========================================================================
# mode: gate — controls + benchmark + build1
# ==========================================================================
def run_gate():
    if not instrument_ok:
        out["cells"].append({"kind": "instrument_hash", "pass": False,
                             "hashes": instrument_hashes})
        out["gate"] = "FAIL"
        flush()
        sys.exit(1)
    out["cells"].append({"kind": "instrument_hash", "pass": True,
                         "hashes": instrument_hashes})
    flush()
    monosets, ms, nb, degs, meta = get_sem()
    init_combos(nb, 6)
    cell = {"kind": "gate", "n": N, "seed": SEED, "nb": int(nb)}
    # sem meta: filter + support structure (NEW record at n=12 s2)
    rx_zero = str(meta.get("R_x", "")).strip() == "0"
    has_lin = int(meta.get("eq_degs_hist", {}).get("1", 0)) > 0
    cell["meta"] = meta
    cell["filter"] = {"rx_zero": bool(rx_zero), "has_linear_eq": bool(has_lin),
                      "standard": bool((not rx_zero) and (not has_lin))}
    cell["eq_degs"] = sorted(degs)
    cell["support_sizes_per_eq"] = [len(f) for f in ms]
    cell["support_degree_hist_per_eq"] = [
        {str(d): sum(1 for m in f if m.bit_count() == d)
         for d in sorted({m.bit_count() for m in f})} for f in ms]
    # sr_pred table + freeze degree (pinned formula)
    pred, HF = semireg_rank_pred(degs, nb, 8)
    cell["sr_pred_table"] = {str(D): int(pred[D]) for D in range(9)}
    cell["HF"] = [int(x) for x in HF]
    frz = next((D for D in range(9) if HF[D] == 0), None)
    cell["freeze_degree"] = int(frz) if frz is not None else None
    cell["sr_pred_D6_eq_156520"] = bool(int(pred[6]) == 156520)
    cell["freeze_eq_7"] = bool(frz == 7)
    log("gate: sr_pred D6=%d (expect 156520) freeze=%s (expect 7)"
        % (int(pred[6]), str(frz)))
    if not cell["sr_pred_D6_eq_156520"]:
        halt(2, "sr_pred(12,6) != 156,520 — pinned-formula drift", cell=cell)
    if not cell["freeze_eq_7"]:
        halt(2, "freeze degree != 7 at n=12 — series drift", cell=cell)
    flush()
    # pinned D3/D4 sem anchors (EV-SIG-002 laws: D3 def/extra 1, D4 8n/3=32)
    for D, dexp in ((3, 1), (4, 32)):
        t0 = time.time()
        rec, _, _, _ = analyze_syzygy_space(monosets, nb, D, extract=False)
        rec.pop("extra_reps", None)
        cell["sem_D%d_pinned" % D] = rec
        ok = (rec["deficit"] == dexp and rec["extra"] == dexp)
        cell["sem_D%d_anchor_ok" % D] = bool(ok)
        log("gate: sem D%d pinned nrows=%d ncols=%d rank=%d sr=%d def=%d "
            "extra=%d ok=%s (%.1fs)" % (D, rec["nrows"], rec["ncols"],
                                        rec["rank"], rec["sr_pred"],
                                        rec["deficit"], rec["extra"], ok,
                                        time.time() - t0))
        flush()
        if not ok:
            halt(3, "sem D%d anchor mismatch (expect %d) — instrument drift"
                 % (D, dexp), cell=cell)
    # int-mask row-builder cross-check vs pinned at D3 and D4 (sem arm)
    for D in (3, 4):
        t0 = time.time()
        tags, prods, allcols, colidx = build_rows(ms, degs, nb, D)
        pos = rows_prods_to_positions(prods, colidx)
        M = m4ri_from_positions(pos, len(allcols))
        r = int(M.rank())
        recp = cell["sem_D%d_pinned" % D]
        ok = (r == recp["rank"] and len(tags) == recp["nrows"]
              and len(allcols) == recp["ncols"])
        cell["xcheck_intmask_D%d" % D] = {
            "rank_intmask_m4ri": r, "nrows_intmask": len(tags),
            "ncols_intmask": len(allcols), "pinned_rank": recp["rank"],
            "pass": bool(ok), "sec": round(time.time() - t0, 2)}
        log("gate: xcheck D%d int-mask rank=%d nrows=%d ncols=%d ok=%s"
            % (D, r, len(tags), len(allcols), ok))
        del M, pos
        gc.collect()
        flush()
        if not ok:
            halt(4, "int-mask row builder mismatch at D%d — method bug" % D,
                 cell=cell)
    # pickle benchmark for carry-dir decision (~91 MB m4ri, D6-scale chunk)
    t0 = time.time()
    Mb = matrix(F2, 4000, 183312)
    rr = random.Random(stable_seed("sig8", "bench"))
    for i in range(4000):
        for _ in range(24):
            Mb[i, rr.randrange(183312)] = 1
    bench = {"build_s": round(time.time() - t0, 2)}
    t0 = time.time()
    buf = pickle.dumps((list(range(4000)), Mb), protocol=4)
    bench["pickle_dumps_s"] = round(time.time() - t0, 2)
    bench["bytes"] = len(buf)
    for label, d in (("tmp", "/tmp/sig8_bench"), ("volume", str(WORK))):
        Path(d).mkdir(parents=True, exist_ok=True)
        fp = Path(d) / "bench.pkl"
        t0 = time.time()
        with open(fp, "wb") as f:
            f.write(buf)
        bench["write_%s_s" % label] = round(time.time() - t0, 2)
        t0 = time.time()
        with open(fp, "rb") as f:
            _ = f.read()
        bench["read_%s_s" % label] = round(time.time() - t0, 2)
        os.remove(fp)
    import shutil
    bench["tmp_free_bytes"] = shutil.disk_usage("/tmp").free
    cell["pickle_benchmark"] = bench
    log("gate: bench dumps=%.1fs write tmp=%.1fs vol=%.1fs (%d bytes)"
        % (bench["pickle_dumps_s"], bench["write_tmp_s"],
           bench["write_volume_s"], bench["bytes"]))
    del Mb, buf
    gc.collect()
    out["cells"].append(cell)
    flush()
    # BUILD1 (resumable; may censor to a follow-up invocation)
    b1cell = run_build1({"kind": "build1", "n": N, "seed": SEED})
    out["cells"].append(b1cell)
    flush()
    out["gate"] = "PASS"
    log("=== GATE+BUILD1 done: %s ===" % b1cell.get("status"))


# ==========================================================================
# mode: build2 — greedy cover + repair + N1 validation
# ==========================================================================
def run_build2():
    monosets, ms, nb, degs, meta = get_sem()
    init_combos(nb, 6)
    with open(build1_path(), "rb") as f:
        b1 = pickle.load(f)
    sextics_sorted, pools, upsets = b1["sextics"], b1["pools"], b1["upsets"]
    NSEX = int(len(sextics_sorted))
    cell = {"kind": "build2", "n": N, "seed": SEED, "n_sextics": NSEX}

    # required support counts per (eq, monomial-degree) == sem histogram
    required = {}
    for i, f in enumerate(ms):
        for m in f:
            required[(i, m.bit_count())] = required.get((i, m.bit_count()), 0) + 1
    # feasibility: pool >= required everywhere
    feas = all(len(pools[(degs[i], d)]) >= cnt
               for (i, d), cnt in required.items() if d > 0)
    cell["pool_feasible"] = bool(feas)
    if not feas:
        cell["status"] = "construction_infeasible_pools"
        out["cells"].append(cell)
        halt(5, "safe pools infeasible at n=12 — construction family empty",
             cell=cell)

    def greedy_cover(seed_tag):
        rng = random.Random(stable_seed("sig8", "n1greedy", N, SEED, seed_tag))
        cnt = np.zeros(NSEX, dtype=np.int32)
        chosen = {}
        classes = sorted(required.keys())
        # forced classes (pool == required): take wholesale
        free = []
        for key in classes:
            i, d = key
            if d == 0:
                chosen[key] = [int(0)]
                continue
            parr = pools[(degs[i], d)]
            if len(parr) == required[key]:
                chosen[key] = parr.tolist()
                for mp in chosen[key]:
                    cnt[upsets[(degs[i], d, mp)]] += 1
            else:
                free.append(key)
        rng.shuffle(free)
        for key in free:
            i, d = key
            di = degs[i]
            need = required[key]
            pool = pools[(di, d)].tolist()
            rng.shuffle(pool)
            picked = []
            upset_list = [upsets[(di, d, mp)] for mp in pool]
            for _ in range(need):
                best, best_gain = None, -1
                for ci, up in enumerate(upset_list):
                    if picked and pool[ci] in picked:
                        continue
                    g = int((cnt[up] == 0).sum()) if len(up) else 0
                    if g > best_gain:
                        best, best_gain = ci, g
                        if g == 0 and best is not None:
                            break
                picked.append(pool[best])
                if len(upset_list[best]):
                    cnt[upset_list[best]] += 1
            chosen[key] = picked
        # swap repair of uncovered sextics
        n_rep = 0
        uncovered = np.where(cnt == 0)[0]
        for sidx in uncovered.tolist():
            s = int(sextics_sorted[sidx])
            done = False
            for key in sorted(required.keys()):
                i, d = key
                if d == 0 or d > 6:
                    continue
                di = degs[i]
                if 6 - d > 6 - di:
                    continue
                parr = pools[(di, d)]
                sub = parr[np.bitwise_or(parr, s) == s]
                for mp in sub.tolist():
                    if mp in chosen[key]:
                        continue
                    up_mp = upsets[(di, d, mp)]
                    for m0 in list(chosen[key]):
                        up0 = upsets[(di, d, m0)]
                        if len(up0):
                            risk = up0[cnt[up0] == 1]
                            ok = (len(risk) == 0 or
                                  bool(np.isin(risk, up_mp).all()))
                        else:
                            ok = True
                        if ok:
                            chosen[key].remove(m0)
                            chosen[key].append(mp)
                            if len(up0):
                                cnt[up0] -= 1
                            if len(up_mp):
                                cnt[up_mp] += 1
                            n_rep += 1
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
            if not done:
                return chosen, cnt, n_rep, s
        return chosen, cnt, n_rep, None

    t0 = time.time()
    chosen, cnt, n_rep, failed_sextic = greedy_cover("main")
    cell["greedy_repair_s"] = round(time.time() - t0, 2)
    cell["repair_swaps"] = int(n_rep)
    cell["uncovered_after"] = int((cnt == 0).sum())
    cell["failed_sextic"] = (sorted(v for v in range(nb)
                                    if (failed_sextic >> v) & 1)
                             if failed_sextic is not None else None)
    log("build2: greedy+repair uncovered=%d swaps=%d (%.1fs)"
        % (cell["uncovered_after"], n_rep, time.time() - t0))
    flush()
    if failed_sextic is not None:
        cell["status"] = "construction_failed_repair"
        out["cells"].append(cell)
        halt(6, "swap repair failed at n=12 (recorded, not evidence)", cell=cell)

    n1_ms = []
    for i in range(len(ms)):
        eq = set()
        for key in required:
            if key[0] == i:
                eq |= set(chosen[key])
        n1_ms.append(sorted(eq))
    # histogram match check
    hist_ok = all(sorted(m.bit_count() for m in n1_ms[i])
                  == sorted(m.bit_count() for m in ms[i])
                  for i in range(len(ms)))
    cell["histogram_match"] = bool(hist_ok)
    # column-set equality at D6 (fresh recompute, both arms)
    t0 = time.time()
    cov_n1 = colset_of_int(n1_ms, degs, nb, 6)
    cov_sem = colset_of_int(ms, degs, nb, 6)
    ceq = (cov_n1 == cov_sem)
    cell["column_set_equal_sem_D6"] = bool(ceq)
    cell["ncols_n1_D6"] = len(cov_n1)
    cell["ncols_sem_D6"] = len(cov_sem)
    cell["colset_verify_s"] = round(time.time() - t0, 2)
    log("build2: N1 D6 colset == sem: %s (%d vs %d)"
        % (ceq, len(cov_n1), len(cov_sem)))
    flush()
    if not ceq:
        cell["status"] = "construction_failed_column_inequality"
        out["cells"].append(cell)
        halt(7, "N1 D6 column set != sem's at n=12 (recorded)", cell=cell)
    # save N1 (json + pkl)
    n1_json = [[int(m) for m in f] for f in n1_ms]
    with open(WORK / "n1_ms.json", "w") as f:
        json.dump({"n": N, "seed": SEED, "nb": int(nb), "eqs": n1_json}, f)
    with open(WORK / "n1_ms.pkl", "wb") as f:
        pickle.dump({"n1_ms": n1_ms, "degs": degs, "nb": int(nb)}, f, protocol=4)
    cell["n1_ms_pkl_sha256"] = file_hash(WORK / "n1_ms.pkl")
    cell["n1_ms_json_sha256"] = file_hash(WORK / "n1_ms.json")
    cell["status"] = "constructed"
    # determinism rebuild (control; conditional on budget)
    if not softcap_hit(150):
        t0 = time.time()
        ch2, cnt2, n_rep2, fail2 = greedy_cover("main")
        det = (fail2 is None
               and all(sorted(ch2[k]) == sorted(chosen[k]) for k in chosen))
        cell["determinism_rebuild_identical"] = bool(det)
        cell["determinism_s"] = round(time.time() - t0, 2)
        log("build2: determinism rebuild identical=%s (%.1fs)"
            % (det, time.time() - t0))
        flush()
    else:
        cell["determinism_rebuild_identical"] = "censored_budget"
    # variety ground truth |V| (2^24; control; conditional on budget)
    if not softcap_hit(170):
        t0 = time.time()
        P = np.arange(2 ** nb, dtype=np.uint32)
        sol = np.ones(2 ** nb, dtype=bool)
        for f in n1_ms:
            acc = np.zeros(2 ** nb, dtype=bool)
            for m in f:
                acc = np.logical_xor(acc, (P & np.uint32(m)) == np.uint32(m))
            sol &= ~acc
        cell["variety_size"] = int(sol.sum())
        cell["variety_s"] = round(time.time() - t0, 2)
        log("build2: N1 |V| = %d (%.1fs)" % (cell["variety_size"],
                                             time.time() - t0))
        flush()
    else:
        cell["variety_size"] = "censored_budget"
    out["cells"].append(cell)
    flush()


# ==========================================================================
# shared measurement: m4ri rank + K-family rank for one (arm, D) cell
# ==========================================================================
def measure_cell_m4ri(ms_int, degs, nb, D, vanish_expected=None):
    """nrows/ncols/rank/rankK/extra/deficit via dense m4ri + int-mask rows."""
    t0 = time.time()
    tags, prods, allcols, colidx = build_rows(ms_int, degs, nb, D)
    nrows, ncols = len(tags), len(allcols)
    pos = rows_prods_to_positions(prods, colidx)
    M = m4ri_from_positions(pos, ncols)
    rank = int(M.rank())
    del M, pos
    gc.collect()
    tag2idx = {tg: ix for ix, tg in enumerate(tags)}
    kvecs = k_family_rows(ms_int, degs, nb, D, tag2idx)
    n_vanish = 0
    for ix, pz in enumerate(prods):
        if len(pz) == 0:
            kvecs.append(np.array([ix], dtype=np.int32))
            n_vanish += 1
    MK = m4ri_from_positions(kvecs, nrows)
    rankK = int(MK.rank())
    del MK, kvecs
    gc.collect()
    pred, HF = semireg_rank_pred(degs, nb, D)
    kernel = nrows - rank
    return {"D": D, "nrows": nrows, "ncols": ncols, "rank": rank,
            "sr_pred": int(pred[D]), "deficit": int(pred[D]) - rank,
            "kernel_dim": kernel, "rankK": rankK,
            "extra": kernel - rankK, "n_vanish": n_vanish,
            "sec": round(time.time() - t0, 2)}


def load_n1():
    with open(WORK / "n1_ms.pkl", "rb") as f:
        d = pickle.load(f)
    return d["n1_ms"], d["degs"], d["nb"]


def to_frozensets(ms_int):
    fs = []
    for f in ms_int:
        fs.append(set(frozenset(v for v in range(64) if (m >> v) & 1)
                      for m in f))
    return fs


# ==========================================================================
# mode: n1d345 — N1 at D3/D4/D5 + sem D5 anchor (GATE-3 data)
# ==========================================================================
def run_n1d345():
    monosets, ms_sem, nb, degs, meta = get_sem()
    init_combos(nb, 6)
    n1_ms, degs_n1, nb_n1 = load_n1()
    assert nb_n1 == nb and degs_n1 == degs
    cell = {"kind": "n1d345", "n": N, "seed": SEED,
            "n1_ms_pkl_sha256": file_hash(WORK / "n1_ms.pkl")}
    # sem D5 anchor reproduction (recorded: EV-SIG-003/005/007)
    t0 = time.time()
    sem5 = measure_cell_m4ri(ms_sem, degs, nb, 5)
    cell["sem_D5"] = sem5
    anch = {"rank": 28097, "sr_pred": 29418, "deficit": 1321,
            "extra": 1322, "rankK": 2093, "kernel_dim": 3415,
            "nrows": 31512, "ncols": 46709}
    ok = all(sem5[k] == v for k, v in anch.items())
    cell["sem_D5_anchor"] = {"expected": anch, "pass": bool(ok)}
    log("n1d345: sem D5 rank=%d sr=%d def=%d extra=%d rankK=%d anchor=%s (%.1fs)"
        % (sem5["rank"], sem5["sr_pred"], sem5["deficit"], sem5["extra"],
           sem5["rankK"], ok, time.time() - t0))
    out["cells"].append(cell)
    flush()
    if not ok:
        halt(8, "sem D5 anchor mismatch at n=12 s2 — instrument drift",
             cell=cell)
    # N1 at D3/D4/D5
    for D in (3, 4, 5):
        if softcap_hit():
            cell["status"] = "censored_softcap_before_D%d" % D
            flush()
            return
        rec = measure_cell_m4ri(n1_ms, degs, nb, D)
        cell["N1_D%d" % D] = rec
        log("n1d345: N1 D%d nrows=%d ncols=%d rank=%d sr=%d def=%d extra=%d "
            "rankK=%d (%.1fs)" % (D, rec["nrows"], rec["ncols"], rec["rank"],
                                  rec["sr_pred"], rec["deficit"], rec["extra"],
                                  rec["rankK"], rec["sec"]))
        flush()
    # pinned cross-check of the N1 D4 cell (method control)
    if not softcap_hit():
        t0 = time.time()
        n1_fs = to_frozensets(n1_ms)
        recp, _, _, _ = analyze_syzygy_space(n1_fs, nb, 4, extract=False)
        recp.pop("extra_reps", None)
        m = cell["N1_D4"]
        ok = (recp["rank"] == m["rank"] and recp["nrows"] == m["nrows"]
              and recp["ncols"] == m["ncols"] and recp["extra"] == m["extra"]
              and recp["rankK"] == m["rankK"])
        cell["xcheck_N1_D4_pinned"] = {"pinned": recp, "pass": bool(ok),
                                       "sec": round(time.time() - t0, 2)}
        log("n1d345: N1 D4 pinned xcheck pass=%s (%.1fs)"
            % (ok, time.time() - t0))
        flush()
        if not ok:
            halt(4, "N1 D4 m4ri-vs-pinned mismatch — method bug", cell=cell)
    else:
        cell["xcheck_N1_D4_pinned"] = "censored_softcap"
    cell["status"] = "completed"
    flush()


# ==========================================================================
# mode: n1s1 — N1 D6 rows/adjacency + K6 + rankK6
# ==========================================================================
def build_adjacency(prods, colidx, ncols):
    pos = rows_prods_to_positions(prods, colidx)
    lens = np.array([len(pz) for pz in pos], dtype=np.int64)
    col_ids = np.concatenate(pos) if len(pos) else np.array([], dtype=np.int32)
    row_ids = np.repeat(np.arange(len(pos), dtype=np.int64), lens)
    order = np.argsort(col_ids, kind="stable")
    col_sorted = col_ids[order]
    row_sorted = row_ids[order]
    ptr = np.searchsorted(col_sorted, np.arange(ncols + 1, dtype=np.int64))
    col_rows = [array("I", row_sorted[ptr[j]:ptr[j + 1]].tolist())
                for j in range(ncols)]
    return col_rows


def run_n1s1():
    monosets, ms_sem, nb, degs, meta = get_sem()
    init_combos(nb, 6)
    n1_ms, degs_n1, nb_n1 = load_n1()
    cell = {"kind": "n1s1", "n": N, "seed": SEED,
            "n1_ms_pkl_sha256": file_hash(WORK / "n1_ms.pkl")}
    st_path = WORK / "null_s1_state.json"
    st = {"stage": int(0)}
    if st_path.exists():
        with open(st_path) as f:
            st = json.load(f)
    if st["stage"] < 1:
        t0 = time.time()
        tags6, prods6, allcols6, colidx6 = build_rows(n1_ms, degs, nb, 6)
        nrows6, ncols6 = len(tags6), len(allcols6)
        with open(build1_path(), "rb") as f:
            b1 = pickle.load(f)
        ncols_sem6 = len(b1["cols6"])
        cell["nrows_D6"] = nrows6
        cell["ncols_D6"] = ncols6
        cell["ncols_eq_sem_D6"] = bool(ncols6 == ncols_sem6)
        log("n1s1: rows6 null nrows=%d ncols=%d (sem %d) (%.1fs)"
            % (nrows6, ncols6, ncols_sem6, time.time() - t0))
        if ncols6 != ncols_sem6:
            out["cells"].append(cell)
            halt(7, "N1 D6 ncols != sem's at rows level — construction bug",
                 cell=cell)
        t0 = time.time()
        col_rows = build_adjacency(prods6, colidx6, ncols6)
        n_vanish = sum(1 for pz in prods6 if len(pz) == 0)
        tag2idx6 = {tg: ix for ix, tg in enumerate(tags6)}
        k6_pos = k_family_rows(n1_ms, degs, nb, 6, tag2idx6)
        for ix, pz in enumerate(prods6):
            if len(pz) == 0:
                k6_pos.append(np.array([ix], dtype=np.int32))
        cell["n_vanish_D6"] = n_vanish
        cell["k6_family_size"] = len(k6_pos)
        with open(WORK / "null_s1.pkl", "wb") as f:
            pickle.dump({"nrows": nrows6, "ncols": ncols6,
                         "col_rows": col_rows, "k6_pos": k6_pos,
                         "n_vanish": n_vanish}, f, protocol=4)
        cell["null_s1_pkl_sha256"] = file_hash(WORK / "null_s1.pkl")
        cell["stage1_s"] = round(time.time() - t0, 2)
        st["stage"] = int(1)
        with open(st_path.with_suffix('.tmp'), "w") as f:
            json.dump(st, f)
        os.replace(st_path.with_suffix('.tmp'), st_path)
        log("n1s1: adjacency+K6 family built, vanish=%d fam=%d (%.1fs)"
            % (n_vanish, len(k6_pos), cell["stage1_s"]))
        out["cells"].append(cell)
        flush()
        del col_rows, k6_pos, prods6, tags6
        gc.collect()
    if st["stage"] < 2:
        if softcap_hit():
            cell["status"] = "censored_softcap_before_rankK6"
            out["cells"].append(cell)
            flush()
            return
        t0 = time.time()
        with open(WORK / "null_s1.pkl", "rb") as f:
            s1 = pickle.load(f)
        MK = m4ri_from_positions(s1["k6_pos"], s1["nrows"])
        MK.echelonize()
        rankK6 = int(MK.rank())
        del MK
        gc.collect()
        cell["rankK6_null"] = rankK6
        cell["rankK6_s"] = round(time.time() - t0, 2)
        st["stage"] = int(2)
        with open(st_path.with_suffix('.tmp'), "w") as f:
            json.dump(st, f)
        os.replace(st_path.with_suffix('.tmp'), st_path)
        with open(WORK / "null_rankK6.json", "w") as f:
            json.dump({"rankK6": rankK6}, f)
        log("n1s1: rankK6 null = %d (%.1fs)" % (rankK6, cell["rankK6_s"]))
        out["cells"].append(cell)
        flush()
    cell["status"] = "completed"
    out["cells"].append(cell)
    flush()


# ==========================================================================
# block-staircase rank engine (algorithm of SIG7 / src/h012c_block_m4ri.py)
# ==========================================================================
def process_subchunk(col_rows, j0, j1, nrows, carries):
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
        rr = _r.Random(int(1))
        for _ in range(min(64, k * k)):
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


def staircase_run(col_rows, nrows, ncols, workdir, budget, chunk_force, tag,
                  save_every=2):
    """Resumable block-staircase rank. Carries flushed every save_every units
    and always at loop exit; on-disk state only ever reflects flushed units
    (a kill loses <= save_every-1 unflushed units, which are redone)."""
    d = Path(workdir)
    d.mkdir(parents=True, exist_ok=True)
    sp = d / "state.json"
    if sp.exists():
        with open(sp) as f:
            st = json.load(f)
        assert st["nrows"] == nrows and st["ncols"] == ncols, "state mismatch"
    else:
        st = {"tag": tag, "nrows": nrows, "ncols": ncols, "next_col": 0,
              "rank_acc": 0, "carries": [], "done": False,
              "secs_total": 0.0, "units": []}
    t_load0 = time.time()
    carries = load_carries(d, st)
    load_s = time.time() - t_load0
    log("staircase %s: loaded %d carry blocks at rank %d (%.1fs)"
        % (tag, len(st["carries"]), st["rank_acc"], load_s))
    gc.disable()
    t0 = time.time()
    units = 0
    pending = []
    last_cost = None

    def flush_pending():
        for (Pv, Hv) in pending:
            entries = save_carry(d, len(st["carries"]), Pv, Hv)
            st["carries"].extend(entries)
        del pending[:]
        with open(d / "state.tmp", "w") as f:
            json.dump(fsafe(st), f)
        os.replace(d / "state.tmp", sp)

    j = st["next_col"]
    while j < st["ncols"]:
        if units > 0:
            el = time.time() - t0
            pred = (last_cost * 1.25 + 10.0) if last_cost else 60.0
            if el + pred > budget:
                break
        c = min(chunk_force, st["ncols"] - j)
        j0, j1 = j, j + c
        k, P_new, H_new, tm = process_subchunk(col_rows, j0, j1, nrows, carries)
        unit_secs = sum(tm[k2] for k2 in ("fill", "tr1", "reduce", "ech", "post"))
        last_cost = unit_secs
        if k:
            pending.append((P_new, H_new))
            carries.append((P_new, H_new))
        j = j1
        st["next_col"] = j
        st["rank_acc"] += k
        st["secs_total"] += unit_secs
        st["units"].append({"j0": j0, "j1": j1, "k": k,
                            "rank_acc": st["rank_acc"],
                            "tm": {k2: round(v, 2) for k2, v in tm.items()}})
        units += 1
        log("staircase %s cols %d..%d k=%d rank=%d fill=%.1f red=%.1f ech=%.1f post=%.1f"
            % (tag, j0, j1, k, st["rank_acc"], tm["fill"], tm["reduce"],
               tm["ech"], tm["post"]))
        if pending and len(pending) >= save_every:
            flush_pending()
    flush_pending()
    if st["next_col"] >= st["ncols"]:
        st["done"] = True
        with open(d / "state.tmp", "w") as f:
            json.dump(fsafe(st), f)
        os.replace(d / "state.tmp", sp)
    gc.enable()
    st["secs_total"] = round(st["secs_total"], 1)
    st["last_load_s"] = round(load_s, 2)
    return st


def run_rank6():
    monosets, ms_sem, nb, degs, meta = get_sem()
    arm = args.arm
    with open(WORK / ("%s_s1.pkl" % arm), "rb") as f:
        s1 = pickle.load(f)
    col_rows, nrows, ncols = s1["col_rows"], s1["nrows"], s1["ncols"]
    carry_dir = args.carry_dir or str(WORK / ("%s_rank6" % arm))
    st = staircase_run(col_rows, nrows, ncols, carry_dir,
                       budget=args.budget, chunk_force=args.chunk_force,
                       tag="%s_n%d_s%d" % (arm, N, SEED))
    pred, HF = semireg_rank_pred(degs, nb, 6)
    res = {"kind": "rank6", "arm": arm, "n": N, "seed": SEED,
           "status": "completed_valid" if st["done"] else "censored_budget_checkpointed",
           "nrows": nrows, "ncols": ncols, "sr_pred": int(pred[6]),
           "rank_acc": st["rank_acc"], "next_col": st["next_col"],
           "cols_fraction": round(float(st["next_col"]) / float(ncols), 6),
           "secs_total": st["secs_total"], "n_units": len(st["units"]),
           "done": st["done"], "checkpoint_dir": carry_dir,
           "resume_command": (
               "sage experiments/EXP-SIG-008/SIG8_run.sage --mode rank6 "
               "--arm %s --budget 225 --out <RUN>/raw.json" % arm)}
    if st["done"]:
        rank6 = st["rank_acc"]
        res["rank"] = rank6
        res["deficit"] = int(pred[6]) - rank6
        res["kernel_dim"] = nrows - rank6
        if arm == "null":
            with open(WORK / "null_rankK6.json") as f:
                rankK6 = json.load(f)["rankK6"]
        else:
            with open(WORK / "sem_rankK6.json") as f:
                rankK6 = json.load(f)["rankK6"]
        res["rankK6"] = rankK6
        res["extra"] = res["kernel_dim"] - rankK6
        res["rank_eq_sr_pred"] = bool(rank6 == int(pred[6]))
        res["extra_eq_0"] = bool(res["extra"] == 0)
        log("rank6 %s DONE: rank=%d sr=%d def=%d kernel=%d rankK=%d extra=%d"
            % (arm, rank6, int(pred[6]), res["deficit"], res["kernel_dim"],
               rankK6, res["extra"]))
    out["cells"].append(res)
    flush()
    log("rank6 %s: %s rank_acc=%d cols=%d/%d work=%.0fs"
        % (arm, res["status"], st["rank_acc"], st["next_col"], ncols,
           st["secs_total"]))


# ==========================================================================
# mode: sems1 — sem D6 S1 + closure bases + D5-closure anchor + rankK6
# ==========================================================================
def run_sems1():
    monosets, ms, nb, degs, meta = get_sem()
    init_combos(nb, 6)
    cell = {"kind": "sems1", "n": N, "seed": SEED}
    st_path = WORK / "sem_s1_state.json"
    st = {"stage": int(0)}
    if st_path.exists():
        with open(st_path) as f:
            st = json.load(f)

    def save_stage(sn):
        st["stage"] = int(sn)
        with open(st_path.with_suffix('.tmp'), "w") as f:
            json.dump(st, f)
        os.replace(st_path.with_suffix('.tmp'), st_path)
        out["cells"] = [cell]
        flush()

    # stage 1: D3/D4/D5 dense kernels + quotient lifts + D5 closure anchor
    if st["stage"] < 1:
        t0 = time.time()
        lifts = {}
        families = {}
        kernels = {}
        anchors = {}
        for D in (3, 4, 5):
            tagsD, prodsD, allcolsD, colidxD = build_rows(ms, degs, nb, D)
            posD = rows_prods_to_positions(prodsD, colidxD)
            MD = m4ri_from_positions(posD, len(allcolsD))
            tag2idxD = {tg: ix for ix, tg in enumerate(tagsD)}
            fam = k_family_rows(ms, degs, nb, D, tag2idxD)
            for ix, pz in enumerate(prodsD):
                if len(pz) == 0:
                    fam.append(np.array([ix], dtype=np.int32))
            ker = left_kernel_positions(MD)
            kernels[D] = ker
            rA, rt, lift = quotient_lift_positions(fam, ker, len(tagsD))
            lifts[D] = (tagsD, tag2idxD, lift)
            families[D] = fam
            anchors[D] = {"nrows": len(tagsD), "ncols": len(allcolsD),
                          "kernel_dim": len(ker), "rankK": rA,
                          "quotient": rt - rA}
            log("sems1 s1: D%d nrows=%d kernel=%d rankK=%d quotient=%d (%.1fs)"
                % (D, len(tagsD), len(ker), rA, rt - rA, time.time() - t0))
            del MD, posD, prodsD, ker
            gc.collect()
        # quotient-size controls (recorded: B3=1, B4=32, B5=1322)
        exp_q = {3: 1, 4: 32, 5: 1322}
        for D in (3, 4, 5):
            if anchors[D]["quotient"] != exp_q[D]:
                cell["anchors"] = anchors
                out["cells"] = [cell]
                halt(8, "quotient size at D%d = %d != recorded %d — drift"
                     % (D, anchors[D]["quotient"], exp_q[D]), cell=cell)
        # D5 closure anchor: A3_5 == 242, A4_5 == 444 via the PINNED
        # EXP-SIG-003 link semantics: FULL left-kernel bases (kernel_3,
        # kernel_4), monomial multiples embedded in the D5 row space,
        # rank mod K5. (The earlier quotient-lift variant was method drift:
        # A4_5 came out 242; fixed to the pinned full-kernel source.)
        t0 = time.time()
        tags5, tag2idx5 = lifts[5][0], lifts[5][1]
        m2 = [0] + COMBOS_LIST[1] + COMBOS_LIST[2]
        m1 = [0] + COMBOS_LIST[1]
        f3_5, miss3 = images_of_int(kernels[3], lifts[3][0], tag2idx5, m2)
        f4_5, miss4 = images_of_int(kernels[4], lifts[4][0], tag2idx5, m1)
        MK = m4ri_from_positions(families[5], len(tags5))
        MK.echelonize()
        rankK5 = int(MK.rank())
        base = MK.matrix_from_rows(list(range(rankK5)))
        del MK
        gc.collect()
        C = base.stack(m4ri_from_positions(f3_5, len(tags5)))
        C.echelonize()
        A3_5 = int(C.rank()) - rankK5
        base2 = C.matrix_from_rows(list(range(int(C.rank()))))
        del C
        gc.collect()
        C = base2.stack(m4ri_from_positions(f4_5, len(tags5)))
        C.echelonize()
        A4_5 = int(C.rank()) - rankK5
        del C, base, base2
        gc.collect()
        ok = (rankK5 == 2093 and A3_5 == 242 and A4_5 == 444
              and miss3 == 0 and miss4 == 0)
        cell["d5_closure_anchor"] = {
            "rankK5": rankK5, "A3_5": A3_5, "A4_5": A4_5,
            "expected": {"rankK5": 2093, "A3_5": 242, "A4_5": 444},
            "miss3": miss3, "miss4": miss4, "pass": bool(ok),
            "sec": round(time.time() - t0, 2)}
        log("sems1 s1: D5 closure anchor rankK5=%d A3_5=%d A4_5=%d pass=%s"
            % (rankK5, A3_5, A4_5, ok))
        cell["d35_anchors"] = anchors
        # persist FULL kernel bases for stage 4 (F-images) BEFORE stage 1 done
        with open(WORK / "sem_kernels.pkl", "wb") as f:
            pickle.dump({"k3": kernels[3], "k4": kernels[4],
                         "k5": kernels[5]}, f, protocol=4)
        save_stage(1)
        if not ok:
            halt(8, "D5 closure anchor mismatch — method/instrument drift",
                 cell=cell)
        del lifts, families
        gc.collect()
    if st["stage"] < 2:
        if softcap_hit():
            cell["status"] = "censored_softcap_before_rows6"
            out["cells"] = [cell]
            flush()
            return
        t0 = time.time()
        tags6, prods6, allcols6, colidx6 = build_rows(ms, degs, nb, 6)
        nrows6, ncols6 = len(tags6), len(allcols6)
        col_rows = build_adjacency(prods6, colidx6, ncols6)
        n_vanish = sum(1 for pz in prods6 if len(pz) == 0)
        tag2idx6 = {tg: ix for ix, tg in enumerate(tags6)}
        k6_pos = k_family_rows(ms, degs, nb, 6, tag2idx6)
        for ix, pz in enumerate(prods6):
            if len(pz) == 0:
                k6_pos.append(np.array([ix], dtype=np.int32))
        cell["nrows_D6"] = nrows6
        cell["ncols_D6"] = ncols6
        cell["n_vanish_D6"] = n_vanish
        cell["k6_family_size"] = len(k6_pos)
        with open(WORK / "sem_s1.pkl", "wb") as f:
            pickle.dump({"nrows": nrows6, "ncols": ncols6,
                         "col_rows": col_rows, "k6_pos": k6_pos,
                         "n_vanish": n_vanish}, f, protocol=4)
        cell["sem_s1_pkl_sha256"] = file_hash(WORK / "sem_s1.pkl")
        cell["rows6_s"] = round(time.time() - t0, 2)
        log("sems1 s2: rows6 nrows=%d ncols=%d vanish=%d fam=%d (%.1fs)"
            % (nrows6, ncols6, n_vanish, len(k6_pos), cell["rows6_s"]))
        save_stage(2)
        del col_rows, prods6, tags6
        gc.collect()
    if st["stage"] < 3:
        if softcap_hit():
            cell["status"] = "censored_softcap_before_rankK6"
            out["cells"] = [cell]
            flush()
            return
        t0 = time.time()
        with open(WORK / "sem_s1.pkl", "rb") as f:
            s1 = pickle.load(f)
        MK = m4ri_from_positions(s1["k6_pos"], s1["nrows"])
        MK.echelonize()
        rankK6 = int(MK.rank())
        del MK
        gc.collect()
        cell["rankK6_sem"] = rankK6
        cell["rankK6_s"] = round(time.time() - t0, 2)
        with open(WORK / "sem_rankK6.json", "w") as f:
            json.dump({"rankK6": rankK6}, f)
        log("sems1 s3: rankK6 sem = %d (%.1fs)" % (rankK6, cell["rankK6_s"]))
        save_stage(3)
    if st["stage"] < 4:
        if softcap_hit():
            cell["status"] = "censored_softcap_before_images"
            out["cells"] = [cell]
            flush()
            return
        t0 = time.time()
        # rebuild tags at D3/D4/D5 (for image tag lookup) + D6 tag2idx
        tagsD = {}
        tag2idxD = {}
        for D in (3, 4, 5):
            tg, pr, ac, ci = build_rows(ms, degs, nb, D)
            tagsD[D] = tg
            tag2idxD[D] = {t2: ix for ix, t2 in enumerate(tg)}
            del pr, ac, ci
            gc.collect()
        tags6, prods6, allcols6, colidx6 = build_rows(ms, degs, nb, 6)
        tag2idx6 = {tg: ix for ix, tg in enumerate(tags6)}
        with open(WORK / "sem_kernels.pkl", "rb") as f:
            K = pickle.load(f)
        m3 = [0] + COMBOS_LIST[1] + COMBOS_LIST[2] + COMBOS_LIST[3]
        m2 = [0] + COMBOS_LIST[1] + COMBOS_LIST[2]
        m1 = [0] + COMBOS_LIST[1]
        f3, miss3 = images_of_int(K["k3"], tagsD[3], tag2idx6, m3)
        f4, miss4 = images_of_int(K["k4"], tagsD[4], tag2idx6, m2)
        f5, miss5 = images_of_int(K["k5"], tagsD[5], tag2idx6, m1)
        cell["F3_size"] = len(f3)
        cell["F4_size"] = len(f4)
        cell["F5_size"] = len(f5)
        cell["F_misses"] = [miss3, miss4, miss5]
        with open(WORK / "sem_f345.pkl", "wb") as f:
            pickle.dump({"f3": f3, "f4": f4, "f5": f5}, f, protocol=4)
        cell["sem_f345_pkl_sha256"] = file_hash(WORK / "sem_f345.pkl")
        cell["images_s"] = round(time.time() - t0, 2)
        log("sems1 s4: F3=%d F4=%d F5=%d misses=%d/%d/%d (%.1fs)"
            % (len(f3), len(f4), len(f5), miss3, miss4, miss5,
               cell["images_s"]))
        save_stage(4)
    cell["status"] = "completed"
    out["cells"] = [cell]
    flush()


# ==========================================================================
# mode: sems2 — union ranks at D6 (rankK6, A3_6, A4_6, A5)
# ==========================================================================
def run_sems2():
    # Single-process staged union ranks; NO m4ri pickling (rows*ncols >
    # INT_MAX overflows the Sage 10.9 matrix pickle reduce -> segfault).
    cell = {"kind": "sems2", "n": N, "seed": SEED}
    st_path = WORK / "sem_s2_state.json"
    st = {"stage": int(0)}
    if st_path.exists():
        with open(st_path) as f:
            st = json.load(f)

    def save_stage(sn):
        st["stage"] = int(sn)
        with open(st_path.with_suffix('.tmp'), "w") as f:
            json.dump(fsafe(st), f)
        os.replace(st_path.with_suffix('.tmp'), st_path)
        out["cells"] = [cell]
        flush()

    with open(WORK / "sem_s1.pkl", "rb") as f:
        s1 = pickle.load(f)
    nrows6 = s1["nrows"]
    tm = {}
    if st["stage"] >= 2 and st.get("base_parts"):
        t0 = time.time()
        parts = []
        for pi in range(st["base_parts"]):
            with open(WORK / ("sem_s2_base_%02d.pkl" % pi), "rb") as f:
                parts.append(pickle.load(f))
        base = parts[0]
        for Bp in parts[1:]:
            base = base.stack(Bp)
            del Bp
        del parts
        gc.collect()
        rankK6 = st["rankK6"]
        log("sems2: resumed base rank %d (%.1fs)"
            % (int(base.rank()), time.time() - t0))
        with open(WORK / "sem_f345.pkl", "rb") as f:
            F = pickle.load(f)
        t0 = time.time()
        FM = m4ri_from_positions(F["f5"], nrows6)
        C = base.stack(FM)
        del base, FM
        gc.collect()
        C.echelonize()
        st["A5"] = int(C.rank()) - rankK6
        tm["ech_f5"] = round(time.time() - t0, 2)
        st["tm"] = tm
        log("sems2: A5=%d (%.1fs)" % (st["A5"], tm["ech_f5"]))
        save_stage(3)
        del C
        gc.collect()
        with open(WORK / "sem_rankK6.json") as f:
            rk = json.load(f)["rankK6"]
        cell["closure_D6"] = {"rankK6": rankK6, "A3_6": st["A3_6"],
                              "A4_6": st["A4_6"], "A5": st["A5"],
                              "m4ri_times": tm,
                              "method": "reduction-free union rank (dense "
                                        "m4ri), resumed for f5"}
        cell["rankK6_matches_sems1"] = bool(rankK6 == rk)
        log("sems2: rankK6=%d A3_6=%d A4_6=%d A5=%d"
            % (rankK6, st["A3_6"], st["A4_6"], st["A5"]))
        cell["status"] = "completed"
        out["cells"].append(cell)
        flush()
        return
    t0 = time.time()
    M = m4ri_from_positions(s1["k6_pos"], nrows6)
    M.echelonize()
    rankK6 = int(M.rank())
    st["rankK6"] = rankK6
    base = M.matrix_from_rows(list(range(rankK6)))
    del M
    gc.collect()
    tm["ech_k6"] = round(time.time() - t0, 2)
    st["tm"] = tm
    log("sems2 s1: rankK6=%d (%.1fs)" % (rankK6, tm["ech_k6"]))
    save_stage(1)
    with open(WORK / "sem_f345.pkl", "rb") as f:
        F = pickle.load(f)
    plan = [("f3", "A3_6", None), ("f4", "A4_6", None),
            ("f5", "A5", 22000)]
    for key, aname, chunk in plan:
        if softcap_hit():
            cell["status"] = "censored_softcap_before_%s" % key
            cell["partial"] = {k: st[k] for k in ("rankK6", "A3_6", "A4_6")
                               if k in st}
            out["cells"] = [cell]
            flush()
            return
        t0 = time.time()
        vecs = F[key]
        if chunk is None:
            chunks = [vecs]
        else:
            chunks = [vecs[i:i + chunk] for i in range(0, len(vecs), chunk)]
        ci = 0
        for ch in chunks:
            ci += 1
            FM = m4ri_from_positions(ch, nrows6)
            C = base.stack(FM)
            del base, FM
            gc.collect()
            C.echelonize()
            r1 = int(C.rank())
            base = C.matrix_from_rows(list(range(r1)))
            del C
            gc.collect()
            log("sems2: %s chunk %d/%d stacked, cum rank %d (%.1fs)"
                % (key, ci, len(chunks), r1, time.time() - t0))
            if key == "f5" and softcap_hit(275) and ci < len(chunks):
                cell["status"] = "censored_softcap_mid_f5"
                cell["partial"] = {k: st[k] for k in
                                   ("rankK6", "A3_6", "A4_6") if k in st}
                cell["f5_chunks_done"] = ci
                out["cells"] = [cell]
                flush()
                return
        st[aname] = int(base.rank()) - rankK6
        tm["ech_" + key] = round(time.time() - t0, 2)
        st["tm"] = tm
        log("sems2: %s=%d (%.1fs)" % (aname, st[aname], tm["ech_" + key]))
        save_stage(2)
        if key == "f4":
            r = int(base.rank())
            part = 10000
            for pi, b0 in enumerate(range(0, r, part)):
                Bp = base.matrix_from_rows(
                    list(range(b0, min(r, b0 + part))))
                with open(WORK / ("sem_s2_base_%02d.pkl" % pi), "wb") as f:
                    pickle.dump(Bp, f, protocol=4)
                del Bp
                gc.collect()
            st["base_parts"] = (r + part - 1) // part
            st["base_rank"] = r
            save_stage(2)
            log("sems2: base persisted in %d parts (rank %d)"
                % (st["base_parts"], r))
            if softcap_hit():
                cell["status"] = "checkpointed_before_f5"
                out["cells"] = [cell]
                flush()
                return
    del base
    gc.collect()
    with open(WORK / "sem_rankK6.json") as f:
        rk = json.load(f)["rankK6"]
    cell["closure_D6"] = {"rankK6": rankK6, "A3_6": st["A3_6"],
                          "A4_6": st["A4_6"], "A5": st["A5"],
                          "m4ri_times": tm,
                          "method": "reduction-free union rank (dense m4ri): "
                                    "rank(K6 u F)-rank(K6), single-process"}
    cell["rankK6_matches_sems1"] = bool(rankK6 == rk)
    log("sems2: rankK6=%d A3_6=%d A4_6=%d A5=%d"
        % (rankK6, st["A3_6"], st["A4_6"], st["A5"]))
    cell["status"] = "completed"
    out["cells"].append(cell)
    flush()


# ==========================================================================
# dispatch
# ==========================================================================
if args.mode == 'gate':
    run_gate()
elif args.mode == 'build2':
    run_build2()
elif args.mode == 'n1d345':
    run_n1d345()
elif args.mode == 'n1s1':
    run_n1s1()
elif args.mode == 'rank6':
    run_rank6()
elif args.mode == 'sems1':
    run_sems1()
elif args.mode == 'sems2':
    run_sems2()

out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
