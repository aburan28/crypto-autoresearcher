"""Validator kernel: TRUE Boolean-ring products (XOR), columns ordered by degree.
Same observable as the runner (new_falls(D) = dim(V_D cap R_{<D}) - dim V_{D-1}), same up/down logic."""
import itertools
def popcount(x): return bin(x).count("1")
class TrueKernel:
    def __init__(self, gens_sets, N):
        self.N=N; self.l=len(gens_sets)
        self.monos=sorted(range(1<<N), key=lambda m:(popcount(m),m))
        self.pos={m:i for i,m in enumerate(self.monos)}
        self.degs=[popcount(m) for m in self.monos]
        self.base=[]
        for f in gens_sets:
            row=[]
            for m in range(1<<N):
                r=0
                for mm in f: r^=1<<self.pos[mm|m]      # XOR: coinciding monomials cancel
                row.append(r)
            self.base.append(row)
        self.cache={}
    def rows(self,S):
        g=self.cache.get(S)
        if g is None:
            g=[0]*(1<<self.N)
            for j in range(self.l):
                if (S>>j)&1:
                    b=self.base[j]; g=[x^y for x,y in zip(g,b)]
            self.cache[S]=g
        return g
    def _dims(self,M,D):
        piv={}
        for S in M:
            for r in self.rows(S):
                if r and self.degs[r.bit_length()-1]<=D:
                    v=r
                    while v:
                        h=v.bit_length()-1
                        if h in piv: v^=piv[h]
                        else: piv[h]=v; break
        rank=len(piv); low=sum(1 for h in piv if self.degs[h]<D)
        return rank,low
    def new_falls(self,M,D):
        rank,low=self._dims(M,D)
        prev=self._dims(M,D-1)[0] if D>1 else 0
        return low-prev
    def ffd(self,M):
        for D in range(1,self.N+1):
            if self.new_falls(M,D)>0: return D
        return None
def invertible(rows,l):
    piv={}
    for r in rows:
        v=r
        while v:
            h=v.bit_length()-1
            if h in piv: v^=piv[h]
            else: piv[h]=v; break
    return len(piv)==l
def gl_rowsets(l):
    for c in itertools.combinations(range(1,1<<l),l):
        if invertible(c,l): yield list(c)
