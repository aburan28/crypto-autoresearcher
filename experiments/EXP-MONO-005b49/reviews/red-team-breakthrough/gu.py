import json, math, random
exec(open("/dev/stdin").read()) if False else None
def qr(a,p):
    a%=p
    if a==0: return 0
    return 1 if pow(a,(p-1)//2,p)==1 else -1
def neg(P,p): return None if P is None else (P[0],(-P[1])%p)
def add(P,Q,A,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        lam=((3*x1*x1+A)*pow((2*y1)%p,p-2,p))%p
    else:
        lam=((y2-y1)*pow((x2-x1)%p,p-2,p))%p
    x3=(lam*lam-x1-x2)%p
    return (x3%p,(lam*(x1-x3)-y1)%p)
def points(A,B,p):
    pts=[None]
    for x in range(p):
        f=(x*x*x+A*x+B)%p
        c=qr(f,p)
        if c==0: pts.append((x,0))
        elif c==1:
            for y in range(1,(p//2)+1):
                if (y*y)%p==f:
                    pts.append((x,y)); pts.append((x,(p-y)%p)); break
    return pts

def analytic_gu(N,tau,e4):
    """E[K_gu] under the SEQUENTIAL distinct-key rejection sampler."""
    s=tau; g=N-tau
    # P1 type S
    contribS = s*(1.0/(N-1))*((tau-1) + (N-tau)*(tau-1)/(N-3))
    # P1 type G, split by whether P1 in E[4]\E[2]
    tot=0.0
    for (cnt,beta) in ((e4,tau-2),(g-e4,tau-1)):
        tot += cnt*(1.0/(N-2))*(beta + tau*(tau-1)/(N-3) + (N-2-beta-tau)*tau/(N-4))
    q=(contribS+tot)/N
    return 6*q

def brute_gu(A,B,p,P):
    """Exact by enumeration over (P1,P2); P3 handled in closed form."""
    N=len(P)
    T2=set()
    for Q in P:
        if add(Q,Q,A,p) is None: T2.add(Q)
    tau=len(T2)
    def key(Q): return "O" if Q is None else Q[0]
    def w(Q): return 1 if Q in T2 else 2
    T2keys={key(Q) for Q in T2}
    q=0.0
    for P1 in P:
        k1=key(P1); w1=w(P1); acc=0.0
        for P2 in P:
            if key(P2)==k1: continue
            w2=w(P2)
            b = add(P1,P2,A,p) in T2
            if b: acc+=1.0
            else:
                t=tau-(1 if k1 in T2keys else 0)-(1 if key(P2) in T2keys else 0)
                acc+= t/(N-w1-w2)
        q += acc/(N-w1)
    return 6*q/N

def divisors(n):
    d=[];i=1
    while i*i<=n:
        if n%i==0:
            d.append(i)
            if i!=n//i: d.append(n//i)
        i+=1
    return sorted(d)

CUR=[("cell1_ord",617,340,362),("cell1_cm",617,69,0),
     ("cell2_ord",3541,577,1628),("cell2_cm",3541,0,2728)]
res={}
for tag,p,A,B in CUR:
    P=points(A,B,p); N=len(P)
    T2=[Q for Q in P if add(Q,Q,A,p) is None]; tau=len(T2)
    E4=[Q for Q in P if add(add(Q,Q,A,p),add(Q,Q,A,p),A,p) is None]
    e4=len(E4)-tau
    an=analytic_gu(N,tau,e4)
    r=dict(N=N,tau=tau,nE4=len(E4),e4=e4,E_gu_analytic=an)
    if p==617:
        r["E_gu_brute"]=brute_gu(A,B,p,P)
    res[tag]=r
    print(tag,json.dumps(r))
json.dump(res,open("/tmp/claude/gu_out.json","w"),indent=1)
