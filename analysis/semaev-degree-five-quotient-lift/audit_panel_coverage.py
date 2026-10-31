#!/usr/bin/env python3
"""Index audit of the preregistered n=33..45 D4 panel; no trials or certificate replay."""
import collections
import datetime
import hashlib
import json
from pathlib import Path


STUDY = Path('analysis/semaev-degree-five-quotient-lift')
EXPANSION = Path('/home/ec2-user/fall-degree-data-20261029/expansion')
INVENTORY = STUDY / 'runtime/panel-remaining-after-local008.json'
OUT = STUDY / 'validation/panel-coverage-20261031-001'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    data = path.read_bytes()
    return json.loads(data), sha(data)


def check_expansion(item, plan_sha):
    name = item['id']
    directory = EXPANSION / name
    results = sorted(directory.glob('attempt-*/result.json'))
    assert len(results) == 1, (name, results)
    result, result_file_sha = load(results[0])
    assert result['id'] == name and result['parameters'] == item and result['plan_sha256'] == plan_sha
    assert result['status'] in ('certificate_verified', 'closure_contains_one')
    inferences = sorted(directory.glob('inference-*.json'))
    assert len(inferences) == 1, (name, inferences)
    inference, inference_sha = load(inferences[0])
    canonical_sha = sha(json.dumps(result, sort_keys=True).encode())
    assert inference['id'] == name
    assert inference['closure_result_canonical_sha256'] == canonical_sha
    assert inferences[0].stem == 'inference-' + canonical_sha
    count = inference['count']
    assert count['plan_sha256'] == plan_sha and count['parameters'] == item['record']
    assert count['status'] == 'completed' and isinstance(count['ordered_solutions'], int)
    expected = 5 if result['status'] == 'certificate_verified' and count['ordered_solutions'] < result['certified_codimension_lower_bound'] else None
    assert inference['last_fall_degree_lower_bound'] == expected
    return {'id': name, 'n': item['record']['n'], 'family': item['record']['basis'],
            'source': 'expansion', 'status': result['status'], 'exact_solutions': count['ordered_solutions'],
            'checked_codimension_lower_bound': result.get('certified_codimension_lower_bound'),
            'last_fall_degree_lower_bound': expected,
            'result_path': str(results[0]), 'result_sha256': result_file_sha,
            'inference_path': str(inferences[0]), 'inference_sha256': inference_sha}


def check_later(item, reference):
    name = item['id']
    result_path = STUDY / reference['path']
    result, digest = load(result_path)
    assert digest == reference['result_sha256']
    assert result['prior_id'] == name and result['status'] == reference['status']
    assert result.get('last_fall_degree_lower_bound') == reference['last_fall_degree_lower_bound']
    assert result['status'] in ('certificate_verified', 'producer_contains_one')
    exact_count = result.get('exact_solutions')
    codim = result.get('certified_codimension_lower_bound')
    if result.get('last_fall_degree_lower_bound') == 5:
        assert isinstance(exact_count, int) and isinstance(codim, int) and exact_count < codim
    return {'id': name, 'n': item['record']['n'], 'family': item['record']['basis'],
            'source': 'later_panel', 'status': result['status'], 'exact_solutions': exact_count,
            'checked_codimension_lower_bound': codim,
            'last_fall_degree_lower_bound': result.get('last_fall_degree_lower_bound'),
            'result_path': str(result_path), 'result_sha256': digest}


def main():
    plan, plan_sha = load(EXPANSION / 'plan.json')
    inventory, inventory_sha = load(INVENTORY)
    planned = {item['id']: item for item in plan['items'] if item['degree'] == 4 and 33 <= item['record']['n'] <= 45}
    assert len(planned) == 140 and len(set(planned)) == 140
    assert inventory['terminal_count'] == 28 and inventory['certified_lfd_at_least5'] == 21
    expansion_ids = {name for name in planned if 33 <= planned[name]['record']['n'] <= 42 and
                     (EXPANSION / name / 'attempt-001/result.json').is_file()}
    later_ids = set(inventory['terminal_inputs'])
    assert not expansion_ids & later_ids
    assert expansion_ids | later_ids <= set(planned)
    rows = []
    for name in sorted(expansion_ids):
        rows.append(check_expansion(planned[name], plan_sha))
    for name in sorted(later_ids):
        rows.append(check_later(planned[name], inventory['terminal_inputs'][name]))
    missing = sorted(set(planned) - expansion_ids - later_ids)
    assert len(rows) == 136 and missing == [f'fresh-n45-rand-{i:02d}' for i in range(1, 5)]
    assert len({row['id'] for row in rows}) == len(rows)
    counts = {}
    for n in range(33, 46):
        subset = [row for row in rows if row['n'] == n]
        counts[str(n)] = {
            'planned': sum(item['record']['n'] == n for item in planned.values()),
            'terminal': len(subset),
            'certified_lfd_at_least5': sum(row['last_fall_degree_lower_bound'] == 5 for row in subset),
            'other_terminal': sum(row['last_fall_degree_lower_bound'] is None for row in subset),
        }
        assert counts[str(n)]['planned'] == counts[str(n)]['terminal'] + sum(planned[name]['record']['n'] == n for name in missing)
    assert sum(x['certified_lfd_at_least5'] for x in counts.values()) == 59
    assert sum(x['terminal'] for x in counts.values()) == 136
    OUT.mkdir(parents=True, exist_ok=False)
    record = {
        'schema': 'semaev.panel-coverage-audit/v1',
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Index and inference-chain audit of existing terminal records. Main certificates are not rehashed or replayed in this audit.',
        'plan_path': str(EXPANSION / 'plan.json'), 'plan_sha256': plan_sha,
        'later_inventory_path': str(INVENTORY), 'later_inventory_sha256': inventory_sha,
        'planned': 140, 'terminal': 136, 'certified_lfd_at_least5': 59,
        'other_terminal': 77, 'pending': 4, 'pending_ids': missing,
        'counts_by_n': counts, 'rows': rows,
    }
    (OUT / 'coverage.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record[key] for key in ('planned', 'terminal', 'certified_lfd_at_least5', 'other_terminal', 'pending', 'pending_ids')}))


if __name__ == '__main__':
    main()
