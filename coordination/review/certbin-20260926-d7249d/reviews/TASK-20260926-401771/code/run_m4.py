"""VC-6: for every S3-U400 system decide 1 in rowspace(M_4) by own elimination.
Where 1 is absent: extract one functional lambda on B_{<=4} (ann-v1 coordinate
order) with lambda(row) = 0 for every M_4 row and lambda(1) = 1, check it
against the UNREDUCED M_4 rows, and write it. Where 1 is present: emit an own
flat-v1 certificate with max |mu| <= 2 (row provenance through an augmented
elimination) and check it with the flat-v1 checker.
Also records rank M_4 and dims_by_deg(M_4) (d = 0..4) from the pivot degrees.
Usage: run_m4.py <instances.jsonl.gz> <workdir> <witness_out.jsonl.gz> [arm] [nproc]"""
import gzip
import json
import sys
import time
from multiprocessing import Pool

import numpy as np

import certs
import kern
import layout as LY

MUS = LY.mu_order(2, LY.NV)


def work(rec):
    t1 = time.time()
    S = certs.System(LY.decode_E(rec["E_hex"]))
    M4 = S.m4_packed()
    R, rank, piv = kern.rref(M4, LY.NCOL4)
    pdeg = LY.ANN_DEG_OF_COL[piv]
    dims = [int((pdeg <= d).sum()) for d in range(5)]
    one_in = bool(rank and piv[-1] == LY.CONST_COL)
    info = {"key": rec["key"], "rank_M4": int(rank), "dims_by_deg_M4": dims, "one_in_M4": one_in}
    wit = None
    if not one_in:
        Rd = kern.unpack_rows(R[:rank], LY.NCOL4)
        lam = np.zeros(LY.NCOL4, dtype=np.uint8)
        lam[LY.CONST_COL] = 1
        lam[piv] = Rd[:, LY.CONST_COL]
        lp = kern.pack_rows(lam[None, :], LY.WORDS4)
        nbad, _, _ = kern.parity_check(lp, M4)
        info["witness_vanishes_on_all_4009_rows"] = nbad == 0
        info["witness_lambda_of_1"] = int(lam[LY.CONST_COL])
        info["witness_checked"] = bool(nbad == 0 and lam[LY.CONST_COL] == 1)
        wit = {"key": rec["key"], "kind": "M4_non_refutation_witness", "D": 4, "nv": 20, "neq": 19,
               "coordinate_order": "ann-v1: multilinear monomials of degree <= 4 in v_0..v_19 sorted by "
                                   "(-degree, bitmask ascending); bit c (LSB first) = lambda on coordinate c",
               "lambda_hex": certs.packed_to_hex(lp[0]), "checked": info["witness_checked"]}
    else:
        nrows = M4.shape[0]
        wa = (nrows + 63) // 64
        aug = np.zeros((nrows, LY.WORDS4 + wa), dtype=np.uint64)
        aug[:, :LY.WORDS4] = M4
        ident = np.zeros((nrows, wa * 64), dtype=np.uint8)
        ident[np.arange(nrows), np.arange(nrows)] = 1
        aug[:, LY.WORDS4:] = kern.pack_rows(ident, wa)
        Ra, ra, pa = kern.rref(aug, LY.NCOL4)
        ridx = int(np.flatnonzero(pa == LY.CONST_COL)[0])
        prov = kern.unpack_rows(Ra[ridx:ridx + 1, LY.WORDS4:], nrows)[0]
        C = []
        for i in np.flatnonzero(prov):
            a, k = divmod(int(i), LY.NEQ)
            C.append([list(MUS[a]), k])
        C.sort(key=lambda e: (tuple(e[0]), e[1]))
        chk = certs.check_flat_as_M4(S, {"C": C})
        info["own_flat_certificate_verified"] = bool(chk["verified"])
        info["own_flat_certificate_max_mu"] = chk["max_mu"]
        info["own_flat_certificate_accepted_as_M4"] = bool(chk["accepted_as_M4"])
        wit = {"key": rec["key"], "kind": "M4_refutation_own_flat_v1", "format": "flat-v1", "closure": "M_4",
               "body": {"C": C}, "checked": bool(chk["accepted_as_M4"])}
    info["seconds"] = round(time.time() - t1, 2)
    return info, wit


def main():
    inst, workdir, wit_out = sys.argv[1:4]
    arm = sys.argv[4] if len(sys.argv) > 4 else "S3-U400"
    nproc = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    t0 = time.time()
    recs = [json.loads(l) for l in gzip.open(inst, "rt")]
    recs = [r for r in recs if r["arm"] == arm]
    with Pool(nproc) as pool:
        res = pool.map(work, recs, chunksize=4)
    with gzip.open(workdir + "/m4-%s.jsonl.gz" % arm, "wt") as f:
        for info, _ in res:
            f.write(json.dumps(info, sort_keys=True) + "\n")
    with gzip.open(wit_out, "wt") as f:
        for _, w in res:
            f.write(json.dumps(w, sort_keys=True) + "\n")
    print("done", len(res), round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
