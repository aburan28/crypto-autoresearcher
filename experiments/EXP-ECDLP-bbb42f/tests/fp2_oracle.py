import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")

p = 1009
d = 219  # non-residue: y0^2 = d, y0 = (0,1) in basis 1, w where w^2=d

# F_{p^2} elements as (u, v) meaning u + v*w, w^2 = d
def fp2_add(A, B):
    return ((A[0] + B[0]) % p, (A[1] + B[1]) % p)

def fp2_sub(A, B):
    return ((A[0] - B[0]) % p, (A[1] - B[1]) % p)

def fp2_mul(A, B):
    u1, v1 = A
    u2, v2 = B
    u = (u1 * u2 + v1 * v2 * d) % p
    v = (u1 * v2 + v1 * u2) % p
    return (u, v)

def fp2_inv(A):
    u, v = A
    norm = (u * u - d * v * v) % p
    norm_inv = pow(norm, -1, p)
    return ((u * norm_inv) % p, (-v * norm_inv) % p)

def fp2_from_int(n):
    return (n % p, 0)

def fp2_eq(A, B):
    return A == B

def fp2_neg(A):
    return ((-A[0]) % p, (-A[1]) % p)

a, b, x0 = 134, 29, 273
a_f = fp2_from_int(a)

def point_add_fp2(P1, P2):
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    x1, y1 = P1
    x2, y2 = P2
    if fp2_eq(x1, x2) and fp2_eq(fp2_add(y1, y2), (0, 0)):
        return None
    if fp2_eq(x1, x2) and fp2_eq(y1, y2):
        num = fp2_add(fp2_mul(fp2_from_int(3), fp2_mul(x1, x1)), a_f)
        den = fp2_mul(fp2_from_int(2), y1)
        lam = fp2_mul(num, fp2_inv(den))
    else:
        num = fp2_sub(y2, y1)
        den = fp2_sub(x2, x1)
        lam = fp2_mul(num, fp2_inv(den))
    x3 = fp2_sub(fp2_sub(fp2_mul(lam, lam), x1), x2)
    y3 = fp2_sub(fp2_mul(lam, fp2_sub(x1, x3)), y1)
    return (x3, y3)

def point_neg_fp2(P):
    if P is None:
        return None
    x, y = P
    return (x, fp2_neg(y))

x0_f = fp2_from_int(x0)
y0_f = (0, 1)  # sqrt(d)
T = (x0_f, y0_f)
negT = point_neg_fp2(T)

def oracle_fp2(P):
    x, y = P
    PT = point_add_fp2(P, T)
    PmT = point_add_fp2(P, negT)
    X = fp2_add(fp2_add(x, fp2_sub(PT[0], x0_f)), fp2_sub(PmT[0], x0_f))
    Y = fp2_add(fp2_add(y, fp2_sub(PT[1], y0_f)), fp2_sub(PmT[1], fp2_neg(y0_f)))
    return X, Y

# test points: use ACTUAL F_p points on the origin curve (a=134,b=29)
from driver.ecc import random_point
import random
rng = random.Random(7)
for _ in range(5):
    Pp = random_point(a, b, p, rng)  # (x,y) in F_p
    P_fp2 = (fp2_from_int(Pp[0]), fp2_from_int(Pp[1]))
    X, Y = oracle_fp2(P_fp2)
    print(Pp, "-> X=", X, " Y=", Y, " (v-component should be 0 for both if formula is y0-free)")
