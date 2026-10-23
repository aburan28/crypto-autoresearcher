import sys,time,random
sys.path.insert(0,'.')
import proto, mac, gf
n,shape,k,D=int(sys.argv[1]),sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
F=gf.GF(n); basis=[1<<j for j in range(k)]; B=0b101
V=gf.span(basis); sat=gf.sat_set(F,shape,V,B)
es,et0,nv=proto.build(n,shape,k,B,basis,0)
blocks=[et0]+[proto.build(n,shape,k,B,basis,1<<i)[1] for i in range(n)]
M=mac.Mac(nv,D)
dS=[max((m.bit_count() for m in e),default=0) for e in es]
dT=[max(max((m.bit_count() for m in blocks[j][g]),default=0) for j in range(n+1)) for g in range(len(et0))]
Srows=[]
for g,e in enumerate(es):
    if dS[g]<=D: Srows+=M.rows_of(e,D-dS[g])
piv=mac.rref(Srows); nf=mac.make_nf(piv); c1=nf(1<<M.idx[0])
NF=[]
for j in range(n+1):
    rows=[]
    for g in range(len(et0)):
        f=blocks[0][g] if j==0 else sorted(set(blocks[j][g])^set(blocks[0][g]))
        rows+=M.rows_of(f,D-dT[g])
    NF.append([nf(r) for r in rows])
print('nv',nv,'ncol',M.ncol,'S rank',len(piv),'rows_T',len(NF[0]),'sat',len(sat),'c1!=0',c1!=0,flush=True)
def Nz(z):
    N=list(NF[0])
    for i in range(n):
        if (z>>i)&1: N=[a^b for a,b in zip(N,NF[i+1])]
    return N
def solve(N,c):
    piv={};kern=[]
    for ri,r in enumerate(N):
        tag=1<<ri
        while r:
            hb=r.bit_length()-1; p=piv.get(hb)
            if p is None: piv[hb]=(r,tag);break
            r^=p[0];tag^=p[1]
        if r==0: kern.append(tag)
    lam=0;x=c
    while x:
        hb=x.bit_length()-1;p=piv.get(hb)
        if p is None: return None,kern
        x^=p[0];lam^=p[1]
    return lam,kern
t=time.time(); ref=[];bad=0;kd=set()
for z in range(1<<n):
    lam,kern=solve(Nz(z),c1); kd.add(len(kern))
    if lam is not None:
        ref.append(z)
        if z in sat: bad+=1
unsat=(1<<n)-len(sat)
print('refuted',len(ref),'of unsat',unsat,'rate',round(len(ref)/unsat,3),'SOUNDNESS VIOLATIONS',bad,'kernel dims',sorted(kd)[:5],'time',round(time.time()-t,1),flush=True)
