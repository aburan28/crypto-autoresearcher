import json, hashlib, math
DOM="EXP-MONO-64aaa4/v1"
def seed_bytes(label,p,role,di,c):
    return hashlib.sha256(f"{DOM}|{label}|{p}|{role}|{di}|{c}".encode()).digest()
def qrtab(p):
    sq=[0]*p
    for y in range(1,(p+1)//2):
        sq[(y*y)%p]=1
    return sq
def is_sing(A,B,p): return (4*pow(A,3,p)+27*pow(B,2,p))%p==0
def Ntau(A,B,p,sq):
    tot=1; roots=0
    for x in range(p):
        f=(x*x*x+A*x+B)%p
        if f==0: roots+=1; tot+=1
        elif sq[f]: tot+=2
    return tot, roots+1
def cons_ord(p,sq):
    for t in range(65536):
        A=int.from_bytes(seed_bytes("curve-a",p,"ord",0,t),"big")%p
        B=int.from_bytes(seed_bytes("curve-b",p,"ord",0,t),"big")%p
        if is_sing(A,B,p) or A==0 or B==0: continue
        N,tau=Ntau(A,B,p,sq)
        if N%p==1: continue
        return A,B,N,tau
    return None
def cons_cm(p,sq,variant):
    for t in range(65536):
        if variant=="j0":
            B=int.from_bytes(seed_bytes("curve-b",p,"cm",0,t),"big")%p
            if B==0: continue
            A=0
        else:
            A=int.from_bytes(seed_bytes("curve-a",p,"cm",0,t),"big")%p
            if A==0: continue
            B=0
        if is_sing(A,B,p): continue
        N,tau=Ntau(A,B,p,sq)
        return A,B,N,tau
    return None
def add(P,Q,A,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        lam=((3*x1*x1+A)*pow((2*y1)%p,p-2,p))%p
    else:
        lam=((y2-y1)*pow((x2-x1)%p,p-2,p))%p
    x3=(lam*lam-x1-x2)%p
    return (x3%p,(lam*(x1-x3)-y1)%p)
def nE4(A,B,p,sq):
    # count points with 4P=O
    c=1  # O
    for x in range(p):
        f=(x*x*x+A*x+B)%p
        if f==0:
            c+=1; continue
        if not sq[f]: continue
        y=None
        for yy in range(1,(p+1)//2):
            if (yy*yy)%p==f: y=yy; break
        P=(x,y); P2=add(P,P,A,p); P4=add(P2,P2,A,p)
        if P4 is None: c+=2
    return c
def exact_tr(N,tau,e4):  # e4 = #E[4] (full)
    if tau==1: return 0.0
    n=(N-tau)//2
    F=(e4-tau)/2
    return 3*((tau-1)*n-F)/(n*(n-1))

d=json.load(open("/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-cb905d/runs/RUN-MONO-cb905d-1/raw-result.json"))
cells=d["part_b"]["cells"]
sqc={}; cur={}
def get_sq(p):
    if p not in sqc: sqc[p]=qrtab(p)
    return sqc[p]
def getcurve(p,role,variant=None):
    k=(p,role,variant)
    if k in cur: return cur[k]
    sq=get_sq(p)
    r = cons_ord(p,sq) if role=="ord" else cons_cm(p,sq,variant)
    A,B,N,tau=r
    e4=nE4(A,B,p,sq)
    cur[k]=(A,B,N,tau,e4)
    return cur[k]

# sanity: reproduce the p=617 pair
print("p617 ord:",getcurve(617,"ord")[:4],"expect A=340 B=362 N=580 tau=4")
print("p617 cm1728:",getcurve(617,"cm","j1728")[:4],"expect A=69 B=0 N=580 tau=4")

rows=[]
for c in cells:
    po,pc,v,N,tau=c["p_ord"],c["p_cm"],c["cm_variant"],c["N"],c["tau"]
    Ao,Bo,No,to,e4o=getcurve(po,"ord")
    Ac,Bc,Nc,tc,e4c=getcurve(pc,"cm",v)
    assert (No,to)==(N,tau) and (Nc,tc)==(N,tau),(po,pc,No,to,Nc,tc,N,tau)
    eo=exact_tr(N,tau,e4o); ec=exact_tr(N,tau,e4c)
    rows.append(dict(p_ord=po,p_cm=pc,v=v,N=N,tau=tau,e4o=e4o,e4c=e4c,
        exact_ord=eo,exact_cm=ec,
        obs_ord=c["ord"]["observed_total_pairs_colliding"],
        obs_cm=c["cm"]["observed_total_pairs_colliding"],
        closed=c["predicted_rate"]))
json.dump(rows,open("/tmp/claude/panel.json","w"),indent=1)
print("cells:",len(rows))
