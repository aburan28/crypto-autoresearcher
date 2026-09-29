"""Verify the CLAIMED WITNESS mu = x_R^{-2} for the degree-2 fall.

Claim: for every n, every F_2-subspace V = <v_1..v_n'> of F_{2^n}, and every
x_R != 0, the F_2-linear functional Tr(mu * -) with mu = x_R^{-2} annihilates
the entire degree-2 part of the Weil-descended S_3(x_1,x_2,x_R) system.
Hence a degree fall exists at degree 2 and d_ff <= 2, uniformly.

UNIQUENESS OF THE ANNIHILATOR IS FALSE, AND THIS SCRIPT DISPROVES IT.
Do not read the count column as confirming uniqueness. When the products
v_j v_k span a PROPER subspace of F_{2^n} -- which happens whenever n' is small
relative to n -- accidental annihilators exist: this script finds 7 at
n=9, n'=3 and 63 at n=9, n'=2, and its negative control finds 14/106
non-witness mu that also annihilate. Uniqueness returns only once the products
span enough of the field.

What IS unique, for every n and every x_R != 0, is the nonzero root of
mu^(1/2) + mu*x_R = 0, namely mu = x_R^{-2}: squaring gives
mu*(1 + mu*x_R^2) = 0. That is a statement about the DEGENERACY EQUATION, not
about the annihilating functional, and only the former may be formalised.
See formal/targets/semaev-s3-degree2-fall-witness.yaml, which states the same
restriction, and FFD_SEMAEV_MEASUREMENT1 section 3a.
"""
import random, itertools
MODS={2:0b111,3:0b1011,4:0b10011,5:0b100101,6:0b1000011,7:0b10000011,
      8:0b100011101,9:0b1000010001,10:0b10000001001}
def mul(a,b,n):
    m=MODS[n]; r=0
    while b:
        if b&1: r^=a
        b>>=1; a<<=1
        if (a>>n)&1: a^=m
    return r
def inv(a,n):
    for c in range(1,1<<n):
        if mul(a,c,n)==1: return c
    raise ZeroDivisionError
def sq(a,n): return mul(a,a,n)
def tr(a,n):
    # absolute trace to F_2: sum_{i=0}^{n-1} a^{2^i}
    s=0; x=a
    for _ in range(n):
        s^=x; x=sq(x,n)
    return s&1   # element of F_2 (trace lands in F_2 => 0 or 1 as field elt)

def quad_coeffs(basis,xR,n):
    """c_{jk} = (v_j v_k)^2 + v_j v_k * xR  for all j,k -- the degree-2 coefficients."""
    out=[]
    for vj in basis:
        for vk in basis:
            t=mul(vj,vk,n)
            out.append(sq(t,n) ^ mul(t,xR,n))
    return out

def indep(basis,n):
    rows=list(basis); r=0
    for bit in range(n):
        p=None
        for i in range(r,len(rows)):
            if (rows[i]>>bit)&1: p=i;break
        if p is None: continue
        rows[r],rows[p]=rows[p],rows[r]
        for i in range(len(rows)):
            if i!=r and ((rows[i]>>bit)&1): rows[i]^=rows[r]
        r+=1
    return r==len(basis)

random.seed(3)
print("n  n'   x_R   claimed mu=x_R^-2 kills deg-2 part? | #mu that do (NOT expected to be 1; see docstring)")
print("-"*88)
allok=True; alluniq=True
for n in range(2,10):
    for nprime in range(1,min(n,5)+1):
        for trial in range(6):
            rng=random.Random(n*97+nprime*13+trial)
            for _ in range(200):
                basis=[rng.randrange(1,1<<n) for _ in range(nprime)]
                if indep(basis,n): break
            else: continue
            xR=rng.randrange(1,1<<n)
            cs=quad_coeffs(basis,xR,n)
            mu=inv(sq(xR,n),n)                       # x_R^{-2}
            ok = all(tr(mul(mu,c,n),n)==0 for c in cs)
            good=[m for m in range(1,1<<n) if all(tr(mul(m,c,n),n)==0 for c in cs)]
            uniq = (good==[mu])
            allok &= ok; alluniq &= uniq
            if trial==0:
                print(f"{n}  {nprime}   {xR:3}   {'YES' if ok else 'NO ':>3}                              | "
                      f"{len(good)} {'(unique, = x_R^-2)' if uniq else '(NOT unique: '+str(good[:4])+')'}")
print()
print("witness kills the degree-2 part in EVERY cell:", allok)
print("witness is the unique ANNIHILATOR in every cell:", alluniq,
      "  <-- expected False; uniqueness of the annihilator is not claimed")

# sanity: a WRONG mu should generally fail
bad=0; tot=0
for n in (4,5,6):
    rng=random.Random(n)
    basis=[rng.randrange(1,1<<n) for _ in range(2)]
    if not indep(basis,n): continue
    xR=rng.randrange(1,1<<n); cs=quad_coeffs(basis,xR,n)
    mu_true=inv(sq(xR,n),n)
    for m in range(1,1<<n):
        if m==mu_true: continue
        tot+=1
        if all(tr(mul(m,c,n),n)==0 for c in cs): bad+=1
print(f"negative control: non-witness mu that also kill it: {bad}/{tot}")
