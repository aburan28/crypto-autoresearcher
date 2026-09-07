import math
def fund(D):
    f=1
    for q in range(2,int(abs(D)**0.5)+2):
        while D%(q*q)==0 and ((D//(q*q))%4 in (0,1)):
            D//=q*q; f*=q
    return D,f
for p,N,lab in ((617,580,"cell 1 (CM variant j=1728)"),(3541,3600,"cell 2 (CM variant j=0)")):
    t=p+1-N; D=t*t-4*p; d,f=fund(D)
    print(f"{lab}: p={p} N={N} t={t}  t^2-4p={D} = {f}^2 * {d}  -> CM field Q(sqrt({d})) ; crater j = "
          + ("1728" if d==-4 else ("0" if d==-3 else "other")))
# supersingular sanity check of the exact formula
def qr(a,p):
    a%=p
    return 0 if a==0 else (1 if pow(a,(p-1)//2,p)==1 else -1)
def add(P,Q,A,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        lam=((3*x1*x1+A)*pow((2*y1)%p,p-2,p))%p
    else: lam=((y2-y1)*pow((x2-x1)%p,p-2,p))%p
    x3=(lam*lam-x1-x2)%p
    return (x3%p,(lam*(x1-x3)-y1)%p)
def pts(A,B,p):
    r=[None]
    for x in range(p):
        f=(x*x*x+A*x+B)%p; c=qr(f,p)
        if c==0: r.append((x,0))
        elif c==1:
            for y in range(1,(p//2)+1):
                if (y*y)%p==f: r.append((x,y)); r.append((x,(p-y)%p)); break
    return r
for p,A,B in ((467,0,5),(479,0,3),(263,7,0),(599,11,0)):
    P=pts(A,B,p); N=len(P)
    T2=[Q for Q in P if add(Q,Q,A,p) is None]; tau=len(T2)
    E4=[Q for Q in P if add(add(Q,Q,A,p),add(Q,Q,A,p),A,p) is None]
    FB=sorted({Q[0] for Q in P if Q is not None and (Q[0]**3+A*Q[0]+B)%p!=0}); n=len(FB)
    lift={}
    for Q in P:
        if Q is None: continue
        if Q[0] in FB and (Q[0] not in lift or Q[1]<lift[Q[0]][1]): lift[Q[0]]=Q
    tot=sum(1 for T in T2 if T is not None for x in FB if add(lift[x],T,A,p)[0]!=x)
    br=3*(tot/2)/(n*(n-1)/2) if n>1 else 0.0
    F=(len(E4)-tau)/2
    fo=3*((tau-1)*n-F)/(n*(n-1)) if tau>1 else 0.0
    print(f"p={p} A={A} B={B} N={N} (p+1={p+1}) supersingular={N==p+1} tau={tau} #E4={len(E4)} brute={br:.12f} formula={fo:.12f} AGREE={abs(br-fo)<1e-14}")
