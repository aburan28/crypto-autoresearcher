#!/usr/bin/env python3
"""Seal only this review's own files after checking the isolated input hash."""
from pathlib import Path
import datetime
import hashlib
import json

root = Path(__file__).resolve().parent
statement = Path('/var/tmp/binstd-round2-blind-20261027/statement.json')
statement_hash = hashlib.sha256(statement.read_bytes()).hexdigest()
assert statement_hash == '2bbf336b088ff099546bcc3b5f3612f439ba2b7aa69a5007c6d02fcdb590f664'
artifacts = ['check_exact.py', 'raw_output.txt', 'results.json', 'runtime.json',
             'report.md', 'commands.md', 'seal_review.py']
hashes = {name: hashlib.sha256((root/name).read_bytes()).hexdigest()
          for name in artifacts}
results = json.loads((root/'results.json').read_text())
assert results['all_required_exact_checks_passed']
raw = (root/'raw_output.txt').read_text()
assert raw.count('EXPECTED ASSERTION FAILURE') == 3
assert 'DEGREE16_PRODUCT 0x1ffff' in raw
assert 'ALL_REQUIRED_EXACT_CHECKS_PASSED True' in raw
sealed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
lines = [
    'schema: blind_review_attestation/v1',
    'task_id: TASK-20261027-b17d02',
    'conductor_card: T-617',
    'reviewer_role: independent_blind_adversarial_reviewer',
    'joints_owned: [J2-blind-factor-and-frobenius]',
    'verdict: holds',
    'joints:',
    '  - joint_id: J2-blind-factor-and-frobenius',
    '    verdict: holds',
    '    scope: Exact supplied factorization, degree-eight irreducibility, canonical Frobenius order and minimal polynomial, and required false controls.',
    '    evidence: [report.md, check_exact.py, raw_output.txt, results.json]',
    '    implementation_bridge_verified: false',
    '    limitation: Actual producer theorem fidelity and archived runner representation were not inspected.',
    'read_sibling_reports: false',
    'blind_from_respected: true',
    'first_filesystem_read: ' + json.dumps(str(statement)),
    'statement_sha256: ' + statement_hash,
    'sealed_at_utc: ' + json.dumps(sealed_at),
    'post_seal_producer_read: false',
    'blindness_maintained_through_final_delivery: true',
    'producer_source_reads: []',
    'prior_review_reads: []',
    'repository_instruction_reads: []',
    'memory_reads: []',
    'search_result_reads: []',
    'sources_read:',
    '  - path: ' + json.dumps(str(statement)),
    '    role: only_external_mathematical_source',
    '    sha256: ' + statement_hash,
]
for name in artifacts:
    lines.extend(['  - path: ' + json.dumps(str(root/name)),
                  '    role: own_review_artifact',
                  '    sha256: ' + hashes[name]])
lines.extend([
    '  - path: ' + json.dumps(str(root/'review_attestation.yaml')),
    '    role: own_attestation_read_after_creation_only_to_compute_final_seal',
    'non_file_context_read:',
    '  - Parent assignment containing the mathematical scope and blind restrictions.',
    '  - Coordinator message providing the absolute conductor executable path.',
    '  - Coordinator message reminding the reviewer of the lease and blind boundary.',
    '  - Direct shell, conductor, clock, and apply_patch tool outputs from this reviewer.',
    'runtime_source_boundary: Standard Python library and shell runtime machinery are execution dependencies, not external research sources.',
    'method:',
    '  factor_irreducibility: Exhaust all monic divisors of degrees one through four, thirty per factor.',
    '  canonical_frobenius: Abstract characteristic-two field argument using cardinality, Lagrange theorem, and polynomial root bound.',
    '  archived_quotient: Exhaust all 510 monic divisors of degrees one through eight, then exact matrix powers and Gaussian elimination.',
    'controls:',
    '  reducible_X8_plus_1: rejected_as_expected',
    '  GF2_order_17: rejected_as_expected',
    '  GF2_minpoly_X17_plus_1: rejected_as_expected',
    '  expected_false_assertion_failures: 3',
    '  unexpected_arithmetic_failures: 0',
    'operational_failures:',
    '  - Bare conductor command was absent from the non-login PATH; absolute-path claim succeeded.',
    'actions:',
    '  experiment_launched: false',
    '  heavy_lean_build: false',
    '  git_or_pr_action: false',
    '  scientific_status_changed: false',
    '  writes_confined_to_assigned_directory: true',
    '  conductor_claim_and_release: explicitly_authorized_control_plane_actions',
    'artifact_sha256:',
])
for name in artifacts:
    lines.append('  ' + json.dumps(name) + ': ' + hashes[name])
(root/'review_attestation.yaml').write_text('\n'.join(lines) + '\n')
sealed_files = artifacts + ['review_attestation.yaml']
seal = '\n'.join(hashlib.sha256((root/name).read_bytes()).hexdigest() + '  ' + name
                 for name in sealed_files) + '\n'
(root/'seal.sha256').write_text(seal)
print('SEALED_AT_UTC', sealed_at)
print('STATEMENT_SHA256', statement_hash)
print(seal, end='')
print('BLIND_REVIEW_SEALED True')
