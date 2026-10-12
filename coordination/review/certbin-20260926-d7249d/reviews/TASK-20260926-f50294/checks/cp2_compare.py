#!/usr/bin/env python3
"""CP-2 of TASK-20260926-f50294: compare EVERY item, per item and per system,
for all 90 blind systems (J6 = TASK-20260926-f0736e rederivation.json) with
RUN-CERTBIN-a3fc60, and the archived J1 output (TASK-20260926-401771) with the
run's certificate-verification.json / annihilator-verification.json; recount
MR19-1 and MR19-3 from J1's verdicts only and re-apply N19-DR-1, -4, -5 and the
mechanical N19-DR-9.

Record-level comparison only: no closure is recomputed here (third checks live
in cp4_*.py). Stdlib only.

Usage: python3 cp2_compare.py <worktree_root> <cp3_json> <out_json>
"""
import decimal
import gzip
import json
import math
import os
import sys
from collections import Counter, defaultdict

ROUND = "coordination/review/certbin-20260926-d7249d"
F0 = f"{ROUND}/reviews/TASK-20260926-f0736e"
J1 = f"{ROUND}/reviews/TASK-20260926-401771"
RUN = "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60"


def jl(p):
    with gzip.open(p, "rt") as fh:
        return [json.loads(x) for x in fh]


# ------------------------------------------------ exact Clopper-Pearson (60 digits)
decimal.getcontext().prec = 80
D = decimal.Decimal


def _tail_ge(k, n, p):
    return sum(D(math.comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def _tail_le(k, n, p):
    return sum(D(math.comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def cp95(k, n, alpha=D("0.05")):
    a2 = alpha / 2
    if k == 0:
        lo = D(0)
    elif k == n:
        lo = a2 ** (D(1) / D(n))
    else:
        l, h = D(0), D(1)
        for _ in range(220):
            m = (l + h) / 2
            if _tail_ge(k, n, m) < a2:
                l = m
            else:
                h = m
        lo = (l + h) / 2
    if k == n:
        hi = D(1)
    elif k == 0:
        hi = 1 - a2 ** (D(1) / D(n))
    else:
        l, h = D(0), D(1)
        for _ in range(220):
            m = (l + h) / 2
            if _tail_le(k, n, m) > a2:
                l = m
            else:
                h = m
        hi = (l + h) / 2
    return lo, hi


def fmt(x):
    return format(x.quantize(D(10) ** -20), "f")


class Tab:
    """Per-item agree / disagree tally."""

    def __init__(self):
        self.items = defaultdict(Counter)
        self.dis = []

    def cmp(self, item, lab, key, run_v, red_v, eq=None, note=None):
        if run_v is None and red_v is None:
            st = "both_absent"
        elif run_v is None:
            st = "re-deriver_only"
        elif red_v is None:
            st = "run_only"
        else:
            ok = (run_v == red_v) if eq is None else eq(run_v, red_v)
            st = "agree" if ok else "disagree"
            if not ok:
                self.dis.append({"item": item, "label": lab, "key": key, "run": run_v, "rederiver": red_v, "note": note})
        self.items[item][st] += 1
        return st


def main():
    root, cp3p, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    os.chdir(root)
    key = json.load(open(f"{ROUND}/blind-inputs-key.json"))
    bi = {x["label"]: x for x in json.load(open(f"{ROUND}/blind/blind-inputs.json"))["instances"]}
    red = json.load(open(f"{F0}/rederivation.json"))
    rs = red["systems"]
    inst = {r["key"]: r for r in jl(f"{RUN}/instances.jsonl.gz")}
    clo = {r["key"]: r for r in jl(f"{RUN}/closures.jsonl.gz")}
    cp3 = json.load(open(cp3p))
    T = Tab()
    per_sys = {}

    for lab in sorted(rs):
        r = rs[lab]
        k = key[lab]["key"]
        I, C = inst[k], clo[k]
        rows = {}

        def c(item, run_v, red_v, eq=None, note=None):
            rows[item] = {"run": run_v, "rederiver": red_v, "status": T.cmp(item, lab, k, run_v, red_v, eq, note)}

        # ---- key map sanity
        assert key[lab]["arm"] == I["arm"] and key[lab]["role"] == I["role"] and I["key"] == k
        assert bi[lab]["kind"] == r["kind"]
        if r["kind"] == "curve":
            assert bi[lab]["x_R"] == I["x_R"] == r["x_R"]
        # ---- instances.jsonl.gz
        q1 = r["Q1"]
        c("s[route1 exhaustive]", I["s"], q1["s_exhaustive_2^20"])
        c("s[route2 quadratic in x_2]", I["s"] if r["kind"] == "curve" else None, q1.get("s_quadratic_route"))
        c("arm (s = 0 or not)", I["role"] == "unsat", q1["s_exhaustive_2^20"] == 0)
        c("degenerate flag", (I["x_R"] < 1024) if r["kind"] == "curve" else None, q1.get("degenerate"),
          note="run: kept curve systems are non-degenerate by the keep rule (x_R >= 1024)")
        c("E_hex (run) == own descent / explicit input (CP-3 cross-check)", True,
          cp3["cross_check_vs_run_E_hex"][lab]["equal_to_run_E_hex"])
        if "E_hex" in r:
            c("E_hex (re-deriver) == E_hex (run)", I["E_hex"], r["E_hex"],
              eq=lambda a, b: [int(x, 16) for x in a] == [int(x, 16) for x in b])
        # ---- M_3 / M_4
        q2 = r["Q2"]
        c("rank_3", C["M_3"]["rank"], q2["rank_3"])
        c("1 in R_3", C["M_3"]["one"], q2["one_in_R3"])
        c("rank_4", C["M_4"]["rank"], q2["rank_4"])
        c("1 in R_4", C["M_4"]["one"], q2["one_in_R4"])
        c("dims_by_deg(M_4)", C["M_4"]["dims_by_deg"], q2["dims_by_deg_M4"])
        c("dims_by_deg(M_3)", C["M_3"]["dims_by_deg"], None)
        # derived_per_instance, from the re-deriver's own M_4 numbers
        dd = q2["dims_by_deg_M4"]
        c("derived (P, fallen, linear_forms, syzygy_excess)",
          [C["derived"]["P"], C["derived"]["fallen"], C["derived"]["linear_forms"], C["derived"]["syzygy_excess"]],
          [q2["rank_4"] - dd[3], dd[3], dd[1] - dd[0], 3819 - q2["rank_4"]])
        # ---- W_4
        W, q3 = C["W_4"], r["Q3"]
        c("W_4 dim per iteration (run list vs re-deriver list minus its confirming W^(i*+1))",
          W["dims"], q3["dims_W_i"][:-1] if q3["dims_W_i"][-1] == q3["dims_W_i"][-2] else q3["dims_W_i"])
        c("W_4 dims-list encoding (re-deriver appends dim W^(i*+1) = dim W^(i*))", True,
          len(q3["dims_W_i"]) == len(W["dims"]) + 1 and q3["dims_W_i"][-1] == q3["dims_W_i"][-2])
        c("W_4 dim(W^(i) cap B_<=3) per iteration (run cumsum(new_fallen) vs re-deriver basis sizes multiplied)",
          [sum(W["new_fallen_per_iteration"][: t + 1]) for t in range(len(W["new_fallen_per_iteration"]))],
          q3["basis_sizes_W_i_cap_B3_multiplied"],
          eq=lambda a, b: a[: len(b)] == b and len(a) == len(b))
        c("W_4 fixpoint index", W["iterations_to_fixpoint"], q3["fixpoint_index"])
        c("W_4 first iteration with 1 (or none)", W["one_first_iteration"] if W["one"] else "none",
          q3["one_first_iteration"] if q3["one_in_W4"] else "none")
        c("W_4 final dimension", W["final_dim"], q3["final_dim"])
        c("dims_by_deg(W_4)", W["dims_by_deg"], q3["dims_by_deg_W4"])
        c("1 in W_4", W["one"], q3["one_in_W4"])
        # ---- rc_b
        rb, q4 = C["rc_b"], r["Q4"]
        c("rc_b applicable", rb["applicable"], q4["applicable"])
        c("rc_b label", rb["label"], q4.get("status"),
          eq=lambda a, b: (a == "substituted" and b == "applied") or a == b)
        c("rc_b kernel dimension", rb["kernel_dim"], q4["kernel_dim"])
        if rb["applicable"] or q4["applicable"]:
            c("rc_b kernel vector c", rb.get("c"), q4.get("kernel_vector"),
              eq=lambda a, b: [i for i, x in enumerate(a) if x] == b)
            c("C-ELL: c_k = Tr(t^k / x_R^2)", rb.get("C-ELL_ok"), q4.get("c_equals_Tr(t^k/x_R^2)"))
            red_ell = None
            if q4.get("ell_linear_support") is not None:
                red_ell = sorted(([0] if q4["ell_constant"] else []) + [v + 1 for v in q4["ell_linear_support"]])
            c("ell (support in E_layout columns 0..20)", rb.get("ell_support"), red_ell,
              note="run lists E_layout columns (0 = constant, 1 + v); re-deriver lists variable indices and the constant separately")
            c("ell constant (run substitution image_const)", rb.get("substitution", {}).get("image_const"), q4.get("ell_constant"))
            c("j*", rb.get("jstar"), q4.get("jstar"))
            c("rank R'_3", rb.get("R3_rank"), q4.get("rank_R3"))
            c("1 in R'_3", rb.get("R3_one"), q4.get("one_R3"))
            c("rank R'_4", rb.get("R4", {}).get("rank"), q4.get("rank_R4"))
            c("1 in R'_4", rb.get("R4", {}).get("one"), q4.get("one_R4"))
            c("dims_by_deg(R'_4)", rb.get("R4", {}).get("dims_by_deg"), q4.get("dims_by_deg_R4"))
            c("sigma", rb.get("sigma"), q4.get("sigma"))
            c("T5_applicable", rb.get("T5_applicable"), q4.get("T5_applicable"))
            dr4 = q4.get("dims_by_deg_R4")
            c("full_B3 (dims_by_deg(R'_4)[3] = 1160)", rb.get("full_B3"), (dr4[3] == 1160) if dr4 else None)
            c("reference profile [0, 0, 18, 360, 3267]", rb.get("ref_profile"), (dr4 == [0, 0, 18, 360, 3267]) if dr4 else None)
        c("ell_route", C["ell_route"], q4.get("ell_route"),
          note="run computes ell_route for S_3 and N-CONV19 only (derived_per_instance); re-deriver for every system with an ell (its AMB-9)")
        # ---- W'_4 (C-T4 subsets in the run; wherever the substitution applied in the re-derivation)
        T4 = C.get("T4")
        q7 = r.get("Q7")
        if T4 or q7:
            Wp = T4["W'_4"] if T4 else None
            Rp = q7["W'_4"] if q7 else None
            c("W'_4 dims per iteration", Wp and Wp["dims"],
              Rp and (Rp["dims_W_i"][:-1] if Rp["dims_W_i"][-1] == Rp["dims_W_i"][-2] else Rp["dims_W_i"]))
            c("W'_4 fixpoint index", Wp and Wp["iterations_to_fixpoint"], Rp and Rp["fixpoint_index"])
            c("W'_4 first iteration with 1", Wp and (Wp["one_first_iteration"] if Wp["one"] else "none"),
              Rp and (Rp["one_first_iteration"] if Rp["one"] else "none"))
            c("W'_4 final dimension", Wp and Wp["final_dim"], Rp and Rp["final_dim"])
            c("dims_by_deg(W'_4)", Wp and Wp["dims_by_deg"], Rp and Rp["dims_by_deg"])
            c("1 in W'_4", Wp and Wp["one"], Rp and Rp["one"])
            c("T4 (final_dim W_4 = final_dim W'_4 + 1160 and one equal)",
              T4 and (T4["final_dim_ok"] and T4["one_ok"]),
              q7 and (q7["final_dim_W4_eq_final_dim_W'4_plus_1160"] and q7["one_agrees"]))
        # ---- certificates present / refuted-set consistency
        c("certificate kind present (wdag-v1 iff refuted, ann-v1 iff not)",
          "wdag" if W["one"] else "ann-or-none",
          "wdag" if (r.get("Q5") or {}).get("status", "").startswith("refuted") else "ann-or-none")
        # ---- D-2 identity on independent numbers
        d2 = None
        if q4.get("applicable") and q4.get("ell_route") is not None and q4.get("one_R4") is not None:
            d2 = {
                "rederiver_ell_route_direct": q4["ell_route"],
                "rederiver_one_R4": q4["one_R4"],
                "rederiver_dims_by_deg_R4[0]": q4["dims_by_deg_R4"][0],
                "run_ell_route": C["ell_route"],
                "run_R4_one": rb.get("R4", {}).get("one"),
                "identity_holds_rederiver": q4["ell_route"] == q4["one_R4"] == (q4["dims_by_deg_R4"][0] == 1),
                "identity_holds_run": (C["ell_route"] == rb.get("R4", {}).get("one")) if C["ell_route"] is not None else None,
                "cross_side_agree": q4["ell_route"] == rb.get("R4", {}).get("one"),
                "ell_route_space_dim_rederiver": q4.get("ell_route_space_dim"),
            }
        c("D-2: ell_route (direct, re-deriver) == 1 in R'_4 (re-deriver)", True if d2 else None,
          d2["identity_holds_rederiver"] if d2 else None)
        per_sys[lab] = {"key": k, "arm": I["arm"], "role": I["role"], "kind": r["kind"], "items": rows, "D-2": d2}

    item_table = {it: dict(cn) for it, cn in sorted(T.items.items())}
    agree_total = sum(cn.get("agree", 0) for cn in T.items.values())
    dis_total = sum(cn.get("disagree", 0) for cn in T.items.values())

    # ================================================= J1 vs run certificate verdicts
    v1 = json.load(open(f"{J1}/verification.json"))
    runcv = json.load(open(f"{RUN}/certificate-verification.json"))
    runav = json.load(open(f"{RUN}/annihilator-verification.json"))
    certs = jl(f"{RUN}/certificates.jsonl.gz")
    anns = jl(f"{RUN}/annihilators.jsonl.gz")
    j1c = {(x["key"], x["closure"], x["format"]): x for x in v1["vc4_refutation_certificates"]["per_certificate"]}
    rnc = {(x["key"], x["closure"], x["format"]): x for x in runcv["results"]}
    submitted = {(x["key"], x["closure"], x["format"]) for x in certs}
    cert_cmp = Counter()
    cert_dis = []
    for kk in sorted(submitted | set(j1c) | set(rnc)):
        a, b = j1c.get(kk), rnc.get(kk)
        if a is None or b is None:
            cert_cmp["missing_on_one_side"] += 1
            cert_dis.append({"cert": kk, "j1": a is not None, "run": b is not None})
            continue
        fields = {
            "verified": (a["verified"], b["valid"]),
            "counts_toward_W4": ((bool(a["verified"]) if kk[2] == "wdag-v1" else a.get("counts_toward_W4")), b.get("counts")),
            "max_mu": (a.get("max_mu"), b.get("max_mu")),
        }
        if kk[2] == "wdag-v1":
            fields["n_nodes"] = (a.get("n_nodes", a.get("node_count")), b.get("n_nodes"))
            fields["max_node_degree"] = (a.get("max_node_degree"), b.get("max_node_degree"))
        for f, (x, y) in fields.items():
            if x is None or y is None:
                cert_cmp[f + ":not_on_both"] += 1
            elif x == y:
                cert_cmp[f + ":agree"] += 1
            else:
                cert_cmp[f + ":disagree"] += 1
                cert_dis.append({"cert": kk, "field": f, "j1": x, "run": y})
    j1a = {x["key"]: x for x in v1["vc5_ann_v1"]["per_certificate"]}
    rna = {x["key"]: x for x in runav["results"]}
    ann_cmp = Counter()
    ann_dis = []
    for kk in sorted(set(j1a) | set(rna) | {x["key"] for x in anns}):
        a, b = j1a.get(kk), rna.get(kk)
        if a is None or b is None:
            ann_cmp["missing_on_one_side"] += 1
            ann_dis.append({"key": kk, "j1": a is not None, "run": b is not None})
            continue
        for f, (x, y) in {"verified": (a["verified"], b["valid"]),
                          "n_functionals": (a["size_L"], b["n_functionals"]),
                          "dim_S_cap_B3": (a["dim_S_cap_B3"], b["dim_S_cap_B_le_D_minus_1"])}.items():
            if x == y:
                ann_cmp[f + ":agree"] += 1
            else:
                ann_cmp[f + ":disagree"] += 1
                ann_dis.append({"key": kk, "field": f, "j1": x, "run": y})

    # ================================================= recount from J1's verdicts only
    arm_unsat = defaultdict(list)
    for kk, x in inst.items():
        if x["role"] == "unsat":
            arm_unsat[x["arm"]].append(kk)
    j1_w4 = {kk[0] for kk, x in j1c.items() if kk[2] == "wdag-v1" and x["verified"] and x.get("counts_toward_W4", True)}
    j1_m4 = {kk[0] for kk, x in j1c.items() if x["verified"] and x.get("counts_toward_M4")}
    engine_w4 = {kk for kk, x in clo.items() if x["W_4"]["one"]}
    uncert = sorted(k for k in engine_w4 if k not in j1_w4 and inst[k]["arm"] == "S3-U400")
    N = len(arm_unsat["S3-U400"])
    w = len([k for k in arm_unsat["S3-U400"] if k in j1_w4])
    wL2 = w
    NL2 = N - len(uncert)

    def label(w_, n_):
        if n_ < 300:
            return "NOT EVALUABLE (sample)"
        if w_ >= math.ceil(0.9 * n_):
            return "PERSISTS"
        if w_ <= math.floor(0.1 * n_):
            return "DECAYS"
        return "PARTIAL"

    lo1, hi1 = cp95(w, N)
    lo386, _ = cp95(386, 386)
    L1, L2 = label(w, N), label(wL2, NL2)
    dr1 = {
        "w_L1": w, "N_L1": N, "w_L2": wL2, "N_L2": NL2, "uncertified_or_undetermined": uncert,
        "cp95_L1": [fmt(lo1), fmt(hi1)], "label_L1": L1, "label_L2": L2,
        "verdict": L1 if L1 == L2 else "UNDETERMINED (budget or certification)",
        "E-PERSIST_falsified": w <= N // 2, "E-DECAY_falsified": w > N // 2,
        "cp95_lower_386_386": fmt(lo386),
        "n17_comparison": "NO DETECTABLE DROP FROM n = 17" if hi1 >= lo386 else "BELOW THE n = 17 FIGURE",
    }

    def rate(arm, closure):
        ks = arm_unsat[arm]
        s = j1_w4 if closure == "W_4" else j1_m4
        kk = len([k for k in ks if k in s])
        lo, hi = cp95(kk, len(ks))
        return {"k": kk, "n": len(ks), "cp95": [fmt(lo), fmt(hi)], "_lo": lo, "_hi": hi}

    dr4 = {}
    for clos in ("W_4", "M_4"):
        s3 = rate("S3-U400", clos)
        for X in ("N-F219", "N-AFF19", "N-ELL19"):
            xr = rate(X, clos)
            dr4[f"{clos}|{X}"] = {"S3": {k: v for k, v in s3.items() if not k.startswith("_")},
                                  "X": {k: v for k, v in xr.items() if not k.startswith("_")},
                                  "verdict": "S_3 ABOVE X" if s3["_lo"] > xr["_hi"] else "NOT DISTINGUISHED"}
    conv = rate("N-CONV19", "W_4")
    s3w = rate("S3-U400", "W_4")
    ell = rate("N-ELL19", "W_4")
    f2 = rate("N-F219", "W_4")
    wc, nc = conv["k"], conv["n"]
    dr5 = {
        "w_c": wc, "n_c": nc, "cp95": conv["cp95"],
        "verdict": "TENSOR-LEVEL" if wc >= math.ceil(0.9 * nc) else ("BELOW" if wc <= math.floor(0.1 * nc) else "MIXED"),
        "AT_S3_RATE": not (conv["_hi"] < s3w["_lo"] or s3w["_hi"] < conv["_lo"]),
        "N-CONV19_ABOVE_N-ELL19": conv["_lo"] > ell["_hi"],
        "N-CONV19_ABOVE_N-F219": conv["_lo"] > f2["_hi"],
    }
    dr9 = "ELIGIBLE" if (L1 == "PERSISTS" and L2 == "PERSISTS") else "NOT ELIGIBLE"
    # MR19-3 recount per (closure, arm, format)
    mr3 = defaultdict(Counter)
    for kk, x in j1c.items():
        arm = kk[0].split(":")[0]
        t = mr3[f"{kk[1]}|{arm}|{kk[2]}"]
        t["submitted"] += 1
        t["verified"] += int(x["verified"])
        t["failed"] += int(not x["verified"])
        # counting toward W_4 by the FROZEN format text: a verified wdag-v1 counts;
        # a flat-v1 counts only at max |mu| <= 2 (J1 records the flag for flat-v1
        # only; for wdag-v1 it is implied by format and verdict)
        if kk[2] == "wdag-v1":
            cnt = bool(x["verified"])
        else:
            cnt = bool(x["verified"] and x.get("max_mu", 99) <= 2)
            assert cnt == bool(x.get("counts_toward_W4")), kk
        t["counting"] += int(cnt)
    ann_j1 = Counter()
    for kk, x in j1a.items():
        ann_j1[kk.split(":")[0] + ":submitted"] += 1
        ann_j1[kk.split(":")[0] + ":verified"] += int(x["verified"])
    # compare with the run's recorded verdicts
    dr = json.load(open(f"{RUN}/decision-rules.json"))
    cs = json.load(open(f"{RUN}/cell-summary.json"))
    run_mr3 = cs["MR19-3"]["certificates"]
    recount_vs_run = {
        "MR19-1_w": [w, cs["MR19-1"]["w"]],
        "MR19-1_N": [N, cs["MR19-1"]["N"]],
        "MR19-1_cp95_lower_str": [dr1["cp95_L1"][0], cs["MR19-1"]["cp95"]["cp95_str"][0]],
        "N19-DR-1_label_L1": [L1, dr["N19-DR-1"]["label_L1"]],
        "N19-DR-1_label_L2": [L2, dr["N19-DR-1"]["label_L2"]],
        "N19-DR-1_verdict": [dr1["verdict"], dr["N19-DR-1"]["verdict"]],
        "N19-DR-1_n17": [dr1["n17_comparison"], dr["N19-DR-1"]["n17_comparison"]],
        "N19-DR-1_E-PERSIST_falsified": [dr1["E-PERSIST_falsified"], dr["N19-DR-1"]["E-PERSIST_falsified_L1"]],
        "N19-DR-1_E-DECAY_falsified": [dr1["E-DECAY_falsified"], dr["N19-DR-1"]["E-DECAY_falsified_L1"]],
        "N19-DR-5_verdict": [dr5["verdict"], dr["N19-DR-5"]["verdict"]],
        "N19-DR-5_AT_S3_RATE": [dr5["AT_S3_RATE"], dr["N19-DR-5"]["AT_S3_RATE"]],
        "N19-DR-5_ABOVE_N-ELL19": [dr5["N-CONV19_ABOVE_N-ELL19"], dr["N19-DR-5"]["N-CONV19_ABOVE_N-ELL19"]],
        "N19-DR-5_ABOVE_N-F219": [dr5["N-CONV19_ABOVE_N-F219"], dr["N19-DR-5"]["N-CONV19_ABOVE_N-F219"]],
        "N19-DR-9_flag": [dr9, dr["N19-DR-9"]["flag"]],
    }
    for kk, v in dr4.items():
        clos, X = kk.split("|")
        recount_vs_run[f"N19-DR-4_{clos}_{X}"] = [v["verdict"], dr["N19-DR-4"]["comparisons"][X][clos]["verdict"]]
    for kk, t in mr3.items():
        rr = run_mr3.get(kk, {})
        recount_vs_run[f"MR19-3_{kk}"] = [dict(t), {x: rr.get(x) for x in ("submitted", "verified", "failed", "counting")}]
    recount_vs_run["MR19-3_ann_v1"] = [dict(ann_j1), {f"{a}:{x}": y for a, v in cs["MR19-3"]["ann_v1"]["per_arm"].items() for x, y in v.items()}]
    changes = {k: v for k, v in recount_vs_run.items() if v[0] != v[1]}

    # ================================================= J1 VC-2 / VC-3 vs instances; VC-6 vs M_4
    reb = {x["key"]: x for x in jl(f"{J1}/work/rebuild.jsonl.gz")}
    vc23 = Counter()
    vc23_dis = []
    for kk, x in inst.items():
        rr = reb.get(kk)
        if rr is None:
            vc23["missing_in_J1"] += 1
            vc23_dis.append(kk)
            continue
        ok_s = rr["s_mine"] == x["s"] and rr["s_archived"] == x["s"]
        ok_role = (rr["s_mine"] == 0) == (x["role"] == "unsat")
        ok_reb = rr.get("rebuild_eq_archived", True) is not False
        ok_hash = rr["E_sha256_match"]
        for nm, ok in (("s", ok_s), ("role", ok_role), ("rebuild_eq_archived_or_na", ok_reb), ("E_sha256", ok_hash)):
            vc23[nm + (":agree" if ok else ":disagree")] += 1
            if not ok:
                vc23_dis.append({"key": kk, "item": nm})
    vc23["J1_records"] = len(reb)
    vc23["run_kept_systems"] = len(inst)
    vc6 = Counter()
    vc6_dis = []
    for arm in ("S3-U400", "S3-SAT100", "N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"):
        for x in jl(f"{J1}/work/m4-{arm}.jsonl.gz"):
            C = clo[x["key"]]["M_4"]
            for nm, a, b in (("one", x["one_in_M4"], C["one"]), ("rank", x["rank_M4"], C["rank"]),
                             ("dims_by_deg", x["dims_by_deg_M4"], C["dims_by_deg"])):
                tag = ("S3-U400" if arm == "S3-U400" else "other_arms_supplementary") + "|" + nm
                vc6[tag + (":agree" if a == b else ":disagree")] += 1
                if a != b:
                    vc6_dis.append({"key": x["key"], "item": nm, "j1": a, "run": b})
            if arm == "S3-U400":
                vc6["S3-U400|witness_checked:" + str(bool(x["witness_checked"] and x["witness_vanishes_on_all_4009_rows"] and x["witness_lambda_of_1"] == 1))] += 1
    wit = {x["key"] for x in jl(f"{J1}/m4-witnesses.jsonl.gz") if x.get("checked")}

    # ================================================= certification status per pool key (CP-3)
    cert_status = {}
    j1_ann_ok = {k for k, x in j1a.items() if x["verified"]}
    for lab in sorted(rs):
        kk = key[lab]["key"]
        Cc = clo[kk]
        e = cp3["per_label"][lab]
        blind_w = e["wdag"]["status"] == "valid"
        blind_a = e["ann"]["status"] == "valid"
        if Cc["W_4"]["one"]:
            run_w = kk in j1_w4 and rnc.get((kk, "W_4", "wdag-v1"), {}).get("valid")
            n = int(bool(run_w)) + int(blind_w)
            st = {2: "certified twice (run wdag-v1 verified by J1 AND valid blind wdag-v1)", 1: "certified once", 0: "engine-reported only"}[n]
            cert_status[lab] = {"key": kk, "claim": "1 in W_4", "status": st, "run_wdag_J1_verified": bool(run_w), "blind_wdag_valid": blind_w}
        else:
            prof_m4 = rs[lab]["Q2"]["dims_by_deg_M4"]
            q4 = rs[lab]["Q4"]
            d3 = prof_m4[3] == rs[lab]["Q2"]["rank_3"] and prof_m4[0] == 0
            t5 = bool(q4.get("T5_applicable")) and q4.get("one_R4") is False
            how = []
            if blind_a:
                how.append("valid blind ann-v1 (CP-3)")
            if kk in j1_ann_ok:
                how.append("run ann-v1 verified by J1")
            if how:
                st = "certified"
            elif d3 or t5:
                st = "derived"
            else:
                st = "engine-reported only"
            cert_status[lab] = {"key": kk, "claim": "1 not in W_4", "status": st, "by": how,
                                "derivation_available_on_rederiver_profile": ("D-3" if d3 else "") + (" T5" if t5 else ""),
                                "satisfiable_s": inst[kk]["s"] if inst[kk]["s"] else None}
    cs_counts = defaultdict(Counter)
    for lab, v in cert_status.items():
        cs_counts[key[lab]["arm"] + "|" + v["claim"]][v["status"]] += 1

    out = {
        "task": "TASK-20260926-f50294", "cp": "CP-2 (and CP-3 per-key certification status)",
        "key_mapping": {lab: key[lab]["key"] for lab in sorted(key)},
        "per_item_table": item_table,
        "compared_item_instances": {"agree": agree_total, "disagree": dis_total},
        "disagreements": T.dis,
        "per_system": per_sys,
        "J1_vs_run_certificates": {"per_field": dict(cert_cmp), "disagreements": cert_dis,
                                   "n_run_submitted": len(submitted), "n_J1": len(j1c), "n_run_verifier": len(rnc)},
        "J1_vs_run_ann_v1": {"per_field": dict(ann_cmp), "disagreements": ann_dis},
        "recount_from_J1_verdicts": {"N19-DR-1": dr1,
                                     "N19-DR-4": {k: {kk: vv for kk, vv in v.items()} for k, v in dr4.items()},
                                     "N19-DR-5": dr5, "N19-DR-9": dr9,
                                     "MR19-3": {k: dict(v) for k, v in mr3.items()}, "ann_v1": dict(ann_j1)},
        "recount_vs_run_recorded": recount_vs_run,
        "recount_changes": changes,
        "J1_VC2_VC3_vs_instances_all_kept": {"counts": dict(vc23), "disagreements": vc23_dis},
        "J1_VC6_vs_run_M4": {"counts": dict(vc6), "disagreements": vc6_dis, "S3-U400_witnessed_keys": len(wit)},
        "certification_status_per_pool_key": cert_status,
        "certification_counts_per_arm": {k: dict(v) for k, v in sorted(cs_counts.items())},
    }
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print("items agree/disagree:", agree_total, dis_total)
    for it, cn in item_table.items():
        print(" ", it, cn)
    print("disagreements:", len(T.dis))
    for d in T.dis[:40]:
        print("   ", d)
    print("J1 vs run certs:", dict(cert_cmp), "ann:", dict(ann_cmp))
    print("recount changes:", changes)
    print("VC2/3:", dict(vc23), "VC6:", dict(vc6))
    print("cert status:", {k: dict(v) for k, v in cs_counts.items()})


if __name__ == "__main__":
    main()
