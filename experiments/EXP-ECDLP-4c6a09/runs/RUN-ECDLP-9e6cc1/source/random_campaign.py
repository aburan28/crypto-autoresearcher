#!/usr/bin/env python3
"""Execute the frozen random-field draw and checked matched descents."""
import concurrent.futures
import hashlib
import json
import platform
import resource
import subprocess
import time
from pathlib import Path

import run_rank
from gp_tables import execute, polynomial, prelude, write

RUN = Path(__file__).resolve().parent.parent
REPO = RUN.parents[3]

def sample_fields():
    candidates = json.loads((RUN/'sampling-candidates.json').read_text())
    gpvec = '['+','.join('['+str(c['seed'])+','+str(c['draw'])+','+polynomial(c['g'])+']' for c in candidates)+']'
    code = prelude() + '\n'.join([
        '{main()=',
        f'my(C={gpvec},seen=[polredabs(y^3-y-1),polredabs(y^3+y-1),polredabs(y^3-3)],chosen=List(),seed=0,n=0,P,R,D);',
        'for(i=1,#C,if(C[i][1]!=seed,if(seed && n!=8,error("Insufficient accepted fields"));seed=C[i][1];n=0);if(n==8,next);P=C[i][3];',
        'if(!polisirreducible(P),print("@@REJECT|",C[i][1],"|",C[i][2],"|reducible");next);R=polredabs(P);',
        'if(setsearch(Set(seen),R),print("@@REJECT|",C[i][1],"|",C[i][2],"|isomorphic_duplicate|",R);next);',
        'D=nfdisc(P);seen=concat(seen,[R]);listput(chosen,P);n++;print("@@ACCEPT|",C[i][1],"|",C[i][2],"|",R,"|",D);',
        'for(kj=1,3,print("@@ROOTS|",#chosen,"|",[6,7,12][kj],"|",lift(polrootsmod(P,(2^([6,7,12][kj]))^3-2^([6,7,12][kj])-1))));',
        ');if(n!=8,error("Final sample incomplete"));',
        'for(i=1,#chosen,for(j=1,i-1,if(nfisisom(chosen[i],chosen[j])!=0,error("Pairwise isomorphic sample"))));',
        'print("@@PAIRWISE_ISOMORPHISM_CHECK|",#chosen,"|passed");};',
        'iferr(main(),E,print("@@ERROR|",E));print("@@DONE");quit;'])+'\n'
    output, process = execute(RUN/'sampling', code, watchdog=120)
    draws = {(c['seed'],c['draw']):c for c in candidates}
    accepted, trace = [], []
    for line in output.splitlines():
        parts = line.split('|')
        if parts[0] in ('@@ACCEPT','@@REJECT'):
            record = dict(draws[(int(parts[1]),int(parts[2]))])
            if parts[0]=='@@ACCEPT':
                record.update({'field_id':f'random-{len(accepted)+1:02d}',
                               'canonical_polynomial_gp':parts[3], 'field_discriminant':int(parts[4]),'roots':{}})
                accepted.append(record)
            trace.append({**record,'decision':parts[0][2:].lower(),'details':parts[3:]})
        elif parts[0]=='@@ROOTS':
            roots = [int(x.strip()) for x in parts[3].strip('[]').split(',') if x.strip()]
            accepted[int(parts[1])-1]['roots'][parts[2]] = roots
    assert len(accepted)==24 and '@@PAIRWISE_ISOMORPHISM_CHECK|24|passed' in output
    jobs=[]
    for field in accepted:
        for a,b in [(-3,3),(7,1)]:
            jobs.append({'id':f"{field['field_id']}-a{a}-b{b}",'A':a,'B':b,'g':field['g'],
                         'degree':3,'field':field['field_id'],'seed':1,'draw_seed':field['seed'],
                         'draw_index':field['draw'],'field_discriminant':field['field_discriminant'],
                         'canonical_polynomial_gp':field['canonical_polynomial_gp']})
    write(RUN/'sampling-result.json',{'fields':accepted,'draw_trace':trace,'jobs':jobs,
                                    'process':process,'pairwise_nfisisom_passed':True})
    return jobs

def main():
    write(RUN/'launch.json',{'started_at_utc':run_rank.stamp(),
          'command_argv':['python3',str(Path(__file__).resolve())],
          'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
          'platform':platform.platform(),'python':platform.python_version(),'pari':'2.17.2',
          'plan_sha256':hashlib.sha256((RUN/'plan.json').read_bytes()).hexdigest(),
          'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (RUN/'source').iterdir() if p.is_file()},
          'inference_identity':'GPT-6 (system identity); no provider probe',
          'requested_policy':'executor-implementation','fallback_used':False,
          'independent_review_performed':False})
    jobs = sample_fields()
    print('SAMPLE_COMPLETE',len(jobs)//2,'distinct fields',len(jobs),'descents',flush=True)
    start=time.monotonic()
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(run_rank.execute,j,area='random-ranks',watchdog=120) for j in jobs]
        for future in concurrent.futures.as_completed(futures):
            r=future.result()
            results.append(r)
            print('RANK',r['job']['id'],r['status'],r['nf_bounds'],round(r['elapsed_seconds'],3),flush=True)
    usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    write(RUN/'random-ranks-result.json',{'nf':sorted(results,key=lambda r:r['job']['id']),
          'process':{'elapsed_seconds':time.monotonic()-start,'finished_at_utc':run_rank.stamp(),
                     'user_cpu_seconds':usage.ru_utime,'system_cpu_seconds':usage.ru_stime,
                     'peak_child_rss_kib':usage.ru_maxrss}})
    print('RANKS_FINISHED',len(results),round(time.monotonic()-start,3),flush=True)

if __name__=='__main__':
    main()
