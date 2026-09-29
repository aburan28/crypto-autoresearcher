#!/usr/bin/env python3
"""Validator's OWN certificate re-verification: affine short-Weierstrass arithmetic written here, shares no code with either executor."""
import json, sys, time, random, glob, os
def inv(a,p): return pow(a,p-2,p)
def add(P,Q,a,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        l=(3*x1*x1+a)*inv(2*y1,p)%p
    else:
        l=(y2-y1)*inv(x2-x1,p)%p
    x3=(l*l-x1-x2)%p; y3=(l*(x1-x3)-y1)%p
    return (x3,y3)
def mul(k,P,a,p):
    R=None; Q=P
    while k:
        if k&1: R=add(R,Q,a,p)
        Q=add(Q,Q,a,p); k>>=1
    return R
def on_curve(P,a,b,p): x,y=P; return (y*y-(x*x*x+a*x+b))%p==0
random.seed(0x7ec3)
report={}
t0=time.time()
# 612fb1: all certificates
tot=0; ok=0; bad=[]; per_run={}
for r in ('34','35','36'):
    d=f'experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-{r}/'
    C=json.load(open(d+'certificates.json')); cv=C['curve']; p,a,b,N=cv['p'],cv['a'],cv['b'],cv['N']; G=tuple(cv['P'])
    raw=json.load(open(d+'raw-result.json'))
    solved=sum(sum(x['solved']) for x in raw['arms'].values() if x['config']['mode']!='rho')
    solved_incl_rho=sum(sum(x['solved']) for x in raw['arms'].values())
    n=0; good=0
    assert mul(N,G,a,p) is None and on_curve(G,a,b,p)
    for c in C['certificates']:
        n+=1
        P=tuple(c['P']); Q=tuple(c['Q']); k=c['k']
        good_i = (c['kind']=='discrete_log' and P==G and on_curve(Q,a,b,p) and 0<=k<N and mul(k,P,a,p)==Q)
        good+=good_i
        if not good_i: bad.append((r,c.get('target'),c.get('arm')))
    per_run[r]={'certificates':n,'my_pass':good,'reported_passed':C['stats']['passed'],'reported_solved':C['stats']['solved_total'],'raw_solved_non_rho_arms':int(solved),'raw_solved_incl_rho':int(solved_incl_rho),'per_arm_certs':{k:len(v['certificates']) for k,v in raw['arms'].items()},'per_arm_solved':{k:int(sum(v['solved'])) for k,v in raw['arms'].items()}}
    tot+=n; ok+=good
report['612fb1']={'total':tot,'my_pass':ok,'failures':bad[:20],'per_run':per_run,'seconds':round(time.time()-t0,1)}
print(json.dumps(report['612fb1'],indent=1)); sys.stdout.flush()
# 869870: all certificates in every curve cell (time-capped sample if needed)
t1=time.time(); rep={}
for r in sorted(glob.glob('experiments/EXP-ECDLP-869870/runs/RUN-ECDLP-869870-02[123]-curve-s*')):
    raw=json.load(open(r+'/raw-result.json')); cv=raw['header']['curve']; p,a,b,N=cv['p'],cv['a'],cv['b'],cv['N']; G=tuple(cv['P'])
    assert mul(N,G,a,p) is None and on_curve(G,a,b,p)
    rr={'curve':cv['curve_id'],'header_cert':raw['header']['certificate'],'cells':{}}
    for ck,cell in raw['cells'].items():
        certs=cell['certificates']; n=len(certs)
        sample=certs if n<=12000 else random.sample(certs,12000)
        good=0; badc=0
        for c in sample:
            st=c['statement']; P=tuple(st['P']); Q=tuple(st['Q']); k=st['k']
            gi=(P==G and on_curve(Q,a,b,p) and 0<=k<N and mul(k,P,a,p)==Q and c.get('verified') is True)
            good+=gi; badc+= (not gi)
        # hits of any table must be <= certificates: use fixture/published hits from summary not available here; use online_walks count
        M=cell['online_walks']['M']
        rr['cells'][ck]={'certificates':n,'checked':len(sample),'my_pass':good,'my_fail':badc,'M_online':M,'online_group_ops':cell['online_extra_raw_summary']['online_group_ops'],'restart_scalar_mults':cell['online_extra_raw_summary']['restart_scalar_mults'],'real_walk_matches_exact_map':cell['online_extra_raw_summary']['real_walk_matches_exact_map']}
    rep[os.path.basename(r)]=rr
report['869870']=rep; report['869870_seconds']=round(time.time()-t1,1)
print(json.dumps(rep,indent=1))
json.dump(report,open(sys.argv[1],'w'),indent=1)
