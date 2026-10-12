"""Exhaustive check of the halving criterion used to type N-CONVL targets (TASK-20260926-c58e87).
Recalled lemma (pointer, not support): for an ordinary binary curve y^2 + xy = x^3 + a x^2 + b,
a point P != O lies in 2E(F_{2^n}) iff Tr(x(P)) = Tr(a). Checked here exhaustively, per curve,
without the lemma: x(2P) = x^2 + b/x^2 for x(P) = x != 0 (and 2P = O for x = 0), so
X2 = {x^2 + b/x^2 : x != 0 an abscissa of E} is exactly the set of abscissae of 2E minus O.
The script compares X2 with T = {x an abscissa of E : Tr(x) = Tr(a)}.
Curves: the archived curve (A, B) and the curves (A, b') of N-CONVL:0:unsat and N-CONVL:2:unsat
(b' read off the constant column of their archived E_hex).
Usage: python3 halving_check.py <worktree> <out.json>
"""
import gzip
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 2)[0] + "/j10-ptm")
import rtlib as R  # noqa: E402

wt, out = sys.argv[1], sys.argv[2]
run = f"{wt}/experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
INS = {json.loads(l)["key"]: json.loads(l) for l in gzip.open(f"{run}/instances.jsonl.gz", "rt")}
N = R.N
trmask = sum(R.gtr(1 << i) << i for i in range(N))


def tr(x):
    return bin(x & trmask).count("1") & 1


def check(a, b):
    tra = tr(a)
    absc = []
    for x in range(1, 1 << N):
        ix = R.ginv(x)
        ix2 = R.gsq(ix)
        if tr(x ^ a ^ R.gmul(b, ix2)) == 0:
            absc.append((x, ix2))
    on0 = True  # x = 0 is always an abscissa: (0, sqrt(b))
    nE = 2 * len(absc) + 2  # 2 points per nonzero abscissa, plus (0, sqrt b) and O
    X2 = set()
    for x, ix2 in absc:
        X2.add(R.gsq(x) ^ R.gmul(b, ix2))
    T = {x for x, _ in absc if tr(x) == tra}
    if tra == 0:
        T.add(0)
    return {"a": a, "b": b, "Tr_a": tra, "#E": nE, "abscissae_nonzero": len(absc),
            "X2_eq_T": X2 == T, "|X2|": len(X2), "|T|": len(T),
            "2E_size_from_X2": 1 + (2 * len(X2 - {0}) + (1 if 0 in X2 else 0))}


keys = ["N-CONVL:0:unsat", "N-CONVL:2:unsat"]
curves = [("archived", R.B_CURVE)]
for k in keys:
    E = R.hex_to_E(INS[k]["E_hex"])
    curves.append((k, sum(int(E[kk, 0]) << kk for kk in range(17))))
res = {}
for name, b in curves:
    res[name] = check(R.A_CURVE, b)
    print(name, res[name], flush=True)
json.dump(res, open(out, "w"), indent=1)
