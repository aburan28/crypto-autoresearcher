#!/usr/bin/env python3
"""TASK-20260923-b8f163, joint J3: metric and decision-rule recomputation with
the validator's OWN aggregation, written from specification.yaml "metrics" and
"decision_rules" before reading the producer's aggregation code or outputs.

Inputs (committed bytes): targets-*.jsonl.gz, references.json,
F-S3-reference-oplogs-D4.jsonl.gz, curve.json. Does NOT import or run
analysis.py or report.py, and uses no impl/ module. M2 uses the validator's own
affine forms (the archived op logs replayed on the validator's own M_4(E^0),
M_4(E^j); see j1-constructions), evaluated on every F-S3 target.

Writes j3_recompute.json (all numbers) next to this file. The comparison with
the producer's decision-rules.json / cell-summary.json / pivot-hazards.json /
sizing.json is a SEPARATE script (j3_compare.py), run afterwards.
Zero trials; no RUN-id.
"""
import gzip
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict

import mpmath

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "j1-constructions"))
import j1_spec_literal as J  # noqa: E402  (validator's own construction code)

RUN = J.RUN
FAMS = ["F-S3", "F-S3-REV", "F-PLANT", "F-RANDX", "F-AFF-1", "F-AFF-2", "F-AFF-3", "F-NULLF2"]
GR = ("rank", "set", "strict", "ops")
T0 = time.time()


def log(m):
    print(f"[{time.time() - T0:7.1f}s] {m}", flush=True)


# ---------------------------------------------------------------------------
# statistics (own)
def cp95(x, n, alpha=0.05):
    """Clopper-Pearson via the regularized incomplete beta (mpmath)."""
    if n == 0:
        return None
    def q(a, b, p):
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(80):
            mid = (lo + hi) / 2
            if mpmath.betainc(a, b, 0, mid, regularized=True) < p:
                lo = mid
            else:
                hi = mid
        return float((lo + hi) / 2)
    lo = 0.0 if x == 0 else q(x, n - x + 1, alpha / 2)
    hi = 1.0 if x == n else q(x + 1, n - x, 1 - alpha / 2)
    return [lo, hi]


def wilson95(x, n, z=1.959963984540054):
    if n == 0:
        return None
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def median(v):
    s = sorted(v)
    n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def lower_median(v):
    s = sorted(v)
    return s[(len(s) - 1) // 2] if s else None


def plugin_entropy(labels):
    c = Counter(labels)
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values()), len(c), n, max(c.values())


def h2(p):
    return 0.0 if p <= 0 or p >= 1 else -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


# ---------------------------------------------------------------------------
def load():
    recs = {}
    for f in FAMS:
        with gzip.open(os.path.join(RUN, f"targets-{f}.jsonl.gz"), "rt") as fh:
            recs[f] = [json.loads(line) for line in fh]
    refs = json.load(open(os.path.join(RUN, "references.json")))
    return recs, refs


def modal_rule(recs_fd):
    """spec modal_reference_rule: most frequent T_set among test targets 1..100
    (draw order, non-degenerate); tie -> the T_set whose first occurrence has the
    lowest index; modal instance = lowest-index target with that T_set."""
    win = sorted((r for r in recs_fd if r["idx"] <= 100 and not r["degenerate"]), key=lambda r: r["idx"])
    cnt, first = Counter(), {}
    for r in win:
        cnt[r["h_set"]] += 1
        first.setdefault(r["h_set"], r["idx"])
    best = sorted(cnt, key=lambda h: (-cnt[h], first[h]))[0]
    return {"modal_idx": first[best], "class_size": cnt[best], "distinct": len(cnt), "window_nondeg": len(win)}


def modal_rule_first100_nondeg(recs_fd):
    """ALTERNATIVE reading (I-4/I-modal): the first 100 NON-DEGENERATE targets."""
    win = sorted((r for r in recs_fd if not r["degenerate"]), key=lambda r: r["idx"])[:100]
    cnt, first = Counter(), {}
    for r in win:
        cnt[r["h_set"]] += 1
        first.setdefault(r["h_set"], r["idx"])
    best = sorted(cnt, key=lambda h: (-cnt[h], first[h]))[0]
    return {"modal_idx": first[best], "class_size": cnt[best], "distinct": len(cnt), "last_idx_in_window": win[-1]["idx"]}


def ref_hash(refs, fam, lab, D, g):
    return refs[fam]["references"][lab][f"D{D}"][f"h_{g}"]


def retention(recs_fd, refs, fam, lab, D, g, arm, include_degenerate=False, modal_min_idx=101):
    """#{targets t in arm : T_g(t) = T_g(ref)} / #arm; the modal reference scores
    targets 101..1000 only. Matches by hash equality against references.json AND
    by the archived per-target content flag; both are returned."""
    key = lab
    pool = [r for r in recs_fd if (include_degenerate or not r["degenerate"])
            and ((r["s"] == 0) if arm == "unsat" else (r["s"] >= 1))]
    if lab == "modal":
        pool = [r for r in pool if r["idx"] >= modal_min_idx]
    hr = ref_hash(refs, fam, lab, D, g)
    x_hash = sum(1 for r in pool if r[f"h_{g}"] == hr)
    x_flag = sum(1 for r in pool if key in r["refs"] and r["refs"][key]["match"][g]) if lab != "modal" or modal_min_idx == 101 else None
    return x_hash, x_flag, len(pool)


def forms_for_refs(B, oplogs, labels):
    """Own exact affine forms e_k(r) = a0_k + <a_k, r> at D = 4."""
    cols, _ = J.column_order_literal(4)
    mus, _ = J.row_order_literal(4)
    colidx = {m: i for i, m in enumerate(cols)}
    f0 = J.equations_from_coef(J.descent_mobius(B, 0))
    fj = []
    for j in range(17):
        fx = J.equations_from_coef(J.descent_mobius(B, 1 << j))
        fj.append([fx[k].symmetric_difference(f0[k]) for k in range(17)])
    rows0 = J.macaulay_rows(f0, mus, colidx)
    rowsj = [J.macaulay_rows(fj[j], mus, colidx) for j in range(17)]
    out = {}
    for lab in labels:
        ol = oplogs[lab]
        a0 = J.replay(rows0, ol)
        a = [0] * len(ol)
        for j in range(17):
            ej = J.replay(rowsj[j], ol)
            for k in range(len(ol)):
                a[k] |= ej[k] << j
        out[lab] = (a0, a)
    return out, (cols, mus, colidx)


def eval_e(a0, a, r):
    return [a0[k] ^ (bin(a[k] & r).count("1") & 1) for k in range(len(a))]


def hazards(evecs, K):
    """S_k, zeros_k, h_k from full e vectors (lists of 0/1) of the scored targets."""
    fz = []
    for e in evecs:
        z = next((k for k in range(K) if e[k] == 0), K)
        fz.append(z)
    cnt = Counter(fz)
    S = [0] * K
    run = len(fz)
    for k in range(K):
        S[k] = run
        run -= cnt.get(k, 0)
    Z = [cnt.get(k, 0) for k in range(K)]
    return S, Z, fz


def main():
    recs, refs = load()
    curve = json.load(open(os.path.join(RUN, "curve.json")))
    B = curve["B"]
    out = {"task": "TASK-20260923-b8f163", "joint": "J3", "order_note": "J1 section sealed at 2026-09-23T20:47:49Z before this script was written"}
    byfd = {(f, D): [r for r in recs[f] if r["D"] == D] for f in FAMS for D in (3, 4)}

    # ---- modal re-derivation
    md = {}
    for f in FAMS:
        for D in (3, 4):
            mine = modal_rule(byfd[(f, D)])
            alt = modal_rule_first100_nondeg(byfd[(f, D)])
            arch = refs[f]["references"].get("modal", {}).get("instance_idx_per_D", {}).get(f"D{D}")
            md[f"{f}/D{D}"] = {"mine": mine, "alt_first100_nondeg": alt, "archived_modal_idx": arch,
                               "equal": mine["modal_idx"] == arch}
    out["modal_rederivation"] = md
    log("modal re-derived")

    # ---- arms, M1 at every granularity, both D, every family
    ret = {}
    flag_hash_disagree = 0
    for f in FAMS:
        labs = [l for l in ("U1", "U2", "U3", "S1", "S2", "modal") if l in refs[f]["references"]]
        for D in (3, 4):
            for g in GR:
                for lab in labs:
                    for arm in ("unsat", "sat"):
                        xh, xf, n = retention(byfd[(f, D)], refs, f, lab, D, g, arm)
                        if xf is not None and xf != xh:
                            flag_hash_disagree += 1
                        ret[f"{f}/D{D}/{g}/{lab}/{arm}"] = {"x": xh, "n": n, "r": (xh / n if n else None), "flag_count": xf}
    out["retention"] = ret
    out["retention_hash_vs_flag_disagreements"] = flag_hash_disagree
    log(f"retention done; hash/flag disagreements {flag_hash_disagree}")

    def rfam(f, D, g, labs=("U1", "U2", "U3", "modal"), arm="unsat"):
        vals = [(lab, ret[f"{f}/D{D}/{g}/{lab}/{arm}"]) for lab in labs if f"{f}/D{D}/{g}/{lab}/{arm}" in ret]
        best = max(vals, key=lambda kv: (kv[1]["r"] if kv[1]["r"] is not None else -1))  # first max in order
        return {"value": best[1]["r"], "argmax_first": best[0], "count": best[1]["x"], "n": best[1]["n"],
                "per_ref": {lab: [v["x"], v["n"], v["r"], cp95(v["x"], v["n"]) if (g == "strict" and D == 4) else None] for lab, v in vals}}

    M1 = {}
    for f in FAMS:
        if f == "F-PLANT":
            continue
        for D in (3, 4):
            for g in GR:
                M1[f"{f}/D{D}/{g}"] = rfam(f, D, g)
    out["retention_family"] = M1
    log(f"F-S3 D4 strict retention_family: {M1['F-S3/D4/strict']}")

    # ---- M3
    num = M1["F-S3/D4/strict"]
    dens = [M1[f"F-AFF-{d}/D4/strict"] for d in (1, 2, 3)]
    m3 = {"numerator": num["value"], "numerator_count": num["count"],
          "denominators": [d["value"] for d in dens], "denominator_counts": [d["count"] for d in dens],
          "per_draw_ratio": [(num["value"] / d["value"] if d["value"] else None) for d in dens]}
    nc, dc = num["count"], [d["count"] for d in dens]
    # spec ratio rule, bullets in the written order; overlap noted
    if nc == 0 and all(c == 0 for c in dc):
        m3["case"] = "numerator 0 AND all denominators 0 (bullets 1 and 3 both literally apply)"
        m3["reading_bullet1_first"] = {"kind": "zero", "value": 0.0, "E2_ge10_met": False}
        m3["reading_bullet3"] = {"kind": "not_estimable", "E1_[0.5,2]_clause": "not evaluable"}
    elif nc == 0:
        m3["case"] = "numerator 0"
        m3["reading_bullet1_first"] = {"kind": "zero", "value": 0.0, "E2_ge10_met": False}
    elif all(c == 0 for c in dc):
        pooled_n = sum(d["n"] for d in dens)
        ub = cp95(0, pooled_n)[1]
        m3["case"] = "lower bound"
        m3["lower_bound"] = num["value"] / ub
    else:
        m3["case"] = "point"
        mean_den = sum(d["value"] for d in dens) / 3
        m3["point"] = num["value"] / mean_den
    out["M3"] = m3
    log(f"M3 {m3}")

    # ---- M4
    m4 = {}
    for f in FAMS:
        for D in (3, 4):
            nd = [r for r in byfd[(f, D)] if not r["degenerate"]]
            psat = sum(1 for r in nd if r["s"] >= 1) / len(nd)
            m4[f"{f}/D{D}"] = {"N": len(nd), "P_sat": psat, "h_P_sat": h2(psat)}
            for g in GR:
                H, dist, N, mx = plugin_entropy([r[f"h_{g}"] for r in nd])
                m4[f"{f}/D{D}"][g] = {"H_bits": H, "distinct": dist, "largest_class": mx, "log2N": math.log2(N)}
    out["M4"] = m4
    log(f"M4 F-S3 D4: {m4['F-S3/D4']}")

    # ---- M2 from own affine forms
    oplogs = {}
    with gzip.open(os.path.join(RUN, "F-S3-reference-oplogs-D4.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            oplogs.setdefault(r["ref"], []).append(r)
    for lab in oplogs:
        lst = sorted(oplogs[lab], key=lambda r: r["k"])
        oplogs[lab] = [(r["p"], r["c"], r["X"]) for r in lst]
    labels5 = ["U1", "U2", "U3", "S1", "S2"]
    forms, geo = forms_for_refs(B, oplogs, labels5 + ["modal"])
    log("own forms built")
    tg4 = sorted(byfd[("F-S3", 4)], key=lambda r: r["idx"])
    fz_mismatch = 0
    M2 = {"per_ref": {}, "P2": []}
    Esets = {}
    for lab in labels5 + ["modal"]:
        a0, a = forms[lab]
        K = len(a)
        E_all = {r["idx"]: eval_e(a0, a, r["x_R"]) for r in tg4}
        Esets[lab] = E_all
        # archived per-target replay_first_zero vs own
        for r in tg4:
            if lab in r["refs"]:
                fz = next((k for k in range(K) if E_all[r["idx"]][k] == 0), K)
                fz_mismatch += fz != r["refs"][lab]["replay_first_zero"]
        scored = [r for r in tg4 if not r["degenerate"] and (lab != "modal" or r["idx"] > 100)]
        ev = [E_all[r["idx"]] for r in scored]
        S, Z, fz = hazards(ev, K)
        dep = [len({e[k] for e in ev}) == 2 for k in range(K)]
        M2["per_ref"][lab] = {"K": K, "n_scored": len(scored), "K_sampled": sum(dep),
                              "K_exact": sum(1 for x in a if x), "full_survivors": S[K - 1] - Z[K - 1] if K else None}
        if lab in labels5:
            for k in range(K):
                if dep[k] and S[k] >= 200:
                    h = Z[k] / S[k]
                    M2["P2"].append({"ref": lab, "k": k, "S_k": S[k], "zeros": Z[k], "h": h, "wilson95": wilson95(Z[k], S[k]),
                                     "a_k_nonzero": a[k] != 0})
    out["replay_first_zero_mismatches_vs_archive"] = fz_mismatch
    hs = [p["h"] for p in M2["P2"]]
    M2["pooled"] = {"n_pairs": len(hs), "median": median(hs), "lower_median": lower_median(hs),
                    "frac_in_[0.4,0.6]": (sum(1 for h in hs if 0.4 <= h <= 0.6) / len(hs)) if hs else None,
                    "n_in_band": sum(1 for h in hs if 0.4 <= h <= 0.6), "n_h_zero": sum(1 for h in hs if h == 0),
                    "min": min(hs) if hs else None, "max": max(hs) if hs else None}
    for lab in labels5:
        hh = [p["h"] for p in M2["P2"] if p["ref"] == lab]
        M2["per_ref"][lab]["P2"] = {"n": len(hh), "median": median(hh),
                                    "frac_in_band": (sum(1 for h in hh if 0.4 <= h <= 0.6) / len(hh)) if hh else None,
                                    "h": [round(x, 6) for x in hh]}
    out["M2"] = M2
    log(f"M2 pooled {M2['pooled']}; fz mismatches vs archive {fz_mismatch}")

    # ---- sizes and savings from own construction (refs at D = 4 and D = 3)
    sz = {}
    for D in (3, 4):
        cols, _ = J.column_order_literal(D)
        mus, _ = J.row_order_literal(D)
        colidx = {m: i for i, m in enumerate(cols)}
        opl = {}
        with gzip.open(os.path.join(RUN, f"F-S3-reference-oplogs-D{D}.jsonl.gz"), "rt") as fh:
            for line in fh:
                r = json.loads(line)
                opl.setdefault(r["ref"], []).append(r)
        for lab in labels5 + ["modal"]:
            if lab == "modal":
                idx = refs["F-S3"]["references"]["modal"]["instance_idx_per_D"][f"D{D}"]
                xR = next(r["x_R"] for r in byfd[("F-S3", D)] if r["idx"] == idx)
            else:
                xR = refs["F-S3"]["references"][lab]["x_R"]
            f = J.equations_from_coef(J.descent_mobius(B, xR))
            rows = J.macaulay_rows(f, mus, colidx)
            Z, leads = J.zero_reduction_set(rows)
            R, C = len(rows), len(cols)
            rank = R - len(Z)
            Zs = set(Z)
            keep = [v for i, v in enumerate(rows) if i not in Zs]
            orv = 0
            for v in keep:
                orv |= v
            nnz_full = sum(bin(v).count("1") for v in rows)
            nnz_p = sum(bin(v).count("1") for v in keep)
            cols_p = bin(orv).count("1")
            ops_strict = sum(len(r["X"]) for r in opl[lab])
            ops_full = C * R
            ops_set = len(leads) * (R - len(Z))
            sz[f"D{D}/{lab}"] = {
                "R": R, "C": C, "rank": rank, "Z": len(Z), "pivot_cols": len(leads),
                "full": {"dense_bytes": R * C / 8, "nnz": nnz_full, "csr_bytes": 4 * nnz_full + 4 * (R + 1)},
                "pruned": {"rows": len(keep), "cols": cols_p, "dense_bytes": len(keep) * cols_p / 8, "nnz": nnz_p,
                           "csr_bytes": 4 * nnz_p + 4 * (len(keep) + 1)},
                "ops_masked_full": ops_full, "ops_strict": ops_strict, "ops_set": ops_set,
                "saving_strict": ops_full / ops_strict, "saving_set": ops_full / ops_set,
                "identity_ops_set_eq_rank_sq": ops_set == rank * rank,
                "identity_saving_set_exact": ops_full * rank * rank == C * R * ops_set,
                "words_per_row": (C + 63) // 64}
    out["sizes_savings"] = sz
    log(f"sizes D4/U1 {sz['D4/U1']}")

    # =====================================================================
    # decision rules, applied to the validator's numbers (as-run readings)
    # =====================================================================
    def p2_stats(pairs):
        hs = [p["h"] for p in pairs]
        if not hs:
            return {"n": 0, "median": None, "frac_in_band": None, "evaluable": False}
        return {"n": len(hs), "median": median(hs), "lower_median": lower_median(hs),
                "frac_in_band": sum(1 for h in hs if 0.4 <= h <= 0.6) / len(hs),
                "n_in_band": sum(1 for h in hs if 0.4 <= h <= 0.6), "n_zero": sum(1 for h in hs if h == 0), "evaluable": True}

    def apply_rules(rf, m1_per_ref, p2, m3_reading, maxref, K_max, sizes_max, mode="as_run"):
        """mode 'as_run' = I-24 as written in the trial plan; 'strict_ne' = any
        non-evaluable clause makes DR-2 'not evaluable'."""
        v = {}
        v["DR-1"] = ("STRICT P-GPU FALSIFIED at this cell" if all(m1_per_ref[l] < 0.5 for l in ("U1", "U2", "U3", "modal"))
                     else "not falsified")
        # M3 predicates
        kind = m3_reading["kind"]
        m3_ge10 = {"zero": False, "point": (m3_reading.get("value", 0) >= 10), "lower_bound": (m3_reading.get("value", 0) >= 10),
                   "not_estimable": None}[kind]
        m3_in_05_2 = {"zero": False, "point": (0.5 <= m3_reading.get("value", 0) <= 2), "lower_bound": None,
                      "not_estimable": "not evaluable"}[kind]
        m3_lt10 = {"zero": True, "point": (m3_reading.get("value", 0) < 10), "lower_bound": None, "not_estimable": None}[kind]
        med = p2["median"]
        fal = [rf >= 0.5, (med < 0.2) if p2["evaluable"] else None, m3_ge10]
        con = [rf <= 0.01, (p2["frac_in_band"] >= 0.9) if p2["evaluable"] else None,
               True if m3_in_05_2 == "not evaluable" else m3_in_05_2]
        if any(c is True for c in fal):
            v["DR-2"] = "E1 FALSIFIED"
        elif mode == "strict_ne" and (any(c is None for c in fal) or any(c is None for c in con)):
            v["DR-2"] = "not evaluable"
        elif all(c is True for c in con):
            v["DR-2"] = "E1 CONSISTENT"
        elif any(c is False for c in con) and not any(c is None for c in fal):
            v["DR-2"] = "between"
        else:
            v["DR-2"] = "not evaluable" if all(c is None for c in con) else "between"
        v["DR-2_clauses"] = {"falsify": fal, "consistent": con}
        # DR-3
        sup = rf >= 0.5 and m3_ge10 is True and K_max <= 1
        falsified = (rf < 0.5) or (m3_lt10 is True)
        v["DR-3"] = "E2 SUPPORTED" if sup else ("E2 FALSIFIED" if falsified else "not decided (M3 clause unknown)")
        # DR-4
        if not p2["evaluable"]:
            v["DR-4"] = "not evaluable"
        elif med < 0.2:
            v["DR-4"] = "H1 FALSIFIED"
        elif p2["frac_in_band"] >= 0.9:
            v["DR-4"] = "H1 SUPPORTED at this cell"
        else:
            v["DR-4"] = "not supported, not falsified"
        # DR-5
        if 0.01 < rf < 0.5:
            v["DR-5"] = "E2-leaning" if m3_ge10 else ("E1-leaning" if kind in ("zero", "point") and m3_reading.get("value", 0) <= 2 else "undetermined")
        else:
            v["DR-5"] = "not applicable"
        # DR-6
        pb = sizes_max["pruned"]["dense_bytes"]
        v["DR-6"] = {"one_system_per_SM": "SURVIVES" if pb <= 233472 else "FAILS",
                     "thousands_per_warp": "FAILS" if pb > 32 else "does not fail", "pruned_dense_bytes": pb, "ref": maxref}
        # DR-7
        v["DR-7"] = {"strict_replay": "closed" if sizes_max["saving_strict"] < 1.5 else "not closed",
                     "T_set_replay": "closed" if sizes_max["saving_set"] < 1.5 else "not closed",
                     "saving_strict": sizes_max["saving_strict"], "saving_set": sizes_max["saving_set"], "ref": maxref}
        return v

    rf = M1["F-S3/D4/strict"]
    m1_per = {l: rf["per_ref"][l][2] for l in ("U1", "U2", "U3", "modal")}
    p2_as_run = p2_stats(M2["P2"])
    maxref = rf["argmax_first"]
    m3_as_run = (m3.get("reading_bullet1_first") or {"kind": m3["case"].split()[0]})
    if m3["case"] == "point":
        m3_as_run = {"kind": "point", "value": m3["point"]}
    elif m3["case"] == "lower bound":
        m3_as_run = {"kind": "lower_bound", "value": m3["lower_bound"]}
    DR = apply_rules(rf["value"], m1_per, p2_as_run, m3_as_run, maxref, M2["per_ref"][maxref]["K_sampled"], sz[f"D4/{maxref}"])
    DR["DR-8"] = "every verdict above is F-S3, D = 4, T_strict (DR-1..DR-5 primary); DR-6/DR-7 use D = 4 sizes of the maximizing reference"
    out["DR_validator"] = {"inputs": {"retention_family": rf["value"], "M1_per_ref": m1_per, "P2": p2_as_run,
                                      "M3_reading_used": m3_as_run, "maximizing_ref": maxref,
                                      "K_sampled_maxref": M2["per_ref"][maxref]["K_sampled"]}, "verdicts": DR}
    log(f"DR (validator): {json.dumps(DR)[:900]}")

    # =====================================================================
    # interpretation sensitivity
    # =====================================================================
    S = {}
    # ---- I-4: degenerate targets
    tg4_all = tg4
    def rf_incl_degenerate(D=4, g="strict"):
        vals = {}
        for lab in ("U1", "U2", "U3", "modal"):
            xh, _, n = retention(byfd[("F-S3", D)], refs, "F-S3", lab, D, g, "unsat", include_degenerate=True)
            vals[lab] = (xh, n, xh / n)
        return vals
    inc = rf_incl_degenerate()
    # P2 with degenerate targets scored
    def p2_variant(scored_filter, dep_basis="all_scored"):
        pairs = []
        for lab in labels5:
            a0, a = forms[lab]
            K = len(a)
            scored = [r for r in tg4_all if scored_filter(r)]
            ev = [Esets[lab][r["idx"]] for r in scored]
            Sx, Zx, _ = hazards(ev, K)
            if dep_basis == "all_scored":
                dep = [len({e[k] for e in ev}) == 2 for k in range(K)]
            elif dep_basis == "survivors":
                dep = [0 < Zx[k] < Sx[k] for k in range(K)]
            elif dep_basis == "all_nondeg":
                allnd = [Esets[lab][r["idx"]] for r in tg4_all if not r["degenerate"]]
                dep = [len({e[k] for e in allnd}) == 2 for k in range(K)]
            elif dep_basis == "rank_increasing":
                basis, dep = {}, []
                for k in range(K):
                    v, inc_ = a[k], False
                    while v:
                        hb = v.bit_length() - 1
                        if hb in basis:
                            v ^= basis[hb]
                        else:
                            basis[hb] = v
                            inc_ = True
                            break
                    dep.append(inc_)
            for k in range(K):
                if dep[k] and Sx[k] >= 200:
                    pairs.append({"ref": lab, "k": k, "S_k": Sx[k], "h": Zx[k] / Sx[k]})
        return pairs
    p2_incdeg = p2_stats(p2_variant(lambda r: True))
    S["I-4"] = {
        "as_run": "degenerate targets (x_R in V; 7 in F-S3) kept as a stratum and excluded from arms, entropy and M2",
        "alternative_A": "degenerate targets included in the arms, entropy and M2 pools",
        "alt_A_retention_unsat_D4_strict": inc,
        "alt_A_P2": p2_incdeg,
        "alternative_B": "degenerate draws replaced by further S_test draws (so 1000 non-degenerate targets)",
        "alt_B_bound": "cannot be computed without new eliminations (zero-trial task); bound: at most 7 added unsat targets, so the retention numerator rises by at most 7 on a denominator of at most 393",
        "alt_B_max_retention_family": 7 / (rf["n"] + 7),
        "P2_pairs_with_S_k_within_7_of_200": sum(1 for p in M2["P2"] if abs(p["S_k"] - 200) <= 7),
    }
    S["I-4"]["alt_A_verdicts"] = apply_rules(max(v[2] for v in inc.values()), {l: v[2] for l, v in inc.items()}, p2_incdeg, m3_as_run,
                                             maxref, M2["per_ref"][maxref]["K_sampled"], sz[f"D4/{maxref}"])
    # M4 including degenerate
    S["I-4"]["alt_A_M4_F-S3_D4_strict"] = dict(zip(("H_bits", "distinct", "N", "largest"), plugin_entropy([r["h_strict"] for r in byfd[("F-S3", 4)]])))

    # ---- I-5: reference-scan draw counting
    S["I-5"] = {"as_run": "every stream draw counts toward 500 (incl. rejected duplicates, degenerate, R = O redraws)",
                "alternative": "only classified candidates count toward 500",
                "fact": "the scans stopped after 9 (F-S3), 7 (F-RANDX), 40/17/18 (F-AFF-1..3) and 15 (F-NULLF2) draws with 3 unsat + 2 sat found; no scan approached 500, so every reading selects the same references (J2 regeneration reproduces the scans exactly)",
                "verdict_flip": False}

    # ---- I-11: maximizing reference
    alt11 = {}
    for lab in ("U1", "U2", "U3", "modal", "S1", "S2"):
        alt11[lab] = apply_rules(rf["value"], m1_per, p2_as_run, m3_as_run, lab, M2["per_ref"][lab]["K_sampled"], sz[f"D4/{lab}"])
    S["I-11"] = {"as_run": "argmax of unsat-arm T_strict retention at D = 4 over (U1, U2, U3, modal); ties to the first -> " + maxref,
                 "alternatives": "any of the tied references (all four M1 counts equal), or the sat references",
                 "verdicts_by_ref": {l: {"DR-3": v["DR-3"], "DR-6": v["DR-6"], "DR-7": v["DR-7"]} for l, v in alt11.items()}}

    # ---- I-12: M3 lower bound
    S["I-12"] = {"as_run": "pooled CP 95% upper bound over summed F-AFF unsat arms (0 successes)",
                 "alternative": "mean of per-draw CP upper bounds, or one-sided 97.5%",
                 "triggered": m3["case"] == "lower bound",
                 "note": "the lower-bound case arises only when the F-S3 numerator count is >= 1 and all F-AFF denominator counts are 0"}

    # ---- I-14: M2 membership / modal hazards
    nd = lambda r: not r["degenerate"]  # noqa: E731
    variants = {
        "as_run (dependence over all scored non-degenerate targets, arms pooled)": p2_variant(nd, "all_scored"),
        "alt: dependence over replay survivors (0 < zeros_k < S_k)": p2_variant(nd, "survivors"),
        "alt: S_k over the unsat arm only (dependence over that arm)": p2_variant(lambda r: nd(r) and r["s"] == 0, "all_scored"),
        "alt: S_k over the unsat arm only, dependence over all non-degenerate": p2_variant(lambda r: nd(r) and r["s"] == 0, "all_nondeg"),
        "READING (J4-owned, not a replacement rule): rank-increasing pivots only": p2_variant(nd, "rank_increasing"),
    }
    S["I-14"] = {"as_run": "modal hazards use targets 101..N; r-dependence over the scored non-degenerate targets",
                 "variants": {}}
    for name, pairs in variants.items():
        st = p2_stats(pairs)
        vv = apply_rules(rf["value"], m1_per, st, m3_as_run, maxref, M2["per_ref"][maxref]["K_sampled"], sz[f"D4/{maxref}"])
        S["I-14"]["variants"][name] = {"P2": st, "DR-2": vv["DR-2"], "DR-4": vv["DR-4"]}
    # modal over all targets (only the modal's own hazards move; the modal is not in P2)
    a0, a = forms["modal"]
    ev = [Esets["modal"][r["idx"]] for r in tg4_all if nd(r) and r["idx"] != refs["F-S3"]["references"]["modal"]["instance_idx_per_D"]["D4"]]
    Sx, Zx, _ = hazards(ev, len(a))
    S["I-14"]["modal_over_all_targets_first3_hazards"] = [(Sx[k], Zx[k]) for k in range(3)]
    S["I-14"]["modal_in_P2_set"] = "no: the P2 set is the union over the 5 F-S3 references (U1, U2, U3, S1, S2); the modal reading cannot move DR-2 or DR-4"

    # ---- I-15: C-UNIF interval
    S["I-15"] = {"as_run": "equal-tailed acceptance region of Binomial(n, 2^-K_rank), <= 0.05% each side",
                 "alternatives": {"CP 99.9% CI of 0/995 contains 2^-17": cp95(0, 995, alpha=0.001)[1] >= 2 ** -17,
                                  "exact two-sided p of 0 survivors": 1.0},
                 "verdict_flip": False,
                 "note": "C-UNIF enters no decision rule directly; it could only void M2 via INV-7, and 0 survivors passes under every reading (J2: the count is structurally 0)."}

    # ---- I-24: DR-2 / DR-3 clause handling
    alt24 = {}
    alt24["as_run"] = DR
    alt24["strict: any unevaluable clause -> DR-2 not evaluable"] = apply_rules(rf["value"], m1_per, p2_as_run, m3_as_run, maxref,
                                                                                 M2["per_ref"][maxref]["K_sampled"], sz[f"D4/{maxref}"], mode="strict_ne")
    if "reading_bullet3" in m3:
        alt24["M3 both-zero read as 'not estimable' (bullet 3) instead of ratio 0 (bullet 1)"] = apply_rules(
            rf["value"], m1_per, p2_as_run, {"kind": "not_estimable"}, maxref, M2["per_ref"][maxref]["K_sampled"], sz[f"D4/{maxref}"])
        alt24["bullet 3 AND strict unevaluable handling"] = apply_rules(
            rf["value"], m1_per, p2_as_run, {"kind": "not_estimable"}, maxref, M2["per_ref"][maxref]["K_sampled"], sz[f"D4/{maxref}"], mode="strict_ne")
    S["I-24"] = {k: {"DR-2": v["DR-2"], "DR-2_clauses": v["DR-2_clauses"], "DR-3": v["DR-3"]} for k, v in alt24.items()}

    # median convention
    S["median_convention"] = {"average_of_middle_two": p2_as_run["median"], "lower_median": p2_as_run.get("lower_median"),
                              "either_below_0.2": (p2_as_run["median"] < 0.2) or (p2_as_run.get("lower_median") or 1) < 0.2}
    out["sensitivity"] = S
    out["wall_seconds"] = round(time.time() - T0, 1)
    json.dump(out, open(os.path.join(HERE, "j3_recompute.json"), "w"), indent=1)
    log("written j3_recompute.json")


if __name__ == "__main__":
    main()
