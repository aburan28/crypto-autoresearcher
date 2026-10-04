"""Exhaustive decomposition search over F_{2^{2n}} for every shipped instance
of one cell (validator's own arithmetic; beyond the plan's V1 step list, used
for the (a)-(d) classification and as an independent check on the 29 UNSAT
solver answers on U-labelled instances).

For instance (n, l, xR): S = all points of E over F_{2^{2n}} whose x lies in
V = span(1, a, ..., a^{l-1}) (2 per nonzero x, 1 for x = 0). A decomposition
is {x1, x2, x3} in V with some choice of points P_i over (x_i) and a point R
over xR such that P1 + P2 + P3 = R; equivalently S_4(x1, x2, x3, xR) = 0.
Search: D = {x(P1 + P2)} over unordered pairs of S (with repetition), then
for each P3 in S look up x(R - P3). Both signs of R are covered because -P3
is also in S. Complete: every decomposition over the algebraic closure of
x-coordinates in F_{2^n} has its points in E(F_{2^{2n}}).

usage: python3 v1_decomp_search.py n15l5 | n17l6 | n19l6
"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from val_gf2n import GF2n, BinaryCurve, decode_le, summation_poly_f3, GF2n_ext2, BinaryCurveExt2

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
HERE = os.path.dirname(os.path.abspath(__file__))
cell = sys.argv[1]
n, l = (int(t) for t in re.match(r"n(\d+)l(\d+)", cell).groups())


class GF2nTable(GF2n):
    """Same field, multiplication and inversion through log/exp tables."""
    def __init__(self, n, mod):
        N = (1 << n) - 1
        exp = [0] * N
        log = [-1] * (1 << n)
        g = 1
        for i in range(N):
            exp[i] = g
            log[g] = i
            g <<= 1
            if (g >> n) & 1:
                g ^= mod
        assert g == 1 and all(v >= 0 for v in log[1:])
        self.exp, self.log, self.N = exp, log, N
        super().__init__(n, mod)

    def mul(self, x, y):
        if x == 0 or y == 0:
            return 0
        return self.exp[(self.log[x] + self.log[y]) % self.N]

    def inv(self, x):
        assert x != 0
        return self.exp[(-self.log[x]) % self.N]

    def sq(self, x):
        if x == 0:
            return 0
        return self.exp[(2 * self.log[x]) % self.N]


names = []
for f in sorted(os.listdir(BENCH)):
    m = re.match(rf"INFO({cell}-(\d+)-[SU])\.dimacs$", f)
    if m:
        names.append((int(m.group(2)), m.group(1)))
names = [nm for _, nm in sorted(names)]
assert len(names) == 20

info0 = open(os.path.join(BENCH, f"INFO{names[0]}.dimacs")).read().split("\n")
F = GF2nTable.from_info_modulus(n, info0[1])
# cross-check table arithmetic against the shift-and-add arithmetic
F0 = GF2n(n, F.mod)
import random
rng = random.Random(3)
for _ in range(2000):
    x, y = rng.getrandbits(n), rng.getrandbits(n)
    assert F.mul(x, y) == F0.mul(x, y)
    if x:
        assert F.inv(x) == F0.inv(x)
E = BinaryCurve(F, a2=1, a6=1)
K = GF2n_ext2(F)
EK = BinaryCurveExt2(K, a2=1, a6=1)


def ext_add_fast(P, Q):
    """EK.add without the per-step on-curve assertion (bulk loop)."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    a2 = EK.a2
    if x1 == x2:
        if K.add(y1, y2) == x1:
            return None
        lam = K.add(x1, K.mul(y1, K.inv(x1)))
        x3 = K.add(K.add(K.mul(lam, lam), lam), a2)
        y3 = K.add(K.mul(x1, x1), K.mul(K.add(lam, (1, 0)), x3))
    else:
        lam = K.mul(K.add(y1, y2), K.inv(K.add(x1, x2)))
        x3 = K.add(K.add(K.add(K.add(K.mul(lam, lam), lam), x1), x2), a2)
        y3 = K.add(K.add(K.mul(lam, K.add(x1, x3)), x3), y1)
    return (x3, y3)


# all points over F_{2^{2n}} with x in V
S = []
for xv in range(1 << l):
    if xv == 0:
        S.append(((0, 0), (1, 0)))  # (0, 1): y^2 = 1
    else:
        for y in EK.ys_for_base_x(xv):
            S.append(((xv, 0), y))
for P in S:
    assert EK.on_curve(P)
assert len(S) == 2 * (1 << l) - 1

t0 = time.time()
D = {}  # x(P1+P2) -> list of (x1, x2)
for i in range(len(S)):
    for j in range(i, len(S)):
        Q = ext_add_fast(S[i], S[j])
        key = None if Q is None else Q[0]
        D.setdefault(key, set()).add((S[i][0][0], S[j][0][0]))
t_pairs = time.time() - t0


def kind(xs):
    crit = [E.x_criterion(x) for x in xs]
    if all(c == 0 or c is None for c in crit):
        return "E"          # every point in E(F_2^n) (x = 0 is the rational 2-torsion point)
    if all(c == 1 for c in crit):
        return "twist"      # every point in E(F_2^2n) \ E(F_2^n)
    return "mixed"


out = []
for nm in names:
    lines = open(os.path.join(BENCH, f"INFO{nm}.dimacs")).read().split("\n")
    assert lines[1].strip() == info0[1].strip()
    xR = decode_le(lines[2])
    label = lines[3].strip()
    if xR == 0:
        Rs = [((0, 0), (1, 0))]
    else:
        Rs = [((xR, 0), y) for y in EK.ys_for_base_x(xR)]
    R = Rs[0]
    found = set()
    for P3 in S:
        Q = ext_add_fast(R, EK.neg(P3))
        key = None if Q is None else Q[0]
        for (x1, x2) in D.get(key, ()):
            found.add(tuple(sorted((x1, x2, P3[0][0]))))
    # every found triple must be a root of f3, and verify one explicit sum
    decs = []
    for tr in sorted(found):
        f3 = summation_poly_f3(F, tr[0], tr[1], tr[2], xR)
        assert f3 == 0, (nm, tr, hex(f3))
        decs.append({"x_hex": [hex(x) for x in tr], "kind": kind(list(tr) + [xR])})
    row = {"instance": nm, "label": label, "xR_hex": hex(xR), "xR_kind": ("E" if E.x_criterion(xR) in (0, None) else "twist"),
           "n_decompositions_unordered_x_triples": len(found),
           "kinds": {k: sum(1 for d in decs if d["kind"] == k) for k in ("E", "twist", "mixed")},
           "decompositions": decs}
    if label == "S":
        cert = tuple(sorted(decode_le(s) for s in lines[4].strip().split("-")))
        row["shipped_certificate_x_hex"] = [hex(x) for x in cert]
        row["shipped_certificate_found_by_search"] = cert in found
    out.append(row)
    print(nm, label, row["xR_kind"], len(found), row["kinds"], row.get("shipped_certificate_found_by_search", ""))

summary = {"cell": cell, "n": n, "l": l, "modulus": F.modulus_str(), "points_with_x_in_V_over_F_2^2n": len(S),
           "pair_table_seconds": round(t_pairs, 2), "total_seconds": round(time.time() - t0, 2),
           "S_instances_with_at_least_one_decomposition": sum(1 for r in out if r["label"] == "S" and r["n_decompositions_unordered_x_triples"] > 0),
           "S_instances_whose_shipped_certificate_was_found": sum(1 for r in out if r.get("shipped_certificate_found_by_search")),
           "U_instances_with_a_decomposition": [r["instance"] for r in out if r["label"] == "U" and r["n_decompositions_unordered_x_triples"] > 0],
           "U_instances_with_none": sum(1 for r in out if r["label"] == "U" and r["n_decompositions_unordered_x_triples"] == 0),
           "rows": out}
json.dump(summary, open(os.path.join(HERE, f"v1_decomp_search_{cell}.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=1))
