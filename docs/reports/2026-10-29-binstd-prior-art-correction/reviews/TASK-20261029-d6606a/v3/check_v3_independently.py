"""Narrow independent successor review; never imports producer checkers."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import yaml

OUT = Path(__file__).resolve().parent
SEALED = OUT.parent
REPO = '/home/ec2-user/crypto-autoresearcher-binstd-prior-correction-20261029'
PREVIOUS = 'dd603f5db2f92076663850fe4c5dd859dc1edb0c'
SNAPSHOT = 'c49b7f123d21e4a9c03465f3c56003a3df9917dd'
BASE = '7e45528b293fd42049b1486a03135670ab5ac55c'
PACKET = 'docs/reports/2026-10-29-binstd-prior-art-correction/'
reads = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(commit, path, purpose):
    raw = subprocess.check_output(['git', '-C', REPO, 'show', commit + ':' + path])
    key = (commit, path)
    if key not in reads:
        reads[key] = {'commit': commit, 'path': path, 'sha256': sha(raw), 'purposes': []}
    if purpose not in reads[key]['purposes']:
        reads[key]['purposes'].append(purpose)
    return raw


def packet(path, commit=SNAPSHOT):
    return git(commit, PACKET + path, 'successor source/binding and exact delta check')


class Unique(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in result:
                raise ValueError('duplicate YAML key: ' + str(key))
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def parse(raw):
    return yaml.load(raw, Loader=Unique)


def diff(left, right, path=()):
    if type(left) is not type(right):
        return [{'path': list(path), 'kind': 'type', 'old': left, 'new': right}]
    if isinstance(left, dict):
        result = []
        for key in sorted(left.keys() | right.keys()):
            sub = path + (key,)
            if key not in left:
                result.append({'path': list(sub), 'kind': 'added', 'new': right[key]})
            elif key not in right:
                result.append({'path': list(sub), 'kind': 'removed', 'old': left[key]})
            else:
                result += diff(left[key], right[key], sub)
        return result
    if isinstance(left, list):
        if len(left) != len(right):
            return [{'path': list(path), 'kind': 'length'}]
        return [d for i, (a, b) in enumerate(zip(left, right)) for d in diff(a, b, path + (i,))]
    if left != right:
        return [{'path': list(path), 'kind': 'value', 'old': left, 'new': right}]
    return []


sealed_expected = {
    'report.md': '9622f2bf92f8de1cd94ccd7f6b58cf2a6d3fbd47b1cf4b6d18d8e3f73d1317d1',
    'attestation.json': '600e85937963f1e3c7b3dc07398173ac17b984441fe188e313288c6288d9fab8',
    'independent_check.py': 'cf873aa979e2f20f5c766cbb84fc09d06916bce849c07769094bd4e1eaf63afe',
    'independent_output.json': 'e14145180de3792752883daf61e7c22fb4a741b2408d1b02e132d76062ff2ba7',
}
for path, expected in sealed_expected.items():
    assert sha((SEALED / path).read_bytes()) == expected
previous_results = json.loads((SEALED / 'independent_output.json').read_text())
handoff = json.loads(packet('handoff-v3.json'))
assert handoff['parent_snapshot'] == PREVIOUS
assert subprocess.check_output(['git', '-C', REPO, 'rev-parse', SNAPSHOT + '^']).decode().strip() == PREVIOUS
for path, expected in handoff['bindings'].items():
    assert sha(packet(path)) == expected, path
old_handoff = json.loads(packet('handoff.json', PREVIOUS))
for path, expected in old_handoff['source_bindings'].items():
    assert sha(packet(path)) == expected, ('previous packet mutated', path)
sources = json.loads(packet('sources.json'))
records = {r['path']: r for r in sources['records']}
for path, row in records.items():
    assert sha(git(SNAPSHOT, path, 'verify all bound source bytes remain unchanged at successor')) == row['sha256']
registry = git(SNAPSHOT, 'tools/schema_supersession_registry.yaml', 'verify live registry bytes unchanged at successor')
assert sha(registry) == sources['registry_sha256']
old_manifest = json.loads(packet('candidates-v2.json', PREVIOUS))
manifest = json.loads(packet('candidates-v3.json'))
old_items = {r['id']: r for r in old_manifest['records']}
assert manifest['source_commit'] == BASE

# Reuse only previously hash-verified reviewer scratch copies of exact pinned
# validator modules/cards. Importing the module does not run its CLI.
sys.dont_write_bytecode = True
tree = SEALED / 'read_inputs'
for path in ('tools/validate_ledger.py', 'tools/build_frontier_map.py', 'orchestration/fast_yaml.py'):
    expected = next(x['sha256'] for x in previous_results['sources_read'] if x['commit'] == BASE and x['path'] == path)
    assert sha((tree / path).read_bytes()) == expected
sys.path[:0] = [str(tree / 'orchestration'), str(tree / 'tools')]
spec = importlib.util.spec_from_file_location('v3_review_validator', tree / 'tools/validate_ledger.py')
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


def prior_errors(doc, path):
    context = validator.Ctx(set())
    validator.check_prior_art(str(tree / path), doc['idea'], context)
    return context.errors


def provenance_failures(entry):
    """Independent contract guard derived from R1 and pinned card identity."""
    failures = []
    if entry.get('provenance') != 'retrieved':
        failures.append('direct Git reading requires retrieved provenance in this packet')
    binding = entry.get('verified_by')
    if not isinstance(binding, dict):
        return failures + ['verified_by mapping missing']
    card_path = 'knowledge/frontiers/ecdlp/index-calculus/' + entry['ref'] + '.yaml'
    checks = {
        'agent': 'Codex coordinator /root; T-782 / TASK-20261029-8b1359',
        'read_on': '2026-10-29',
        'source_path': card_path,
        'source_commit': BASE,
        'source_sha256': records[card_path]['sha256'],
    }
    for key, expected in checks.items():
        if binding.get(key) != expected:
            failures.append(key + ' mismatch')
    if binding.get('method') != 'Direct reading of the pinned repository card through Git; no retrieval-index resolution asserted.':
        failures.append('method is not bounded to the documented direct Git reading')
    if binding.get('scope') != 'Repository-card attribution and comparison only; no new full-text literature verification or independent verification of the card findings.':
        failures.append('scope omits or changes card-only verification limitations')
    return failures


results, controls = [], []
for item in manifest['records']:
    old_item = old_items[item['id']]
    old_raw = packet(old_item['candidate'], PREVIOUS)
    new_raw = packet(item['candidate'])
    assert sha(old_raw) == item['previous_candidate_sha256'] == old_item['candidate_sha256']
    assert item['previous_candidate'] == old_item['candidate']
    assert sha(new_raw) == item['candidate_sha256'] == item['proposed_registry_entry']['superseding_sha256']
    for key in ('original_path', 'original_sha256', 'effective_path', 'effective_sha256',
                'prior_registry_entry', 'proposed_destination'):
        assert item[key] == old_item[key]
    old_route, new_route = copy.deepcopy(old_item['proposed_registry_entry']), copy.deepcopy(item['proposed_registry_entry'])
    old_route.pop('superseding_sha256'); new_route.pop('superseding_sha256')
    assert old_route == new_route
    old, new = parse(old_raw), parse(new_raw)
    changes = diff(old, new)
    if item['id'].endswith('43f871'):
        assert old_raw == new_raw and changes == []
    else:
        expected_paths = [('idea', 'prior_art', 'nearest', 0, 'provenance'),
                          ('idea', 'prior_art', 'nearest', 0, 'verified_by')]
        assert [tuple(x['path']) for x in changes] == expected_paths, changes
        entry = new['idea']['prior_art']['nearest'][0]
        assert not provenance_failures(entry)
        assert changes[0]['old'] == 'kb' and changes[0]['new'] == 'retrieved'
        for mutation in ('kb', 'missing_verified_by', 'wrong_hash', 'wrong_path', 'backdated_read', 'wrong_agent', 'overclaimed_scope'):
            bad = copy.deepcopy(entry)
            if mutation == 'kb':
                bad['provenance'] = 'kb'
            elif mutation == 'missing_verified_by':
                bad.pop('verified_by')
            elif mutation == 'wrong_hash':
                bad['verified_by']['source_sha256'] = '0' * 64
            elif mutation == 'wrong_path':
                bad['verified_by']['source_path'] = 'knowledge/frontiers/ecdlp/index-calculus/KR-IC-f5c584.yaml'
            elif mutation == 'backdated_read':
                bad['verified_by']['read_on'] = '2026-10-03'
            elif mutation == 'wrong_agent':
                bad['verified_by']['agent'] = 'CONTROL unrecorded reader'
            else:
                bad['verified_by']['scope'] = 'CONTROL independently verified full-text theorem and empirical findings.'
            found = provenance_failures(bad)
            assert found
            controls.append({'id': item['id'], 'mutation': mutation, 'detected_by': 'independent provenance contract guard',
                             'failures': found, 'passed': True})
    source = parse(records[item['effective_path']]['text'])
    full_differences = diff(source, new)
    assert all(x['path'][:2] == ['idea', 'prior_art'] for x in full_differences)
    before, after = prior_errors(source, item['original_path']), prior_errors(new, item['original_path'])
    assert len(before) == 1 and not after
    results.append({'id': item['id'], 'changes_from_v2': changes,
                    'only_r1_changes': True, 'non_prior_art_fields_preserved_against_effective_source': True,
                    'before_errors': before, 'after_errors': after})

result = {'joint':'J1','snapshot':SNAPSHOT,'source_commit':BASE,'previous_snapshot':PREVIOUS,
          'verdict':'holds_for_v3_r1_closure','sealed_original_hashes':sealed_expected,
          'candidate_results':results,'controls':controls,'sources_read':list(reads.values()),
          'reused_read_only_reviewer_sources':[str(tree / x) for x in ('tools/validate_ledger.py','tools/build_frontier_map.py','orchestration/fast_yaml.py')],
          'prior_art_errors_before':4,'prior_art_errors_after':0,
          'v3_handoff_binding_count':len(handoff['bindings']),'v2_handoff_bindings_still_unchanged':len(old_handoff['source_bindings']),
          'all_22_source_records_and_registry_unchanged':True,
          'provenance_controls_count':len(controls),'producer_checker_executed':False,
          'scope':'Narrow successor diff and R1 closure. All original review limitations remain.'}
(OUT / 'output.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:result[k] for k in ('joint','verdict','prior_art_errors_before','prior_art_errors_after','provenance_controls_count')},indent=2))
print('All original sealed review hashes preserved; all V3 and retained V2 source bindings pass.')
