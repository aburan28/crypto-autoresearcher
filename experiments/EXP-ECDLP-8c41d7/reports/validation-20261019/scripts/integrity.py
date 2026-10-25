#!/usr/bin/env python3
"""Artifact integrity: seeds, prime rule, stdout.log vs raw rows, timeline vs git commit times, elapsed vs started/finished."""
import json, hashlib, re, subprocess, datetime as dt
from sympy import isprime
R="/home/user/crypto-autoresearcher"
ROOT=f"{R}/experiments/EXP-ECDLP-8c41d7/runs"
SEED="EXP-ECDLP-f49f75/v1"
def load(n): return [json.loads(l) for l in open(f"{ROOT}/RUN-ECDLP-8c41d7-{n:02d}/raw-result.jsonl")]
def frozen_prime(m,L):
    k=(2**(m*L))//(2**L)+1
    while True:
        p=k*2**L-1
        if p%4==3 and p>2**(m*L) and isprime(p): return p
        k+=1
bad=0
for n in (1,2,3,4):
    rows=load(n)
    for r in rows:
        want=int(hashlib.sha256(f"{SEED}|4|{r['L']}|{r['inst']}".encode()).hexdigest()[:12],16)
        ok_seed = want==r['seed']
        fp=frozen_prime(4,r['L'])
        exp_p = 262271 if (n==4) else fp
        ok_p = r['p']==exp_p and isprime(r['p']) and (r['p']+1)%(2**r['L'])==0 and r['p']%4==3 and r['p_bits']==r['p'].bit_length()
        ok_kind = r['kind']==('planted' if r['inst']<4 else 'random')
        ok_to = r['timeout']==600
        if not(ok_seed and ok_p and ok_kind and ok_to):
            bad+=1; print("BAD",n,r['L'],r['inst'],ok_seed,ok_p,ok_kind,ok_to)
    print(f"RUN-{n:02d}: rows={len(rows)} L={sorted({r['L'] for r in rows})} p={sorted({r['p'] for r in rows})} frozen-rule p(4,L)={sorted({frozen_prime(4,r['L']) for r in rows})} arms={sorted({a for r in rows for a in r['results']})}")
print("seed/prime/kind/timeout violations:", bad)
print("262271 prime:", isprime(262271), " 16|(p+1):", (262271+1)%16==0, " p+1 = 2^%d * %d"%((lambda x:(x&-x).bit_length()-1)(262272), 262272//(262272&-262272)), " bits:", (262271).bit_length(), " = smallest prime >2^18 with 64|p+1 (m=3,L=6 rule):", frozen_prime(3,6)==262271)
# stdout.log vs raw
pat=re.compile(r"(\w+):([\w-]+)/([\d.None]+)/(True|False|None)")
mism=0
for n in (1,2,3,4):
    rows={ (r['L'],r['inst']): r for r in load(n)}
    for line in open(f"{ROOT}/RUN-ECDLP-8c41d7-{n:02d}/stdout.log"):
        m=re.match(r"m=4 L=(\d+) inst=(\d+) elim=B:(\w+) (.*)$",line.strip())
        if not m: continue
        L,i=int(m.group(1)),int(m.group(2)); r=rows[(L,i)]
        if m.group(3)!=str(r.get('elim_equals_B')): mism+=1; print("stdout elim mismatch",n,L,i)
        for arm,st,w,pl in pat.findall(m.group(4)):
            v=r['results'][arm]
            if st!=v['status'] or (w!='None' and abs(float(w)-v['wall_s'])>1e-9) or pl!=str(v.get('planted_in_variety')): mism+=1; print("stdout mismatch",n,L,i,arm)
print("stdout.log vs raw-result mismatches:", mism)
# timeline
def ts(p): return dt.datetime.strptime(open(p).read().strip(),"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
def ct(h): return dt.datetime.fromisoformat(subprocess.run(["git","-C",R,"show","-s","--format=%cI",h],capture_output=True,text=True).stdout.strip())
tl={1:("6d6df97b6d","spec+plan freeze"),2:("04a87943e2","AMD-01 (+RUN-01 records)"),3:("d2d3f9ef29","AMD-02 (+RUN-02 records)"),4:("7413b95b6a","AMD-03 + p19 launcher (+RUN-03 records)")}
for n,(h,lab) in tl.items():
    s=ts(f"{ROOT}/RUN-ECDLP-8c41d7-{n:02d}/started_at"); c=ct(h)
    env=json.load(open(f"{ROOT}/RUN-ECDLP-8c41d7-{n:02d}/environment.json"))
    print(f"RUN-{n:02d} started {s:%FT%TZ}; authorising commit {h} ({lab}) committed {c.astimezone(dt.timezone.utc):%FT%TZ}; gap = {(s-c).total_seconds():.0f} s; env git_head={env['git_head'][:10]} dirty={env['git_dirty']}; authorising commit is ancestor of env head: {subprocess.run(['git','-C',R,'merge-base','--is-ancestor',h,env['git_head']]).returncode==0}")
for n in (3,4):
    s=ts(f"{ROOT}/RUN-ECDLP-8c41d7-{n:02d}/started_at"); f=ts(f"{ROOT}/RUN-ECDLP-8c41d7-{n:02d}/finished_at")
    el=[json.loads(l) for l in open(f"{ROOT}/RUN-ECDLP-8c41d7-{n:02d}/stdout.log") if l.startswith('{"jobs"')][0]['elapsed_s']
    print(f"RUN-{n:02d}: finished_at-started_at = {(f-s).total_seconds():.0f} s vs launcher elapsed_s = {el}")
