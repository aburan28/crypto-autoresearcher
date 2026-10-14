#!/usr/bin/env python3
"""Prospective rejection power under explicit independent-arm rare flags."""
import json
from pathlib import Path
import numpy as np
from scipy.stats import binom
from common import HERE,put_json
from metrics import fair_coin_run_probability


def paired_power(n,q,ratio,alpha):
    target=q*ratio;discordance=target*(1-q)+q*(1-target);conditional=target*(1-q)/discordance
    lo=max(1,int(binom.ppf(1e-14,n,discordance)));hi=int(binom.ppf(1-1e-14,n,discordance))
    d=np.arange(lo,hi+1);critical=binom.isf(alpha/2,d,.5).astype(int)+1
    return float(np.sum(binom.pmf(d,n,discordance)*binom.sf(critical-1,d,conditional)))


if __name__=='__main__':
    inputs=json.loads((HERE/'inputs.json').read_text());config=json.loads((HERE/'config.json').read_text());rows=[]
    alpha=config['familywise_alpha']/config['primary_tests']
    for model in inputs['candidates']:
        qvalues=[3e-5,1e-6,fair_coin_run_probability(256,32)] if model['metric_index']==0 else [1e-4,8.5e-4]
        for q in qvalues:
            for ratio in (1.05,1.1,1.2,2,3,5):
                rows.append({'candidate':model['id'],'windows_per_arm':model['windows'],'control_rate':q,'target_ratio':ratio,
                             'exact_planning_model_power':paired_power(model['windows'],q,ratio,alpha)})
    result={'schema':1,'per_primary_test_alpha':alpha,'rows':rows,'assumptions':'Independent rare flags in matched arms for planning; actual arms may be dependent. Exact tests use observed discordance. No universal sensitivity guarantee.',
            'fair_coin_run32_reference':fair_coin_run_probability(256,32),'point_observations_are_not_independent_trials':True}
    put_json(HERE/'power-plan.json',result);print(json.dumps(result,sort_keys=True))
