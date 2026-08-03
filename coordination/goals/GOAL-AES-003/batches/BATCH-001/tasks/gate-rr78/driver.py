import sys,os,json,time,subprocess,hashlib,random
sys.path.insert(0,'/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602')
from aes_reduced import AES,key_expansion,AES_INV_MIX,AES_MIX,mat_inv,GF,MODULE_SHA256

MASTER_SEED=20260801
DEADLINE=1785621270+2400          # start epoch + 2400 s
def now(): return time.time()
def stamp(): return time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())

rng=random.Random(MASTER_SEED)
def rb(n): return bytes(rng.randrange(256) for _ in range(n))

INVMIX_HEX=bytes(x for row in AES_INV_MIX for x in row).hex()
DIAG0=[0,5,10,15]; SUB3=[0,5,10]; SIB_IN=[0,5,10,12]
ptkey=rb(16); PTRK=b"".join(key_expansion(ptkey,11)).hex()

# sibling output subspace: random invertible 4x4 over GF(2^8), B != MC; pass B^{-1}
def sibling_invmat():
    while True:
        B=tuple(tuple(rng.randrange(256) for _ in range(4)) for _ in range(4))
        if B==AES_MIX: continue
        Bi=mat_inv(B)
        if Bi is not None: return B,bytes(x for row in Bi for x in row).hex()
SIB_B,SIB_INV=sibling_invmat()

CFG=[]; META={}
def add(cid,r,finalmc,nbits,j0,mode,base,freeb,rks,invmat,note):
    CFG.append(f"{cid} {r} {finalmc} {nbits} {j0} {mode} {base.hex()} "
               f"{','.join(map(str,freeb))} {b''.join(rks).hex()} {invmat} {PTRK}")
    META[cid]=dict(id=cid,r=r,finalmc=finalmc,nbits=nbits,j0=j0,mode=mode,
                   base=base.hex(),free_bytes=freeb,invmat=invmat,arm=note,
                   round_keys_sha256=hashlib.sha256(b"".join(rks)).hexdigest())

def sched(key,r): return key_expansion(key,r+1)
def indep(r): return [rb(16) for _ in range(r+1)]

stage=sys.argv[1]

if stage=="pin2":
    for t in range(3):
        key=rb(16); base=bytearray(rb(16))
        for b in [0,5]: base[b]=0
        add(f"PIN2-t{t}",4,0,16,t%4,"coset",bytes(base),[0,5,0,0],sched(key,4),INVMIX_HEX,"pin2")
        META[f"PIN2-t{t}"]["key"]=key.hex()
elif stage=="pc":
    key=rb(16)
    for j0 in range(4):
        base=bytearray(rb(16))
        for b in DIAG0: base[b]=0
        add(f"PC1-j{j0}",2,0,32,j0,"coset",bytes(base),DIAG0,sched(key,2),INVMIX_HEX,"positive_control_PR1")
        META[f"PC1-j{j0}"]["key"]=key.hex()
    base=bytearray(rb(16))
    for b in DIAG0: base[b]=0
    for j0 in (1,0):
        add(f"PC1b-j{j0}",2,1,32,j0,"constcoset" if j0 else "coset",bytes(base),DIAG0,sched(key,2),INVMIX_HEX,"positive_control_PR1b")
        META[f"PC1b-j{j0}"]["key"]=key.hex()
elif stage=="sub24":
    for t in range(20):
        key=rb(16); base=bytearray(rb(16))
        for b in SUB3: base[b]=0
        j0=t%4
        for r in (2,3,4,5,6,10):
            add(f"S24-AES-r{r}-t{t}",r,0,24,j0,"coset",bytes(base),SUB3+[0],sched(key,r),INVMIX_HEX,"subcoset24_aes")
            META[f"S24-AES-r{r}-t{t}"]["key"]=key.hex()
    for t in range(8):
        base=bytearray(rb(16))
        for b in SUB3: base[b]=0
        j0=t%4
        for r in (4,5,6):
            rk=indep(r)
            add(f"S24-RK-r{r}-t{t}",r,0,24,j0,"coset",bytes(base),SUB3+[0],rk,INVMIX_HEX,"subcoset24_indep_roundkeys")
        key=rb(16)
        for r in (4,5,6):
            add(f"S24-SIB-r{r}-t{t}",r,0,24,j0,"coset",bytes(base),SUB3+[0],sched(key,r),SIB_INV,"subcoset24_sibling_outspace")
            add(f"S24-SIBIN-r{r}-t{t}",r,0,24,j0,"coset",bytes(base),SIB_IN[:3]+[0],sched(key,r),INVMIX_HEX,"subcoset24_sibling_inspace")
            add(f"S24-RPT-r{r}-t{t}",r,0,24,j0,"randpt",bytes(base),SUB3+[0],sched(key,r),INVMIX_HEX,"subcoset24_random_plaintexts")
elif stage=="main32":
    for t in range(int(sys.argv[2])):
        key=rb(16); base=bytearray(rb(16))
        for b in DIAG0: base[b]=0
        j0=t%4
        for r in (3,4,5,6,10):
            add(f"M32-AES-r{r}-t{t}",r,0,32,j0,"coset",bytes(base),DIAG0,sched(key,r),INVMIX_HEX,"full32_aes")
            META[f"M32-AES-r{r}-t{t}"]["key"]=key.hex()
elif stage=="null32":
    for t in range(int(sys.argv[2])):
        base=bytearray(rb(16))
        for b in DIAG0: base[b]=0
        j0=t%4
        for r in (4,5,6):
            rk=indep(r)
            add(f"N32-RK-r{r}-t{t}",r,0,32,j0,"coset",bytes(base),DIAG0,rk,INVMIX_HEX,"full32_indep_roundkeys")
            key=rb(16)
            add(f"N32-SIB-r{r}-t{t}",r,0,32,j0,"coset",bytes(base),DIAG0,sched(key,r),SIB_INV,"full32_sibling_outspace")
            add(f"N32-SIBIN-r{r}-t{t}",r,0,32,j0,"coset",bytes(base),SIB_IN,sched(key,r),INVMIX_HEX,"full32_sibling_inspace")
            add(f"N32-RPT-r{r}-t{t}",r,0,32,j0,"randpt",bytes(base),DIAG0,sched(key,r),INVMIX_HEX,"full32_random_plaintexts")
elif stage=="combo32":
    key=rb(16); base=bytearray(rb(16))
    for b in DIAG0: base[b]=0
    for r in (4,5,6,10):
        add(f"C32-AES-r{r}",r,0,32,0,"coset",bytes(base),DIAG0,sched(key,r),INVMIX_HEX,"full32_aes")
        META[f"C32-AES-r{r}"]["key"]=key.hex()
    rk=indep(6)
    add("C32-RK-r6",6,0,32,0,"coset",bytes(base),DIAG0,rk,INVMIX_HEX,"full32_indep_roundkeys")
    add("C32-SIB-r6",6,0,32,0,"coset",bytes(base),DIAG0,sched(key,6),SIB_INV,"full32_sibling_outspace")
    META["C32-SIB-r6"]["key"]=key.hex()
elif stage=="r3":
    key=rb(16); base=bytearray(rb(16))
    for b in DIAG0: base[b]=0
    for r in (3,):
        add(f"R32-AES-r{r}",r,0,32,0,"coset",bytes(base),DIAG0,sched(key,r),INVMIX_HEX,"full32_aes")
        META[f"R32-AES-r{r}"]["key"]=key.hex()
elif stage=="deep32":
    for t in range(int(sys.argv[2])):
        key=rb(16); base=bytearray(rb(16))
        for b in DIAG0: base[b]=0
        for r in (7,8):
            add(f"D32-AES-r{r}-t{t}",r,0,32,t%4,"coset",bytes(base),DIAG0,sched(key,r),INVMIX_HEX,"full32_aes_deep")
            META[f"D32-AES-r{r}-t{t}"]["key"]=key.hex()

out=open(f"raw_{stage}.jsonl","a")
meta=open(f"meta_{stage}.jsonl","a")
p=subprocess.Popen(["./gate"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
sent=0
for line in CFG:
    if now()>DEADLINE-20:
        print(json.dumps({"halt":"deadline","stamp":stamp(),"configs_sent":sent,"configs_planned":len(CFG)}))
        break
    p.stdin.write(line+"\n"); p.stdin.flush(); sent+=1
    res=p.stdout.readline()
    if not res: break
    d=json.loads(res); d["stamp"]=stamp(); d.update({k:v for k,v in META[d["id"]].items() if k in("arm","key","round_keys_sha256","base","free_bytes","invmat")})
    out.write(json.dumps(d)+"\n"); out.flush()
    meta.write(json.dumps(META[d["id"]])+"\n")
    print(f"{d['id']:24s} n={d['n']:22d} mod8={d['n_mod8']} maxocc={d['max_occupancy']} ovf={d['overflow']} idok={d['identity_check_ok']} const={d['pi_constant']} {d['seconds']:.1f}s",flush=True)
p.stdin.close(); p.wait()
out.close(); meta.close()
