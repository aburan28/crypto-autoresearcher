"""For VC-7 (h): decide, with own code, whether W_4 differs from M_4 on a system.
W_4 != M_4 iff W^(1) != W^(0), i.e. iff some v_j * b with b in the RREF basis
of rowspace(M_4) cap B_{<=3} lies outside rowspace(M_4) (EXP-CERTBIN-e94b27
mutant_closure_W_D iteration). Also records rank, 1 in M_4 and dims_by_deg(M_4).
Usage: run_step.py <instances.jsonl.gz> <workdir> <arm> <role> [nproc]"""
import gzip
import json
import sys
import time
from multiprocessing import Pool

import certs
import kern
import layout as LY


def work(rec):
    t1 = time.time()
    S = certs.System(LY.decode_E(rec["E_hex"]))
    R, rank, piv = kern.rref(S.m4_packed(), LY.NCOL4)
    pdeg = LY.ANN_DEG_OF_COL[piv]
    n_out, first = kern.step_outside(R[:rank], rank, LY.NCOL4, LY.NV, 3, piv, LY.ANN_DEG_OF_COL,
                                     LY.ANN_MASK_OF_COL, LY.ANN_COL_OF_MASK, stop_first=True)
    return {"key": rec["key"], "rank_M4": int(rank), "one_in_M4": bool(rank and piv[-1] == LY.CONST_COL),
            "dims_by_deg_M4": [int((pdeg <= d).sum()) for d in range(5)],
            "W1_ne_W0": bool(n_out > 0), "first_product_outside_basisrow_j": list(first) if n_out else None,
            "seconds": round(time.time() - t1, 2)}


def main():
    inst, workdir, arm, role = sys.argv[1:5]
    nproc = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    t0 = time.time()
    recs = [json.loads(l) for l in gzip.open(inst, "rt")]
    recs = [r for r in recs if r["arm"] == arm and r["role"] == role]
    with Pool(nproc) as pool:
        res = pool.map(work, recs, chunksize=2)
    with gzip.open(workdir + "/step-%s-%s.jsonl.gz" % (arm, role), "wt") as f:
        for o in res:
            f.write(json.dumps(o, sort_keys=True) + "\n")
    print("done", arm, role, len(res), sum(o["W1_ne_W0"] for o in res), round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
