"""Positive control for blind_rederivation_b8cf21.py: same independent code,
applied to FROB-q7-n3-object01, where the producer DID find accepted relations
(all_rank=1 on cover "1" alone; all_rank=8 on cover "1,2,3"). If my code found
zero everywhere it would just be broken; this rules that out."""
import itertools

Q, N_FIELD = 7, 3
MODULUS = [1, 0, 1, 1]                 # f(z) = z^3 + z^2 + 1 over GF(7)
A, B = 3, 4

BASE1 = [(129, 3), (129, 4), (304, 3), (304, 4), (309, 3), (309, 4)]
BASE2 = [(184, 80), (184, 319), (291, 183), (291, 216), (320, 109), (320, 290)]
BASE3 = [(151, 150), (151, 200), (246, 98), (246, 245), (297, 54), (297, 296)]

def digits(a):
    out = []
    for _ in range(N_FIELD):
        out.append(a % Q); a //= Q
    assert a == 0
    return out
def encode(ds): return sum((int(x) % Q) * Q ** i for i, x in enumerate(ds))
def fadd(a, b): return encode([(x + y) % Q for x, y in zip(digits(a), digits(b))])
def fneg(a): return encode([(-x) % Q for x in digits(a)])
def fsub(a, b): return fadd(a, fneg(b))
def fmul(a, b):
    da, db = digits(a), digits(b)
    c = [0] * (2 * N_FIELD - 1)
    for i, x in enumerate(da):
        for j, y in enumerate(db):
            c[i + j] = (c[i + j] + x * y) % Q
    for k in range(len(c) - 1, N_FIELD - 1, -1):
        u = c[k]
        if u == 0: continue
        for i in range(N_FIELD):
            c[k - N_FIELD + i] = (c[k - N_FIELD + i] - u * MODULUS[i]) % Q
    return encode(c[:N_FIELD])
def fpow(a, k):
    out, base = 1, a
    while k:
        if k & 1: out = fmul(out, base)
        base = fmul(base, base); k >>= 1
    return out
def finv(a): return fpow(a, Q ** N_FIELD - 2)
def fdiv(a, b): return fmul(a, finv(b))

def on_curve(P):
    x, y = P
    return fmul(y, y) == fadd(fadd(fmul(fmul(x, x), x), fmul(A, x)), B)
def ec_neg(P): return None if P is None else (P[0], fneg(P[1]))
def ec_add(P, R):
    if P is None: return R
    if R is None: return P
    x1, y1 = P; x2, y2 = R
    if x1 == x2:
        if fadd(y1, y2) == 0: return None
        lam = fdiv(fadd(fmul(3, fmul(x1, x1)), A), fmul(2, y1))
    else:
        lam = fdiv(fsub(y2, y1), fsub(x2, x1))
    x3 = fsub(fsub(fmul(lam, lam), x1), x2)
    y3 = fsub(fmul(lam, fsub(x1, x3)), y1)
    return (x3, y3)

bad = [P for P in BASE1+BASE2+BASE3 if not on_curve(P)]
print(f"[sanity] off-curve points: {len(bad)}/18")
assert not bad

def accepted_count_for_union(union):
    uset = set(union); count = 0
    for Qp1, Qp2 in itertools.product(union, repeat=2):
        q3 = ec_neg(ec_add(Qp1, Qp2))
        if q3 is not None and q3 in uset:
            count += 1
    return count

for name, u in [("cover 1 (6 pts)", BASE1), ("cover 1,2,3 (18 pts)", BASE1+BASE2+BASE3)]:
    print(f"[independent] {name}: accepted_count = {accepted_count_for_union(u)}")
print("Producer: cover '1' all_rank=1 (nonzero expected); cover '1,2,3' all_rank=8, Delta_rank=5 (many expected)")
