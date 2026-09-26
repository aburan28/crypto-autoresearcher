#!/usr/bin/env python3
"""TASK-20260926-0f8aec, joint J3: compare the literal transcription
(j3-literal-ext.json) with the archived closures.jsonl.gz records, and run the
per-system glue checks over EVERY system (M_4 label backed by macaulay_closure
and by a flat certificate with max |mu| <= 2 that sums to 1 under my own
arithmetic; M_4/W_4 iteration-0 agreement; derived fields; rc_b text rules;
extractor/engine dimension agreement). Reports violation counts only (no
per-arm refutation counts are printed: RV-4 hygiene). Imports nothing from
impl/, verifier/ or src/.
"""
from __future__ import annotations

import gzip
import json
import sys
from itertools import combinations
from pathlib import Path

WT = Path(sys.argv[1])
OUTDIR = Path(__file__).resolve().parent
RUN = WT / "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
MONOS2 = [()] + [(i,) for i in range(18)] + list(combinations(range(18), 2))


def rows_to_masks(E_hex):
    out = []
    for h in E_hex:
        r = int(h, 16)
        f = []
        for col, m in enumerate(MONOS2):
            if (r >> col) & 1:
                mk = 0
                for i in m:
                    mk |= 1 << i
                f.append(mk)
        out.append(f)
    return out


def flat_sum(body, eqs):
    acc = set()
    for mu, k in body:
        mk = 0
        for i in mu:
            mk |= 1 << i
        for m in eqs[k]:
            acc ^= {mk | m}
    return acc


def main():
    lit = json.load(open(OUTDIR / "j3-literal-ext.json"))
    cl = {}
    for l in gzip.open(RUN / "closures.jsonl.gz", "rt"):
        r = json.loads(l)
        cl[(r["key"], r["closure"])] = r
    inst = {}
    for l in gzip.open(RUN / "instances.jsonl.gz", "rt"):
        r = json.loads(l)
        inst[r["key"]] = r
    certs = [json.loads(l) for l in gzip.open(RUN / "certificates.jsonl.gz", "rt")]

    # ---- A. literal vs archived on the selected systems
    A = {}
    W_FIELDS = ["iterations_to_fixpoint", "dims", "final_dim", "one", "one_first_iteration", "dims_by_deg"]
    for key, e in lit["systems"].items():
        diffs = []
        rec = {}
        m4 = cl[(key, "M_4")]
        for f in ["rank", "one", "dims_by_deg", "P", "fallen", "linear_forms"]:
            if m4.get(f) != e["M_4_literal"][f]:
                diffs.append(("M_4", f, m4.get(f), e["M_4_literal"][f]))
        if (key, "M_3") in cl:
            m3 = cl[(key, "M_3")]
            for f in ["rank", "one", "dims_by_deg"]:
                if m3.get(f) != e["M_3_literal"][f]:
                    diffs.append(("M_3", f, m3.get(f), e["M_3_literal"][f]))
            rec["M_3_compared"] = True
        w4 = cl[(key, "W_4")]
        for f in W_FIELDS:
            if w4.get(f) != e["W_4_literal"][f]:
                diffs.append(("W_4", f, w4.get(f), e["W_4_literal"][f]))
        if w4.get("new_fallen_per_iteration") != e["W_4_literal"]["new_fallen_per_iteration_literal"]:
            diffs.append(("W_4", "new_fallen_per_iteration", w4.get("new_fallen_per_iteration"),
                          e["W_4_literal"]["new_fallen_per_iteration_literal"]))
        if w4.get("stack_rows_per_iteration") != e["W_4_literal"]["stack_rows_per_iteration_literal"]:
            diffs.append(("W_4", "stack_rows_per_iteration", w4.get("stack_rows_per_iteration"),
                          e["W_4_literal"]["stack_rows_per_iteration_literal"]))
        rb = cl[(key, "rc_b")]
        lb = e["rc_b_literal"]
        for f in ["kernel_dim", "label", "c", "ell_linear_support", "ell_const", "j_star"]:
            if f in lb or rb.get(f) is not None:
                if rb.get(f) != lb.get(f):
                    diffs.append(("rc_b", f, rb.get(f), lb.get(f)))
        if "R'_4_literal" in e:
            for nm in ["R'_3", "R'_4"]:
                ar = cl.get((key, nm))
                for f in ["rank", "one", "dims_by_deg"]:
                    if ar is None or ar.get(f) != e[nm + "_literal"][f]:
                        diffs.append((nm, f, None if ar is None else ar.get(f), e[nm + "_literal"][f]))
            wp = cl.get((key, "W'_4"))
            for f in W_FIELDS:
                if wp is None or wp.get(f) != e["W'_4_literal"][f]:
                    diffs.append(("W'_4", f, None if wp is None else wp.get(f), e["W'_4_literal"][f]))
            if rb.get("T5_applicable") != e["T5_applicable_literal"]:
                diffs.append(("rc_b", "T5_applicable", rb.get("T5_applicable"), e["T5_applicable_literal"]))
        rec["archived"] = {"M_4": {f: m4.get(f) for f in ["rank", "one", "dims_by_deg", "P", "fallen", "linear_forms"]},
                           "W_4": {f: w4.get(f) for f in W_FIELDS + ["new_fallen_per_iteration",
                                                                    "stack_rows_per_iteration"]},
                           "rc_b": {f: rb.get(f) for f in ["kernel_dim", "label", "c", "ell_linear_support", "ell_const",
                                                          "j_star", "T5_applicable"]}}
        if (key, "R'_4") in cl:
            rec["archived"]["R'_3"] = {f: cl[(key, "R'_3")].get(f) for f in ["rank", "one", "dims_by_deg"]}
            rec["archived"]["R'_4"] = {f: cl[(key, "R'_4")].get(f) for f in ["rank", "one", "dims_by_deg"]}
            rec["archived"]["W'_4"] = {f: cl[(key, "W'_4")].get(f) for f in W_FIELDS}
        rec["diffs"] = diffs
        A[key] = rec
        print("A", key, "diffs", diffs, flush=True)

    # ---- B. global glue checks over every system
    V = {}

    def bad(kind, key):
        V.setdefault(kind, []).append(key)
    m4cert = {}
    for c in certs:
        if c["closure"] == "M_4":
            m4cert.setdefault(c["key"], []).append(c)
    n_m4_checked = 0
    for key, r in inst.items():
        m4 = cl.get((key, "M_4"))
        w4 = cl.get((key, "W_4"))
        rb = cl.get((key, "rc_b"))
        if m4 is None or w4 is None or rb is None:
            bad("missing M_4/W_4/rc_b record", key)
            continue
        if r["arm"] in ("S3-U62", "S3-C20", "S3-S62", "NULL-AFF62", "NULL-F262") and (key, "M_3") not in cl:
            bad("missing M_3 on archived arm", key)
        d = m4["dims_by_deg"]
        if len(d) != 5 or d[4] != m4["rank"]:
            bad("M_4 dims_by_deg[4] != rank", key)
        if (m4["P"], m4["fallen"], m4["linear_forms"]) != (m4["rank"] - d[3], d[3], d[1] - d[0]):
            bad("M_4 derived P/fallen/linear_forms", key)
        if m4["one"] != (d[0] == 1):
            bad("M_4 one != (dims_by_deg[0]==1)", key)
        if (m4["label"] == "refuted") != m4["one"]:
            bad("M_4 label != one", key)
        if m4["one"] != (w4["one_first_iteration"] == 0):
            bad("M_4 one != (W_4 one_first_iteration == 0)", key)
        if m4["one"] and not w4["one"]:
            bad("M_4 one but not W_4 one", key)
        if w4["dims"][0] != m4["rank"]:
            bad("W_4 dims[0] != rank M_4", key)
        if w4["final_dim"] != w4["dims"][-1] or w4["iterations_to_fixpoint"] != len(w4["dims"]) - 1:
            bad("W_4 final_dim/iterations inconsistent with dims", key)
        if w4.get("codim") != 4048 - w4["final_dim"]:
            bad("W_4 codim", key)
        if (w4["label"] == "refuted") != w4["one"]:
            bad("W_4 label != one", key)
        if w4["one"] != (w4["dims_by_deg"][0] == 1):
            bad("W_4 one != (dims_by_deg[0]==1)", key)
        # M_4 label backed by a flat certificate with max|mu|<=2 summing to 1
        cs = m4cert.get(key, [])
        if m4["one"]:
            n_m4_checked += 1
            if len(cs) != 1:
                bad("M_4 refuted without exactly one M_4 certificate", key)
            else:
                c = cs[0]
                eqs = rows_to_masks(r["E_hex"])
                mx = max((len(mu) for mu, _ in c["body"]), default=0)
                if c["format"] != "flat-v1" or mx > 2 or c.get("max_mu") != mx:
                    bad("M_4 certificate not flat-v1 with max|mu|<=2", key)
                if flat_sum(c["body"], eqs) != {0}:
                    bad("M_4 certificate does not sum to 1 (own arithmetic)", key)
        elif cs:
            bad("M_4 certificate on a system not labelled M_4-refuted", key)
        # wdag extractor
        x = w4.get("wdag_extractor")
        if w4["one"]:
            if x is None:
                bad("W_4 refuted without extractor record", key)
            elif x["extractor_dims"] != w4["dims"] or x["extractor_one_first_iteration"] != w4["one_first_iteration"] \
                    or not x["dims_equal_engine"] or not x["depth_equal_engine"]:
                bad("extractor dims/depth != engine", key)
        elif x is not None:
            bad("extractor record on a non-refuted system", key)
        # rc_b text rules
        kd = rb["kernel_dim"]
        if kd != 1:
            if rb["label"] != f"not applicable (kernel dim {kd})" or rb["substituted"]:
                bad("rc_b label for kernel dim != 1", key)
        else:
            lin = rb["ell_linear_support"]
            if not lin:
                want = "REFUTED-AT-DEGREE-2" if rb["ell_const"] else "ELL-TRIVIAL"
                if rb["label"] != want or rb["substituted"]:
                    bad("rc_b label for zero linear part", key)
            else:
                if rb["label"] != "SUBSTITUTED" or not rb["substituted"] or rb["j_star"] != min(lin):
                    bad("rc_b substituted/j_star", key)
        if rb["substituted"]:
            r3, r4, wp = cl.get((key, "R'_3")), cl.get((key, "R'_4")), cl.get((key, "W'_4"))
            if r3 is None or r4 is None or wp is None:
                bad("substituted without R'_3/R'_4/W'_4", key)
                continue
            if rb["T5_applicable"] != (r4["dims_by_deg"][3] == r3["rank"]):
                bad("T5_applicable rule", key)
            if rb["T5_applicable"]:
                pr = rb.get("T5_prediction")
                if pr != {"W4_refuted": bool(r4["one"]), "W4_final_dim": r4["rank"] + 834}:
                    bad("T5_prediction rule", key)
            if rb.get("subst_profile_is_semiregular") != (r4["dims_by_deg"] == [0, 0, 16, 288, 2328]):
                bad("subst semiregular flag", key)
            if w4["final_dim"] != wp["final_dim"] + 834 or w4["one"] != wp["one"]:
                bad("T4 relation (archived records)", key)
        else:
            if any((key, n) in cl for n in ("R'_3", "R'_4", "W'_4")):
                bad("R' records on an unsubstituted system", key)
        if m4.get("profile_is_unsubst_semiregular") != (m4["dims_by_deg"] == [0, 0, 17, 323, 2771]):
            bad("unsubst semiregular flag", key)
    # the closures file has nothing with D >= 5
    names = sorted({k[1] for k in cl})
    B = {"systems": len(inst), "closure_names_in_file": names,
         "M_4_refuted_systems_certificate_checked_total_all_arms": n_m4_checked,
         "violations": {k: {"count": len(v), "examples": v[:5]} for k, v in V.items()}}
    print("B", json.dumps(B)[:2000], flush=True)
    out = {"task": "TASK-20260926-0f8aec", "joint": "J3", "A_literal_vs_archived": A, "B_glue_checks_all_systems": B}
    json.dump(out, open(OUTDIR / "j3-compare.json", "w"), indent=1)
    print("WROTE j3-compare.json")


if __name__ == "__main__":
    main()
