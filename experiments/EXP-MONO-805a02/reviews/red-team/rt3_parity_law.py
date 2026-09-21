"""RED TEAM: harden the parity law. (i) squarefree-part factor shapes only ever
(1,1,1,1) or (2,2) -> generic Galois image is inside the Klein 4-group V_4, i.e.
the m=4 cover is IMPRIMITIVE; (ii) the same j=0-or-j=k law at m=5."""
import random, sys, time
import sympy
sys.path.insert(0, "/Volumes/SSD990/crypto-autoresearcher")
from harness.semaev import s3_expr, s4_expr, x1, x2, x3
x4, U, T = sympy.symbols("x4 U T")

def leg(v,p):
    v%=p
    return 0 if v==0 else (1 if pow(v,(p-1)//2,p)==1 else -1)

def shape_sqfree(expr, var, p):
    poly = sympy.Poly(sympy.expand(expr), var)
    co=[int(c)%p for c in poly.all_coeffs()]
    while len(co)>1 and co[0]==0: co=co[1:]
    deg=len(co)-1
    if deg<=0: return deg, None, None
    P=sympy.Poly(co,var,modulus=p)
    fl=P.factor_list()
    full=sorted([f.degree() for f,m in fl[1] for _ in range(m)])
    sq  =sorted([f.degree() for f,m in fl[1]])
    return deg, tuple(full), tuple(sq)

# ---- (i) m=4 shape census over UNIFORM specialisations (null-object style) ----
for (p,a,b) in [(211,37,57),(1009,17,19)]:
    S4=s4_expr(a,b); rng=random.Random(str((p,"shapes")))
    full_c={}; sq_c={}; nsplit=0; n=0
    for _ in range(400):
        u=[rng.randrange(p) for _ in range(3)]
        deg,full,sq=shape_sqfree(S4.subs({x1:u[0],x2:u[1],x4:u[2]}),x3,p)
        if full is None: continue
        n+=1; full_c[full]=full_c.get(full,0)+1; sq_c[sq]=sq_c.get(sq,0)+1
        if max(full)==1: nsplit+=1
    print(f"m=4 p={p} UNIFORM specialisation, n={n}: complete-split(mult) rate={nsplit/n:.4f}")
    print("   full shapes:", sorted(full_c.items(), key=lambda kv:-kv[1]))
    print("   squarefree :", sorted(sq_c.items(), key=lambda kv:-kv[1]))
    print("   [random quartic baseline: split rate ~1/24=0.0417; S_4 cover of a "
          "regular V_4 action predicts 1/4 of Frobenius elements trivial]")

# ---- (ii) m=5 parity law ----
def s5_in_x4(a,b,u1,u2,u3,tval):
    S4n = s4_expr(a,b).subs({x1:u1,x2:u2,x3:u3}).subs(x4,U)
    S3p = s3_expr(a,b).subs({x1:x4,x2:T,x3:U},simultaneous=True).subs(T,tval)
    return sympy.resultant(sympy.expand(S4n), sympy.expand(S3p), U)

for (p,a,b) in [(211,37,57)]:
    on=[v for v in range(p) if leg((v**3+a*v+b)%p,p)==1]
    off=[v for v in range(p) if leg((v**3+a*v+b)%p,p)==-1]
    rng=random.Random(str((p,"m5")))
    for name,spec in [("A_j0 all four on-curve (Stage5-as-specified)",("on","on","on","on")),
                      ("C_j1 target off-curve (GENUINELY partial)",("on","on","on","off")),
                      ("E_j4 ALL FOUR off-curve",("off","off","off","off")),
                      ("G_j2 two off-curve",("on","on","off","off"))]:
        ns=0; n=0; shapes={}
        t0=time.perf_counter()
        for _ in range(15):
            u=[rng.choice(on if s=="on" else off) for s in spec]
            deg,full,sq=shape_sqfree(s5_in_x4(a,b,u[0],u[1],u[2],u[3]),x4,p)
            if full is None: continue
            n+=1; shapes[full]=shapes.get(full,0)+1
            if max(full)==1: ns+=1
        print(f"m=5 p={p} {name:46s} split(mult)={ns}/{n}  shapes={sorted(shapes.items(),key=lambda kv:-kv[1])[:3]}  ({time.perf_counter()-t0:.1f}s)")
