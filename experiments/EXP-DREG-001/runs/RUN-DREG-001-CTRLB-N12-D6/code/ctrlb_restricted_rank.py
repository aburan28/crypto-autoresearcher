# CTRL-B column-restriction driver -- TASK-20260726-DREG-CTRLB-P1 / RUN-DREG-001-CTRLB-N12-D6.
#
# WHAT THIS COMPUTES (observations only; no interpretation):
#   The FULL-column exact GF(2) rank of the NULL degree-6 Macaulay matrix for the cell
#   n=12, t=3, ti=0, seed=2026, D=6, nb=24, RESTRICTED to the sem arm's exact column
#   support (174035 monomials), i.e. with exactly the 16016 monomials that are in the
#   null support and absent from the sem support deleted as columns. Rows are unchanged
#   (183312). Reports deficit_genuine = rank(null|_sem-support) - 138573, where 138573 is
#   the COMMITTED sem full-column rank (RUN-DREG-001-MEASURE-N12-D6/d6-sem-cont-1); the
#   sem arm is NOT recomputed or restricted here.
#
# EXPLICIT NON-USE OF sr_pred: the semi-regular predictor 156520 is support-INDEPENDENT
#   and is NOT the predictor for the restricted matrix. It is recorded for provenance
#   only. The quantity reported is rank - 138573, never sr_pred - rank.
#
# INSTRUMENT: src/h012c_block_m4ri.py (column-chunked, memory-safe block-m4ri). This
#   driver imports and calls that module's kernel unchanged (process_subchunk,
#   save_carry, load_carries, load_state, save_state, monosets_hash, file_hash); it only
#   substitutes a column-restricted view of the per-column row lists (col_rows) for the
#   full column list, and adds the identity/coverage/bracket audits this task requires.
#   The un-chunked DREG_dff.sage is NOT used anywhere.
#
# BUDGET DISCIPLINE: a wall-clock or memory cap stop is failed_infrastructure
#   (AGENTS.md rule 5). A partial rank_acc is never reported as a rank, a deficit, or a
#   bound. A rank outside the pre-registered bracket [140504, 156520] is integrity_failure
#   with no interpretation attached.
#
# Run (from repo root):
#   TMPDIR=/Volumes/Volume/sage-scratch-dreg SAGE_TMP=/Volumes/Volume/sage-scratch-dreg \
#   /usr/bin/time -l /usr/local/bin/sage -python \
#     experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/code/ctrlb_restricted_rank.py \
#     --phase all --chunk-force 12000 --wall-cap 2700 --aggregate-used 0
import sys, os, json, time, gc, pickle, hashlib, argparse, resource, platform
from array import array
from pathlib import Path
from collections import Counter

REPO = Path("/Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law")
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from h012c_block_m4ri import (monosets_hash, file_hash, process_subchunk, save_carry,
                              load_carries, load_state, save_state)
from h012_peel_rank import build_system, boolean_null, semireg_rank_pred
from macaulay_export import macaulay_rows
from ic_first_fall_fast import mono_deg

# ---------------- frozen cell + committed constants (BATCH-002 receipts) -------------
N, T, TI, SEED, D = 12, 3, 0, 2026, 6
C = {
    "sem_system_hash": "c47d17c3fd70d5d81127e8d37e21441883f720ca10187f57a3aeb47bfe3ba818",
    "null_system_hash": "f2f610730a7155933be2afe2d979c8535e1f35f5c0c5ddb246fabe717b147344",
    "null_hash_stem": "f2f610730a715593",
    "nb": 24,
    "nrows": 183312,
    "sem_ncols": 174035,
    "null_ncols": 190051,
    "support_gap": 16016,
    "sem_rank_committed": 138573,
    "null_rank_full_committed": 156520,
    "sr_pred": 156520,
}
BRACKET = (140504, 156520)                 # pre-registered, declared before execution
DEFICIT_BRACKET = (1931, 17947)

ADJ = (REPO / "experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-null/work"
            / "h012c_adj_null_n12_t3_i0_D6_s2026_f2f610730a715593.pkl")
RUN_DIR = REPO / "experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6"
SCRATCH = Path("/Volumes/Volume/sage-scratch-dreg/ctrlb-n12d6")
RESTRICTED_PKL = SCRATCH / "ctrlb_adj_null_restricted_to_sem_support_n12_D6_s2026.pkl"
STATE_DIR = SCRATCH / "state"

T_PROC0 = time.time()


def clog(msg):
    print(f"[ctrlb {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def peak_rss_bytes():
    # macOS: ru_maxrss is in BYTES.
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


class IntegrityFailure(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise IntegrityFailure(msg)


def sha256_bytes(b):
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def deg_hist(monos):
    return {str(d): c for d, c in sorted(Counter(mono_deg(m) for m in monos).items())}


# ------------------------------------------------------------------ prepare ---------
def prepare():
    """Rebuild both colidx maps, audit the restriction, and materialise the restricted
    per-column row lists. Aborts as IntegrityFailure before any rank work on mismatch."""
    t0 = time.time()
    audit = {"phase": "prepare", "cell": {"n": N, "t": T, "ti": TI, "seed": SEED,
                                          "D": D, "nb": None}}

    # -- scratch/disk safety ---------------------------------------------------------
    tmpdir, sagetmp = os.environ.get("TMPDIR", ""), os.environ.get("SAGE_TMP", "")
    need(tmpdir.rstrip("/") == "/Volumes/Volume/sage-scratch-dreg",
         f"TMPDIR must be /Volumes/Volume/sage-scratch-dreg, got {tmpdir!r}")
    need(sagetmp.rstrip("/") == "/Volumes/Volume/sage-scratch-dreg",
         f"SAGE_TMP must be /Volumes/Volume/sage-scratch-dreg, got {sagetmp!r}")
    need(Path("/Volumes/Volume/sage-scratch-dreg").is_dir(), "scratch dir missing")
    stv = os.statvfs("/Volumes/Volume/sage-scratch-dreg")
    audit["scratch"] = {"path": "/Volumes/Volume/sage-scratch-dreg",
                        "free_bytes": stv.f_bavail * stv.f_frsize,
                        "tmpdir": tmpdir, "sage_tmp": sagetmp}
    clog(f"scratch ok, free={stv.f_bavail * stv.f_frsize / 2**30:.1f} GiB")

    # -- reused committed null adjacency pickle --------------------------------------
    need(ADJ.exists(), f"missing null adjacency pickle {ADJ}")
    adj_sha = file_hash(ADJ)
    with open(ADJ, "rb") as f:
        payload = pickle.load(f)
    need(payload["which"] == "null", f"adjacency arm != null: {payload['which']!r}")
    need(payload["D"] == D, f"adjacency D != {D}: {payload['D']!r}")
    need(payload["system_hash"] == C["null_system_hash"],
         f"adjacency system_hash mismatch: {payload['system_hash']}")
    need(payload["system_hash"][:16] == C["null_hash_stem"],
         "adjacency system_hash stem != committed filename stem")
    need(ADJ.name.endswith(C["null_hash_stem"] + ".pkl"),
         "adjacency filename stem != committed stem")
    need(payload["ncols"] == C["null_ncols"], f"adjacency ncols {payload['ncols']}")
    need(payload["nrows"] == C["nrows"], f"adjacency nrows {payload['nrows']}")
    col_rows_pkl = payload["col_rows"]
    need(len(col_rows_pkl) == C["null_ncols"], "adjacency col_rows length mismatch")
    audit["reused_adjacency"] = {
        "path": str(ADJ), "sha256": adj_sha, "bytes": ADJ.stat().st_size,
        "git_tracked": False,
        "git_note": ("this .pkl is matched by .gitignore rule '*.pkl' and is therefore NOT "
                     "under version control; its content is independently re-derived and "
                     "compared column-by-column below, so the measurement does not rest on "
                     "the trustworthiness of an untracked file"),
        "embedded": {"which": payload["which"], "D": payload["D"],
                     "system_hash": payload["system_hash"],
                     "ncols": payload["ncols"], "nrows": payload["nrows"]},
        "system_hash_matches_committed": True,
        "filename_stem_matches_embedded_hash": True,
    }
    clog(f"adj pickle ok sha256={adj_sha[:16]} ncols={payload['ncols']} "
         f"nrows={payload['nrows']}")
    del payload
    gc.collect()

    # -- rebuild both systems from the committed seed --------------------------------
    sysret = build_system(N, T, TI, SEED)
    need(sysret is not None, "build_system returned None")
    rng, nb, sem_monosets, eq_degs = sysret
    null_monosets = boolean_null(sem_monosets, nb, rng)   # SAME rng state as producer
    sem_hash = monosets_hash(sem_monosets)
    null_hash = monosets_hash(null_monosets)
    need(nb == C["nb"], f"nb {nb} != {C['nb']}")
    need(sem_hash == C["sem_system_hash"], f"sem system_hash mismatch: {sem_hash}")
    need(null_hash == C["null_system_hash"], f"null system_hash mismatch: {null_hash}")
    audit["cell"]["nb"] = nb
    audit["system_hashes"] = {
        "sem": sem_hash, "sem_matches_committed": True,
        "null": null_hash, "null_matches_committed": True,
        "eq_degs_hist": {str(d): eq_degs.count(d) for d in sorted(set(eq_degs))},
    }
    pred, _HF = semireg_rank_pred(eq_degs, nb, D)
    sr_pred = int(pred[D])
    need(sr_pred == C["sr_pred"], f"sr_pred {sr_pred} != committed {C['sr_pred']}")
    audit["sr_pred_provenance_only"] = {
        "value": sr_pred, "matches_committed": True,
        "note": ("support-INDEPENDENT semi-regular predictor for the FULL 190051-column "
                 "space; it is NOT the predictor for the restricted matrix and is NEVER "
                 "subtracted from the restricted rank in this run"),
    }
    clog(f"systems rebuilt: nb={nb} sem={sem_hash[:16]} null={null_hash[:16]} "
         f"sr_pred={sr_pred} ({time.time()-t0:.1f}s)")

    # -- sem column support ----------------------------------------------------------
    rows, sem_colidx, _ = macaulay_rows(sem_monosets, nb, D)
    sem_nrows = len(rows)
    sem_cols = set(sem_colidx.keys())
    del rows, sem_colidx
    gc.collect()
    need(len(sem_cols) == C["sem_ncols"], f"sem ncols {len(sem_cols)}")
    need(sem_nrows == C["nrows"], f"sem nrows {sem_nrows}")
    clog(f"sem support built: {len(sem_cols)} cols, {sem_nrows} rows "
         f"({time.time()-t0:.1f}s)")

    # -- null column support + independent adjacency rebuild -------------------------
    null_rows, null_colidx, _ = macaulay_rows(null_monosets, nb, D)
    nrows = len(null_rows)
    need(nrows == C["nrows"], f"null nrows {nrows}")
    need(len(null_colidx) == C["null_ncols"], f"null ncols {len(null_colidx)}")
    col_rows_rebuilt = [array("I") for _ in range(len(null_colidx))]
    for ri, prod in enumerate(null_rows):
        for m in prod:
            col_rows_rebuilt[null_colidx[m]].append(ri)
    del null_rows
    gc.collect()
    nnz = sum(len(a) for a in col_rows_rebuilt)
    identical = (len(col_rows_rebuilt) == len(col_rows_pkl)
                 and all(col_rows_rebuilt[j] == col_rows_pkl[j]
                         for j in range(len(col_rows_pkl))))
    need(identical, "reused null adjacency pickle does NOT match an independent "
                    "in-process rebuild of the null degree-6 Macaulay adjacency")
    audit["reused_adjacency"]["independent_rebuild_identical"] = True
    audit["reused_adjacency"]["nnz"] = nnz
    clog(f"null support built: {len(null_colidx)} cols, nnz={nnz}; reused pickle "
         f"col_rows identical to independent rebuild ({time.time()-t0:.1f}s)")
    del col_rows_rebuilt
    gc.collect()

    null_cols = set(null_colidx.keys())

    # -- restriction audit -----------------------------------------------------------
    sem_only = sem_cols - null_cols
    deleted = null_cols - sem_cols
    kept = null_cols & sem_cols
    need(len(sem_only) == 0, f"sem support not a subset of null support: "
                             f"{len(sem_only)} sem-only monomials")
    need(kept == sem_cols, "kept set != sem support (set equality)")
    need(len(kept) == C["sem_ncols"], f"kept count {len(kept)} != {C['sem_ncols']}")
    need(len(deleted) == C["support_gap"],
         f"deleted count {len(deleted)} != {C['support_gap']}")
    need(kept | deleted == null_cols, "kept union deleted != null support")
    need(not (kept & deleted), "kept and deleted overlap")
    del_hist = deg_hist(deleted)
    need(set(del_hist.keys()) == {"6"}, f"deleted degree histogram not all 6: {del_hist}")
    need(del_hist["6"] == C["support_gap"], "deleted degree-6 count mismatch")

    kept_idx = sorted(null_colidx[m] for m in kept)
    deleted_idx = sorted(null_colidx[m] for m in deleted)
    need(len(kept_idx) == len(set(kept_idx)) == C["sem_ncols"], "kept index collision")
    need(len(deleted_idx) == len(set(deleted_idx)) == C["support_gap"],
         "deleted index collision")
    need(set(kept_idx) | set(deleted_idx) == set(range(C["null_ncols"])),
         "kept+deleted indices do not partition [0, 190051)")
    inv = {i: m for m, i in null_colidx.items()}
    need({inv[i] for i in kept_idx} == sem_cols,
         "monomials at kept indices != sem support (round-trip set equality)")
    need({inv[i] for i in deleted_idx} == deleted,
         "monomials at deleted indices != null-minus-sem (round-trip set equality)")

    audit["restriction"] = {
        "kept_columns": len(kept_idx),
        "deleted_columns": len(deleted_idx),
        "kept_equals_sem_support_exactly": True,
        "deleted_equals_null_minus_sem_exactly": True,
        "sem_subset_of_null": True,
        "sem_only_monomials": 0,
        "kept_union_deleted_equals_null_support": True,
        "kept_deleted_indices_partition_full_null_column_range": True,
        "degree_histogram_kept": deg_hist(kept),
        "degree_histogram_deleted": del_hist,
        "degree_histogram_null_support": deg_hist(null_cols),
        "min_deleted_column_index": int(deleted_idx[0]),
        "max_deleted_column_index": int(deleted_idx[-1]),
    }
    clog(f"restriction audited: keep={len(kept_idx)} delete={len(deleted_idx)} "
         f"deleted_deg_hist={del_hist} ({time.time()-t0:.1f}s)")

    del inv, null_cols, sem_cols, kept, deleted, deleted_idx, null_colidx
    gc.collect()

    # -- materialise restricted per-column row lists ---------------------------------
    kept_arr = array("I", kept_idx)
    restriction_sha = sha256_bytes(kept_arr.tobytes())
    restricted = [col_rows_pkl[j] for j in kept_idx]
    del col_rows_pkl
    gc.collect()
    rnnz = sum(len(a) for a in restricted)
    payload_out = {
        "which": "null_restricted_to_sem_support", "D": D,
        "system_hash": null_hash, "sem_system_hash": sem_hash,
        "restriction_sha256": restriction_sha, "kept_idx": kept_arr,
        "col_rows": restricted, "ncols": len(restricted), "nrows": nrows,
        "source_adj_path": str(ADJ), "source_adj_sha256": adj_sha,
    }
    SCRATCH.mkdir(parents=True, exist_ok=True)
    tmp = RESTRICTED_PKL.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        pickle.dump(payload_out, f, protocol=4)
    os.replace(tmp, RESTRICTED_PKL)
    restricted_sha = file_hash(RESTRICTED_PKL)
    audit["restricted_adjacency"] = {
        "path": str(RESTRICTED_PKL), "sha256": restricted_sha,
        "bytes": RESTRICTED_PKL.stat().st_size,
        "ncols": len(restricted), "nrows": nrows, "nnz": rnnz,
        "restriction_sha256": restriction_sha,
        "note": "outside the repository (scratch volume); not staged for commit",
    }
    audit["elapsed_s"] = round(time.time() - t0, 2)
    audit["peak_rss_bytes_so_far"] = peak_rss_bytes()
    audit["all_assertions_passed"] = True
    with open(RUN_DIR / "column-audit.json", "w") as f:
        json.dump(audit, f, indent=1)
    clog(f"restricted adjacency written {RESTRICTED_PKL} sha={restricted_sha[:16]} "
         f"nnz={rnnz}; column-audit.json written ({audit['elapsed_s']}s, "
         f"peak_rss={audit['peak_rss_bytes_so_far']/2**30:.2f} GiB)")
    return restricted, kept_arr, nrows, sem_hash, null_hash, adj_sha, restricted_sha, \
        restriction_sha, sr_pred, audit


def load_restricted():
    """Resume path: reload the restricted adjacency from scratch and re-verify identity."""
    need(RESTRICTED_PKL.exists(), f"missing restricted adjacency {RESTRICTED_PKL}")
    restricted_sha = file_hash(RESTRICTED_PKL)
    with open(RESTRICTED_PKL, "rb") as f:
        p = pickle.load(f)
    need(p["which"] == "null_restricted_to_sem_support", "restricted arm tag mismatch")
    need(p["D"] == D and p["system_hash"] == C["null_system_hash"], "restricted identity")
    need(p["sem_system_hash"] == C["sem_system_hash"], "restricted sem hash")
    need(p["ncols"] == C["sem_ncols"] and p["nrows"] == C["nrows"], "restricted dims")
    need(sha256_bytes(p["kept_idx"].tobytes()) == p["restriction_sha256"],
         "kept_idx hash mismatch")
    need(len(p["col_rows"]) == C["sem_ncols"], "restricted col_rows length")
    clog(f"restricted adjacency reloaded sha={restricted_sha[:16]} ncols={p['ncols']}")
    return (p["col_rows"], p["kept_idx"], p["nrows"], p["sem_system_hash"],
            p["system_hash"], p["source_adj_sha256"], restricted_sha,
            p["restriction_sha256"])


# ------------------------------------------------------------------- rank -----------
def rank_loop(restricted, nrows, ident, chunk_force, wall_cap, aggregate_used,
              reserve_s, max_units):
    ncols = len(restricted)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    st = load_state(STATE_DIR)
    if st is None:
        st = dict(ident)
        st.update({"nrows": nrows, "ncols": ncols, "next_col": 0, "rank_acc": 0,
                   "carries": [], "done": False, "rate_mat": 2.0e12,
                   "secs_total": 0.0, "units": [], "chunk_force": chunk_force,
                   "invocations": []})
        save_state(STATE_DIR, st)
        clog(f"init restricted rank: nrows={nrows} ncols={ncols} "
             f"chunk_force={chunk_force}")
    else:
        for k, v in ident.items():
            need(st.get(k) == v, f"resume identity mismatch for {k}: "
                                 f"{st.get(k)!r} != {v!r}")
        need(st["nrows"] == nrows and st["ncols"] == ncols, "resume dims mismatch")
        clog(f"RESUME at col {st['next_col']} rank_acc={st['rank_acc']} "
             f"(identity check passed)")
    st["invocations"].append({"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                           time.gmtime()),
                              "aggregate_used_s_at_start": aggregate_used,
                              "resume": st["next_col"] > 0})
    save_state(STATE_DIR, st)

    if st["done"]:
        clog(f"already DONE rank={st['rank_acc']}")
        return st, "already_done"

    carries = load_carries(STATE_DIR, st)
    clog(f"loaded {len(carries)} carrier blocks (all checkpoint hashes verified)")
    covlog = open(RUN_DIR / "chunk-coverage.log", "a")
    covlog.write(f"# invocation start utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
                 f"next_col={st['next_col']} rank_acc={st['rank_acc']} "
                 f"ncols={ncols} chunk_force={chunk_force}\n")
    covlog.flush()

    stop_reason = "completed"
    last_unit_wall = None
    while st["next_col"] < ncols:
        elapsed_agg = aggregate_used + (time.time() - T_PROC0)
        est = last_unit_wall if last_unit_wall else 200.0
        if elapsed_agg + est + reserve_s > wall_cap:
            stop_reason = "wall_cap"
            clog(f"STOP wall cap: aggregate_used+elapsed={elapsed_agg:.1f}s "
                 f"+ est_unit={est:.1f}s + reserve={reserve_s}s > cap={wall_cap}s")
            break
        if max_units and len(st["units"]) >= max_units:
            stop_reason = "max_units"
            break
        c = chunk_force if chunk_force else 12000
        c = min(c, ncols - st["next_col"])
        j0, j1 = st["next_col"], st["next_col"] + c
        u_t0 = time.time()
        k, P_new, H_new, tm = process_subchunk(restricted, j0, j1, nrows, carries, st)
        unit_secs = sum(tm[k2] for k2 in ("fill", "tr1", "reduce", "ech", "post"))
        if st["rank_acc"] > 0 and tm["reduce"] > 1.0:
            meas = nrows * st["rank_acc"] * tm["c"] * 0.7 / tm["reduce"]
            st["rate_mat"] = 0.5 * st["rate_mat"] + 0.5 * meas
        if k:
            entries = save_carry(STATE_DIR, len(st["carries"]), P_new, H_new)
            carries.append((P_new, H_new))
            st["carries"].extend(entries)
            del H_new
        st["rank_acc"] += k
        st["next_col"] = j1
        st["secs_total"] += unit_secs
        last_unit_wall = time.time() - u_t0
        st["units"].append({"j0": j0, "j1": j1, "c": c, "k": k,
                            "rank_acc": st["rank_acc"],
                            "unit_wall_s": round(last_unit_wall, 2),
                            "tm": {k2: round(v, 2) for k2, v in tm.items()}})
        save_state(STATE_DIR, st)
        covlog.write(json.dumps(st["units"][-1]) + "\n")
        covlog.flush()
        clog(f"cols {j0}..{j1} k={k} rank={st['rank_acc']} fill={tm['fill']:.1f} "
             f"red={tm['reduce']:.1f} ech={tm['ech']:.1f} post={tm['post']:.1f} "
             f"unit_wall={last_unit_wall:.1f} agg={aggregate_used + time.time()-T_PROC0:.0f}s")
        gc.collect()

    if st["next_col"] >= ncols:
        st["done"] = True
        save_state(STATE_DIR, st)
    covlog.write(f"# invocation end utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
                 f"next_col={st['next_col']} rank_acc={st['rank_acc']} "
                 f"done={st['done']} stop_reason={stop_reason}\n")
    covlog.close()
    return st, stop_reason


def coverage_audit(st, ncols):
    """Exact-once coverage of [0, ncols) by the chunk log."""
    units = st["units"]
    ok, problems = True, []
    cursor = 0
    total = 0
    for u in units:
        if u["j0"] != cursor:
            ok = False
            problems.append(f"gap/overlap: expected j0={cursor}, got {u['j0']}")
        if u["j1"] <= u["j0"]:
            ok = False
            problems.append(f"non-positive chunk at {u['j0']}")
        cursor = u["j1"]
        total += u["j1"] - u["j0"]
    if cursor != ncols:
        ok = False
        problems.append(f"final cursor {cursor} != ncols {ncols}")
    if total != ncols:
        ok = False
        problems.append(f"summed chunk widths {total} != ncols {ncols}")
    k_sum = sum(u["k"] for u in units)
    if k_sum != st["rank_acc"]:
        ok = False
        problems.append(f"sum of per-chunk new pivots {k_sum} != rank_acc "
                        f"{st['rank_acc']}")
    npiv = sum(e["npiv"] for e in st["carries"])
    if npiv != st["rank_acc"]:
        ok = False
        problems.append(f"carrier pivot total {npiv} != rank_acc {st['rank_acc']}")
    return {
        "covers_range_exactly_once": ok,
        "problems": problems,
        "n_units": len(units),
        "first_column": units[0]["j0"] if units else None,
        "last_column_exclusive": cursor,
        "summed_chunk_widths": total,
        "sum_of_new_pivots": k_sum,
        "carrier_pivot_total": npiv,
        "n_resumes": max(0, len(st.get("invocations", [])) - 1),
        "all_carrier_checkpoint_hashes_verified": True,
        "chunks": [{"j0": u["j0"], "j1": u["j1"], "k": u["k"],
                    "rank_acc": u["rank_acc"]} for u in units],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("prepare", "rank", "all"), default="all")
    ap.add_argument("--chunk-force", type=int, default=12000)
    ap.add_argument("--wall-cap", type=float, default=2700.0,
                    help="AGGREGATE task wall cap in seconds (all invocations)")
    ap.add_argument("--aggregate-used", type=float, default=0.0,
                    help="wall seconds already consumed by earlier invocations")
    ap.add_argument("--reserve", type=float, default=90.0)
    ap.add_argument("--max-units", type=int, default=0)
    args = ap.parse_args()

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    clog(f"start phase={args.phase} chunk_force={args.chunk_force} "
         f"wall_cap={args.wall_cap} aggregate_used={args.aggregate_used}")
    status = "unset"
    out = {}
    try:
        if args.phase in ("prepare", "all") and not RESTRICTED_PKL.exists():
            (restricted, kept_arr, nrows, sem_hash, null_hash, adj_sha,
             restricted_sha, restriction_sha, sr_pred, audit) = prepare()
        else:
            (restricted, kept_arr, nrows, sem_hash, null_hash, adj_sha,
             restricted_sha, restriction_sha) = load_restricted()
            sr_pred = C["sr_pred"]
        prepare_done_s = time.time() - T_PROC0
        if args.phase == "prepare":
            clog(f"prepare-only complete in {prepare_done_s:.1f}s")
            return 0

        ident = {"n": N, "t": T, "ti": TI, "d": D, "seed": SEED,
                 "which": "null_restricted_to_sem_support", "nb": C["nb"],
                 "system_hash": null_hash, "sem_system_hash": sem_hash,
                 "restriction_sha256": restriction_sha,
                 "restricted_adj_sha256": restricted_sha,
                 "source_adj_sha256": adj_sha}
        st, stop_reason = rank_loop(restricted, nrows, ident, args.chunk_force,
                                    args.wall_cap, args.aggregate_used, args.reserve,
                                    args.max_units)
        ncols = C["sem_ncols"]
        wall_this = time.time() - T_PROC0
        cov = coverage_audit(st, ncols) if st["done"] else None

        out = {
            "schema": ("RUN-DREG-001-CTRLB-N12-D6 raw result -- observations only; "
                       "no interpretation, no hypothesis-status language"),
            "experiment_id": "EXP-DREG-001",
            "run_id": "RUN-DREG-001-CTRLB-N12-D6",
            "task": "TASK-20260726-DREG-CTRLB-P1",
            "goal": "GOAL-DREG-001 BATCH-003",
            "cell": {"n": N, "t": T, "ti": TI, "seed": SEED, "D": D, "nb": C["nb"]},
            "arm": "null_restricted_to_sem_support",
            "nrows": nrows,
            "ncols_restricted": ncols,
            "ncols_deleted": C["support_gap"],
            "ncols_null_full": C["null_ncols"],
            "sem_rank_committed": C["sem_rank_committed"],
            "null_rank_full_committed": C["null_rank_full_committed"],
            "sr_pred": C["sr_pred"],
            "sr_pred_note": ("support-INDEPENDENT; NOT the semi-regular predictor for the "
                             "restricted column space; recorded for provenance only and "
                             "never subtracted from the restricted rank"),
            "certificate_kind": "none",
            "certificate_reason": ("pure exact GF(2) rank measurement; no discrete-log "
                                   "solve and no factor-base relation is claimed"),
            "system_hashes": {"null": null_hash, "sem": sem_hash},
            "source_adj_sha256": adj_sha,
            "restricted_adj_sha256": restricted_sha,
            "restriction_sha256": restriction_sha,
            "preregistered_bracket": {"restricted_null_rank": list(BRACKET),
                                      "deficit_genuine": list(DEFICIT_BRACKET),
                                      "declared_before_execution": True},
            "chunk_force": args.chunk_force,
            "secs_total": round(st["secs_total"], 1),
            "n_units": len(st["units"]),
            "wall_seconds_this_invocation": round(wall_this, 2),
            "wall_seconds_aggregate": round(args.aggregate_used + wall_this, 2),
            "prepare_seconds": round(prepare_done_s, 2),
            "peak_rss_bytes": peak_rss_bytes(),
            "peak_rss_source": "resource.getrusage(RUSAGE_SELF).ru_maxrss (bytes, macOS)",
            "stop_reason": stop_reason,
        }

        if st["done"]:
            rank = int(st["rank_acc"])
            need(cov["covers_range_exactly_once"],
                 f"chunk coverage audit failed: {cov['problems']}")
            in_bracket = BRACKET[0] <= rank <= BRACKET[1]
            deficit = rank - C["sem_rank_committed"]
            out.update({
                "rank_null_restricted": rank,
                "deficit_genuine": deficit,
                "deficit_genuine_formula": "rank(null|_sem-support) - 138573",
                "in_preregistered_bracket": bool(in_bracket),
                "chunk_coverage": cov,
                "status": "completed_valid" if in_bracket else "integrity_failure",
            })
            if not in_bracket:
                out["integrity_failure_reason"] = (
                    f"rank {rank} outside pre-registered bracket "
                    f"[{BRACKET[0]}, {BRACKET[1]}]; per the frozen contract this "
                    f"falsifies the instrument or the committed BATCH-002 receipts and "
                    f"is NOT a mathematical finding. No interpretation attached.")
            status = out["status"]
        else:
            out.update({
                "rank_null_restricted": None,
                "deficit_genuine": None,
                "in_preregistered_bracket": None,
                "status": "failed_infrastructure",
                "failure_class": "resource_exhaustion",
                "cap_hit": ("aggregate wall-clock cap "
                            f"{args.wall_cap}s" if stop_reason == "wall_cap"
                           else stop_reason),
                "last_completed_column_exclusive": int(st["next_col"]),
                "partial_rank_acc": int(st["rank_acc"]),
                "partial_rank_acc_note": ("NOT a rank, NOT a bound, NOT evidence "
                                          "(AGENTS.md rule 5); reported only to make the "
                                          "resume point auditable"),
                "resume_state_path": str(STATE_DIR / "state.json"),
                "restricted_adj_path": str(RESTRICTED_PKL),
                "chunk_coverage_partial": {
                    "n_units": len(st["units"]),
                    "covered_range": [0, int(st["next_col"])],
                    "chunks": [{"j0": u["j0"], "j1": u["j1"], "k": u["k"],
                                "rank_acc": u["rank_acc"]} for u in st["units"]],
                },
            })
            status = "failed_infrastructure"
    except IntegrityFailure as e:
        status = "integrity_failure"
        out = {"experiment_id": "EXP-DREG-001", "run_id": "RUN-DREG-001-CTRLB-N12-D6",
               "task": "TASK-20260726-DREG-CTRLB-P1", "status": "integrity_failure",
               "integrity_failure_reason": str(e),
               "certificate_kind": "none",
               "wall_seconds_this_invocation": round(time.time() - T_PROC0, 2),
               "peak_rss_bytes": peak_rss_bytes(),
               "note": ("aborted before/at an identity or restriction check; no rank is "
                        "reported and no interpretation is attached")}
        clog(f"INTEGRITY FAILURE: {e}")

    out["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(RUN_DIR / "raw-result.json", "w") as f:
        json.dump(out, f, indent=1)
    clog(f"status={status} -> {RUN_DIR / 'raw-result.json'}")
    if status == "completed_valid":
        clog(f"RESULT rank(null|_sem-support)={out['rank_null_restricted']} "
             f"deficit_genuine={out['deficit_genuine']} "
             f"in_bracket={out['in_preregistered_bracket']} "
             f"units={out['n_units']} secs_total={out['secs_total']} "
             f"peak_rss={out['peak_rss_bytes']}")
    return 0 if status == "completed_valid" else 1


if __name__ == "__main__":
    sys.exit(main())
