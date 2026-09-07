import sys, random
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.isogeny3 import psi_3_roots, isogenous_curve_3, push_point_3
from driver.ecc import point_add, on_curve
from driver.curve_order import compute_group_order

def brute_all_points(a, b, p):
    pts = [None]
    for x in range(p):
        rhs = (x**3 + a*x + b) % p
        if rhs == 0:
            pts.append((x, 0))
        else:
            ls = pow(rhs, (p-1)//2, p)
            if ls == 1:
                y = None
                for cand in range(1, p):
                    if (cand*cand) % p == rhs:
                        y = cand
                        break
                pts.append((x, y))
                pts.append((x, (-y) % p))
    return pts

random.seed(4242)
tested = 0
hom_fails = 0
oncurve_fails = 0
degree_fails = 0
found_rational_x0 = 0
for trial in range(200):
    p = random.choice([97, 101, 103, 1009, 1013, 10007])
    a = random.randrange(0, p)
    b = random.randrange(0, p)
    if (4*a**3 + 27*b*b) % p == 0:
        continue
    roots0 = psi_3_roots(a, b, p)
    if not roots0:
        continue
    x0 = roots0[0]
    found_rational_x0 += 1
    a3, b3 = isogenous_curve_3(a, b, p, x0)
    if (4*a3**3 + 27*b3*b3) % p == 0:
        print("codomain singular", p, a, b, x0)
        continue
    tested += 1

    pts = brute_all_points(a, b, p)
    for P in pts:
        img = push_point_3(P, a, p, x0)
        if not on_curve(img, a3, b3, p):
            oncurve_fails += 1
            print("NOT ON CURVE", p, a, b, x0, P, img)

    for _ in range(150):
        P1 = random.choice(pts)
        P2 = random.choice(pts)
        lhs = push_point_3(point_add(P1, P2, a, p), a, p, x0)
        rhs = point_add(push_point_3(P1, a, p, x0),
                         push_point_3(P2, a, p, x0), a3, p)
        if lhs != rhs:
            hom_fails += 1
            if hom_fails <= 5:
                print("HOM FAIL", p, a, b, x0, P1, P2, lhs, rhs)

    try:
        N1, _, _ = compute_group_order(a, b, p, random.Random(1), max_points=20)
        N2, _, _ = compute_group_order(a3, b3, p, random.Random(2), max_points=20)
        if N1 != N2:
            degree_fails += 1
            print("N MISMATCH", p, a, b, x0, N1, N2)
    except RuntimeError:
        pass

print(f"found_rational_x0={found_rational_x0} tested={tested} oncurve_fails={oncurve_fails} hom_fails={hom_fails} degree_fails={degree_fails}")
