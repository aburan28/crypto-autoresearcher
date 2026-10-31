"""Advance the immutable late-panel inventory by one collected terminal input."""

from pathlib import Path
import argparse
import datetime
import hashlib
import json


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--collection', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    study = Path('analysis/semaev-degree-five-quotient-lift')
    assert not args.out.exists(), 'inventories are write-once'
    previous = json.loads(args.previous.read_text())
    collection = json.loads((args.collection / 'result.json').read_text())
    manifest = json.loads((args.collection / 'manifest.json').read_text())
    result = json.loads((args.collection / 'terminal.json').read_text())
    prior_id = collection['prior_id']
    assert prior_id in {item['prior_id'] for item in previous['items']}
    assert result['returncode'] == 0
    assert manifest['prior_id'] == prior_id and manifest['result_sha256'] == digest(args.collection / 'result.json')
    assert manifest['verified_artifact_count'] == 47
    if collection['last_fall_degree_lower_bound'] == 5:
        assert collection['status'] == 'certificate_verified'
        assert collection['certified_codimension_lower_bound'] > collection['exact_solutions']
    output = dict(previous)
    output['items'] = [item for item in previous['items'] if item['prior_id'] != prior_id]
    output['terminal_inputs'] = dict(previous['terminal_inputs'])
    output['terminal_inputs'][prior_id] = {
        'path': str((args.collection / 'result.json').relative_to(study)),
        'result_sha256': digest(args.collection / 'result.json'),
        'status': collection['status'],
        'last_fall_degree_lower_bound': collection['last_fall_degree_lower_bound'],
    }
    output['terminal_count'] = len(output['terminal_inputs'])
    output['certified_lfd_at_least5'] = sum(row['last_fall_degree_lower_bound'] == 5 for row in output['terminal_inputs'].values())
    assert output['terminal_count'] == previous['terminal_count'] + 1
    output['scope'] = (f"Derived from {output['terminal_count']} named terminal records; "
                       f"{len(output['items'])} original n45 random-subspace panel inputs remain; "
                       "no new draws. The separate n47 D4 seed is not a panel input.")
    output['created_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    link = {'path': str(args.previous.relative_to(study)), 'sha256': digest(args.previous)}
    output['prior_inventory'] = link
    output['previous_inventory'] = link['path']
    output['previous_inventory_sha256'] = link['sha256']
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'terminal': output['terminal_count'], 'certified_lfd_at_least5': output['certified_lfd_at_least5'],
                      'remaining': len(output['items']), 'sha256': digest(args.out)}))


if __name__ == '__main__':
    main()
