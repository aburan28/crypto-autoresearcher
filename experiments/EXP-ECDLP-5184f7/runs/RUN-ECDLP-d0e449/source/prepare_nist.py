"""Fixed full-size fields; ordinary uniform models and public synthetic groups."""
import argparse, concurrent.futures, hashlib, json, math, subprocess, time
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment
from common import GP, Stream, generator, gp_environment, gp_file, limits, sha, write
from finite_math import Curve
from curve_identity import curve_identity


def sample(out, plan):
    selected=[];used={r['p'] for r in plan['prime_cases']};draws=[]
    queries=(out/'prime-proof-queries.gp').open('x')
    outputs=(out/'prime-proof-results.stdout').open('x')
    stderr=(out/'prime-proof.stderr').open('x')
    proc=subprocess.Popen([str(GP),'-q','-f','-s','128M'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                          stderr=stderr,text=True,env=gp_environment(),preexec_fn=limits)
    def prime(p):
        q=f'print(isprime({p}));\n';queries.write(q);queries.flush()
        proc.stdin.write(q);proc.stdin.flush();s=proc.stdout.readline();outputs.write(s);outputs.flush()
        if not s.strip() in ['0','1']:raise RuntimeError('primality process failed')
        return int(s)
    try:
        for case in plan['prime_cases']:
            label,p,bits=case['label'],case['p'],case['bits']
            assert prime(p)
            selected.append({'id':label+'-S','case':label,'arm':'S','p':p,'bits':bits,'models':512})
            for arm,count in plan['random_fields_per_case'].items():
                for i in range(count):
                    rng=Stream(f'nist-prime/{plan["sampling_seed"]}/{label}/{arm}/{i}')
                    lo=max((99*p+99)//100,1<<(bits-1));hi=min(101*p//100,(1<<bits)-1)
                    lo+=lo%2==0
                    for attempt in range(50000):
                        q=lo+2*rng.below((hi-lo)//2+1)
                        why='used' if q in used else 'residue' if arm=='C' and q%12!=p%12 else None
                        flag=None
                        if why is None:flag=prime(q);why=None if flag else 'composite'
                        draws.append({'case':label,'arm':arm,'field_index':i,'draw':attempt,'p':q,'isprime':flag,'rejection':why})
                        if why is None:used.add(q);break
                    else:raise RuntimeError('prime candidate limit')
                    selected.append({'id':f'{label}-{arm}{i:03d}','case':label,'arm':arm,'p':q,'bits':bits,'models':4})
                    if (i+1)%36==0:print('PRIMES',label,arm,i+1,flush=True)
    finally:
        if proc.poll() is None:proc.stdin.write('quit;\n');proc.stdin.flush();proc.wait(timeout=10)
        queries.close();outputs.close();stderr.close()
    write(out/'control-prime-draws.json',draws)
    write(out/'prime-sample.json',{'moduli':selected,'globally_distinct_moduli':len(used)})
    return selected


def count_chunk(out, modulus, rows, chunk):
    stage=out/'curves'/modulus['id']/f'chunk-{chunk:03d}';stage.mkdir(parents=True,exist_ok=False)
    p=modulus['p'];source=stage/'point-counts.gp'
    source.write_text(f'p={p};setrand({2026101183+chunk});v=['+','.join(f'[{r["A"]},{r["B"]}]' for r in rows)+'];\n'+
        'for(i=1,#v,E=ellinit(v[i],p);N=ellcard(E);F=factor(N,2^20);'
        'P=vector(matsize(F)[1],j,isprime(F[j,1]));'
        'print([i-1,N,lift(E.j),Vec(F[,1]),Vec(F[,2]),P,isprime(N)]));\nquit;\n')
    raw,process=gp_file(source,stage/'point-counts')
    results=[json.loads(s)for s in raw.splitlines()if s.strip()]
    assert len(results)==len(rows)
    for row,result in zip(rows,results,strict=True):
        idx,N,j,factors,exponents,primes,Nprime=result
        assert idx==row['chunk_index'];assert math.prod(q**e for q,e in zip(factors,exponents))==N
        trace=p+1-N;assert trace*trace<=4*p
        flags={'anomalous':N==p,'supersingular':trace%p==0,'j_special':j in [0,1728%p]}
        small=[];large=[]
        for q,e,prime in zip(factors,exponents,primes,strict=True):
            if q<(1<<20):assert prime
            embedding=next((k for k in range(1,21)if pow(p,k,q)==1),None)if prime else None
            if prime and e==1 and embedding is None and not any(flags.values()):
                if 16<=q.bit_length()<=20:small.append(q)
                if q.bit_length()>=128:large.append(q)
        row.update(N=N,j=j,trace=trace,frobenius_discriminant=trace*trace-4*p,
                   partial_factors=[{'q':q,'exponent':e,'certified_prime':bool(flag)}for q,e,flag in zip(factors,exponents,primes)],
                   order_certified_prime=bool(Nprime),flags=flags,small_ell=min(small)if small else None,
                   large_ell=max(large)if large else None,
                   factorization_complete=all(primes),endomorphism_conductor=None)
    write(stage/'rows.json',rows)
    write(stage/'process.json',process)
    print('ORDERS',modulus['id'],chunk,len(rows),round(process['elapsed_seconds'],2),flush=True)
    return modulus['id'],rows


def models(out, moduli, excluded):
    jobs=[];rejects=Counter()
    for m in moduli:
        rng=Stream(f'nist-curve/2026101181/{m["id"]}');rows=[];draws=[];p=m['p']
        while len(rows)<m['models']:
            A,B=rng.below(p),rng.below(p);bad=(p,A,B)in excluded
            singular=(4*pow(A,3,p)+27*B*B)%p==0
            draws.append({'draw':len(draws),'A':A,'B':B,'singular':singular,'excluded_probe':bad})
            if bad or singular:rejects['probe'if bad else'singular']+=1;continue
            rows.append({'index':len(rows),'modulus_id':m['id'],'p':p,'A':A,'B':B,'case':m['case'],'arm':m['arm']})
        stage=out/'curves'/m['id'];stage.mkdir(parents=True)
        write(stage/'coefficient-draws.json',draws)
        for start in range(0,len(rows),16):
            part=[dict(r,chunk_index=i)for i,r in enumerate(rows[start:start+16])]
            jobs.append((m,part,start//16))
    allrows={m['id']:[]for m in moduli}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
        fs=[pool.submit(count_chunk,out,*job)for job in jobs]
        for future in concurrent.futures.as_completed(fs):
            mid,rows=future.result();allrows[mid].extend(rows)
    for m in moduli:
        rows=sorted(allrows[m['id']],key=lambda r:r['index'])
        assert len(rows)==m['models'] and [r['index']for r in rows]==list(range(m['models']))
        allrows[m['id']]=rows
        write(out/'curves'/m['id']/'curves.json',{'modulus':m,'curves':rows,'factorization':'bounded partial; prime flags exact'})
    return allrows,dict(rejects)


def match(left,right):
    if not left or not right:return []
    costs=np.full((len(left),len(right)+len(left)),100.)
    for i,l in enumerate(left):
        for j,r in enumerate(right):
            q,s=l['small_ell'],r['small_ell']
            if max(q,s)*10<=min(q,s)*11:costs[i,j]=abs(math.log(q/s))
            else:costs[i,j]=1e6
    a,b=linear_sum_assignment(costs)
    return [(left[i],right[j])for i,j in zip(a,b)if j<len(right)and costs[i,j]<100]


def group(row,m,ell,kind):
    curve=Curve(row['p'],row['A'],row['B']);G,draws=generator(row,ell,domain='nist-group')
    field={'characteristic':row['p'],'degree':1,'representation':'prime field, canonical integer residues','element_encoding':'integers 0..p-1','modulus':row['p']}
    cm={'model':'short-Weierstrass','a4':row['A'],'a6':row['B'],'subgroup_order':ell,'cofactor':row['N']//ell,'generator':G,'target_group':'prime-order cyclic subgroup of E(F_p)'}
    return {'group_id':m['id']+f'-{row["index"]:04d}-{kind}','modulus_id':m['id'],'case':m['case'],'arm':m['arm'],'bits':m['bits'],'candidate_index':row['index'],
            'p':row['p'],'A':row['A'],'B':row['B'],'N':row['N'],'ell':ell,'h':row['N']//ell,'G':G,'generator_draws':draws,'kind':kind,
            'field':field,'curve':cm,'identity':curve_identity(field,cm,'nistcomparison')}


def anchors(out, cases):
    params=[
      ('P-192','64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1','ffffffffffffffffffffffff99def836146bc9b1b4d22831','188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012','07192b95ffc8da78631011ed6b24cdd573f977a11e794811'),
      ('P-224','b4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4','ffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d','b70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21','bd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34')]
    result=[]
    for label,b,n,x,y in params:
        case=next(c for c in cases if c['label']==label);p=case['p'];A=p-3;B=int(b,16);ell=int(n,16);G=[int(x,16),int(y,16)]
        curve=Curve(p,A,B);assert curve.on_curve(tuple(G))and curve.mul(tuple(G),ell)is None
        src=out/(label+'-anchor.gp');src.write_text(f'p={p};E=ellinit([{A},{B}],p);print([ellcard(E),isprime({ell})]);\nquit;\n')
        raw,timing=gp_file(src,out/(label+'-anchor'));assert json.loads(raw.strip())==[ell,1]
        row={'p':p,'A':A,'B':B,'N':ell,'index':0,'modulus_id':label+'-standard'}
        m={'id':label+'-standard','case':label,'arm':'S','bits':case['bits']}
        g=group(row,m,ell,'standard-anchor');g['G']=G;g['curve']['generator']=G
        g['identity']=curve_identity(g['field'],g['curve'],'niststandard');g['parameter_provenance']='Public NIST parameter constants, verified internally by PARI ellcard, exact prime proof and nG=O; no external source fetched'
        result.append(g)
    write(out/'standard-anchors.json',result)
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--probe',type=Path,required=True);a=ap.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic();plan=json.loads(a.plan.read_text())
    excluded={(r['p'],A,B)for r in json.loads(a.probe.read_text())for A,B in r['rows']}
    moduli=sample(out,plan);allrows,rejects=models(out,moduli,excluded)
    lookup={m['id']:m for m in moduli};groups={};pairs=[];selected=[]
    for case in plan['prime_cases']:
        label=case['label'];left=[r for r in allrows[label+'-S']if r['small_ell']]
        for arm in ['R','C']:
            right=[r for m in moduli if m['case']==label and m['arm']==arm for r in allrows[m['id']]if r['small_ell']]
            matched=match(left,right)
            for l,r in matched:
                gs=group(l,lookup[l['modulus_id']],l['small_ell'],'small')if l['modulus_id']+f'-{l["index"]:04d}-small'not in groups else groups[l['modulus_id']+f'-{l["index"]:04d}-small']
                gr=group(r,lookup[r['modulus_id']],r['small_ell'],'small')
                groups[gs['group_id']]=gs;groups[gr['group_id']]=gr
                pairs.append({'case':label,'control_arm':arm,'S_group':gs['group_id'],'control_group':gr['group_id'],'control_field':r['modulus_id'],'ell_ratio':gs['ell']/gr['ell']})
            selected.append({'case':label,'arm':arm,'S_eligible_curves':len(left),'control_eligible_curves':len(right),'matched_pairs':len(matched),'distinct_matched_fields':len({r['modulus_id']for _,r in matched})})
        for m in [m for m in moduli if m['case']==label]:
            rows=[r for r in allrows[m['id']]if r['large_ell']]
            chosen=rows[:64]if m['arm']=='S'else rows[:1]
            for r in chosen:
                g=group(r,m,r['large_ell'],'large');groups[g['group_id']]=g
        sm=lookup[label+'-S'];easy=None
        for r in allrows[sm['id']]:
            q=next((f['q']for f in r['partial_factors']if f['q']in[5,7,11,13]and f['exponent']==1),None)
            if q:easy=group(r,sm,q,'easy');break
        if easy:groups[easy['group_id']]=easy
    for g in anchors(out,plan['prime_cases']):groups[g['group_id']]=g
    targets=[];truth=[]
    for g in sorted(groups.values(),key=lambda g:g['group_id']):
        count=4 if g['kind']in['small','easy']else 1;curve=Curve(g['p'],g['A'],g['B']);rng=Stream('nist-target/2026101184/'+g['group_id'])
        for i in range(count):
            q=1+rng.below(g['ell']-1);Q=list(curve.mul(tuple(g['G']),q));tid=g['group_id']+f'-t{i}'
            targets.append({'id':tid,'group_id':g['group_id'],'target_index':i,'Q':Q,'curve_uid':g['identity']['curve_uid']})
            truth.append({'id':tid,'synthetic_scalar':q})
    write(out/'matching.json',pairs);write(out/'selection-summary.json',selected)
    write(out/'public-groups.json',list(groups.values()));write(out/'public-targets.json',targets);write(out/'validation-only/synthetic-truth.json',truth)
    write(out/'preparation-result.json',{'moduli':len(moduli),'random_control_fields':len(moduli)-2,'uniform_models':sum(map(len,allrows.values())),
          'groups_by_kind':dict(Counter(g['kind']for g in groups.values())),'public_targets':len(targets),'selection':selected,'rejected_coefficients':rejects,'elapsed_seconds':time.monotonic()-started,
          'sample_and_matching_frozen_before_attacks':True,'source_hashes':{p.name:sha(p)for p in Path(__file__).parent.glob('*.py')}})
    print('PREPARATION_COMPLETE',len(moduli),'models',sum(map(len,allrows.values())),dict(Counter(g['kind']for g in groups.values())),flush=True)

if __name__=='__main__':main()
