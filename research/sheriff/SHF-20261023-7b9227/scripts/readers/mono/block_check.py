"""Block-system check at m = 5 on the symmetric base (distinguishes the claimed module F_2^4/D,
blocks of size 4 = parity classes of the number of minus signs, from the dual module with blocks
of size 2, which has the SAME cycle-type distribution -- TransitiveGroup(8,39) vs (8,41)).

Derivation: the two blocks are swapped by (v, sigma) in G_5 iff the translation part v has odd
weight.  For an F_p-fibre (x_1..x_4 roots of g), Frobenius acts on P_i by P_i -> chi_i P_{sigma(i)}
(with chi over the field where the point lives); the product of all four signs equals
chi_p(prod_i f(x_i)) = chi_p(Res(g, f)) up to the sign convention, a quantity in F_p.  So:
   s := chi_p( prod_i f(x_i) ) = +1  =>  Frobenius preserves the two blocks,
   s = -1                           =>  Frobenius swaps them.
Prediction from the group model: joint distribution of (cycle type on roots, swap flag).
Observed: joint distribution of (cycle type of F over F_p, s).  Compared by chi-square and by
checking that no observed pair is impossible under the model.  Also compared with the dual
model (blocks of size 2 -- there the swap flag is NOT determined by the weight parity of v in
the same way; we only report whether observed (cycle type, s) pairs are compatible with the
size-4 block structure: s = -1 must have no fixed points and only even cycles).
Usage: sage -python block_check.py OUTDIR
"""
import sys, json, itertools, collections, os
from sage.all import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mono_lib import S3_expr, symbolic_S, symmetric_base_group

set_random_seed(20261023)
OUT = sys.argv[1]
m = 5; n = 4
G, nV, perms = symmetric_base_group(m)
reps = [eps for eps in itertools.product([1, -1], repeat=n) if eps[0] == 1]
parity = {i + 1: (sum(1 for e in eps if e == -1) % 2) for i, eps in enumerate(reps)}
# model joint distribution (cycle type on V, swap flag)
model = collections.Counter()
for g in G:
    tup = g.tuple()
    seen = set(); ct = []
    for s0 in range(1, nV + 1):
        if s0 in seen: continue
        l = 0; x = s0
        while x not in seen:
            seen.add(x); x = tup[x - 1]; l += 1
        ct.append(l)
    swap = (parity[tup[0]] != parity[1])
    model[(tuple(sorted(ct)), swap)] += 1
order = sum(model.values())
print('model (cycle type, swap):', dict(model))

results = {}
for (p, a, b) in [(1009, 5, 7), (10007, 2, 3)]:
    F = GF(p)
    R4, S4sym = symbolic_S(4, F(a), F(b), F)
    PX = PolynomialRing(F, 'x'); x = PX.gen()
    fpoly = x ** 3 + F(a) * x + F(b)
    obs = collections.Counter(); N = 1500 if p < 5000 else 600; Kc = {}
    for _ in range(N):
        g = x ** 4 + sum(F.random_element() * x ** i for i in range(4))
        if not g.is_squarefree(): continue
        degs = [int(h.degree()) for h, e in g.factor()]
        k = lcm(degs); K = Kc.setdefault(k, GF(p ** k, 'w') if k > 1 else F)
        roots = [r for r, e in g.change_ring(K).roots()]
        prodf = prod(r ** 3 + K(a) * r + K(b) for r in roots)
        if prodf == 0: continue
        prodf = F(prodf)   # symmetric in the roots => in F_p
        s = -1 if not prodf.is_square() else 1
        PT = PolynomialRing(K, 'T'); T = PT.gen(); PTX = PolynomialRing(PT, 'X'); X = PTX.gen()
        A = PTX(S3_expr(K(a), K(b), roots[0], roots[1], X))
        B4 = S4sym(roots[2], roots[3], T, X, 0)
        Fq = A.resultant(PTX(B4))
        Fq = PolynomialRing(F, 'T')([F(c) for c in Fq.list()])
        if Fq.degree() != 8 or gcd(Fq, Fq.derivative()).degree() != 0: continue
        ct = tuple(sorted(int(h.degree()) for h, e in Fq.factor() for _ in range(e)))
        obs[(ct, s == -1)] += 1
    tot = sum(obs.values())
    chi2 = 0.0; impossible = {}
    for key in set(obs) | set(model):
        o = obs.get(key, 0); pk = model.get(key, 0) / order
        if pk == 0:
            if o: impossible[str(key)] = o
            continue
        chi2 += (o - pk * tot) ** 2 / (pk * tot)
    # compatibility with size-4 blocks when swapping: no fixed points, even cycles only
    bad_swap = sum(v for (ct, sw), v in obs.items() if sw and (1 in ct or any(l % 2 for l in ct)))
    results['%d,%d,%d' % (p, a, b)] = {'n': tot, 'observed': {str(k): v for k, v in sorted(obs.items())},
                                       'chi2': float(int(float(chi2) * 10)) / 10.0, 'dof': int(len(model) - 1),
                                       'impossible_pairs_observed': impossible, 'swap_pairs_incompatible_with_size4_blocks': bad_swap}
    print((p, a, b), results['%d,%d,%d' % (p, a, b)])
json.dump({'model': {str(k): int(v) for k, v in model.items()}, 'order': int(order), 'results': results},
          open(os.path.join(OUT, 'block_check.json'), 'w'), indent=1)
