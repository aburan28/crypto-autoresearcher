import math,json
def qr(a,p):
    a%=p
    return 0 if a%p==0 else (1 if pow(a,(p-1)//2,p)==1 else -1)
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
                if (y*y)%p==f: pts.append((x,y)); pts.append((x,(p-y)%p)); break
    return pts
def brute_tr(A,B,p):
    P=points(A,B,p); N=len(P)
    T2=[Q for Q in P if add(Q,Q,A,p) is None]; tau=len(T2)
    E4=[Q for Q in P if (lambda D: add(D,D,A,p) is None)(add(Q,Q,A,p))]
    e4=len(E4)-tau
    FB=sorted({Q[0] for Q in P if Q is not None and (Q[0]**3+A*Q[0]+B)%p!=0})
    n=len(FB)
    lift={}
    for Q in P:
        if Q is None: continue
        if Q[0] in FB and (Q[0] not in lift or Q[1]<lift[Q[0]][1]): lift[Q[0]]=Q
    tot=0
    for T in T2:
        if T is None: continue
        for x in FB:
            if add(lift[x],T,A,p)[0]!=x: tot+=1
    Ebrute = 3*(tot/2)/(n*(n-1)/2) if n>1 else 0.0
    F=e4/2
    Eform = 3*((tau-1)*n-F)/(n*(n-1)) if (tau>1 and n>1) else 0.0
    return dict(N=N,tau=tau,nE4=len(E4),e4=e4,n=n,F_formula=F,
                E_brute=Ebrute,E_formula=Eform,agree=abs(Ebrute-Eform)<1e-14)
# test on a spread of curves incl tau=2 and tau=1
tests=[(617,340,362),(617,69,0),(3541,577,1628),(3541,0,2728),
       (101,3,7),(103,5,11),(191,2,9),(421,17,3),(569,4,13),(211,0,5),(211,7,0),
       (307,1,1),(457,0,3),(1009,2,2),(1009,0,7),(1013,11,0)]
for p,A,B in tests:
    if (4*pow(A,3,p)+27*pow(B,2,p))%p==0: continue
    r=brute_tr(A,B,p)
    print(f"p={p:5d} A={A:4d} B={B:4d} tau={r['tau']} #E4={r['nE4']:3d} F={r['F_formula']:.1f} "
          f"brute={r['E_brute']:.10f} formula={r['E_formula']:.10f} AGREE={r['agree']}")
