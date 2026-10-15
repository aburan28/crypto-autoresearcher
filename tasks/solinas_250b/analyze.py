#!/usr/bin/env python3
"""Infer only after the exact fixed target has completed and passed checks."""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.stats import beta,binomtest,t
from campaign import read_record
from common import ARMS,jobs_for,model_for,put_json
from counts import discordance
from metrics import fair_coin_run_probability


def cp(hits,n,alpha):
    return [0.0 if not hits else float(beta.ppf(alpha/2,hits,n-hits+1)),
            1.0 if hits==n else float(beta.ppf(1-alpha/2,hits+1,n-hits))]


def welch(left,right,alpha):
    left=np.asarray(left);right=np.asarray(right)
    vx=float(np.var(left,ddof=1)/len(left));vy=float(np.var(right,ddof=1)/len(right))
    difference=float(np.mean(left)-np.mean(right));se=(vx+vy)**.5
    if not se:return {'difference':difference,'interval':[difference,difference],'p_two_sided_approx':1.0 if not difference else 0.0,'df':None,'se':0.0}
    df=(vx+vy)**2/(vx*vx/(len(left)-1)+vy*vy/(len(right)-1));radius=float(t.ppf(1-alpha/2,df))*se
    return {'difference':difference,'interval':[difference-radius,difference+radius],'p_two_sided_approx':float(2*t.sf(abs(difference/se),df)),'df':df,'se':se}


def analyze(run):
    run=Path(run);completion=json.loads((run/'completion.json').read_text())
    if not completion['fixed_sample_complete']:raise ValueError('No fixed-sample inference from incomplete run')
    design=json.loads((run/'design.json').read_text());inputs=design['inputs'];config=design['config'];models={};chunks={};integrity={}
    jobs=jobs_for(inputs,config);expected={j['id'] for j in jobs}
    if {p.parent.name for p in (run/'records').glob('*/record.json.gz') if not p.parent.name.startswith('.')}!=expected:raise ValueError('Missing/extra immutable chunk record')
    for job in jobs:
        row=read_record(run/'records'/job['id']/'record.json.gz')
        if row['design_sha256']!=completion['design_sha256'] or row['validity']!='passed_online_and_independent_chunk_checks':raise ValueError('Invalid chunk')
        model=model_for(inputs,job);group=models.setdefault(model['id'],{'windows':0,'events':{}});group['windows']+=job['count']
        for name,event in row['counts']['events'].items():
            target=group['events'].setdefault(name,{'hits':[0]*len(event['hits']),'joint_counts':[0]*len(event['joint_counts'])})
            if sum(event['joint_counts'])!=job['count']:raise ValueError('Joint count total mismatch')
            for c,hits in enumerate(event['hits']):
                if hits!=sum(n for mask,n in enumerate(event['joint_counts']) if (mask>>c)&1):raise ValueError('Joint/marginal mismatch')
                target['hits'][c]+=hits
            target['joint_counts']=[a+b for a,b in zip(target['joint_counts'],event['joint_counts'])]
        if job['named'] and model['metric_index']==0:
            chunks.setdefault(model['id'],[]).append(row['counts']['events']['run22']['hits'][0]/job['count'])
        for key,value in row['verification'].items():integrity[key]=integrity.get(key,0)+value
    rates=[];tests=[];alpha=config['familywise_alpha']/config['primary_tests']
    for model in inputs['candidates']:
        group=models[model['id']];n=group['windows']
        primary=[f'run{k}' for k in config['primary_longrun_thresholds']] if model['metric_index']==0 else [model['metric']]
        for name,event in group['events'].items():
            for c,arm in enumerate(ARMS):
                hits=event['hits'][c];row={'candidate':model['id'],'event':name,'cohort':arm,'hits':hits,'windows':n,'rate':hits/n,'cp_interval':cp(hits,n,config['rate_interval_alpha']/30)}
                if name.startswith('run'):row['fair_coin_reference']=fair_coin_run_probability(256,int(name[3:]))
                rates.append(row)
            if name in primary:
                for a,b in ((0,2),(1,2),(0,1)):
                    ab,ba=discordance(event['joint_counts'],a,b);p=float(binomtest(ab,ab+ba,.5).pvalue) if ab+ba else 1.0
                    ra=next(r for r in rates if r['candidate']==model['id'] and r['event']==name and r['cohort']==ARMS[a])
                    rb=next(r for r in rates if r['candidate']==model['id'] and r['event']==name and r['cohort']==ARMS[b])
                    tests.append({'id':f"{model['id']}:{name}:{ARMS[a]}-vs-{ARMS[b]}",'method':'exact paired McNemar',
                        'a_only':ab,'b_only':ba,'p_two_sided_exact':p,'difference':ra['rate']-rb['rate'],
                        'difference_interval_from_simultaneous_marginals':[ra['cp_interval'][0]-rb['cp_interval'][1],ra['cp_interval'][1]-rb['cp_interval'][0]],
                        'rate_ratio_interval_from_simultaneous_marginals':[ra['cp_interval'][0]/rb['cp_interval'][1],ra['cp_interval'][1]/rb['cp_interval'][0]] if rb['cp_interval'][0]>0 else None,
                        'passes_family_threshold':p<=alpha})
    fields=[]
    for model in inputs['ordinary_controls']:
        group=models[model['id']];fields.append({'id':model['id'],'arm':model['arm'],'model_uid':model['model_uid'],'N':model['N'],
            'windows':group['windows'],'events':{name:{'hits':event['hits'][0],'rate':event['hits'][0]/group['windows']} for name,event in group['events'].items()}})
    longrun=next(m for m in inputs['candidates'] if m['metric_index']==0)
    for arm in ('R','C'):
        control=[f['events']['run22']['rate'] for f in fields if f['arm']==arm];result=welch(chunks[longrun['id']],control,alpha)
        tests.append({'id':f'P-224-selected-run22-vs-{arm}','method':'approximate Welch; S chunks and ordinary fields as units',
            'S_chunks':len(chunks[longrun['id']]),'ordinary_fields':len(control),'ordinary_mean_rate':float(np.mean(control)),**result,
            'passes_family_threshold':result['p_two_sided_approx']<=alpha})
    if len(tests)!=20 or len(rates)!=30:raise ValueError('Prospective family sizes changed')
    result={'schema':1,'point_observations':completion['point_observations'],'primary_tests':tests,'rates':rates,'ordinary_fields':fields,
        'integrity':integrity,'familywise_alpha':config['familywise_alpha'],'per_primary_test_alpha':alpha,
        'confidence_scope':'Primary20-test family nominal99.99%, with two approximate field tests; separate30-rate CP family nominal at least99.99% under independent windows. Their union is nominal99.98% subject to Welch approximation.',
        'limitations':['Independent starts are pseudorandom; adjacent walk points are dependent.','One fixed S curve per named case cannot establish a Solinas-prime population effect.',
            'Ordinary fields reuse earlier prime pools; coefficients/step x matched, group/step orders unmatched.','No ECDLP security, attack-cost, or scientific-state conclusion.'],
        'retention':design['storage'],'scope':'Descriptive observations; no official scientific-state transition'}
    put_json(run/'analysis.json',result);return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path);args=parser.parse_args()
    result=analyze(args.run);print(json.dumps({'point_observations':result['point_observations'],'threshold_passes':sum(t['passes_family_threshold'] for t in result['primary_tests'])}))
