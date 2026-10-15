#!/usr/bin/env python3
"""Pool a fixed list of completed independent seeds; never choose seeds by p-value."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze import cp
from research import put_json,sha


def pool(runs,output):
    runs=[Path(r).resolve() for r in runs];designs=[json.loads((r/'design.json').read_text()) for r in runs]
    if len({d['config']['seed'] for d in designs})!=len(runs):raise ValueError('Duplicate seeds cannot be independent replication')
    baseline=designs[0]
    for design in designs:
        config=dict(design['config']);base_config=dict(baseline['config']);config.pop('seed');base_config.pop('seed')
        if config!=base_config or design['inputs']!=baseline['inputs'] or design['source_sha256']!=baseline['source_sha256']:
            raise ValueError('Pool requires identical source/model/config apart from seed')
    analyses=[]
    for run in runs:
        if not json.loads((run/'completion.json').read_text())['fixed_sample_complete']:raise ValueError('Incomplete run')
        if json.loads((run/'verification.json').read_text())['validity']!='passed stated checks':raise ValueError('Unverified run')
        analyses.append(json.loads((run/'analysis.json').read_text()))
    alpha=baseline['config']['familywise_alpha'];rate_rows=[];paired=[];tails=[];fields=[]
    for i,candidate in enumerate(analyses[0]['candidates']):
        for j,row in enumerate(candidate['rates']):
            hits=sum(a['candidates'][i]['rates'][j]['hits'] for a in analyses)
            n=sum(a['candidates'][i]['rates'][j]['windows'] for a in analyses)
            rate_rows.append({'candidate':candidate['id'],'cohort':row['cohort'],'hits':hits,'windows':n,'rate':hits/n,'cp_interval':cp(hits,n,alpha/9)})
    for i,test in enumerate(analyses[0]['primary_tests'][:9]):
        ab=sum(a['primary_tests'][i]['a_only'] for a in analyses);ba=sum(a['primary_tests'][i]['b_only'] for a in analyses)
        p=float(binomtest(ab,ab+ba,.5).pvalue) if ab+ba else 1.0
        paired.append({'id':test['id'],'a_only':ab,'b_only':ba,'p_two_sided_exact':p,
                       'passes_fixed_pooled_threshold':p<=alpha/9})
    for i,row in enumerate(analyses[0]['tail_spectrum']):
        hits=sum(a['tail_spectrum'][i]['hits'] for a in analyses);n=sum(a['tail_spectrum'][i]['windows'] for a in analyses)
        tails.append({'cohort':row['cohort'],'threshold':row['threshold'],'hits':hits,'windows':n,'rate':hits/n,'cp_interval':cp(hits,n,alpha/24)})
    for i,row in enumerate(analyses[0]['ordinary_fields']):
        hits=sum(a['ordinary_fields'][i]['hits'] for a in analyses);n=sum(a['ordinary_fields'][i]['windows'] for a in analyses)
        fields.append({'id':row['id'],'arm':row['arm'],'hits':hits,'windows':n,'rate':hits/n})
    result={'schema':1,'seeds':[d['config']['seed'] for d in designs],
        'inputs':[{'run':str(r),'analysis_sha256':sha(r/'analysis.json'),'verification_sha256':sha(r/'verification.json')} for r in runs],
        'point_observations':sum(a['point_observations'] for a in analyses),'rates':rate_rows,'paired_tests':paired,'tail_spectrum':tails,
        'ordinary_field_counts':fields,'inference_scope':'Nine pooled exact paired tests at alpha0.001/9; separate nine-rate and24-tail CP families. Ordinary-field counts are descriptive: pooling seeds does not create new fields.',
        'sampling_condition':'Seed list and stopping count must be fixed before sampling; do not select runs or pool after observing favorable p-values. This helper cannot enforce historical selection decisions.'}
    put_json(output,result);return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('runs',type=Path,nargs='+');args=parser.parse_args()
    print(json.dumps({'pooled_point_observations':pool(args.runs,args.output)['point_observations']}))
