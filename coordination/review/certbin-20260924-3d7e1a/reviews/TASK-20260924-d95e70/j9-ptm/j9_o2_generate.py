#!/usr/bin/env python3
"""J9 O2 generation -- TASK-20260924-d95e70, exactly per o2-declaration.yaml.
Seed 2026092431001; one numpy PCG64 generator; per draw: the F-NULLF2
construction (M[Upos] = g.integers(0, 2, size=Upos.size)), then
c = int(g.integers(0, 2)); row 16 replaced by v_0 + v_9 + c. Keep iff s = 0
by exhaustive 2^18 evaluation. First 20 kept; every draw recorded."""
import gzip
import hashlib
import json
import os
import sys
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "j7-mechanism"))
import rtlib as R  # noqa: E402

SRC = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
STAGE1_IMPL = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/impl"
SEED = 2026092431001
NKEEP = 20

EQ = []
for d in range(3):
    EQ.extend(sum(1 << i for i in c) for c in combinations(range(18), d))
COL = {m: j for j, m in enumerate(EQ)}
assert len(EQ) == 172


def E_of_sets(fs):
    E = np.zeros((17, 172), dtype=np.uint8)
    for k, f in enumerate(fs):
        for m in f:
            E[k, COL[m]] ^= 1
    return E


def to_hex(E):
    out = []
    for row in E:
        v = 0
        for j in np.flatnonzero(row):
            v |= 1 << int(j)
        out.append(format(v, "x"))
    return out


# ---------------- exhaustive evaluation (own, bit-sliced over 2^18) ----------
NV = 18
ALL = (1 << (1 << NV)) - 1
_u = np.arange(1 << NV, dtype=np.int64)
VT = []
for i in range(NV):
    bits = ((_u >> i) & 1).astype(np.uint8)
    VT.append(int.from_bytes(np.packbits(bits, bitorder="little").tobytes(), "little"))
MT = []
for m in EQ:
    t = ALL
    for i in range(NV):
        if (m >> i) & 1:
            t &= VT[i]
    MT.append(t)


def count_solutions(E):
    bad = 0
    for k in range(17):
        t = 0
        for j in np.flatnonzero(E[k]):
            t ^= MT[int(j)]
        bad |= t
    return (ALL & ~bad).bit_count()


def main():
    assert np.__version__ == "2.4.6", np.__version__
    B = json.load(open(os.path.join(SRC, "curve.json")))["B"]
    # union support U from MY descent
    E0 = E_of_sets(R.descent(B, 0))
    U = E0.astype(bool).copy()
    for j in range(17):
        U |= (E_of_sets(R.descent(B, 1 << j)) ^ E0).astype(bool)
    sizes = [int(x) for x in U.sum(axis=1)]
    p1 = json.load(gzip.open(os.path.join(SRC, "checkpoint", "p1-instances.json.gz"), "rt"))
    arch_sizes = p1["F-NULLF2"]["union_support_size_per_eq"]
    # cross-check with the archived Stage-1 affine basis (read-only import)
    sys.path.insert(0, STAGE1_IMPL)
    from gf2n import TableField
    from macaulay import affine_basis
    aE0, aEj = affine_basis(TableField(), B)
    aU = aE0.astype(bool).copy()
    for x in aEj:
        aU |= x.astype(bool)
    checks = {"union_sizes_mine": sizes, "union_sizes_archived": arch_sizes,
              "sizes_match": sizes == arch_sizes, "U_equals_archived_affine_basis_U": bool(np.array_equal(U, aU))}
    assert checks["sizes_match"] and checks["U_equals_archived_affine_basis_U"], checks
    # self-test of the exhaustive evaluator against archived s on 12 F-S3 targets
    st = []
    for line in gzip.open(os.path.join(SRC, "targets-F-S3.jsonl.gz"), "rt"):
        r = json.loads(line)
        if r["D"] == 4 and r["x_R"] and len(st) < 12:
            s = count_solutions(E_of_sets(R.descent(B, r["x_R"])))
            st.append({"idx": r["idx"], "archived_s": r["s"], "mine": s, "ok": s == r["s"]})
    checks["evaluator_selftest"] = st
    assert all(x["ok"] for x in st), st
    Upos = np.flatnonzero(U.reshape(-1))
    g = np.random.Generator(np.random.PCG64(SEED))
    draws, kept, seen = [], [], set()
    n = 0
    while len(kept) < NKEEP:
        M = np.zeros(17 * 172, dtype=np.uint8)
        M[Upos] = g.integers(0, 2, size=Upos.size).astype(np.uint8)
        M = M.reshape(17, 172)
        c = int(g.integers(0, 2))
        n += 1
        E = M.copy()
        E[16, :] = 0
        E[16, COL[1 << 0]] = 1
        E[16, COL[1 << 9]] = 1
        E[16, COL[0]] = c
        hx = to_hex(E)
        h = hashlib.sha256(json.dumps(hx).encode()).hexdigest()
        rec = {"draw": n, "c": c, "E_sha256": h}
        if h in seen:
            rec.update({"s": None, "status": "rejected_duplicate"})
        else:
            seen.add(h)
            s = count_solutions(E)
            rec["s"] = s
            if s == 0:
                rec["status"] = "kept"
                rec["kept_index"] = len(kept) + 1
                kept.append({"label": f"N-ELL-{len(kept) + 1:02d}", "draw": n, "c": c, "E_hex": hx, "E_sha256": h})
            else:
                rec["status"] = "rejected_satisfiable"
        draws.append(rec)
    out = {"task": "TASK-20260924-d95e70", "object": "O2 N-ELL", "seed": SEED, "numpy": np.__version__,
           "declaration": "o2-declaration.yaml", "checks": checks, "draws_total": n,
           "kept": len(kept), "rejected": sum(1 for d in draws if d["status"] != "kept"),
           "s_histogram_all_draws": {str(k): sum(1 for d in draws if d["s"] == k) for k in sorted({d["s"] for d in draws if d["s"] is not None})}}
    with open(os.path.join(HERE, "n-ell-generation-log.jsonl"), "w") as f:
        for d in draws:
            f.write(json.dumps(d) + "\n")
    json.dump({"summary": out, "instances": kept}, open(os.path.join(HERE, "n-ell-instances.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
