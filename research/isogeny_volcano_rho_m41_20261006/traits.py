"""Arithmetic traits of each level / curve that bear on rho. Pure integer math, no sampling."""
import math, json
L = 549756390943
LAM = 256851699273            # eigenvalue of tau on <P> (lambda^41 = 1 mod L)
MU = (-LAM) % L           # eigenvalue of w = (1+sqrt(-7))/2 = -tau
MOD = (1 << 41) | 0x9

def gmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 41: a ^= MOD
    return r

def ghs_magic(b):
    """m(b) = dim_F2 span{(1, sigma^i(b))}; GHS descent genus is 2^(m-1) or 2^(m-1)-1."""
    vecs, z = [], b
    for _ in range(41):
        vecs.append((1 << 41) | z); z = gmul(z, z)
    rank, rows = 0, []
    for v in vecs:
        for r in rows: v = min(v, v ^ r)
        if v: rows.append(v); rank += 1
    return rank

def norm(x, y, f):  # N(x + y f w), w^2 = w - 2
    return x * x + x * y * f + 2 * f * f * y * y

def min_endo_degree(f):
    """smallest degree of a non-integer endomorphism in O_f = Z[f w]"""
    return min(norm(x, 1, f) for x in range(-f - 2, 3))

def min_degree_for_root(f, zeta):
    """min N(alpha), alpha in O_f, alpha acting on <P> as zeta: alpha = x + y f w, x + y f MU = zeta (mod L).
    Gauss-reduce the lattice {(x,y): x + y f MU = 0 mod L} under the norm form, then search near the target."""
    fm = f * MU % L
    B = [(L, 0), ((-fm) % L, 1)]
    q = lambda v: norm(v[0], v[1], f)
    def bil(u, v): return (q((u[0]+v[0], u[1]+v[1])) - q(u) - q(v)) / 2
    while True:  # Lagrange-Gauss reduction
        if q(B[0]) > q(B[1]): B = [B[1], B[0]]
        mu = round(bil(B[0], B[1]) / q(B[0]))
        if mu == 0: break
        B[1] = (B[1][0] - mu * B[0][0], B[1][1] - mu * B[0][1])
    t0 = (zeta % L, 0)  # one solution; search t0 + i B0 + j B1 near the origin
    # Babai: solve coordinates in R^2 with the standard embedding x + y f w -> complex
    def emb(v): return complex(v[0] + v[1] * f * 0.5, v[1] * f * math.sqrt(7) / 2)
    e0, e1, et = emb(B[0]), emb(B[1]), emb(t0)
    det = e0.real * e1.imag - e0.imag * e1.real
    c0 = (-et.real * e1.imag + et.imag * e1.real) / det
    c1 = (-e0.real * et.imag + e0.imag * et.real) / det
    best = None
    for i in range(round(c0) - 3, round(c0) + 4):
        for j in range(round(c1) - 3, round(c1) + 4):
            v = (t0[0] + i * B[0][0] + j * B[1][0], i * B[0][1] + j * B[1][1] + t0[1])
            if v[1] == 0 and v[0] in (-1, 0, 1): continue
            n = q(v); best = n if best is None or n < best else best
    return best

def prim_roots(k):
    g = 5  # find a generator of (Z/L)^*
    fac = [2, 3, 11, 41, 67720669]
    while any(pow(g, (L - 1) // p, L) == 1 for p in fac): g += 1
    h = pow(g, (L - 1) // k, L)
    return [pow(h, e, L) for e in range(1, k) if math.gcd(e, k) == 1] if k > 1 else [1]

def tau_power_in_order(f):
    """smallest k >= 1 with tau^k in Z + f O_K (tau = -w)."""
    x, y = 1, 0
    for k in range(1, 400):
        x, y = -(2 * 0 + 0) + (-1) * 0, 0  # placeholder replaced below
        break
    a, b = 1, 0  # tau^k = a + b w ; tau = -w ; w^2 = w - 2
    for k in range(1, 400):
        a, b = 2 * b, -a - b  # (a + b w)(-w) = -a w - b w^2 = -a w - b(w - 2) = 2b + (-a - b) w
        if b % f == 0: return k
    return None

LEVELS = {"crater": 1, "floor409": 409, "floor1721": 1721, "bottom": 409 * 1721}
divs = sorted({d for d in range(2, 1001) if (L - 1) % d == 0})
out = {}
for lev, f in LEVELS.items():
    rows = {}
    for k in divs:
        rows[k] = min(min_degree_for_root(f, z) for z in prim_roots(k))
    out[lev] = dict(conductor=f, disc=-7 * f * f, min_nonscalar_endo_degree=min_endo_degree(f),
                    min_k_tau_power_in_End=tau_power_in_order(f), orbit_k_min_endo_degree=rows)
# sanity: crater, k = 37 must be degree 2 (tau itself)
assert out["crater"]["orbit_k_min_endo_degree"][41] == 2, out["crater"]["orbit_k_min_endo_degree"][41]
json.dump(out, open("level_traits.json", "w"), indent=1)
print(f"{'level':10} {'f':>7} {'min deg':>14} {'tau^k in End':>12}  min degree of endo giving orbit size k:")
print(" " * 48 + "  ".join(f"k={k:<4}" for k in divs))
for lev, d in out.items():
    print(f"{lev:10} {d['conductor']:7d} {d['min_nonscalar_endo_degree']:14d} {d['min_k_tau_power_in_End']:12d}   " +
          "  ".join(f"{d['orbit_k_min_endo_degree'][k]:.1e}" for k in divs))
print("GHS m(b): crater", ghs_magic(1))
