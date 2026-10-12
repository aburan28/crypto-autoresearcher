"""Frozen case/field-cluster summaries, approximate 99.9% intervals and limits."""
import argparse, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import beta
from common import write

REPS=500000


def random_source(domain):
    seed=int.from_bytes(hashlib.sha256(('2026101182/'+domain).encode()).digest()[:8],'big')
    return np.random.default_rng(seed)


def bootstrap_mean(values,domain):
    xs=np.asarray(values,dtype=float);rng=random_source(domain);result=np.empty(REPS)
    if not len(xs):return None
    for i in range(0,REPS,5000):
        count=min(5000,REPS-i);result[i:i+count]=xs[rng.integers(len(xs),size=(count,len(xs)))].mean(axis=1)
    return result


def interval(estimate,samples,log=False):
    conv=math.exp if log else float
    if samples is None:return {'estimate':None,'CI99_9':None,'reason':'no eligible sampled observations'}
    return {'estimate':conv(estimate),'CI99_9':[conv(v)for v in np.quantile(samples,[.0005,.9995])],
      'CI99_9667_reserved_three_primary_tests':[conv(v)for v in np.quantile(samples,[.001/6,1-.001/6])],
      'coverage':'approximate nominal cluster percentile bootstrap, conditional on frozen selection/matching'}


def exact_rate(k,n,alpha=.001):
    if not n:return {'estimate':None,'n':0,'successes':0,'CI99_9':None}
    lo=0. if not k else float(beta.ppf(alpha/2,k,n-k+1))
    hi=1. if k==n else float(beta.ppf(1-alpha/2,k+1,n-k))
    return {'estimate':k/n,'n':n,'successes':k,'CI99_9':[lo,hi],'interval':'exact Clopper-Pearson, iid specified sampled curve/field-target trials only'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);a=ap.parse_args();run=a.run.resolve();out=run/'analysis';out.mkdir(exist_ok=False)
    load=lambda p:json.loads((run/p).read_text());groups=load('preparation/public-groups.json');moduli=load('preparation/prime-sample.json')['moduli'];pairs=load('preparation/matching.json')
    jobs={j['job_id']:j for j in load('attacks/job-index.json')};bygroup=defaultdict(list);allrows=[]
    for p in sorted((run/'attacks').glob('chunk-*/raw-results.jsonl')):
        for line in p.read_text().splitlines():
            r=json.loads(line);j=jobs[r['job_id']];bygroup[j['group_id'],j['mode']].append(r);allrows.append((j,r))
    metrics=[];lookup={}
    for g in groups:
        for mode in ['rho','oracle','rho32','bsgs']:
            rows=bygroup[g['group_id'],mode]
            if not rows:continue
            calls=[r['counts']['search']['group_calls']for r in rows]
            total=[r['counts']['setup']['group_calls']+r['counts']['search']['group_calls']for r in rows]
            if mode=='bsgs':normalized=[total[i]/(r['M']+g['ell']/(2*r['M']))for i,r in enumerate(rows)]
            else:normalized=[min(c/math.sqrt(g['ell']),20)for c in calls]
            row={**{k:g[k]for k in ['group_id','case','arm','kind','modulus_id','ell']},'mode':mode,'attempts':len(rows),
                 'normalized_mean':float(np.mean(normalized)),'search_calls_mean':float(np.mean(calls)),
                 'search_wall_seconds_mean':float(np.mean([r['wall_seconds'][1]for r in rows])),
                 'recovered':sum(r['scalar']is not None for r in rows),'censors':sum(r['censored']for r in rows),
                 'table_allocated_bytes_mean':float(np.mean([r['table_allocated_bytes']for r in rows]))}
            metrics.append(row);lookup[g['group_id'],mode]=row
    write(out/'group-metrics.json',metrics)
    cases={};clusters=[]
    for case in ['P-192','P-224']:
        contrasts={}
        for arm in ['R','C']:
            for mode in ['rho','oracle','rho32','bsgs']:
                for quantity in ['normalized_mean','search_wall_seconds_mean']:
                    byfield=defaultdict(list)
                    for pair in pairs:
                        if pair['case']!=case or pair['control_arm']!=arm:continue
                        s=lookup[pair['S_group'],mode][quantity];c=lookup[pair['control_group'],mode][quantity]
                        if s<=0 or c<=0:continue
                        byfield[pair['control_field']].append(math.log(s/c))
                    vals=[float(np.mean(byfield[k]))for k in sorted(byfield)]
                    key=f'{mode}_S_{arm}'+('_search_wall'if quantity!='normalized_mean'else'')
                    result=interval(float(np.mean(vals))if vals else 0.,bootstrap_mean(vals,case+'/'+key),True)
                    result.update(control_fields=len(vals),matched_pairs=sum(map(len,byfield.values())),weighting='equal random control field; within field equal matched pair')
                    contrasts[key]=result
                    if quantity=='normalized_mean':clusters.extend({'case':case,'arm':arm,'mode':mode,'field':k,'matched_pairs':len(byfield[k]),'mean_log_ratio':float(np.mean(byfield[k]))}for k in sorted(byfield))
        primary=contrasts['rho_S_R'];ci=primary['CI99_9667_reserved_three_primary_tests'];decision='inconclusive'
        if ci and primary['control_fields']>=25 and primary['matched_pairs']>=50:
            if ci[0]>1.2:decision='materially greater generic small-subgroup work in this tested scope'
            elif ci[0]>=1/1.2 and ci[1]<=1.2:decision='practically similar generic small-subgroup work in this tested scope'
            elif ci[1]<1/1.2:decision='materially lower generic small-subgroup work in this tested scope'
        cases[case]={'primary':primary,'decision':decision,'attack_comparisons':contrasts}
    write(out/'matched-field-clusters.json',clusters)
    curves={m['id']:load('preparation/curves/'+m['id']+'/curves.json')['curves']for m in moduli};populations={}
    for case in ['P-192','P-224']:
        srows=curves[case+'-S'];pc={}
        for arm in ['R','C']:
            ms=[m for m in moduli if m['case']==case and m['arm']==arm];first=[curves[m['id']][0]for m in ms]
            endpoints={}
            for label,key in [('small_subgroup_eligibility','small_ell'),('certified_large_factor','large_ell'),('prime_curve_order','order_certified_prime')]:
                kS=sum(bool(r[key])for r in srows);kC=sum(bool(r[key])for r in first)
                # First control curve per field is an independent unconditional sample.
                # Two 99.95% exact rate intervals yield a conservative >=99.9% difference interval.
                sr=exact_rate(kS,len(srows));cr=exact_rate(kC,len(first));sa=exact_rate(kS,len(srows),.0005);ca=exact_rate(kC,len(first),.0005)
                endpoints[label]={'S_rate':sr,'control_first_curve_rate':cr,'difference_S_minus_control':{'estimate':sr['estimate']-cr['estimate'],
                    'CI99_9':[sa['CI99_9'][0]-ca['CI99_9'][1],sa['CI99_9'][1]-ca['CI99_9'][0]],'coverage':'conservative exact marginal >=99.9%; independent first control curve per field'},
                    'all_control_model_count':4*len(ms),'all_control_model_hits':sum(bool(r[key])for m in ms for r in curves[m['id']])}
            sv=[r['trace']/(2*math.sqrt(r['p']))for r in srows];cv=[float(np.mean([r['trace']/(2*math.sqrt(r['p']))for r in curves[m['id']]]))for m in ms]
            ds=bootstrap_mean(sv,case+'/trace/S/'+arm)-bootstrap_mean(cv,case+'/trace/'+arm)
            endpoints['normalized_trace_difference']=interval(float(np.mean(sv)-np.mean(cv)),ds)
            pc[arm]=endpoints
        populations[case]=pc
    bounded={}
    for case in ['P-192','P-224']:
        bounded[case]={}
        for arm in ['S','R','C']:
            rows=[m for m in metrics if m['case']==case and m['arm']==arm and m['kind']=='large'and m['mode']=='rho']
            k=sum(r['recovered']for r in rows);n=sum(r['attempts']for r in rows)
            bounded[case][arm]={**exact_rate(k,n),'censors':sum(r['censors']for r in rows),'search_cap_group_calls':4096,'interpretation':'specified bounded recovery probability; zero recovery is inconclusive for cryptographic ECDLP resistance'}
        anchors=[m for m in metrics if m['case']==case and m['kind']=='standard-anchor']
        bounded[case]['standard_anchor']=anchors
    arith=load('arithmetic/observations.json');amap=defaultdict(list)
    for r in arith:amap[r['modulus_id'],r['backend'],r['workload']].append(r['seconds_per_operation'])
    arithmetic={}
    for case in ['P-192','P-224']:
        ac={}
        for work in ['products','inversions','point_additions']:
            fixed=float(np.median(amap[case+'-S','builtin',work]));wr={}
            for arm in ['R','C']:
                xs=[math.log(fixed/float(np.median(amap[m['id'],'builtin',work])))for m in moduli if m['case']==case and m['arm']==arm]
                wr['S_'+arm]=interval(float(np.mean(xs)),bootstrap_mean(xs,case+'/arithmetic/'+arm+'/'+work),True)
                wr['S_'+arm]['limitation']='conditional on one fixed S five-batch median; interval covers sampled control-field variation, excludes S systematic timing error'
            wr['S_builtin_seconds_per_operation']=fixed
            wr['S_Python_fold_over_builtin_ratio']=float(np.median(amap[case+'-S','fold',work]))/fixed
            ac[work]=wr
        arithmetic[case]=ac
    attack_result=load('attacks/attack-result.json');prep=load('preparation/preparation-result.json');ar=load('arithmetic/arithmetic-result.json')
    summary={'experiment_id':'EXP-ECDLP-5184f7','run_id':run.name,'cases':cases,'population':populations,'bounded_large_subgroups':bounded,'arithmetic':arithmetic,
      'counts':prep,'attack_jobs':len(allrows),'small_main_rho_censors':sum(r['censored']for j,r in allrows if j['kind']=='small'and j['mode']in['rho','oracle','rho32']),
      'integrity_controls':attack_result,'arithmetic_integrity':ar,'inference':{'bootstrap_replicates':REPS,'seed':2026101182,'marginal_confidence':.999,'three_family_primary_confidence':1-.001/3,
       'joint_scope':'Bonferroni reserves three primary tests including prior wider Solinas test; diagnostics marginal only','matching_not_resampled':True},
      'limitations':['small subgroup attacks do not measure 192/224-bit subgroup resistance','partial factorization leaves composite cofactors unresolved','no number-field rank experiment in this run','single S prime per case','cluster bootstrap nominal coverage approximate','large zero-recovery outcomes inconclusive','no independent scientific review or sealed bound']}
    write(out/'summary.json',summary)
    print(json.dumps({'run_id':run.name,'attack_jobs':len(allrows),'cases':{k:{'primary':v['primary'],'decision':v['decision']}for k,v in cases.items()}},indent=2),flush=True)

if __name__=='__main__':main()
