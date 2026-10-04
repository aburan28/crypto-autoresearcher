"""Exact count of targets xR in F_{2^n} that admit an S_4 decomposition with
x1, x2, x3 in V, separately on E(F_{2^n}) and on the twist coset (points of
E over F_{2^{2n}} with x in F_{2^n} and Frobenius acting as -1). The twist
coset is isomorphic, x-preservingly, to E'(F_{2^n}) for the quadratic twist
E': y^2 + xy = x^3 + (1 + 1) x^2 + 1 = x^3 + 1 (delta = 1, Tr(1) = 1 for odd
n; the isomorphism (x, y) -> (x, y + s x), s^2 + s = 1, fixes x), so both
counts are base-field computations. Validator's own arithmetic.
usage: python3 v1_target_fractions.py n15l5|n17l6|n19l6"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from val_gf2n import GF2n, BinaryCurve
sys.argv = sys.argv[:2]
cell = sys.argv[1]
n, l = (int(t) for t in re.match(r"n(\d+)l(\d+)", cell).groups())
BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
HERE = os.path.dirname(os.path.abspath(__file__))
info = open(os.path.join(BENCH, f"INFO{cell}-1-S.dimacs")).read().split("\n")

class GF2nTable(GF2n):
    def __init__(self, n, mod):
        N = (1 << n) - 1
        exp = [0] * N; log = [-1] * (1 << n); g = 1
        for i in range(N):
            exp[i] = g; log[g] = i; g <<= 1
            if (g >> n) & 1: g ^= mod
        assert g == 1 and all(v >= 0 for v in log[1:])
        self.exp, self.log, self.N = exp, log, N
        super().__init__(n, mod)
    def mul(self, x, y):
        if x == 0 or y == 0: return 0
        return self.exp[(self.log[x] + self.log[y]) % self.N]
    def inv(self, x):
        return self.exp[(-self.log[x]) % self.N]
    def sq(self, x):
        return 0 if x == 0 else self.exp[(2 * self.log[x]) % self.N]

F = GF2nTable.from_info_modulus(n, info[1])
E = BinaryCurve(F, a2=1, a6=1)      # the shipped curve
Et = BinaryCurve(F, a2=0, a6=1)     # its quadratic twist (delta = 1)

def add_fast(C, P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if y1 ^ y2 == x1: return None
        lam = x1 ^ F.mul(y1, F.inv(x1))
        x3 = F.sq(lam) ^ lam ^ C.a2
        return (x3, F.sq(x1) ^ F.mul(lam ^ 1, x3))
    lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
    x3 = F.sq(lam) ^ lam ^ x1 ^ x2 ^ C.a2
    return (x3, F.mul(lam, x1 ^ x3) ^ x3 ^ y1)

out = {"cell": cell, "n": n, "l": l}
t0 = time.time()
for name, C in (("E", E), ("twist", Et)):
    S = []
    for xv in range(1 << l):
        for y in C.ys(xv):
            S.append((xv, y))
    for P in S:
        assert C.on_curve(P)
    pairs = set()
    for i in range(len(S)):
        for j in range(i, len(S)):
            Q = add_fast(C, S[i], S[j])
            pairs.add(Q)
    targets = set()
    for Q in pairs:
        for P3 in S:
            R = add_fast(C, Q, P3)
            if R is not None:
                targets.add(R[0])
    # x-coordinates of E(F_2^n) resp. twist points (candidates for a random target of that kind)
    out[name] = {"points_with_x_in_V": len(S), "distinct_pair_sums": len(pairs),
                 "decomposable_targets_xR": len(targets),
                 "fraction_of_all_2^n_field_elements": len(targets) / (1 << n)}
out["either_kind_fraction"] = (out["E"]["decomposable_targets_xR"] + out["twist"]["decomposable_targets_xR"]) / (1 << n)
out["seconds"] = round(time.time() - t0, 2)
json.dump(out, open(os.path.join(HERE, f"v1_target_fractions_{cell}.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
