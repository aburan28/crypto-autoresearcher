# GF(2^4) with x^4+x+1 (0x13); MDS check for candidate MixColumns rows.
from itertools import combinations
P=0x13
def m(a,b):
    r=0
    while b:
        if b&1: r^=a
        b>>=1; a<<=1
        if a&0x10: a^=P
    return r
def inv(a):
    if a==0: return 0
    r=1
    for _ in range(14): r=m(r,a)
    return r
def det(M):
    # Gaussian elimination over GF(2^4)
    n=len(M); M=[row[:] for row in M]; d=1
    for c in range(n):
        p=None
        for r in range(c,n):
            if M[r][c]: p=r;break
        if p is None: return 0
        if p!=c: M[c],M[p]=M[p],M[c]
        d=m(d,M[c][c]); ic=inv(M[c][c])
        for r in range(c+1,n):
            if M[r][c]:
                f=m(M[r][c],ic)
                for k in range(c,n): M[r][k]^=m(f,M[c][k])
    return d
def circ(row):
    return [[row[(j-i)%4] for j in range(4)] for i in range(4)]
def is_mds(M):
    bad=[]
    for k in (1,2,3,4):
        for rs in combinations(range(4),k):
            for cs in combinations(range(4),k):
                sub=[[M[r][c] for c in cs] for r in rs]
                if det(sub)==0: bad.append((rs,cs,k))
    return (len(bad)==0, bad)
def minv(M):
    n=4; A=[M[i][:]+[1 if i==j else 0 for j in range(n)] for i in range(n)]
    for c in range(n):
        p=[r for r in range(c,n) if A[r][c]][0]
        A[c],A[p]=A[p],A[c]
        ic=inv(A[c][c]); A[c]=[m(ic,v) for v in A[c]]
        for r in range(n):
            if r!=c and A[r][c]:
                f=A[r][c]
                A[r]=[A[r][k]^m(f,A[c][k]) for k in range(2*n)]
    return [row[n:] for row in A]
for row in [(2,3,1,1),(1,2,3,1),(5,2,1,1),(1,2,4,8),(3,1,1,2)]:
    M=circ(list(row))
    ok,bad=is_mds(M)
    print("row",row,"MDS" if ok else "NOT MDS (%d singular submatrices)"%len(bad))
    if ok:
        I=minv(M)
        print("   inverse rows:",[["%x"%v for v in r] for r in I])
        ok2,_=is_mds(I); print("   inverse MDS:",ok2, " zero coeff in inverse:", any(v==0 for r in I for v in r))
    else:
        print("   first singular:",bad[0])
