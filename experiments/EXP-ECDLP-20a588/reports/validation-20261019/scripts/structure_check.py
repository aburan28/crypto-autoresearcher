import json,hashlib,glob
base="/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-20a588/"
plan=json.load(open(base+"trial-plan.json"))
rows=[]
for f in ("runs/RUN-ECDLP-20a588-01/raw-result.jsonl","runs/RUN-ECDLP-20a588-03/raw-result.jsonl"):
    for l in open(base+f):
        r=json.loads(l); r['_f']=f; rows.append(r)
def isprime(n):
    if n<2: return False
    i=2
    while i*i<=n:
        if n%i==0: return False
        i+=1
    return True
errs=[]
for r in rows:
    s=int(hashlib.sha256(f"{plan['seed']}|{r['m']}|{r['L']}|{r['inst']}".encode()).hexdigest()[:12],16)
    if r['seed']!=s: errs.append(("seed",r['L'],r['inst']))
    if r['kind']!=("planted" if r['inst']<4 else "random"): errs.append(("kind",r['L'],r['inst']))
    if r['timeout']!=600: errs.append(("timeout",r['L'],r['inst']))
    if not isprime(r['p']): errs.append(("notprime",r['L']))
    if r['p']%4!=3 or r['p']<=2**(3*r['L']): errs.append(("primeform",r['L']))
    k=(r['p']+1)//2**r['L']
    if (r['p']+1)%2**r['L']: errs.append(("p+1 not div",r['L']))
    if set(r['arms'])!=set(r['results']): errs.append(("armsmismatch",r['L'],r['inst']))
    if r['p'].bit_length()==17: errs.append(("17bit",r['L']))
print("rows",len(rows),"errors:",errs)
# per cell arms
from collections import defaultdict
c=defaultdict(set)
for r in rows: c[r['L']].add(tuple(r['arms']))
for L,a in sorted(c.items()): print("L=%d arms in cell:"%L,a)
# insts per cell
ci=defaultdict(list)
for r in rows: ci[r['L']].append(r['inst'])
print({L:sorted(v) for L,v in ci.items()})
# status values
from collections import Counter
print(Counter((r['L'],a,v['status']) for r in rows for a,v in r['results'].items()))
# wall of timeouts distribution
to=[(r['L'],a,v['wall_s']) for r in rows for a,v in r['results'].items() if v['status']=='timeout']
print("timeout wall range:",min(w for _,_,w in to),max(w for _,_,w in to), "n",len(to))
# max wall of ok results
ok=[(v['wall_s'],r['L'],a) for r in rows for a,v in r['results'].items() if v['status']=='ok']
print("max ok wall:",max(ok))
# f4_max_deg by (L,arm) max
f=defaultdict(int)
for r in rows:
    for a,v in r['results'].items():
        if v.get('f4_max_deg') is not None: f[(r['L'],a)]=max(f[(r['L'],a)],v['f4_max_deg'])
print(dict(sorted(f.items())))
# singular vdim equality A_block vs B_sg
bad=0;n=0
for r in rows:
    A=r['results'].get('A_block_sg');B=r['results'].get('B_sg')
    if A and B and A['status']=='ok' and B['status']=='ok':
        n+=1
        if A['vdim']!=B['vdim']: bad+=1
print("Singular vdim equality A_block_sg == B_sg on",n,"instances; mismatches",bad)
# order-of-run / position effect: instance index vs time for B_ms and A_elim at L=5,6
for L in (5,6):
    print("L",L,{a:[round(r['results'][a]['wall_s'],1) for r in rows if r['L']==L and r['results'][a]['status']=='ok'] for a in ('A_elim_ms','B_ms')})
