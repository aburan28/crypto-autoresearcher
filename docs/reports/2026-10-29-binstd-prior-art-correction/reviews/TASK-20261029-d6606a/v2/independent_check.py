"""Independent J1 checks. All writes stay under this review task directory.

No producer code is imported or executed. The pinned validator and its real
reference resolver run against a six-card scratch tree to avoid corpus scans.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import yaml

REPO = Path('/home/ec2-user/crypto-autoresearcher-binstd-prior-correction-20261029')
OUT = Path(__file__).resolve().parent
TREE = OUT / 'read_inputs'
SNAPSHOT = 'dd603f5db2f92076663850fe4c5dd859dc1edb0c'
BASE = '7e45528b293fd42049b1486a03135670ab5ac55c'
PACKET = 'docs/reports/2026-10-29-binstd-prior-art-correction/'
read_log = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_read(commit, path, purpose):
    data = subprocess.check_output(['git', '-C', str(REPO), 'show', commit + ':' + path])
    key = (commit, path)
    if key not in read_log:
        read_log[key] = {'commit': commit, 'path': path, 'sha256': sha(data), 'purposes': []}
    if purpose not in read_log[key]['purposes']:
        read_log[key]['purposes'].append(purpose)
    return data


def pkt(path, purpose='packet binding verification'):
    return git_read(SNAPSHOT, PACKET + path, purpose)


def save_copy(path, data):
    dest = TREE / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        assert dest.read_bytes() == data, str(dest)
    else:
        dest.write_bytes(data)
    return dest


class UniqueLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for kn, vn in node.value:
            key = self.construct_object(kn, deep=deep)
            if key in result:
                raise ValueError('duplicate mapping key: ' + str(key))
            result[key] = self.construct_object(vn, deep=deep)
        return result


def parse(raw):
    return yaml.load(raw, Loader=UniqueLoader)


def differences(a, b, path=()):
    """Enumerate actual typed value changes, skipping exactly idea.prior_art."""
    if path == ('idea', 'prior_art'):
        return []
    if type(a) is not type(b):
        return [{'path': list(path), 'before': a, 'after': b, 'kind': 'type'}]
    if isinstance(a, dict):
        result = []
        for key in a.keys() | b.keys():
            sub = path + (key,)
            if sub == ('idea', 'prior_art'):
                continue
            if key not in a or key not in b:
                result.append({'path': list(sub), 'kind': 'missing_key'})
            else:
                result += differences(a[key], b[key], sub)
        return result
    if isinstance(a, list):
        if len(a) != len(b):
            return [{'path': list(path), 'kind': 'length'}]
        return [d for index, (x, y) in enumerate(zip(a, b))
                for d in differences(x, y, path + (index,))]
    if a != b:
        return [{'path': list(path), 'before': a, 'after': b, 'kind': 'value'}]
    return []


def tagged_values(node, path=()):
    """Independent YAML AST view catches type/coercion changes hidden by ==."""
    if path == ('idea', 'prior_art'):
        return []
    if isinstance(node, yaml.MappingNode):
        return sorted((r for key, val in node.value
                       for r in tagged_values(val, path + (key.value,))), key=repr)
    if isinstance(node, yaml.SequenceNode):
        return [r for i, val in enumerate(node.value)
                for r in tagged_values(val, path + (i,))]
    return [(path, node.tag, node.value)]


handoff = json.loads(pkt('handoff.json', 'initial scope and binding instructions'))
plan = json.loads(pkt('review-plan.json', 'initial prospective review instructions'))
sources = json.loads(pkt('sources.json', 'embedded originals, effective sources and source bindings'))
manifest = json.loads(pkt('candidates-v2.json', 'candidate and proposed registry bindings'))
assert sources['source_commit'] == manifest['source_commit'] == handoff['source_commit'] == BASE
assert subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', SNAPSHOT + '^']).decode().strip() == BASE

packet_checks = []
for path, expected in handoff['source_bindings'].items():
    actual = sha(pkt(path))
    assert actual == expected, path
    packet_checks.append({'path': path, 'sha256': actual})

records = {r['path']: r for r in sources['records']}
source_checks = []
for path, row in records.items():
    data = git_read(BASE, path, 'source byte and SHA-256/Git object verification')
    assert data == row['text'].encode('utf-8'), path
    assert sha(data) == row['sha256'], path
    actual_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert actual_blob == row['git_blob'], path
    snapshot_data = git_read(SNAPSHOT, path, 'verify original and prior replacement bytes unchanged at reviewed snapshot')
    assert snapshot_data == data, path
    source_checks.append({'path': path, 'sha256': sha(data), 'git_blob': actual_blob,
                          'snapshot_unchanged': True})
    if path.startswith('knowledge/') or path in {x[k] for x in manifest['records'] for k in ('original_path', 'effective_path')}:
        save_copy(path, data)

registry_path = 'tools/schema_supersession_registry.yaml'
registry_raw = git_read(BASE, registry_path, 'old selected registry bindings and whole-file digest')
assert sha(registry_raw) == sources['registry_sha256']
assert git_read(SNAPSHOT, registry_path, 'verify registry unchanged at reviewed snapshot') == registry_raw
registry = parse(registry_raw)
selected = {x['original_path']: x for x in sources['selected']}
for path in ('tools/validate_ledger.py', 'tools/build_frontier_map.py', 'orchestration/fast_yaml.py'):
    save_copy(path, git_read(BASE, path, 'unmodified targeted validator or reference-resolver dependency'))
git_read(BASE, 'AGENTS.md', 'reviewer role, prospective review and immutable-record policy')

# Import exact pinned source bytes in a scratch tree. No producer imports,
# no resolver stubs, and no access to other knowledge rows or the live tree.
sys.dont_write_bytecode = True
sys.path[:0] = [str(TREE / 'orchestration'), str(TREE / 'tools')]
spec = importlib.util.spec_from_file_location('j1_pinned_validator', TREE / 'tools/validate_ledger.py')
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


def errors(doc, original_path):
    context = validator.Ctx(set())
    validator.check_prior_art(str(TREE / original_path), doc['idea'], context)
    return context.errors


checks = []
controls = []
lineage_checks = []
new_registry_rows = []
old_registry_rows = []
for item in manifest['records']:
    original_path = item['original_path']
    effective_path = item['effective_path']
    old_data = records[effective_path]['text'].encode()
    new_data = pkt(item['candidate'], 'independent full typed-field and attribution comparison')
    assert sha(new_data) == item['candidate_sha256']
    assert records[original_path]['sha256'] == item['original_sha256']
    assert records[effective_path]['sha256'] == item['effective_sha256']
    old, new = parse(old_data), parse(new_data)
    assert old['idea']['id'] == new['idea']['id'] == item['id']
    diff = differences(old, new)
    assert not diff, (item['id'], diff)
    old_ast = tagged_values(yaml.compose(old_data))
    new_ast = tagged_values(yaml.compose(new_data))
    assert old_ast == new_ast, item['id']
    prior_old = old['idea'].get('prior_art')
    prior_new = new['idea']['prior_art']
    moved = [] if not prior_old else [r for r in prior_old['nearest'] if str(r['ref']).startswith('IDEA-')]
    assert prior_new.get('internal_lineage', []) == moved
    for before, after in zip(moved, prior_new.get('internal_lineage', [])):
        assert type(before) is type(after)
        assert all(type(before[k]) is type(after[k]) and before[k] == after[k] for k in before)
    if prior_old:
        assert prior_old['searched'] == prior_new['searched']
        assert prior_old['rows_checked'] == prior_new['rows_checked']
        assert prior_old['frontier_map_commit'] == prior_new['frontier_map_commit']
    else:
        assert prior_new['searched']['corpus_grep'] == prior_new['searched']['web'] == []
        assert 'no search log at proposal time is asserted' in prior_new['searched']['note']
    retro = prior_new['retrospective_review']
    assert retro['read_on'] == '2026-10-29'
    assert retro['source_commit'] == BASE
    assert 'not evidence of a pre-proposal' in retro['scope']
    assert 'heuristic' in retro['literature_verification'] and 'abstract_read' in retro['literature_verification']
    lineage_checks.append({'id': item['id'], 'moved_entries': moved, 'exact_parsed_values_retained': True,
                           'historical_search_block_preserved': bool(prior_old)})

    matching = [r for r in registry['records'] if r['superseded_path'] == original_path]
    assert len(matching) <= 1
    actual_route = matching[0] if matching else None
    assert actual_route == selected[original_path]['route'] == item['prior_registry_entry']
    if actual_route:
        assert actual_route['superseding_path'] == effective_path
        assert actual_route['superseding_sha256'] == item['effective_sha256']
        old_registry_rows.append(actual_route)
    new_route = item['proposed_registry_entry']
    assert new_route['superseded_path'] == original_path
    assert new_route['superseded_sha256'] == item['original_sha256']
    assert new_route['superseding_path'] == item['proposed_destination']
    assert new_route['superseding_sha256'] == item['candidate_sha256']
    assert new_route['kind'] == 'ledger' and new_route['registered'] == '2026-10-29'
    save_copy(item['proposed_destination'], new_data)
    new_registry_rows.append(new_route)

    before, after = errors(old, original_path), errors(new, original_path)
    assert len(before) == 1 and after == [], (item['id'], before, after)
    checks.append({'id': item['id'], 'outside_prior_art_differences': diff,
                   'outside_prior_art_tagged_scalar_count': len(old_ast),
                   'tagged_scalar_ast_equal': True, 'before': before, 'after': after,
                   'old_registry_binding_matches': True, 'new_registry_binding_matches': True})

    for mutation in ('claim', 'nested_formal_statement', 'approval'):
        bad = copy.deepcopy(new)
        if mutation == 'claim':
            bad['idea']['claim'] = 'CONTROL unauthorized result'
        elif mutation == 'nested_formal_statement':
            bad['idea']['heuristic_assumptions'][0]['formal_statement'] += ' CONTROL threshold changes'
        else:
            bad['idea']['approved_by'] = 'CONTROL invented retrospective approval'
        changes = differences(old, bad)
        assert changes
        controls.append({'id': item['id'], 'control': mutation, 'detection': 'independent typed field comparator',
                         'differences': changes, 'passed': True})
    for mutation in ('internal_nearest', 'missing_prior_art', 'unknown_kr', 'empty_delta', 'invalid_relation'):
        bad = copy.deepcopy(new)
        if mutation == 'internal_nearest':
            bad['idea']['prior_art']['nearest'][0]['ref'] = 'IDEA-20261003-f20e41'
        elif mutation == 'missing_prior_art':
            bad['idea'].pop('prior_art')
        elif mutation == 'unknown_kr':
            bad['idea']['prior_art']['nearest'][0]['ref'] = 'KR-IC-000000'
        elif mutation == 'empty_delta':
            bad['idea']['prior_art']['nearest'][0]['delta'] = ''
        else:
            bad['idea']['prior_art']['nearest'][0]['relation'] = 'proves'
        found = errors(bad, original_path)
        assert found, (item['id'], mutation)
        controls.append({'id': item['id'], 'control': mutation,
                         'detection': 'unmodified pinned check_prior_art', 'errors': found, 'passed': True})
    if moved:
        bad = copy.deepcopy(new)
        bad['idea']['prior_art']['internal_lineage'][0]['delta'] += ' CONTROL altered lineage'
        assert bad['idea']['prior_art']['internal_lineage'] != moved
        controls.append({'id': item['id'], 'control': 'lineage_mutation',
                         'detection': 'independent lineage equality', 'passed': True})
    # Proves-too-much: the schema intentionally cannot validate semantic truth.
    bad = copy.deepcopy(new)
    bad['idea']['prior_art']['nearest'][0]['delta'] = 'CONTROL: this card proves all diversity floors and an ECDLP attack improvement.'
    bad['idea']['prior_art']['retrospective_review']['scope'] = 'CONTROL: this proves a literature search before the 2026-10-03 proposal.'
    found = errors(bad, original_path)
    assert not found
    controls.append({'id': item['id'], 'control': 'false_semantic_claim_still_schema_green',
                     'detection': 'documents semantic limit; manual fidelity review required',
                     'errors': found, 'expected_schema_acceptance': True, 'passed': True})


def registry_check(rows, name):
    path = OUT / name
    path.write_text(yaml.safe_dump({'schema': 'schema-supersession-registry-v1', 'records': rows}, sort_keys=False))
    routes = validator.load_schema_supersessions(str(path))
    context = validator.Ctx(set(), schema_supersessions=routes)
    validator.check_schema_supersessions(context, routes)
    return routes, context.errors


old_routes, old_errors = registry_check(old_registry_rows, 'scratch_old_registry.yaml')
new_routes, new_errors = registry_check(new_registry_rows, 'scratch_proposed_registry.yaml')
assert not old_errors and not new_errors
route_controls = []
for row in new_registry_rows:
    for field in ('superseded_sha256', 'superseding_sha256'):
        bad_rows = copy.deepcopy(new_registry_rows)
        next(r for r in bad_rows if r['superseded_path'] == row['superseded_path'])[field] = '0' * 64
        _, found = registry_check(bad_rows, 'scratch_registry_hash_control.yaml')
        assert len(found) == 1 and 'hash changed' in found[0]
        route_controls.append({'original_path': row['superseded_path'], 'control': field + '_tamper',
                               'errors': found, 'passed': True})
for item in manifest['records']:
    path = str(TREE / item['original_path'])
    context = validator.Ctx(set(), schema_supersessions=new_routes)
    assert context.source_path(path) == str(TREE / item['proposed_destination'])

# Record full candidate field and source statuses without pretending an AST or
# digest comparison is a scientific review of the contextual evidence records.
card_statuses = []
for row in sources['records']:
    if row['path'].startswith('knowledge/'):
        card = parse(row['text'])
        card_statuses.append({'id': card['id'], 'status': card['status'], 'sources': card['sources']})
result = {
    'joint': 'J1', 'task': 'TASK-20261029-d6606a', 'snapshot': SNAPSHOT, 'source_commit': BASE,
    'verdict': 'mechanical_checks_hold', 'packet_sha256_checks': packet_checks,
    'source_checks': source_checks, 'registry_sha256': sha(registry_raw),
    'validator_sha256': sha((TREE / 'tools/validate_ledger.py').read_bytes()),
    'pyyaml_version': yaml.__version__, 'python_version': sys.version,
    'candidate_checks': checks, 'lineage_checks': lineage_checks, 'card_statuses': card_statuses,
    'prior_art_errors_before': sum(len(c['before']) for c in checks),
    'prior_art_errors_after': sum(len(c['after']) for c in checks),
    'controls': controls, 'registry_controls': route_controls,
    'old_targeted_registry_errors': old_errors, 'proposed_targeted_registry_errors': new_errors,
    'reference_resolution_scope': 'Unmodified real resolver enumerates only the six copied KR source files in this task scratch tree.',
    'registry_scope': 'Real loader/hash checker and routing tested only on four proposed rows in scratch; no live application or full registry validation.',
    'producer_checker': 'Read but not executed, imported, or used as preservation oracle.',
    'full_ledger_run': False, 'scientific_experiments': False, 'network_research': False,
    'sources_read': list(read_log.values()),
}
(OUT / 'independent_output.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({k: result[k] for k in ('joint', 'verdict', 'prior_art_errors_before', 'prior_art_errors_after', 'validator_sha256')}, indent=2))
print('Source bindings:', len(source_checks), 'Packet bindings:', len(packet_checks))
print('Candidate controls:', len(controls), 'Registry hash controls:', len(route_controls))
print('All mechanical assertions passed. Full-ledger validation and live application were not run.')
