"""Input binding and receipt consistency, never authentication of a Lean run.

Fresh kernel checks remain authoritative. These checks prevent accidentally
reusing inconsistent/stale receipts; someone able to fabricate the whole JSON
can fabricate its hashes and logs too. Dependency oleans remain in the usual
Lean/Lake trust boundary, bound by the checked toolchain and dependency pins.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import re


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def workspace_inputs(workspace: Path) -> dict[str, str]:
    """Bind all local Lean sources/configs, including imported helper files.

    Generated root modules are included after regeneration. Hidden dependency
    and build directories (.git/.lake) are excluded; their pins are local inputs. Symlinks
    outside those directories are rejected rather than silently omitted.
    """
    result = {}
    for directory, dirs, files in os.walk(workspace):
        dirs[:] = sorted(d for d in dirs if d not in {'.git', '.lake'})
        for name in dirs:
            if (Path(directory)/name).is_symlink():
                raise ValueError('verification requires regular local source directories')
        for name in sorted(files):
            if not (name.endswith('.lean') or name in {
                    'lakefile.toml', 'lean-toolchain', 'lake-manifest.json'}):
                continue
            path = Path(directory)/name
            if path.is_symlink():
                raise ValueError('verification requires regular local source files')
            result[path.relative_to(workspace).as_posix()] = sha256(path)
    return dict(sorted(result.items()))


def verifier_inputs() -> dict[str, str]:
    directory = Path(__file__).resolve().parent
    return {f'orchestration/formal/{p.name}': sha256(p)
            for p in sorted(directory.glob('*.py'))}


def archived_verifier_inputs(repo: Path, revision: str) -> dict[str, str]:
    """An explicitly selected archived verifier, never an implicit trust upgrade."""
    import subprocess
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('archived verifier requires an exact reviewed Git revision')
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', revision,
                                     'orchestration/formal'], cwd=repo, text=True).splitlines()
    return {p: hashlib.sha256(subprocess.check_output(['git', 'show', f'{revision}:{p}'], cwd=repo)).hexdigest()
            for p in paths if Path(p).parent.as_posix() == 'orchestration/formal' and p.endswith('.py')}


def receipt_errors(receipt: dict, *, repo: Path, spec: Path, task,
                   verifier_revision: str | None = None) -> list[str]:
    """Check identity, complete local inputs and consistent success fields."""
    if not isinstance(receipt, dict) or any(not isinstance(receipt.get(key), dict)
            for key in ('task', 'verification', 'provenance')):
        return ['malformed receipt or failed verification']
    errors = []
    expected_task = json.loads(json.dumps(asdict(task)))
    verification = receipt.get('verification') or {}
    provenance = receipt.get('provenance') or {}
    workspace = (repo/task.workspace).resolve()
    checks = {
        'schema': receipt.get('schema') == 'crypto.autoresearch.formal_verification.v1',
        'task identity': receipt.get('task') == expected_task,
        'infrastructure': receipt.get('infrastructure_failure') is None,
        'result schema': verification.get('schema') == 'crypto.autoresearch.formal_proof_result.v1',
        'result identity': all(verification.get(k) == expected_task[k]
                               for k in ('task_id', 'theorem_file', 'theorem_name')),
        'result status': verification.get('status') == 'machine_verified',
        'build': verification.get('build_passed') is True,
        'axiom audit': verification.get('axiom_audit_passed') is True,
        'forbidden constructs': verification.get('forbidden_constructs') == [],
        'blocking reason': verification.get('blocking_reason') is None,
        'build log': isinstance(receipt.get('build_log'), str) and bool(receipt['build_log'].strip()),
        'named audit log': any(line.strip() == f'target axiom audit passed: {task.theorem_name}'
                              for line in str(receipt.get('audit_log', '')).splitlines()),
        'negative audit diagnostics': not re.search(
            r'target axiom audit failed:|requested declaration is not a theorem:|zero-axiom audit failed:|^.*error(?:\([^\n)]*\))?:|^FAIL\b',
            str(receipt.get('audit_log', '')), re.MULTILINE),
        'nonempty project audit': bool(re.search(
            r'axiom audit: [1-9][0-9]* theorem\(s\), all standard axioms only|^zero-axiom audit passed: \S+',
            str(receipt.get('audit_log', '')), re.MULTILINE)),
        'spec hash': provenance.get('task_spec_sha256') == sha256(spec),
        'theorem hash': provenance.get('theorem_sha256') == sha256(workspace/task.theorem_file),
        'toolchain hash': provenance.get('lean_toolchain_sha256') == sha256(workspace/'lean-toolchain'),
        'manifest hash': provenance.get('lake_manifest_sha256') == sha256(workspace/'lake-manifest.json'),
        'local source inputs': provenance.get('workspace_inputs') == workspace_inputs(workspace),
        'verifier inputs': provenance.get('verifier_inputs') == (
            archived_verifier_inputs(repo, verifier_revision) if verifier_revision else verifier_inputs()),
    }
    if verifier_revision:
        checks['archived verifier revision'] = provenance.get('source_commit') == verifier_revision
    observed = re.search(r'version ([^, ]+)', str(provenance.get('lean_version', '')))
    checks['Lean version'] = bool(observed and observed.group(1) ==
        (workspace/'lean-toolchain').read_text().strip().split(':v')[-1])
    errors.extend(key for key, passed in checks.items() if not passed)
    return errors


def main(argv=None) -> int:
    import argparse
    from .targets import load_spec, task_from_spec
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path.cwd())
    parser.add_argument('--inventory', required=True, type=Path)
    parser.add_argument('--receipt-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--min-verified', type=int, default=65)
    parser.add_argument('--verifier-revision', help='Exact independently reviewed archived verifier revision; defaults to current verifier bytes. Does not claim old runs used current repairs.')
    args = parser.parse_args(argv)
    if args.min_verified < 1:
        parser.error('at least one checked declaration is required')
    if args.output.exists():
        parser.error('output already exists; preserve the previous summary')
    inventory = json.loads(args.inventory.read_text())
    receipts = [(p, json.loads(p.read_text())) for p in sorted(args.receipt_dir.glob('*.json'))]
    targets = []
    for entry in inventory['targets']:
        task = task_from_spec(load_spec(args.repo_root/entry['spec']))
        row = {'spec': entry['spec'], 'theorem': task.theorem_name,
               'semantic_review': 'pending'}
        if not (args.repo_root/task.workspace/task.theorem_file).is_file():
            row['status'] = 'undischarged'
        else:
            candidates = [(p, data) for p, data in receipts
                          if data.get('task', {}).get('theorem_name') == task.theorem_name]
            attempts = [{'receipt': str(p), 'errors': receipt_errors(data, repo=args.repo_root,
                         spec=args.repo_root/entry['spec'], task=task,
                         verifier_revision=args.verifier_revision)} for p, data in candidates]
            accepted = next((a for a in reversed(attempts) if not a['errors']), None)
            row.update(status='machine_verified' if accepted else 'not_verified_for_current_inputs',
                       receipt=accepted['receipt'] if accepted else None, attempts=attempts)
        targets.append(row)
    counts = {'targets': len(targets),
              'machine_verified': sum(t['status'] == 'machine_verified' for t in targets),
              'undischarged': sum(t['status'] == 'undischarged' for t in targets),
              'failed_current_inputs': sum(t['status'] == 'not_verified_for_current_inputs' for t in targets)}
    result = {'schema': 'lean-retrospective.verification-summary.v2',
              'scope': 'Receipt consistency for exact named declarations and local inputs; not run authentication or semantic fidelity. Fresh Lean verification and independent review are required.',
              'verifier_revision': args.verifier_revision or 'current_verifier_bytes',
              'baseline': inventory['revision'], 'counts': counts, 'targets': targets}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as handle:
        json.dump(result, handle, indent=2); handle.write('\n')
    print(json.dumps(counts))
    return int(bool(counts['failed_current_inputs'] or counts['machine_verified'] < args.min_verified))


if __name__ == '__main__':
    raise SystemExit(main())
