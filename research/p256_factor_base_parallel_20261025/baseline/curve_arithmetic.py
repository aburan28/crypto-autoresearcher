from dataclasses import dataclass

def sqrt_mod(a,p):
    a%=p
    if not a:return 0
    if pow(a,(p-1)//2,p)!=1:return None
    if p%4==3:
        y=pow(a,(p+1)//4,p);return min(y,p-y)
    q,s=p-1,0
    while q%2==0:s+=1;q//=2
    z=2
    while pow(z,(p-1)//2,p)!=p-1:z+=1
    c,x,t,m=pow(z,q,p),pow(a,(q+1)//2,p),pow(a,q,p),s
    while t!=1:
        i,t2=1,t*t%p
        while t2!=1:i+=1;t2=t2*t2%p
        b=pow(c,1<<(m-i-1),p)
        x,t,c,m=x*b%p,t*b*b%p,b*b%p,i
    return min(x,p-x)

@dataclass(frozen=True)
class Curve:
    p:int
    a:int
    b:int
    def rhs(self,x):return (x*x*x+self.a*x+self.b)%self.p
    def neg(self,P):return None if P is None else (P[0],-P[1]%self.p)
    def add(self,P,Q):
        if P is None:return Q
        if Q is None:return P
        x,y=P;u,v=Q;p=self.p
        if x==u:
            if (y+v)%p==0:return None
            slope=(3*x*x+self.a)*pow(2*y,-1,p)%p
        else:slope=(v-y)*pow((u-x)%p,-1,p)%p
        w=(slope*slope-x-u)%p
        return w,(slope*(x-w)-y)%p
    def mul(self,k,P):
        if k<0:return self.mul(-k,self.neg(P))
        R=None
        while k:
            if k&1:R=self.add(R,P)
            P=self.add(P,P);k>>=1
        return R
    def lift(self,x):
        y=sqrt_mod(self.rhs(x),self.p)
        return None if y is None else (x%self.p,y)
