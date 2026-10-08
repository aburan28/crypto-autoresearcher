"""Exhaustive search, per volcano level, for endomorphisms whose degree is smooth (all primes <= 43,
norm <= 2^44), i.e. those that could be evaluated cheaply as a chain of small isogenies. For each,
the order k of its eigenvalue on <P> is the equivalence-class size it would give rho. Cost model (stated,
not measured): one affine add ~ 45 field mults (inversion ~ 42); a p-isogeny step ~ p/2 + 2 mults;
a Frobenius/Verschiebung 2-step ~ 2 mults. Net rho speedup S = sqrt(K/2) c_add / (c_add + (K/2-1) c_alpha) relative to negation-only rho, K = |<-1, alpha>| on <P>,
since the canonical representative needs the whole orbit each step."""
import math, json, itertools
L = 549756390943; LAM = 256851699273; MU = (-LAM) % L
FAC = [2, 3, 11, 41, 67720669]
def mul(a, b): return (a[0]*b[0] - 2*a[1]*b[1], a[0]*b[1] + a[1]*b[0] + a[1]*b[1])
def nrm(a): return a[0]*a[0] + a[0]*a[1] + 2*a[1]*a[1]
def order(z):
    z %= L
    if z == 0: return None
    k = L - 1
    for p in FAC:
        while k % p == 0 and pow(z, k // p, L) == 1: k //= p
    return k
# primes of O_K above small rational primes (norm p), found by search
gens = {}
for p in [2, 7, 11, 23, 29, 37, 43]:
    sols = [(x, y) for x in range(-20, 21) for y in range(1, 21) if nrm((x, y)) == p]
    a = sols[0]; ab = (a[0] + a[1], -a[1])  # conjugate: x + y wbar, wbar = 1 - w
    gens[p] = [a] if nrm(mul(a, a)) == p * p and p == 7 else [a, ab]
gens[7] = [gens[7][0]]  # ramified: one prime
COSTADD = 45.0
def cost(exps):
    c = 0.0
    for (p, _), e in exps.items(): c += e * (2.0 if p == 2 else p / 2 + 2)
    return c
LOGB = 44
plist = [(p, i) for p in gens for i in range(len(gens[p]))]
maxe = {pi: int(LOGB / math.log2(pi[0])) for pi in plist}
best = {}
LEV = {"crater": 1, "floor409": 409, "floor1721": 1721, "bottom": 703889}
for lev in LEV: best[lev] = dict(best_S=0.0, best=None, smallest_k=None, smallest_k_alpha=None, n_candidates=0)
def rec(idx, elt, lognorm, exps):
    if idx == len(plist):
        if elt[1] == 0: return  # integer: scalar multiplication, no class structure beyond itself
        for lev, f in LEV.items():
            if elt[1] % f: continue
            for sgn in (1, -1):
                lam = sgn * (elt[0] + elt[1] * MU) % L
                k = order(lam)
                if not k or lam in (1, L - 1): continue  # +-1: already the negation map
                K = k if k % 2 == 0 and pow(lam, k // 2, L) == L - 1 else 2 * k  # |<-1, lam>|
                b = best[lev]; b["n_candidates"] += 1
                c = cost(exps); h = K // 2  # classes shrink by K/2 relative to the negation-only baseline
                S = math.sqrt(h) * COSTADD / (COSTADD + (h - 1) * c)
                if S > b["best_S"]: b.update(best_S=S, best=dict(alpha=elt, sign=sgn, norm=nrm(elt), k=k, K=K, cost_mults=c))
                if b["smallest_k"] is None or k < b["smallest_k"]: b.update(smallest_k=k, smallest_k_alpha=dict(alpha=elt, norm=nrm(elt)))
        return
    pi = plist[idx]; g = gens[pi[0]][pi[1]]; e = 0; cur = elt
    while lognorm + e * math.log2(pi[0]) <= LOGB:
        ex = dict(exps); ex[pi] = e
        rec(idx + 1, cur, lognorm + e * math.log2(pi[0]), ex)
        cur = mul(cur, g); e += 1
rec(0, (1, 0), 0.0, {})
json.dump(best, open("smooth_endos.json", "w"), indent=1, default=str)
for lev, b in best.items():
    print(lev, "candidates:", b["n_candidates"], " smallest orbit k:", b["smallest_k"], b["smallest_k_alpha"],
          " best modelled net speedup S:", round(b["best_S"], 4), b["best"])
