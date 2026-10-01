"""VC-4 second route: evaluate every flat-v1 and wdag-v1 certificate as
functions {0,1}^20 -> F_2 (the evaluation map B -> F_2^(2^20) is a ring
isomorphism): tt(mu * f_k) = tt(mu) AND tt(f_k), tt(v_j * p) = tt(v_j) AND tt(p),
sums are XOR. poly = 1 in B iff its truth table is all ones. Node degrees are
recomputed from the ANF obtained by a Moebius transform of each node's truth
table. Independent of the monomial-mask arithmetic of certs.py.
Writes work/certs-tt.jsonl.gz.
Usage: run_certs_tt.py <instances.jsonl.gz> <certificates.jsonl.gz> <workdir> [nproc]"""
import gzip
import json
import sys
import time
from multiprocessing import Pool

import numpy as np

import kern
import layout as LY

NPT = 1 << 20
IDX = np.arange(NPT, dtype=np.uint32)
TT_V = [np.packbits(((IDX >> i) & 1).astype(np.uint8), bitorder="little").view(np.uint64) for i in range(20)]
ONES = np.full(NPT // 64, np.uint64(0xFFFFFFFFFFFFFFFF), dtype=np.uint64)
G = {}


def init(ehex):
    G["ehex"] = ehex
    G["cache"] = {}


def tt_system(key):
    c = G["cache"]
    if key not in c:
        if len(c) > 32:
            c.clear()
        E = LY.decode_E(G["ehex"][key])
        tt = kern.mobius(LY.anf_u32(E), 20)
        c[key] = [np.packbits(((tt >> k) & 1).astype(np.uint8), bitorder="little").view(np.uint64)
                  for k in range(19)]
    return c[key]


def tt_mu(mu):
    t = ONES
    for i in mu:
        t = t & TT_V[i]
    return t


def anf_degree(tt_packed):
    bits = np.unpackbits(tt_packed.view(np.uint8), bitorder="little").astype(np.uint32)
    anf = kern.mobius(bits, 20)
    nz = np.flatnonzero(anf & 1)
    return int(LY.POP[nz].max()) if nz.size else -1


def work(item):
    lineno, line = item
    rec = json.loads(line)
    fk = tt_system(rec["key"])
    b = rec["body"]
    out = {"line": lineno, "key": rec["key"], "format": rec["format"]}
    if rec["format"] == "flat-v1":
        acc = np.zeros(NPT // 64, dtype=np.uint64)
        for mu, k in b["C"]:
            acc ^= tt_mu(mu) & fk[k]
        out["tt_output_is_one"] = bool(np.array_equal(acc, ONES))
    else:
        vals, degs = [], []
        for nd in b["nodes"]:
            acc = np.zeros(NPT // 64, dtype=np.uint64)
            for mu, k in nd["rows"]:
                acc ^= tt_mu(mu) & fk[k]
            for j, c in nd["prods"]:
                acc ^= TT_V[j] & vals[c]
            vals.append(acc)
            degs.append(anf_degree(acc))
        out["tt_output_is_one"] = bool(np.array_equal(vals[b["output"]], ONES))
        used = {c for nd in b["nodes"] for _, c in nd["prods"]}
        out["tt_node_degrees"] = degs
        out["tt_rule_c_ok"] = all(degs[c] <= 3 for c in used)
        out["tt_rule_d_ok"] = all(d <= 4 for d in degs)
    return out


def main():
    inst, cert_path, workdir = sys.argv[1:4]
    nproc = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    t0 = time.time()
    ehex = {json.loads(l)["key"]: json.loads(l)["E_hex"] for l in gzip.open(inst, "rt")}
    lines = list(enumerate(gzip.open(cert_path, "rt")))
    with Pool(nproc, initializer=init, initargs=(ehex,)) as pool:
        res = pool.map(work, lines, chunksize=10)
    with gzip.open(workdir + "/certs-tt.jsonl.gz", "wt") as f:
        for o in res:
            f.write(json.dumps(o, sort_keys=True) + "\n")
    print("done", len(res), round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
