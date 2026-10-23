from sage.all import pari, factor, is_square, isqrt
# P4 blind re-derivation.
# (1) Prime counts up to 5000 by an own sieve.
# (2) CM-73 sweep over every prime p = 1 (mod 6), 7 <= p <= 5000, for the curve family
#     C_p : y^2 = (x^3 + g)(x^3 + g^2) = x^6 + (g + g^2) x^3 + g^3, g a primitive root mod p
#     (family as stated in the paper; g = PARI znprimroot, and separately the least primitive
#     root computed here). Frobenius char poly T^4 - s1 T^3 + s2 T^2 - p s1 T + p^2 from PARI
#     hyperellcharpoly; "CM-73" := s2 - 2p = -73 (paper: a_2 - 2p = -73).
# (3) Independent cross-check of (s1, s2) by direct point counts over F_p and F_{p^2}
#     (own numpy arithmetic in F_p[s]/(s^2 - nr)) for all p <= 1000 and the 11 norm-form primes.
import numpy as np

def sieve(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i*i::i] = bytearray(len(s[i*i::i]))
    return [i for i in range(n + 1) if s[i]]

P = sieve(5000)
p16 = [p for p in P if p % 6 == 1]
p56 = [p for p in P if p % 6 == 5]
print(f"primes <= 5000: {len(P)};  p = 1 mod 6: {len(p16)} (first {p16[0]}, last {p16[-1]});  p = 5 mod 6: {len(p56)};  2,3: 2")

def least_primroot(p):
    fac = [q for q, _ in factor(p - 1)]
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in fac):
            return g

def charpoly_pari(p, g):
    c = (g + g * g) % p; d = pow(g, 3, p)
    f = pari(f"Mod(1,{p})*x^6 + Mod({c},{p})*x^3 + Mod({d},{p})")
    cp = pari.hyperellcharpoly(f)
    co = [int(cp.polcoef(i)) for i in range(5)]  # T^0..T^4
    assert co[4] == 1 and co[0] == p * p
    s1 = -co[3]; s2 = co[2]
    assert co[1] == -p * s1
    return s1, s2

def counts_numpy(p, g):
    c = (g + g * g) % p; d = pow(g, 3, p)
    x = np.arange(p, dtype=np.int64)
    sq = np.zeros(p, dtype=np.int64); sq[(x * x) % p] = 1
    chi = np.where(sq == 1, 1, -1); chi[0] = 0
    fx = ((pow_np(x, 3, p) * (pow_np(x, 3, p) + c)) % p + d) % p
    N1 = int(np.sum(1 + chi[fx])) + 2           # leading coeff 1 is a square: 2 points at infinity
    nr = next(a for a in range(2, p) if pow(a, (p - 1) // 2, p) == p - 1)
    A, B = np.meshgrid(x, x, indexing="ij"); A = A.ravel(); B = B.ravel()   # z = A + B s, s^2 = nr
    def mul(a1, b1, a2, b2):
        return (a1 * a2 + nr * (b1 * b2 % p)) % p, (a1 * b2 + b1 * a2) % p
    z2 = mul(A, B, A, B); z3 = mul(z2[0], z2[1], A, B); z6 = mul(z3[0], z3[1], z3[0], z3[1])
    fa = (z6[0] + c * z3[0] + d) % p; fb = (z6[1] + c * z3[1]) % p
    norm = (fa * fa - nr * (fb * fb % p)) % p
    N2 = int(np.sum(1 + chi[norm])) + 2
    s1 = p + 1 - N1
    s2 = (s1 * s1 - (p * p + 1 - N2)) // 2
    return s1, s2

def pow_np(x, e, p):
    r = np.ones_like(x)
    for _ in range(e):
        r = (r * x) % p
    return r

nf = []
cm73_pari = []; cm73_least = []
mismatch_numpy = []
checked_numpy = 0
g_differs = []
for p in p16:
    g = int(pari(f"lift(znprimroot({p}))"))
    gl = least_primroot(p)
    if g != gl:
        g_differs.append((p, g, gl))
    s1, s2 = charpoly_pari(p, g)
    if s2 - 2 * p == -73:
        cm73_pari.append((p, s1, s2))
    if gl != g:
        t1, t2 = charpoly_pari(p, gl)
        if t2 - 2 * p == -73:
            cm73_least.append((p, t1, t2))
    elif s2 - 2 * p == -73:
        cm73_least.append((p, s1, s2))
    rem = 4 * p - 73
    is_nf = rem > 0 and rem % 3 == 0 and is_square(rem // 3)
    if is_nf:
        nf.append((p, isqrt(rem // 3), s2 - 2 * p))
    if p <= 1000 or is_nf:
        checked_numpy += 1
        if counts_numpy(p, g) != (s1, s2):
            mismatch_numpy.append(p)

print(f"processed {len(p16)} primes p = 1 mod 6 in [7, 5000]")
print(f"znprimroot != least primitive root at: {g_differs if g_differs else 'none'}")
print(f"CM-73 (s2 - 2p = -73), g = znprimroot: {cm73_pari}")
print(f"CM-73 (s2 - 2p = -73), g = least primitive root: {cm73_least}")
print(f"norm-form primes 4p = 73 + 3k^2 (p, k, s2-2p): {nf}  count={len(nf)}")
print(f"numpy F_p/F_p^2 cross-check of (s1, s2): {checked_numpy} primes, mismatches {mismatch_numpy}")
