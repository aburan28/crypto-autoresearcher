#!/usr/bin/env python3
"""Prospective power under a stated rare-event pair model, not a guarantee."""
import json
from pathlib import Path
import numpy as np
from scipy.stats import binom
from metrics import fair_coin_run_probability
HERE=Path(__file__).resolve().parent


def paired_power(windows,control_rate,ratio,alpha):
    target_rate=control_rate*ratio
    discordant=target_rate*(1-control_rate)+control_rate*(1-target_rate)
    conditional=target_rate*(1-control_rate)/discordant
    lo=max(1,int(binom.ppf(1e-14,windows,discordant)));hi=int(binom.ppf(1-1e-14,windows,discordant))
    d=np.arange(lo,hi+1)
    critical=binom.isf(alpha/2,d,.5).astype(int)+1
    # Upper-direction rejection of the two-sided exact McNemar/binomial test.
    probability=binom.sf(critical-1,d,conditional)
    return float(np.sum(binom.pmf(d,windows,discordant)*probability))


if __name__=='__main__':
    inputs=json.loads((HERE/'inputs.json').read_text());config=json.loads((HERE/'config.json').read_text())
    alpha=config['familywise_alpha']/config['primary_tests'];rows=[]
    for candidate in inputs['candidates']:
        rates=[3e-5,fair_coin_run_probability(256,22),1e-6] if candidate['metric_index']==0 else [1e-4,5e-4,1e-3]
        for q in rates:
            for ratio in (2,3,5):rows.append({'candidate':candidate['id'],'windows_per_arm':candidate['windows'],'control_rate':q,'target_ratio':ratio,'exact_model_power':paired_power(candidate['windows'],q,ratio,alpha)})
    result={'schema':1,'per_test_alpha':alpha,'assumptions':'Independent rare flags within each paired window; empirical pairs may be dependent. Power is planning under this specified alternative, not guaranteed sensitivity for every point process.',
            'fair_coin_256_run22_probability':fair_coin_run_probability(256,22),'rows':rows,
            'point_counts_are_not_independent_trials':'A 256-point window is the trial; all generator cohorts use the same Q within a pair/triple.'}
    path=HERE/'power-plan.json';data=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if path.exists() and path.read_text()!=data:raise ValueError('Power plan differs')
    path.write_text(data);print(data)
