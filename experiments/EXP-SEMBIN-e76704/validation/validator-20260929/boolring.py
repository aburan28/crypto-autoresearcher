"""Validator's independent Boolean-ring (F_2[u]/(u^2-u)) implementation.
Polynomials are python ints: bit m set <=> monomial with variable-set bitmask m has coefficient 1."""
import itertools
def popcount(x): return bin(x).count("1")
def from_set(f):
    r=0
    for m in f: r^=1<<m
    return r
def monos(p):
    m=0
    while p:
        if p&1: yield m
        p>>=1; m+=1
def deg(p):
    return max((popcount(m) for m in monos(p)), default=-1)
def mul_mono_true(p,m):          # TRUE Boolean product: coinciding monomials cancel (XOR)
    r=0
    for mm in monos(p): r^=1<<(mm|m)
    return r
def mul_mono_or(p,m):            # what src/ does: support union (OR)
    r=0
    for mm in monos(p): r|=1<<(mm|m)
    return r
def mul(p,q):
    r=0
    for m in monos(q): r^=mul_mono_true(p,m)
    return r
def rank(vecs):
    piv={}
    for v in vecs:
        while v:
            h=v.bit_length()-1
            if h in piv: v^=piv[h]
            else: piv[h]=v; break
    return len(piv)
def low_part_dim(vecs, D, N):
    """dim(span(vecs) cap R_{<D}): eliminate on degree>=D coordinates first."""
    hi=[m for m in range(1<<N) if popcount(m)>=D]
    # change coordinates: put hi monomials in top bits
    order=hi+[m for m in range(1<<N) if popcount(m)<D]
    pos={m:i for i,m in enumerate(reversed(order))}   # hi monomials get the largest positions
    nb=len(order)-len(hi)
    def remap(p):
        r=0
        for m in monos(p): r|=1<<pos[m]
        return r
    piv={}
    for v in (remap(x) for x in vecs):
        while v:
            h=v.bit_length()-1
            if h in piv: v^=piv[h]
            else: piv[h]=v; break
    return sum(1 for h in piv if h<nb)
def V(gens, D, N, mulf):
    rows=[]
    for g in gens:
        for m in range(1<<N):
            r=mulf(g,m)
            if r and deg(r)<=D: rows.append(r)
    return rows
def new_falls(gens,N,D,mulf):
    rowsD=V(gens,D,N,mulf)
    low=low_part_dim(rowsD,D,N)
    prev=rank(V(gens,D-1,N,mulf)) if D>1 else 0
    return low-prev
def ffd(gens,N,mulf,Dmax=None):
    for D in range(1,(Dmax or N)+1):
        if new_falls(gens,N,D,mulf)>0: return D
    return None
