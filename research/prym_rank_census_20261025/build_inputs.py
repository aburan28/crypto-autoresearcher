"""Prospective public fixture construction; no relation collection or point logs."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SHARED = ROOT / 'research/prym_experiment_design_20261019/implementation'
sys.path.insert(0, str(SHARED))
from fixtures import attach_ec1, describe
from independent import verify_fixture


def build(config):
    excluded = set()
    for name in config['exclude_fixture_files']:
        for f in json.loads((ROOT / name).read_text())['fixtures']:
            excluded.add((f['p'], f['a'], f['b']))
    fixtures, trace = [], []
    for p in config['primes']:
        found = 0
        for b in range(1, p):
            a = config['fixed_A']
            if (p, a, b) in excluded:
                trace.append(dict(p=p, a=a, b=b, reason='previous_panel_excluded'))
                continue
            f, details = describe(p, a, b, config['factor_base_size'])
            entry = dict(p=p, a=a, b=b, **details)
            trace.append(entry)
            if f is None:
                continue
            if f['r'] == p:
                entry['reason'] = 'anomalous_excluded'
                continue
            # C smoothness is equivalent here to B != 0 and 4 A^3+27 B^2 != 0.
            # E2 has discriminant -16 B^2 (4 A^3+27 B^2).
            verify_fixture(f)
            fixtures.append(attach_ec1(f))
            found += 1
            if found == config['fixtures_per_prime']:
                break
        if found != config['fixtures_per_prime']:
            raise RuntimeError('finite fixture construction exhausted')
    return dict(schema='prym-rank-census-fixtures/v1', fixtures=fixtures,
                search_trace=trace, source_generation=config,
                secret_labels_present=False, relation_acceptance_observed=False)


if __name__ == '__main__':
    directory = Path(__file__).resolve().parent
    data = build(json.loads((directory / 'config.json').read_text()))
    with (directory / 'fixtures.json').open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(fixtures=len(data['fixtures']), inspected=len(data['search_trace']),
                          acceptance_observed=False)))
