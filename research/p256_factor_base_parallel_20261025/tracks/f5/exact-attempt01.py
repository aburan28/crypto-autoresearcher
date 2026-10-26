from sage.all import *
import json, time, platform
from pathlib import Path
proof.all(True)
p=ZZ(2**256-2**224+2**192+2**96-1)
b=ZZ(0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)
r=ZZ(0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551)
F=GF(p); R=PolynomialRing(F,'x');x=R.gen(); E=EllipticCurve(F,[-3,b]); t=p+1-r; D=t*t-4*p
G=E(ZZ(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296),ZZ(0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5))
start=time.time()
base={'sage':version(),'p':str(p),'a':'-3','b':str(b),'r':str(r),'t':str(t),'Delta_pi':str(D),'p_prime':p.is_prime(proof=True),'r_prime':r.is_prime(proof=True),'G_nonzero':not G.is_zero(),'rG_zero':(r*G).is_zero(),'nonsingular':E.discriminant()!=0,'ordinary':t%p!=0}
assert all(base[k] for k in ['p_prime','r_prime','G_nonzero','rG_zero','nonsingular','ordinary'])
lo=p+1-2*p.isqrt();hi=p+1+2*p.isqrt();base['hasse_unique_multiple']=int(hi//r-(lo-1)//r)==1 and lo<=r<=hi
assert base['hasse_unique_multiple']; E.set_order(r)
base['cubic_factor_degrees']=[int(f.degree()) for f,e in (x**3-3*x+b).factor()]
base['screen']=[]
for ell in prime_range(2,44):
    roots=[int(z) for z in GF(ell)['z']([p,-t,1]).roots(multiplicities=False)]
    base['screen'].append({'ell':int(ell),'Delta_mod_ell':int(D%ell),'kronecker':int(kronecker(D,ell)),'Frobenius_roots':roots,'interpretation':'distinct split rational kernel lines' if ell!=2 and len(roots)==2 else ('ramified/repeated; actual kernels separately checked' if D%ell==0 else 'inert: no rational cyclic ell-isogeny')})
print(json.dumps(base,indent=2),flush=True)
Path('frobenius.json').write_text(json.dumps(base,indent=2)+'\n')
# Actual low odd degree kernels, with irreducible-factor receipts.
for ell in [3,5,11]:
    psi=E.division_polynomial(ell)
    fac=psi.factor()
    receipt={'ell':ell,'division_polynomial_degree':int(psi.degree()),'factor_degrees':[int(q.degree()) for q,e in fac],'multiplicities':[int(e) for q,e in fac]}
    candidates=[]
    # Degree (ell-1)/2 irreducible factors can be full cyclic kernels; validate using Sage isogeny construction.
    for q,e in fac:
        if q.degree()!=(ell-1)//2:continue
        try:
            phi=E.isogeny(q);Ep=phi.codomain();du=phi.dual();Ptest=[n*G for n in [0,1,2,3,17,257,65537]]
        except Exception as exc:
            candidates.append({'kernel':[str(z) for z in q.list()],'status':'construction_error','error':repr(exc)});continue
            checks=[]
            for P in Ptest:
                checks.append({'scalar_point':str(P),'image':str(phi(P)),'dual_composition':du(phi(P))==ell*P,'recovery':inverse_mod(ell,r)*du(phi(P))==P})
            assert all(c['dual_composition'] and c['recovery'] for c in checks)
            X,Y=phi.rational_maps();Xd,Yd=du.rational_maps()
            # Function-field certificate: map lands on codomain; reduce y^2=f(x).
            K=FractionField(PolynomialRing(F,['X','Y']));XX,YY=K.gens(); ff=XX**3-3*XX+b
            num=Y.numerator();den=Y.denominator()
            # Sage maps are exact objects; independent polynomial divisibility after common denominator.
            S=PolynomialRing(F,['x','y']);sx,sy=S.gens();
            xmap=FractionField(S)(X);ymap=FractionField(S)(Y)
            eq=(ymap**2+Ep.a1()*xmap*ymap+Ep.a3()*ymap-xmap**3-Ep.a2()*xmap**2-Ep.a4()*xmap-Ep.a6()).numerator()
            landing=eq.reduce([sy**2-(sx**3-3*sx+b)])==0
            assert landing
            cand={'status':'certified_map','kernel':[str(z) for z in q.list()],'degree':int(phi.degree()),'separable':phi.is_separable(),'codomain_ainvs':[str(z) for z in Ep.a_invariants()],'codomain_j':str(Ep.j_invariant()),'source_j':str(E.j_invariant()),'rational_maps':[str(X),str(Y)],'dual_maps':[str(Xd),str(Yd)],'landing_polynomial_remainder_zero':landing,'checks':checks,'f_E':None,'direction':'unresolved','subgroup_proof':'dual o phi=[ell], gcd(ell,r)=1; inverse_mod(ell,r)*dual recovers points; same scalar logs','x_degrees':[int(X.numerator().degree()),int(X.denominator().degree())]}
            candidates.append(cand)
    receipt['candidates']=candidates
    Path('kernel-screen-%s.json'%ell).write_text(json.dumps(receipt,indent=2)+'\n')
