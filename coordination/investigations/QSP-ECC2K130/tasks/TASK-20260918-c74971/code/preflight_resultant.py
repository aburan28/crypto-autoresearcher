import time, random
# F_{2^n} = F_2[z]/(f), bit-packed
def mkfield(n, modpoly):
    M=modpoly
    def mul(a,b):
        r=0
        while b:
            if b&1: r^=a
            b>>=1; a<<=1
            if a>>n & 1: a^=M
        return r
    def inv(a):
        # Fermat: a^(2^n - 2)
        r=1; e=(1<<n)-2; base=a
        while e:
            if e&1: r=mul(r,base)
            base=mul(base,base); e>>=1
        return r
    return mul, inv

def sylvester_res(fc, gc, mul, inv, n):
    """fc, gc: coefficient lists in X (index = power), entries in F_{2^n}. Returns det of Sylvester matrix."""
    df=len(fc)-1; dg=len(gc)-1
    N=df+dg
    if N==0: return 1
    Mx=[[0]*N for _ in range(N)]
    for i in range(dg):
        for j,c in enumerate(fc): Mx[i][i+df-j]=c
    for i in range(df):
        for j,c in enumerate(gc): Mx[dg+i][i+dg-j]=c
    # Gaussian elimination over F_{2^n}
    det=1
    for col in range(N):
        piv=None
        for r in range(col,N):
            if Mx[r][col]: piv=r; break
        if piv is None: return 0
        if piv!=col: Mx[col],Mx[piv]=Mx[piv],Mx[col]
        det=mul(det,Mx[col][col])
        ic=inv(Mx[col][col])
        for r in range(col+1,N):
            if Mx[r][col]:
                fac=mul(Mx[r][col],ic)
                for c in range(col,N):
                    if Mx[col][c]: Mx[r][c]^=mul(fac,Mx[col][c])
    return det

for n,modp in [(17,(1<<17)|(1<<3)|1),(23,(1<<23)|(1<<5)|1),(29,(1<<29)|(1<<2)|1)]:
    mul,inv=mkfield(n,modp)
    random.seed(20260917)
    # two bivariate polys: treat as polys in X whose coefficients are polys in Y -> here just field elts (m=2 eliminant shape)
    for deg in (4,8,16):
        fc=[random.randrange(1,1<<n) for _ in range(deg+1)]
        gc=[random.randrange(1,1<<n) for _ in range(deg+1)]
        t=time.time(); r=sylvester_res(fc,gc,mul,inv,n); el=time.time()-t
        print(f'n={n:3d}  deg_X={deg:3d}  Sylvester {2*deg}x{2*deg}  res!=0:{r!=0}  {el:.3f}s')
