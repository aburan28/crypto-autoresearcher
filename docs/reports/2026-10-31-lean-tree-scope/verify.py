#!/usr/bin/env python3
"""Recompute a frozen Lean-source inventory boundary from local Git objects.

File/path identity only. This does not build Lean, audit axioms, assess theorem
meaning, authenticate historical execution, or count distinct research claims.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
SNAPSHOTS = {
    'crypto': ('192e5eec8b16fc7ce632c00f2a6d65fb9e60fb8c', 'crypto.json.gz'),
    'cryptanalysis': ('d3673ee089dd2a3a4ba15da087b95ebf2fb8e123', 'cryptanalysis.json.gz'),
    'auto-researcher': ('7a40243d9db4de7c1310e2534897b7d6e7d02929', 'auto-researcher.json.gz'),
}
ARCHIVE = '6d83c09bc224472fedbfa5c1baa7e65b20502573'
RECEIPT = 'reports/lean-current-corpus-20261025-main-update/receipt.json'


def run_git(repo: Path, *args: str) -> bytes:
    env = {**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_NO_REPLACE_OBJECTS': '1',
           'GIT_TERMINAL_PROMPT': '0', 'GIT_ALLOW_PROTOCOL': ''}
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          capture_output=True, env=env, timeout=90).stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def tree(repo: Path, commit: str) -> tuple[dict[str, str], int, int, str]:
    require(run_git(repo, 'cat-file', '-t', commit).strip() == b'commit', 'source is not a commit')
    tree_oid = run_git(repo, 'rev-parse', commit + '^{tree}').decode().strip()
    lean: dict[str, str] = {}
    blobs = nonblobs = 0
    for entry in run_git(repo, 'ls-tree', '-r', '-z', commit).split(b'\0'):
        if not entry:
            continue
        meta, name = entry.split(b'\t', 1)
        mode, kind, oid = meta.decode('ascii').split()
        path = name.decode('utf-8')
        if kind == 'blob':
            blobs += 1
            if path.endswith('.lean'):
                require(path not in lean, f'duplicate Lean path: {path}')
                lean[path] = oid
        else:
            nonblobs += 1
    return lean, blobs, nonblobs, tree_oid


def build(repos: dict[str, Path]) -> dict:
    snapshots = {}
    trees = {}
    for name, (commit, filename) in SNAPSHOTS.items():
        repo = repos[name]
        archive = (HERE / filename).read_bytes()
        data = gzip.decompress(archive)
        inv = json.loads(data)
        lean, blobs, nonblobs, tree_oid = tree(repo, commit)
        require(inv['source_commit'] == commit and inv['source_tree'] == tree_oid,
                f'{name}: wrong source commit or tree')
        require(inv['counts']['tracked_blobs'] == blobs, f'{name}: blob count differs')
        require(inv['counts']['tracked_non_blob_entries'] == nonblobs,
                f'{name}: nonblob count differs')
        recorded = {row['path']: row['blob_oid'] for row in inv['lean_files']}
        require(recorded == lean and inv['counts']['lean_files_total'] == len(lean),
                f'{name}: Lean path/blob map differs')
        require(len(recorded) == len(inv['lean_files']), f'{name}: duplicate Lean path')
        snapshots[name] = {
            'commit': commit, 'tree': tree_oid, 'inventory': filename,
            'inventory_sha256': digest(data), 'archive_sha256': digest(archive),
            'tracked_blobs': blobs,
            'tracked_lean_files': len(lean),
            'lexical_theorem_lemma_pointers': inv['counts']['lexical_theorem_lemma_pointers'],
            'tracked_study_directories': inv['counts']['tracked_study_directories'],
            'study_directories_with_colocated_lean': inv['counts']['tracked_study_directories_with_colocated_lean'],
        }
        trees[name] = lean
    crypto = repos['crypto']
    tool = run_git(crypto, 'show', SNAPSHOTS['crypto'][0] + ':tools/formal_coverage_inventory.py')
    cryptanalysis = repos['cryptanalysis']
    receipt_bytes = run_git(cryptanalysis, 'show', SNAPSHOTS['cryptanalysis'][0] + ':' + RECEIPT)
    receipt = json.loads(receipt_bytes)
    old, _, _, _ = tree(cryptanalysis, ARCHIVE)
    current = trees['cryptanalysis']
    same = sorted(p for p in old.keys() & current.keys() if old[p] == current[p])
    changed = sorted(p for p in old.keys() & current.keys() if old[p] != current[p])
    added = sorted(current.keys() - old.keys())
    fresh = sorted(receipt['fresh_native_files'])
    require(len(fresh) == len(set(fresh)) and all(p in current for p in fresh),
            'fresh path is duplicate or absent')
    require(not set(fresh) & set(same), 'fresh path overlaps identical archive')
    require(len(same) == receipt['archived_byte_identical_files'] == 90,
            'archive-identical count differs')
    require(len(fresh) == 7 and len(current) == 184, 'receipt/tree count differs')
    outside = sorted(set(current) - set(same) - set(fresh))
    require(len(outside) == 87, 'outside-receipt count differs')
    return {
        'schema': 'lean-source-tree-scope/v1',
        'interpretation': 'Exact tracked Git source paths and lexical declarations; no theorem, axiom, semantic-fidelity, execution, or individual-claim coverage verdict.',
        'source_tool': {'repo': 'crypto', 'path': 'tools/formal_coverage_inventory.py',
                        'commit': SNAPSHOTS['crypto'][0], 'sha256': digest(tool)},
        'snapshots': snapshots,
        'cryptanalysis_corpus_boundary': {
            'archive_commit': ARCHIVE,
            'receipt_path': RECEIPT,
            'receipt_sha256': digest(receipt_bytes),
            'receipt_scope': receipt['scope'],
            'archive_lean_files': len(old),
            'current_tracked_lean_files': len(current),
            'archived_byte_identical_paths': same,
            'changed_archive_paths': changed,
            'new_since_archive_paths': added,
            'fresh_native_receipt_paths': fresh,
            'outside_this_receipt_paths': outside,
            'outside_this_receipt_by_root': dict(sorted(Counter(p.split('/')[0] for p in outside).items())),
            'boundary': 'Outside this particular 97-source receipt does not imply uncompiled or invalid; other gates and semantic reviews must be checked per claim.',
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    for name in SNAPSHOTS:
        ap.add_argument('--' + name + '-repo', required=True, type=Path)
    ap.add_argument('--write', action='store_true', help='create manifest.json once')
    args = ap.parse_args()
    repos = {name: getattr(args, name.replace('-', '_') + '_repo') for name in SNAPSHOTS}
    result = build(repos)
    encoded = (json.dumps(result, sort_keys=True, indent=2) + '\n').encode()
    path = HERE / 'manifest.json'
    if args.write:
        with path.open('xb') as stream:
            stream.write(encoded)
    else:
        require(path.read_bytes() == encoded, 'manifest differs from exact Git recomputation')
    b = result['cryptanalysis_corpus_boundary']
    print('PASS', 'Lean files', {n: result['snapshots'][n]['tracked_lean_files'] for n in SNAPSHOTS},
          'cryptanalysis receipt', len(b['archived_byte_identical_paths']),
          len(b['fresh_native_receipt_paths']), 'outside', len(b['outside_this_receipt_paths']))


if __name__ == '__main__':
    main()
