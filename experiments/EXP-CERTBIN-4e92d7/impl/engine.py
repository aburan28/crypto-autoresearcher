"""Phases 2-6: per (family, D) eliminations, traces, reference comparisons,
fixed-schedule replays and per-instance instrument checks."""
import time
from collections import Counter

import numpy as np

from elim import (eliminate, affine_forms, eval_forms, replay_direct, gf2_rank_rows,
                  int_rank, ops_json_list)
from oracles import ps0_check
from stats import wilson

GRANS = ("rank", "set", "strict", "ops")


class RefData:
    pass


def popcount_rows(M):
    return np.bitwise_count(M).sum(axis=1)


def instance_checks(S, M, res, inst):
    """PS0, PS1, PS3 for one instance at one D."""
    sols = inst["sols"]
    one = (S.const_col in set(res.c))
    out = {"one_in_R": one}
    bad0, evs = ps0_check(S, M, sols)
    out["PS0_fail"] = bad0
    out["PS1_fail"] = bool(one and len(sols) >= 1)
    ev_rank = gf2_rank_rows(np.stack(evs)) if evs else 0
    out["PS3_eval_rank"] = int(ev_rank)
    out["PS3_deficit"] = int(S.C - res.rank)
    out["PS3_fail"] = bool(S.C - res.rank < ev_rank)
    return out


def make_ref(S, M, inst, label, group, planesM=None):
    res, cpass, leads = eliminate(M, S.C, keep_ops=True)
    r = RefData()
    r.label, r.group, r.inst = label, group, inst
    r.M = M
    r.res = res
    r.cpass = cpass
    r.p = np.array(res.p, dtype=np.int64)
    r.c = np.array(res.c, dtype=np.int64)
    r.checks = instance_checks(S, M, res, inst)
    r.forms = None
    if planesM is not None:
        r.forms = affine_forms(planesM, res.p, res.c, res.X)
    # the reference's own fixed-schedule replay must meet a 1 at every pivot
    r.self_replay_ok = bool((replay_direct(M, res.p, res.c, res.X) == 1).all())
    # sizes
    R = M.shape[0]
    nnz_full = int(np.bitwise_count(M).sum())
    keep = np.ones(R, dtype=bool)
    keep[res.Z] = False
    Mk = M[keep]
    color = np.bitwise_or.reduce(Mk, axis=0) if Mk.shape[0] else np.zeros(M.shape[1], dtype=np.uint64)
    cols_pruned = int(np.bitwise_count(color).sum())
    nnz_pruned = int(np.bitwise_count(Mk).sum())
    rows_pruned = int(keep.sum())
    r.sizes = {
        "full": {"rows": R, "cols": S.C, "dense_bytes": R * S.C / 8, "nnz": nnz_full,
                 "csr_bytes": 4 * nnz_full + 4 * (R + 1)},
        "pruned": {"rows": rows_pruned, "cols": cols_pruned, "dense_bytes": rows_pruned * cols_pruned / 8,
                   "nnz": nnz_pruned, "csr_bytes": 4 * nnz_pruned + 4 * (rows_pruned + 1)},
    }
    W = S.W
    ops_masked_full = S.C * R
    ops_set = len(res.pivcols) * (R - len(res.Z))
    r.saving = {
        "unit": "one full-row XOR (C_D bits)",
        "ops_masked_full": ops_masked_full,
        "ops_strict": res.ops_strict,
        "ops_set": ops_set,
        "rank_sq": res.rank ** 2,
        "ops_set_equals_rank_sq": ops_set == res.rank ** 2,
        "saving_strict": ops_masked_full / res.ops_strict if res.ops_strict else None,
        "saving_set": ops_masked_full / ops_set if ops_set else None,
        "saving_set_identity_exact": (ops_set > 0 and ops_masked_full * res.rank ** 2 == (S.C * R) * ops_set),
        "saving_rank": 1.0,
        "words_per_row": W,
        "word_ops_masked_full": ops_masked_full * W,
        "word_ops_strict": res.ops_strict * W,
        "word_ops_set": ops_set * W,
    }
    return r


def ref_summary(r, S, keep_strict=True):
    res = r.res
    d = {
        "label": r.label, "group": r.group,
        "rank": res.rank, "one_in_R": r.checks["one_in_R"],
        "h_rank": res.h_rank, "h_set": res.h_set, "h_strict": res.h_strict, "h_ops": res.h_ops,
        "len_strict": len(res.p), "Z_size": len(res.Z), "cpass": r.cpass, "self_replay_ok": r.self_replay_ok,
        "checks": r.checks, "sizes": r.sizes, "saving": r.saving,
    }
    if keep_strict:
        d["T_strict"] = [[int(p), int(c)] for p, c in zip(res.p, res.c)]
        d["T_set"] = [res.pivcols, res.Z]
    if r.forms is not None:
        a0, a = r.forms
        nz = [int(x) for x in a if x]
        d["K_exact"] = len(nz)
        d["K_rank"] = int_rank(nz)
        d["forms_a0"] = a0.tolist()
        d["forms_a"] = a.tolist()
    return d


def compare(tres, tp, tc, ref, col_deg, anomalies, tag):
    rres = ref.res
    m = {}
    m["rank"] = tres.rank == rres.rank
    hs = tres.h_set == rres.h_set
    cs = (tres.pivcols == rres.pivcols and tres.Z == rres.Z) if hs else False
    if hs != cs:
        anomalies.append({"where": tag, "granularity": "set", "hash_equal": hs, "content_equal": cs})
    m["set"] = cs
    L = min(len(tp), len(ref.p))
    diff = (tp[:L] != ref.p[:L]) | (tc[:L] != ref.c[:L])
    nz = np.flatnonzero(diff)
    kdiv = int(nz[0]) if nz.size else L
    strict_content = (kdiv == L and len(tp) == len(ref.p))
    hstrict = tres.h_strict == rres.h_strict
    if hstrict != strict_content:
        anomalies.append({"where": tag, "granularity": "strict", "hash_equal": hstrict,
                          "content_equal": strict_content})
    m["strict"] = strict_content
    hops = tres.h_ops == rres.h_ops
    if hops:
        ops_content = strict_content and all(np.array_equal(x, y) for x, y in zip(tres.X, rres.X))
        if not ops_content:
            anomalies.append({"where": tag, "granularity": "ops", "hash_equal": True, "content_equal": False})
    else:
        ops_content = False
    m["ops"] = ops_content
    Lr = len(ref.p)
    if kdiv < Lr:
        dcol = int(ref.c[kdiv])
    elif kdiv < len(tp):
        dcol = int(tc[kdiv])
    else:
        dcol = None
    return {
        "match": m,
        "kdiv": kdiv,
        "f_div": kdiv / Lr if Lr else None,
        "div_col": dcol,
        "div_deg": int(col_deg[dcol]) if dcol is not None else None,
        "len_t": int(len(tp)),
    }


def determine_modal(first100):
    """Modal T_set among non-degenerate targets 1..100 (draw order); ties go to
    the T_set whose first occurrence has the lowest index; the modal instance
    is the lowest-index target with that T_set."""
    cnt = Counter()
    first = {}
    for idx, hset in first100:
        cnt[hset] += 1
        first.setdefault(hset, idx)
    best = max(cnt.items(), key=lambda kv: (kv[1], -first[kv[0]]))
    return first[best[0]], best[0], best[1], len(cnt)


def hazard_table(e_mat, K, a_info=None, over_survivors=False):
    """e_mat: (T, K) uint8 replay entries (255 = not reached). Returns the
    per-pivot hazard table and first-zero indices."""
    T = e_mat.shape[0]
    if T == 0:
        return None, np.zeros(0, dtype=np.int64)
    zero = (e_mat == 0)
    has0 = zero.any(axis=1)
    fz = np.where(has0, zero.argmax(axis=1), K).astype(np.int64)
    # S_k = #{fz >= k}; zeros_k = #{fz == k}
    counts = np.bincount(fz, minlength=K + 1)
    geq = np.cumsum(counts[::-1])[::-1]
    Sk = geq[:K]
    zk = counts[:K]
    if over_survivors:
        dep = (zk > 0) & (zk < Sk)
    else:
        nz_any = zero.any(axis=0)
        one_any = (e_mat == 1).any(axis=0)
        dep = nz_any & one_any
    tab = {
        "S_k": Sk.tolist(),
        "zeros_k": zk.tolist(),
        "sampled_dependent": dep.astype(int).tolist(),
        "dependence_basis": "replay survivors" if over_survivors else "all scored targets",
    }
    h = []
    wl = []
    for k in range(K):
        if Sk[k] > 0:
            h.append(round(float(zk[k] / Sk[k]), 6))
            w = wilson(int(zk[k]), int(Sk[k]))
            wl.append([round(w[0], 6), round(w[1], 6)])
        else:
            h.append(None)
            wl.append(None)
    tab["h_k"] = h
    tab["wilson95"] = wl
    if a_info is not None:
        a0, a = a_info
        tab["a_nonzero"] = (a != 0).astype(int).tolist()
        tab["a0"] = a0.astype(int).tolist()
        if not over_survivors:
            zd = zero.mean(axis=0)
            tab["unconditional_zero_density"] = [round(float(zd[k]), 6) if dep[k] else None for k in range(K)]
    tab["K_sampled"] = int(dep.sum())
    tab["n_scored"] = int(T)
    tab["full_replay_survivors"] = int(counts[K])
    return tab, fz


def process_family(ctx, fam, D, ref_insts, targets, build_E, reverse, planes_E,
                   cross_groups, log, affine_route=True, keep_oplogs=False):
    """Eliminate references (own) and all targets of one family at one D."""
    t0 = time.time()
    S = ctx["shapes"][D]
    col_deg = S.col_deg
    anomalies = []
    planesM = None
    if planes_E is not None:
        planesM = np.stack([S.build(Ex, reverse=reverse) for Ex in planes_E])
    own = []
    for inst in ref_insts:
        M = S.build(build_E(inst), reverse=reverse)
        own.append(make_ref(S, M, inst, inst["selected_as"], "own", planesM))
    groups = {"own": own}
    groups.update(cross_groups)
    all_refs = [(g, r) for g, rs in groups.items() for r in rs]
    records = []
    first100 = []
    keep_M20 = {}
    modal = None
    modal_info = None
    caff = {"checked_pairs": 0, "mismatch_pairs": 0, "mismatches": []}
    replay_fz_direct = {}  # (group,label) -> {idx: fz}

    def ensure_modal():
        nonlocal modal, modal_info
        if modal is not None or not first100:
            return
        midx, mh, mcount, ndistinct = determine_modal(first100)
        inst = next(t for t in targets if t["idx"] == midx)
        M = S.build(build_E(inst), reverse=reverse)
        modal = make_ref(S, M, inst, "modal", "own", planesM)
        modal_info = {"modal_idx": midx, "modal_h_set": mh, "modal_class_size_in_1_100": mcount,
                      "distinct_T_set_in_1_100": ndistinct,
                      "stratum": "sat" if inst["s"] >= 1 else "unsat"}
        # C-AFF direct replay of the modal on the stored first-20 targets
        if modal.forms is not None:
            for idx, (Mt, rt) in keep_M20.items():
                _caff_check(Mt, rt, modal, idx)

    def _caff_check(Mt, rt, ref, idx):
        e_dir = replay_direct(Mt, ref.res.p, ref.res.c, ref.res.X)
        e_aff = eval_forms(ref.forms[0], ref.forms[1], [rt])[0]
        caff["checked_pairs"] += 1
        if not np.array_equal(e_dir, e_aff):
            caff["mismatch_pairs"] += 1
            caff["mismatches"].append({"target_idx": idx, "ref": f"{ref.group}:{ref.label}",
                                       "n_entries_differ": int((e_dir != e_aff).sum())})

    for t in targets:
        idx = t["idx"]
        if idx > 100:
            ensure_modal()
        M = S.build(build_E(t), reverse=reverse)
        res, cpass, leads = eliminate(M, S.C, keep_ops=True)
        tp = np.array(res.p, dtype=np.int64)
        tc = np.array(res.c, dtype=np.int64)
        chk = instance_checks(S, M, res, t)
        rec = {
            "family": fam, "D": D, "idx": idx, "x_R": t.get("x_R"),
            "degenerate": bool(t.get("degenerate")),
            "stratum": "degenerate" if t.get("degenerate") else ("sat" if t["s"] >= 1 else "unsat"),
            "s": t["s"], "sat": t["s"] >= 1, "rational_flag": t.get("rational_flag"),
            "rank": res.rank, "one_in_R": chk["one_in_R"], "Z_size": len(res.Z),
            "h_rank": res.h_rank, "h_set": res.h_set, "h_strict": res.h_strict, "h_ops": res.h_ops,
            "len_strict": len(tp), "ops_strict": res.ops_strict, "cpass": cpass,
            "PS0_fail": chk["PS0_fail"], "PS1_fail": chk["PS1_fail"], "PS3_fail": chk["PS3_fail"],
            "PS3_eval_rank": chk["PS3_eval_rank"], "refs": {},
        }
        cmp_refs = list(all_refs)
        if modal is not None and idx > 100:
            cmp_refs.append(("own", modal))
        for g, r in cmp_refs:
            key = r.label if g == "own" else f"{g}:{r.label}"
            rec["refs"][key] = compare(res, tp, tc, r, col_deg, anomalies, f"{fam}/D{D}/t{idx}/{key}")
            if not affine_route:
                e = replay_direct(M, r.res.p, r.res.c, r.res.X, stop_at_zero=True)
                z = np.flatnonzero(e == 0)
                rec["refs"][key]["replay_first_zero"] = int(z[0]) if z.size else len(r.p)
        if affine_route and idx <= 20:
            keep_M20[idx] = (M, t["x_R"])
            for g, r in cmp_refs:
                if r.forms is not None:
                    _caff_check(M, t["x_R"], r, idx)
        if idx <= 100 and not t.get("degenerate"):
            first100.append((idx, res.h_set))
        records.append(rec)
        if idx == 100:
            ensure_modal()
        if idx % 100 == 0:
            log(f"  {fam} D={D}: {idx}/{len(targets)} targets ({time.time() - t0:.0f}s)")
    ensure_modal()

    # Modal-reference scores use targets 101..N only (modal_reference_rule);
    # for the null F_2 family the modal's direct replays ran inline for 101..N.
    hazards = {}
    refs_for_hazard = list(all_refs) + ([("own", modal)] if modal is not None else [])
    for g, r in refs_for_hazard:
        key = r.label if g == "own" else f"{g}:{r.label}"
        if r.label == "modal" and g == "own":
            scored = [rec for rec in records if rec["idx"] > 100 and not rec["degenerate"]]
        else:
            scored = [rec for rec in records if not rec["degenerate"]]
        K = len(r.p)
        if affine_route and r.forms is not None:
            rs = [rec["x_R"] for rec in scored]
            e = eval_forms(r.forms[0], r.forms[1], rs) if rs else np.zeros((0, K), dtype=np.uint8)
            tab, fz = hazard_table(e, K, r.forms, over_survivors=False)
            # first replay divergence for every target (incl. degenerate), recorded per target
            allrs = [rec["x_R"] for rec in records]
            eall = eval_forms(r.forms[0], r.forms[1], allrs)
            z = (eall == 0)
            fza = np.where(z.any(axis=1), z.argmax(axis=1), K)
            for rec, f in zip(records, fza):
                if key in rec["refs"]:
                    rec["refs"][key]["replay_first_zero"] = int(f)
        else:
            e = np.full((len(scored), K), 255, dtype=np.uint8)
            for i, rec in enumerate(scored):
                f = rec["refs"].get(key, {}).get("replay_first_zero")
                if f is None:
                    continue
                e[i, :min(f, K)] = 1
                if f < K:
                    e[i, f] = 0
            tab, fz = hazard_table(e, K, None, over_survivors=True)
        if tab is not None:
            tab["p"] = r.p.tolist()
            tab["c"] = r.c.tolist()
            if r.forms is not None:
                nz = [int(x) for x in r.forms[1] if x]
                tab["K_exact"] = len(nz)
                tab["K_rank"] = int_rank(nz)
                tab["predicted_retention_2^-K_rank"] = 2.0 ** (-tab["K_rank"])
            tab["measured_fixed_schedule_retention"] = tab["full_replay_survivors"] / tab["n_scored"] if tab["n_scored"] else None
            surv = [1 - hk for hk in tab["h_k"] if hk is not None]
            prod = 1.0
            for x in surv:
                prod *= x
            tab["product_of_per_pivot_survivals"] = prod
        hazards[key] = tab

    refs_out = [ref_summary(r, S) for r in own]
    if modal is not None:
        ms = ref_summary(modal, S)
        ms["modal_info"] = modal_info
        ms["instance_idx"] = modal.inst["idx"]
        refs_out.append(ms)
    oplogs = None
    if keep_oplogs:
        oplogs = [(r.label, r.inst, ops_json_list(r.res)) for r in own + ([modal] if modal else [])]
    result = {
        "family": fam, "D": D, "reverse": reverse, "refs": refs_out, "records": records,
        "hazards": hazards, "caff_direct": caff, "hash_anomalies": anomalies,
        "modal_info": modal_info, "wall_seconds": time.time() - t0,
        "ref_cpass": {r.label: r.cpass for r in own + ([modal] if modal else [])},
    }
    live = {"own": own, "modal": modal}
    return result, live, oplogs
