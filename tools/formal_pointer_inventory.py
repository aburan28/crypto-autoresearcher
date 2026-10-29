#!/usr/bin/env python3
"""Inventory explicit EXP-ID mentions in registered formal target inputs.

This is a syntactic pointer inventory. It cannot establish theorem fidelity,
machine verification, execution validity, or the absence of a relevant theorem.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import json
import re
import subprocess

EXP_RE = re.compile(r'(?<![A-Za-z0-9_-])EXP-(?:[A-Za-z0-9]+-)+[A-Za-z0-9]+(?![A-Za-z0-9_-])')
TEXT_EXT = {'.md', '.txt', '.yaml', '.yml', '.json', '.lean'}
MAX_SOURCE_BYTES = 1_000_000


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=repo)


class Blobs:
    def __init__(self, repo: Path):
        self.process = subprocess.Popen(
            ['git', 'cat-file', '--batch'], cwd=repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def get(self, spec: str) -> bytes | None:
        assert self.process.stdin and self.process.stdout
        self.process.stdin.write((spec + '\n').encode())
        self.process.stdin.flush()
        header = self.process.stdout.readline().decode().strip().split()
        if header[-1] == 'missing':
            return None
        assert header[1] == 'blob', header
        size = int(header[2])
        data = self.process.stdout.read(size)
        assert self.process.stdout.read(1) == b'\n'
        return data

    def close(self):
        assert self.process.stdin
        self.process.stdin.close()
        assert self.process.wait() == 0


def scalar(text: str, key: str) -> str | None:
    match = re.search(rf'^{re.escape(key)}:\s*(\S+)', text, re.M)
    return match.group(1).strip('"\'') if match else None


def build(repo: Path, revision: str) -> dict:
    commit = git(repo, 'rev-parse', f'{revision}^{{commit}}').decode().strip()
    paths = git(repo, 'ls-tree', '-r', '--name-only', commit, '--', 'experiments').decode().splitlines()
    ids = sorted({p.split('/')[1] for p in paths if p.startswith('experiments/EXP-') and p.count('/') >= 2})
    unrecognized = [name for name in ids if not EXP_RE.fullmatch(name)]
    if unrecognized:
        raise ValueError(f'experiment IDs outside token grammar: {unrecognized[:10]}')
    idset = set(ids)
    names = [p for p in git(repo, 'ls-tree', '--name-only', f'{commit}:formal/targets').decode().splitlines()
             if p.endswith(('.yaml', '.yml'))]
    mapping: dict[str, set[str]] = defaultdict(set)
    witnesses: list[dict] = []
    skipped_sources: list[dict] = []
    blobs = Blobs(repo)
    try:
        for name in names:
            target = Path(name).stem
            spec_path = f'formal/targets/{name}'
            spec = blobs.get(f'{commit}:{spec_path}')
            assert spec is not None
            spec_text = spec.decode('utf-8')
            candidates = [(spec_path, spec_text, 'target_spec')]
            source = scalar(spec_text, 'source')
            theorem_file = scalar(spec_text, 'theorem_file')
            workspace = scalar(spec_text, 'workspace') or 'formal'
            for path, kind in ((source, 'declared_source'),
                               (f'{workspace}/{theorem_file}' if theorem_file else None, 'theorem_source')):
                if not path or Path(path).suffix.lower() not in TEXT_EXT:
                    continue
                blob = blobs.get(f'{commit}:{path}')
                if blob is None:
                    skipped_sources.append({'target': target, 'path': path, 'reason': 'missing_at_commit'})
                elif len(blob) > MAX_SOURCE_BYTES:
                    skipped_sources.append({'target': target, 'path': path, 'reason': 'over_1MB'})
                else:
                    candidates.append((path, blob.decode('utf-8', errors='replace'), kind))
            for path, text, kind in candidates:
                for exp_id in sorted(set(EXP_RE.findall(text)) & idset):
                    mapping[exp_id].add(target)
                    witnesses.append({'experiment_id': exp_id, 'target': target,
                                      'path': path, 'kind': kind})
    finally:
        blobs.close()
    cohorts = dict(sorted(Counter(i.split('-')[1] for i in ids).items()))
    linked = sorted(mapping)
    return {
        'schema': 'crypto.validation.formal_pointer_inventory/v1',
        'source_commit': commit,
        'experiments_tree_sha': git(repo, 'rev-parse', f'{commit}:experiments').decode().strip(),
        'formal_targets_tree_sha': git(repo, 'rev-parse', f'{commit}:formal/targets').decode().strip(),
        'experiment_paths_sha256': sha256(('\n'.join(paths) + '\n').encode()).hexdigest(),
        'experiment_directories': len(ids),
        'all_experiment_ids': ids,
        'cohort_count': len(cohorts),
        'cohorts': cohorts,
        'formal_targets': len(names),
        'targets_with_exact_experiment_pointer': len({w['target'] for w in witnesses}),
        'experiment_ids_with_exact_formal_pointer': len(linked),
        'experiment_ids_without_exact_formal_pointer': len(ids) - len(linked),
        'exact_pointer_map': {k: sorted(v) for k, v in sorted(mapping.items())},
        'pointer_witnesses': sorted(witnesses, key=lambda w: (w['target'], w['experiment_id'], w['kind'], w['path'])),
        'skipped_sources': skipped_sources,
        'method': 'Exact EXP directory-ID token in registered target YAML, its declared text source, or its theorem source, at this commit. Syntactic coverage only; no proof or run claim.',
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--repo', type=Path, default=Path.cwd())
    ap.add_argument('--revision', default='HEAD')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    result = build(args.repo, args.revision)
    if args.out.exists():
        raise SystemExit(f'refusing to overwrite {args.out}')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in (
        'source_commit', 'experiment_directories', 'formal_targets',
        'targets_with_exact_experiment_pointer', 'experiment_ids_with_exact_formal_pointer',
        'experiment_ids_without_exact_formal_pointer', 'skipped_sources')}, indent=2))


if __name__ == '__main__':
    main()
