# DEVELOPMENT check on a toy field only: can Sage do generic EC arithmetic over the
# quotient ring GF(p)[t]/(t^5-3) (NOT the PARI FFELT field)?
import time
for p in [11, 2**64 - 2**32 + 1]:
    R = PolynomialRing(GF(p), 't'); t = R.gen()
    K = R.quotient(t**5 - 3, 'w'); w = K.gen()
    print(p, type(K).__name__, K.is_field(), type(R).__name__, type(GF(p)(1)).__name__)
    E = EllipticCurve(K, [K(3), 8*w**4])
    print(type(E).__name__)
    if p == 11:
        # find a point by brute force x = w + k
        for k in range(p):
            x = w + k; r = x**3 + 3*x + 8*w**4
            try:
                y = r.sqrt()
            except Exception as e:
                continue
            if y**2 == r: break
        Pt = E(x, y); print('point ok', Pt)
        t0 = time.time(); Q = 12345678901234567890123*Pt; print('mul ok', time.time()-t0, type(Pt).__name__)
        import inspect; print(inspect.getsource(type(Pt)._acted_upon_)[:300] if hasattr(type(Pt), '_acted_upon_') else 'no _acted_upon_')
