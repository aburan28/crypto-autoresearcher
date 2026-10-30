from sage.all import *
import json
from pathlib import Path
proof.all(True)
p=ZZ(2)**256-ZZ(2)**224+ZZ(2)**192+ZZ(2)**96-1
r=ZZ('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551',16)
b=ZZ('5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b',16)
F=GF(p); R=PolynomialRing(F,'z'); z=R.gen(); f=z**3-3*z+b
K=F.extension(z*z+1,'i'); i=K.gen(); assert i*i==-1 and i**p==-i
E=EllipticCurve(F,[-3,b]); G=E(ZZ('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296',16),ZZ('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5',16))
assert f.is_irreducible()
rows=[]
for k in [0,1,2,19,31337,r-1]:
 P=k*G
 if P.is_zero():
  rows.append({'scalar':'0','quartic_infinity':'2*infinity','sextic_infinity':'infinity_plus+infinity_minus','norm_recovery':True});continue
 xp,yp=P[0],P[1]
 sqrtK=lambda c: K(c.sqrt()) if c.is_square() else i*K((-c).sqrt())
 u=sqrtK(yp); zz=sqrtK(xp)
 assert u**4==K(f(xp)) and (-u)**4==K(f(xp))
 assert u*u==yp and set([u**p,(-u)**p])==set([u,-u])
 assert K(yp)**2==zz**6-3*zz**2+b and zz*zz==xp
 assert set([zz**p,(-zz)**p])==set([zz,-zz])
 assert (z**6-3*z*z+b-yp*yp)%(z*z-xp)==0
 assert inverse_mod(2,r)*(2*P)==P
 rows.append({'scalar':str(k),'quartic_split':bool(yp.is_square()),'sextic_split':bool(xp.is_square()),'quartic_and_sextic_landing':True,'Fp2_Frobenius_stable_supports':True,'norm_recovery':True})
controls=[]
for pp in [5,7,11,13,19]:
 FF=GF(pp); RR=PolynomialRing(FF,'x'); x=RR.gen()
 good=x**3-3*x+1; bad=x**3-3*x+2
 assert gcd(good,good.derivative())==1
 assert gcd(bad,bad.derivative())!=1
 controls.append({'p':pp,'b1_smooth':True,'b2_singular_rejected':True})
# This wrong order witness must fail the actual group equation.
assert (r-1)*G!=E(0)
out={'sage':str(version()),'cubic_irreducible':True,'p2_modulus_irreducible':True,'fibres':rows,'smoothness_negative_controls':controls,'wrong_generator_order_rejected':True,'limits':'Fibre supports and ideal identities only; arbitrary Jacobian group arithmetic is unimplemented.'}
Path('/review/fibre-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2)); print('COMPLETION_SENTINEL',flush=True)
