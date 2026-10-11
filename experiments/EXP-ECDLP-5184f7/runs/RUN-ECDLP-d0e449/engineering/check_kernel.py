"""Excluded engineering checks of old/toy and full-size representations."""
import json, math, subprocess, sys
from pathlib import Path
repo=Path('/workspace/solinas-run');ext=repo/'experiments/EXP-ECDLP-5184f7/extensions/nist-fullsize-20261011'
sys.path.insert(0,str(ext/'implementation'))
from common import Stream, generator, write
from finite_math import Curve
from prepare_nist import anchors
from run_attacks_nist import equivalent
out=Path('/workspace/solinas-runtime/nist-comparison/instrument-03');out.mkdir(parents=True,exist_ok=False)
oldprep=Path('/workspace/solinas-runtime/prime-comparison/instrument-check-01')
source=oldprep/'public-jobs.txt';old=json.loads('[]')
oldraw=[json.loads(x)for x in (oldprep/'kernel.stdout').read_text().splitlines()if x.strip()]
jobs=[]
for line in source.read_text().splitlines():
    fs=line.split();jobs.append(line+' '+str(math.isqrt(400*int(fs[7]))+1))
(out/'toy-public-jobs.txt').write_text('\n'.join(jobs)+'\n')
kernel=Path('/workspace/solinas-runtime/nist-comparison/attack')
with (out/'toy.stdout').open('x')as so,(out/'toy.stderr').open('x')as se:
    r=subprocess.run([str(kernel),str(out/'toy-public-jobs.txt')],stdout=so,stderr=se,timeout=600)
assert r.returncode==0
newraw=[json.loads(x)for x in (out/'toy.stdout').read_text().splitlines()if x.strip()]
assert len(oldraw)==len(newraw)
assert all(equivalent({k:v for k,v in a.items()if k != "table_allocated_bytes"},{k:v for k,v in b.items()if k != "table_allocated_bytes"})for a,b in zip(oldraw,newraw,strict=True))
print('TOY_EXACT_KERNEL_PARITY',len(newraw),flush=True)
probe=json.loads(Path('/workspace/solinas-runtime/nist-comparison/instrument-01/results.json').read_text())
groups=[]
for label,i,q in [('P192',0,7),('P224',0,369119)]:
    item=next(r for r in probe if r['name']==label);p=item['p'];A,B=item['rows'][i];N=item['outputs'][i][1]
    row={'p':p,'A':A,'B':B,'N':N,'index':i,'modulus_id':'EXCLUDED-'+label}
    G,_=generator(row,q);ec=Curve(p,A,B);truth=1+Stream('excluded-kernel-check/'+label).below(q-1);Q=list(ec.mul(tuple(G),truth))
    groups.append({'label':label,'p':p,'A':A,'B':B,'ell':q,'h':N//q,'G':G,'Q':Q,'truth':truth})
case=json.loads((ext/'contract.json').read_text())['prime_cases']
anc=anchors(out,case)
for g in anc:
    q=(1<<130)+1234567;ec=Curve(g['p'],g['A'],g['B']);Q=list(ec.mul(tuple(g['G']),q))
    groups.append({'label':g['case']+'-full','p':g['p'],'A':g['A'],'B':g['B'],'ell':g['ell'],'h':g['h'],'G':g['G'],'Q':Q,'truth':q})
truths={};fulljobs=[]
for g in groups:
    p=g['p'];cap=math.isqrt(400*g['ell'])+1 if g['ell']<(1<<20)else 64
    for mode in (['rho','oracle','rho32','bsgs','transport']if g['ell']<(1<<20)else['rho','transport']):
        A,B,G,Q,u=g['A'],g['B'],g['G'],g['Q'],1
        if mode=='transport':
            u=3;A=A*pow(u,4,p)%p;B=B*pow(u,6,p)%p;G=[G[0]*pow(u,2,p)%p,G[1]*pow(u,3,p)%p];Q=[Q[0]*pow(u,2,p)%p,Q[1]*pow(u,3,p)%p]
        jid=g['label']+'-'+mode;truths[jid]=g
        adding=32 if mode=='rho32'else 16
        fulljobs.append(' '.join(map(str,[jid,mode,adding,1,p,A,B,g['ell'],g['h'],*G,*Q,u,cap])))
(out/'full-public-jobs.txt').write_text('\n'.join(fulljobs)+'\n')
with (out/'full.stdout').open('x')as so,(out/'full.stderr').open('x')as se:
    r=subprocess.run([str(kernel),str(out/'full-public-jobs.txt')],stdout=so,stderr=se,timeout=600)
assert r.returncode==0
records=[json.loads(s)for s in (out/'full.stdout').read_text().splitlines()if s.strip()]
assert len(records)==len(fulljobs)
by={r['job_id']:r for r in records}
for r in records:
    g=truths[r['job_id']]
    if g['ell']<(1<<20):assert r['verified']and r['scalar']==g['truth']
    else:assert r['counts']['search']['group_calls']==64 and r['censored']
for g in groups:assert equivalent(by[g['label']+'-rho'],by[g['label']+'-transport'],True)
write(out/'checks.json',{'toy_exact_parity_jobs':len(newraw),'full_size_jobs':len(records),'small_scalars_correct':True,'large_explicit_caps_exact':True,'transport_traces_exact':True,'status':'passed','excluded_from_scientific_sample':True})
print('FULL_SIZE_KERNEL_CHECKS',len(records),'passed',flush=True)
