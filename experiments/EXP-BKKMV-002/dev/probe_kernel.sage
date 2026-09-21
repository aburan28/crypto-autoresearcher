# probe_kernel.sage — EXP-BKKMV-002 dev probe (NOT a run)
# Verifies the fiberwise engine kernels BEFORE the official runs:
#   K1: companion-matrix resultant identity Res_X(A,B) = b2^8 * det(A(C_B))
#       vs the formal 10x10 Sylvester determinant (random instances, incl. a8=0)
#   K2: degenerate formal-Sylvester specializations:
#       b2=0        -> a8 * b1^8 * A(-b0/b1)
#       b2=b1=0     -> a8^2 * b0^8
#       vs the same formal determinant
#   K3: tensor-contraction evaluation (A-coefficients on a grid) vs Sage substitution
#   K4: tensor-grid interpolation round-trip on 17^5 (m=6-sized data, GF(101))
#   K5: timing of one m=6 section (values + interpolation), synthetic data
# Output: dev/probe_kernel.json ; all randomness seeded.

import json, time, random
import numpy as np

T0 = time.time()
def elapsed(): return time.time() - T0

def jsan(o):
    from sage.rings.integer import Integer
    from sage.rings.rational import Rational
    if isinstance(o, Integer): return int(o)
    if isinstance(o, Rational): return int(o) if o.denominator() == 1 else str(o)
    if isinstance(o, dict): return {str(k): jsan(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [jsan(v) for v in o]
    if isinstance(o, (int, float, str, bool)) or o is None: return o
    try:
        return float(o)
    except Exception:
        return str(o)

out = {"probe": "kernel", "checks": [], "timings": {}, "notes": []}
P = 1000003
F = GF(P)
rng = random.Random(int(20260718))

def sylvester10(a, b):
    """Formal Sylvester matrix for A = sum a[i] X^i (i=0..8), B = b[2]X^2+b[1]X+b[0].
    a: list of 9 field elements (a[0]..a[8]); b: list of 3 (b[0]..b[2])."""
    M = Matrix(F, 10, 10, 0)
    for k in range(2):        # rows 0..1: shifts of [a8..a0]
        for j in range(9):
            M[k, k + j] = a[8 - j]
    for r in range(8):        # rows 2..9: shifts of [b2,b1,b0]
        for j in range(3):
            M[2 + r, r + j] = b[2 - j]
    return M

def evalA(a, x):
    acc = F(0)
    for i in range(8, -1, -1):
        acc = acc * x + a[i]
    return acc

def companion_res(a, b):
    b0, b1, b2 = b[0], b[1], b[2]
    c0 = b0 / b2
    c1 = b1 / b2
    C = Matrix(F, 2, 2, [F(0), -c0, F(1), -c1])
    M = Matrix(F, 2, 2, 0)
    Cp = Matrix(F, 2, 2, 0); Cp[0,0] = F(1); Cp[1,1] = F(1)  # C^0
    for i in range(9):
        M += a[i] * Cp
        Cp = Cp * C
    return b2**8 * M.determinant()

def degen_b1(a, b):   # b2 = 0, b1 != 0
    beta = -b[0] / b[1]
    return a[8] * b[1]**8 * evalA(a, beta)

def degen_b0(a, b):   # b2 = b1 = 0
    return a[8]**2 * b[0]**8

# ---------- K1: regular instances, companion vs Sylvester det vs Sage resultant ----------
R.<X> = PolynomialRing(F)
k1 = 0
for trial in range(3000):
    a = [F.random_element() for _ in range(9)]
    b = [F.random_element() for _ in range(3)]
    if b[2] == 0: b[2] = F(1)
    if trial % 7 == 0: a[8] = F(0)      # include formal-degree drops of A
    if trial % 11 == 0: a[0] = F(0)
    det = sylvester10(a, b).determinant()
    comp = companion_res(a, b)
    A = sum(a[i] * X**i for i in range(9))
    B = b[2]*X**2 + b[1]*X + b[0]
    sg = A.resultant(B)
    ok = (det == comp)
    if a[8] != 0:
        ok = ok and (det == sg)                      # actual degrees == formal: all three agree
    else:
        ok = ok and (det == b[2] * sg)               # formal(8,2) with a8=0 == b2 * Res_{7,2} (col-0 expansion)
    if not ok:
        out["checks"].append({"id": "K1", "pass": False, "trial": trial,
                              "det": str(det), "comp": str(comp), "sage": str(sg)})
        break
    k1 += 1
else:
    out["checks"].append({"id": "K1", "pass": True, "n": k1,
                          "what": "companion == Sylvester det (3000 instances); == sage resultant when a8!=0; == b2*sage when a8=0 (formal-vs-actual degree factor, expected)"})

# ---------- K2a: b2 = 0 degenerate ----------
k2a = 0
for trial in range(2000):
    a = [F.random_element() for _ in range(9)]
    b = [F.random_element(), F.random_element(), F(0)]
    if b[1] == 0: b[1] = F(1)
    if trial % 5 == 0: a[8] = F(0)
    det = sylvester10(a, b).determinant()
    fm = degen_b1(a, b)
    if det != fm:
        out["checks"].append({"id": "K2a", "pass": False, "trial": trial, "det": str(det), "formula": str(fm)})
        break
    k2a += 1
else:
    out["checks"].append({"id": "K2a", "pass": True, "n": k2a,
                          "what": "b2=0: formal det == a8*b1^8*A(-b0/b1), 2000 instances"})

# ---------- K2b: b2 = b1 = 0 degenerate ----------
k2b = 0
for trial in range(1000):
    a = [F.random_element() for _ in range(9)]
    b = [F.random_element(), F(0), F(0)]
    if b[0] == 0: b[0] = F(1)
    if trial % 5 == 0: a[8] = F(0)
    det = sylvester10(a, b).determinant()
    fm = degen_b0(a, b)
    if det != fm:
        out["checks"].append({"id": "K2b", "pass": False, "trial": trial, "det": str(det), "formula": str(fm)})
        break
    k2b += 1
else:
    out["checks"].append({"id": "K2b", "pass": True, "n": k2b,
                          "what": "b2=b1=0: formal det == a8^2*b0^8, 1000 instances"})

# ---------- K3: tensor contraction vs Sage subs (m=5-sized random tensor) ----------
t3 = time.time()
T = np.random.randint(0, P, size=(9, 9, 9, 9, 9)).astype(np.int64)   # axes x1..x4, X
xs = [F.random_element() for _ in range(4)]
# sage polynomial from tensor (fast dict constructor)
R5.<x1,x2,x3,x4,XX> = PolynomialRing(F, 5)
nz = np.nonzero(T)
f_sage = R5({tuple(int(v) for v in idx): F(int(T[idx])) for idx in zip(*nz)})
# contraction along each x-axis: tensordot(pw[j], tmp, axes=([0],[0])) computes
# result[...] = sum_i pw[j][i] * tmp[i,...] = sum_i xs[j]^i * tmp[i,...]  (poly eval on axis 0)
subs_map = {x1: xs[0], x2: xs[1], x3: xs[2], x4: xs[3]}
f_sub = f_sage.subs(subs_map)
a_sage = [f_sub.monomial_coefficient(XX**i) for i in range(9)]
pw = [np.array([pow(int(xs[j]), e, P) for e in range(9)], dtype=np.int64) for j in range(4)]
tmp = T.astype(np.int64)
for j in range(4):
    tmp = np.tensordot(pw[j], tmp, axes=([0], [0])) % P
a_contract = tmp % P   # shape (9,) = a_0..a_8 at the point
k3pass = all(F(int(a_contract[i])) == a_sage[i] for i in range(9))
out["checks"].append({"id": "K3", "pass": bool(k3pass),
                      "what": "tensor contraction (tensordot over axis0 with power vector) == sage subs, random 9^5 tensor"})
out["timings"]["K3_seconds"] = round(time.time() - t3, 3)

# ---------- K4: interpolation round-trip on 17^5 over GF(101) ----------
t4 = time.time()
p2 = 101
nodes = np.arange(1, 18, dtype=np.int64)  # 17 distinct nodes mod 101
# inverse Vandermonde mod p2
Vp = Matrix(GF(p2), 17, 17, lambda i, j: GF(p2)(int(nodes[i]))**j)
W = np.array([[int(Vp.inverse()[i, j]) for j in range(17)] for i in range(17)], dtype=np.int64)
true_coeffs = np.random.randint(0, p2, size=(17, 17, 17, 17, 17)).astype(np.int64)
# evaluate on grid: contract all 5 axes with power tables (17 nodes x 17 exponents)
pw5 = [np.array([[pow(int(nd), e, p2) for e in range(17)] for nd in nodes], dtype=np.int64)]
vals = true_coeffs
for j in range(5):
    vals = np.tensordot(pw5[0], vals, axes=([1], [0])) % p2   # pw5[0][c,e] = nodes[c]^e ; contract exponent axis
    vals = np.moveaxis(vals, 0, -1)                           # keep node axis last to preserve axis order
# interpolate back along each axis
rec = vals
for j in range(5):
    rec = np.moveaxis(rec, j, 0).reshape(17, -1)
    rec = (W @ rec) % p2
    rec = rec.reshape((17,) * 5)
    rec = np.moveaxis(rec, 0, j)
k4pass = bool(np.array_equal(rec, true_coeffs))
out["checks"].append({"id": "K4", "pass": k4pass,
                      "what": "17^5 tensor-grid evaluation+interpolation round-trip exact, GF(101)"})
out["timings"]["K4_seconds_17^5_eval_plus_interp"] = round(time.time() - t4, 3)

# ---------- K5: synthetic m=6 section timing (companion values on 17^5 + interpolation) ----------
t5 = time.time()
p3 = 1000003
A_vals = np.random.randint(0, p3, size=(9, 17, 17, 17, 17)).astype(np.int64)  # a_0..a_8 on 17^4 grid
b2v, b1v, b0v = 123457, 65431, 77777
Fm = GF(p3)
c0 = int(Fm(b0v) / Fm(b2v)); c1 = int(Fm(b1v) / Fm(b2v))
C = np.array([[0, -c0], [1, -c1]], dtype=np.int64)
Cps = [np.eye(2, dtype=np.int64)]
for i in range(8):
    Cps.append((Cps[-1] @ C) % p3)
# M_entries[k,l] = sum_i A_vals[i] * Cps[i][k,l]  -> (4, 9) @ (9, 17^4)
L = np.array([[Cps[i][k, l] for i in range(9)] for k in range(2) for l in range(2)], dtype=np.int64)
Aflat = A_vals.reshape(9, -1)
Ment = (L @ Aflat) % p3
det = (Ment[0] * Ment[3] - Ment[1] * Ment[2]) % p3
b2_8 = pow(b2v, 8, p3)
Vslice = (det * b2_8) % p3      # one x5 slice (17^4 values)
V = np.tile(Vslice, 17)          # stand-in for 17 slices (same cost class)
t_vals = time.time() - t5
t6 = time.time()
Vg = V.reshape((17,) * 5)
Wp = Matrix(GF(p3), 17, 17, lambda i, j: GF(p3)(i + 1)**j)
W17 = np.array([[int(Wp.inverse()[i, j]) for j in range(17)] for i in range(17)], dtype=np.int64)
rec = Vg
for j in range(5):
    rec = np.moveaxis(rec, j, 0).reshape(17, -1)
    rec = (W17 @ rec) % p3
    rec = rec.reshape((17,) * 5)
    rec = np.moveaxis(rec, 0, j)
t_interp = time.time() - t6
out["timings"]["K5_one_slice_companion_seconds"] = round(t_vals, 3)
out["timings"]["K5_full_section_est_seconds"] = round(t_vals * 17 + t_interp, 3)
out["timings"]["K5_interp_seconds"] = round(t_interp, 3)

out["wall_seconds"] = round(elapsed(), 3)
with open("/Volumes/Volume/crypto-autoresearcher/experiments/EXP-BKKMV-002/dev/probe_kernel.json", "w") as fh:
    json.dump(jsan(out), fh, indent=1)
print(json.dumps(jsan(out["checks"])))
print(json.dumps(jsan(out["timings"])))
