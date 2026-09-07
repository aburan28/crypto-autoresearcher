import math
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
def analytic_gu(N,tau,e4):
    s=tau; g=N-tau
    c=s*(1.0/(N-1))*((tau-1)+(N-tau)*(tau-1)/(N-3))
    for cnt,beta in ((e4,tau-2),(g-e4,tau-1)):
        c+=cnt*(1.0/(N-2))*(beta+tau*(tau-1)/(N-3)+(N-2-beta-tau)*tau/(N-4))
    return 6*c/N
def brute_gu(A,B,p):
    P=pts(A,B,p); N=len(P)
    T2=set(Q for Q in P if add(Q,Q,A,p) is None); tau=len(T2)
    E4=[Q for Q in P if add(add(Q,Q,A,p),add(Q,Q,A,p),A,p) is None]; e4=len(E4)-tau
    key=lambda Q:"O" if Q is None else Q[0]
    w=lambda Q:1 if Q in T2 else 2
    T2k={key(Q) for Q in T2}
    q=0.0
    for P1 in P:
        k1=key(P1); w1=w(P1); acc=0.0
        for P2 in P:
            if key(P2)==k1: continue
            if add(P1,P2,A,p) in T2: acc+=1.0
            else:
                t=tau-(1 if k1 in T2k else 0)-(1 if key(P2) in T2k else 0)
                acc+=t/(N-w1-w(P2))
        q+=acc/(N-w1)
    return N,tau,e4,6*q/N,analytic_gu(N,tau,e4)
for p,A,B in ((1013,11,0),(263,7,0),(599,11,0),(211,0,5)):
    N,tau,e4,br,an=brute_gu(A,B,p)
    print(f"p={p} A={A} B={B} N={N} tau={tau} e4={e4}  gu_brute={br:.12f} gu_analytic={an:.12f} AGREE={abs(br-an)<1e-12}")

print()
# honest power for the REAL (exact) effect sizes
import json
lr_real_cell2 = math.log(0.011665736107823454/0.005006490238643939) - math.log(0.011662034467456778/0.005002776225113788)
print("EXACT log P3 at cell 2 = %+.8e"%lr_real_cell2)
se2 = 0.1865904  # overdispersion-corrected se at 20000 draws
need = (2.8016/abs(lr_real_cell2))     # se needed for 80% power, two-sided alpha=.05
scale = (se2/ (abs(lr_real_cell2)/2.8016))**2
print("draws per curve per arm for 80%% power against the REAL cell-2 effect: %.3g  (vs 20,000 run, vs 209,000 recommended by the prior round)"%(20000*scale))
print("at cell 1 the exact effect is EXACTLY 0 -> no sample size gives power above alpha; every rejection there is by construction a false positive.")
