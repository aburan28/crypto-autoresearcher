#!/usr/bin/env python3
"""Frozen wider-study analysis; distinct prime blocks are the resampling unit."""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from common import write, sha


def compare(rows, key, exponent=True):
    rng = np.random.default_rng(2026101131)
    total, combined = 0, np.zeros(500000)
    for bits in sorted({r['bits'] for r in rows}):
        xs = np.array([r[key] for r in rows if r['bits'] == bits])
        total += len(xs)
        combined += len(xs) * xs[rng.integers(len(xs), size=(500000, len(xs)))].mean(axis=1)
    combined /= total
    convert = math.exp if exponent else float
    return {'estimate': convert(np.mean([r[key] for r in rows])),
        'CI99_9': [convert(v) for v in np.quantile(combined, [.0005, .9995])],
        'CI99_9667_reserved_three_primary_tests': [convert(v) for v in np.quantile(combined, [.001/6, 1-.001/6])],
        'prime_blocks': total, 'confidence_scope': 'Approximate marginal percentile block-bootstrap; Bonferroni interval reserves three primary family tests'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    run, out = args.run.resolve(), args.run.resolve() / 'analysis'
    out.mkdir(exist_ok=False)
    load = lambda p: json.loads((run / p).read_text())
    groups = load('preparation/public-groups.json')
    moduli = load('preparation/prime-sample.json')['moduli']
    jobs = {j['job_id']: j for j in load('attacks/job-index.json')}
    by_group = defaultdict(list)
    count, bsgs_accounted = 0, 0
    for path in sorted((run / 'attacks').glob('block-*/raw-results.jsonl')):
        for line in path.read_text().splitlines():
            r = json.loads(line)
            j = jobs[r['job_id']]
            by_group[j['group_id'], j['mode']].append(r)
            count += 1
            if r['mode'] == 'bsgs':
                M = r['M']
                assert r['counts']['setup']['group_calls'] == M + M.bit_count() + M.bit_length() - 1
                assert r['counts']['search']['group_calls'] == r['scalar'] // M
                bsgs_accounted += 1
    metrics = []
    for g in groups:
        for mode in ['rho', 'oracle', 'rho32', 'bsgs']:
            rows = by_group[g['group_id'], mode]
            if not rows:
                continue
            expected = 4 if mode == 'bsgs' else 16
            calls = [r['counts']['search']['group_calls'] for r in rows]
            total = [r['counts']['search']['group_calls'] + r['counts']['setup']['group_calls'] for r in rows]
            norm = [total[i] / (r['M'] + g['ell']/(2*r['M'])) if mode == 'bsgs'
                    else min(calls[i]/math.sqrt(g['ell']),20) for i,r in enumerate(rows)]
            metrics.append({**{k:g[k] for k in ['group_id','block','arm','bits','slot','ell','kind']},
                'mode':mode,'attempts':len(rows),'complete':len(rows)==expected,
                'normalized_mean':float(np.mean(norm)), 'end_to_end_mean':float(np.mean(total)),
                'recovered':sum(r['scalar'] is not None for r in rows),'censors':sum(r['censored'] for r in rows),
                'CPU_seconds_mean':float(np.mean([sum(r['cpu_seconds'][:2]) for r in rows])),
                'table_allocated_bytes_mean':float(np.mean([r['table_allocated_bytes'] for r in rows]))})
    write(out/'group-metrics.json',metrics)
    lookup = {(r['block'],r['slot'],r['arm'],r['mode']):r for r in metrics if r['kind']=='matched' and r['complete']}
    block_ids = sorted({m['block'] for m in moduli})
    blocks, attacks = [], {}
    for mode in ['rho','oracle','rho32','bsgs']:
        for control in ['R','C']:
            rows=[]
            for block in block_ids:
                values=[]
                for slot in range(8):
                    s=lookup[block,slot,'S',mode]
                    controls=[lookup[block,slot,control+str(i),mode] for i in [1,2]]
                    mean=float(np.mean([r['normalized_mean'] for r in controls]))
                    values.append(math.log(s['normalized_mean']/mean))
                rows.append({'block':block,'bits':s['bits'],'mode':mode,'contrast':'S/'+control,
                             'log_ratio':float(np.mean(values)),'matched_slots':8,'control_primes_per_S':2})
            blocks.extend(rows)
            attacks[mode+'_S_'+control]=compare(rows,'log_ratio')
    write(out/'prime-block-metrics.json',blocks)
    audit=[]
    for m in moduli:
        curves=load('preparation/curves/'+m['id']+'/curves.json')['curves'][:128]
        audit.append({**m,'audited_models':len(curves),
            'mean_proxy_bits':float(np.mean([.5*math.log2(c['ell']) for c in curves])),
            'obvious_flag_fraction':float(np.mean([c['flags']['anomalous'] or c['flags']['supersingular']
                 or c['flags']['j_special'] or c['flags']['embedding_degree_le20'] is not None for c in curves]))})
    write(out/'unconditional-audit.json',audit)
    populations={}
    for control in ['R','C']:
        rows=[]
        for block in block_ids:
            s=next(r for r in audit if r['block']==block and r['arm']=='S')
            c=[r['mean_proxy_bits'] for r in audit if r['block']==block and r['arm'].startswith(control)]
            rows.append({'bits':s['bits'],'difference':s['mean_proxy_bits']-float(np.mean(c))})
        populations['S_'+control]=compare(rows,'difference',False)
    ar=[]
    for path in sorted((run/'arithmetic').glob('m*/result.json')):
        r=json.loads(path.read_text());ar.extend({**r['modulus'],**v}for v in r['observations'])
    arithmetic={}
    for work in ['products','inversions','point_additions']:
        rows=[];prototype=[]
        for block in block_ids:
            times={arm:float(np.median([r['seconds_per_operation'] for r in ar if r['block']==block and r['arm']==arm
                    and r['backend']=='generic' and r['workload']==work])) for arm in ['S','R1','R2','C1','C2']}
            rows.append({'bits':next(m['bits']for m in moduli if m['block']==block),
                         'S_R':math.log(times['S']/np.mean([times['R1'],times['R2']])),
                         'S_C':math.log(times['S']/np.mean([times['C1'],times['C2']]))})
            sparse=np.median([r['seconds_per_operation'] for r in ar if r['block']==block and r['arm']=='S'
                             and r['backend']=='sparse' and r['workload']==work])
            prototype.append(sparse/times['S'])
        arithmetic[work]={key:compare(rows,key)for key in ['S_R','S_C']}
        arithmetic[work]['median_Python_fold_over_builtin_seconds']=float(np.median(prototype))
    checks=load('attacks/control-checks.json')
    attack_result=load('attacks/attack-result.json')
    easy=[]
    for bits in sorted({m['bits']for m in moduli}):
        tiny=next(r for r in metrics if r['bits']==bits and r['kind']=='easy' and r['mode']=='bsgs')
        ordinary=[r['end_to_end_mean']for r in metrics if r['bits']==bits and r['kind']=='matched' and r['mode']=='bsgs']
        easy.append({'bits':bits,'pass':tiny['complete'] and tiny['recovered']==4 and tiny['end_to_end_mean']<min(ordinary),
                     'easy_ell':tiny['ell'],'method':'BSGS complete-coverage positive control'})
    integrity=not attack_result['failures'] and len(checks)==768 and all(r['pass']for r in checks) and all(r['pass']for r in easy)
    primary=attacks['rho_S_R'];lo,hi=primary['CI99_9'];decision='inconclusive'
    if integrity and lo>=1/1.2 and hi<=1.2:decision='practically similar normalized rho cost in this sampled scope'
    elif integrity and lo>1.2:decision='higher measured generic rho work; structure diagnostics required before broader inference'
    strata={}
    for bits in sorted({m['bits']for m in moduli}):
        strata[str(bits)]=compare([r for r in blocks if r['mode']=='rho' and r['contrast']=='S/R' and r['bits']==bits],'log_ratio')
    summary={'experiment_id':'EXP-ECDLP-5184f7','run_id':run.name,'label':'Prospective fresh wider Solinas sample',
        'primary_result':primary,'decision':decision,'main_prime_blocks':len(block_ids),'moduli':len(moduli),
        'random_control_primes':sum(m['arm']!='S'for m in moduli),'field_bit_strata':sorted({m['bits']for m in moduli}),
        'prepared_nonsingular_models':load('preparation/preparation-result.json')['nonsingular_models'],
        'unconditional_models':sum(m['audited_models']for m in audit),'attack_jobs':count,'BSGS_jobs_exactly_accounted':bsgs_accounted,
        'attack_comparisons':attacks,'primary_strata':strata,'population_proxy_difference_bits':populations,
        'arithmetic':arithmetic,'arithmetic_observations':len(ar),'integrity_controls_pass':bool(integrity),
        'exact_control_checks':len(checks),'easy_positive_controls':easy,
        'main_rho_censors':sum(r['censors']for r in metrics if r['mode']=='rho' and r['kind']=='matched'),
        'bootstrap':{'replicates':500000,'seed':2026101131,'confidence':.999,'unit':'whole prime block within bit-size strata'},
        'scope':'Toy, uniform coefficient models, matched largest subgroups and implemented attacks; no production ECDLP or universal resistance claim',
        'source_sha256':sha(Path(__file__))}
    write(out/'summary.json',summary)
    print(json.dumps({k:summary[k]for k in ['run_id','primary_result','decision','attack_jobs','integrity_controls_pass']},indent=2))


if __name__=='__main__':main()
