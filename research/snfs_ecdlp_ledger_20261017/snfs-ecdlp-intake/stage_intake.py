#!/usr/bin/env python3
"""Validate/stage the supplied ledger. This is not the campaign harness.

Requires Python 3 and PyYAML. No network calls or experiment execution.
Run with --verify to check existing outputs without changing them.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import secrets

import yaml

ROOT = Path(__file__).resolve().parent
REQUIRED = {
    'provisional_id', 'title', 'lane', 'status', 'mechanism', 'hypothesis',
    'experiment', 'measurements', 'controls', 'stopping_rule',
    'cost_estimate_cpu_hours', 'sources', 'novelty',
}


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'Duplicate YAML key {key!r}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest_record(record):
    return digest_bytes(json.dumps(record, sort_keys=True,
                                  ensure_ascii=False).encode())


def read_json(name):
    return json.loads((ROOT / name).read_text())


def save_json(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2,
                                      ensure_ascii=False) + '\n')


def load_source():
    raw = (ROOT / 'source.yaml').read_text()
    document = yaml.load(raw, Loader=UniqueLoader)
    tree = yaml.compose(raw)
    roots = {key.value: value for key, value in tree.value}
    repairs, lines = [], {}
    for record, node in zip(document['records'], roots['records'].value):
        fields = {key.value: value for key, value in node.value}
        pid = record['provisional_id']
        lines[pid] = node.start_mark.line + 1
        for index, item in enumerate(fields['experiment'].value):
            if isinstance(item, yaml.MappingNode):
                # Preserve the exact original prose, including its colon.
                value = raw[item.start_mark.index:item.end_mark.index].strip()
                record['experiment'][index] = value
                repairs.append({
                    'record': pid, 'field': f'experiment[{index}]',
                    'source_line': item.start_mark.line + 1,
                    'from_yaml_type': 'mapping', 'to_type': 'string',
                    'preserved_text': value,
                })
    return document, repairs, lines


def status_class(raw):
    for prefix in ('theorem-closed-control', 'negative-control', 'open'):
        if raw.startswith(prefix):
            return prefix
    raise ValueError(f'Unknown status {raw}')


def dependencies():
    # Preserve priority independently from data/control dependencies.
    return [
        {'from': 'SNFS-A1', 'to': target, 'kind': 'control'}
        for target in ('SNFS-A2', 'SNFS-A3', 'SNFS-A4')
    ] + [
        {'from': 'SNFS-A2', 'to': 'SNFS-A3', 'kind': 'optional-solver'},
        {'from': 'SNFS-E1', 'to': 'SNFS-E2', 'kind': 'lattice-input'},
        {'from': 'SNFS-D2', 'to': 'SNFS-E2', 'kind': 'comparison'},
        {'from': 'SNFS-E1', 'to': 'SNFS-E4',
         'kind': 'measured-lattice-input; synthetic branch independent'},
        {'from': 'SNFS-E1', 'to': 'SNFS-E3',
         'kind': 'surface-input; source permits own-fibre fallback'},
        {'from': 'SNFS-E4', 'to': 'SNFS-E3', 'kind': 'instance-sizing'},
        {'from': 'SNFS-B2', 'to': 'SNFS-B5', 'kind': 'positive-control'},
        {'from': 'SNFS-B3', 'to': 'SNFS-B5', 'kind': 'positive-control'},
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    document, repairs, lines = load_source()
    records = document['records']
    batch = document['batch']
    identifiers = [record['provisional_id'] for record in records]
    assert len(records) == batch['record_count'] == 23
    assert len(identifiers) == len(set(identifiers))
    assert set(batch['priority_order']) <= set(identifiers)
    assert len(batch['priority_order']) == len(set(batch['priority_order']))
    totals = [0, 0]
    classes = Counter()
    for record in records:
        assert REQUIRED <= record.keys(), record['provisional_id']
        for name in REQUIRED - {'lane', 'experiment', 'measurements',
                                 'sources', 'cost_estimate_cpu_hours'}:
            assert isinstance(record[name], str) and record[name]
        assert set(record['lane']) <= set(batch['lanes'])
        for name in ('experiment', 'measurements', 'sources'):
            assert isinstance(record[name], list) and record[name]
            assert all(isinstance(value, str) for value in record[name])
        bounds = str(record['cost_estimate_cpu_hours']).split('-')
        lower, upper = int(bounds[0]), int(bounds[-1])
        assert 0 <= lower <= upper
        totals[0] += lower
        totals[1] += upper
        classes[status_class(record['status'])] += 1

    audit = read_json('audit-findings.json')
    assert len({item['key'] for item in audit['findings']}) == len(audit['findings'])
    for finding in audit['findings']:
        assert set(finding['records']) <= set(identifiers)
    edges = dependencies()
    # Check the recorded dependency graph has no invalid targets or cycles.
    remaining = set(identifiers)
    while remaining:
        available = {pid for pid in remaining if not any(
            edge['to'] == pid and edge['from'] in remaining for edge in edges)}
        assert available, 'dependency cycle'
        remaining -= available
    assert all({edge['from'], edge['to']} <= set(identifiers) for edge in edges)

    source_sha = digest_bytes((ROOT / 'source.yaml').read_bytes())
    manifest_path = ROOT / 'intake-manifest.json'
    if manifest_path.exists():
        manifest = read_json(manifest_path.name)
        assert manifest['source_sha256'] == source_sha, 'Source changed; review lineage first'
    else:
        assert not args.verify, 'Manifest missing'
        seeds = set()
        entries = []
        for record in records:
            seed = secrets.token_hex(16)
            while seed in seeds:
                seed = secrets.token_hex(16)
            seeds.add(seed)
            cls = status_class(record['status'])
            entries.append({
                'provisional_id': record['provisional_id'],
                'immutable_id': None,
                'lineage': [{'batch_provisional_id': batch['provisional_id'],
                             'record_provisional_id': record['provisional_id'],
                             'source_sha256': source_sha}],
                'source_line': lines[record['provisional_id']],
                'record_sha256': digest_record(record),
                'seed_candidate_hex': seed,
                'seed_reservation_state': 'pending-campaign-registry-check',
                'status_class': cls,
                'original_status': record['status'],
                'evidence_eligibility': ('receipt-only' if cls == 'theorem-closed-control'
                                         else 'bounded-measurement-after-preflight'),
                'execution_state': 'not-run',
                'audit_keys': [finding['key'] for finding in audit['findings']
                               if record['provisional_id'] in finding['records']],
            })
        manifest = {
            'format': 'local-staging-v1; not an existing harness schema',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'batch_provisional_id': batch['provisional_id'],
            'campaign_id': None,
            'source_sha256': source_sha,
            'registry_import_state': 'pending-existing-harness-location',
            'immutable_id_policy': 'Only the existing harness assigns immutable IDs',
            'collision_policy': 'Merge lineage into matching canonical record; do not rename',
            'registry_collision_check': 'not-performed; registry unavailable',
            'seed_policy': '128-bit candidates unique within this batch; not reserved campaign-wide',
            'authorization': 'Standing approval retained; no additional approval inferred or requested',
            'field_mapping': 'All batch and record keys/values retained in normalized-ledger.json; normalization is limited to ten colon-bearing experiment entries',
            'status_policy': 'Original status and novelty retained verbatim; class mapping is metadata, not theorem certification',
            'priority_order': batch['priority_order'],
            'unprioritized_records': [pid for pid in identifiers
                                     if pid not in batch['priority_order']],
            'dependency_edges': edges,
            'external_inputs': {
                'SNFS-D1': ['rank-campaign point, independence and saturation certificates'],
                'SNFS-A3': ['WDSat', 'Boolean F5B/M4RI', 'Macaulay cache'],
                'SNFS-E3': ['WDSat', 'Boolean F5B/M4RI', 'Macaulay cache',
                            'ic relation/matrix stages'],
                'SNFS-B7': ['ic factor-base/relation/matrix stages'],
            },
            'claim_boundary': batch['claim_boundary'],
            'additional_execution_constraints': {
                'SNFS-B4': 'Public parameter calculations and polynomial selection only; no sieving under any circumstances',
                'all': 'Resolve applicable preflight notes and use the existing execution/evidence protections; no experiment was run by this staging script',
            },
            'records': entries,
        }

    assert [entry['provisional_id'] for entry in manifest['records']] == identifiers
    candidates = [entry['seed_candidate_hex'] for entry in manifest['records']]
    assert len(candidates) == len(set(candidates)) == 23
    assert all(len(seed) == 32 and int(seed, 16) >= 0 for seed in candidates)
    assert manifest['registry_collision_check'].startswith('not-performed')
    assert manifest['priority_order'] == batch['priority_order']
    assert manifest['dependency_edges'] == edges
    for entry, record in zip(manifest['records'], records):
        assert entry['immutable_id'] is None
        assert entry['record_sha256'] == digest_record(record)
        assert entry['execution_state'] == 'not-run'
        assert entry['seed_reservation_state'] == 'pending-campaign-registry-check'
        assert entry['original_status'] == record['status']
        assert entry['evidence_eligibility'].startswith('receipt-only') == (
            status_class(record['status']) == 'theorem-closed-control')
        assert entry['audit_keys'] == [finding['key'] for finding in audit['findings']
                                       if record['provisional_id'] in finding['records']]

    report = {
        'scope': 'Structural validation and arithmetic preflight only; no scientific experiment outcomes',
        'source_sha256': source_sha,
        'audit_sha256': digest_bytes((ROOT / 'audit-findings.json').read_bytes()),
        'record_count': len(records),
        'source_record_field_counts': {record['provisional_id']: len(record) for record in records},
        'status_class_counts': dict(classes),
        'lane_counts': dict(Counter(lane for record in records for lane in record['lane'])),
        'declared_cpu_hours': {'min': totals[0], 'max': totals[1],
                               'measured': False, 'includes_uncertainty': False},
        'normalizations': repairs,
        'checks': {
            'required_fields_present': True,
            'unknown_fields_retained': True,
            'provisional_ids_unique_within_batch': True,
            'priorities_resolve': True,
            'dependencies_resolve_and_are_acyclic': True,
            'source_statuses_and_novelty_retained': True,
            'batch_seed_candidates_unique': True,
            'canonical_ids_assigned': False,
            'registry_collision_checks_completed': False,
            'campaign_seeds_reserved': False,
            'scientific_experiments_executed': False,
            'hypotheses_promoted_to_results': False,
        },
        'arithmetic_preflight': {
            'A4_valid_n_d_pairs': [[n, d] for n in (31, 61, 89, 127)
                                    for d in (2, 3, 5) if n % d == 0],
            'D4_null_model': {
                'assumed_subgroup_order': 2**32,
                'nonzero_hit_expectations': {
                    str(rank): (61**rank - 1) / 2**32 for rank in (2, 3, 4)},
                'assumption': 'Approximately uniform map to a subgroup of this order; deterministic origin excluded',
            },
            'E4_illustration': {
                'gram_matrix': '18 I_100 (synthetic example only)',
                'p_proxy': '2^256 (size proxy, not a prime)',
                'rank': 100,
                'height_as_squared_norm': math.exp((2*256*math.log(2)
                    - 2*(50*math.log(math.pi)-math.lgamma(51)))/100)*18,
                'interpretation': 'Volume heuristic only; does not refute a numerical claim about a different determinant',
            },
        },
        'audit_finding_count': len(audit['findings']),
        'pending_integration': [
            'Existing harness location and schema',
            'Campaign identity and canonical collision/lineage lookup',
            'Campaign-wide seed reservation and per-instance derivation rules',
            'Execution/evidence protection configuration and reusable certificates',
        ],
    }
    if args.verify:
        assert read_json('normalized-ledger.json') == document
        assert read_json('validation.json') == report
    else:
        save_json('normalized-ledger.json', document)
        save_json('intake-manifest.json', manifest)
        save_json('validation.json', report)
    print(json.dumps({'mode': 'verified' if args.verify else 'staged',
                      'records': len(records), 'yaml_normalizations': len(repairs),
                      'declared_cpu_hours': totals,
                      'scientific_experiments_executed': False,
                      'registry_import_state': manifest['registry_import_state']}))


if __name__ == '__main__':
    main()
