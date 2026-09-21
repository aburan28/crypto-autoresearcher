import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.ecc import point_add, scalar_mult, on_curve, tonelli_shanks

p = 1009
a, b = 417, 272
T = (886, 996)
print("3T =", scalar_mult(3, T, a, p))
x0, y0 = T
print("3T =", scalar_mult(3, T, a, p))

# now directly compute X(P) = x(P) + [x(P+T) - x0] using MY VERIFIED point_add, numerically
def X_sum_def(P):
    if P is None:
        return None
    x, y = P
    PT = point_add(P, T, a, p)
    if PT is None:
        return None
    return (x + PT[0] - x0) % p

def Y_sum_def(P):
    if P is None:
        return None
    x, y = P
    PT = point_add(P, T, a, p)
    if PT is None:
        return None
    return (y + PT[1] - y0) % p

# test many points P, check if (X(P),Y(P)) lie on a CONSISTENT curve
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
        X, Y = X_sum_def(P), Y_sum_def(P)
        results.append((X, Y))
        if len(results) >= 6:
            break
    if len(results) >= 6:
        break

# solve A,B from first two points
(X1,Y1),(X2,Y2) = results[0], results[1]
dX = (X1 - X2) % p
A = ((Y1*Y1-X1**3) - (Y2*Y2-X2**3)) * pow(dX, -1, p) % p
B = (Y1*Y1 - X1**3 - A*X1) % p
print("derived A,B from first 2 points:", A, B)
for (X,Y) in results:
    ok = (Y*Y - X**3 - A*X - B) % p == 0
    print(X, Y, "on derived curve?", ok)
