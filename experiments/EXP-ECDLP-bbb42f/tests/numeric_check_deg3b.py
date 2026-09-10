import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.ecc import point_add, point_neg, scalar_mult, tonelli_shanks

p = 1009
a, b = 417, 272
T = (886, 996)
x0, y0 = T
negT = point_neg(T, p)
print("3T =", scalar_mult(3, T, a, p), "negT=", negT)

def X_sum2(P):
    if P is None:
        return None
    x, y = P
    PT = point_add(P, T, a, p)
    PmT = point_add(P, negT, a, p)
    if PT is None or PmT is None:
        return None
    return (x + (PT[0]-x0) + (PmT[0]-x0)) % p

def Y_sum2(P):
    if P is None:
        return None
    x, y = P
    PT = point_add(P, T, a, p)
    PmT = point_add(P, negT, a, p)
    if PT is None or PmT is None:
        return None
    return (y + (PT[1]-y0) + (PmT[1]-(-y0 % p))) % p

results = []
for x in range(p):
    rhs = (x**3+a*x+b) % p
    y = tonelli_shanks(rhs, p)
    if y is None:
        continue
    for yy in {y, (-y) % p}:
        P = (x, yy)
        if x == x0:
            continue
        X, Y = X_sum2(P), Y_sum2(P)
        if X is None:
            continue
        results.append((X, Y))
        if len(results) >= 8:
            break
    if len(results) >= 8:
        break

(X1, Y1) = results[0]
A = B = None
for (X2, Y2) in results[1:]:
    dX = (X1 - X2) % p
    if dX == 0:
        continue
    A = ((Y1*Y1-X1**3) - (Y2*Y2-X2**3)) * pow(dX, -1, p) % p
    B = (Y1*Y1 - X1**3 - A*X1) % p
    break
print("derived A,B:", A, B)
allok = True
for (X,Y) in results:
    ok = (Y*Y - X**3 - A*X - B) % p == 0
    if not ok:
        allok = False
    print(X, Y, "on derived curve?", ok)
print("ALL OK:", allok)
