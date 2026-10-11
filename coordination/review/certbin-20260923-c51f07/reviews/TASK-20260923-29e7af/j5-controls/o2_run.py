#!/usr/bin/env python3
"""J5 / proves-too-much object O2, step 2: ONE invocation of the ARCHIVED
pipeline (engine.process_family, unchanged) on the declared O2 family at D = 4,
200 instances (R0 + 199 targets from o2-declaration.json). Then the sealed
prediction (o2-prediction.json) is checked.

Classification (s, sols) uses the archived families.classify_null_instance
(oracle B + witness check), the same path as F-NULLF2. The per-instance T_ops
prefix check re-uses the archived elim.eliminate on the SAME 200 instances
(no new instance). Verification computation under DEC-20260923-4d7a19; not a
trial, no RUN id, not evidence about H-CERTBIN-a73f1c.
"""
import json
import os
import sys
import time

REPO = "/home/user/crypto-autoresearcher"
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/impl")
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IMPL)

import numpy as np  # noqa: E402
from gf2n import TableField  # noqa: E402
from macaulay import MacaulayShape, affine_basis, affine_combine, NEQ, EQ_MONS  # noqa: E402
from families import classify_null_instance  # noqa: E402
from engine import process_family  # noqa: E402
from elim import eliminate  # noqa: E402


def log(msg):
    print(msg, flush=True)


def main():
    t0 = time.time()
    decl = json.load(open(os.path.join(HERE, "o2-declaration.json")))
    pred = json.load(open(os.path.join(HERE, "o2-prediction.json")))
    P_hi = pred["P_hi_rank_of_degree_ge3_block"]
    b = pred["column_boundary_b_first_degree2_col"]
    L_ref = pred["L_ref_rank_M4_E0"]
    F = TableField()
    B = json.load(open(os.path.join(RUN, "curve.json")))["B"]
    E0, _ = affine_basis(F, B)
    Cj = []
    for cj in decl["c_j"]:
        Cm = np.zeros_like(E0)
        for k in range(NEQ):
            Cm[k, 0] = (cj >> k) & 1
        Cj.append(Cm)
    assert EQ_MONS[0] == ()
    build = lambda inst: affine_combine(E0, Cj, inst["x_R"])  # noqa: E731
    S = MacaulayShape(4)
    ctx = {"F": F, "shapes": {4: S}}
    ref = {"selected_as": "R0", "x_R": 0}
    ref.update(classify_null_instance(F, build(ref)))
    targets = []
    for i, r in enumerate(decl["r_targets_idx_1_to_199"]):
        t = {"idx": i + 1, "x_R": r, "degenerate": False}
        t.update(classify_null_instance(F, build(t)))
        targets.append(t)
    assert len(targets) + 1 == 200
    log(f"classified 200 O2 instances ({time.time() - t0:.0f}s); running process_family")
    res, live, _ = process_family(ctx, "O2-CONSTCOL", 4, ref_insts=[ref], targets=targets, build_E=build,
                                  reverse=False, planes_E=[E0] + Cj, cross_groups={}, log=log, affine_route=True)
    R0 = live["own"][0]
    modal = live["modal"]
    L = len(R0.p)
    hz = res["hazards"]["R0"]
    # ---- prediction checks (pipeline outputs)
    rows = []
    for rec in res["records"]:
        m = rec["refs"]["R0"]
        rows.append({"idx": rec["idx"], "s": rec["s"], "rank": rec["rank"], "match": m["match"], "kdiv": m["kdiv"],
                     "f_div": m["f_div"], "div_col": m["div_col"], "div_deg": m["div_deg"],
                     "replay_first_zero": m["replay_first_zero"], "one_in_R": rec["one_in_R"],
                     "PS0_fail": rec["PS0_fail"], "PS1_fail": rec["PS1_fail"], "PS3_fail": rec["PS3_fail"]})
    # ---- T_ops prefix check with the archived eliminate on the same instances
    ops_prefix_ok = []
    R0_ops = [(int(p), int(c), tuple(int(x) for x in X)) for p, c, X in zip(R0.res.p, R0.res.c, R0.res.X)]
    for t in targets:
        er, _, _ = eliminate(S.build(build(t)), S.C, keep_ops=True, with_row_pass=False)
        ops = [(int(p), int(c), tuple(int(x) for x in X)) for p, c, X in zip(er.p[:P_hi], er.c[:P_hi], er.X[:P_hi])]
        ops_prefix_ok.append(ops == R0_ops[:P_hi])
    a_nz = hz["a_nonzero"]
    a0 = hz["a0"]
    first_nonzero_a = next((k for k, x in enumerate(a_nz) if x), None)
    checks = {
        "L_ref_pipeline": L, "L_ref_predicted": L_ref, "L_ref_equal": L == L_ref,
        "R0_steps_on_cols_lt_b": int(sum(1 for c in R0.res.c if c < b)), "P_hi_predicted": P_hi,
        "R0_step_P_hi_minus_1_col": int(R0.res.c[P_hi - 1]), "R0_step_P_hi_col": int(R0.res.c[P_hi]) if L > P_hi else None,
        "all_kdiv_ge_P_hi": all(r["kdiv"] >= P_hi for r in rows),
        "min_kdiv": min(r["kdiv"] for r in rows),
        "all_f_div_ge_bound": all(r["f_div"] >= P_hi / L_ref - 1e-12 for r in rows),
        "min_f_div": min(r["f_div"] for r in rows), "f_div_bound": P_hi / L_ref,
        "all_div_deg_le_2_or_none": all(r["div_deg"] is None or r["div_deg"] <= 2 for r in rows),
        "div_deg_counts": {str(d): sum(1 for r in rows if r["div_deg"] == d) for d in (None, 0, 1, 2, 3, 4)},
        "all_replay_first_zero_ge_P_hi": all(r["replay_first_zero"] >= P_hi for r in rows),
        "a_k_zero_for_all_k_lt_P_hi": all(x == 0 for x in a_nz[:P_hi]),
        "a_k0_one_for_all_k_lt_P_hi": all(x == 1 for x in a0[:P_hi]),
        "first_k_with_a_k_nonzero": first_nonzero_a,
        "T_ops_prefix_identical_through_P_hi_all_199": all(ops_prefix_ok), "n_T_ops_prefix_identical": sum(ops_prefix_ok),
        "modal_idx": res["modal_info"]["modal_idx"] if res["modal_info"] else None,
        "modal_T_strict_prefix_equals_R0_through_P_hi": (
            [(int(p), int(c)) for p, c in zip(modal.res.p[:P_hi], modal.res.c[:P_hi])] ==
            [(p, c) for p, c, _ in R0_ops[:P_hi]]) if modal is not None else None,
        "retention_vs_R0": {g: sum(r["match"][g] for r in rows) / len(rows) for g in ("rank", "set", "strict", "ops")},
        "K_sampled": hz["K_sampled"], "K_exact": hz.get("K_exact"), "K_rank": hz.get("K_rank"),
        "caff_direct": res["caff_direct"], "hash_anomalies": res["hash_anomalies"],
        "PS_fail_any": any(r["PS0_fail"] or r["PS1_fail"] or r["PS3_fail"] for r in rows),
        "sat_count": sum(1 for r in rows if r["s"] >= 1), "one_in_R_count": sum(1 for r in rows if r["one_in_R"]),
    }
    checks["signature_met"] = all(checks[k] for k in (
        "L_ref_equal", "all_kdiv_ge_P_hi", "all_f_div_ge_bound", "all_div_deg_le_2_or_none",
        "all_replay_first_zero_ge_P_hi", "a_k_zero_for_all_k_lt_P_hi", "a_k0_one_for_all_k_lt_P_hi",
        "T_ops_prefix_identical_through_P_hi_all_199")) and checks["R0_steps_on_cols_lt_b"] == P_hi
    out = {"checks": checks, "rows": rows, "hazard_R0_first_after_P_hi": {
        "S_k": hz["S_k"][P_hi:P_hi + 40], "zeros_k": hz["zeros_k"][P_hi:P_hi + 40], "h_k": hz["h_k"][P_hi:P_hi + 40]},
        "wall_seconds": round(time.time() - t0, 1), "numpy": np.__version__, "pid": os.getpid()}
    json.dump(out, open(os.path.join(HERE, "o2-results.json"), "w"), indent=1)
    print(json.dumps(checks, indent=1))


if __name__ == "__main__":
    main()
