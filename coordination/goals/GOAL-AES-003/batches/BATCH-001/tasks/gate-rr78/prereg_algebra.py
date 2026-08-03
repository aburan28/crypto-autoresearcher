import sys
sys.path.insert(0,'/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602')
from aes_reduced import shift_rows, inv_shift_rows, mix_columns, AES_MIX, AES_INV_MIX
OFF=(0,1,2,3)
def vec(f):
    # 128x128 GF(2) matrix as list of 128 ints (columns as basis images)
    cols=[]
    for b in range(128):
        s=bytearray(16); s[b//8] |= 1<<(7-(b%8))
        o=f(bytes(s))
        v=0
        for i,by in enumerate(o):
            for k in range(8):
                if (by>>(7-k))&1: v |= 1<<(i*8+k)
        cols.append(v)
    return cols
SR  = vec(lambda s: shift_rows(s,OFF))
MC  = vec(lambda s: mix_columns(s,AES_MIX))
def apply(M,x):
    r=0
    for b in range(128):
        if (x>>b)&1: r^=M[b]
    return r
def bitvec(idx_bytes):
    return [1<<(i*8+k) for i in idx_bytes for k in range(8)]
def span(vs):
    basis=[]
    for v in vs:
        for b in basis:
            v=min(v, v^b)
        if v: basis.append(v); basis.sort(reverse=True)
    # proper reduce
    basis=[]
    for v in vs:
        cur=v
        for b in basis:
            cur=min(cur,cur^b)
        if cur: basis.append(cur)
    return basis
def rank(vs):
    basis=[];
    for v in vs:
        cur=v
        for b in basis:
            cur=min(cur,cur^b)
        if cur: basis.append(cur)
    return len(basis)
def inter_dim(A,B):
    # dim(A cap B) = dimA+dimB-dim(A+B)
    return rank(A)+rank(B)-rank(A+B)

col=lambda j: bitvec([4*j+r for r in range(4)])
Cs={j:col(j) for j in range(4)}
# M_j = MC(SR(C_j))
Ms={j:[apply(MC,apply(SR,v)) for v in Cs[j]] for j in range(4)}
print("dim M_j:", [rank(Ms[j]) for j in range(4)])
print("dim sum all M:", rank(sum(Ms.values(),[])))
# V2 = SR(C_0)  (r=2 output space under pinned convention, full diagonal coset)
V2=[apply(SR,v) for v in Cs[0]]
for j0 in range(4):
    MJ=sum((Ms[j] for j in range(4) if j!=j0),[])
    print(f"j0={j0}: dim M_J={rank(MJ)}  dim(V2 cap M_J)={inter_dim(V2,MJ)}  dim(M_0 cap M_J)={inter_dim(Ms[0],MJ)}")
# 3-byte subcoset: after round1 (full) space = MC(SR(D')) with D'={0,5,10}
D3=bitvec([0,5,10])
W1=[apply(MC,apply(SR,v)) for v in D3]
print("dim MC(SR(D3)) =",rank(W1), " is it byte-aligned in col0?")
# check byte-alignment: is W1 spanned by coordinate bytes?
print("  W1 basis vectors touch bytes:", sorted({i for v in W1 for i in range(16) if (v>>(i*8))&0xff}))
