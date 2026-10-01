"""Numerically test CCG Prop 4.13:  d_reg(Weil(F)) == n*d_reg(F) - n + 1.

F_2^n as F_2[a]/(mod).  Everything is linear algebra over F_2 / over K.
d_reg(F) = min{ e : (F^top)_e == R_e }, computed as a rank condition.
"""
import itertools, random
from itertools import combinations_with_replacement as cwr

# ---------- F_{2^n} arithmetic, elements = int bitmasks ----------
MODS = {1:0b10, 2:0b111, 3:0b1011, 4:0b10011, 5:0b100101}  # x^n + ... irreducible over F2

def fmul(a,b,n):
    m=MODS[n]; r=0
    while b:
        if b&1: r^=a
        b>>=1; a<<=1
        if a>>n & 1: a^=m
    return r

# ---------- monomials of degree d in v vars as exponent tuples ----------
def mons(v,d):
    out=[]
    for c in cwr(range(v),d):
        e=[0]*v
        for i in c: e[i]+=1
        out.append(tuple(e))
    return sorted(set(out))

def madd(a,b): return tuple(x+y for x,y in zip(a,b))

# ---------- d_reg of a homogeneous-top system ----------
def dreg(top, v, K_n, maxdeg=14):
    """top: list of dicts {monomial: coeff-in-F_{2^n}} homogeneous.
       Returns min e with (top)_e == R_e, over the field F_{2^n}."""
    for e in range(1, maxdeg+1):
        target = mons(v,e)
        idx = {m:i for i,m in enumerate(target)}
        rows=[]
        for g in top:
            dg = max(sum(m) for m in g)
            if dg>e: continue
            for mm in mons(v, e-dg):
                row=[0]*len(target)
                for m,c in g.items():
                    row[idx[madd(m,mm)]] ^= c
                rows.append(row)
        # rank over F_{2^n}: gaussian elimination
        r=0; ncols=len(target)
        for col in range(ncols):
            piv=None
            for i in range(r,len(rows)):
                if rows[i][col]: piv=i; break
            if piv is None: continue
            rows[r],rows[piv]=rows[piv],rows[r]
            inv=None
            # find inverse of rows[r][col] in F_{2^n}
            a=rows[r][col]
            for cand in range(1,1<<K_n):
                if fmul(a,cand,K_n)==1: inv=cand; break
            rows[r]=[fmul(x,inv,K_n) for x in rows[r]]
            for i in range(len(rows)):
                if i!=r and rows[i][col]:
                    f=rows[i][col]
                    rows[i]=[x ^ fmul(f,y,K_n) for x,y in zip(rows[i],rows[r])]
            r+=1
            if r==ncols: break
        if r==len(target): return e
    return None

def topof(poly):
    d=max(sum(m) for m in poly)
    return {m:c for m,c in poly.items() if sum(m)==d}

# ---------- Weil restriction ----------
def weil(F, m_vars, n):
    """F: list of dicts over K=F_{2^n} in m_vars vars.  Returns list over F_2 in m_vars*n vars.
       x_i = sum_j a^j * x_{i,j}."""
    V = m_vars*n
    def vidx(i,j): return i*n+j
    out=[]
    for f in F:
        # expand f(x_1..x_m) with x_i replaced; accumulate dict monomial -> K coeff
        acc={}
        for mon,c in f.items():
            # product over i of (sum_j a^j x_ij)^{mon[i]}
            terms=[({tuple(0 for _ in range(V))}, {tuple(0 for _ in range(V)): 1})]
            cur={tuple(0 for _ in range(V)): c}
            for i in range(m_vars):
                for _ in range(mon[i]):
                    nxt={}
                    for mm,cc in cur.items():
                        for j in range(n):
                            e=list(mm); e[vidx(i,j)]+=1
                            aj=1
                            for _k in range(j): aj=fmul(aj,2,n)  # a^j  (a = bit 1<<1 = 2)
                            key=tuple(e)
                            nxt[key]=nxt.get(key,0) ^ fmul(cc,aj,n)
                    cur=nxt
            for mm,cc in cur.items():
                acc[mm]=acc.get(mm,0)^cc
        # split acc (K-valued) into n F_2-valued components w.r.t. basis 1,a,..,a^{n-1}
        for j in range(n):
            comp={}
            for mm,cc in acc.items():
                bit=(cc>>j)&1
                if bit: comp[mm]=1
            if comp: out.append(comp)
    return out

def run(name, F, m_vars, n):
    """Returns True/False for a real comparison, or None when the HYPOTHESIS FAILS.

    (F^top)_d = R_d for d >> 0 is a hypothesis of CCG Prop 4.13, not a
    formality: it fails for underdetermined systems, where the top part never
    fills the ring and d_reg is undefined. Such a cell is NOT a confirmation.
    An earlier version of this function returned `dW == pred` there, which is
    None == None, i.e. it scored a vacuous MATCH -- exactly the trap the
    null-object discipline exists to prevent.  It is now refused explicitly.
    """
    top=[topof(f) for f in F]
    dF=dreg(top, m_vars, n)
    if dF is None:
        print(f"{name}: n={n} m={m_vars} | HYPOTHESIS FAILS over K ((F^top)_d never fills R_d) "
              f"-- d_reg undefined, formula does not apply, NOT a confirmation")
        return None
    W=weil(F,m_vars,n)
    Wtop=[topof(g) for g in W]
    dW=dreg(Wtop, m_vars*n, 1)
    pred = n*dF - n + 1
    ok = "MATCH" if dW==pred else "MISMATCH"
    print(f"{name}: n={n} m={m_vars} | d_reg(F)={dF}  d_reg(Weil F)={dW}  predicted={pred}  -> {ok}")
    return dW==pred

random.seed(11)
results=[]
# one variable, degree 2 and 3, n=2,3
for n in (2,3):
    for deg in (2,3):
        f={(deg,):1, (1,): 2, (0,):1}   # x^deg + a*x + 1
        results.append(run(f"1var deg{deg}", [f], 1, n))
# two variables (closer to a summation-polynomial shape), n=2
f2={(2,0):1,(1,1):2,(0,2):1,(1,0):1,(0,0):1}
results.append(run("2var quadratic", [f2], 2, 2))
f3={(2,1):1,(1,2):2,(1,1):1,(0,0):1}
results.append(run("2var cubic-ish", [f3], 2, 2))
print()
real=[r for r in results if r is not None]
skipped=len(results)-len(real)
print(f"non-vacuous cases: {len(real)}, hypothesis-failure cells refused: {skipped}, all match: {all(real) if real else 'n/a'}")

print("\n=== determined multivariate cases (hypothesis actually holds) ===")
res2=[]
def run2(name,F,m,n):
    top=[topof(f) for f in F]
    dF=dreg(top,m,n)
    if dF is None:
        print(f"{name}: n={n} m={m} | HYPOTHESIS FAILS over K ((F^top)_d never fills R_d) -- formula does not apply")
        return None
    W=weil(F,m,n); dW=dreg([topof(g) for g in W], m*n, 1)
    pred=n*dF-n+1
    print(f"{name}: n={n} m={m} | d_reg(F)={dF}  d_reg(Weil F)={dW}  predicted={pred}  -> {'MATCH' if dW==pred else 'MISMATCH'}")
    return dW==pred

# 2 equations in 2 variables over F_4 and F_8 -> top part can fill R_d
g1={(2,0):1,(1,1):2,(0,1):1,(0,0):1}
g2={(0,2):1,(1,0):3,(0,0):1}
res2.append(run2("2x2 quadratic", [g1,g2], 2, 2))
res2.append(run2("2x2 quadratic", [g1,g2], 2, 3))
h1={(2,0):1,(1,1):2,(0,0):1}
h2={(1,1):1,(0,2):3,(1,0):1}
res2.append(run2("2x2 quadratic b", [h1,h2], 2, 2))
# 3 equations in 3 variables, n=2
k1={(2,0,0):1,(0,1,0):1,(0,0,0):1}
k2={(0,2,0):1,(0,0,1):2,(0,0,0):1}
k3={(0,0,2):1,(1,0,0):3,(0,0,0):1}
res2.append(run2("3x3 quadratic", [k1,k2,k3], 3, 2))
real=[r for r in res2 if r is not None]
print(f"\nnon-vacuous determined cases: {len(real)}, all match: {all(real) if real else 'n/a'}")
