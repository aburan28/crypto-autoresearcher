"""Additional same-session report checks; never modifies frozen measurement source."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; REPO = HERE.parents[2]
TASK = REPO/'tasks/solinas_higher_order'; RUN = TASK/'runs/higher-order-20261012'
sys.path.insert(0, str(TASK))
from research import canonical, check_source
from metrics import features, transport, encode, decode
from native import seed_for


def main():
    design = check_source(RUN); config = design['config']; analysis = json.loads((RUN/'analysis.json').read_text())
    counts = {'diagnostic_feature_replays': 0, 'transport_prefix_feature_replays': 0}
    for path in sorted((RUN/'records').glob('*.json')):
        record = json.loads(path.read_text()); p = record['job']['curve']['p']; width = (p.bit_length()+7)//8
        relevant = record['job']['kind'] == 'walk' and record['diagnostics']
        if not relevant and not any('isomorphic_u2' in u for u in record['units']): continue
        raw = (RUN/record['raw']['path']).read_bytes()
        for unit in record['units']:
            begin = unit['offset_points']*2*width; end = begin+unit['points']*2*width; part = raw[begin:end]
            if 'isomorphic_u2' in unit:
                if features(transport(part, p), p) != unit['isomorphic_u2']: raise ValueError('u=2 prefix feature replay differs')
                counts['transport_prefix_feature_replays'] += 1
            if relevant:
                coords = decode(part, p); arr = np.frombuffer(part, dtype=np.uint8).reshape(-1, 2*width)
                rng = np.random.default_rng(int.from_bytes(seed_for(config['seed'], record['job']['id'], unit['label'], 'shuffle')[:8], 'big'))
                companions = {'shuffled': arr[rng.permutation(len(arr))].tobytes(),
                              'sorted': encode(sorted(coords), p), 'isomorphic_u2': transport(part, p)}
                for name, data in companions.items():
                    if features(data, p) != record['diagnostics'][unit['label']][name]: raise ValueError('Walk companion replay differs')
                    counts['diagnostic_feature_replays'] += 1
    if len(analysis['comparisons']) != 58 or len(analysis['prefix_benchmarks']) != 20: raise ValueError('Primary family count differs')
    if len(analysis['target_region_secondary']) != 100: raise ValueError('Exploratory region count differs')
    if len(analysis['discovery']['comparisons']) != 56: raise ValueError('Exploratory discovery count differs')
    for outcome in analysis['comparisons']:
        if not outcome['interval'][0] <= outcome['difference'] <= outcome['interval'][1]: raise ValueError('Interval/estimate differs')
        if 'ML' in outcome['population'] and outcome['left_units'] != config['walk_blocks']: raise ValueError('ML per-point inference')
    for benchmark in analysis['prefix_benchmarks']:
        expected = (benchmark['as_or_more_extreme']+1)/(benchmark['bank_generators']+1)
        if benchmark['monte_carlo_p'] != expected: raise ValueError('Monte Carlo ties or plus-one correction differs')
    report = {'schema': 1, 'status': 'passed', 'counts': counts, 'family_counts': {'primary_intervals': 58, 'primary_prefix_tests': 20,
              'exploratory_regions': 100, 'exploratory_discovery': 56}, 'source_design_sha256': hashlib.sha256(canonical(design)).hexdigest(),
              'scope': 'Additional deterministic checks of already measured diagnostic artifacts and inference bookkeeping; same-session, no scientific-state claim'}
    (HERE/'additional-verification.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps(report))


if __name__ == '__main__': main()
