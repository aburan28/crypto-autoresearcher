# Independent check of THM_QUOTIENT_DESCENT1 (research/THM_QUOTIENT_DESCENT1.lean:10-14)
# 1) abstract: in Z/a x Z/b, (forall P, -(P+S)+T = -(P+T+S)) <-> 2T=0, with and without 2S=0
# 2) concrete curve y^2 = x^3+2x^2+5x over F_1009 (the .md Sage check), + a curve with a rational
#    3-torsion point showing degree-2 maps whose involution is P -> -P+Q with Q not 2-torsion.
import itertools, random
def abstract(a,b):
    G=[(i,j) for i in range(a) for j in range(b)]
    add=lambda u,v:((u[0]+v[0])%a,(u[1]+v[1])%b); neg=lambda u:((-u[0])%a,(-u[1])%b)
    z=(0,0); bad_with=bad_without=0
    for S in G:
        for T in G:
            lhs=all(add(neg(add(P,S)),T)==neg(add(add(P,T),S)) for P in G)
            rhs=add(T,T)==z
            if lhs!=rhs:
                bad_without+=1
                if add(S,S)==z: bad_with+=1
    return bad_with,bad_without
for a,b in [(2,2),(4,2),(6,4),(12,1),(3,5),(8,8)]:
    print("Z/%d x Z/%d"%(a,b),"counterexamples (with hS, without hS):",abstract(a,b))
p=1009
def ec(a1,a2,a3,a4,a6):
    pass
# short-ish Weierstrass y^2 = x^3 + A2 x^2 + A4 x + A6
def mk(A2,A4,A6):
    O=None
    def onc(P):
        return P is None or (P[1]*P[1]-(P[0]**3+A2*P[0]**2+A4*P[0]+A6))%p==0
    def neg(P): return None if P is None else (P[0],(-P[1])%p)
    def add(P,Q):
        if P is None: return Q
        if Q is None: return P
        if P[0]==Q[0] and (P[1]+Q[1])%p==0: return None
        if P==Q: l=(3*P[0]**2+2*A2*P[0]+A4)*pow(2*P[1],-1,p)%p
        else: l=(Q[1]-P[1])*pow(Q[0]-P[0],-1,p)%p
        x=(l*l-A2-P[0]-Q[0])%p; y=(l*(P[0]-x)-P[1])%p
        return (x,y)
    pts=[None]+[(x,y) for x in range(p) for y in range(p) if (y*y-(x**3+A2*x*x+A4*x+A6))%p==0]
    return pts,add,neg
pts,add,neg=mk(2,5,0)
T2=(0,0)
def mul(n,P):
    R=None
    for _ in range(n): R=add(R,P)
    return R
print("#E(F_1009) for y^2=x^3+2x^2+5x:",len(pts))
xc=lambda P: None if P is None else P[0]
ok=all(xc(neg(add(P,T2)))==xc(add(neg(P),T2)) for P in pts)
print(".md Sage check (2-torsion translation commutes with [-1] on x) holds for all points:",ok)
# order-3 points?
o3=[Q for Q in pts if Q is not None and mul(3,Q) is None]
print("order-3 points on this curve:",len(o3))
# find any curve over F_1009 with a rational 3-torsion point, check translation by it does not descend through x
random.seed(1)
for trial in range(200):
    A2,A4,A6=random.randrange(p),random.randrange(p),random.randrange(p)
    if (4*A4**3+27*A6**2)%p==0: continue
    pts,add,neg=mk(A2,A4,A6)
    o3=[Q for Q in pts if Q is not None and add(Q,add(Q,Q)) is None]
    if o3: break
R=o3[0]
print("curve A2,A4,A6=",(A2,A4,A6),"#E=",len(pts),"R=",R,"(order 3)")
# translation by order-3 R does not permute x-fibres: find P where x(P)=x(P') but x(P+R)!=x(P'+R)
bad=sum(1 for P in pts if P is not None and xc(add(P,R))!=xc(add(neg(P),R)))
print("points P with x(P+R)!=x(-P+R) (descent fails, expected >0):",bad)
# degree-2 map phi(P)=x(P+R): fibre of P is {P, -P-2R}; involution P->-P+Q with Q=-2R=R, not 2-torsion
Q=neg(add(R,R))
inv=lambda P: add(neg(P),Q)
fib_ok=all(xc(add(P,R))==xc(add(inv(P),R)) for P in pts)
print("phi=x(P+R) has involution P->-P+Q, Q=-2R:",fib_ok,"; Q 2-torsion?",add(Q,Q) is None)
# the lemma for that involution: tau_T commutes with iota_Q iff 2T=0 (holds for every Q)
for T in pts[:40]:
    comm=all(add(inv(P),T)==inv(add(P,T)) for P in pts)
    assert comm==(add(T,T) is None)
print("lemma holds for involution with non-2-torsion Q on first 40 T: True")
