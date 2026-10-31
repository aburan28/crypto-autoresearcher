"""Signed Frobenius, division-polynomial cycles, and source candidate-list metrics."""
import json,math,pathlib
D=pathlib.Path(__file__).resolve().parent
CONTROLS=[{'name':'scalar_plus','p':7,'A':0,'b':2,'n':9,'ell':3,'expected':[1,1,1]},{'name':'scalar_minus','p':7,'A':0,'b':5,'n':7,'ell':3,'expected':[2,1,1]},{'name':'jordan','p':7,'A':0,'b':1,'n':12,'ell':3,'expected':[3,3,3]},{'name':'nonsplit','p':5,'A':1,'b':1,'n':9,'ell':7,'expected':[48,24,8]}]
def factors(n):
 out=[];d=2
 while d*d<=n:
  if n%d==0:
   out.append(d)
   while n%d==0:n//=d
  d+=1
 if n>1:out.append(n)
 return out

def ordmod(a,l):
 d=l-1
 for q in factors(d):
  while d%q==0 and pow(a,d//q,l)==1:d//=q
 return d

def matmul(a,b,l):return ((a[0]*b[0]+a[1]*b[2])%l,(a[0]*b[1]+a[1]*b[3])%l,(a[2]*b[0]+a[3]*b[2])%l,(a[2]*b[1]+a[3]*b[3])%l)
def matpow(a,n,l):
 b=(1,0,0,1)
 while n:
  if n&1:b=matmul(b,a,l)
  a=matmul(a,a,l);n//=2
 return b

def morder(a,l,mode):
 def good(m):
  if mode=='full':return m==(1,0,0,1)
  if mode=='x':return m in [(1,0,0,1),(l-1,0,0,l-1)]
  return m[1]==m[2]==0 and m[0]==m[3]
 d=l*(l*l-1)
 for q in factors(d):
  while d%q==0 and good(matpow(a,d//q,l)):d//=q
 assert good(matpow(a,d,l));return d

def nullity(m,l,sign):
 a,b,c,d=(m[0]-sign)%l,m[1],m[2],(m[3]-sign)%l
 return 2 if (a,b,c,d)==(0,0,0,0) else (1 if (a*d-b*c)%l==0 else 0)

def profile(a,l,xorder):
 cycles={}
 for d in range(1,xorder+1):
  if xorder%d:continue
  m=matpow(a,d,l);fixed=(l**nullity(m,l,1)+l**nullity(m,l,-1)-2)//2
  exact=fixed-sum(e*c for e,c in cycles.items() if d%e==0);assert exact%d==0
  if exact:cycles[d]=exact//d
 assert sum(d*c for d,c in cycles.items())==(l*l-1)//2
 return [[d,c] for d,c in cycles.items()]

def divisionpoly(p,A,b,l):
 """Odd division polynomial from the exact recurrence."""
 from flint import fmpz_mod_poly_ctx
 C=fmpz_mod_poly_ctx(p);x=C([0,1]);f=x**3+A*x+b;U={0:C([]),1:C([1]),2:C([1]),3:3*x**4+6*A*x*x+12*b*x-A*A,4:2*(x**6+5*A*x**4+20*b*x**3-5*A*A*x*x-4*A*b*x-8*b*b-A**3)}
 def u(k):
  if k not in U:
   m=k//2
   if k%2:
    aa=u(m+2)*u(m)**3;bb=u(m-1)*u(m+1)**3
    U[k]=16*f*f*aa-bb if m%2==0 else aa-16*f*f*bb
   else:U[k]=u(m)*(u(m+2)*u(m-1)**2-u(m-2)*u(m+1)**2)
  return U[k]
 return u(l).monic()

def scalar_on_curve(p,A,b,n,l):
 from flint import fmpz_mod_poly_ctx
 C=fmpz_mod_poly_ctx(p);x=C([0,1]);f=x**3+A*x+b;P=divisionpoly(p,A,b,l);xx=x%P;ff=f%P
 def inv(v):return v.inverse_mod(P)
 def add(P1,P2):
  if P1 is None:return P2
  if P2 is None:return P1
  X,H=P1;Z,J=P2
  if X==Z:
   if H==-J%P:return None
   assert H==J
   S=((3*X*X+A)*inv(2*ff*H%P))%P
  else:S=((J-H)*inv((Z-X)%P))%P
  V=(ff*S*S-X-Z)%P;K=(S*(X-V)-H)%P;return V,K
 lam=(p+1-n)*pow(2,-1,l)%l;assert lam
 ans=None;B=(xx,C([1]));k=lam
 while k:
  if k&1:ans=add(ans,B)
  B=add(B,B);k//=2
 assert ans is not None
 return ans[0]==xx.pow_mod(p,P) and ans[1]==ff.pow_mod((p-1)//2,P)

def candidate_lists(p,t,l,eigs,kind,proj):
 if kind in ('scalar','jordan'):return [1,1,1,1,1,1,1,1]
 if kind=='nonsplit':return [0]*8 # this source skips Elkies-eigenvalue list on this branch
 vals=[[],[],[],[]]
 ds=[d for d in range(2,l) if (l-1)%d==0 and ((pow(p%l,(l-1)//2,l)==1)==(((l-1)//d*(d-1))%2==0))]
 for lam in eigs:
  for known in (True,False):
   cand=[a for a in range(1,(l+1)//2) if ordmod(a*a*pow(p,-1,l)%l,l) in ([proj] if known else ds)]
   if l%4==1:cand=[a for a in cand if pow(a,(l-1)//2,l)==pow(lam,(l-1)//2,l)]
   true=min(lam,l-lam);assert true in cand
   off=0 if known else 2;vals[off].append(len(cand));vals[off+1].append(cand.index(true)+1)
 return [v for z in vals for v in (min(z),max(z))]

def compute(p,A,b,n,l,control=False):
 t=p+1-n;delta=t*t-4*p;disc=delta%l;roots=[a for a in range(l) if (a*a-t*a+p)%l==0]
 if disc:
  scalar=False;kind='split' if roots else 'nonsplit'
 else:
  scalar=scalar_on_curve(p,A,b,n,l) if delta%(l*l)==0 or control else False
  kind='scalar' if scalar else 'jordan'
 mat=(roots[0],0,0,roots[0]) if scalar else (0,(-p)%l,1,t%l)
 full=morder(mat,l,'full');xo=morder(mat,l,'x');proj=morder(mat,l,'projective');pat=profile(mat,l,xo);cost=candidate_lists(p,t,l,roots,kind,proj)
 return {'kind':kind,'full_order':full,'x_order':xo,'projective_order':proj,'factor_degrees':pat,'eigenvalues':roots,'cost':cost,'scalar':int(scalar)}

def controls():
 out=[]
 for r in CONTROLS:
  p,A,b,n,l=[r[k] for k in ('p','A','b','n','ell')];count=1+sum(1 if (v:=(x*x*x+A*x+b)%p)==0 else 2 if pow(v,(p-1)//2,p)==1 else 0 for x in range(p));assert count==n
  z=compute(p,A,b,n,l,True);actual={}
  for pol,multiplicity in divisionpoly(p,A,b,l).factor()[1]:
   assert multiplicity==1;actual[pol.degree()]=actual.get(pol.degree(),0)+1
  assert sorted(map(list,actual.items()))==z['factor_degrees']
  assert [z['full_order'],z['x_order'],z['projective_order']]==r['expected'];out.append(z)
 assert compute(5,1,1,9,7,True)==out[-1]
 def valid_small(p,A,b,n):
  if (4*A**3+27*b*b)%p==0:return False
  return 1+sum(1 if (v:=(x*x*x+A*x+b)%p)==0 else 2 if pow(v,(p-1)//2,p)==1 else 0 for x in range(p))==n
 assert not valid_small(7,0,0,8)
 assert not valid_small(7,0,2,10)
 return {'status':'PASS','records':out,'aa':'PASS','singular_detected':'PASS','wrong_order_detected':'PASS'}

def main():
 ctrl=controls();(D/'matrix-controls.json').write_text(json.dumps(ctrl,indent=2)+'\n');data=json.loads((D/'prior-inputs.json').read_text());cells=[]
 log=(D/'matrix.jsonl').open('w',buffering=1)
 for i,x in enumerate(data['rows']):
  r=x['row'];p,b,n=[int(r[k]) for k in ('p','b','n')]
  for l in data['levels']:
   z=compute(p,-3,b,n,l);expected={'split':2,'nonsplit':0,'jordan':1,'scalar':l+1}[z['kind']];assert expected==x['roots'][str(l)],(i,l,expected,x['roots'][str(l)])
   cells.append({'index':i,'ell':l,**z});log.write(json.dumps(cells[-1],sort_keys=True)+'\n')
 log.close()
 result={'status':'PASS','controls':ctrl,'cells':cells,'cell_count':len(cells),'source':'Python matrix orders and fixed-point inversion; full torsion quotient for ambiguous scalarity.'};(D/'matrix.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('matrix cells',len(cells))
if __name__=='__main__':main()
