# H012c -- checkpointable block-m4ri exact rank for degree-D Macaulay matrices.
#
# Problem: single-call m4ri echelonize tops out ~n=15 (nrows x ncols too big)
# and Bash calls are capped at ~280 s. This engine computes the EXACT rank of
# the sem system (columns = monomials, rows = Macaulay polys) in column
# sub-chunks, carrying a block-staircase basis of the column space across
# processes via pickles. Never merges the global basis: rank = sum of per
# sub-chunk new pivots (exact quotient argument).
#
# Math (all over GF(2)):
#   carriers = list of (P, H): H is nrows x k, columns are rref basis vectors
#   of the processed column space, P = pivot coords (H[P[j], i] = delta_ij),
#   and H rows at all EARLIER carriers' pivots are 0 (staircase property).
#   Sub-chunk B (nrows x c, raw columns of M): Y = B.rows(P); B += H*Y zeroes
#   B at P. After all carriers: rref(B^T) rows with pivots P_new (disjoint
#   from all old P) become the next carrier. rank_acc += k.
#
# State per run dir results/h012c_{tag}_sem_n{n}_t{ti}/:
#   state.json + carry_XXX.pkl. Restart-safe: resume re-runs nothing finished.
#
# Validation gates: n=12 sem D5 ti0 -> 28096 ; n=18 sem D5 ti0 -> 143882.
#
# Run: sage -python src/h012c_blockm4ri.py --n-list 18 --targets 1 --d 5 \
#        --tag _n18v --budget 230
import sys, os, time, json, gc, pickle, argparse, hashlib
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sage.all import GF, matrix
from h012_peel_rank import build_system, semireg_rank_pred, boolean_null
from macaulay_export import macaulay_rows

F2 = GF(2)
RES = Path(__file__).parent.parent / "results"


def log(msg):
    print(f"[h012c {time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------- adjacency (per-column row lists) ----------

def monosets_hash(monosets):
    """Hash the ordered Boolean generators without relying on pickle bytes."""
    h = hashlib.sha256()
    for f in monosets:
        encoded = sorted(tuple(sorted(int(v) for v in m)) for m in f)
        h.update(len(encoded).to_bytes(8, "big"))
        for mono in encoded:
            h.update(len(mono).to_bytes(4, "big"))
            for v in mono:
                h.update(v.to_bytes(4, "big"))
    return h.hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def adj_path(which, n, t, ti, D, seed, system_hash):
    return RES / (f"h012c_adj_{which}_n{n}_t{t}_i{ti}_D{D}_s{seed}_"
                  f"{system_hash[:16]}.pkl")


def get_adj(which, n, t, ti, D, seed, system_hash, monosets, nb):
    p = adj_path(which, n, t, ti, D, seed, system_hash)
    if p.exists():
        with open(p, "rb") as f:
            payload = pickle.load(f)
        assert payload["system_hash"] == system_hash
        assert payload["which"] == which and payload["D"] == D
        col_rows = payload["col_rows"]
        ncols, nrows = payload["ncols"], payload["nrows"]
        log(f"adj loaded {which} n={n} ti={ti}: ncols={ncols} nrows={nrows}")
        return col_rows, ncols, nrows
    if monosets is None or nb is None:
        raise RuntimeError(f"missing identity-bound adjacency cache: {p}")
    t0 = time.time()
    rows, colidx, _ = macaulay_rows(monosets, nb, D)
    nrows = len(rows)
    ncols = len(colidx)
    col_rows = [array("I") for _ in range(ncols)]
    for ri, prod in enumerate(rows):
        for m in prod:
            col_rows[colidx[m]].append(ri)
    rows = None
    gc.collect()
    with open(p, "wb") as f:
        pickle.dump({"which": which, "D": D, "system_hash": system_hash,
                     "col_rows": col_rows, "ncols": ncols, "nrows": nrows},
                    f, protocol=4)
    log(f"adj built {which} n={n} ti={ti}: ncols={ncols} nrows={nrows} "
        f"in {time.time()-t0:.1f}s")
    return col_rows, ncols, nrows


# ---------- state ----------

def run_dir(tag, which, n, ti):
    d = RES / f"h012c_{tag}_{which}_n{n}_t{ti}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_state(d):
    sp = d / "state.json"
    if sp.exists():
        with open(sp) as f:
            return json.load(f)
    return None


def save_state(d, st):
    sp = d / "state.json"
    with open(sp.with_suffix(".tmp"), "w") as f:
        json.dump(st, f)
    os.replace(sp.with_suffix(".tmp"), sp)


# ---------- carries ----------

def load_carries(d, st):
    """Load identity-checked carrier blocks in their saved staircase order."""
    out = []
    for c in st["carries"]:
        p = d / c["file"]
        if file_hash(p) != c["sha256"]:
            raise RuntimeError(f"checkpoint hash mismatch: {p}")
        with open(p, "rb") as f:
            P_block, H_block = pickle.load(f)
        out.append((P_block, H_block))
    return out


def save_carry(d, idx, P, H):
    """Stream H blocks to separate files, avoiding a second full H in memory."""
    nrows, k = H.dimensions()
    blk = max(1000, int(1.9e9) // nrows)
    entries = []
    for b0 in range(0, k, blk):
        b1 = min(k, b0 + blk)
        Hb = H.matrix_from_columns(list(range(b0, b1)))
        fn = f"carry_{idx:03d}_{b0 // blk:03d}.pkl"
        tmp = d / (fn + ".tmp")
        final = d / fn
        with open(tmp, "wb") as f:
            pickle.dump((P[b0:b1], Hb), f, protocol=4)
        os.replace(tmp, final)
        entries.append({"file": fn, "npiv": b1 - b0,
                        "sha256": file_hash(final)})
        del Hb
        gc.collect()
    return entries


# ---------- one sub-chunk ----------

def process_subchunk(col_rows, j0, j1, nrows, carries, st):
    """Returns (k_new, P_new, H_new, timing dict)."""
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
    # M4RI places all nonzero echelon rows first.  Restricting the scan to the
    # cached rank is exact and avoids touching thousands of trailing zero rows.
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
        # rref sanity on up to 256 sampled pairs
        import random as _r
        rr = _r.Random(1)
        for _ in range(min(256, k * k)):
            i, j = rr.randrange(k), rr.randrange(k)
            assert int(H_new[P_new[j], i]) == (1 if i == j else 0), "NOT RREF"
    del Bc
    gc.collect()
    tm["post"] = time.time() - t0
    tm["c"] = c
    return k, P_new, H_new, tm


# ---------- main loop ----------

def run_ti(n, t, ti, D, seed, tag, budget, max_units, chunk_force=0,
           which="sem"):
    if which not in ("sem", "null"):
        raise ValueError(f"unsupported system arm: {which}")
    d = run_dir(tag, which, n, ti)
    st = load_state(d)
    if st is None:
        sysret = build_system(n, t, ti, seed)
        if sysret is None:
            log(f"n={n} ti={ti}: build_system failed")
            return
        rng, nb, sem_monosets, eq_degs = sysret
        monosets = (sem_monosets if which == "sem"
                    else boolean_null(sem_monosets, nb, rng))
        system_hash = monosets_hash(monosets)
        pred, HF = semireg_rank_pred(eq_degs, nb, D)
        col_rows, ncols, nrows = get_adj(which, n, t, ti, D, seed,
                                         system_hash, monosets, nb)
        st = {"n": n, "t": t, "ti": ti, "d": D, "seed": seed,
              "which": which, "system_hash": system_hash, "nb": nb,
              "nrows": nrows, "ncols": ncols, "pred": int(pred[D]),
              "next_col": 0, "rank_acc": 0, "carries": [], "done": False,
              "rate_mat": 2.0e12, "secs_total": 0.0, "units": []}
        save_state(d, st)
        log(f"init {which} n={n} ti={ti}: nb={nb} nrows={nrows} "
            f"ncols={ncols} pred={st['pred']} hash={system_hash[:16]}")
    else:
        expected = {"n": n, "t": t, "ti": ti, "d": D, "seed": seed,
                    "which": which}
        for key, value in expected.items():
            if st.get(key) != value:
                raise RuntimeError(f"resume identity mismatch for {key}: "
                                   f"{st.get(key)!r} != {value!r}")
        col_rows, ncols, nrows = get_adj(which, n, t, ti, D, seed,
                                         st["system_hash"], None, None)
        assert ncols == st["ncols"] and nrows == st["nrows"]

    if st["done"]:
        log(f"n={n} ti={ti} already DONE rank={st['rank_acc']}")
        return

    carries = load_carries(d, st)
    t_start = time.time()
    units = 0

    while st["next_col"] < st["ncols"]:
        if units > 0 and (time.time() - t_start) > budget:
            break
        if max_units and units >= max_units:
            break
        # adaptive chunk size: target ~110 s of reduce work
        rank = max(st["rank_acc"], 2000)
        c = int(110.0 * st["rate_mat"] / (st["nrows"] * rank * 0.7))
        c = max(4000, min(24000, c, st["ncols"] - st["next_col"]))
        if chunk_force:
            c = min(chunk_force, st["ncols"] - st["next_col"])
        j0, j1 = st["next_col"], st["next_col"] + c

        k, P_new, H_new, tm = process_subchunk(col_rows, j0, j1, st["nrows"],
                                               carries, st)
        unit_secs = sum(tm[k2] for k2 in ("fill", "tr1", "reduce", "ech", "post"))
        # calibrate matmul rate from reduce phase (only when meaningful)
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
        save_state(d, st)
        units += 1
        eta = ""
        if st["units"]:
            avg = st["secs_total"] / len(st["units"])
            eta = f" eta~{(st['ncols']-j1)/max(c,1)*avg/60:.0f}min-work"
        log(f"n={n} ti={ti} cols {j0}..{j1} k={k} rank={st['rank_acc']}"
            f" fill={tm['fill']:.1f} red={tm['reduce']:.1f} ech={tm['ech']:.1f}"
            f" post={tm['post']:.1f}{eta}")
        gc.collect()

    if st["next_col"] >= st["ncols"]:
        st["done"] = True
        save_state(d, st)
        res = {"status": "completed_valid", "which": which,
               "n": n, "ti": ti, "d": st["d"], "nb": st["nb"],
               "nrows": st["nrows"], "ncols": st["ncols"], "pred": st["pred"],
               "rank": st["rank_acc"], "deficit": st["pred"] - st["rank_acc"],
               "secs_total": round(st["secs_total"], 1),
               "n_units": len(st["units"]), "system_hash": st["system_hash"],
               "completed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                   time.gmtime())}
        rp = RES / f"h012c_{tag}_{which}_result_n{n}_t{ti}.json"
        with open(rp, "w") as f:
            json.dump(res, f, indent=1)
        log(f"DONE n={n} ti={ti}: rank={res['rank']} pred={res['pred']}"
            f" deficit={res['deficit']} -> {rp}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-list", default="12")
    ap.add_argument("--t", type=int, default=3)
    ap.add_argument("--targets", type=int, default=1)
    ap.add_argument("--d", type=int, default=5)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--tag", default="x")
    ap.add_argument("--budget", type=float, default=230.0)
    ap.add_argument("--max-units", type=int, default=0)
    ap.add_argument("--chunk-force", type=int, default=0)
    ap.add_argument("--which", choices=("sem", "null"), default="sem")
    ap.add_argument("--results-dir", default="")
    args = ap.parse_args()
    global RES
    if args.results_dir:
        RES = Path(args.results_dir).resolve()
        RES.mkdir(parents=True, exist_ok=True)
    for n in [int(x) for x in args.n_list.split(",")]:
        for ti in range(args.targets):
            run_ti(n, args.t, ti, args.d, args.seed, args.tag,
                   args.budget, args.max_units, args.chunk_force, args.which)


if __name__ == "__main__":
    main()
