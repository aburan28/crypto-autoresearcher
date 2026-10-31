#!/usr/bin/env python3
"""J2 independently authored byte/provenance checks, no Lean/Rust execution."""
import difflib
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = '/home/ec2-user/crypto-autoresearcher-stark-affine-20261029'
CRYPTO = '/home/ec2-user/crypto'
REV = 'd4f1279102709518247f5a7d1926de354fe5929a'
OLD = '9f5302e3ea60f04d5fa5ca55a3313eb1834c9bf6'
BASE = 'research/stark-affine-proof-20261029/'
NATIVE = BASE + 'native-40818135384/'
MODULE = 'formal/CryptoResearch/Stark/AffineTransition.lean'
OUT = Path(__file__).parent
reads = []

def read(path, rev=REV, repo=REPO):
    data = subprocess.check_output(['git', '-C', repo, 'show', f'{rev}:{path}'])
    record = {'repository': repo, 'revision': rev, 'path': path,
              'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    if record not in reads:
        reads.append(record)
    return data

def sha(data):
    return hashlib.sha256(data).hexdigest()

handoff = json.loads(read(BASE + 'J2-handoff.json'))
checks = {}
for path, expected in handoff['bindings'].items():
    actual = sha(read(path))
    checks['handoff:' + path] = {'expected': expected, 'actual': actual, 'pass': actual == expected}

old = read(MODULE, OLD)
current = read(MODULE)
insertion = b'''\n-- Native negative control: this application would prove False in the zero ring
-- if the multiplication obstruction did not require Nontrivial R.
-- #check_failure itself fails elaboration if the term is accepted.
#check_failure
  (multiplication_not_affine (R := ZMod 1) 0 0 0
    (fun x y => zero_ring_product_control x y) : False)
\n'''
changes = [op for op in difflib.SequenceMatcher(None, old.splitlines(keepends=True), current.splitlines(keepends=True)).get_opcodes() if op[0] != 'equal']
checks['source_delta'] = {'old_sha256': sha(old), 'current_sha256': sha(current),
    'insertion_sha256': sha(insertion), 'insertion_bytes': len(insertion),
    'changed_opcodes': changes, 'pass': current.count(insertion) == 1 and current.replace(insertion, b'', 1) == old}
receipt = json.loads(read(NATIVE + 'stark-affine-probes.json'))
binding = json.loads(read(NATIVE + 'binding.json'))
types = read(NATIVE + 'types-and-axioms.txt').decode()
prov = receipt['provenance']
checks['native_old_source'] = {'pass': sha(old) == prov['theorem_sha256'] == prov['workspace_inputs'][MODULE.removeprefix('formal/')] == binding['module_sha256_checked_against_old_head']}
checks['native_excerpt'] = {'occurrences_in_build_log': receipt['build_log'].count(types), 'pass': types in receipt['build_log']}
checks['native_receipt_hash'] = {'pass': sha(read(NATIVE + 'stark-affine-probes.json')) == binding['receipt_sha256']}
for path, field in [('formal/lean-toolchain', 'lean_toolchain_sha256'), ('formal/lake-manifest.json', 'lake_manifest_sha256'), ('formal/targets/stark-affine-probes.yaml', 'task_spec_sha256')]:
    checks['native:' + path] = {'pass': sha(read(path)) == prov[field]}
checks['native:formal/lakefile.toml'] = {'pass': sha(read('formal/lakefile.toml')) == prov['workspace_inputs']['lakefile.toml']}
names = ['recover_coefficients','coefficients_eq_of_probes','three_probe_extensionality','multiplication_not_affine','two_probes_insufficient','zero_ring_product_control']
type_summaries = []
for name in names:
    type_lines = [line for line in types.splitlines() if re.search(r': @?' + name + r'(?:\.\{| :).* :|: @?' + name + r' :', line)]
    axiom_lines = [line for line in types.splitlines() if "AffineTransition." + name + "' depends on axioms:" in line]
    type_summaries.append({'declaration': name, 'type_header': type_lines, 'axiom_output': axiom_lines})
    checks['type_and_axioms:' + name] = {'pass': len(type_lines) == 1 and len(axiom_lines) == 1}
checks['historical_control_absent'] = {'pass': b'#check_failure' not in old and '#check_failure' not in receipt['build_log']}
run = json.loads(read(NATIVE + 'run.json'))
jobs = json.loads(read(NATIVE + 'jobs.json'))
artifacts = json.loads(read(NATIVE + 'artifacts.json'))
synthetic = json.loads(read(NATIVE + 'synthetic-commit.json'))
job = next(j for j in jobs['jobs'] if j['id'] == binding['job_id'])
artifact = next(a for a in artifacts['artifacts'] if a['id'] == binding['artifact_id'])
checks['native_identity_metadata'] = {'pass':
    run['id'] == job['run_id'] == artifact['workflow_run']['id'] == binding['run_id']
    and run['run_attempt'] == job['run_attempt'] == binding['attempt'] == 1
    and run['head_sha'] == job['head_sha'] == artifact['workflow_run']['head_sha'] == binding['pr_head'] == OLD
    and prov['source_commit'] == binding['synthetic_merge'] == synthetic['sha']
    and OLD in [p['sha'] for p in synthetic['parents']]
    and run['conclusion'] == job['conclusion'] == 'success'
    and artifact['digest'] == 'sha256:' + binding['artifact_zip_sha256']}
inputs = json.loads(read(BASE + 'inputs.json'))
rust_meta = inputs['crypto_source']
rust = read(rust_meta['path'], rust_meta['commit'], CRYPTO)
blob = subprocess.check_output(['git', '-C', CRYPTO, 'rev-parse', f"{rust_meta['commit']}:{rust_meta['path']}"]).decode().strip()
checks['rust_full_source'] = {'git_blob': blob, 'sha256': sha(rust), 'pass': blob == rust_meta['blob_oid'] and sha(rust) == rust_meta['sha256']}
rust_lines = rust.decode().splitlines(keepends=True)
expected_exhibit = ''.join(f"\n--- {rust_meta['path']} lines {start}-{end} at {rust_meta['commit']} ---\n" + ''.join(rust_lines[start-1:end]) for start,end in rust_meta['excerpt_ranges'])
exhibit = read(BASE + 'source-exhibit.txt').decode()
checks['rust_exhibit'] = {'pass': expected_exhibit == exhibit, 'actual_sha256': sha(exhibit.encode()), 'reconstructed_sha256': sha(expected_exhibit.encode())}
historical_manifest_comparisons = []
for path, expected in inputs['inputs'].items():
    if path in handoff['bindings'] or path == BASE + 'review-plan.json':
        actual = sha(read(path))
        historical_manifest_comparisons.append({'path': path, 'manifest_sha256': expected, 'snapshot_sha256': actual, 'matches': expected == actual})
result = {'schema': 'j2-independent-bindings/v1', 'reviewer_task': 'TASK-20261029-55585f',
    'producer_snapshot': REV, 'checks': checks, 'all_checked_bindings_pass': all(v['pass'] for v in checks.values()),
    'historical_inputs_manifest_comparisons': historical_manifest_comparisons,
    'type_headers_and_axiom_outputs': type_summaries,
    'native_control_current_machine_status': 'not_verified',
    'native_outcome_obtained_here': False,
    'limits': ['Byte checks do not authenticate execution.', 'No raw job log or zip was read; only their recorded metadata digests were cross-checked.', 'No Lean, Rust, verifier, experiment, dependency installation, or network request was run.', 'No new source native outcome is inferred.'],
    'sources_read_by_check': reads}
(OUT / 'binding-checks.json').write_text(json.dumps(result, indent=2) + '\n')
(OUT / 'source-insertion.txt').write_bytes(insertion)
print(json.dumps({'all_checked_bindings_pass':result['all_checked_bindings_pass'], 'failed_checks':[k for k,v in checks.items() if not v['pass']], 'historical_manifest_mismatches':[x for x in historical_manifest_comparisons if not x['matches']], 'source_delta':checks['source_delta'], 'type_headers_and_axiom_outputs':type_summaries}, indent=2))
raise SystemExit(0 if result['all_checked_bindings_pass'] else 1)
