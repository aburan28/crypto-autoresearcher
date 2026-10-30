#!/usr/bin/env python3
"""T-794 bounded archival mapping checks; no native or scientific execution."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
COMMIT = 'd316dffae04f9b50131c31d50a005cf7daca1061'
ARCHIVE = 'e3fe39bed74e607855a3f6fa238ab5144b2bf232'
NATIVE = '8ef2a271eb45801d12b431e85165b378d3f5176b'
PREFIX = 'research/historical-claim-evidence-binstd-20261029/'
SEED = 'research/historical-claim-evidence-20261029/matrix.json'
REPOS = {
    'auto': '/home/ec2-user/crypto-autoresearcher-historical-binstd-20261029',
    'cryptanalysis': '/home/ec2-user/cryptanalysis-known-label-native-types-20261029',
    'crypto': '/home/ec2-user/crypto',
}
ENV = {**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_NO_REPLACE_OBJECTS': '1',
       'GIT_ALLOW_PROTOCOL': '', 'GIT_TERMINAL_PROMPT': '0'}
READS = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.run(['git', '--literal-pathspecs', '-C', REPOS[repo], *args],
                          env=ENV, check=True, capture_output=True, timeout=20).stdout


def read(repo, commit, path, purpose):
    data = git(repo, 'show', f'{commit}:{path}')
    assert len(data) <= 16 * 1024 * 1024
    READS.append(dict(repo=repo, commit=commit, path=path, sha256=sha(data),
                      bytes=len(data), purpose=purpose))
    return data


def write_json(name, data):
    with (OUT / name).open('x') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


matrix_bytes = read('auto', COMMIT, PREFIX + 'matrix.json', 'primary mapping')
matrix = json.loads(matrix_bytes)
seed_bytes = read('auto', COMMIT, SEED, 'unchanged seed comparison')
seed = json.loads(seed_bytes)
archive_seed = read('auto', ARCHIVE, SEED, 'builder exact seed comparison')
assert seed_bytes == archive_seed
assert len(seed['claims']) == 6
assert matrix['claims'][:6] == seed['claims']
assert matrix['sources'][:len(seed['sources'])] == seed['sources']
assert len(matrix['claims']) == 8

blobs = {}
source_results = []
for source in matrix['sources']:
    if source['kind'] == 'unavailable':
        source_results.append(dict(id=source['id'], unavailable=True, reason=source['reason']))
        continue
    data = read(source['repo'], source['commit'], source['path'], 'source bytes and digest')
    oid = git(source['repo'], 'rev-parse', f"{source['commit']}:{source['path']}").decode().strip()
    assert oid == source['blob_oid']
    assert sha(data) == source['sha256']
    blobs[source['id']] = data
    source_results.append(dict(id=source['id'], bytes=len(data), blob_oid=oid,
                               sha256=sha(data), binding_passed=True))
assert sum(map(len, blobs.values())) == 602399
assert len(blobs) == 32
for claim in matrix['claims']:
    ex = claim['excerpt']
    lines = blobs[claim['source_id']].decode().splitlines(keepends=True)
    excerpt = ''.join(lines[ex['start_line']-1:ex['end_line']])
    assert excerpt == ex['text'] and sha(excerpt.encode()) == ex['sha256']

# Invoke the exact immutable checker without materializing/importing worktree code.
checker_bytes = read('auto', COMMIT, 'tools/claim_evidence_matrix.py', 'checker source and execution')
namespace = {'__name__': 't794_bound_checker'}
exec(compile(checker_bytes, COMMIT + ':tools/claim_evidence_matrix.py', 'exec'), namespace)
positive = namespace['check'](matrix, REPOS)
positive['matrix_sha256'] = sha(matrix_bytes)
retained = json.loads(read('auto', COMMIT, PREFIX+'integrity.json', 'retained result comparison'))
assert positive == retained

source_by_id = {s['id']: s for s in matrix['sources']}
bindings = json.loads(blobs['binstd-supplement-bindings'])
assert bindings['new_checkout'] == NATIVE
assert 'whole run was not green' in bindings['run_boundary']
assert bindings['hosted_run'] == 40636717165

NAMES = {
    'binstd/degree-eight-irreducibility': 'CryptoResearch.Binstd.factor8_irreducible_pair',
    'binstd/canonical-frobenius': 'CryptoResearch.Binstd.canonicalFrobenius_order_and_minpoly',
}


def check_native_mapping(claim):
    source = source_by_id[claim['source_id']]
    receipt_id, = claim['evidence']['native_build']
    receipt = json.loads(blobs[receipt_id])
    expected = NAMES[claim['id']]
    for section in ['task', 'verification']:
        assert receipt[section]['theorem_name'] == expected
        assert 'formal/' + receipt[section]['theorem_file'] == source['path']
    assert receipt['task']['task_id'] == receipt['verification']['task_id']
    assert receipt['provenance']['source_commit'] == source['commit'] == NATIVE
    assert receipt['provenance']['theorem_sha256'] == source['sha256']
    assert receipt['verification']['status'] == 'machine_verified'
    assert receipt['verification']['build_passed'] is True
    assert receipt['verification']['axiom_audit_passed'] is True
    assert receipt['verification']['forbidden_constructs'] == []
    assert receipt['verification']['blocking_reason'] is None
    assert receipt['infrastructure_failure'] is None
    assert receipt['provenance']['lean_toolchain_sha256'] == sha(blobs['binstd-native-toolchain'])
    assert receipt['provenance']['lake_manifest_sha256'] == sha(blobs['binstd-native-dependencies'])
    for sid in ['binstd-factor-definitions', 'binstd-degree-eight-irreducibility-source',
                'binstd-canonical-frobenius-source', 'binstd-native-toolchain',
                'binstd-native-dependencies', 'binstd-native-lakefile']:
        s = source_by_id[sid]
        assert receipt['provenance']['workspace_inputs'][s['path'][len('formal/'):]] == s['sha256']
    types_id, = claim['evidence']['elaborated_types']
    assert receipt['audit_log'].encode() == blobs[types_id]
    assert expected + ' :' in receipt['audit_log']
    assert "depends on axioms: [propext, Classical.choice, Quot.sound]" in receipt['audit_log']
    bound_receipt, = [r for r in bindings['receipts']
                     if r['new_receipt'] == source_by_id[receipt_id]['path']]
    assert bound_receipt['new_sha256'] == sha(blobs[receipt_id])
    assert 'supplemental overall run failed' in ' '.join(claim['assumptions'])
    assert 'original control job failed during setup' in ' '.join(claim['assumptions'])
    return dict(claim_id=claim['id'], declaration=expected, source_commit=NATIVE,
                source_sha256=source['sha256'], receipt_sha256=sha(blobs[receipt_id]),
                types_sha256=sha(blobs[types_id]), receipt_type_bytes_equal=True,
                listed_workspace_entries_matched=6,
                receipt_workspace_entries=len(receipt['provenance']['workspace_inputs']),
                receipt_verifier_entries=len(receipt['provenance']['verifier_inputs']),
                native_rerun=False)


native_results = [check_native_mapping(c) for c in matrix['claims'][6:]]
receipts = [json.loads(blobs[c['evidence']['native_build'][0]]) for c in matrix['claims'][6:]]
assert receipts[0]['provenance']['workspace_inputs'] == receipts[1]['provenance']['workspace_inputs']
assert receipts[0]['provenance']['verifier_inputs'] == receipts[1]['provenance']['verifier_inputs']
repair = json.loads(blobs['binstd-kernel-controls'])
assert repair['run_id'] == 40719320437 and repair['lean_version'] == '4.22.0'
assert repair['executed_tests'] == 323 and repair['test_failures'] == 0
worker, = [s for s in repair['source_comparison'] if s['path'] == 'orchestration/formal/lean_worker.py']
assert worker['supplement_sha256'] == worker['repair_sha256'] == receipts[0]['provenance']['verifier_inputs'][worker['path']]
assert 'does not rewrite' in ' '.join(repair['limits'])

# Controls use already bound bytes; they do not discover or read extra source paths.
original_reader = namespace['read_source']


def cached_reader(source, repositories, remaining):
    data = blobs[source['id']]
    namespace['require'](sha(data) == source['sha256'], 'source SHA-256 mismatch')
    return data


namespace['read_source'] = cached_reader
controls = []
for name, mutate in [
    ('changed_excerpt', lambda m: m['claims'][-1]['excerpt'].__setitem__('text', 'wrong theorem\n')),
    ('changed_source_digest', lambda m: m['sources'][-1].__setitem__('sha256', '0'*64)),
    ('complete_coverage_overclaim', lambda m: m['scope'].__setitem__('coverage', 'complete')),
]:
    changed = copy.deepcopy(matrix)
    mutate(changed)
    try:
        namespace['check'](changed, REPOS)
    except namespace['MatrixError'] as exc:
        controls.append(dict(name=name, expected='reject', outcome='rejected', reason=str(exc)))
    else:
        raise AssertionError('control unexpectedly accepted: ' + name)

swapped = copy.deepcopy(matrix)
swapped['claims'][-1]['evidence']['native_build'] = matrix['claims'][-2]['evidence']['native_build']
namespace['check'](swapped, REPOS)
try:
    check_native_mapping(swapped['claims'][-1])
except AssertionError:
    controls.append(dict(name='wrong_named_receipt_role', integrity_checker='accepted as documented',
                         independent_mapping_check='rejected',
                         meaning='Byte presence does not validate semantic evidence-role assignment.'))
else:
    raise AssertionError('swapped receipt escaped independent identity check')

changed_statement = copy.deepcopy(matrix)
changed_statement['claims'][-1]['statement'] = 'All historical BINSTD execution and timing are verified.'
namespace['check'](changed_statement, REPOS)
controls.append(dict(name='unjustified_statement_overclaim', integrity_checker='accepted as documented',
                     reviewer_disposition='rejected by source/type/scope comparison',
                     meaning='Scientific statement truth is expressly outside this integrity checker.'))

result = dict(schema='t794.independent_mapping_checks/v1', reviewed_commit=COMMIT,
              matrix_sha256=sha(matrix_bytes), seed_sha256=sha(seed_bytes),
              old_six_claims_unchanged=True, old_source_records_unchanged=True,
              old_source_records=len(seed['sources']), seed_at_archive_byte_identical=True,
              all_eight_excerpts_match=True, source_results=source_results,
              native_bindings=native_results, controls=controls,
              retained_integrity_result_reproduced=True,
              native_builds=0, experiment_runs=0, network_requests=0,
              claims_coverage='partial', individual_claim_denominator=None,
              complete_workspace_reverification=False,
              limitation='Only six listed workspace entries are independently compared; other entries and hosted execution retain archived review trust.')
write_json('checks.json', result)
write_json('sources-read.json', READS)
print(json.dumps({k: result[k] for k in ['matrix_sha256','old_six_claims_unchanged',
    'old_source_records_unchanged','old_source_records','all_eight_excerpts_match',
    'retained_integrity_result_reproduced','native_builds','experiment_runs','network_requests']}, indent=2))
print(json.dumps(controls, indent=2))
