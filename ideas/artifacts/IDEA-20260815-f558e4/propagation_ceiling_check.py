import itertools, random
random.seed(7)

def fibers_from_labels(lab, N, s):
    F=[[] for _ in range(s)]
    for x in range(N): F[lab[x]].append(x)
    return F

def q_strict(lab,N,s):
    """fraction of (R,R') pairs whose sum-fiber is FORCED by (fiber(R),fiber(R'))"""
    F=fibers_from_labels(lab,N,s); tot=0
    for i in range(s):
        for j in range(s):
            if not F[i] or not F[j]: continue
            img={lab[(a+b)%N] for a in F[i] for b in F[j]}
            if len(img)==1: tot+=len(F[i])*len(F[j])
    return tot/N**2

def q_maj(lab,N,s):
    """best-F propagation probability: majority vote per fiber-pair"""
    F=fibers_from_labels(lab,N,s); tot=0
    for i in range(s):
        for j in range(s):
            if not F[i] or not F[j]: continue
            cnt=[0]*s
            for a in F[i]:
                for b in F[j]: cnt[lab[(a+b)%N]]+=1
            tot+=max(cnt)
    return tot/N**2

for N,s in [(11,2),(11,3),(23,2),(23,3),(23,4),(31,3),(37,4),(41,5)]:
    # balanced interval partition (AP structure)
    lab_int=[min(x*s//N, s-1) for x in range(N)]
    # random balanced partition
    order=list(range(N)); random.shuffle(order)
    lab_rand=[0]*N
    for idx,x in enumerate(order): lab_rand[x]=min(idx*s//N,s-1)
    # best random over trials
    best=0; bestlab=None
    for _ in range(300):
        o=list(range(N)); random.shuffle(o)
        L=[0]*N
        for idx,x in enumerate(o): L[x]=min(idx*s//N,s-1)
        v=q_maj(L,N,s)
        if v>best: best,bestlab=v,L
    print(f"N={N:3d} s={s}  1/s={1/s:.4f} | strict(interval)={q_strict(lab_int,N,s):.4f} "
          f"strict(rand)={q_strict(lab_rand,N,s):.4f} | maj(interval)={q_maj(lab_int,N,s):.4f} "
          f"maj(rand)={q_maj(lab_rand,N,s):.4f} maj(best-of-300rand)={best:.4f}")
