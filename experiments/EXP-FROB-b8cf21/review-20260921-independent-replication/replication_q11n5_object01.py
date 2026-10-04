"""
BLIND RE-DERIVATION for /review-evidence EXP-FROB-b8cf21.

Independent, from-scratch check of the load-bearing zero-witness claim on
FROB-q11-n5-object01 (H-FROB-824aa8's existence prediction). This file:

  - imports nothing from experiments/EXP-FROB-b8cf21/runs/TASK-20260907-ee1e3c/
    (neither implementation.py's Sage path nor checker.py's own Field class);
  - takes as GIVEN, frozen, immutable INPUT DATA only: the field modulus,
    curve coefficients, subgroup order, and the raw base point coordinate
    lists, all read directly from fixtures.json (an immutable run artifact,
    not code);
  - independently re-implements finite-field arithmetic (digit encoding is a
    DATA FORMAT fact stated in fixtures.json's 'modulus' field, not an
    algorithm under test) and elliptic-curve point addition/negation from
    scratch, in plain Python, with no Sage dependency at all;
  - re-derives, independently, whether ANY 3-point relation P1+P2+P3=O exists
    with all three points drawn from the stated base union, for cover "1"
    alone and cover "1,2", on FROB-q11-n5-object01.

Producer's own definition being re-derived (implementation.py L515-528, read
for understanding only, not imported/reused):
    accepted = Q3 is not None and Q3 in union_set
  where Q3 = -(Q1+Q2), ranging Q1,Q2 over ALL ordered pairs of union x union.
"""
import itertools

# ---- Frozen input data, read directly from fixtures.json (immutable) ----
Q, N_FIELD = 11, 5
MODULUS = [1, 0, 0, 0, 2, 1]          # f(z) = z^5 + 2z^4 + 1 over GF(11)
A, B = 1, 2                            # curve y^2 = x^3 + A x + B
N_SUBGROUP = 10061

BASE1 = [(45629, 38778), (45629, 138377), (84671, 63598), (84671, 113557),
         (87112, 41749), (87112, 135285), (147141, 49044), (147141, 128111),
         (150808, 35), (150808, 97)]
BASE2 = [(24681, 45561), (24681, 131594), (24703, 50144), (24703, 127011),
         (67275, 34296), (67275, 142859), (100995, 58921), (100995, 103593),
         (152760, 26276), (152760, 150879)]


# ---- Independent field arithmetic (digit encoding: a = sum digit_i * Q^i) ----
def digits(a):
    out = []
    for _ in range(N_FIELD):
        out.append(a % Q)
        a //= Q
    assert a == 0
    return out


def encode(ds):
    return sum((int(x) % Q) * Q ** i for i, x in enumerate(ds))


def fadd(a, b):
    return encode([(x + y) % Q for x, y in zip(digits(a), digits(b))])


def fneg(a):
    return encode([(-x) % Q for x in digits(a)])


def fsub(a, b):
    return fadd(a, fneg(b))


def fmul(a, b):
    da, db = digits(a), digits(b)
    c = [0] * (2 * N_FIELD - 1)
    for i, x in enumerate(da):
        for j, y in enumerate(db):
            c[i + j] = (c[i + j] + x * y) % Q
    # reduce mod f(z) = MODULUS (monic, degree N_FIELD)
    for k in range(len(c) - 1, N_FIELD - 1, -1):
        u = c[k]
        if u == 0:
            continue
        for i in range(N_FIELD):
            c[k - N_FIELD + i] = (c[k - N_FIELD + i] - u * MODULUS[i]) % Q
    return encode(c[:N_FIELD])


def fpow(a, k):
    out = 1
    base = a
    while k:
        if k & 1:
            out = fmul(out, base)
        base = fmul(base, base)
        k >>= 1
    return out


def finv(a):
    assert a != 0
    return fpow(a, Q ** N_FIELD - 2)


def fdiv(a, b):
    return fmul(a, finv(b))


# ---- Independent elliptic curve arithmetic (affine Weierstrass, INFINITY=None) ----
def on_curve(P):
    x, y = P
    lhs = fmul(y, y)
    rhs = fadd(fadd(fmul(fmul(x, x), x), fmul(A, x)), B)
    return lhs == rhs


def ec_neg(P):
    if P is None:
        return None
    x, y = P
    return (x, fneg(y))


def ec_add(P, Rp):
    if P is None:
        return Rp
    if Rp is None:
        return P
    x1, y1 = P
    x2, y2 = Rp
    if x1 == x2:
        if fadd(y1, y2) == 0:
            return None  # P + (-P) = O
        # doubling: lam = (3x1^2 + A) / (2y1)
        lam = fdiv(fadd(fmul(3, fmul(x1, x1)), A), fmul(2, y1))
    else:
        lam = fdiv(fsub(y2, y1), fsub(x2, x1))
    x3 = fsub(fsub(fmul(lam, lam), x1), x2)
    y3 = fsub(fmul(lam, fsub(x1, x3)), y1)
    return (x3, y3)


# ---- Sanity: every stated base point actually lies on E ----
bad = [P for P in BASE1 + BASE2 if not on_curve(P)]
print(f"[sanity] points off-curve among BASE1+BASE2: {len(bad)} / {len(BASE1)+len(BASE2)}")
assert not bad, f"OFF-CURVE POINTS FOUND (independent check disagrees with fixture data): {bad}"

# ---- Independent re-derivation of accepted_count for cover "1" and "1,2" ----
def accepted_count_for_union(union):
    uset = set(union)
    count = 0
    witnesses = []
    for Qp1, Qp2 in itertools.product(union, repeat=2):
        s = ec_add(Qp1, Qp2)
        q3 = ec_neg(s)
        if q3 is not None and q3 in uset:
            count += 1
            witnesses.append((Qp1, Qp2, q3))
    return count, witnesses


for name, union in [("cover 1 (base1 only, 10 pts)", BASE1),
                     ("cover 2 (base2 only, 10 pts)", BASE2),
                     ("cover 1,2 (base1 U base2, 20 pts)", BASE1 + BASE2)]:
    c, w = accepted_count_for_union(union)
    print(f"[independent] {name}: accepted_count = {c}" + (f"  witnesses(sample)={w[:3]}" if w else ""))

print()
print("PRODUCER'S CLAIM (metrics.json, FROB-q11-n5-object01, negation presentation):")
print("  cover '1'   -> all_rank=0 (=> accepted_count=0 implied)")
print("  cover '2'   -> all_rank=0 (=> accepted_count=0 implied)")
print("  cover '1,2' -> all_rank=0, Delta_rank=0, mixed_accepted_pairs=0")
