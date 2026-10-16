#!/usr/bin/env python3
"""Snapshot crypto's computed curve traits for the curve catalog (no arithmetic).

Reads `docs/curves/{traits.json,registry.json,TRAITS.md}` at one exact commit of
an aburan28/crypto checkout (`git show`, so the working tree is never read),
and writes, under `ui/curves/`:

* `crypto-<EC1>.json`: a `curve-capsule/1` for each `--capsule` EC1 alias,
  copied verbatim from the registry representation; the shared
  identity helper must reproduce the registry's `curve_uid`.
* `crypto-traits.json`: the traits records whose registry representations
  include a catalogued `curve_uid`, verbatim, with the three source pins.

and re-pins both in `ui/curves/catalog.json`. `--check` rebuilds in memory and
fails if any written file differs. Joins use exact `curve_uid` only: a capsule
under another modulus or generator is a different record and gets no traits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.curve_identity import inspect_manifest  # noqa: E402

PATHS = {'traits': 'docs/curves/traits.json', 'registry': 'docs/curves/registry.json',
         'definitions': 'docs/curves/TRAITS.md'}
SNAPSHOT = 'ui/curves/crypto-traits.json'
CATALOG = 'ui/curves/catalog.json'


def dump(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def build(crypto, commit, repository, aliases):
    commit = subprocess.run(['git', '-C', str(crypto), 'rev-parse', '--verify', f'{commit}^{{commit}}'],
                            check=True, capture_output=True, text=True).stdout.strip()
    blobs = {k: subprocess.run(['git', '-C', str(crypto), 'show', f'{commit}:{p}'], check=True,
                               capture_output=True).stdout for k, p in PATHS.items()}
    pins = {k: {'repository': repository, 'commit': commit, 'path': PATHS[k], 'sha256': sha(raw)}
            for k, raw in blobs.items()}
    traits, registry = json.loads(blobs['traits']), json.loads(blobs['registry'])
    if traits.get('schema') != 'curve-traits/1' or traits.get('registry_sha256') != pins['registry']['sha256']:
        raise SystemExit('traits.json is not curve-traits/1 built from this registry.json')
    files = {}
    catalog = json.loads((REPO / CATALOG).read_text())
    reps = {r['ec1']: r for c in registry['curves'] for r in c['representations']}
    for alias in aliases:
        rep = reps.get(alias)
        if rep is None:
            raise SystemExit(f'{alias} is not a registry representation at {commit}')
        capsule = {'schema': 'curve-capsule/1', 'curve_uid': rep['curve_uid'], 'field': rep['field'],
                   'curve': {**rep['curve'], 'curve_id': alias}, 'source': pins['registry']}
        if inspect_manifest(capsule)['curve_uid'] != rep['curve_uid']:
            raise SystemExit(f'{alias}: identity helper does not reproduce the registry curve_uid')
        path = f'ui/curves/crypto-{alias}.json'
        files[path] = dump(capsule)
        catalog['capsules'] = [s for s in catalog['capsules'] if s['path'] != path]
        catalog['capsules'].append({'path': path, 'sha256': sha(files[path])})
    uids = set()
    for spec in catalog['capsules']:
        raw = files.get(spec['path']) or (REPO / spec['path']).read_bytes()
        uids.add(json.loads(raw)['curve_uid'])
    by_slug = {t['slug']: t for t in traits['curves']}
    records = []
    for curve in registry['curves']:
        joined = [r for r in curve['representations'] if r['curve_uid'] in uids]
        if joined:
            records.append({'slug': curve['slug'], 'icv1': curve['icv1'], 'traits': by_slug[curve['slug']],
                            'representations': [{k: r[k] for k in ('ec1', 'curve_uid', 'field_sha256')}
                                                for r in curve['representations']]})
    snapshot = {'schema': 'crypto-curve-traits-snapshot/1', 'adapter': 'crypto-curve-traits/1',
                'traits_schema': traits['schema'], 'registry_sha256': traits['registry_sha256'],
                'factor_budget': traits.get('factor_budget'), 'sources': pins,
                'records': sorted(records, key=lambda r: r['slug'])}
    files[SNAPSHOT] = dump(snapshot)
    catalog['supplementary_traits'] = [{'adapter': 'crypto-curve-traits/1', 'path': SNAPSHOT,
                                        'sha256': sha(files[SNAPSHOT])}]
    files[CATALOG] = dump(catalog)
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--crypto', required=True, type=Path, help='aburan28/crypto checkout')
    ap.add_argument('--commit', required=True, help='exact crypto commit to read')
    ap.add_argument('--repository', default='aburan28/crypto')
    ap.add_argument('--capsule', action='append', default=[], help='registry EC1 alias to capsule')
    ap.add_argument('--check', action='store_true', help='fail if the committed files differ')
    args = ap.parse_args(argv)
    aliases = args.capsule
    if args.check and not aliases:  # re-derive the registry capsules already catalogued
        catalog = json.loads((REPO / CATALOG).read_text())
        aliases = [s['path'][len('ui/curves/crypto-'):-len('.json')] for s in catalog['capsules']
                   if s['path'].startswith('ui/curves/crypto-EC1')]
    files = build(args.crypto, args.commit, args.repository, aliases)
    stale = [p for p, raw in files.items() if not (REPO / p).is_file() or (REPO / p).read_bytes() != raw]
    if args.check:
        print('\n'.join(f'stale: {p}' for p in stale) or 'crypto curve traits snapshot is current')
        return 1 if stale else 0
    for path in stale:
        (REPO / path).write_bytes(files[path])
        print(f'wrote {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
