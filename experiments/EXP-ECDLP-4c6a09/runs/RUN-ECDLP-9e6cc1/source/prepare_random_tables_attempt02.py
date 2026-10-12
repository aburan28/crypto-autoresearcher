#!/usr/bin/env python3
"""Export checked random-field points and verify exact-K coefficient grids."""
import concurrent.futures
import hashlib
import json
import shutil
import time
from fractions import Fraction
from pathlib import Path

from gp_tables_random import execute, exact_grid, polynomial, prelude, write
from benchmark import exact_seed_check
from finite_math import self_controls

RUN = Path(__file__).resolve().parent.parent

def export_one(stage, result, qr):
    j=result['job']
    spec={'id':j['id'],'field':j['field'],'g':j['g'],'A':j['A'],'B':j['B'],
          'draw_seed':j['draw_seed'],'draw_index':j['draw_index'],
          'canonical_polynomial_gp':j['canonical_polynomial_gp'],
          'field_discriminant':j['field_discriminant'],
          'rank_bounds':result['nf_bounds'],'rank_status':result['status'],
          'rank_seed_discovery_elapsed_seconds':result['elapsed_seconds'],
          'seed_discovery_available':bool(result['nf_raw_vectors_gp'])}
    nr=result['nf_raw_vectors_gp'][-1] if result['nf_raw_vectors_gp'] else None
    code=prelude()+'\n'.join([
        '{main()=',
        f'my(N=nfinit({polynomial(j["g"])}),EK=ellinit([0,0,0,{j["A"]},{j["B"]}],N),QR={qr},NR,T,S=List(),P,dup,PR,MP,R,MR,PI,EP,C,F,L,H,G,found,RP);',
        f'NR={nr};T=NR[3];' if nr else 'T=QR[4];',
        'T=concat([QR[4][1]],T);print("@@RAW_SEED_COUNT|",#T-1);',
        'for(i=1,#T,P=T[i];if(#P==1,next);if(!ellisoncurve(EK,P),error("Seed off exact curve"));dup=0;for(t=1,#S,if(P==S[t] || P==ellneg(EK,S[t]),dup=1;break));if(!dup,listput(S,P)));',
        'print("@@UNIQUE_AVAILABLE_SEED_COUNT|",#S);S=Vec(S);if(#S>4,S=S[1..4]);',
        'for(i=1,#S,print("@@SEED|",i,"|",vector(3,t,polcoef(lift(S[i][1]),t-1)),"|",vector(3,t,polcoef(lift(S[i][2]),t-1))));',
        'for(kj=1,3,R=2^([6,7,12][kj]);PI=R^3-R-1;',
        f'EP=ellinit([0,0,0,{j["A"]},{j["B"]}],PI);C=ellcard(EP);F=factor(C);L=F[#F[,1],1];if(F[#F[,1],2]!=1,error("Repeated largest prime"));H=C/L;',
        'RP=QR[4][1];G=ellmul(EP,[Mod(RP[1],PI),Mod(RP[2],PI)],H);if(#G==1,G=ellmul(EP,ellgroup(EP,,1)[3][1],H));if(#G==1,error("Zero G"));',
        'print("@@GROUP|",kj,"|",PI,"|",C,"|",L,"|",H,"|",lift(G[1]),"|",lift(G[2]));',
        'MR=polrootsmod(N.pol,PI);if(!#MR,print("@@NO_ROOT|",kj);next);R=vecmin(lift(MR));',
        'PR=idealprimedec(N,PI);found=0;for(i=1,#PR,if(PR[i][4]==1 && lift(trace(nfmodpr(N,Mod(y,N.pol),PR[i])))==R,found=i;break));if(!found,error("Missing degree-one prime"));PR=PR[found];MP=nfmodprinit(N,PR);',
        'print("@@ROOT|",kj,"|",R,"|",found);',
        'for(i=1,#S,if(nfeltval(N,S[i][1],PR)<0,print("@@REDUCED_SEED|",kj,"|",i,"|O");next);',
        'P=[lift(trace(nfmodpr(N,S[i][1],MP))),lift(trace(nfmodpr(N,S[i][2],MP)))];if(!ellisoncurve(EP,P),error("Reduced seed off curve"));print("@@REDUCED_SEED|",kj,"|",i,"|",P[1],"|",P[2]));',
        ');};', 'iferr(main(),E,print("@@ERROR|",E));print("@@DONE");quit;'])+'\n'
    output,process=execute(stage/'seed-export'/spec['id'],code)
    spec['seeds_coefficients'],spec['reductions']=[],{}
    for line in output.splitlines():
        v=line.split('|')
        if v[0]=='@@SEED':
            fractions=[[Fraction(x.strip()) for x in s.strip('[]').split(',')] for s in v[2:4]]
            spec['seeds_coefficients'].append([[[x.numerator,x.denominator] for x in coord] for coord in fractions])
        elif v[0]=='@@RAW_SEED_COUNT':spec['raw_descent_point_count']=int(v[1])
        elif v[0]=='@@UNIQUE_AVAILABLE_SEED_COUNT':spec['unique_available_point_count']=int(v[1])
        elif v[0]=='@@GROUP':
            kj,p,n,ell,h,gx,gy=map(int,v[1:])
            spec['reductions'][str(kj)]={'k':[6,7,12][kj-1],'p':p,'group_order':n,'ell':ell,
                                        'cofactor':h,'G':[gx,gy],'seeds_full':[]}
        elif v[0]=='@@ROOT':
            spec['reductions'][v[1]].update({'root':int(v[2]),'prime_index':int(v[3]),'eligible':True})
        elif v[0]=='@@NO_ROOT':spec['reductions'][v[1]]['eligible']=False
        elif v[0]=='@@REDUCED_SEED':
            spec['reductions'][v[1]]['seeds_full'].append(None if v[3]=='O' else list(map(int,v[3:5])))
    spec['export_process']=process
    spec['seed_count']=len(spec['seeds_coefficients'])
    assert 1<=spec['seed_count']<=4
    exact_seed_check(spec)
    for red in spec['reductions'].values():
        if red['eligible']:assert len(red['seeds_full'])==spec['seed_count']
    write(stage/'seed-export'/spec['id']/'spec.json',spec)
    return spec

def prepare_one(stage,result,qr):
    try:
        spec=export_one(stage,result,qr)
        if any(r['eligible'] for r in spec['reductions'].values()):
            exact_grid(stage,spec,bounds=(4,),repetitions=3)
        print('TABLES',spec['id'],'seeds',spec['seed_count'],flush=True)
        return {'id':spec['id'],'status':'complete','spec':spec}
    except Exception as exc:
        status={'id':result['job']['id'],'status':'implementation_or_resource_failure',
                'error':str(exc),'asserts_nothing_about':'Mathematical viability; no resampling'}
        write(stage/('failure-'+result['job']['id']+'.json'),status)
        print('PREPARATION_FAILED',status['id'],str(exc),flush=True)
        return status

def main():
    stage=RUN/'point-preparation-attempt-02'
    stage.mkdir(exist_ok=False)
    (stage/'source').mkdir()
    for name in ['prepare_random_tables_attempt02.py','gp_tables_random.py','benchmark.py','finite_math.py']:
        shutil.copy2(RUN/'source'/name,stage/'source'/name)
    write(stage/'launch.json',{'command_argv':['python3',str(Path(__file__).resolve())],
                             'plan_sha256':hashlib.sha256((RUN/'plan.json').read_bytes()).hexdigest(),
                             'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (stage/'source').iterdir()}})
    write(stage/'controls-result.json',self_controls())
    inherited=json.loads((RUN/'inputs/inherited-points.json').read_text())
    qr={}
    for q in inherited['q']:
        output=(RUN/'inputs'/(q['job']['id']+'.stdout.log')).read_text()
        qr[(q['job']['A'],q['job']['B'])]=[line.split('|',1)[1] for line in output.splitlines() if line.startswith('@@Q_RAW|')][-1]
    results=json.loads((RUN/'random-ranks-result.json').read_text())['nf']
    start=time.monotonic()
    outputs=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for future in concurrent.futures.as_completed([pool.submit(prepare_one,stage,r,qr[(r['job']['A'],r['job']['B'])]) for r in results]):
            outputs.append(future.result())
    write(stage/'seed-specs.json',[o['spec'] for o in outputs if o['status']=='complete'])
    write(stage/'result.json',{'outcomes':outputs,'elapsed_seconds':time.monotonic()-start})
    print('PREPARATION_FINISHED',len(outputs),sum(o['status']=='complete' for o in outputs),flush=True)

if __name__=='__main__':main()
