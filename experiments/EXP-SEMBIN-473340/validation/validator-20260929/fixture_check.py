"""Independent-kernel (vbr.py) check of the gate fixtures cited by
DEC-20260929-0d6685 definitional_finding (validator, after the blind phase).
System: (n,n')=(6,3), basis [1,2,4], x_R = a_real_xR(6,1,1,Random(603)) from
ffd_semaev_core_v1; generators greedily reduced to an independent subset in
build order (own code); M rows select generator XOR-combinations (own code)."""
import sys, os, random, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(1, os.path.normpath(os.path.join(HERE, "..", "..", "src")))
from ffd_semaev_core_v1 import build_system, a_real_xR
import vbr
xR = a_real_xR(6, 1, 1, random.Random(603))
base = build_system(6, 3, 1, xR, [1, 2, 4])
basis = {}; sem = []
for f in base:
    r = vbr.tobits(f); r0 = r
    while r:
        h = r.bit_length(); b = basis.get(h)
        if b is None: basis[h] = r; sem.append(f); break
        r ^= b
def recombine(M):
    out = []
    for row in M:
        acc = frozenset()
        for j in range(len(sem)):
            if (row >> j) & 1: acc = acc ^ sem[j]
        out.append(acc)
    return out
res = dict(xR=xR, n_base=len(base), n_indep=len(sem))
for M in ([1,2,4,8,16], [1,2,4,8,26], [1,2,4,13,26]):
    W = recombine(M)
    res[str(M)] = {c: vbr.dff(vbr.profile(W, 6, 6, c)) for c in ("reduced", "formal", "legacy")}
W = recombine([1,2,4,8,26]); pf = vbr.profile(W, 6, 3, "formal")
res["witness_formal_falls2_dimV1"] = [pf[2][1], pf[1][0]]
res["witness_degrees"] = [vbr.pdeg(f) for f in W]
print(json.dumps(res))
json.dump(res, open(os.path.join(HERE, "fixture_check.json"), "w"), indent=1)
