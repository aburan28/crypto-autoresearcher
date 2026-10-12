"""Frozen paired/block analysis with field clustering and multiplicity correction."""
import csv
import io
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import norm, t
from research import canonical, check_source, immutable, jobs


def paired(left, right, alpha):
    left, right = np.asarray(left), np.asarray(right)
    differences = left-right
    count = len(differences)
    if count < 2:
        raise ValueError('At least two independent blocks needed for intervals')
    error = float(np.std(differences, ddof=1)/math.sqrt(count))
    critical = float(t.ppf(1-alpha/2, count-1))
    difference = float(differences.mean())
    return {'left_mean': float(left.mean()), 'right_mean': float(right.mean()),
            'difference': difference, 'standard_error': error, 'df': count-1,
            'left_units': count, 'right_units': count, 'method': 'paired block Student approximation',
            'interval': [difference-critical*error, difference+critical*error],
            'approximate_90pct_power_detectable_difference': (critical+float(norm.ppf(.9)))*error}


def welch(left, right, alpha):
    left, right = np.asarray(left), np.asarray(right)
    if len(left)<2 or len(right)<2:
        raise ValueError('At least two independent units in each arm needed')
    vl, vr = float(np.var(left, ddof=1)/len(left)), float(np.var(right, ddof=1)/len(right))
    error = math.sqrt(vl+vr)
    df = (vl+vr)**2/(vl**2/(len(left)-1)+vr**2/(len(right)-1))
    critical = float(t.ppf(1-alpha/2, df))
    difference = float(left.mean()-right.mean())
    return {'left_mean': float(left.mean()), 'right_mean': float(right.mean()),
            'difference': difference, 'standard_error': error, 'df': df,
            'left_units': len(left), 'right_units': len(right), 'method': 'Welch approximation on independent units; R/C averaged within fields',
            'interval': [difference-critical*error, difference+critical*error],
            'approximate_90pct_power_detectable_difference': (critical+float(norm.ppf(.9)))*error}


def analyze(output):
    output = Path(output).resolve()
    config = check_source(output)['config']
    inputs = json.loads((output/'inputs.json').read_text())
    queue = jobs(inputs, config)
    if not (output/'receipt.json').exists() or not (output/'verification.json').exists():
        raise ValueError('A completed, verified run is required')
    verification = json.loads((output/'verification.json').read_text())
    if verification['status'] != 'passed':
        raise ValueError('Verification did not pass')
    records = [json.loads((output/'records'/(job['id']+'.json')).read_text()) for job in queue]
    alpha = config['familywise_alpha']/config['primary_comparisons']
    comparisons = []
    for case in config['cases']:
        for mode in ('walk', 'iid'):
            metrics = config['walk_metrics'] if mode == 'walk' else config['iid_metrics']
            selected = [r for r in records if r['job']['case']==case and r['job']['mode']==mode]
            by_cohort = {cohort: sorted([r for r in selected if r['job']['cohort']==cohort], key=lambda r:r['job']['block'])
                         for cohort in ('published','random')}
            if [r['job']['block'] for r in by_cohort['published']] != [r['job']['block'] for r in by_cohort['random']]:
                raise ValueError('Unpaired generator blocks')
            for metric in metrics:
                comparison = paired([r['features'][metric] for r in by_cohort['published']],
                                    [r['features'][metric] for r in by_cohort['random']], alpha)
                comparison.update({'case':case,'population':mode,'metric':metric,
                                   'left':'published','right':'random-generators'})
                comparisons.append(comparison)
        selected = [r for r in records if r['job']['case']==case and r['job']['mode']=='field']
        for metric in config['field_metrics']:
            # S is one fixed prime, independent uniform coefficient draws. Its
            # models estimate only that fixed prime's random-model expectation.
            structured = [r['features'][metric] for r in selected if r['job']['arm']=='S']
            for arm in ('R','C'):
                fields = defaultdict(list)
                for record in selected:
                    if record['job']['arm']==arm:
                        fields[record['job']['field_id']].append(record['features'][metric])
                controls = [float(np.mean(v)) for _,v in sorted(fields.items())]
                comparison = welch(structured, controls, alpha)
                comparison.update({'case':case, 'population':'random-model affine points','metric':metric,
                                   'left':'fixed Solinas prime random models','right':arm+' fields'})
                comparisons.append(comparison)
    if len(comparisons)!=config['primary_comparisons']:
        raise ValueError('Primary comparison multiplicity differs from frozen contract')
    for comparison in comparisons:
        comparison['excludes_zero'] = comparison['interval'][0]>0 or comparison['interval'][1]<0
    summaries=[]
    grouped=defaultdict(list)
    for r in records:
        grouped[(r['job']['case'],r['job']['mode'],r['job']['cohort'],r['job']['arm'])].append(r)
    for (case,mode,cohort,arm),rows in sorted(grouped.items()):
        summaries.append({'case':case,'mode':mode,'cohort':cohort,'arm':arm,
                          'units':len(rows),'points':sum(r['features']['points'] for r in rows),
                          'unique_models':len({r['model_uid'] for r in rows}),
                          'unique_fields':len({r['job']['curve']['p'] for r in rows}),
                          'unique_generators':len({r['generator_identity']['curve_uid'] for r in rows if r['generator_identity']}),
                          'mean_features':{metric:float(np.mean([r['features'][metric] for r in rows]))
                                           for metric in set(config['walk_metrics']+config['iid_metrics'])}})
    diagnostics=[]
    for case in config['cases']:
        rows=[r for r in records if r['job']['case']==case and r['diagnostics']]
        shuffled=[r['diagnostics']['shuffled_x_lag1'] for r in rows]
        diagnostics.append({'case':case,'units':len(rows),
                            'shuffled_mean_x_lag1':float(np.mean(shuffled)),
                            'shuffled_99pct_interval':welch(shuffled,[0.0]*len(shuffled),.01)['interval'],
                            'sorted_positive_min_x_lag1':min(r['diagnostics']['sorted_positive_x_lag1'] for r in rows),
                            'u2_mean_absolute_x_lag1_change':float(np.mean([abs(r['features']['x_lag1']-r['diagnostics']['isomorphic_u2_features']['x_lag1']) for r in rows])),
                            'interpretation':'Diagnostic controls on exactly the same point sets; sorted order is deliberately synthetic, u=2 changes coordinates but preserves the group.'})
    analysis={'status':'derived_measured_observations','comparisons':comparisons,'summaries':summaries,
              'diagnostics':diagnostics,'familywise_confidence_nominal':1-config['familywise_alpha'],
              'per_interval_confidence':1-alpha,'inference':'Approximate Student/Welch intervals with Bonferroni correction; coverage relies on independent blocks/fields and a sampling-distribution approximation. Not an exact finite-sample guarantee.',
              'excludes_zero_count':sum(c['excludes_zero'] for c in comparisons),
              'scope':'Two fixed standard primes; generator interaction is conditional on each exact standard curve. R/C random-curve controls do not identify an official-generator by prime interaction across fields.',
              'security_claim':'none'}
    immutable(output/'analysis.json',canonical(analysis))
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=['case','population','metric','left','right','difference','low','high','standard_error','left_units','right_units','excludes_zero'],lineterminator='\n')
    writer.writeheader()
    for row in comparisons:
        writer.writerow({k:row[k] for k in writer.fieldnames if k not in ('low','high')} | {'low':row['interval'][0],'high':row['interval'][1]})
    immutable(output/'comparisons.csv',stream.getvalue().encode())
    print(json.dumps({'status':analysis['status'],'comparisons':len(comparisons),
                      'excludes_zero_count':analysis['excludes_zero_count']}))


if __name__=='__main__':
    import sys
    analyze(sys.argv[1])
