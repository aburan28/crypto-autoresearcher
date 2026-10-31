"""Streaming descriptive aggregation; physical traces and six lists stay distinct."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re

SLOT=re.compile(r'(discovery|validation|confirmation-A|confirmation-B)-(10|13|16)-([0-3])\Z')


def unique(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError('duplicate JSON key')
        d[k]=v
    return d


def nonfinite(value):
    raise ValueError('nonfinite JSON')


def finite_float(value):
    result=float(value)
    if not math.isfinite(result):raise ValueError('nonfinite JSON')
    return result


def rows(path,max_line_bytes):
    with Path(path).open('rb') as f:
        while True:
            line=f.readline(max_line_bytes+1)
            if not line:break
            if len(line)>max_line_bytes:raise ValueError('row resource bound exceeded; no truncation')
            if not line.endswith(b'\n'):raise ValueError('partial JSONL row')
            yield json.loads(line,object_pairs_hook=unique, parse_constant=nonfinite, parse_float=finite_float)


def sum_vectors(target,counts):
    for family,vector in counts.items():
        for primitive,value in vector.items():target[family+'/'+primitive]+=value


def summarize(raw,max_line_bytes=64<<20):
    raw=Path(raw);trace_meta={};trace_counts=Counter();physical=defaultdict(Counter)
    for trace in rows(raw/'traces.jsonl',max_line_bytes):
        ident=trace['trace_id']
        if ident in trace_meta:raise ValueError('duplicate trace ID')
        if len(trace_meta)>=36864:raise ValueError('trace metadata resource cap exceeded')
        curve=trace['curve_id'];trace_meta[ident]={'curve_id':curve,'target_id':trace['target_id']}
        trace_counts[curve]+=1
        # Original and incremental are actual physical executions. Six cells do
        # not each incur this trace vector; no division or duplication here.
        for method in ['original','incremental']:
            attempt=trace[method]
            if attempt is not None:sum_vectors(physical[(curve,method)],attempt['counts'])
    setups=[]
    for setup in rows(raw/'setups.jsonl',max_line_bytes):
        setups.append({'curve_id':setup['curve_id'],'arm_id':setup['arm_id'],'setup_reason':setup['setup_reason'],'counts':setup['counts']})
    curves=defaultdict(lambda:defaultdict(lambda:{'outcomes':Counter(),'decoder_component_costs':Counter(),'attempts':0,'successes':0,'zero_candidate_checks':0,'targets':set(),'retained_targets':set()}))
    paired=defaultdict(dict)
    for cell in rows(raw/'decoder-cells.jsonl',max_line_bytes):
        meta=trace_meta[cell['trace_id']];curve=meta['curve_id'];key=cell['cell_id'].rsplit('/',1)[-1]
        item=curves[curve][key];item['retained_targets'].add(meta['target_id']);item['attempts']+=1;item['successes']+=cell['status']=='RECOVERED'
        item['outcomes'][cell['status']]+=1;item['zero_candidate_checks']+=cell['zero_candidate_checks']
        sum_vectors(item['decoder_component_costs'],cell['counts'])
        if cell['status']=='RECOVERED':item['targets'].add(meta['target_id'])
        if key in ['t0.e0','t1.e2']:paired[cell['trace_id']][key]=cell['status']=='RECOVERED'
    result=[]
    for curve,cells in sorted(curves.items()):
        match=SLOT.fullmatch(curve);stage=match[1] if match else 'disclosed_fixture'
        for key,item in sorted(cells.items()):
            item={**item,'outcomes':dict(item['outcomes']),'decoder_component_costs':dict(item['decoder_component_costs']),'unique_targets_recovered':len(item['targets'])}
            item['unique_targets_retained']=len(item.pop('retained_targets'));del item['targets'];n=item['attempts'];s=item['successes']
            item['success_fraction']={'numerator':s,'denominator':n}
            item['decoder_component_batch_cost_per_success']={k:({'numerator':v,'denominator':s} if s else None) for k,v in item['decoder_component_costs'].items()}
            item['zero_event_upper_bound']=(1-(0.05/144)**(1/n)) if n and s==0 else None
            item['uncertainty_model']='Zero-event bound only: independent identically distributed restart events on this fixed curve, simultaneous alpha0.05/144. Nonzero fractions descriptive; no population interval.'
            result.append({'curve_id':curve,'stage':stage,'tier':int(match[2]) if match else None,'cell':key,**item})
    discordants=defaultdict(Counter)
    for ident,pair in paired.items():
        if set(pair)=={'t0.e0','t1.e2'}:
            a,b=pair['t0.e0'],pair['t1.e2'];discordants[trace_meta[ident]['curve_id']][str(int(a))+str(int(b))]+=1
    panels={stage:[r for r in result if r['stage']==stage] for stage in ['confirmation-A','confirmation-B']}
    return {'schema':'classical.ecdlp.controlled-followup.analysis/v1','per_curve_six_cell':result,'panels':panels,
        'coverage':{'retained_curves':len(trace_counts),'retained_physical_trace_records':sum(trace_counts.values()),'retained_decoder_cells':sum(r['attempts'] for r in result),'retained_curve_cell_pairs':len(result),'per_curve_cells':{curve:sorted(cells) for curve,cells in sorted(curves.items())},'interpretation':'Retained counts only; workload completeness is checked independently before labels, and partial rows are never padded.'},
        'traces_by_curve':dict(trace_counts),'paired_discordants_t0e0_t1e2':{k:dict(v) for k,v in discordants.items()},
        'setup_components':setups,'physical_trace_components_once':[{'curve_id':k[0],'method':k[1],'counts':dict(v)} for k,v in sorted(physical.items())],
        'cost_scope':'Decoder costs are component-only. Physical original/incremental query, blinding, reduction, conversion and state vectors retained once per actual trace; setup/common separately. No full-solver ratio is asserted.',
        'uncertainty':'Curve is population unit; six cells share traces. No p-values or exponent fits; A/B panel distributions retained separately.',
        'wall_valid':False,'counter_replay_qualified':False,'unmetered':['native RSS','interpreter allocations','I/O','Python integer internals'],'scientific_conclusion':None}
