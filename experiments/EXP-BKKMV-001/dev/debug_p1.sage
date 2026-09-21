import random
R = PolynomialRing(GF(1000003), 2, 'y')
def dense_support(n, d):
    out = []
    def rec(prefix, left, dim):
        if dim == 0:
            out.append(tuple(prefix))
            return
        for v in range(left + 1):
            rec(prefix + [v], left - v, dim - 1)
    rec([], d, n - 1)
    return set(out)
supp = dense_support(2, 2)
print("supp:", sorted(supp), "len:", len(supp))
rng = random.Random(int(900000000 + 2*1000 + 2))
def random_poly_on_support(R, supp, rng):
    p = R.base_ring().order()
    f = R(0)
    g = R.gens()
    for e in sorted(supp):
        c = rng.randrange(1, p)
        mon = R(1)
        for i, v in enumerate(e):
            if v:
                mon *= g[i]**v
        f += c * mon
    return f
f0 = random_poly_on_support(R, supp, rng)
f1 = random_poly_on_support(R, supp, rng)
print("f0:", f0)
s0 = set(tuple(int(v) for v in e[:2]) for e in f0.exponents())
print("supp f0:", sorted(s0), len(s0))
maxes = [max(e[i] for e in s0) for i in range(2)]
print("maxes:", maxes, "full:", (maxes[0]+1)*(maxes[1]+1))
P0 = Polyhedron(vertices=[list(e) for e in s0])
P1 = Polyhedron(vertices=[list(e) for e in s0])
print("V0:", P0.volume(), "V sum:", (P0+P1).volume())
print("Minkowski vertices sum:", (P0+P1).vertices())
