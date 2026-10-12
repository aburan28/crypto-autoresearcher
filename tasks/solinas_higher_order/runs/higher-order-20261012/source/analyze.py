"""Predeclared clustered comparisons and independent feature-only ML test."""
import csv
import io
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import beta, norm, t
from research import canonical, check_source, digest, immutable


def paired(left, right, alpha):
    left = np.asarray(left, dtype=float); right = np.asarray(right, dtype=float)
    values = left-right; count = len(values)
    if count < 2: raise ValueError('Insufficient independent units')
    se = float(np.std(values, ddof=1)/math.sqrt(count)); difference = float(values.mean())
    critical = float(t.ppf(1-alpha/2, count-1))
    return {'left_mean': float(left.mean()), 'right_mean': float(right.mean()), 'difference': difference,
            'interval': [difference-critical*se, difference+critical*se], 'standard_error': se, 'df': count-1,
            'left_units': count, 'right_units': count, 'method': 'paired Student approximation on independent block/target units',
            'approximate_90pct_power_detectable_difference': (critical+float(norm.ppf(.9)))*se}


def welch(left, right, alpha):
    left = np.asarray(left, dtype=float); right = np.asarray(right, dtype=float)
    vl, vr = float(left.var(ddof=1)/len(left)), float(right.var(ddof=1)/len(right))
    se = math.sqrt(vl+vr); df = (vl+vr)**2/(vl**2/(len(left)-1)+vr**2/(len(right)-1))
    critical = float(t.ppf(1-alpha/2, df)); difference = float(left.mean()-right.mean())
    return {'left_mean': float(left.mean()), 'right_mean': float(right.mean()), 'difference': difference,
            'interval': [difference-critical*se, difference+critical*se], 'standard_error': se, 'df': df,
            'left_units': len(left), 'right_units': len(right), 'method': 'Welch approximation; random controls clustered by field',
            'approximate_90pct_power_detectable_difference': (critical+float(norm.ppf(.9)))*se}


def binomial_interval(hits, count, alpha):
    return [0.0 if hits == 0 else float(beta.ppf(alpha/2, hits, count-hits+1)),
            1.0 if hits == count else float(beta.ppf(1-alpha/2, hits+1, count-hits))]


def records(output, folder='records'):
    return [json.loads(p.read_text()) for p in sorted((Path(output)/folder).glob('*.json'))]


def summarize_discovery(rows, config):
    comparisons = []; alpha = config['familywise_alpha']/56
    for case in config['cases']:
        for mode in ('walk', 'iid'):
            by = {cohort: sorted([r for r in rows if r['job']['case'] == case and r['job']['mode'] == mode and r['job']['cohort'] == cohort],
                                 key=lambda r: r['job']['block']) for cohort in ('published', 'random')}
            if not by['published'] or len(by['published']) != len(by['random']): raise ValueError('Discovery pairs absent')
            for metric in config['walk_metrics']:
                comparison = paired([r['features'][metric] for r in by['published']], [r['features'][metric] for r in by['random']], alpha)
                comparisons.append(comparison | {'case': case, 'population': 'discovery-'+mode, 'metric': metric})
        selected = [r for r in rows if r['job']['case'] == case and r['job']['mode'] == 'field']
        for metric in config['field_metrics']:
            structured = [r['features'][metric] for r in selected if r['job']['arm'] == 'S']
            for arm in ('R', 'C'):
                fields = defaultdict(list)
                for r in selected:
                    if r['job']['arm'] == arm: fields[r['job']['field_id']].append(r['features'][metric])
                controls = [float(np.mean(v)) for _, v in sorted(fields.items())]
                comparisons.append(welch(structured, controls, alpha) | {'case': case, 'population': 'discovery-field-'+arm, 'metric': metric})
    if len(comparisons) != 56: raise ValueError('Discovery metric count differs')
    for c in comparisons: c['excludes_zero'] = c['interval'][0] > 0 or c['interval'][1] < 0
    return {'comparisons': comparisons, 'excludes_zero_count': sum(c['excludes_zero'] for c in comparisons),
            'inference': 'Exploratory scan of prior points; fresh primary comparisons below are the confirmation'}


def train_and_test_ml(old_rows, fresh_rows, config, output, alpha):
    from sklearn.ensemble import HistGradientBoostingClassifier
    import joblib
    outcomes = []; metadata = []
    for case in config['cases']:
        training = [r for r in old_rows if r['job']['case'] == case and r['job']['mode'] == 'walk']
        training.sort(key=lambda r: (r['job']['block'], r['job']['cohort']))
        if any(r.get('ml_points') != config['walk_points'] for r in training): raise ValueError('Training/test window mismatch')
        x = np.array([[r['ml_features'][m] for m in config['walk_metrics']] for r in training])
        y = np.array([int(r['job']['cohort'] == 'published') for r in training])
        # No generator coords, field identifiers, seed, index, label or raw point
        # is passed into the feature matrix. No hyperparameter search or peeking.
        settings = {k: v for k, v in config['ml'].items() if k != 'algorithm'}
        model = HistGradientBoostingClassifier(**settings).fit(x, y)
        testing = sorted([r for r in fresh_rows if r['job']['case'] == case and r['job']['kind'] == 'walk'], key=lambda r: r['job']['block'])
        testx = np.array([[u['features'][m] for m in config['walk_metrics']] for r in testing for u in r['units']])
        labels = np.array([int(u['label'] == 'published') for r in testing for u in r['units']])
        prediction = model.predict(testx); scores = (prediction == labels).astype(float).reshape(-1, 2).mean(1)
        result = paired(scores, np.full(len(scores), .5), alpha)
        result.update(case=case, population='ML independent-seed test', metric='accuracy_minus_half',
                      left='classifier accuracy', right='balanced chance benchmark',
                      accuracy=float(scores.mean()), model_selection='Locked algorithm; trained on old points, evaluated on untouched fresh paired blocks',
                      above_chance=result['interval'][0] > 0)
        outcomes.append(result)
        model_dir = Path(output)/'ml-models'; model_dir.mkdir(exist_ok=True)
        temp = model_dir/(case+'.tmp'); joblib.dump(model, temp)
        target = model_dir/(case+'.joblib'); immutable(target, temp.read_bytes()); temp.unlink()
        metadata.append({'case': case, 'train_rows': len(x), 'test_rows': len(testx), 'test_pairs': len(testing),
                         'features': config['walk_metrics'], 'training_feature_sha256': __import__('hashlib').sha256(x.tobytes()+y.tobytes()).hexdigest(),
                         'model_sha256': digest(target), 'predicted_published_fraction': float(prediction.mean()),
                         'ml_notes': 'Feature-only classifier of point walks, not a scalar/key model. Both training and test windows contain 2048 points; fresh seeds and random generators prevent point overlap with training.'})
    return outcomes, metadata


def analyze(output):
    output = Path(output); design = check_source(output); config = design['config']
    if json.loads((output/'verification.json').read_text())['status'] != 'passed': raise ValueError('Verified data required')
    if not (output/'discovery'/'receipt.json').exists(): raise ValueError('Discovery data required for locked ML training')
    fresh = records(output); old = records(output, 'discovery/records')
    alpha = config['familywise_alpha']/config['primary_tests']; comparisons = []; benchmarks = []; secondary = []; extremes = []
    for case in config['cases']:
        walks = sorted([r for r in fresh if r['job']['case'] == case and r['job']['kind'] == 'walk'], key=lambda r: r['job']['block'])
        for metric in config['walk_metrics']:
            left = [next(u for u in r['units'] if u['label'] == 'published')['features'][metric] for r in walks]
            right = [next(u for u in r['units'] if u['label'] == 'random')['features'][metric] for r in walks]
            comparisons.append(paired(left, right, alpha) | {'case': case, 'population': 'fresh walks', 'metric': metric,
                                                            'left': 'published', 'right': 'fresh random generators'})
        fields = [r for r in fresh if r['job']['case'] == case and r['job']['kind'] == 'field']
        for metric in config['field_metrics']:
            structured = [r['units'][0]['features'][metric] for r in fields if r['job']['arm'] == 'S']
            for arm in ('R', 'C'):
                grouped = defaultdict(list)
                for r in fields:
                    if r['job']['arm'] == arm: grouped[r['job']['field_id']].append(r['units'][0]['features'][metric])
                control = [float(np.mean(v)) for _, v in sorted(grouped.items())]
                comparisons.append(welch(structured, control, alpha) | {'case': case, 'population': 'fresh affine points', 'metric': metric,
                                                                       'left': 'fixed S prime random models', 'right': arm+' random fields'})
        targeted = sorted([r for r in fresh if r['job']['case'] == case and r['job']['kind'] == 'target'], key=lambda r: r['job']['id'])
        for metric in config['walk_metrics']:
            left = [float(np.mean([u['features'][metric] for u in r['units'] if u['label'] == 'target'])) for r in targeted]
            right = [float(np.mean([u['features'][metric] for u in r['units'] if u['label'] == 'random'])) for r in targeted]
            comparisons.append(paired(left, right, alpha) | {'case': case, 'population': 'targeted-generator walks', 'metric': metric,
                                                            'left': 'fixed five-region target set', 'right': 'matched fresh random G',
                                                            'scope': 'Finite deliberately chosen generator set; four starts averaged per generator. No claim of uniform target-population sampling.'})
            for region in config['target_regions']:
                indices = [i for i, r in enumerate(targeted) if r['job']['target']['region'] == region]
                secondary.append(paired([left[i] for i in indices], [right[i] for i in indices], config['familywise_alpha']/100) |
                                 {'case': case, 'population': 'exploratory region '+region, 'metric': metric})
        bank = [u for r in fresh if r['job']['case'] == case and r['job']['kind'] == 'bank' for u in r['units']]
        bank.sort(key=lambda u: u['generator_index'])
        if len(bank) != config['bank_generators']: raise ValueError('Generator bank count differs')
        official = next(r for r in fresh if r['job']['case'] == case and r['job']['kind'] == 'prefix')['units'][0]
        for metric in config['walk_metrics']:
            values = np.array([u['features'][metric] for u in bank], dtype=float); score = official['features'][metric]
            hits = int(np.count_nonzero(values >= score)); probability = (hits+1)/(len(bank)+1)
            benchmarks.append({'case': case, 'metric': metric, 'official_score': score, 'bank_generators': len(bank),
                               'as_or_more_extreme': hits, 'monte_carlo_p': probability, 'bonferroni_p': min(1.0, probability*config['primary_tests']),
                               'tail_probability_interval': binomial_interval(hits, len(bank), alpha), 'crosses_threshold': probability <= alpha,
                               'quantiles': {str(q): float(np.quantile(values, q)) for q in (.5, .9, .99, .999, .9999)},
                               'null': 'Published trimmed prefix compared with a uniform random-generator benchmark on this exact standard curve; ties count conservatively',
                               'scope': 'Right-tail anomaly benchmark, not proof of random original generator selection or security'})
            top = sorted(bank, key=lambda u: (-u['features'][metric], u['generator_index']))[:3]
            extremes.append({'case': case, 'metric': metric, 'top_three': [{'generator_index': u['generator_index'], 'G': u['generator'], 'score': u['features'][metric]} for u in top],
                             'scope': 'Exploratory selected order statistics; extreme maxima are expected in a large bank, not independent discoveries'})
    ml, ml_metadata = train_and_test_ml(old, fresh, config, output, alpha); comparisons.extend(ml)
    if len(comparisons)+len(benchmarks) != config['primary_tests']: raise ValueError('Frozen multiplicity differs')
    for c in comparisons: c['excludes_zero'] = c['interval'][0] > 0 or c['interval'][1] < 0
    for c in secondary: c['excludes_zero'] = c['interval'][0] > 0 or c['interval'][1] < 0
    diagnostics = []
    for case in config['cases']:
        rows = [r for r in fresh if r['job']['case'] == case and r['job']['kind'] == 'walk' and r['diagnostics']]
        for label in ('published', 'random'):
            for metric in config['walk_metrics']:
                observed = [next(u for u in r['units'] if u['label'] == label)['features'][metric] for r in rows]
                shuffled = [r['diagnostics'][label]['shuffled'][metric] for r in rows]
                transformed = [r['diagnostics'][label]['isomorphic_u2'][metric] for r in rows]
                diagnostics.append({'case': case, 'cohort': label, 'metric': metric, 'units': len(rows),
                                    'mean_observed': float(np.mean(observed)), 'mean_shuffled': float(np.mean(shuffled)),
                                    'mean_absolute_u2_change': float(np.mean(np.abs(np.asarray(observed)-transformed))),
                                    'sorted_positive_mean': float(np.mean([r['diagnostics'][label]['sorted'][metric] for r in rows]))})
    result = {'schema': 1, 'status': 'derived_measured_observations', 'comparisons': comparisons, 'prefix_benchmarks': benchmarks,
              'excludes_zero_count': sum(c['excludes_zero'] for c in comparisons), 'prefix_threshold_count': sum(c['crosses_threshold'] for c in benchmarks),
              'primary_tests': config['primary_tests'], 'familywise_confidence_nominal': 1-config['familywise_alpha'], 'per_test_alpha': alpha,
              'inference': 'Bonferroni across 58 approximate mean/accuracy intervals and 20 exact Monte Carlo reference tests; conditional public pseudorandom-seed model. Approximate interval coverage is not an exact guarantee.',
              'prefix_interval_notes': 'Clopper-Pearson intervals describe the random-generator tail fraction, separately from the Monte Carlo reference rank. Minimum reference p is 1/(98304+1).',
              'ml': ml_metadata, 'discovery': summarize_discovery(old, config), 'diagnostics': diagnostics,
              'target_region_secondary': secondary, 'bank_extremes_exploratory': extremes,
              'secondary_notes': '100 region intervals form a separate exploratory family; not included in the 78 primary tests and not used to enlarge/stop sampling',
              'security_claim': 'none', 'rare_coverage': {str(q): 1-(1-q)**config['bank_generators'] for q in (1e-4, 1e-5, 1e-6)},
              'limitations': ['Two fixed Solinas primes, not a population of all Solinas primes', 'Fresh points on the existing random-field/model pool, not new independent field draws',
                              'Only fixed public feature menu, trimmed 256-point prefixes, and finite targeted regions', 'Official generator chosen once; independent starts are not independently chosen official generators',
                              'Zero resolved feature effects do not exclude algebraic structure, rare weaker effects, or greater ECDLP resistance']}
    immutable(output/'analysis.json', canonical(result))
    stream = io.StringIO(newline=''); writer = csv.DictWriter(stream, fieldnames=['case', 'population', 'metric', 'left', 'right', 'difference', 'low', 'high', 'left_units', 'right_units', 'excludes_zero'], lineterminator='\n'); writer.writeheader()
    for r in comparisons: writer.writerow({k: r[k] for k in writer.fieldnames if k not in ('low', 'high')} | {'low': r['interval'][0], 'high': r['interval'][1]})
    immutable(output/'comparisons.csv', stream.getvalue().encode())
    immutable(output/'discovery'/'analysis.json', canonical(result['discovery']))
    print(json.dumps({'stage': 'analysis-complete', 'mean_intervals': len(comparisons), 'resolved_mean_intervals': result['excludes_zero_count'],
                      'prefix_benchmarks': len(benchmarks), 'resolved_prefix_benchmarks': result['prefix_threshold_count'],
                      'ml_accuracy': {r['case']: r['accuracy'] for r in ml}}), flush=True)
