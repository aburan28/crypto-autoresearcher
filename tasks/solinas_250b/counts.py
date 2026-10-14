"""Exact sufficient counts; no inference until the fixed campaign completes."""
import numpy as np
from common import events_for


def summarize(scores,model,config,named):
    result={'events':{},'score_sums':[],'score_square_sums':[]};cohorts=scores.shape[1]
    for event in events_for(model,config,named):
        flags=scores[:,:,event['metric']]>=event['threshold']
        pattern=np.sum(flags.astype(np.uint8)*(1<<np.arange(cohorts,dtype=np.uint8)),axis=1)
        result['events'][event['name']]={'threshold':event['threshold'],'metric':event['metric'],
            'hits':np.sum(flags,axis=0).tolist(),'joint_counts':np.bincount(pattern,minlength=1<<cohorts).tolist()}
    for c in range(cohorts):
        data=scores[:,c,:].astype(np.uint64)
        result['score_sums'].append(np.sum(data,axis=0).tolist())
        result['score_square_sums'].append(np.sum(data*data,axis=0).tolist())
    return result


def discordance(joint,a,b):
    ab=sum(int(n) for mask,n in enumerate(joint) if (mask>>a)&1 and not (mask>>b)&1)
    ba=sum(int(n) for mask,n in enumerate(joint) if (mask>>b)&1 and not (mask>>a)&1)
    return ab,ba
