#!/usr/bin/env python3
"""Check historical claim/evidence bindings, without deciding scientific validity.

Reads explicit immutable Git objects, never working-tree evidence or remote URLs.
Missing evidence remains visible. A successful integrity check is not a proof,
an execution certificate, a review decision, or a complete claim denominator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

SCHEMA = 'historical-claim-evidence/v1'
ROLES = frozenset(('formal_source', 'toolchain', 'dependencies', 'native_build',
                  'axiom_audit', 'elaborated_types', 'fidelity_review', 'protocol',
                  'raw_records', 'implementation', 'controls', 'replay',
                  'execution_review', 'context'))
REQUIRED = {
    'mathematical': {'formal_source', 'toolchain', 'dependencies', 'native_build',
                     'axiom_audit', 'elaborated_types', 'fidelity_review', 'controls'},
    'computed': {'protocol', 'raw_records', 'implementation', 'controls', 'replay',
                 'execution_review'},
    'measured': {'protocol', 'raw_records', 'implementation', 'controls',
                 'execution_review'},
    'interpretive': {'context', 'fidelity_review'},
}
MAX_BLOB = 16 * 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024


class MatrixError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise MatrixError(message)


def fields(obj, names, label):
    require(isinstance(obj, dict) and set(obj) == set(names), f'{label}: wrong fields')


def string(value, label):
    require(isinstance(value, str) and bool(value.strip()), f'{label}: empty/non-string')
    return value


def strings(value, label):
    require(isinstance(value, list), f'{label}: expected list')
    for item in value:
        string(item, label)
    require(len(value) == len(set(value)), f'{label}: duplicate value')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, f'duplicate JSON key: {key}')
        obj[key] = value
    return obj


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=no_duplicate_keys)


def git(repo, *args):
    try:
        return subprocess.run(
            ['git', '--literal-pathspecs', '-C', str(repo), *args],
            env={**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_TERMINAL_PROMPT': '0',
                 'GIT_NO_REPLACE_OBJECTS': '1'},
            check=True, capture_output=True, timeout=20,
        ).stdout
    except (subprocess.SubprocessError, OSError) as exc:
        raise MatrixError(f'local Git object unavailable ({args[0]}): {exc}') from exc


def read_source(source, repositories):
    fields(source, ('id', 'kind', 'repo', 'commit', 'path', 'blob_oid', 'sha256'), 'Git source')
    require(source['repo'] in repositories, f"repository not supplied: {source['repo']}")
    repo = repositories[source['repo']]
    commit = source['commit']
    require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', commit),
            'commit must be a full immutable object ID')
    require(git(repo, 'cat-file', '-t', commit).strip() == b'commit', 'object is not a commit')
    path = string(source['path'], 'path')
    parsed = PurePosixPath(path)
    require(not parsed.is_absolute() and parsed.as_posix() == path and
            '..' not in parsed.parts and '\\' not in path and '\0' not in path,
            'path must be canonical and repository-relative')
    entries = git(repo, 'ls-tree', '-z', commit, '--', path).split(b'\0')
    require(len(entries) == 2 and entries[1] == b'' and entries[0], 'path is absent or ambiguous')
    metadata, actual_path = entries[0].split(b'\t', 1)
    mode, kind, oid = metadata.decode('ascii').split()
    require(mode in ('100644', '100755') and kind == 'blob', 'source must be a regular Git blob')
    require(actual_path.decode('utf-8') == path and oid == source['blob_oid'], 'Git blob binding mismatch')
    size = int(git(repo, 'cat-file', '-s', oid))
    require(size <= MAX_BLOB, 'source exceeds bounded reader limit; use an explicit unavailable record')
    data = git(repo, 'cat-file', 'blob', oid)
    require(len(data) == size and digest(data) == source['sha256'], 'source SHA-256 mismatch')
    return data


def check(matrix, repositories):
    fields(matrix, ('schema', 'scope', 'sources', 'claims'), 'matrix')
    require(matrix['schema'] == SCHEMA, 'unsupported schema')
    fields(matrix['scope'], ('objective', 'coverage', 'omissions'), 'scope')
    string(matrix['scope']['objective'], 'objective')
    require(matrix['scope']['coverage'] == 'partial', 'this register does not establish complete claim coverage')
    strings(matrix['scope']['omissions'], 'omissions')
    require(matrix['scope']['omissions'], 'unresolved coverage must be stated')
    require(isinstance(matrix['sources'], list) and matrix['sources'], 'empty source register')
    require(isinstance(matrix['claims'], list) and matrix['claims'], 'empty claim register')
    sources, blobs, unavailable = {}, {}, []
    total = 0
    for source in matrix['sources']:
        require(isinstance(source, dict), 'source is not an object')
        sid = string(source.get('id'), 'source id')
        require(sid not in sources, f'duplicate source: {sid}')
        if source.get('kind') == 'unavailable':
            fields(source, ('id', 'kind', 'locator', 'reason'), 'unavailable source')
            string(source['locator'], 'locator'); string(source['reason'], 'reason')
            unavailable.append(sid)
        else:
            require(source.get('kind') == 'git', 'unknown source kind')
            blobs[sid] = read_source(source, repositories)
            total += len(blobs[sid])
            require(total <= MAX_TOTAL, 'matrix exceeds bounded total reader limit')
        sources[sid] = source
    claims, ids = [], set()
    for claim in matrix['claims']:
        fields(claim, ('id', 'classification', 'source_id', 'excerpt', 'statement',
                       'assumptions', 'evidence', 'open_obligations'), 'claim')
        cid = string(claim['id'], 'claim id')
        require(cid not in ids, f'duplicate claim: {cid}'); ids.add(cid)
        category = claim['classification']
        require(category in REQUIRED, 'unknown claim classification')
        string(claim['statement'], 'statement')
        strings(claim['assumptions'], 'assumptions')
        strings(claim['open_obligations'], 'open obligations')
        sid = claim['source_id']
        require(sid in blobs, 'claim excerpt requires available source bytes')
        excerpt = claim['excerpt']
        fields(excerpt, ('start_line', 'end_line', 'text', 'sha256'), 'excerpt')
        start, end = excerpt['start_line'], excerpt['end_line']
        lines = blobs[sid].decode('utf-8').splitlines(keepends=True)
        require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
                'invalid excerpt line range')
        text = ''.join(lines[start-1:end])
        require(text == excerpt['text'] and digest(text.encode('utf-8')) == excerpt['sha256'],
                'claim excerpt does not match bound source')
        evidence = claim['evidence']
        require(isinstance(evidence, dict) and set(evidence) <= ROLES, 'unknown evidence role')
        for role, refs in evidence.items():
            strings(refs, role)
            require(all(ref in sources for ref in refs), f'dangling evidence reference: {role}')
        present = {role for role, refs in evidence.items() if refs and all(r in blobs for r in refs)}
        claims.append({
            'id': cid, 'classification': category, 'source_id': sid,
            'excerpt_integrity': 'passed',
            'bound_evidence_roles': sorted(present),
            'missing_evidence_roles': sorted(REQUIRED[category] - present),
            'unavailable_evidence': sorted({r for refs in evidence.values() for r in refs if r not in blobs}),
            'open_obligations': claim['open_obligations'],
            'scientific_validity': 'not_assessed_by_integrity_checker',
        })
    return {
        'schema': 'historical-claim-evidence-check/v1', 'integrity_status': 'passed',
        'coverage_complete': False, 'individual_claim_denominator': None,
        'scientific_validity': 'not_assessed_by_integrity_checker',
        'interpretation': 'Exact source/excerpt/evidence identity only; presence of a role does not validate its content or prove a claim.',
        'claim_rows': len(claims), 'available_sources': len(blobs),
        'unavailable_sources': unavailable, 'source_bytes_read': total,
        'omissions': matrix['scope']['omissions'], 'claims': claims,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('matrix', type=Path)
    parser.add_argument('--repo', action='append', default=[], metavar='NAME=LOCAL_PATH')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        repositories = {}
        for pair in args.repo:
            name, path = pair.split('=', 1)
            require(name not in repositories and name and path, 'invalid/duplicate repository mapping')
            repositories[name] = Path(path)
        matrix_bytes = args.matrix.read_bytes()
        record = json.loads(matrix_bytes.decode('utf-8'), object_pairs_hook=no_duplicate_keys)
        result = check(record, repositories)
        result['matrix_sha256'] = digest(matrix_bytes)
        encoded = json.dumps(result, indent=2, ensure_ascii=True) + '\n'
        if args.output:
            require(args.output.resolve() != args.matrix.resolve(), 'output must not replace the matrix')
            require(not args.output.exists(), 'output already exists; preserve prior receipts')
            with args.output.open('x', encoding='utf-8') as out:
                out.write(encoded)
        else:
            print(encoded, end='')
        return 0
    except (ValueError, KeyError, TypeError, UnicodeError, OSError) as exc:
        print(f'matrix integrity failure: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
