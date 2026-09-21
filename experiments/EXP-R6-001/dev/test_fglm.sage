import time
def S3(X1,X2,X3,a,b):
    return ((X1-X2)**2*X3**2 - 2*((X1+X2)*(X1*X2+a)+2*b)*X3 + ((X1*X2-a)**2 - 4*b*(X1+X2)))
# rebuild probe F=16 system exactly (seed 101 curve, seed 1016 FB)
exec(open("experiments/EXP-R6-001/R6_run.sage").read().split("# ------------------------------------------------------------------- modes")[0].split("T0 = time.time()")[1].replace("def now(): return time.time()\ndef elapsed(): return now() - T0","def now(): return time.time()"))
c = find_curve_with_subgroup(2**13, int(1.15*2**13), 16, seed=101)
E = EllipticCurve(GF(c["p"]), [c["a4"], c["a6"]])
xs, pts = fb_random(E, 16, seed=1016)
set_random_seed(0)  # match probe's planted index draw? probe used current randstate after fb; approximate: any planted triple
R = pts[0]+pts[3]+pts[7]
xR = R.xy()[0]
F = E.base_field(); a4,a6 = E.a4(), E.a6()
Rp = PolynomialRing(F, ['x1','x2','x3','u'], order='degrevlex'); x1,x2,x3,u = Rp.gens()
eqs = [S3(x1,x2,u,a4,a6), S3(u,x3,F(xR),a4,a6)] + [prod(z-f for f in xs) for z in (x1,x2,x3)]
I = Rp.ideal(eqs)
t0=time.time(); gb=I.groebner_basis(); print("gb %.2f d_reg=%d" % (time.time()-t0, max((g.total_degree() for g in gb))))
t0=time.time(); vd=I.vector_space_dimension(); print("vdim", vd, "%.2fs"%(time.time()-t0))
t0=time.time(); lex = I.transformed_basis("fglm"); print("fglm %.2fs, npolys=%d" % (time.time()-t0, len(lex)))
for g in lex: print("  lexgb elem deg", g.total_degree(), "vars", [str(v) for v in g.variables()])
t0=time.time()
fu = lex[-1]
rt = fu.univariate().roots(F)
print("roots %d in %.3fs" % (len(rt), time.time()-t0))
