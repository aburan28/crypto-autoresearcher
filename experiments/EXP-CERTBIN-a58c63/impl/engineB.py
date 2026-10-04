"""Regime B (new): per (cell, family) eliminations at D = 66 over F_{2^n},
traces, reference comparisons with in-pass first-divergence classification
(Lemma 2B), per-instance Lemma B-S checks (delta, C-DELTA, C-RANKB), PS0/PS1,
sizes and saving ratios; phase-4 replays, K_B probes and C-BREAK minors."""
import time
from collections import Counter

import numpy as np

from regimeB import eliminate, replay, column_pass, sha, canon, guided
from detmod import minor
from engineA import determine_modal


class RefB:
    pass


def delta_encode(X):
    X = [int(x) for x in X]
    if not X:
        return []
    return [X[0]] + [b - a for a, b in zip(X, X[1:])]


def ps0_B(S, M, sols, l):
    """Every row of M_66 vanishes at every solution (x_1, x_2) in V^2."""
    if not sols:
        return []
    T = S._tabs
    nzr, nzc = np.nonzero(M)
    vals = M[nzr, nzc].astype(np.int64)
    starts = np.flatnonzero(np.r_[True, nzr[1:] != nzr[:-1]])
    bad = []
    vm = (1 << l) - 1
    for u in sols:
        x1, x2 = u & vm, u >> l
        ev = S.eval_vector(x1, x2)
        e = ev[nzc]
        pr = T.exp[T.log[vals] + T.log[e]]
        pr[e == 0] = 0
        rs = np.bitwise_xor.reduceat(pr, starts)
        n = int((rs != 0).sum())
        if n:
            bad.append({"u": int(u), "nonvanishing_rows": n})
    return bad


def instance_B(S, M, res, inst, l, deltacalc, oC):
    """one_in_R, PS0, PS1, delta (unsat), C-DELTA, C-RANKB for one instance."""
    one = S.const_col in set(res.c)
    s = inst["s"]
    out = {"one_in_R": one, "PS1_fail": bool(one and s >= 1)}
    out["PS0_fail"] = ps0_B(S, M, inst["sols"], l) if s >= 1 else []
    if s == 0:
        vals = oC.values(inst["coeffs"]).reshape(1 << l, 1 << l)
        d = deltacalc.compute(vals)
        out["delta"] = d["delta"]
        out["top"] = d["top"]
        out["top_identity_ok"] = d["top_identity_ok"]
        out["C-DELTA_ok"] = bool(one == (d["delta"] + 4 <= S.D)) and d["top_identity_ok"]
    else:
        out["delta"] = None
        out["C-DELTA_ok"] = None
    C = S.C
    if l == 5:
        pred = C if s == 0 else C - s
        out["rank_pred"] = pred
        out["C-RANKB_ok"] = res.rank == pred
    else:
        if s == 0:
            out["rank_pred"] = S.R
            out["C-RANKB_ok"] = res.rank == S.R
        else:
            out["rank_pred"] = None
            out["rank_pred_note"] = "sat at l = 6: recorded, predicted 2028, not a control"
            out["C-RANKB_ok"] = None
    return out


def make_ref_B(S, T, M, inst, label, group, l, deltacalc, oC):
    res, cpass, leads = eliminate(M, T)
    r = RefB()
    r.label, r.group, r.inst = label, group, inst
    r.M = M
    r.res = res
    r.cpass = cpass
    r.p = np.array(res.p, dtype=np.int64)
    r.c = np.array(res.c, dtype=np.int64)
    r.checks = instance_B(S, M, res, inst, l, deltacalc, oC)
    rp = replay(M, T, r.p, r.c, res.X)
    r.self_replay_ok = bool(rp["survived"] and rp["first_invalid"] is None and rp["e"] == res.pivot_vals)
    nb = (S.n + 7) // 8
    R, C = M.shape
    nnz_full = int((M != 0).sum())
    keep = np.ones(R, dtype=bool)
    keep[res.Z] = False
    Mk = M[keep]
    cols_pruned = int((Mk != 0).any(axis=0).sum()) if Mk.shape[0] else 0
    rows_pruned = int(keep.sum())
    r.sizes = {
        "bytes_per_entry": nb,
        "full": {"rows": R, "cols": C, "dense_bytes": R * C * nb, "nnz": nnz_full},
        "pruned": {"rows": rows_pruned, "cols": cols_pruned, "dense_bytes": rows_pruned * cols_pruned * nb,
                   "nnz": int((Mk != 0).sum())},
        "compare_32_B": 32, "compare_233472_B": 233472,
    }
    ops_masked_full = R * C * (C + 1) // 2
    r.M = None   # the dense matrix is rebuilt when needed (memory; AMD reply E)
    r.saving = {"unit": "one F_{2^n} multiply-add",
                "ops_masked_full": ops_masked_full, "ops_strict": res.ops_strict_B,
                "saving_strict": ops_masked_full / res.ops_strict_B if res.ops_strict_B else None,
                "ops_set": "NOT DEFINED in regime B (spec); not reported"}
    return r


def ref_summary_B(r):
    res = r.res
    return {"label": r.label, "group": r.group, "x_R": r.inst.get("x_R"), "coeffs": list(r.inst["coeffs"]),
            "s": r.inst["s"], "rank": res.rank, "one_in_R": r.checks["one_in_R"],
            "h_rank": res.h_rank, "h_set": res.h_set, "h_strict": res.h_strict, "h_ops": res.h_ops,
            "len_strict": len(res.p), "Z_size": len(res.Z), "cpass": r.cpass,
            "self_replay_ok": r.self_replay_ok, "first_nonpivot_col": res.first_nonpivot_col,
            "checks": r.checks, "sizes": r.sizes, "saving": r.saving,
            "T_strict": [[int(p), int(c)] for p, c in zip(res.p, res.c)],
            "pivcols": res.pivcols, "Z": res.Z}


def compare_B(tres, tp, tc, ref, col_deg, anomalies, tag, cls):
    rres = ref.res
    m = {"rank": tres.rank == rres.rank}
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
    if (tres.h_strict == rres.h_strict) != strict_content:
        anomalies.append({"where": tag, "granularity": "strict", "hash_equal": tres.h_strict == rres.h_strict,
                          "content_equal": strict_content})
    m["strict"] = strict_content
    if tres.h_ops == rres.h_ops:
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
    out = {"match": m, "kdiv": kdiv, "f_div": kdiv / Lr if Lr else None, "div_col": dcol,
           "div_deg": int(col_deg[dcol]) if dcol is not None else None, "len_t": int(len(tp))}
    if strict_content:
        out["type"] = "MATCH"
        out["rule"] = "R0"
        out["prefix_flag"] = False
        if cls is not None:
            anomalies.append({"where": tag, "issue": "classified although T_strict matches", "cls": cls})
    else:
        if cls is None:
            anomalies.append({"where": tag, "issue": "no in-pass classification for a divergence"})
            out["type"] = "UNCLASSIFIED"
            out["rule"] = "R6"
            out["prefix_flag"] = False
        else:
            if cls["k"] != kdiv:
                anomalies.append({"where": tag, "issue": "classification step != kdiv", "k": cls["k"], "kdiv": kdiv})
            out["type"] = cls["type"]
            out["rule"] = cls["rule"]
            out["prefix_flag"] = cls["prefix_flag"]
            out["p_ref"], out["c_ref"] = cls.get("p_ref"), cls.get("c_ref")
            out["p_t"], out["c_t"] = cls.get("p_t"), cls.get("c_t")
            out["div_col"] = cls["div_col"]
            out["div_deg"] = int(col_deg[cls["div_col"]])
    return out


_G = {}


def set_unit_globals(**kw):
    _G.clear()
    _G.update(kw)


def target_record_B(t):
    S, T = _G["S"], _G["T"]
    fam, l = _G["fam"], _G["l"]
    cmp_refs = [(k, r) for k, r in _G["cmp_refs"] if not (k == "modal" and t["idx"] <= 100)]
    reverse = _G["reverse"]
    anomalies = []
    M = S.build(t["coeffs"], reverse=reverse)
    refs_arg = [(k, r.p, r.c) for k, r in cmp_refs]
    res, cpass, leads = eliminate(M, T, refs=refs_arg)
    tp = np.array(res.p, dtype=np.int64)
    tc = np.array(res.c, dtype=np.int64)
    chk = instance_B(S, M, res, t, l, _G["deltacalc"], _G["oC"]) if not reverse else {
        "one_in_R": S.const_col in set(res.c)}
    rec = {"family": fam, "regime": "B", "D": S.D, "idx": t["idx"], "x_R": t.get("x_R"),
           "coeffs": list(t["coeffs"]) if t.get("x_R") is None else None,
           "degenerate": bool(t.get("degenerate")),
           "stratum": "degenerate" if t.get("degenerate") else ("sat" if t["s"] >= 1 else "unsat"),
           "s": t["s"], "x2E_class": t.get("x2E_class"),
           "rank": res.rank, "Z_size": len(res.Z),
           "h_rank": res.h_rank, "h_set": res.h_set, "h_strict": res.h_strict, "h_ops": res.h_ops,
           "len_strict": len(tp), "cpass": cpass, "first_nonpivot_col": res.first_nonpivot_col,
           "pivcols_hash": sha(canon(res.pivcols)), "refs": {}}
    rec.update(chk)
    for key, r in cmp_refs:
        d = compare_B(res, tp, tc, r, S.col_deg, anomalies, f"B/{fam}/t{t['idx']}/{key}", res.classif.get(key))
        # AMD-20260924-3a9f06 C-2: E3 success = R3 COLUMN at the target's own first non-pivot column
        d["E3_success"] = bool(d.get("type") == "COLUMN" and d.get("c_ref") == res.first_nonpivot_col)
        # rejected PREFIX-first reading (sensitivity only): COLUMN at the first non-pivot column and no prefix
        d["E3_prefix_first_sensitivity"] = bool(d["E3_success"] and not d.get("prefix_flag"))
        rec["refs"][key] = d
    rec["_anomalies"] = anomalies
    if _G.get("keep_sets"):
        rec["_pivcols"] = res.pivcols
    return rec


def process_family_B(S, T, fam, ref_insts, targets, reverse, cross, log, mapper, l, deltacalc, oC,
                     modal_enabled=True, keep_oplogs=False):
    t0 = time.time()
    own = []
    for inst in ref_insts:
        M = S.build(inst["coeffs"], reverse=reverse)
        own.append(make_ref_B(S, T, M, inst, inst["selected_as"], "own", l, deltacalc, oC))
    cmp_refs = [(r.label, r) for r in own] + list(cross)
    common = dict(S=S, T=T, fam=fam, l=l, reverse=reverse, deltacalc=deltacalc, oC=oC)
    set_unit_globals(cmp_refs=cmp_refs, **common)
    first = [t for t in targets if t["idx"] <= 100]
    rest = [t for t in targets if t["idx"] > 100]
    records = mapper(target_record_B, first)
    modal, modal_info = None, None
    n_nd = sum(1 for t in targets if not t.get("degenerate"))
    if modal_enabled and own and n_nd > 100:
        f100 = [(r["idx"], r["h_set"]) for r in records if not r["degenerate"]]
        if f100:
            midx, mh, mcount, ndistinct = determine_modal(f100)
            inst = next(t for t in targets if t["idx"] == midx)
            modal = make_ref_B(S, T, S.build(inst["coeffs"], reverse=reverse), inst, "modal", "own", l,
                               deltacalc, oC)
            modal_info = {"modal_idx": midx, "modal_h_set": mh, "modal_class_size_in_1_100": mcount,
                          "distinct_T_set_in_1_100": ndistinct, "stratum": "sat" if inst["s"] >= 1 else "unsat"}
    cmp2 = cmp_refs + ([("modal", modal)] if modal is not None else [])
    set_unit_globals(cmp_refs=cmp2, **common)
    records += mapper(target_record_B, rest)
    anomalies = []
    for rec in records:
        anomalies += rec.pop("_anomalies")
    refs_out = [ref_summary_B(r) for r in own]
    if modal is not None:
        ms = ref_summary_B(modal)
        ms["modal_info"] = modal_info
        ms["instance_idx"] = modal.inst["idx"]
        refs_out.append(ms)
    oplogs = None
    if keep_oplogs:
        oplogs = [(r.label, r.inst, [[int(p), int(c), delta_encode(X)] for p, c, X in zip(r.res.p, r.res.c, r.res.X)])
                  for r in own if r.label.startswith("U")]
    log(f"    B {fam}{' REV' if reverse else ''}: {len(records)} targets ({time.time() - t0:.0f}s)")
    result = {"regime": "B", "family": fam, "D": S.D, "reverse": reverse, "refs": refs_out, "records": records,
              "hash_anomalies": anomalies, "modal_info": modal_info, "wall_seconds": time.time() - t0}
    live = own + ([modal] if modal is not None else [])
    return result, live, oplogs


# ---------------------------------------------------------------------------
# phase 4: replays, K_B probes, C-BREAK
def kb_probes(S, T, ref, coeff_fn, g, q, max_draws=10, want=3, draw_log=None):
    """K_B by the T_STRICT-GUIDED computation (AMD-20260924-3a9f06 C-6).
    Probes x = g.integers(0, q) (the F-RANDX uniform-x routine) drawn in order
    from the ONE S_probe generator; a probe is SKIPPED iff its guided
    computation stops (x is a root of some Delta_{k+1}); each draw counts
    toward max_draws. K_B = #steps whose pivot entry is not identical across
    the reference and its accepted probes."""
    import hashlib
    probes = []
    tried = []
    gref = guided(S.build(coeff_fn(ref.inst["x_R"])), T, ref.p, ref.c)
    ref_e = gref["e"]
    for _ in range(max_draws):
        if len(probes) >= want:
            break
        x = int(g.integers(0, q))
        if draw_log is not None:
            draw_log.append(x)
        gd = guided(S.build(coeff_fn(x)), T, ref.p, ref.c)
        ok = gd["broke_at"] is None
        tried.append({"draw_index": (len(draw_log) - 1) if draw_log is not None else None,
                      "x_sha256": hashlib.sha256(str(x).encode()).hexdigest(), "x": x,
                      "accepted": ok, "breaks_at": gd["broke_at"]})
        if ok:
            probes.append(gd["e"])
    out = {"tried": tried, "probes_accepted": len(probes), "L": len(ref.p),
           "reference_guided_equals_own": ref_e == list(ref.res.pivot_vals)}
    if not probes:
        out["K_B"] = None
        out["note"] = "not estimable: every probe skipped within the draw limit"
        return out
    E = np.array([ref_e] + probes, dtype=np.int64)
    varying = (E != E[0:1]).any(axis=0)
    out["K_B"] = int(varying.sum())
    out["varying_steps_first50"] = np.flatnonzero(varying)[:50].tolist()
    if len(probes) < want:
        out["note"] = f"K_B from {len(probes)} accepted probes (fewer than {want})"
    return out


def replayb_v2(S, T, DF, ref, matched_insts, max_attrib=20):
    """C-REPLAYB (v2), AMD-20260924-3a9f06 C-4, for one unsat reference:
    (a) guided = own on the reference and every matched target;
    (b) the v1 fixed replay is schedule-valid iff X_k^t subset of X_k^r for all k,
        otherwise first invalid at k*, no zero pivot before k*, pivot entries
        before k* equal the target's own;
    (c) each distinct (k, i), i in X_k^t minus X_k^r, verified by the independent
        determinant module (minor on {p_0..p_{k-1}, i} x {c_0..c_k} is 0 at x_r and
        nonzero at the lowest-idx matched target exhibiting it); all of them, or
        the 20 with the smallest k if more (total recorded);
    (d) data: verified coincidental zeros, #schedule-valid, k* distribution."""
    fails = []
    Mr = S.build(ref.inst["coeffs"])
    rX = [set(int(v) for v in X) for X in ref.res.X]
    gr = guided(Mr, T, ref.p, ref.c)
    a_ref = (gr["broke_at"] is None and gr["e"] == list(ref.res.pivot_vals)
             and all(set(int(v) for v in cX) == x for cX, x in zip(gr["cleared"], rX)))
    if not a_ref:
        fails.append({"item": "a", "on": "reference"})
    per_t = []
    attrib = {}
    for t in matched_insts:
        Mt = S.build(t["coeffs"])
        own, _, _ = eliminate(Mt, T, with_row_pass=False)
        if not (list(own.p) == list(ref.p) and list(own.c) == list(ref.c)):
            fails.append({"item": "precondition", "idx": t["idx"], "issue": "not T_strict-matched"})
            continue
        tX = [set(int(v) for v in X) for X in own.X]
        g = guided(Mt, T, ref.p, ref.c)
        a_ok = (g["broke_at"] is None and g["e"] == list(own.pivot_vals)
                and all(set(int(v) for v in cX) == x for cX, x in zip(g["cleared"], tX)))
        if not a_ok:
            fails.append({"item": "a", "idx": t["idx"]})
        kstar = None
        for k in range(len(tX)):
            if not tX[k] <= rX[k]:
                kstar = k
                break
        rp = replay(Mt, T, ref.p, ref.c, ref.res.X, stop_at_zero=True)
        pred_valid = kstar is None
        b_ok = True
        if pred_valid:
            b_ok = rp["first_invalid"] is None and rp["survived"] and rp["e"] == list(own.pivot_vals)
        else:
            zero_before = rp["first_zero"] is not None and rp["first_zero"] < kstar
            b_ok = (rp["first_invalid"] == kstar and not zero_before and rp["e"][:kstar] == list(own.pivot_vals)[:kstar])
        if not b_ok:
            fails.append({"item": "b", "idx": t["idx"], "k_star": kstar, "first_invalid": rp["first_invalid"],
                          "first_zero": rp["first_zero"]})
        if kstar is not None:
            for k in range(len(tX)):
                for i in sorted(tX[k] - rX[k]):
                    attrib.setdefault((k, i), t)
        per_t.append({"idx": t["idx"], "k_star": kstar, "schedule_valid": pred_valid,
                      "replay_first_invalid": rp["first_invalid"], "replay_first_zero": rp["first_zero"],
                      "a_pass": a_ok, "b_pass": b_ok})
    keys = sorted(attrib)
    checked = keys[:max_attrib]
    verified = []
    for (k, i) in checked:
        t = attrib[(k, i)]
        rows = list(ref.p[:k]) + [i]
        cols = list(ref.c[:k + 1])
        d_ref = minor(Mr, rows, cols, DF)
        d_t = minor(S.build(t["coeffs"]), rows, cols, DF)
        ok = d_ref == 0 and d_t != 0
        verified.append({"k": int(k), "i": int(i), "c_k": int(ref.c[k]), "target_idx": t["idx"],
                         "minor_at_x_ref": int(d_ref), "minor_at_target": int(d_t), "pass": ok})
        if not ok:
            fails.append({"item": "c", "k": int(k), "i": int(i)})
    ks = [x["k_star"] for x in per_t if x["k_star"] is not None]
    return {"pass": not fails, "failures": fails, "reference_a_pass": a_ref, "per_target": per_t,
            "n_matched_checked": len(per_t), "n_schedule_valid": sum(x["schedule_valid"] for x in per_t),
            "k_star_distribution": dict(Counter(ks)),
            "attributed_zeros_total": len(keys), "attributed_zeros_checked": len(checked),
            "verified_coincidental_zeros": verified,
            "label": "X-ZERO REFERENCE" if keys else None}


def cbreak_check(M_orig, ref, k, DF):
    """Minor on rows p_0..p_k, cols c_0..c_k is 0 and minor on p_0..p_{k-1},
    c_0..c_{k-1} is not (independent determinant module)."""
    d1 = minor(M_orig, ref.p[:k + 1], ref.c[:k + 1], DF)
    d0 = minor(M_orig, ref.p[:k], ref.c[:k], DF)
    return {"k": int(k), "minor_k_plus_1": int(d1), "minor_k": int(d0), "pass": d1 == 0 and d0 != 0}
