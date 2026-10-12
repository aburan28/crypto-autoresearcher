"""Run frozen synthetic jobs; known scalar truth used only after kernel returns."""
import argparse, hashlib, json, math, os, platform, random, subprocess, time
from collections import Counter, defaultdict
from pathlib import Path
from common import Stream, limits, sha, write
from finite_math import Curve
from curve_identity import curve_identity


def equivalent(a,b,transport=False):
    if transport:
        return all(a[k]==b[k]for k in ['scalar','censored','iterations','restarts','trace_sha256','collisions'])and all(a['counts'][p]['group_calls']==b['counts'][p]['group_calls']for p in ['setup','search','verification'])
    ignore={'job_id','mode','cpu_seconds','wall_seconds','process_max_RSS_KiB'}
    return {k:v for k,v in a.items()if k not in ignore}=={k:v for k,v in b.items()if k not in ignore}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prep',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--kernel',type=Path,required=True);a=ap.parse_args()
    prep,out=a.prep.resolve(),a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    load=lambda p:json.loads((prep/p).read_text())
    groups=load('public-groups.json');targets=load('public-targets.json');gmap={g['group_id']:g for g in groups};tmap={t['id']:t for t in targets}
    truth={t['id']:t['synthetic_scalar']for t in load('validation-only/synthetic-truth.json')}
    bygroup=defaultdict(list)
    for t in targets:bygroup[t['group_id']].append(t)
    control_small=set();control_large=set()
    for case in ['P-192','P-224']:
        for kind,count,selected in [('small',4,control_small),('large',4,control_large)]:
            selected.update(g['group_id']for g in sorted(groups,key=lambda g:g['group_id'])if g['case']==case and g['arm']=='S'and g['kind']==kind)
            keep=sorted(selected & {g['group_id']for g in groups if g['case']==case})[:count]
            selected.difference_update(g['group_id']for g in groups if g['case']==case);selected.update(keep)
    jobs=[]
    for g in groups:
        for t in bygroup[g['group_id']]:
            if g['kind']=='small':modes=[('rho',16,[1,2,3,4]),('oracle',16,[1,2,3,4]),('rho32',32,[101,102,103,104]),('bsgs',0,[0])]
            elif g['kind']=='easy':modes=[('rho',16,[1,2,3,4]),('bsgs',0,[0])]
            else:modes=[('rho',16,[1])]
            if g['group_id']in control_small:modes +=[(k,16,[1,2,3,4])for k in ['sham','replay','transport','native_iso']]
            if g['group_id']in control_large:modes +=[(k,16,[1])for k in ['replay','transport']]
            cap=math.isqrt(400*g['ell'])+1 if g['kind']in['small','easy']else 4096
            for mode,adding,seeds in modes:
                for seed in seeds:
                    jid='j'+hashlib.sha256(f'{t["id"]}/{mode}/{seed}'.encode()).hexdigest()[:24]
                    jobs.append({'job_id':jid,'group_id':g['group_id'],'target_id':t['id'],'mode':mode,'adding':adding,'seed':seed,'search_cap':cap,'kind':g['kind'],'case':g['case']})
    random.Random(2026101185).shuffle(jobs);write(out/'job-index.json',jobs)
    cpus=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpus[0]})
    write(out/'environment.json',{'python':platform.python_version(),'platform':platform.platform(),'CPU':cpus[0],'allowed_CPUs':cpus,'kernel_sha256':sha(a.kernel),'watchdog_seconds_per_chunk':600,'worker_AS_bytes':4<<30,'solver_interface':'public points/order/seeds/cap only, no family tags or synthetic truth'})
    allrecords={};checks=[];maps={};started=time.monotonic()
    for start in range(0,len(jobs),128):
        chunk=jobs[start:start+128];stage=out/f'chunk-{start//128:04d}';stage.mkdir();public=stage/'public-jobs.txt'
        with public.open('x')as f:
            for j in chunk:
                g=gmap[j['group_id']];t=tmap[j['target_id']];A,B,G,Q,u=g['A'],g['B'],g['G'],t['Q'],1
                if j['mode']in['transport','native_iso']:
                    u=1+Stream('nist-isomorphism/2026101186/'+g['group_id']).below(g['p']-1)
                    A=A*pow(u,4,g['p'])%g['p'];B=B*pow(u,6,g['p'])%g['p']
                    G=[G[0]*pow(u,2,g['p'])%g['p'],G[1]*pow(u,3,g['p'])%g['p']]
                    Q=[Q[0]*pow(u,2,g['p'])%g['p'],Q[1]*pow(u,3,g['p'])%g['p']]
                    if g['group_id']not in maps:
                        cm=dict(g['curve'],a4=A,a6=B,generator=G)
                        maps[g['group_id']]={'source_identity':g['identity'],'destination_identity':curve_identity(g['field'],cm,'nistisomorphism'),'field':g['field'],'curve':cm,'u':u,'map':'(x,y)->(u^2 x,u^3 y), inverse encoding only for transport control'}
                f.write(' '.join(map(str,[j['job_id'],j['mode'],j['adding'],j['seed'],g['p'],A,B,g['ell'],g['h'],*G,*Q,u,j['search_cap']]))+'\n')
        tick=time.monotonic()
        with (stage/'raw-results.jsonl').open('x')as so,(stage/'kernel.stderr').open('x')as se:
            r=subprocess.run([str(a.kernel.resolve()),str(public)],stdout=so,stderr=se,timeout=600,preexec_fn=limits)
        rows=[json.loads(line)for line in (stage/'raw-results.jsonl').read_text().splitlines()if line.strip()]
        index={j['job_id']:j for j in chunk};recovered=0;collisions=0;bsgs=0
        assert r.returncode==0 and len(rows)==len(chunk)
        for rec in rows:
            j=index[rec['job_id']];g=gmap[j['group_id']];t=tmap[j['target_id']];curve=Curve(g['p'],g['A'],g['B'])
            assert rec['ell']==g['ell']and rec['cap']==j['search_cap']and rec['job_id']not in allrecords
            if rec['scalar']is not None:
                assert rec['verified']and rec['scalar']==truth[t['id']]and curve.mul(tuple(g['G']),rec['scalar'])==tuple(t['Q']);recovered+=1
            elif j['mode']=='bsgs':raise RuntimeError('BSGS complete coverage failed')
            for c in rec['collisions']:
                assert c['denominator']==(c['bprime']-c['b'])%g['ell']
                left=curve.add(curve.mul(tuple(g['G']),c['a']),curve.mul(tuple(t['Q']),c['b']))
                right=curve.add(curve.mul(tuple(g['G']),c['aprime']),curve.mul(tuple(t['Q']),c['bprime']))
                assert left==right
                if c['scalar']is not None:assert c['scalar']==(c['a']-c['aprime'])*pow(c['denominator'],-1,g['ell'])%g['ell']
                collisions+=1
            if j['mode']=='bsgs':
                M=rec['M'];assert rec['counts']['setup']['group_calls']==M+M.bit_count()+M.bit_length()-1
                assert rec['counts']['search']['group_calls']==rec['scalar']//M;bsgs+=1
            allrecords[rec['job_id']]=rec
        check={'chunk':start//128,'expected_jobs':len(chunk),'completed_jobs':len(rows),'exit_code':r.returncode,'validated_scalars':recovered,'checked_collision_equations':collisions,'exact_BSGS_accounting':bsgs,'elapsed_seconds':time.monotonic()-tick,'raw_sha256':sha(stage/'raw-results.jsonl')}
        write(stage/'checks.json',check);checks.append(check)
        if start//128%10==0:print('ATTACK_JOBS',len(allrecords),'/',len(jobs),flush=True)
    lookup={(j['target_id'],j['mode'],j['seed']):j['job_id']for j in jobs};controls=[]
    for j in jobs:
        if j['mode']in['sham','replay','transport']:
            base=allrecords[lookup[j['target_id'],'rho',j['seed']]]
            passed=equivalent(base,allrecords[j['job_id']],j['mode']=='transport');assert passed
            controls.append({'job_id':j['job_id'],'control':j['mode'],'pass':passed,'kind':j['kind']})
    write(out/'isomorphism-maps.json',list(maps.values()));write(out/'control-checks.json',controls)
    write(out/'attack-result.json',{'expected_jobs':len(jobs),'completed_jobs':len(allrecords),'mode_counts':dict(Counter(j['mode']for j in jobs)),'groups_by_kind':dict(Counter(g['kind']for g in groups)),
          'integrity_controls_pass':all(c['pass']for c in controls),'exact_control_checks':len(controls),'all_returned_scalars_and_collision_equations_verified':True,'failures':[],
          'BSGS_exact_accounting_jobs':sum(c['exact_BSGS_accounting']for c in checks),'elapsed_seconds':time.monotonic()-started})
    print('ATTACKS_COMPLETE',len(allrecords),'exact controls',len(controls),flush=True)

if __name__=='__main__':main()
