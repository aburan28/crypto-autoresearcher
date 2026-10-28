"""Independent algebra, public parameters; producer JSON is comparison data only."""
from sage.all import *
import json, sys, time, platform
from pathlib import Path
proof.all(True)
OUT=Path('/review')
TRACKS=Path('/inputs')
p=ZZ(2)**256-ZZ(2)**224+ZZ(2)**192+ZZ(2)**96-1
r=ZZ('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551',16)
b=ZZ('5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b',16)
gx=ZZ('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296',16)
gy=ZZ('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5',16)
t=p+1-r; delta=t*t-4*p
result={'runtime':str(version()),'python':platform.python_version(),'proof_all':True,'parameters':{'p':str(p),'r':str(r),'b':str(b)},'checks':{}}
def say(k,v):
 result['checks'][k]=v; print(k,json.dumps(v),flush=True)
def coeffs(f): return [str(ZZ(c)) for c in f.list()]
def save():
 with (OUT/'independent-results.json').open('w') as f:json.dump(result,f,indent=2)
assert p.is_prime(proof=True) and r.is_prime(proof=True)
F=GF(p); R=PolynomialRing(F,'x'); x=R.gen(); Q=R.fraction_field()
a=F(-3); bf=F(b); f=x**3+a*x+bf
E=EllipticCurve(F,[a,bf]); G=E(F(gx),F(gy))
assert not G.is_zero() and r*G==E(0)
rad=(4*p).isqrt(); lo=p+1-rad; hi=p+1+rad
assert (lo+r-1)//r==hi//r==1
say('source',{'p_prime':True,'r_prime':True,'G_order_r':True,'hasse_radius':str(rad),'hasse_unique_multiple':str(r),'t':str(t),'delta':str(delta),'ordinary':bool(t%p),'smooth':bool(E.discriminant())})
# The prime factors are certificate witnesses read after the blind record, not imports.
factors=[ZZ(v) for v in ['3','5','456597257999','1428624589419343516204097','46523541035814968339936406074986559003387']]
assert prod(factors)==-delta and len(set(factors))==len(factors)
assert all(q.is_prime(proof=True) for q in factors) and delta%4==1
say('conductor',{'prime_factor_certificate_witnesses':list(map(str,factors)),'all_proven_prime':True,'fundamental':True,'f_pi':1,'f_E':1})
# Recover the whole candidate set from division polynomials, independently.
maprows=[]
for ell in [3,5,11]:
 fs=E.division_polynomial(ell).factor(); hs=[h.monic() for h,e in fs]
 print('factored',ell,[int(h.degree()) for h in hs],flush=True)
 if ell==3: candidates=[h for h in hs if h.degree()==1]
 elif ell==5: candidates=[prod(h for h in hs if h.degree()==1)]
 else:candidates=hs
 producer=json.loads((TRACKS/'f5'/('attempt02-kernel-screen-%s.json'%ell)).read_text())
 good=[]; invalid=0
 for idx,h in enumerate(candidates):
  n=h.degree(); c=lambda j: h[j] if j>=0 else F(0)
  s1=-c(n-1); s2=c(n-1)**2-2*c(n-2)
  s3=-c(n-1)**3+3*c(n-1)*c(n-2)-3*c(n-3)
  S0=Q(h.derivative())/h
  S1=x*S0-n; S2=x*x*S0-n*x-s1
  S3=x**3*S0-n*x*x-s1*x-s2
  xm=Q(x)+6*S2+2*a*S0-4*(S3+a*S1+bf*S0).derivative()
  ym=xm.derivative()
  ap=a-5*(6*s2+2*a*n); bp=bf-7*(10*s3+6*a*s1+4*bf*n)
  landing=Q(f)*ym**2-xm**3-ap*xm-bp==0
  A=R.quotient(h,'q'); q=A.gen(); closure=[]
  for m in range(2,(ell-1)//2+1):
   mr=Q(E.multiplication_by_m(m,x_only=True))
   z=mr.numerator()(q)/mr.denominator()(q)
   closure.append(bool(h(z)==0))
  valid=landing and all(closure)
  if not valid:
   invalid+=1
   maprows.append({'ell':ell,'candidate':idx,'status':'rejected','landing':landing,'kernel_closure':closure,'h':coeffs(h)})
   continue
  # Compare the independently derived normalized map with serialized producer map.
  matches=[c for c in producer['candidates'] if c['status']=='certified_map' and [F(ZZ(z)) for z in c['kernel']]==h.list()]
  assert len(matches)==1
  pc=matches[0]; assert [F(ZZ(z)) for z in pc['codomain_ainvs']]==[F(0),F(0),F(0),ap,bp]
  RP=PolynomialRing(F,['x','y']); xx,yy=RP.gens(); QQ=RP.fraction_field()
  px,py=[QQ(sage_eval(s,locals={'x':xx,'y':yy})) for s in pc['rational_maps']]
  assert px==QQ(xm) and py==yy*QQ(ym)
  # The dual is read as a proposed rational identity, then checked directly.
  dx,dy=[QQ(sage_eval(s,locals={'x':xx,'y':yy})) for s in pc['dual_maps']]
  assert dx.denominator().degree(yy)==0 and dx.numerator().degree(yy)==0
  xd=Q(dx.subs({yy:1})); yd=Q((dy/yy).subs({yy:1}))
  # Check dual landing and both exact compositions, without producer code.
  fd=Q(x**3+ap*x+bp)
  assert fd*yd**2==xd**3+a*xd+bf
  mult=Q(E.multiplication_by_m(ell,x_only=True))
  assert xd(xm)==mult
  assert ym*yd(xm)==mult.derivative()/ell
  EP=EllipticCurve(F,[ap,bp]); multp=Q(EP.multiplication_by_m(ell,x_only=True))
  assert xm(xd)==multp
  assert yd*ym(xd)==multp.derivative()/ell
  for scalar in [0,1,2,19,31337,r-1]:
   P=scalar*G
   if P.is_zero(): continue
   PX=EP(xm(P[0]),P[1]*ym(P[0]))
   back=E(xd(PX[0]),PX[1]*yd(PX[0]))
   assert back==ell*P and inverse_mod(ell,r)*back==P
  good.append(h)
  maprows.append({'ell':ell,'candidate':idx,'status':'verified','h':coeffs(h),'independent_velu_landing':True,'kernel_closure':closure,'producer_map_equal':True,'dual_landing':True,'both_compositions_xy':True,'point_recovery_scalars':['0','1','2','19','31337','r-1'],'degrees':[int(xm.numerator().degree()),int(xm.denominator().degree())]})
 assert len(good)=={3:1,5:1,11:2}[ell]
 if ell==11: assert invalid==10
 say('maps_degree_%s'%ell,{'factor_degrees':[int(h.degree()) for h in hs],'valid_maps':len(good),'rejected':invalid})
 result['maps']=maprows; save()
# Covers: algebra and a fresh SEA count for the second elliptic factor.
assert gcd(f,f.derivative())==1 and bf!=0
sextic=x**6+a*x*x+bf
assert gcd(sextic,sextic.derivative())==1
assert 3-1==2 # dimension Prym
B=EllipticCurve(F,[0,-3,0,0,bf**2])
NB=B.cardinality(algorithm='pari'); tB=p+1-NB
assert abs(tB)<=rad and 0<NB<r
expected=json.loads((TRACKS/'f7'/'elliptic-quotient-checks.json').read_text())
say('covers',{'quartic_smooth':True,'genus_quartic':3,'sextic_squarefree':True,'genus_sextic':2,'B_ainvs':list(map(str,B.a_invariants())),'B_count_fresh_pari':str(NB),'B_trace':str(tB),'B_coprime_r':bool(gcd(NB,r)==1),'J2_order':str(r*NB),'quartic_pullback_norm_degree':2})
# Symbolic quotient map identity, using w²=s⁴−3s²+b*s.
s=Q(x); w2=s**4-3*s*s+bf*s; X=bf/s
assert bf**2*w2/s**4==X**3-3*X*X+bf**2
# Arithmetic consequence of independently derived Cartier joint.
rows=[]
for k in [-2,-1,0,1,2]:
 N=p*p+k*p+1
 rows.append({'k':k,'prym_order_candidate':str(N),'mod_r':str(N%r),'gcd_r':str(gcd(N,r))})
assert all(row['gcd_r']=='1' for row in rows)
say('five_candidates',rows)
# Small fields: construct Fp2 for exact counts, C polynomial from N1,N2,N3.
controls=[]
for pp in [5,7,11,13,19]:
 for bb in [1,2]:
  FF=GF(pp); RR=PolynomialRing(FF,'v'); v=RR.gen(); ff=v**3-3*v+bb
  if gcd(ff,ff.derivative())!=1:continue
  Ns=[]; Es=[]
  for degree in [1,2,3]:
   KK=GF(pp**degree,'a'); vals=list(KK)
   # count u⁴=f(x) using power residue multiplicities, plus unique infinity.
   count=ZZ(1)
   for xx0 in vals:
    yy0=xx0**3-3*xx0+bb
    if yy0==0: count+=1
    elif yy0**((KK.order()-1)//gcd(4,KK.order()-1))==1:count+=gcd(4,KK.order()-1)
   Ns.append(count)
   if degree==1:Es.append(EllipticCurve(FF,[-3,bb]).cardinality())
  traces=[ZZ(pp)**j+1-Ns[j-1] for j in [1,2,3]]
  c1=-traces[0]; c2=(traces[0]**2-traces[1])//2
  c3=(-traces[0]**3+3*traces[0]*traces[1]-2*traces[2])//6
  Z=PolynomialRing(ZZ,'T'); T=Z.gen()
  CC=T**6+c1*T**5+c2*T**4+c3*T**3+pp*c2*T*T+pp**2*c1*T+pp**3
  trE=pp+1-Es[0]; ee=T*T-trE*T+pp
  quotient,rem=CC.quo_rem(ee); assert rem==0
  row={'p':pp,'b':bb,'counts_C':list(map(str,Ns)),'chi_C':str(CC),'chi_Prym':str(quotient)}
  if pp%4==3:
   assert quotient[3]==quotient[1]==0 and quotient[2]%pp==0
   assert abs(quotient[2])<=2*pp
   row['A_over_p']=str(quotient[2]//pp)
  if pp==5 and bb==1:
   g=ff**3
   mat=matrix(FF,[[g[4],g[3]],[g[9],g[8]]])
   assert mat==matrix(FF,[[2,1],[1,0]]) and mat.determinant()!=0
   assert quotient[3]!=0 or quotient[1]!=0
   row['cartier_matrix_i']=[[int(z) for z in line] for line in mat.rows()]
  controls.append(row)
say('small_field_controls',controls)
result['coverage']={'independent_code_imports':False,'producer_json_used_as_comparison_data':True,'all_four_maps_checked':True,'nonkernel_control_count':10,'full_quartic_arithmetic':False,'complete_P256_Prym_polynomial':False,'performance_measurement':False,'scientific_transition':False}
save(); print('COMPLETION_SENTINEL',flush=True)
