# Scope control for crypto:research/conductor_gap_cm_pairs_20261010/lean/GenericInvariance.lean
# Witness for Hom hypotheses (inj, map_mul, map_inv) and a demonstration that a representation-hashing
# r-adding rho (as ecbench's rho/kangaroo: jump index = hash(key(x)), ic_boundary.rs:1926-1928,
# generic.rs:275-278) is NOT transcript-invariant under an isomorphism, while BSGS (equality only) is.
import random
p = 1019; q = 2*p + 1          # q = 2039 prime, QR subgroup of F_q^* has order p
assert all(q % d for d in range(2, int(q**0.5)+1))
G1 = dict(mul=lambda a,b:(a+b)%p, inv=lambda a:(-a)%p, one=0, key=lambda a:a)
G2 = dict(mul=lambda a,b:(a*b)%q, inv=lambda a:pow(a,-1,q), one=1, key=lambda a:a)
gen2 = 4
phi = lambda x: pow(gen2, x, q)
# Hom witness: injective, preserves mul and inv
img = [phi(x) for x in range(p)]
print("phi injective:", len(set(img)) == p,
      "| map_mul:", all(phi((a+b)%p) == (phi(a)*phi(b))%q for a in range(0,p,7) for b in range(0,p,11)),
      "| map_inv:", all(phi((-a)%p) == pow(phi(a),-1,q) for a in range(p)))
def bsgs(G, g, h):
    m = int(p**0.5)+1; ops = 0; baby = []; x = G["one"]
    for j in range(m): baby.append(x); x = G["mul"](x, g); ops += 1
    gm_inv = G["inv"](x); ops += 1; y = h
    for i in range(m+1):
        for j, bj in enumerate(baby):          # equality queries only (free in the Lean model)
            if bj == y: return ops, (i*m + j) % p
        y = G["mul"](y, gm_inv); ops += 1
    return ops, None
def powG(G, g, k):
    r = G["one"]
    for _ in range(k): r = G["mul"](r, g)
    return r
def rho(G, g, h, tape_seed, r=16):
    rnd = random.Random(tape_seed)
    J = [(rnd.randrange(p), rnd.randrange(p)) for _ in range(r)]
    Jel = [G["mul"](powG(G, g, a), powG(G, h, b)) for a, b in J]
    a0, b0 = rnd.randrange(p), rnd.randrange(p)
    x = G["mul"](powG(G, g, a0), powG(G, h, b0)); a, b = a0, b0
    seen = {}; ops = 0
    while ops < 20*p:
        k = G["key"](x)
        if k in seen:
            a2, b2 = seen[k]
            if (b2 - b) % p: return ops, ((a - a2) * pow(b2 - b, -1, p)) % p
            return ops, None
        seen[k] = (a, b)
        j = (k * 2654435761 >> 7) % r       # representation-dependent jump choice
        x = G["mul"](x, Jel[j]); a = (a + J[j][0]) % p; b = (b + J[j][1]) % p; ops += 1
    return ops, None
random.seed(3); diff_rho = diff_bsgs = 0; N = 200
for t in range(N):
    g1 = random.randrange(1, p); d = random.randrange(p); h1 = (g1*d) % p
    g2, h2 = phi(g1), phi(h1)
    cb1, ab1 = bsgs(G1, g1, h1); cb2, ab2 = bsgs(G2, g2, h2)
    cr1, ar1 = rho(G1, g1, h1, t); cr2, ar2 = rho(G2, g2, h2, t)
    diff_bsgs += (cb1, ab1) != (cb2, ab2); diff_rho += cr1 != cr2
print(f"BSGS (equality-only): transcripts differing on transported instances: {diff_bsgs}/{N}")
print(f"hash-partition rho, same tape: cost differs on transported instances: {diff_rho}/{N}")
