"""Read a pinned, offline metadata snapshot; never fetch or execute benchmarks."""
import json
import math
import re
from pathlib import Path

from tools.curve_identity import inspect_manifest
from .comparisons import _read


def payload(repo: Path):
    try:
        catalog = repo / 'ui/benchmarks/catalog.json'
        if not catalog.exists():
            return {'rows': [], 'identities': {}, 'sources': {}, 'coverage': 'No snapshot supplied.'}
        if catalog.stat().st_size > 8192:
            raise ValueError('Oversized catalog')
        pin = json.loads(catalog.read_text())
        raw, _ = _read(repo, pin)
        data = json.loads(raw)
        if data.get('schema') != 1 or not isinstance(data.get('rows'), list) or len(data['rows']) > 1000:
            raise ValueError('Unsupported snapshot')
        slug, commit = data['source_repository'], data['source_commit']
        if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', slug) or not re.fullmatch(r'[a-f0-9]{40}', commit):
            raise ValueError('Invalid provenance')
        identities = data['identities']
        for uid, identity in identities.items():
            actual = inspect_manifest(identity)
            if uid != actual['curve_uid'] or any(identity.get(k) != v for k, v in actual.items()):
                raise ValueError('Curve identity mismatch')
        for path, source in data['sources'].items():
            if (path.startswith('/') or '..' in path.split('/') or '\\' in path
                    or not re.fullmatch(r'[a-f0-9]{64}', source['sha256'])
                    or source['path'] != path
                    or source['url'] != f'https://github.com/{slug}/blob/{commit}/{path}'):
                raise ValueError('Invalid source pin')
        seen = set()
        for row in data['rows']:
            if row['id'] in seen or row['curve_uid'] not in identities:
                raise ValueError('Duplicate row or unresolved curve')
            seen.add(row['id'])
            if row['curve_id'] != identities[row['curve_uid']]['curve_id']:
                raise ValueError('Curve alias mismatch')
            for key in ('candidate_sha256', 'workload_sha256'):
                if not re.fullmatch(r'[a-f0-9]{64}', row[key]):
                    raise ValueError('Invalid identity digest')
            if not row['candidate_sha256'].startswith(row['candidate_id'].rsplit('h', 1)[-1]) or not row['workload_sha256'].startswith(row['workload_id']):
                raise ValueError('Compact identity mismatch')
            if not row['sources'] or any(p not in data['sources'] for p in row['sources']):
                raise ValueError('Unresolved source')
            for key in ('target_count', 'targets_verified', 'factor_base_points', 'total_operations', 'wall_ns', 'ic_online_ns', 'rho_online_ns'):
                value = row.get(key)
                if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                    raise ValueError('Invalid measurement')
        return data
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
        return {'rows': [], 'identities': {}, 'sources': {}, 'error': 'Benchmark snapshot is missing, invalid, or does not match its pin.'}
