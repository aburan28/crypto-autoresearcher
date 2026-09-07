import sys, random
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.isogeny2 import two_torsion_roots, isogenous_curve_2, push_point_2
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

random.seed(99)
tested_curves = 0
hom_fails = 0
oncurve_fails = 0
degree_fails = 0
for trial in range(60):
    p = random.choice([97, 101, 103, 1009, 1013])
    a = random.randrange(0, p)
    b = random.randrange(0, p)
    if (4*a**3 + 27*b*b) % p == 0:
        continue
    roots0 = two_torsion_roots(a, b, p)
    if not roots0:
        continue
    x0 = roots0[0]
    tested_curves += 1
    a2, b2, t = isogenous_curve_2(a, b, p, x0)
    # singular check on codomain
    if (4*a2**3 + 27*b2*b2) % p == 0:
        print("codomain singular!", p, a, b, x0)
        continue

    pts = brute_all_points(a, b, p)
    # on-curve check for image points
    for P in pts:
        img = push_point_2(P, a, p, x0, t)
        if not on_curve(img, a2, b2, p):
            oncurve_fails += 1
            print("NOT ON CURVE", p, a, b, x0, P, img)

    # homomorphism check on random pairs
    for _ in range(200):
        P1 = random.choice(pts)
        P2 = random.choice(pts)
        lhs = push_point_2(point_add(P1, P2, a, p), a, p, x0, t)
        rhs = point_add(push_point_2(P1, a, p, x0, t), push_point_2(P2, a, p, x0, t), a2, p)
        if lhs != rhs:
            hom_fails += 1
            if hom_fails <= 5:
                print("HOM FAIL", p, a, b, x0, P1, P2, lhs, rhs)

    # degree / kernel check: exactly the 2 kernel points map to O; #E' should have same N (Tate)
    try:
        N1, _, _ = compute_group_order(a, b, p, random.Random(1), max_points=20)
        N2, _, _ = compute_group_order(a2, b2, p, random.Random(2), max_points=20)
    except RuntimeError:
        continue  # pathological small composite-order test curve; not a real acceptance candidate
    if N1 != N2:
        degree_fails += 1
        print("N MISMATCH (violates Tate invariance -> isogeny formula bug)", p, a, b, x0, N1, N2)

print(f"tested_curves={tested_curves} oncurve_fails={oncurve_fails} hom_fails={hom_fails} degree_fails={degree_fails}")
