# Toy prime-field curve: does a COORDINATE-DERIVED statistic sustain propagation?
def curve_points(p,a,b):
    pts=[None]  # None = point at infinity
    for x in range(p):
        rhs=(x*x*x+a*x+b)%p
        for y in range(p):
            if (y*y)%p==rhs: pts.append((x,y))
    return pts
def add(P,Q,p,a):
    if P is None: return Q
    if Q is None: return P
    if P[0]==Q[0] and (P[1]+Q[1])%p==0: return None
    if P==Q: lam=(3*P[0]*P[0]+a)*pow(2*P[1],p-2,p)%p
    else:    lam=(Q[1]-P[1])*pow((Q[0]-P[0])%p,p-2,p)%p
    x=(lam*lam-P[0]-Q[0])%p; y=(lam*(P[0]-x)-P[1])%p
    return (x,y)

def q_maj_from_labels(lab, N, s, addtab):
    F=[[] for _ in range(s)]
    for k in range(N): F[lab[k]].append(k)
    tot=0
    for i in range(s):
        for j in range(s):
            if not F[i] or not F[j]: continue
            cnt=[0]*s
            for u in F[i]:
                for v in F[j]: cnt[lab[(u+v)%N]]+=1
            tot+=max(cnt)
    return tot/N**2

for (p,a,b) in [(101,3,5),(103,2,7),(107,1,1)]:
    pts=curve_points(p,a,b)
    n=len(pts)
    # find a generator of a large cyclic subgroup: use full group if cyclic
    # build orbit of a point
    best=None
    for P0 in pts[1:]:
        orb=[]; R=None
        for _ in range(n+1):
            R=add(R,P0,p,a); orb.append(R)
            if R is None: break
        if best is None or len(orb)>len(best[1]): best=(P0,orb)
    P0,orb=best; N=len(orb)
    if N<20: continue
    # orb[k-1] = k*P0 for k=1..N, orb[N-1]=None (identity) => index k mod N
    kP={}
    for idx,R in enumerate(orb): kP[(idx+1)%N]=R
    for s in [2,3,4,5]:
        # coordinate-derived statistic: bucket by x-coordinate
        lab=[0]*N
        for k in range(N):
            R=kP[k]
            lab[k]= 0 if R is None else min(R[0]*s//p, s-1)
        q=q_maj_from_labels(lab,N,s,None)
        # DL-interval statistic (NOT efficiently computable) for comparison
        labI=[min(k*s//N,s-1) for k in range(N)]
        qI=q_maj_from_labels(labI,N,s,None)
        print(f"p={p} N={N:3d} s={s}  baseline 1/s={1/s:.3f} | x-bucket q={q:.3f} | DL-interval q={qI:.3f}")
    print()
