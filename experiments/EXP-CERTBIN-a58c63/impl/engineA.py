"""Regime A (Weil descent to F_2, D in {3, 4}): per (cell, family, D)
eliminations, traces, reference comparisons, fixed-schedule replays and
per-instance instrument checks.

Copied from EXP-CERTBIN-4e92d7/impl/engine.py (process_family, make_ref,
ref_summary, compare, determine_modal, instance_checks) and restructured so
that the per-target work is a pure function of (target, references) that can
be sharded across at most two worker processes with byte-identical output
(see impl-provenance.json). The Wilson intervals of the Stage-1 hazard table
are dropped (RC-3: exact bands are computed in hull.py instead).
"""
import time
from collections import Counter

import numpy as np

from elim import (sha, canon, eliminate, affine_forms, eval_forms, replay_direct, gf2_rank_rows,
                  int_rank, ops_json_list)
from oracles import ps0_check

GRANS = ("rank", "set", "strict", "ops")


class RefData:
    pass


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
    r.self_replay_ok = bool((replay_direct(M, res.p, res.c, res.X) == 1).all())
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


def ref_summary(r, keep_strict=True):
    res = r.res
    d = {
        "label": r.label, "group": r.group,
        "rank": res.rank, "one_in_R": r.checks["one_in_R"],
        "h_rank": res.h_rank, "h_set": res.h_set, "h_strict": res.h_strict, "h_ops": res.h_ops,
        "len_strict": len(res.p), "Z_size": len(res.Z), "cpass": r.cpass, "self_replay_ok": r.self_replay_ok,
        "checks": r.checks, "sizes": r.sizes, "saving": r.saving,
        "x_R": r.inst.get("x_R"), "s": r.inst.get("s"),
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
    """Stage-1 modal rule: modal T_set among non-degenerate targets 1..100 (draw
    order); ties to the T_set whose first occurrence has the lowest index; the
    modal instance is the lowest-index target with that T_set."""
    cnt = Counter()
    first = {}
    for idx, hset in first100:
        cnt[hset] += 1
        first.setdefault(hset, idx)
    best = max(cnt.items(), key=lambda kv: (kv[1], -first[kv[0]]))
    return first[best[0]], best[0], best[1], len(cnt)


# ---------------------------------------------------------------------------
# the pure per-target function (runs in the parent or in a forked worker)
_G = {}


def set_unit_globals(**kw):
    _G.clear()
    _G.update(kw)


def target_record_A(t):
    S = _G["S"]
    fam, D = _G["fam"], _G["D"]
    build_E = _G["build_E"]
    reverse = _G["reverse"]
    cmp_refs = _G["cmp_refs"]
    affine_route = _G["affine_route"]
    anomalies = []
    M = S.build(build_E(t), reverse=reverse)
    res, cpass, leads = eliminate(M, S.C, keep_ops=True)
    tp = np.array(res.p, dtype=np.int64)
    tc = np.array(res.c, dtype=np.int64)
    chk = instance_checks(S, M, res, t)
    rec = {
        "family": fam, "D": D, "idx": t["idx"], "x_R": t.get("x_R"),
        "degenerate": bool(t.get("degenerate")),
        "stratum": "degenerate" if t.get("degenerate") else ("sat" if t["s"] >= 1 else "unsat"),
        "s": t["s"], "sat": t["s"] >= 1, "rational_flag": t.get("rational_flag"),
        "x2E_class": t.get("x2E_class"),
        "rank": res.rank, "one_in_R": chk["one_in_R"], "Z_size": len(res.Z),
        "h_rank": res.h_rank, "h_set": res.h_set, "h_strict": res.h_strict, "h_ops": res.h_ops,
        "len_strict": len(tp), "ops_strict": res.ops_strict, "cpass": cpass,
        "PS0_fail": chk["PS0_fail"], "PS1_fail": chk["PS1_fail"], "PS3_fail": chk["PS3_fail"],
        "PS3_eval_rank": chk["PS3_eval_rank"], "pivcols_hash": sha(canon(res.pivcols)), "refs": {},
    }
    for key, r in cmp_refs:
        if key == "modal" and t["idx"] <= 100:
            continue
        rec["refs"][key] = compare(res, tp, tc, r, S.col_deg, anomalies, f"{fam}/D{D}/t{t['idx']}/{key}")
        if not affine_route:
            e = replay_direct(M, r.res.p, r.res.c, r.res.X, stop_at_zero=True)
            z = np.flatnonzero(e == 0)
            rec["refs"][key]["replay_first_zero"] = int(z[0]) if z.size else len(r.p)
    caff = []
    if affine_route and t["idx"] <= 20:
        for key, r in cmp_refs:
            if r.forms is None:
                continue
            e_dir = replay_direct(M, r.res.p, r.res.c, r.res.X)
            e_aff = eval_forms(r.forms[0], r.forms[1], [t["x_R"]])[0]
            z = np.flatnonzero(e_dir == 0)
            caff.append({"ref": key, "ok": bool(np.array_equal(e_dir, e_aff)),
                         "n_entries_differ": int((e_dir != e_aff).sum()),
                         "direct_first_zero": int(z[0]) if z.size else len(r.p)})
    rec["_caff"] = caff
    rec["_anomalies"] = anomalies
    return rec


def process_family_A(S, fam, D, ref_insts, targets, build_E, reverse, planes_E, cross, log,
                     mapper, affine_route=True, modal_enabled=True):
    """Eliminate own references and all targets of one family at one D.
    cross: list of (key, RefData) references of another family (scored too)."""
    t0 = time.time()
    planesM = None
    if planes_E is not None:
        planesM = np.stack([S.build(Ex, reverse=reverse) for Ex in planes_E])
    own = []
    for inst in ref_insts:
        M = S.build(build_E(inst), reverse=reverse)
        own.append(make_ref(S, M, inst, inst["selected_as"], "own", planesM))
    cmp_refs = [(r.label, r) for r in own] + list(cross)
    common = dict(S=S, fam=fam, D=D, build_E=build_E, reverse=reverse, affine_route=affine_route)
    set_unit_globals(cmp_refs=cmp_refs, **common)
    first = [t for t in targets if t["idx"] <= 100]
    rest = [t for t in targets if t["idx"] > 100]
    records = mapper(target_record_A, first)
    modal = None
    modal_info = None
    n_nd = sum(1 for t in targets if not t.get("degenerate"))
    if modal_enabled and own and n_nd > 100:
        f100 = [(r["idx"], r["h_set"]) for r in records if not r["degenerate"]]
        if f100:
            midx, mh, mcount, ndistinct = determine_modal(f100)
            inst = next(t for t in targets if t["idx"] == midx)
            modal = make_ref(S, S.build(build_E(inst), reverse=reverse), inst, "modal", "own", planesM)
            modal_info = {"modal_idx": midx, "modal_h_set": mh, "modal_class_size_in_1_100": mcount,
                          "distinct_T_set_in_1_100": ndistinct,
                          "stratum": "sat" if inst["s"] >= 1 else "unsat"}
            # the modal's C-AFF direct replays on targets 1..20
            if modal.forms is not None:
                for rec in records:
                    if rec["idx"] <= 20:
                        t = next(x for x in targets if x["idx"] == rec["idx"])
                        M = S.build(build_E(t), reverse=reverse)
                        e_dir = replay_direct(M, modal.res.p, modal.res.c, modal.res.X)
                        e_aff = eval_forms(modal.forms[0], modal.forms[1], [t["x_R"]])[0]
                        z = np.flatnonzero(e_dir == 0)
                        rec["_caff"].append({"ref": "modal", "ok": bool(np.array_equal(e_dir, e_aff)),
                                             "n_entries_differ": int((e_dir != e_aff).sum()),
                                             "direct_first_zero": int(z[0]) if z.size else len(modal.p)})
    cmp2 = cmp_refs + ([("modal", modal)] if modal is not None else [])
    set_unit_globals(cmp_refs=cmp2, **common)
    records += mapper(target_record_A, rest)
    log(f"    {fam} D={D}: {len(records)} targets ({time.time() - t0:.0f}s)")
    all_refs = cmp2
    # affine route: first replay-zero index per target and reference from the forms
    if affine_route:
        for key, r in all_refs:
            if r.forms is None:
                continue
            K = len(r.p)
            rs = [rec["x_R"] for rec in records]
            e = eval_forms(r.forms[0], r.forms[1], rs)
            z = (e == 0)
            fza = np.where(z.any(axis=1), z.argmax(axis=1), K)
            for rec, f in zip(records, fza):
                if key in rec["refs"]:
                    rec["refs"][key]["replay_first_zero"] = int(f)
    caff = {"checked_pairs": 0, "mismatch_pairs": 0, "mismatches": []}
    anomalies = []
    for rec in records:
        for c in rec.pop("_caff"):
            caff["checked_pairs"] += 1
            if not c["ok"]:
                caff["mismatch_pairs"] += 1
                caff["mismatches"].append({"target_idx": rec["idx"], **c})
            # C-FORMS path 3: the direct replay's first zero equals the forms' first zero
            fz = rec["refs"].get(c["ref"], {}).get("replay_first_zero")
            if fz is not None and fz != c["direct_first_zero"]:
                caff.setdefault("first_zero_mismatch", []).append({"target_idx": rec["idx"], "ref": c["ref"],
                                                                   "forms": fz, "direct": c["direct_first_zero"]})
        anomalies += rec.pop("_anomalies")
    refs_out = [ref_summary(r) for r in own]
    if modal is not None:
        ms = ref_summary(modal)
        ms["modal_info"] = modal_info
        ms["instance_idx"] = modal.inst["idx"]
        refs_out.append(ms)
    result = {"regime": "A", "family": fam, "D": D, "reverse": reverse, "refs": refs_out, "records": records,
              "caff_direct": caff, "hash_anomalies": anomalies, "modal_info": modal_info,
              "wall_seconds": time.time() - t0,
              "ref_cpass": {r.label: r.cpass for r in own + ([modal] if modal else [])}}
    live = own + ([modal] if modal is not None else [])
    return result, live
