import sys, random
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.projective_ecc import proj_add, proj_double, proj_scalar_mult, to_affine, from_affine
from driver.ecc import point_add, scalar_mult, random_point

random.seed(555)
fails = 0
checks = 0
for trial in range(20):
    p = random.choice([97, 101, 1009, 10007, 100003, 1048583])
    a = random.randrange(0, p)
    b = random.randrange(0, p)
    if (4 * a**3 + 27 * b * b) % p == 0:
        continue
    rng = random.Random(trial)
    pts = [random_point(a, b, p, rng) for _ in range(15)]

    # doubling
    for P in pts:
        Pp = from_affine(P, p)
        d1 = to_affine(proj_double(Pp, a, p), p)
        d2 = point_add(P, P, a, p)
        checks += 1
        if d1 != d2:
            fails += 1
            print("DOUBLE MISMATCH", p, a, b, P, d1, d2)

    # addition (all pairs incl P+P, P+(-P))
    for i in range(len(pts)):
        for j in range(len(pts)):
            P1, P2 = pts[i], pts[j]
            r1 = to_affine(proj_add(from_affine(P1, p), from_affine(P2, p), a, p), p)
            r2 = point_add(P1, P2, a, p)
            checks += 1
            if r1 != r2:
                fails += 1
                print("ADD MISMATCH", p, a, b, P1, P2, r1, r2)

    # scalar mult vs affine scalar_mult
    for P in pts[:5]:
        k = rng.randrange(1, 500)
        s1 = to_affine(proj_scalar_mult(k, from_affine(P, p), a, p), p)
        s2 = scalar_mult(k, P, a, p)
        checks += 1
        if s1 != s2:
            fails += 1
            print("SCALAR MISMATCH", p, a, b, P, k, s1, s2)

print(f"checks={checks} fails={fails}")
