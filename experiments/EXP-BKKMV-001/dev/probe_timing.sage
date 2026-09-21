# Dev probe (exploratory, not a canonical run): time Semaev polynomial computation
# S_3, S_4, S_5 over F_1000003, plus sectioned support sizes and a Polyhedron volume test.
import time, json, sys

p = 1000003
Fp = GF(p)
A, B = Fp(12345), Fp(67890)

t0 = time.time()
R3 = PolynomialRing(Fp, 3, 'x')
x1, x2, x3 = R3.gens()
S3 = (x1*x2 + x1*x3 + x2*x3 + A)**2 - 4*(x1*x2*x3 - B)*(x1 + x2 + x3)
t1 = time.time()

# S_4 = Res_X(S_3(x1,x2,X), S_3(x3,x4,X))
R4 = PolynomialRing(Fp, 5, 'x')   # x1..x4, X
a = R4.gens()
S3a = S3.subs({x1: a[0], x2: a[1], x3: a[4]})
S3b = S3.subs({x1: a[2], x2: a[3], x3: a[4]})
t2 = time.time()
S4 = S3a.resultant(S3b, a[4])
t3 = time.time()

# S_5 = Res_X(S_4(x1,x2,x3,X), S_3(x4,x5,X))
R5 = PolynomialRing(Fp, 6, 'x')   # x1..x5, X
b = R5.gens()
S4a = S4.subs({a[0]: b[0], a[1]: b[1], a[2]: b[2], a[3]: b[5]})
S3c = S3.subs({x1: b[3], x2: b[4], x3: b[5]})
t4 = time.time()
S5 = S4a.resultant(S3c, b[5])
t5 = time.time()

def supp_size(f):
    return len(f.exponents())

out = {
  "t_S3": float(t1-t0), "t_S4_setup": float(t2-t1), "t_S4_resultant": float(t3-t2),
  "t_S5_setup": float(t4-t3), "t_S5_resultant": float(t5-t4),
  "S3_terms": int(supp_size(S3)), "S4_terms": int(supp_size(S4)), "S5_terms": int(supp_size(S5)),
  "S4_deg_per_var": [int(S4.degree(g)) for g in R4.gens()[:4]],
  "S5_deg_per_var": [int(S5.degree(g)) for g in R5.gens()[:5]],
  "S4_total_deg": int(S4.total_degree()), "S5_total_deg": int(S5.total_degree()),
}
print(json.dumps(out))
sys.stdout.flush()

# Polyhedron volume probe on sectioned S_4 support (3D)
tsec = Fp(999983)
f = S4.subs({a[3]: tsec})
pts = [list(e) for e in f.exponents()]
t6 = time.time()
P = Polyhedron(vertices=pts)
t7 = time.time()
out2 = {"t_poly3d": t7-t6, "n_pts": len(pts), "n_vertices": len(P.vertices()),
        "vol": str(P.volume()), "backend": str(P.backend())}
print(json.dumps(out2))
sys.stdout.flush()

# Polyhedron volume probe on sectioned S_5 support (4D)
f5 = S5.subs({b[4]: tsec})
pts5 = [list(e) for e in f5.exponents()]
t8 = time.time()
P5 = Polyhedron(vertices=pts5)
t9 = time.time()
out3 = {"t_poly4d": t9-t8, "n_pts": len(pts5), "n_vertices": len(P5.vertices()),
        "vol": str(P5.volume()), "backend": str(P5.backend())}
print(json.dumps(out3))
