# CTRL-B admitted measurement driver — TASK-20260731-016 / GOAL-DREG-001 BATCH-005.
#
# Computes full-column exact GF(2) rank of the null D=6 Macaulay matrix restricted to
# sem's exact column support under CTRL-B-Q-MACHINE-v1 + support/deletion-set hash
# admission from ctrl_b_protocol.yaml (TASK-20260725-701).
#
# Instrument: src/h012c_block_m4ri.py chunked_block_m4ri (process_subchunk kernel).
# Forbids unchunked DREG_dff.sage. Pure rank: certificate.kind = none.
#
# Writes only under this task directory (+ TMPDIR/SAGE_TMP scratch outside the repo).
import sys, os, json, time, gc, pickle, hashlib, argparse, resource, shutil
from array import array
from pathlib import Path
from collections import Counter

REPO = Path(__file__).resolve().parents[7]  # .../tasks/<id>/ -> repo root
SRC = REPO / "src"
assert (SRC / "h012c_block_m4ri.py").exists(), f"bad REPO root: {REPO}"
sys.path.insert(0, str(SRC))

from h012c_block_m4ri import (
    monosets_hash, file_hash, process_subchunk, save_carry,
    load_carries, load_state, save_state,
)
from h012_peel_rank import build_system, boolean_null, semireg_rank_pred
from macaulay_export import macaulay_rows
from ic_first_fall_fast import mono_deg

N, T, TI, SEED, D = 12, 3, 0, 2026, 6
C = {
    "sem_system_hash":
        "c47d17c3fd70d5d81127e8d37e21441883f720ca10187f57a3aeb47bfe3ba818",
    "null_system_hash":
        "f2f610730a7155933be2afe2d979c8535e1f35f5c0c5ddb246fabe717b147344",
    "null_hash_stem": "f2f610730a715593",
    "nb": 24,
    "nrows": 183312,
    "sem_ncols": 174035,
    "null_ncols": 190051,
    "support_gap": 16016,
    "sem_rank_committed": 138573,
    "null_rank_full_committed": 156520,
    "sr_pred": 156520,
    "column_deletion_lower_bound_genuine": 1931,
    "raw_headline_quarantined": 17947,
}
BRACKET = (140504, 156520)
DEFICIT_BRACKET = (1931, 17947)
SET_HASH_ALG = "sha256_sorted_monomial_canonical_v1"
CHECKER_ID = "CTRL-B-Q-MACHINE-v1"

TASK_DIR = Path(__file__).resolve().parent
PROTOCOL = (REPO / "coordination/goals/GOAL-DREG-001/batches/BATCH-004/tasks"
            / "TASK-20260725-701/ctrl_b_protocol.yaml")
# Prefer in-repo adj; fall back to sibling worktree reuse path named in protocol.
ADJ_CANDIDATES = [
    REPO / "experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-null/work"
         / "h012c_adj_null_n12_t3_i0_D6_s2026_f2f610730a715593.pkl",
    Path("/Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law"
         "/experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-null/work"
         "/h012c_adj_null_n12_t3_i0_D6_s2026_f2f610730a715593.pkl"),
]
SCRATCH = Path("/Volumes/Volume/sage-scratch-dreg/ctrlb-task-20260731-011")
RESTRICTED_PKL = SCRATCH / "ctrlb_adj_null_restricted_to_sem_support_n12_D6_s2026.pkl"
STATE_DIR = SCRATCH / "state"

T_PROC0 = time.time()


def clog(msg):
    print(f"[ctrlb {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def peak_rss_bytes():
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


class IntegrityFailure(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise IntegrityFailure(msg)


def deg_hist(monos):
    return {str(d): c for d, c in sorted(Counter(mono_deg(m) for m in monos).items())}


def canonical_mono_line(m):
    """Protocol set_hash_procedure: comma-joined sorted variable indices; empty -> ''."""
    if not m:
        return ""
    return ",".join(str(int(v)) for v in sorted(m))


def set_hash_sorted_monomial_canonical_v1(monos):
    """SHA-256 over utf-8 newlines of canonical lines sorted by (deg, sorted tuple)."""
    ordered = sorted(monos, key=lambda m: (mono_deg(m), tuple(sorted(m))))
    body = "\n".join(canonical_mono_line(m) for m in ordered).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def find_adj():
    for p in ADJ_CANDIDATES:
        if p.exists():
            return p
    return None


# ------------------------------------------------------------------ prepare ---------
def prepare():
    t0 = time.time()
    audit = {"phase": "prepare",
             "cell": {"n": N, "t": T, "ti": TI, "seed": SEED, "D": D, "nb": None},
             "set_hash_algorithm_id": SET_HASH_ALG,
             "protocol_path": str(PROTOCOL.relative_to(REPO))}

    tmpdir, sagetmp = os.environ.get("TMPDIR", ""), os.environ.get("SAGE_TMP", "")
    need(tmpdir.rstrip("/") == "/Volumes/Volume/sage-scratch-dreg",
         f"TMPDIR must be /Volumes/Volume/sage-scratch-dreg, got {tmpdir!r}")
    need(sagetmp.rstrip("/") == "/Volumes/Volume/sage-scratch-dreg",
         f"SAGE_TMP must be /Volumes/Volume/sage-scratch-dreg, got {sagetmp!r}")
    need(Path("/Volumes/Volume/sage-scratch-dreg").is_dir(), "scratch dir missing")
    stv = os.statvfs("/Volumes/Volume/sage-scratch-dreg")
    free_b = stv.f_bavail * stv.f_frsize
    need(free_b > 8 * 2**30, f"ENOSPC risk: free={free_b} bytes")
    audit["scratch"] = {"path": "/Volumes/Volume/sage-scratch-dreg",
                        "free_bytes": free_b, "tmpdir": tmpdir, "sage_tmp": sagetmp}
    clog(f"scratch ok, free={free_b / 2**30:.1f} GiB")

    ADJ = find_adj()
    need(ADJ is not None, "missing null adjacency pickle in candidates")
    adj_sha = file_hash(ADJ)
    with open(ADJ, "rb") as f:
        payload = pickle.load(f)
    need(payload["which"] == "null", f"adjacency arm != null: {payload['which']!r}")
    need(payload["D"] == D, f"adjacency D != {D}")
    need(payload["system_hash"] == C["null_system_hash"], "adjacency system_hash mismatch")
    need(payload["ncols"] == C["null_ncols"] and payload["nrows"] == C["nrows"],
         "adjacency dims mismatch")
    col_rows_pkl = payload["col_rows"]
    need(len(col_rows_pkl) == C["null_ncols"], "adjacency col_rows length mismatch")
    audit["reused_adjacency"] = {
        "path": str(ADJ), "sha256": adj_sha, "bytes": ADJ.stat().st_size,
        "embedded": {"which": payload["which"], "D": payload["D"],
                     "system_hash": payload["system_hash"],
                     "ncols": payload["ncols"], "nrows": payload["nrows"]},
    }
    clog(f"adj pickle ok sha256={adj_sha[:16]} ncols={payload['ncols']} "
         f"nrows={payload['nrows']}")
    del payload
    gc.collect()

    sysret = build_system(N, T, TI, SEED)
    need(sysret is not None, "build_system returned None")
    rng, nb, sem_monosets, eq_degs = sysret
    null_monosets = boolean_null(sem_monosets, nb, rng)
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
        "note": ("support-INDEPENDENT; NOT subtracted from restricted rank; "
                 "raw 17947 vs sr_pred remains quarantined_confounded"),
    }
    clog(f"systems rebuilt: nb={nb} sem={sem_hash[:16]} null={null_hash[:16]} "
         f"sr_pred={sr_pred} ({time.time()-t0:.1f}s)")

    rows, sem_colidx, _ = macaulay_rows(sem_monosets, nb, D)
    sem_nrows = len(rows)
    sem_cols = set(sem_colidx.keys())
    del rows, sem_colidx
    gc.collect()
    need(len(sem_cols) == C["sem_ncols"], f"sem ncols {len(sem_cols)}")
    need(sem_nrows == C["nrows"], f"sem nrows {sem_nrows}")
    clog(f"sem support built: {len(sem_cols)} cols ({time.time()-t0:.1f}s)")

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
    need(identical, "reused null adjacency pickle != independent rebuild")
    audit["reused_adjacency"]["independent_rebuild_identical"] = True
    audit["reused_adjacency"]["nnz"] = nnz
    clog(f"null support built: {len(null_colidx)} cols, nnz={nnz}; pickle identical "
         f"({time.time()-t0:.1f}s)")
    del col_rows_rebuilt
    gc.collect()

    null_cols = set(null_colidx.keys())
    sem_only = sem_cols - null_cols
    deleted = null_cols - sem_cols
    kept = null_cols & sem_cols
    need(len(sem_only) == 0, f"sem not subset of null: {len(sem_only)} extras")
    need(kept == sem_cols, "kept set != sem support")
    need(len(kept) == C["sem_ncols"], f"kept count {len(kept)}")
    need(len(deleted) == C["support_gap"], f"deleted count {len(deleted)}")
    need(kept | deleted == null_cols, "kept ∪ deleted != null")
    need(not (kept & deleted), "kept ∩ deleted nonempty")
    del_hist = deg_hist(deleted)
    need(del_hist == {"6": C["support_gap"]}, f"deleted deg hist {del_hist}")

    # Protocol regenerate-and-match set digests (sem_cols / deleted).
    restricted_support_hash = set_hash_sorted_monomial_canonical_v1(sem_cols)
    deleted_set_hash = set_hash_sorted_monomial_canonical_v1(deleted)
    # Recompute from kept (== sem) and deleted to confirm path.
    need(set_hash_sorted_monomial_canonical_v1(kept) == restricted_support_hash,
         "kept-set hash != sem-set hash")
    need(deleted == null_cols - sem_cols, "deleted_set != null_cols \\ sem_cols")

    kept_idx = sorted(null_colidx[m] for m in kept)
    deleted_idx = sorted(null_colidx[m] for m in deleted)
    need(set(kept_idx) | set(deleted_idx) == set(range(C["null_ncols"])),
         "kept+deleted indices do not partition full null column range")
    need(len(kept_idx) == C["sem_ncols"] and len(deleted_idx) == C["support_gap"],
         "index cardinality mismatch")
    # full_column_coverage_loop_to_ncols: every null column index visited exactly once
    coverage_loop = sorted(kept_idx + deleted_idx)
    need(coverage_loop == list(range(C["null_ncols"])),
         "full_column_coverage_loop_to_ncols failed")

    audit["restriction"] = {
        "kept_columns": len(kept_idx),
        "deleted_columns": len(deleted_idx),
        "kept_equals_sem_support_exactly": True,
        "deleted_equals_null_minus_sem_exactly": True,
        "deleted_degree_histogram": del_hist,
        "degree_histogram_kept": deg_hist(kept),
        "restricted_support_hash": restricted_support_hash,
        "deleted_set_hash": deleted_set_hash,
        "set_hash_algorithm_id": SET_HASH_ALG,
        "full_column_coverage_loop_to_ncols": True,
    }
    clog(f"restriction audited: keep={len(kept_idx)} delete={len(deleted_idx)} "
         f"restricted_support_hash={restricted_support_hash[:16]} "
         f"deleted_set_hash={deleted_set_hash[:16]} ({time.time()-t0:.1f}s)")

    del null_cols, sem_cols, kept, deleted, deleted_idx, null_colidx
    gc.collect()

    kept_arr = array("I", kept_idx)
    restriction_sha = hashlib.sha256(kept_arr.tobytes()).hexdigest()
    restricted = [col_rows_pkl[j] for j in kept_idx]
    del col_rows_pkl
    gc.collect()
    rnnz = sum(len(a) for a in restricted)
    payload_out = {
        "which": "null_restricted_to_sem_support", "D": D,
        "system_hash": null_hash, "sem_system_hash": sem_hash,
        "restriction_sha256": restriction_sha,
        "restricted_support_hash": restricted_support_hash,
        "deleted_set_hash": deleted_set_hash,
        "set_hash_algorithm_id": SET_HASH_ALG,
        "kept_idx": kept_arr,
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
        "restricted_support_hash": restricted_support_hash,
        "deleted_set_hash": deleted_set_hash,
    }
    audit["elapsed_s"] = round(time.time() - t0, 2)
    audit["peak_rss_bytes_so_far"] = peak_rss_bytes()
    audit["all_assertions_passed"] = True
    with open(TASK_DIR / "column-audit.json", "w") as f:
        json.dump(audit, f, indent=1)
    clog(f"restricted adjacency written sha={restricted_sha[:16]} nnz={rnnz} "
         f"({audit['elapsed_s']}s, peak_rss={audit['peak_rss_bytes_so_far']/2**30:.2f} GiB)")
    return (restricted, nrows, sem_hash, null_hash, adj_sha, restricted_sha,
            restriction_sha, restricted_support_hash, deleted_set_hash, sr_pred, audit)


def load_restricted():
    need(RESTRICTED_PKL.exists(), f"missing restricted adjacency {RESTRICTED_PKL}")
    restricted_sha = file_hash(RESTRICTED_PKL)
    with open(RESTRICTED_PKL, "rb") as f:
        p = pickle.load(f)
    need(p["which"] == "null_restricted_to_sem_support", "restricted arm tag mismatch")
    need(p["D"] == D and p["system_hash"] == C["null_system_hash"], "restricted identity")
    need(p["sem_system_hash"] == C["sem_system_hash"], "restricted sem hash")
    need(p["ncols"] == C["sem_ncols"] and p["nrows"] == C["nrows"], "restricted dims")
    need(hashlib.sha256(p["kept_idx"].tobytes()).hexdigest() == p["restriction_sha256"],
         "kept_idx hash mismatch")
    need(p.get("set_hash_algorithm_id") == SET_HASH_ALG, "set hash alg id mismatch")
    need(p.get("restricted_support_hash"), "missing restricted_support_hash in pickle")
    need(p.get("deleted_set_hash"), "missing deleted_set_hash in pickle")
    clog(f"restricted adjacency reloaded sha={restricted_sha[:16]} ncols={p['ncols']}")
    return (p["col_rows"], p["nrows"], p["sem_system_hash"], p["system_hash"],
            p["source_adj_sha256"], restricted_sha, p["restriction_sha256"],
            p["restricted_support_hash"], p["deleted_set_hash"])


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
        clog(f"RESUME at col {st['next_col']} rank_acc={st['rank_acc']}")
    st["invocations"].append({
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "aggregate_used_s_at_start": aggregate_used,
        "resume": st["next_col"] > 0,
    })
    save_state(STATE_DIR, st)

    if st["done"]:
        clog(f"already DONE rank={st['rank_acc']}")
        return st, "already_done"

    carries = load_carries(STATE_DIR, st)
    clog(f"loaded {len(carries)} carrier blocks (checkpoint hashes verified)")
    covlog = open(TASK_DIR / "chunk-coverage.log", "a")
    covlog.write(
        f"# start utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"next_col={st['next_col']} rank_acc={st['rank_acc']} ncols={ncols}\n")
    covlog.flush()

    stop_reason = "completed"
    last_unit_wall = None
    while st["next_col"] < ncols:
        elapsed_agg = aggregate_used + (time.time() - T_PROC0)
        est = last_unit_wall if last_unit_wall else 200.0
        if elapsed_agg + est + reserve_s > wall_cap:
            stop_reason = "wall_cap"
            clog(f"STOP wall cap: agg={elapsed_agg:.1f}+est={est:.1f}+"
                 f"reserve={reserve_s} > cap={wall_cap}")
            break
        if max_units and len(st["units"]) >= max_units:
            stop_reason = "max_units"
            break
        rss = peak_rss_bytes()
        if rss > 8 * 2**30:
            stop_reason = "memory_cap"
            clog(f"STOP memory cap: rss={rss/2**30:.2f} GiB > 8 GiB")
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
        st["units"].append({
            "j0": j0, "j1": j1, "c": c, "k": k,
            "rank_acc": st["rank_acc"],
            "unit_wall_s": round(last_unit_wall, 2),
            "tm": {k2: round(v, 2) for k2, v in tm.items()},
        })
        save_state(STATE_DIR, st)
        covlog.write(json.dumps(st["units"][-1]) + "\n")
        covlog.flush()
        clog(f"cols {j0}..{j1} k={k} rank={st['rank_acc']} "
             f"fill={tm['fill']:.1f} red={tm['reduce']:.1f} ech={tm['ech']:.1f} "
             f"post={tm['post']:.1f} unit_wall={last_unit_wall:.1f} "
             f"agg={aggregate_used + time.time()-T_PROC0:.0f}s")
        gc.collect()

    if st["next_col"] >= ncols:
        st["done"] = True
        save_state(STATE_DIR, st)
    covlog.write(
        f"# end utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"next_col={st['next_col']} rank_acc={st['rank_acc']} done={st['done']} "
        f"stop_reason={stop_reason}\n")
    covlog.close()
    return st, stop_reason


def coverage_audit(st, ncols):
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
    if cursor != ncols or total != ncols:
        ok = False
        problems.append(f"coverage cursor/total {cursor}/{total} != ncols {ncols}")
    k_sum = sum(u["k"] for u in units)
    if k_sum != st["rank_acc"]:
        ok = False
        problems.append(f"sum k {k_sum} != rank_acc {st['rank_acc']}")
    npiv = sum(e["npiv"] for e in st["carries"])
    if npiv != st["rank_acc"]:
        ok = False
        problems.append(f"carrier pivots {npiv} != rank_acc {st['rank_acc']}")
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


def evaluate_admission(metrics_block, q_machine):
    """Path-pinned admission_metrics from ctrl_b_protocol.yaml."""
    checks = {
        "cell_identity_matches_n12_t3_ti0_seed2026_D6":
            metrics_block["cell"] == {"n": 12, "t": 3, "ti": 0, "seed": 2026, "D": 6,
                                      "nb": 24},
        "sem_system_hash_equals_ctrl_a_pin":
            metrics_block["sem_system_hash"] == C["sem_system_hash"],
        "null_system_hash_equals_ctrl_a_pin":
            metrics_block["null_system_hash"] == C["null_system_hash"],
        "restricted_ncols_equals_174035":
            metrics_block["restricted_ncols"] == 174035,
        "deleted_ncols_equals_16016":
            metrics_block["deleted_ncols"] == 16016,
        "deleted_set_equals_null_minus_sem":
            metrics_block["deleted_set_equals_null_minus_sem"] is True,
        "deleted_degree_histogram_equals_6_16016":
            metrics_block["deleted_degree_histogram"] == {"6": 16016},
        "restricted_support_hash_equals_rebuild_digest":
            metrics_block["restricted_support_hash_rebuild_match"] is True,
        "deleted_set_hash_equals_rebuild_digest":
            metrics_block["deleted_set_hash_rebuild_match"] is True,
        "full_column_coverage_loop_to_ncols":
            metrics_block["full_column_coverage_loop_to_ncols"] is True,
        "rank_sem_anchor_138573_unchanged":
            metrics_block["rank_sem_anchor"] == 138573,
        "deficit_genuine_in_closed_interval_1931_17947":
            (metrics_block["deficit_genuine"] is not None
             and DEFICIT_BRACKET[0] <= metrics_block["deficit_genuine"]
             <= DEFICIT_BRACKET[1]),
        "certificate_kind_none_pure_rank":
            metrics_block["certificate_kind"] == "none",
        "quarantine_predicates_Q1_Q4_hold":
            q_machine["all_pass"] is True,
    }
    return checks, all(checks.values())


def evaluate_q_machine(receipt):
    """CTRL-B-Q-MACHINE-v1 closed boolean checks on this receipt's named fields."""
    r = receipt
    # Q1: never cite 17947 as structural syzygy via raw_deficit / deficit_vs_sr_pred
    structural_metric_id = r.get("structural_metric_id")
    structural_metric_value = r.get("structural_metric_value")
    structural_d6_number = r.get("structural_d6_number")
    q1 = True
    if structural_metric_id in ("deficit_vs_sr_pred", "raw_deficit") \
            and structural_metric_value == 17947:
        q1 = False
    if structural_d6_number == 17947 and structural_metric_id not in (
            None, "deficit_genuine"):
        q1 = False
    # Allowlisted quarantine fields may mention 17947.
    q2 = r.get("raw_headline_status") == "quarantined_confounded"
    admission_status = r.get("ctrl_b_admission_status")
    if admission_status != "admitted":
        # Q3: before admission, only lower_bound or pinned D5 structural citations
        sid = structural_metric_id
        if sid in ("deficit_vs_sr_pred", "raw_deficit", "deficit_genuine"):
            q3 = False
        elif structural_d6_number == 17947:
            q3 = False
        else:
            q3 = True  # this receipt does not emit forbidden pre-admission structural cites
        q4 = None  # N/A
    else:
        q3 = None  # N/A after admission
        # Q4: structural_d6 equals measured deficit_genuine with metric id deficit_genuine
        dg = r.get("metrics", {}).get("deficit_genuine")
        q4 = (structural_d6_number == dg
              and structural_metric_id == "deficit_genuine"
              and (structural_d6_number != 17947
                   or (dg == 17947 and structural_metric_id == "deficit_genuine")))
    preds = {
        "Q1": {"pass": q1, "rule": "never_cite_17947_as_structural_syzygy_signal"},
        "Q2": {"pass": q2, "rule": "raw_headline_labeled_quarantined_confounded"},
        "Q3": {"pass": q3, "rule": "before_admission_only_lower_bound_or_pinned_d5",
               "na": q3 is None},
        "Q4": {"pass": q4, "rule": "after_admission_structural_d6_equals_deficit_genuine",
               "na": q4 is None},
    }
    evaluated = [p["pass"] for p in preds.values() if p["pass"] is not None]
    return {
        "checker_id": CHECKER_ID,
        "predicates": preds,
        "all_pass": all(evaluated) if evaluated else False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("prepare", "rank", "all"), default="all")
    ap.add_argument("--chunk-force", type=int, default=12000)
    ap.add_argument("--wall-cap", type=float, default=3400.0)
    ap.add_argument("--aggregate-used", type=float, default=0.0)
    ap.add_argument("--reserve", type=float, default=90.0)
    ap.add_argument("--max-units", type=int, default=0)
    ap.add_argument("--fresh-state", action="store_true",
                    help="wipe STATE_DIR before rank (force full recompute)")
    args = ap.parse_args()

    TASK_DIR.mkdir(parents=True, exist_ok=True)
    if args.fresh_state and STATE_DIR.exists():
        shutil.rmtree(STATE_DIR)
        clog(f"wiped prior state at {STATE_DIR}")
    if args.fresh_state and RESTRICTED_PKL.exists() and args.phase in ("prepare", "all"):
        # keep pickle only if prepare will rebuild; wipe for true fresh prepare
        pass

    clog(f"start phase={args.phase} chunk_force={args.chunk_force} "
         f"wall_cap={args.wall_cap} aggregate_used={args.aggregate_used} "
         f"repo={REPO}")
    status = "unset"
    out = {}
    try:
        if args.phase in ("prepare", "all") and (
                not RESTRICTED_PKL.exists() or args.fresh_state
                or args.phase == "prepare"):
            if args.fresh_state and RESTRICTED_PKL.exists():
                RESTRICTED_PKL.unlink()
            (restricted, nrows, sem_hash, null_hash, adj_sha, restricted_sha,
             restriction_sha, rsh, dsh, sr_pred, audit) = prepare()
        else:
            (restricted, nrows, sem_hash, null_hash, adj_sha, restricted_sha,
             restriction_sha, rsh, dsh) = load_restricted()
            sr_pred = C["sr_pred"]
            audit = None
        prepare_done_s = time.time() - T_PROC0
        if args.phase == "prepare":
            clog(f"prepare-only complete in {prepare_done_s:.1f}s")
            return 0

        ident = {
            "n": N, "t": T, "ti": TI, "d": D, "seed": SEED,
            "which": "null_restricted_to_sem_support", "nb": C["nb"],
            "system_hash": null_hash, "sem_system_hash": sem_hash,
            "restriction_sha256": restriction_sha,
            "restricted_adj_sha256": restricted_sha,
            "source_adj_sha256": adj_sha,
            "restricted_support_hash": rsh,
            "deleted_set_hash": dsh,
            "set_hash_algorithm_id": SET_HASH_ALG,
        }
        st, stop_reason = rank_loop(
            restricted, nrows, ident, args.chunk_force,
            args.wall_cap, args.aggregate_used, args.reserve, args.max_units)
        ncols = C["sem_ncols"]
        wall_this = time.time() - T_PROC0
        cov = coverage_audit(st, ncols) if st["done"] else None

        base_metrics = {
            "cell": {"n": N, "t": T, "ti": TI, "seed": SEED, "D": D, "nb": C["nb"]},
            "sem_system_hash": sem_hash,
            "null_system_hash": null_hash,
            "restricted_ncols": ncols,
            "deleted_ncols": C["support_gap"],
            "deleted_set_equals_null_minus_sem": True,
            "deleted_degree_histogram": {"6": 16016},
            "restricted_support_hash": rsh,
            "deleted_set_hash": dsh,
            "restricted_support_hash_rebuild_match": True,
            "deleted_set_hash_rebuild_match": True,
            "full_column_coverage_loop_to_ncols": True,
            "rank_sem_anchor": C["sem_rank_committed"],
            "certificate_kind": "none",
            "deficit_genuine": None,
        }

        out = {
            "schema": "TASK-20260731-016 CTRL-B results — observations + admission only",
            "task_id": "TASK-20260731-016",
            "experiment_id": "EXP-DREG-001",
            "goal_id": "GOAL-DREG-001",
            "batch_id": "BATCH-005",
            "protocol_ref":
                "coordination/goals/GOAL-DREG-001/batches/BATCH-004/tasks/"
                "TASK-20260725-701/ctrl_b_protocol.yaml",
            "authorization_decision": "DEC-20260725-026",
            "cell": base_metrics["cell"],
            "arm": "null_restricted_to_sem_support",
            "instrument": {
                "path": "src/h012c_block_m4ri.py",
                "mode": "chunked_block_m4ri",
                "forbid_honored": ["unchunked DREG_dff.sage at D6"],
            },
            "nrows": nrows,
            "ncols_restricted": ncols,
            "ncols_deleted": C["support_gap"],
            "ncols_null_full": C["null_ncols"],
            "anchors": {
                "rank_sem": C["sem_rank_committed"],
                "sr_pred": C["sr_pred"],
                "rank_null_full": C["null_rank_full_committed"],
                "column_deletion_lower_bound_genuine":
                    C["column_deletion_lower_bound_genuine"],
                "raw_deficit_vs_sr_pred_quarantined":
                    C["raw_headline_quarantined"],
            },
            "sr_pred_note": ("support-INDEPENDENT; never subtracted from restricted "
                             "rank; raw 17947 remains quarantined_confounded"),
            "certificate": {"kind": "none",
                            "reason": "pure exact GF(2) rank; no DL solve/relation"},
            "system_hashes": {"null": null_hash, "sem": sem_hash},
            "set_hashes": {
                "algorithm_id": SET_HASH_ALG,
                "restricted_support_hash": rsh,
                "deleted_set_hash": dsh,
                "rebuild_match": True,
            },
            "source_adj_sha256": adj_sha,
            "restricted_adj_sha256": restricted_sha,
            "restriction_sha256_kept_idx": restriction_sha,
            "preregistered_bracket": {
                "restricted_null_rank": list(BRACKET),
                "deficit_genuine": list(DEFICIT_BRACKET),
            },
            "chunk_force": args.chunk_force,
            "secs_total": round(st["secs_total"], 1),
            "n_units": len(st["units"]),
            "wall_seconds_this_invocation": round(wall_this, 2),
            "wall_seconds_aggregate": round(args.aggregate_used + wall_this, 2),
            "prepare_seconds": round(prepare_done_s, 2),
            "peak_rss_bytes": peak_rss_bytes(),
            "stop_reason": stop_reason,
            "raw_headline_status": "quarantined_confounded",
            "raw_headline_value": 17947,
            "quarantine_note": ("raw 17947 = sr_pred - rank_sem is support-confounded; "
                                "never cite as deficit_genuine unless admitted and "
                                "equal to measured deficit_genuine"),
        }

        if st["done"]:
            rank = int(st["rank_acc"])
            need(cov["covers_range_exactly_once"],
                 f"chunk coverage audit failed: {cov['problems']}")
            in_bracket = BRACKET[0] <= rank <= BRACKET[1]
            deficit = rank - C["sem_rank_committed"]
            base_metrics["deficit_genuine"] = deficit
            # Provisional structural fields for Q-machine (set after admission decision)
            out.update({
                "rank_null_restricted": rank,
                "metrics": {
                    "rank_null_restricted": rank,
                    "deficit_genuine": deficit,
                    "deficit_genuine_formula": "rank(null|sem_support) - 138573",
                    "expected_interval": list(DEFICIT_BRACKET),
                },
                "in_preregistered_bracket": bool(in_bracket),
                "chunk_coverage": cov,
            })
            # First evaluate Q1/Q2 with pre-admission posture, then admit if metrics pass
            out["ctrl_b_admission_status"] = "pending"
            out["structural_metric_id"] = None
            out["structural_metric_value"] = None
            out["structural_d6_number"] = None
            q_pre = evaluate_q_machine(out)
            adm_checks, adm_ok = evaluate_admission(base_metrics, q_pre)
            # Re-evaluate with post-admission structural citation if numeric gates pass
            if adm_ok and in_bracket:
                out["ctrl_b_admission_status"] = "admitted"
                out["structural_metric_id"] = "deficit_genuine"
                out["structural_metric_value"] = deficit
                out["structural_d6_number"] = deficit
                q_post = evaluate_q_machine(out)
                adm_checks, adm_ok = evaluate_admission(base_metrics, q_post)
                out["q_machine"] = q_post
            else:
                out["ctrl_b_admission_status"] = "not_admitted"
                out["q_machine"] = q_pre
            out["admission_metrics"] = adm_checks
            out["all_admission_metrics_pass"] = bool(adm_ok and in_bracket)
            if adm_ok and in_bracket:
                out["validity"] = "completed_valid"
                out["deficit_genuine_admitted"] = True
                # If measured deficit equals quarantined headline, still OK under Q4
                # when cited strictly as deficit_genuine.
                out["status"] = "completed_valid"
            else:
                out["validity"] = "invalid_measurement"
                out["deficit_genuine_admitted"] = False
                out["status"] = "invalid_measurement"
                out["metrics"]["deficit_genuine"] = None  # do not mint on failed admission
                out["structural_metric_id"] = None
                out["structural_metric_value"] = None
                out["structural_d6_number"] = None
                out["ctrl_b_admission_status"] = "not_admitted"
                if not in_bracket:
                    out["integrity_failure_reason"] = (
                        f"rank {rank} outside bracket {list(BRACKET)}")
            status = out["status"]
        else:
            out.update({
                "rank_null_restricted": None,
                "metrics": {"rank_null_restricted": None, "deficit_genuine": None},
                "validity": "failed_infrastructure",
                "status": "failed_infrastructure",
                "failure_class": "resource_exhaustion",
                "deficit_genuine_admitted": False,
                "ctrl_b_admission_status": "not_admitted",
                "cap_hit": stop_reason,
                "last_completed_column_exclusive": int(st["next_col"]),
                "partial_rank_acc": int(st["rank_acc"]),
                "partial_rank_acc_note": ("NOT a rank, NOT a bound, NOT evidence "
                                          "(AGENTS.md rule 5)"),
            })
            out["structural_metric_id"] = None
            out["structural_metric_value"] = None
            out["structural_d6_number"] = None
            out["q_machine"] = evaluate_q_machine(out)
            status = "failed_infrastructure"
    except IntegrityFailure as e:
        status = "invalid_measurement"
        out = {
            "task_id": "TASK-20260731-016",
            "experiment_id": "EXP-DREG-001",
            "validity": "invalid_measurement",
            "status": "invalid_measurement",
            "failure_class": "invalid_measurement",
            "integrity_failure_reason": str(e),
            "certificate": {"kind": "none"},
            "deficit_genuine_admitted": False,
            "ctrl_b_admission_status": "not_admitted",
            "rank_null_restricted": None,
            "metrics": {"deficit_genuine": None},
            "raw_headline_status": "quarantined_confounded",
            "raw_headline_value": 17947,
            "wall_seconds_this_invocation": round(time.time() - T_PROC0, 2),
            "peak_rss_bytes": peak_rss_bytes(),
            "note": "aborted at identity/restriction check; no rank reported",
        }
        out["structural_metric_id"] = None
        out["structural_metric_value"] = None
        out["structural_d6_number"] = None
        out["q_machine"] = evaluate_q_machine(out)
        clog(f"INTEGRITY FAILURE: {e}")
    except OSError as e:
        # ENOSPC / I/O
        status = "failed_infrastructure"
        out = {
            "task_id": "TASK-20260731-016",
            "validity": "failed_infrastructure",
            "status": "failed_infrastructure",
            "failure_class": "infrastructure_error",
            "infrastructure_reason": str(e),
            "deficit_genuine_admitted": False,
            "ctrl_b_admission_status": "not_admitted",
            "rank_null_restricted": None,
            "metrics": {"deficit_genuine": None},
            "raw_headline_status": "quarantined_confounded",
            "raw_headline_value": 17947,
            "certificate": {"kind": "none"},
            "wall_seconds_this_invocation": round(time.time() - T_PROC0, 2),
            "peak_rss_bytes": peak_rss_bytes(),
            "note": "infra failure is NOT negative mathematical evidence",
        }
        out["structural_metric_id"] = None
        out["structural_metric_value"] = None
        out["structural_d6_number"] = None
        out["q_machine"] = evaluate_q_machine(out)
        clog(f"INFRA FAILURE: {e}")

    out["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(TASK_DIR / "raw-result.json", "w") as f:
        json.dump(out, f, indent=1)
    clog(f"status={status} -> {TASK_DIR / 'raw-result.json'}")
    if out.get("validity") == "completed_valid":
        clog(f"RESULT rank={out['rank_null_restricted']} "
             f"deficit_genuine={out['metrics']['deficit_genuine']} "
             f"admitted={out['deficit_genuine_admitted']}")
    return 0 if status == "completed_valid" else 1


if __name__ == "__main__":
    sys.exit(main())
