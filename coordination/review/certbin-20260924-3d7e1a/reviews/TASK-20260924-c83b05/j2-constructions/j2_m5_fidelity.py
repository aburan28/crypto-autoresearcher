#!/usr/bin/env python3
"""J2: M_5 object fidelity (and, optionally, a literal W_5). TASK-20260924-c83b05.

Instance rule (declared; within RV-7's 20 archived instances, and overlapping
the literal-W_4 set): the lowest-idx instance of U62, S62, N-AFF62 and N-F262.
For each:
  (a) own M_5 rows (spec conventions: row = mu_index * 17 + k, mu of degree
      <= 3 in degree-then-lex order, content multilinear mu * f_k, zero rows
      retained) compared ROW BY ROW, bit-level, with the engine's
      Closure(18, 5, 17).build_M and the copied MacaulayShape(5).build;
  (b) own rank_5 and "1 in R_5" by own top-bit elimination, against the
      archived M_5 record of closures.jsonl.gz;
  (c) with --w5: own LITERAL W_5 on the lowest-idx S62 instance (the only set
      on which W_5 ran), against the archived W_5 record.
Output: j2-constructions/m5_fidelity_results.json
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
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/impl")
resource.setrlimit(resource.RLIMIT_AS, (3 * 1024 ** 3, 3 * 1024 ** 3))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import own_algebra as oa  # noqa: E402


def main():
    do_w5 = "--w5" in sys.argv
    t00 = time.time()
    inst = json.load(open(os.path.join(RUN, "instance-sets.json")))
    recs = {}
    for line in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt"):
        r = json.loads(line)
        recs[(r["key"], r["closure"])] = r
    sets = inst["sets"]
    chosen = [min(sets[s], key=lambda x: x["idx"]) for s in ("U62", "S62", "N-AFF62", "N-F262")]
    sys.path.insert(0, IMPL)
    from closure import Closure
    from macaulay import MacaulayShape
    from instances import E_from_hex, eqs_of
    cl5 = Closure(18, 5, 17)
    sh5 = MacaulayShape(5)
    sp = oa.Space(18, 5)
    out = []
    for it in chosen:
        t0 = time.time()
        key = it["key"]
        eqs = oa.eqs_from_hex(it["E_hex"])
        E = E_from_hex(it["E_hex"])
        Meng = cl5.build_M(eqs_of(E))
        same_shape = bool(np.array_equal(Meng, sh5.build(E)))
        own = oa.macaulay_rows(sp, eqs, 5)
        dense = cl5.unpack(Meng)
        bad = 0
        for r in range(cl5.R):
            eng = sp.poly(int(cl5.col_mask[c]) for c in np.flatnonzero(dense[r]))
            if eng != own[r]:
                bad += 1
        del dense
        tb = time.time()
        basis = oa.span_basis(own)
        te = time.time() - tb
        arch = recs[(key, "M_5")]
        row = {"key": key, "shape": [cl5.R, cl5.C], "own_rows": len(own), "own_cols": len(sp.mons),
               "rows_differing_from_engine_build_M": bad, "engine_build_M_equals_copied_MacaulayShape5": same_shape,
               "zero_rows": sum(1 for v in own if v == 0),
               "own_rank_5": len(basis), "own_one_in_R_5": 0 in basis,
               "own_dims_by_deg": oa.dims_by_deg(sp, basis),
               "archived_rank_5": arch["rank"], "archived_one_in_R_5": arch["one"],
               "archived_dims_by_deg": arch.get("dims_by_deg"),
               "elimination_seconds": round(te, 1), "wall_seconds": round(time.time() - t0, 1)}
        row["agree"] = (bad == 0 and same_shape and row["own_rank_5"] == arch["rank"] and row["own_one_in_R_5"] == arch["one"]
                        and (arch.get("dims_by_deg") is None or row["own_dims_by_deg"] == arch["dims_by_deg"]))
        out.append(row)
        print(json.dumps(row), flush=True)
        del basis, own
    res = {"task_id": "TASK-20260924-c83b05", "joint": "J2", "construction": "M_5 fidelity", "instances": out,
           "all_agree": all(r["agree"] for r in out)}
    if do_w5:
        it = min(sets["S62"], key=lambda x: x["idx"])
        key = it["key"]
        eqs = oa.eqs_from_hex(it["E_hex"])
        t0 = time.time()
        lit, _, _ = oa.literal_W(sp, eqs, 5)
        arch = recs[(key, "W_5")]
        fields = ["dims", "iterations_to_fixpoint", "final_dim", "one", "one_first_iteration", "dims_by_deg"]
        res["literal_W5"] = {"key": key, "literal": lit,
                             "vs_archived": {f: {"literal": lit[f], "archived": arch[f], "equal": lit[f] == arch[f]} for f in fields},
                             "all_equal": all(lit[f] == arch[f] for f in fields),
                             "wall_seconds": round(time.time() - t0, 1)}
        print(json.dumps({k: v for k, v in res["literal_W5"].items() if k != "literal"}), flush=True)
    res["peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    res["wall_seconds"] = round(time.time() - t00, 1)
    json.dump(res, open(os.path.join(HERE, "m5_fidelity_results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
