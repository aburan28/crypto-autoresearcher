"""Independent integer/polynomial arithmetic for the SEA branch audit."""
from functools import lru_cache

def trim(a):
 a=list(a)
 while a and not a[-1]:a.pop()
 return tuple(a)
def add(a,b,p):return trim([((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0))%p for i in range(max(len(a),len(b)))])
def neg(a,p):return tuple((-x)%p for x in a)
def sub(a,b,p):return add(a,neg(b,p),p)
def scale(a,k,p):return trim([x*k%p for x in a])
def mul(a,b,p):
 if not a or not b:return ()
 c=[0]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]=(c[i+j]+x*y)%p
 return trim(c)
def divrem(a,b,p):
 a=list(trim(a));b=trim(b);assert b;inv=pow(b[-1],-1,p);q=[0]*max(0,len(a)-len(b)+1)
 while len(a)>=len(b):
  k=len(a)-len(b);factor=a[-1]*inv%p;q[k]=factor
  for i,x in enumerate(b):a[k+i]=(a[k+i]-factor*x)%p
  while a and not a[-1]:a.pop()
 return trim(q),tuple(a)
def mod(a,f,p):return divrem(a,f,p)[1]
def monic(a,p):return scale(a,pow(a[-1],-1,p),p) if a else ()
def gcd(a,b,p):
 while b:a,b=b,mod(a,b,p)
 return monic(a,p)
def derivative(a,p):return trim([i*a[i]%p for i in range(1,len(a))])
def power(a,n,f,p):
 r=(1,);a=mod(a,f,p)
 while n:
  if n&1:r=mod(mul(r,a,p),f,p)
  n>>=1
  if n:a=mod(mul(a,a,p),f,p)
 return r
def evaluate(a,x,p):
 r=0
 for c in reversed(a):r=(r*x+c)%p
 return r

def division_remainder(ell,A,B,f,p):
 """Normalized division polynomials: even psi_n divided by2y."""
 f=monic(f,p)
 def M(a,b):return mod(mul(a,b,p),f,p)
 def P(a,n):return power(a,n,f,p)
 g=mod((B,A,0,1),f,p);g2=scale(M(g,g),16,p)
 @lru_cache(None)
 def psi(n):
  if n==0:return ()
  if n in (1,2):return (1,)
  if n==3:return mod(((-A*A)%p,12*B%p,6*A%p,0,3),f,p)
  if n==4:return mod(scale(((-8*B*B-A*A*A)%p,-4*A*B%p,-5*A*A%p,20*B%p,5*A%p,0,1),2,p),f,p)
  m=n//2
  if n%2:
   left=M(psi(m+2),P(psi(m),3));right=M(psi(m-1),P(psi(m+1),3))
   if m%2:right=M(g2,right)
   else:left=M(g2,left)
   return sub(left,right,p)
  return M(psi(m),sub(M(psi(m+2),P(psi(m-1),2)),M(psi(m-2),P(psi(m+1),2)),p))
 return psi(ell)

def velu(A,B,f,p):
 f=monic(f,p);d=len(f)-1;c1=f[-2] if d>=1 else 0;c2=f[-3] if d>=2 else 0;c3=f[-4] if d>=3 else 0
 s1=-c1;s2=c1*c1-2*c2;s3=-c1*c1*c1+3*c1*c2-3*c3
 return ((A-10*(3*s2+d*A))%p,(B-14*(5*s3+3*A*s1+2*d*B))%p)
def j_invariant(A,B,p):return 1728*4*pow(A,3,p)*pow((4*pow(A,3,p)+27*B*B)%p,-1,p)%p
def isomorphic(A,B,C,D,p):
 if not A or not B or not C or not D:return None
 r=C*pow(A,-1,p)%p;s=D*pow(B,-1,p)%p;u2=s*pow(r,-1,p)%p
 return pow(u2,2,p)==r and pow(u2,3,p)==s and pow(u2,(p-1)//2,p)==1

def arithmetic_controls():
 # Ell=3, p101, P=(0,1) on y²=x³+1: kernel x, quotient y²=x³-27.
 assert division_remainder(3,0,1,(0,1),101)==()
 assert velu(0,1,(0,1),101)==(0,74)
 # A non-kernel must be rejected by the same division-polynomial arithmetic.
 assert division_remainder(3,2,1,(0,1),101)!=( )
 # Independent direct scalar arithmetic verifies the known3-torsion point.
 x,y=0,1;s=3*x*x*pow(2*y,-1,101)%101;x2=(s*s-2*x)%101;y2=(s*(x-x2)-y)%101
 assert (x2,y2)==(0,100)
 for p in [101,103]:
  a=(1,2,1);b=(3,1);q,r=divrem(mul(a,b,p),a,p);assert q==b and not r
 return {'status':'PASS','explicit_order3_kernel_and_velu':True,'nonkernel_refused':True,'polynomial_division_controls':2}
