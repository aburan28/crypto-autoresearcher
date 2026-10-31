#!/usr/bin/env python3
"""Check one hosted formal receipt bundle against an exact Git source inventory.

This checks receipt fields and source bytes, not theorem meaning or run execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], stderr=subprocess.DEVNULL)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob(rev: str, path: str) -> bytes:
    return git('show', f'{rev}:{path}')


def generated_root(rev: str) -> bytes:
    paths = [p.decode() for p in git('ls-tree', '-r', '-z', '--name-only', rev,
                                     'formal/CryptoResearch').split(b'\0') if p]
    modules = sorted('CryptoResearch.' + p[len('formal/CryptoResearch/'):-5].replace('/', '.')
                     for p in paths if p.endswith('.lean'))
    header = ('/-\nGENERATED FILE -- do not edit, and do not commit.\n\n'
              'Rebuild with `python3 tools/rebuild_formal_root.py`.  It lists every module\n'
              'under CryptoResearch/ so that `lake build` compiles them and AxiomAudit.lean can\n'
              'see their theorems.\n-/\n')
    return (header + '\n' + ''.join(f'import {m}\n' for m in modules)).encode()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inventory', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--source-commit', required=True)
    ap.add_argument('--base', required=True)
    ap.add_argument('--head', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    for rev in (args.source_commit, args.base, args.head):
        if not re.fullmatch('[0-9a-f]{40}', rev):
            ap.error('commit arguments must be full SHA-1 IDs')
    inventory = json.loads(args.inventory.read_text())
    rows = inventory['rows']
    issues: list[str] = []
    parents = git('rev-list', '--parents', '-n', '1', args.source_commit).decode().strip().split()
    if parents != [args.source_commit, args.base, args.head]:
        issues.append('CI test merge is not exact base/head merge')
    expected = {PurePosixPath(r['target']).stem + '.json': r for r in rows}
    actual = {p.name: p for p in args.receipts.glob('*.json')}
    if set(expected) != set(actual):
        issues.append(f'receipt names differ: missing={sorted(set(expected)-set(actual))}, extra={sorted(set(actual)-set(expected))}')
    blob_cache: dict[str, str] = {}
    receipt_rows = []
    workspace_groups: dict[str, dict[str, str]] = {}
    verifier_inputs: dict[str, str] | None = None
    for filename, row in expected.items():
        if filename not in actual:
            continue
        raw = actual[filename].read_bytes()
        receipt = json.loads(raw)
        task, proof, provenance = receipt['task'], receipt['verification'], receipt['provenance']
        checks = {
            'receipt_schema': receipt['schema'] == 'crypto.autoresearch.formal_verification.v1',
            'source_commit': provenance['source_commit'] == args.source_commit,
            'task_spec_hash': provenance['task_spec_sha256'] == row['target_sha256'],
            'theorem_module_hash': provenance['theorem_sha256'] == row['module_sha256'],
            'module_path': f"{task['workspace']}/{task['theorem_file']}" == row['module'],
            'theorem_name': task['theorem_name'] == row['theorem_name'] == proof['theorem_name'],
            'claim_id': task['claim_id'] == row['claim_id'],
            'task_id': task['task_id'] == proof['task_id'],
            'theorem_file': task['theorem_file'] == proof['theorem_file'],
            'toolchain_hash': provenance['lean_toolchain_sha256'] == provenance['workspace_inputs'].get('lean-toolchain'),
            'lake_manifest_hash': provenance['lake_manifest_sha256'] == provenance['workspace_inputs'].get('lake-manifest.json'),
            'machine_verified': proof['status'] == 'machine_verified',
            'build_passed': proof['build_passed'] is True,
            'axiom_audit_passed': proof['axiom_audit_passed'] is True,
            'no_forbidden_constructs': proof['forbidden_constructs'] == [],
        }
        for name, good in checks.items():
            if not good:
                issues.append(f'{filename}: {name}')
        if row['source'] not in blob_cache:
            blob_cache[row['source']] = digest(git_blob(args.source_commit, row['source']))
        if blob_cache[row['source']] != row['source_sha256']:
            issues.append(f'{filename}: source hash differs in CI test merge')
        workspace = task['workspace']
        inputs = provenance['workspace_inputs']
        if workspace in workspace_groups and workspace_groups[workspace] != inputs:
            issues.append(f'{filename}: inconsistent {workspace} workspace hash map')
        workspace_groups[workspace] = inputs
        if verifier_inputs is not None and verifier_inputs != provenance['verifier_inputs']:
            issues.append(f'{filename}: inconsistent verifier input hash map')
        verifier_inputs = provenance['verifier_inputs']
        receipt_rows.append({'target': row['target'], 'receipt': filename,
                             'receipt_sha256': digest(raw), 'claim_id': row['claim_id'],
                             'checks': checks,
                             'semantic_review_status_in_receipt': receipt['semantic_review']['status']})
    workspace_checked = 0
    generated_checked = 0
    for workspace, inputs in workspace_groups.items():
        for name, want in inputs.items():
            if workspace == 'formal' and name == 'CryptoResearch.lean':
                got = digest(generated_root(args.source_commit))
                generated_checked += 1
            else:
                got = digest(git_blob(args.source_commit, f'{workspace}/{name}'))
                workspace_checked += 1
            if got != want:
                issues.append(f'{workspace}/{name}: workspace input hash mismatch')
    for name, want in (verifier_inputs or {}).items():
        if digest(git_blob(args.source_commit, name)) != want:
            issues.append(f'{name}: verifier input hash mismatch')
    output = {
        'schema': 'crypto.validation.hosted-formal-receipt-audit/v1',
        'inventory_revision': inventory['revision'],
        'source_commit': args.source_commit,
        'base': args.base, 'head': args.head,
        'statistics': {'targets': len(rows), 'receipts': len(receipt_rows),
                       'declared_sources_checked': len(blob_cache),
                       'tracked_workspace_inputs_checked': workspace_checked,
                       'generated_workspace_roots_checked': generated_checked,
                       'verifier_inputs_checked': len(verifier_inputs or {}),
                       'machine_verified': sum(x['checks']['machine_verified'] for x in receipt_rows),
                       'axiom_audit_passed': sum(x['checks']['axiom_audit_passed'] for x in receipt_rows),
                       'semantic_pending_in_receipts': sum(x['semantic_review_status_in_receipt'] == 'pending' for x in receipt_rows),
                       'issue_count': len(issues)},
        'issues': issues, 'rows': receipt_rows,
        'scope': 'Exact Git source and hosted receipt consistency; theorem fidelity and historical execution remain separate.'
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps(output['statistics'], sort_keys=True))
    return 0 if not issues else 1


if __name__ == '__main__':
    raise SystemExit(main())
