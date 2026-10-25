# Newton polytope / support of S_{m+1}(x_1..x_m, z) with z fixed, for a random curve over F_p.
import itertools, sys
p = next_prime(2^28)
F = GF(p)
a = F.random_element(); b = F.random_element()
R = PolynomialRing(F, 'x1,x2,x3,x4,x5,X', order='degrevlex')
x1,x2,x3,x4,x5,X = R.gens()
def S3(u,v,w):
    return (u-v)^2*w^2 - 2*((u+v)*(u*v+a)+2*b)*w + (u*v-a)^2 - 4*b*(u+v)
def resX(f,g):
    return f.resultant(g, X)
S4 = resX(S3(x1,x2,X), S3(x3,x4,X))
print("S4: nterms", len(S4.monomials()), "degs", [S4.degree(v) for v in (x1,x2,x3,x4)], "total", S4.total_degree())
S5 = resX(S4.subs({x4:X}), S3(x4,x5,X))
print("S5: nterms", len(S5.monomials()), "degs", [S5.degree(v) for v in (x1,x2,x3,x4,x5)], "total", S5.total_degree())
def support_stats(f, free, fixed):
    z = F.random_element()
    g = f.subs({fixed: z})
    mons = g.monomials()
    exps = [tuple(mon.degree(v) for v in free) for mon in mons]
    m = len(free); d = max(max(e) for e in exps)
    box = (d+1)^m
    cen = [sum(e[j] for e in exps)/len(exps) for j in range(m)]
    # continuous centroid of convex hull via Polyhedron
    P = Polyhedron(vertices=exps)
    cc = P.centroid()
    cN = sum(cc)
    print(f"  free vars {m}, deg/var {d}, support {len(exps)} of box {box}; discrete centroid sum {float(sum(cen)):.4f}; hull centroid sum {float(cN):.4f}; hull volume {float(P.volume()):.2f} vs box {d^m}")
    print(f"  JM basic asymptotic reach delta_max = 1/((m+1) c_N) = {float(1/((m+1)*cN)):.5f}; box formula 2/(m(m+1)d) = {float(2/(m*(m+1)*d)):.5f}")
S3p = S3(x1,x2,x3)
print("S3 with x3 fixed:"); support_stats(S3p, [x1,x2], x3)
print("S4 with x4 fixed:"); support_stats(S4, [x1,x2,x3], x4)
print("S5 with x5 fixed:"); support_stats(S5, [x1,x2,x3,x4], x5)
