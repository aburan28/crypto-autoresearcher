#!/usr/bin/env python3
"""Frozen rare-event count analysis; windows, not points, are trials."""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.stats import beta, binomtest, t
from research import ARMS, check_record, jobs_for, model_for, put_json
from metrics import fair_coin_run_probability


def cp(hits,n,alpha):
    return [0.0 if not hits else float(beta.ppf(alpha/2,hits,n-hits+1)),
            1.0 if hits==n else float(beta.ppf(1-alpha/2,hits+1,n-hits))]


def mcnemar(flags,a,b):
    ab=int(np.sum(flags[:,a]&~flags[:,b]));ba=int(np.sum(~flags[:,a]&flags[:,b]))
    return {'a_only':ab,'b_only':ba,'discordant':ab+ba,
            'p_two_sided_exact':float(binomtest(ab,ab+ba,.5).pvalue) if ab+ba else 1.0}


def welch(x,y,alpha):
    x=np.asarray(x);y=np.asarray(y);vx=float(np.var(x,ddof=1)/len(x));vy=float(np.var(y,ddof=1)/len(y))
    difference=float(np.mean(x)-np.mean(y));se=(vx+vy)**.5
    if not se:return {'difference':difference,'se':0.0,'df':None,'interval':[difference,difference],'p_two_sided_approx':1.0 if difference==0 else 0.0}
    df=(vx+vy)**2/(vx*vx/(len(x)-1)+vy*vy/(len(y)-1)); radius=float(t.ppf(1-alpha/2,df))*se
    return {'difference':difference,'se':se,'df':df,'interval':[difference-radius,difference+radius],
            'p_two_sided_approx':float(2*t.sf(abs(difference/se),df))}


def analyze(run):
    run=Path(run);design=json.loads((run/'design.json').read_text());inputs=design['inputs'];config=design['config']
    completion=json.loads((run/'completion.json').read_text())
    if not completion['fixed_sample_complete']:raise ValueError('Incomplete fixed sample')
    alpha=config['familywise_alpha']/config['primary_tests'];by_model={};chunkrates={};tails=[]
    for job in jobs_for(inputs,config):
        record=json.loads((run/'records'/f"{job['id']}.json").read_text());check_record(run,record)
        model=model_for(inputs,job);cohorts=3 if job['named'] else 1
        scores=np.fromfile(run/'artifacts'/job['id']/'scores.bin',dtype='<u4').reshape(job['count'],cohorts,3)
        metric=model['metric_index'] if job['named'] else 0;threshold=model['threshold_integer'] if job['named'] else 22
        by_model.setdefault(job['model'],[]).append((job['offset'],scores))
        chunkrates.setdefault(job['model'],[]).append(float(np.mean(scores[:,0,metric]>=threshold)))
    candidates=[];tests=[]
    for model in inputs['candidates']:
        scores=np.concatenate([s for _,s in sorted(by_model[model['id']])]);n=len(scores)
        flags=scores[:,:,model['metric_index']]>=model['threshold_integer'];rates=[]
        for i,arm in enumerate(ARMS):
            hits=int(flags[:,i].sum());rates.append({'cohort':arm,'hits':hits,'windows':n,'rate':hits/n,
                'cp_interval':cp(hits,n,config['rate_interval_alpha']/9)})
        candidates.append({'id':model['id'],'metric':model['metric'],'threshold_integer':model['threshold_integer'],'rates':rates})
        for a,b in ((0,2),(1,2),(0,1)):
            result=mcnemar(flags,a,b);difference=rates[a]['rate']-rates[b]['rate']
            tests.append({'id':f"{model['id']}:{ARMS[a]}-vs-{ARMS[b]}",'method':'exact conditional McNemar',
                'candidate':model['id'],'a':ARMS[a],'b':ARMS[b],'difference':difference,
                'difference_interval_from_simultaneous_marginals':[rates[a]['cp_interval'][0]-rates[b]['cp_interval'][1],rates[a]['cp_interval'][1]-rates[b]['cp_interval'][0]],
                **result,'passes_family_threshold':result['p_two_sided_exact']<=alpha})
        if model['metric_index']==0:
            for threshold in config['longrun_spectrum']:
                for i,arm in enumerate(ARMS):
                    hits=int(np.sum(scores[:,i,0]>=threshold));tails.append({'cohort':arm,'threshold':threshold,
                        'hits':hits,'windows':n,'rate':hits/n,'cp_interval':cp(hits,n,.001/(len(config['longrun_spectrum'])*3)),
                        'fair_coin_reference':fair_coin_run_probability(256,threshold)})
    fields=[]
    for model in inputs['ordinary_controls']:
        scores=np.concatenate([s for _,s in sorted(by_model[model['id']])]);hits=int(np.sum(scores[:,0,0]>=22));n=len(scores)
        fields.append({'id':model['id'],'arm':model['arm'],'model_uid':model['model_uid'],'hits':hits,'windows':n,'rate':hits/n,
                       'N':model['N'],'order_is_prime':model['order_is_prime']})
    longrun=next(m for m in inputs['candidates'] if m['metric_index']==0)
    for arm in ('R','C'):
        sample=[f['rate'] for f in fields if f['arm']==arm];result=welch(chunkrates[longrun['id']],sample,alpha)
        tests.append({'id':f'P-224-selected-vs-ordinary-{arm}','method':'approximate Welch, S chunks and ordinary fields as units',
            'S_chunks':len(chunkrates[longrun['id']]),'ordinary_fields':len(sample),'ordinary_mean_rate':float(np.mean(sample)),
            **result,'passes_family_threshold':result['p_two_sided_approx']<=alpha})
    if len(tests)!=config['primary_tests']:raise ValueError('Test family count mismatch')
    result={'schema':1,'scope':'Observations; no hypothesis-state transition, prime-family causal claim, or ECDLP conclusion',
        'point_observations':completion['point_observations'],'primary_family':{'tests':len(tests),'alpha':config['familywise_alpha'],
        'per_test_alpha':alpha,'coverage':'Exact 9 paired tests; approximate 2 field tests. Bonferroni nominal 99.9%; field approximation is not an exact coverage guarantee.'},
        'rate_family':'9 two-sided CP intervals, Bonferroni nominal at least 99.9% under independent windows',
        'tail_family':'24 separate exploratory CP intervals, Bonferroni nominal at least 99.9%; not a combined family with primary/rate intervals',
        'candidates':candidates,'primary_tests':tests,'tail_spectrum':tails,'ordinary_fields':fields,
        'limitations':['Fixed seeds are reproducible pseudorandom samples. All points within a window are dependent.',
            'Ordinary controls reuse previous prime pools, match A=-3, B and step x, but do not match group order or generator order.',
            'One selected S prime per named curve cannot establish a population-wide Solinas-prime effect.',
            'Fair-coin probabilities are an explicit benchmark, not an assumption that curve-point bits are IID.',
            'Paired power assumes independent arm flags for planning; exact paired tests retain observed dependence.',
            'Events outside fixed bit/thresholds and effects substantially rarer than 1e-5 remain outside the powered scope.']}
    put_json(run/'analysis.json',result);return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path);args=parser.parse_args()
    result=analyze(args.run);print(json.dumps({'point_observations':result['point_observations'],'primary_tests':len(result['primary_tests']),
        'threshold_passes':sum(t['passes_family_threshold'] for t in result['primary_tests'])}))
