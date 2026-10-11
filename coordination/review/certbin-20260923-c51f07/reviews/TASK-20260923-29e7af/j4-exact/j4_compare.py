#!/usr/bin/env python3
"""J4 step 3 (TASK-20260923-29e7af): compare the SEALED predictions with the
archived pivot-hazards.json, pivot by pivot, and the archived affine forms in
the phase-2 checkpoint with mine. Run only after ORDER.log records the seal.

Outputs: comparison-D4.json (every mismatch listed individually) and
p2-table.tsv (the per-pair table the card asks for).
"""
import gzip
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
DECLARED = ["U1", "U2", "U3", "S1", "S2"]

import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("jp", os.path.join(HERE, "j4_predict.py"))
jp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jp)


def main():
    pred = json.load(open(os.path.join(HERE, "predictions-D4.json")))
    forms = json.load(open(os.path.join(HERE, "forms-D4.json")))["refs"]
    ph = json.load(open(os.path.join(RUN, "pivot-hazards.json")))["families"]
    fams = {f: jp.targets(f) for f in ("F-S3", "F-RANDX", "F-PLANT")}
    out = {"per_ref_all_pivots": {}, "cross": {}, "archived_forms_vs_mine": {}, "P2": {}}

    def compare_family(fam, key, lab, scored_filter):
        F = forms[lab]
        a0 = np.array(F["a0"], dtype=np.uint8)
        a = np.array(F["a"], dtype=np.int64)
        rs = [x for i, x, dg in fams[fam] if not dg and scored_filter(i)]
        Sk, zk, dep, full = jp.hazard(jp.evalf(a0, a, rs))
        A = ph[fam]["D4"][key]
        K = len(a)
        mism = []
        for name, mine, arch in (("S_k", Sk.tolist(), A["S_k"]), ("zeros_k", zk.tolist(), A["zeros_k"]),
                                 ("sampled_dependent", dep.astype(int).tolist(), A["sampled_dependent"])):
            if len(arch) != K:
                mism.append({"field": name, "len_mine": K, "len_arch": len(arch)})
                continue
            for k in range(K):
                if mine[k] != arch[k]:
                    mism.append({"field": name, "k": k, "mine": mine[k], "archived": arch[k]})
        if "a_nonzero" in A:
            for k in range(K):
                if int(a[k] != 0) != A["a_nonzero"][k]:
                    mism.append({"field": "a_nonzero", "k": k, "mine": int(a[k] != 0), "archived": A["a_nonzero"][k]})
                if int(a0[k]) != A["a0"][k]:
                    mism.append({"field": "a0", "k": k, "mine": int(a0[k]), "archived": A["a0"][k]})
        hk_m = [round(float(zk[k] / Sk[k]), 6) if Sk[k] else None for k in range(K)]
        hk_bad = [k for k in range(K) if hk_m[k] != A["h_k"][k]]
        for k in hk_bad:
            mism.append({"field": "h_k", "k": k, "mine": hk_m[k], "archived": A["h_k"][k]})
        return {"n_scored_mine": len(rs), "n_scored_archived": A["n_scored"],
                "full_replay_survivors_mine": full, "full_replay_survivors_archived": A["full_replay_survivors"],
                "K_sampled_mine": int(dep.sum()), "K_sampled_archived": A["K_sampled"],
                "n_mismatches": len(mism), "mismatches": mism[:200]}, A

    for lab in DECLARED + ["modal"]:
        flt = (lambda i: i > 100) if lab == "modal" else (lambda i: True)
        res, A = compare_family("F-S3", lab, lab, flt)
        out["per_ref_all_pivots"][lab] = res
        for fam in ("F-RANDX", "F-PLANT"):
            key = f"F-S3:{lab}"
            if key in ph[fam]["D4"]:
                r2, _ = compare_family(fam, key, lab, lambda i: True)
                out["cross"].setdefault(fam, {})[lab] = r2

    # archived forms (phase-2 checkpoint) vs mine
    with gzip.open(os.path.join(RUN, "checkpoint", "p2-F-S3-D4.json.gz"), "rt") as f:
        ck = json.load(f)
    for r in ck["refs"]:
        lab = r["label"]
        if lab in forms and "forms_a" in r:
            out["archived_forms_vs_mine"][lab] = {
                "a_equal": r["forms_a"] == forms[lab]["a"], "a0_equal": r["forms_a0"] == forms[lab]["a0"]}

    # P2 set: archived membership vs mine, and the per-pair table
    arch_P2 = []
    for lab in DECLARED:
        A = ph["F-S3"]["D4"][lab]
        for k in range(len(A["S_k"])):
            if A["sampled_dependent"][k] and A["S_k"][k] >= 200:
                arch_P2.append((lab, k, A["h_k"][k]))
    mine_P2 = {(p["ref"], p["k"]): p for p in pred["P2"]}
    out["P2"]["archived_n"] = len(arch_P2)
    out["P2"]["mine_n"] = len(mine_P2)
    out["P2"]["membership_equal"] = sorted((l, k) for l, k, _ in arch_P2) == sorted(mine_P2)
    rows = []
    for lab, k, h_obs in arch_P2:
        p = mine_P2.get((lab, k))
        cls = p["class"] if p else "NOT_IN_MY_P2"
        if cls in ("DEP", "DEP_TAU"):
            pred_h = 0.0
            match = (h_obs == 0.0)
            band = "[0, 0]"
        else:
            S = p["S_k"]
            w = 3.29 / (2 * np.sqrt(S))
            band = f"[{0.5 - w:.4f}, {0.5 + w:.4f}]"
            match = (0.5 - w <= h_obs <= 0.5 + w)
        exact_equal = p is not None and round(p["h_exact_recomputed"], 6) == h_obs
        rows.append({"ref": lab, "k": k, "c_k": p["c_k"] if p else None, "a_hex": p["a_hex"] if p else None,
                     "rank_increment_literal": (cls != "DEP"), "rank_increment_mod_r0": (cls == "IND"),
                     "class": cls, "S_k": p["S_k"] if p else None,
                     "predicted_structural": ("0 exactly" if cls in ("DEP", "DEP_TAU") else f"~1/2 in 99.9% band {band}"),
                     "predicted_exact_h": round(p["h_exact_recomputed"], 6) if p else None,
                     "observed_h_k": h_obs, "structural_match": bool(match), "exact_match": bool(exact_equal)})
    out["P2"]["table"] = rows
    out["P2"]["n_structural_mismatch"] = sum(not r["structural_match"] for r in rows)
    out["P2"]["n_exact_mismatch"] = sum(not r["exact_match"] for r in rows)
    with open(os.path.join(HERE, "comparison-D4.json"), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(HERE, "p2-table.tsv"), "w") as f:
        cols = ["ref", "k", "c_k", "a_hex", "rank_increment_literal", "rank_increment_mod_r0", "class", "S_k",
                "predicted_structural", "predicted_exact_h", "observed_h_k", "structural_match", "exact_match"]
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    summ = {lab: {k: v for k, v in r.items() if k != "mismatches"} for lab, r in out["per_ref_all_pivots"].items()}
    print(json.dumps(summ, indent=1))
    print(json.dumps({fam: {lab: {k: v for k, v in r.items() if k != "mismatches"} for lab, r in d.items()}
                      for fam, d in out["cross"].items()}, indent=1))
    print(json.dumps(out["archived_forms_vs_mine"]))
    print({k: v for k, v in out["P2"].items() if k != "table"})


if __name__ == "__main__":
    main()
