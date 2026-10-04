#!/usr/bin/env python3
"""J2 (1): LITERAL, slow W_4 of the validator's own (own_algebra.literal_W)
beside the archived closure of RUN-CERTBIN-c417e0, TASK-20260924-c83b05.

Instance selection rule (declared here, applied mechanically; 6 archived
instances, within RV-7's 20):
  - U62: the lowest-idx instance;
  - S62: the lowest-idx instance, and the instance with the SMALLEST archived
    W_4 final_dim (ties -> lowest idx), chosen to maximise the non-trivial
    content of W_4 (largest codimension);
  - C20: the lowest-idx instance;
  - N-AFF62 and N-F262: the lowest-idx instance of each.
For each instance:
  (a) the Boolean system is decoded by OWN code from instance-sets.json E_hex
      (the bytes the engine used), and cross-checked: curve instances against
      S_3 evaluated at all 2^18 points with own F_{2^17} arithmetic from the
      Stage-1 archived x_R (a degree <= 2 multilinear polynomial is determined
      by its 2^18 values); N-AFF62 against A0 + sum_j r_j Aj recomputed from
      p1-instances.json.gz; N-F262 against the p1 per-target E_hex;
  (b) own M_4 (spec row/column conventions) compared ROW BY ROW, bit-level,
      with the engine's Closure(18, 4, 17).build_M and the copied
      MacaulayShape(4).build (imported from impl/ only to build the SAME
      object for the comparison, RV-3);
  (c) own rank_4 and "1 in R_4" against the archived M_4 record;
  (d) own LITERAL W_4: dims per iteration, fixpoint index, first iteration
      containing 1, final dim, dims by degree, against the archived W_4 record;
  (e) the archived engine's w_closure re-run on the same system, and its final
      basis compared bit-level with the literal final basis (mutual
      containment + equal dimension).
Outputs: j2-constructions/literal_w4_results.json
"""
import gzip
import json
import os
import resource
import sys
import time

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0")
SRC = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05")
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/impl")
resource.setrlimit(resource.RLIMIT_AS, (3 * 1024 ** 3, 3 * 1024 ** 3))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import own_algebra as oa  # noqa: E402


def load():
    inst = json.load(open(os.path.join(RUN, "instance-sets.json")))
    recs = {}
    for line in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt"):
        r = json.loads(line)
        recs[(r["key"], r["closure"])] = r
    return inst, recs


def select(inst, recs):
    sets = inst["sets"]
    lo = lambda s: min(sets[s], key=lambda x: x["idx"])  # noqa: E731
    s62_min = min(sets["S62"], key=lambda x: (recs[(x["key"], "W_4")]["final_dim"], x["idx"]))
    chosen = [lo("U62"), lo("S62"), s62_min, lo("C20"), lo("N-AFF62"), lo("N-F262")]
    out, seen = [], set()
    for c in chosen:
        if c["key"] not in seen:
            out.append(c)
            seen.add(c["key"])
    return out


def system_checks(it, curve, s3t, p1):
    eqs = oa.eqs_from_hex(it["E_hex"])
    fam = it["family"]
    res = {"family": fam}
    if fam == "F-S3":
        xr_stage1 = s3t[it["idx"]]
        res["x_R_instance_sets"] = it["archived"]["x_R"]
        res["x_R_stage1_targets"] = xr_stage1
        S = oa.s3_all_points(curve["B"], xr_stage1)
        tt = oa.eval_eqs_all(eqs)
        ok = all(np.array_equal(tt[k], ((S >> k) & 1).astype(np.uint8)) for k in range(17))
        res["E_hex_equals_own_S3_descent_at_all_2^18_points"] = bool(ok)
        sols = [int(u) for u in np.flatnonzero(S == 0)]
        res["own_s_from_S3"] = len(sols)
    elif fam == "F-AFF-1":
        r = it["archived"]["x_R"]
        A0 = [int(h, 16) for h in p1["F-AFF-1"]["A0_hex"]]
        Aj = [[int(h, 16) for h in row] for row in p1["F-AFF-1"]["Aj_hex"]]
        rows = list(A0)
        for j in range(17):
            if (r >> j) & 1:
                rows = [x ^ y for x, y in zip(rows, Aj[j])]
        res["E_hex_equals_own_A0_plus_sum_rj_Aj"] = rows == [int(h, 16) for h in it["E_hex"]]
    else:
        t = {x["idx"]: x for x in p1["F-NULLF2"]["targets"]}[it["idx"]]
        res["E_hex_equals_p1_E_hex"] = [int(h, 16) for h in t["E_hex"]] == [int(h, 16) for h in it["E_hex"]]
    tt = oa.eval_eqs_all(eqs)
    res["own_s_exhaustive"] = int((np.bitwise_or.reduce(tt, axis=0) == 0).sum())
    res["archived_s"] = it["archived"]["s"]
    return eqs, res


def engine_rows_to_own(cl, packed, space):
    dense = cl.unpack(packed)
    out = []
    for row in dense:
        out.append(space.poly(int(cl.col_mask[c]) for c in np.flatnonzero(row)))
    return out


def main():
    t00 = time.time()
    inst, recs = load()
    curve = json.load(open(os.path.join(SRC, "curve.json")))
    s3t = {}
    for line in gzip.open(os.path.join(SRC, "targets-F-S3.jsonl.gz"), "rt"):
        r = json.loads(line)
        s3t[r["idx"]] = r["x_R"]
    p1 = json.load(gzip.open(os.path.join(SRC, "checkpoint", "p1-instances.json.gz"), "rt"))
    chosen = select(inst, recs)
    sys.path.insert(0, IMPL)
    from closure import Closure            # engine, imported ONLY for (b) and (e)
    from macaulay import MacaulayShape
    from instances import E_from_hex, eqs_of
    space = oa.Space(18, 4)
    cl4 = Closure(18, 4, 17)
    sh4 = MacaulayShape(4)
    results = []
    for it in chosen:
        t0 = time.time()
        key = it["key"]
        eqs, sysres = system_checks(it, curve, s3t, p1)
        # engine's own decoding of the same bytes, for the bit-level comparison
        Eeng = E_from_hex(it["E_hex"])
        eqs_eng = eqs_of(Eeng)
        sysres["own_decoding_equals_engine_decoding"] = [sorted(f) for f in eqs] == [sorted(f) for f in eqs_eng]
        # (b) M_4 row by row
        own_rows = oa.macaulay_rows(space, eqs, 4)
        Meng = cl4.build_M(eqs_eng)
        Mshape = sh4.build(Eeng)
        eng_rows = engine_rows_to_own(cl4, Meng, space)
        m4 = {"shape_engine": list(Meng.shape) + [cl4.C], "rows_own": len(own_rows), "cols_own": len(space.mons),
              "rows_bit_identical_to_engine_build_M": own_rows == eng_rows,
              "engine_build_M_equals_copied_MacaulayShape": bool(np.array_equal(Meng, Mshape)),
              "zero_rows": sum(1 for r in own_rows if r == 0)}
        # engine column order == spec descending degrevlex, constant last
        def degrevlex_key(m):          # larger = earlier column
            return m
        cols = [int(x) for x in cl4.col_mask]
        ok_order = cols[-1] == 0
        for a, b in zip(cols, cols[1:]):
            da, db = oa.popcount(a), oa.popcount(b)
            if da != db:
                ok_order &= da > db
            else:
                diff = a ^ b
                i = diff.bit_length() - 1
                ok_order &= not ((a >> i) & 1)      # a > b iff a lacks v_i at the largest differing index
        m4["engine_columns_are_spec_descending_degrevlex_constant_last"] = bool(ok_order)
        # (c) own rank_4, 1 in R_4
        b0 = oa.span_basis(own_rows)
        arch_m4 = recs[(key, "M_4")]
        m4.update({"own_rank_4": len(b0), "own_one_in_R_4": 0 in b0,
                   "archived_rank_4_closures_jsonl": arch_m4["rank"], "archived_one_in_R_4_closures_jsonl": arch_m4["one"],
                   "archived_rank_4_stage1": it["archived"]["rank_4"], "archived_one_in_R_4_stage1": it["archived"]["one_in_R_4"]})
        m4["agree"] = (m4["own_rank_4"] == arch_m4["rank"] == it["archived"]["rank_4"]
                       and m4["own_one_in_R_4"] == arch_m4["one"] == it["archived"]["one_in_R_4"])
        # (d) literal W_4
        tl = time.time()
        lit, lbasis, _ = oa.literal_W(space, eqs, 4)
        tlit = time.time() - tl
        arch = recs[(key, "W_4")]
        cmp_fields = ["dims", "iterations_to_fixpoint", "final_dim", "one", "one_first_iteration", "dims_by_deg"]
        lit_vs_arch = {f: {"literal": lit[f], "archived": arch[f], "equal": lit[f] == arch[f]} for f in cmp_fields}
        # (e) engine re-run and bit-level final-space comparison
        te = time.time()
        erec, ecert = cl4.w_closure(eqs_eng, want_cert=False)
        teng = time.time() - te
        fb, fl = cl4._final
        eng_final = engine_rows_to_own(cl4, fb, space)
        eng_in_lit = all(oa.in_span(lbasis, v) for v in eng_final)
        ebasis = oa.span_basis(eng_final)
        lit_in_eng = all(oa.in_span(ebasis, v) for v in lbasis.values())
        rerun_vs_arch = {f: erec[f] == arch[f] for f in cmp_fields}
        results.append({
            "key": key, "set": key.split(":")[0], "idx": it["idx"],
            "system": sysres, "M_4": m4,
            "literal_W4": lit, "literal_seconds": round(tlit, 1),
            "literal_vs_archived": lit_vs_arch,
            "literal_equals_archived_all_fields": all(v["equal"] for v in lit_vs_arch.values()),
            "engine_rerun_equals_archived": rerun_vs_arch, "engine_rerun_seconds": round(teng, 1),
            "bit_level_final_space": {"engine_final_basis_rows": len(eng_final), "engine_final_rank_own": len(ebasis),
                                      "literal_final_dim": len(lbasis),
                                      "engine_final_subset_literal": eng_in_lit, "literal_final_subset_engine": lit_in_eng,
                                      "identical_spaces": bool(eng_in_lit and lit_in_eng and len(ebasis) == len(lbasis))},
            "archived_new_fallen_per_iteration": arch["new_fallen_per_iteration"],
            "archived_stack_rows_per_iteration": arch["stack_rows_per_iteration"],
            "wall_seconds": round(time.time() - t0, 1)})
        print(json.dumps({k: results[-1][k] for k in ("key", "literal_equals_archived_all_fields", "wall_seconds")}),
              results[-1]["bit_level_final_space"]["identical_spaces"], m4["agree"],
              m4["rows_bit_identical_to_engine_build_M"], flush=True)
    out = {"task_id": "TASK-20260924-c83b05", "joint": "J2", "construction": "literal W_4 vs archived closure",
           "selection_rule": __doc__.split("Instance selection rule")[1].split("For each instance")[0].strip(),
           "instances": results,
           "all_literal_equal_archived": all(r["literal_equals_archived_all_fields"] for r in results),
           "all_bit_level_identical": all(r["bit_level_final_space"]["identical_spaces"] for r in results),
           "all_M4_rows_bit_identical": all(r["M_4"]["rows_bit_identical_to_engine_build_M"] for r in results),
           "all_M4_rank_agree": all(r["M_4"]["agree"] for r in results),
           "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
           "wall_seconds": round(time.time() - t00, 1)}
    json.dump(out, open(os.path.join(HERE, "literal_w4_results.json"), "w"), indent=1)
    print("done", out["all_literal_equal_archived"], out["all_bit_level_identical"], out["all_M4_rows_bit_identical"],
          out["all_M4_rank_agree"], out["wall_seconds"])


if __name__ == "__main__":
    main()
