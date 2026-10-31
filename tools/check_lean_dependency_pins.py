#!/usr/bin/env python3
"""Record actual installed Lean dependency revisions and reject dirty sources.

This checks Git source custody, not the correctness of cached dependency binaries
or an independent kernel recheck. It never downloads or modifies dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def git(directory: Path, *args: str) -> str:
    return subprocess.check_output(
        ['git', '-C', str(directory), *args], text=True,
        stderr=subprocess.PIPE).strip()


def audit(workspace: Path) -> dict:
    workspace = workspace.resolve()
    manifest_path = workspace / 'lake-manifest.json'
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    packages = manifest.get('packages')
    if not isinstance(packages, list) or not packages:
        raise ValueError('manifest must enumerate nonempty pinned dependencies')
    package_root = (workspace / manifest.get('packagesDir', '.lake/packages')).resolve()
    if not package_root.is_relative_to(workspace):
        raise ValueError('dependency directory escapes workspace')
    names = set()
    records = []
    for entry in packages:
        name, revision = entry.get('name'), entry.get('rev')
        if (entry.get('type') != 'git' or not isinstance(name, str)
                or re.fullmatch(r'[A-Za-z0-9_-]+', name) is None
                or not isinstance(revision, str)
                or re.fullmatch(r'[0-9a-f]{40}', revision) is None
                or name in names):
            raise ValueError('dependency requires unique name and exact Git revision')
        names.add(name)
        installed = (package_root / name).resolve()
        if not installed.is_relative_to(package_root) or not installed.is_dir():
            raise ValueError(f'{name}: missing or escaping installed dependency')
        top = Path(git(installed, 'rev-parse', '--show-toplevel')).resolve()
        if top != installed:
            raise ValueError(f'{name}: not an independent dependency Git checkout')
        head = git(installed, 'rev-parse', 'HEAD')
        changes = git(installed, 'status', '--porcelain', '--untracked-files=all')
        records.append({'name': name, 'expected_revision': revision,
                        'installed_revision': head, 'clean_sources': not changes})
        if head != revision or changes:
            raise ValueError(f'{name}: installed revision mismatch or dirty/untracked sources')
    return {'schema': 'lean-dependency-pins/v1', 'passed': True,
            'manifest_sha256': hashlib.sha256(raw).hexdigest(),
            'dependencies': records,
            'binary_or_independent_kernel_recheck': False,
            'trust_limit': 'Git source custody only; ignored build outputs retain Lean/Lake binary trust.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--artifact-out', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = audit(args.workspace)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        result = {'schema': 'lean-dependency-pins/v1', 'passed': False,
                  'error': str(exc), 'binary_or_independent_kernel_recheck': False}
    result['github_run_id'] = os.environ.get('GITHUB_RUN_ID')
    result['github_checkout_sha'] = os.environ.get('GITHUB_SHA')
    result['checker_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.artifact_out.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
