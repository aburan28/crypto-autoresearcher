#!/usr/bin/env python3
"""TASK-20260923-01af16 scratch invocation #6 (the card's spare): light checks for
J5, J6 and the proves-too-much report.  Pure Python arithmetic and reading of
committed files; no solver.  Output: scratch/small_checks.out.json (+ stdout).

  C1  provenance citation locators: newline numbering vs str.splitlines() numbering
  C2  the 142 arithmetic as stated in the paper: (2 - 2/5)*log2(p) + 2*k(k-1), k = 5
  C3  which rho formula reproduces BOTH 159.83 and 101.93 (the note states none)
  C4  object A: the 180-bit prime l | p^5+1 found by the pipeline has ord_l(q) = 2
  C5  object B: fundamental discriminant of E_0 over F_{p^5} (from t1^2 - 4p)
  C6  label-decision lines of the committed gfpn_audit.py (pristine copy)
  C7  does each proves-too-much output satisfy the frozen success criterion?
"""
import json, math, os, re, sys, hashlib
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.dirname(HERE)
REPO = "/home/user/crypto-autoresearcher"
sys.path.insert(0, os.path.join(SCR, "pipeline_pristine"))
from gfpn_arith import miller_rabin  # byte-identical copy of the producer's module

p = 2**64 - 2**32 + 1
q = p**5
res = {}

# C1 ---------------------------------------------------------------------------
texts = {"EcGFp5": "inputs/PORNIN-2022-274-ECGFP5/paper_fulltext.md", "EcMasFp5": "inputs/ECMASFP5-HACKMD-2025/note_fulltext.md"}
c1 = []
for run, cur in [("RUN-GFPN-b71f2f", "EcGFp5"), ("RUN-GFPN-3bbef2", "EcMasFp5")]:
    raw = open(os.path.join(REPO, texts[cur]), encoding="utf-8").read()
    nl = raw.split("\n"); sl = raw.splitlines()
    fp = yaml.safe_load(open(os.path.join(REPO, f"experiments/EXP-GFPN-726eb2/runs/{run}/figure-provenance.yaml")))
    for f in fp["figure_provenance"]["figures"]:
        for c in f.get("citations") or []:
            L, T = c["line"], c["text"]
            std = nl[L - 1].lstrip("\x0c").rstrip() if L <= len(nl) else None
            where = [i + 1 for i, l in enumerate(nl) if l.lstrip("\x0c").rstrip() == T]
            c1.append({"run": run, "figure": f["id"], "cited_line": L, "text_at_cited_line_newline_numbering_matches": std == T,
                       "text_at_cited_line_splitlines_numbering_matches": (sl[L - 1].rstrip() == T) if L <= len(sl) else None,
                       "newline_line_of_quoted_text": where})
    res.setdefault("C1_formfeeds", {})[cur] = raw.count("\x0c")
res["C1_citations"] = c1
res["C1_summary"] = {"total": len(c1), "off_under_newline_numbering": sum(1 for c in c1 if not c["text_at_cited_line_newline_numbering_matches"]),
                     "all_match_under_splitlines": all(c["text_at_cited_line_splitlines_numbering_matches"] for c in c1)}

# C2 ---------------------------------------------------------------------------
k = 5
systems_bits = (2 - 2 / k) * math.log2(p)
D_bits = k * (k - 1)
res["C2_142_arithmetic"] = {"log2_p": math.log2(p), "systems_bits_(2-2/5)log2p": systems_bits, "D_bits_k(k-1)": D_bits,
                             "per_system_floor_bits_2D": 2 * D_bits, "total_bits": systems_bits + 2 * D_bits,
                             "note": "reproduces the paper's 'at least 2^142' (lines 138-149, newline numbering) as arithmetic on its stated model; recomputing it certifies the arithmetic only, not the model"}

# C3 ---------------------------------------------------------------------------
n_mas = 0xfffffffb0000000effffffe20000002cffffffcc2c13f5f892042da0dfcde3fc8f4b2caf22360ee3
l_tw = 0x128ad28934008b50864257bbff0983af9688b4f04ff3f024f86f
cands = {"0.5*log2(pi*l/4) [audit, = log2(0.886*sqrt l)]": 0.5 * math.log2(math.pi / 4),
         "0.5*log2(l)": 0.0, "0.5*log2(pi*l/2)": 0.5 * math.log2(math.pi / 2), "0.5*log2(pi*l)": 0.5 * math.log2(math.pi),
         "0.5*log2(l) - 1 (sqrt(l)/2)": -1.0}
c3 = {}
for name, c in cands.items():
    a = 0.5 * math.log2(n_mas) + c; b = 0.5 * math.log2(l_tw) + c
    c3[name] = {"curve": round(a, 4), "twist": round(b, 4), "curve_rounds_to_159.83": round(a, 2) == 159.83, "twist_rounds_to_101.93": round(b, 2) == 101.93}
res["C3_rho_formula_fit"] = c3

# C4 ---------------------------------------------------------------------------
l180 = 981394945332765852739783890042638080022301387020925721
res["C4_objA"] = {"l": str(l180), "l_bits": l180.bit_length(), "l_divides_q_plus_1": (q + 1) % l180 == 0,
                  "q_mod_l_equals_minus_1": q % l180 == l180 - 1, "l_probable_prime_MR": miller_rabin(l180),
                  "ord_l_q": 2 if (q % l180 == l180 - 1 and l180 > 2) else None,
                  "pipeline_reported_e_for_the_curve_row": None}
rawA = os.path.join(SCR, "objects/objA_supersingular/out/raw-result.json")
if os.path.exists(rawA):
    rA = json.load(open(rawA))
    e = int(rA["steps"]["embedding_degree"]["embedding_degree"])
    nA = int(rA["steps"]["order_certificate"]["candidate_n"])
    res["C4_objA"].update({"pipeline_reported_e_for_the_curve_row": str(e), "pipeline_e_bits": e.bit_length(),
                           "pipeline_n_used": str(nA), "n_used_is_q_plus_1": nA == q + 1, "n_used_prime_MR": miller_rabin(nA),
                           "pow_q_e_mod_n_equals_1": pow(q % nA, e, nA) == 1, "true_ord_of_q_mod_n": 2 if (q % nA == nA - 1) else None,
                           "twist_row_embedding_degree_for_l180": rA["steps"]["twist"].get("twist_embedding_degree")})

# C5 ---------------------------------------------------------------------------
t1 = 570399549
d1 = t1 * t1 - 4 * p
res["C5_objB"] = {"t1": t1, "t1^2-4p": d1, "mod4": d1 % 4, "abs_bits": abs(d1).bit_length(),
                  "note": "PARI core(t1^2-4p) = itself (prep.gp.out), so the fundamental discriminant of E_0 (and of E_0 over F_{p^5}) is t1^2-4p"}
rawB = os.path.join(SCR, "objects/objB_subfield/out/raw-result.json")
if os.path.exists(rawB):
    rB = json.load(open(rawB))
    D5 = int(rB["steps"]["cm_discriminant"]["D"])
    s2 = D5 // d1
    res["C5_objB"].update({"D_over_Fp5": str(D5), "D_over_Fp5_bits": abs(D5).bit_length(), "D5_divisible_by_d1": D5 % d1 == 0,
                           "quotient_is_square": math.isqrt(s2) ** 2 == s2, "pipeline_cm_row": None})
    t = yaml.safe_load(open(os.path.join(SCR, "objects/objB_subfield/out/audit-table.yaml")))["audit_table"]
    res["C5_objB"]["pipeline_cm_row"] = [r for r in t["rows"] if r["criterion"] == "cm_discriminant_bits"][0]

# C6 ---------------------------------------------------------------------------
src = open(os.path.join(SCR, "pipeline_pristine/gfpn_audit.py")).read().splitlines()
want = [227, 228, 229, 230, 231, 232, 233, 234, 346, 376, 377, 378, 379, 382, 385, 390, 397, 402, 403, 405, 434, 441, 449, 452, 453, 470, 474, 499, 569, 573, 576, 578, 579, 580, 624, 625, 627, 628, 629, 630, 631, 632, 633, 634, 635]
res["C6_label_lines"] = {str(i): src[i - 1] for i in want}
res["C6_sha256_pristine"] = hashlib.sha256(open(os.path.join(SCR, "pipeline_pristine/gfpn_audit.py"), "rb").read()).hexdigest()

# C7 ---------------------------------------------------------------------------
PRIMARY = ["order_certificate", "cofactor", "embedding_degree", "cm_discriminant_bits", "twist_order_factorization",
           "twist_security_bits", "rigidity_reproduced", "figure_provenance_table"]
c7 = {}
for obj in ["objA_supersingular", "objB_subfield", "objC_tampered_selfreports", "objD_mas_shifted_rigidity", "objD_gf_shifted_rigidity"]:
    rp = os.path.join(SCR, "objects", obj, "out/raw-result.json")
    if not os.path.exists(rp):
        c7[obj] = "no output"; continue
    r = json.load(open(rp)); m = r["metrics"]; nv = r["not_verifiable"]
    tab = yaml.safe_load(open(os.path.join(SCR, "objects", obj, "out/audit-table.yaml")))["audit_table"]
    prov = yaml.safe_load(open(os.path.join(SCR, "objects", obj, "out/figure-provenance.yaml")))["figure_provenance"]
    ids = [f["id"] for f in prov["figures"]]
    per = {}
    for k_ in PRIMARY:
        v = m.get(k_)
        per[k_] = {"value": v, "present_with_certificate_or_reason": (v is not None and ("certificate" in str(v) or v == "present")) or (v in ("not_verifiable", "bound", None) and bool(nv))}
    c7[obj] = {"per_metric": per, "control_row": [x["result"] for x in tab["rows"] if x["criterion"] == "scurve_control_certificate_match"][0],
               "field_security_142_tagged": "field_security_142" in ids, "twist_security_101_93_tagged": "twist_security_101_93" in ids or tab["curve_id"] == "EcGFp5",
               "run_status": r["run_status"],
               "labels": {x["criterion"]: x["result"] for x in tab["rows"]},
               "any_FAIL_label": any(str(x["result"]).startswith("FAIL") for x in tab["rows"])}
    c7[obj]["success_criterion_literally_met"] = all(v["present_with_certificate_or_reason"] for v in per.values()) and c7[obj]["control_row"].startswith("PASS") and c7[obj]["field_security_142_tagged"]
res["C7_success_criterion_on_known_false_objects"] = c7

# C8 ---------------------------------------------------------------------------
# rows that differ between a scratch rerun on a REAL curve and the committed table
c8 = {}
for obj, run in [("objC_tampered_selfreports", "RUN-GFPN-3bbef2"), ("objD_mas_shifted_rigidity", "RUN-GFPN-3bbef2"), ("objD_gf_shifted_rigidity", "RUN-GFPN-b71f2f")]:
    mine = yaml.safe_load(open(os.path.join(SCR, "objects", obj, "out/audit-table.yaml")))["audit_table"]
    theirs = yaml.safe_load(open(os.path.join(REPO, f"experiments/EXP-GFPN-726eb2/runs/{run}/audit-table.yaml")))["audit_table"]
    diffs = []
    for a, b in zip(mine["rows"], theirs["rows"]):
        for k_ in a:
            if a[k_] != b.get(k_):
                diffs.append({"criterion": a["criterion"], "field": k_, "scratch": a[k_], "committed": b.get(k_)})
    c8[obj] = {"compared_with": f"experiments/EXP-GFPN-726eb2/runs/{run}/audit-table.yaml", "differing_fields": diffs,
               "not_verifiable_equal": mine["not_verifiable"] == theirs["not_verifiable"]}
res["C8_rerun_vs_committed_tables"] = c8

json.dump(res, open(os.path.join(SCR, "small_checks.out.json"), "w"), indent=2, default=str)
print(json.dumps({"C1_summary": res["C1_summary"], "C1_formfeeds": res["C1_formfeeds"], "C2": res["C2_142_arithmetic"]["total_bits"],
                  "C3": c3, "C4": res["C4_objA"], "C5": {k_: v for k_, v in res["C5_objB"].items() if k_ != "pipeline_cm_row"},
                  "C7": {k_: (v if isinstance(v, str) else {"success_criterion_literally_met": v["success_criterion_literally_met"], "any_FAIL_label": v["any_FAIL_label"], "labels": v["labels"]}) for k_, v in c7.items()}}, indent=1, default=str))
