#!/usr/bin/env python3
"""Retrieve scoped advisory evidence without treating missing data as a refutation.

The default check is structural. --artifacts requires explicit authorized source
roots, checks content digests and recorded JSON values, and certifies no new
scientific inference. No command executes a proof assistant or changes the ledger.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parents[1] / 'research' / 'ten-lead-evidence'
BASES = frozenset({'execution_limit', 'implementation_gap', 'bounded_observation',
    'finite_enumeration', 'written_derivation', 'native_certificate', 'construction_fact'})
REQUIRED = frozenset({'schema_version', 'id', 'lead', 'key', 'created_at', 'record_type',
    'basis', 'statement', 'scope', 'scope_kind', 'assumptions', 'not_implied', 'lesson',
    'next_discriminating_test', 'revisit_when', 'support', 'depends_on', 'supersedes',
    'contradicts', 'formal_verification', 'review', 'broad_direction_closed'})


class EvidenceError(ValueError):
    """A record or its provenance cannot support the requested check."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise EvidenceError(f'Cannot read JSON at {path}: {error}') from error


def digest(path: Path) -> str:
    try:
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        return h.hexdigest()
    except OSError as error:
        raise EvidenceError(f'Cannot hash artifact {path}: {error}') from error


def validate_record(q: dict) -> dict:
    require(isinstance(q, dict), 'Claim must be an object')
    require(not REQUIRED - q.keys(), f'Missing fields: {sorted(REQUIRED - q.keys())}')
    require(isinstance(q['id'], str) and re.fullmatch(r'C-[0-9a-f]{12}', q['id']) is not None,
            'Invalid claim ID')
    require(q['schema_version'] == '1.0', 'Unsupported claim schema version')
    require(isinstance(q['basis'], str) and q['basis'] in BASES, 'Unknown evidence basis; Lean promotion is not implemented')
    require(type(q['lead']) is int and 1 <= q['lead'] <= 10, 'Invalid lead number')
    require(q['broad_direction_closed'] is False, 'Advisory records cannot close a direction')
    for key in ('key', 'created_at', 'record_type', 'statement', 'scope', 'scope_kind',
                'lesson', 'next_discriminating_test', 'revisit_when'):
        require(isinstance(q[key], str) and bool(q[key].strip()), f'Empty or invalid {key}')
    for key in ('assumptions', 'not_implied', 'depends_on', 'supersedes', 'contradicts'):
        require(isinstance(q[key], list) and all(isinstance(x, str) for x in q[key]),
                f'Invalid {key}')
    require(bool(q['not_implied']), 'Explicit inference boundaries are required')
    require(isinstance(q['support'], list) and bool(q['support']), 'Supporting references required')
    for support in q['support']:
        require(isinstance(support, dict), 'Support must be an object')
        require(all(isinstance(support.get(k), str) for k in ('source', 'path', 'sha256')),
                'Invalid support reference')
        path = Path(support['path'])
        require(not path.is_absolute() and '..' not in path.parts and bool(path.parts),
                'Support path must remain inside its source root')
        require(re.fullmatch(r'[0-9a-f]{64}', support['sha256']) is not None,
                'Invalid artifact digest')
    formal = q['formal_verification']
    require(isinstance(formal, dict) and formal.get('status') in ('not_formalized', 'draft'),
            'A Lean label requires a kernel replay adapter and semantic review; neither is supplied here')
    require(isinstance(q['review'], dict) and q['review'].get('official_ledger_imported') is False,
            'Official research promotion is outside this register')
    return q


def validate_graph(claims: list[dict]) -> None:
    by_id = {q['id']: q for q in claims}
    require(len(by_id) == len(claims), 'Duplicate claim ID')
    active, done = set(), set()

    def visit(identifier: str) -> None:
        require(identifier in by_id, f'Missing dependency: {identifier}')
        if identifier in done:
            return
        require(identifier not in active, f'Dependency cycle at {identifier}')
        active.add(identifier)
        for dependency in by_id[identifier]['depends_on']:
            visit(dependency)
        active.remove(identifier)
        done.add(identifier)

    for q in claims:
        visit(q['id'])
        for identifier in q['contradicts'] + q['supersedes']:
            require(identifier in by_id, f'Missing referenced claim: {identifier}')


class Register:
    def __init__(self, root: Path = DEFAULT_ROOT, source_roots: dict[str, Path] | None = None):
        self.root = root.resolve()
        self.sources = read_json(self.root / 'sources.json')
        configured = self.sources.get('roots', {})
        self.source_roots = {k: Path(v).resolve() for k, v in configured.items() if v}
        self.source_roots.update({k: Path(v).resolve() for k, v in (source_roots or {}).items()})

    def load(self) -> list[dict]:
        claims = []
        for path in sorted((self.root / 'claims').glob('C-*.json')):
            q = validate_record(read_json(path))
            require(path.stem == q['id'], f'Filename and record ID differ: {path}')
            claims.append(q)
        require(bool(claims), 'No advisory claims found')
        return claims

    def artifact_path(self, source: str, relative: str) -> Path:
        require(source in self.source_roots,
                f'Source root {source!r} unavailable; supply --source-root {source}=/authorized/path. '
                'Missing access is not negative scientific evidence.')
        base = self.source_roots[source]
        target = (base / relative).resolve()
        require(target.is_relative_to(base), 'Artifact path or symlink escapes source root')
        return target

    def check_artifacts(self, claims: list[dict]) -> tuple[int, int]:
        seen: dict[tuple[str, str], str] = {}
        assertions = 0
        for q in claims:
            bound = {(s['source'], s['path']) for s in q['support']}
            for support in q['support']:
                key = support['source'], support['path']
                if key not in seen:
                    seen[key] = digest(self.artifact_path(*key))
                require(seen[key] == support['sha256'], f'Artifact changed: {key}')
            for assertion in q.get('artifact_assertions', []):
                key = assertion['source'], assertion['path']
                require(key in bound, 'Recorded-value assertions must refer to a bound artifact')
                value = read_json(self.artifact_path(*key))
                try:
                    for part in assertion['pointer']:
                        value = value[int(part)] if isinstance(value, list) else value[part]
                except (KeyError, IndexError, ValueError, TypeError) as error:
                    raise EvidenceError(f'Invalid artifact pointer in {q["id"]}') from error
                expected = assertion['expected']
                require(type(value) is type(expected) and value == expected,
                        f'Recorded value differs in {q["id"]}: {assertion["pointer"]}')
                assertions += 1
        return len(seen), assertions

    def check(self, *, artifacts: bool = False, archive_dir: Path | None = None) -> dict:
        claims = self.load()
        validate_graph(claims)
        leads = [read_json(p) for p in sorted((self.root / 'leads').glob('L*.json'))]
        require(len(leads) == 10 and {q['lead'] for q in leads} == set(range(1, 11)),
                'Expected one entry for each of the ten leads')
        for lead in leads:
            require(lead['research_question_status'] == 'open' and lead['exhausted'] is False
                    and lead['official_status_changed'] is False, 'Unexpected official lead transition')
            ids = {q['id'] for q in claims if q['lead'] == lead['lead']}
            require(set(lead['claim_ids_at_initial_import']) <= ids, 'Missing initial-import claim')
        ids = {q['id'] for q in claims}
        for edge in read_json(self.root / 'relations.json')['edges']:
            require(edge['source'] in ids and edge['target'] in ids and edge['type']
                    and edge['explanation'], 'Invalid typed relationship')
        bound, assertions = self.check_artifacts(claims) if artifacts else (0, 0)
        if archive_dir is not None:
            for archive in self.sources['archives']:
                name = archive.get('name') or Path(archive['file']).name
                require(Path(name).name == name, 'Invalid archive filename')
                require(digest(archive_dir / name) == archive['sha256'], f'Archive differs: {name}')
        return dict(status='PASS_RECORD_STRUCTURE_AND_REQUESTED_BINDINGS', claims=len(claims),
                    leads=len(leads), artifacts_checked=artifacts, unique_bound_artifacts=bound,
                    artifact_value_assertions=assertions, archive_hashes_checked=archive_dir is not None,
                    lean_verified_claims=0, broad_directions_closed=0,
                    scientific_truth_newly_certified=False, independent_agent_review_obtained=False,
                    official_ledger_changed=False)

    def append(self, q: dict) -> dict:
        q = dict(q)
        q.setdefault('id', 'C-' + secrets.token_hex(6))
        q.setdefault('created_at', datetime.now(timezone.utc).isoformat())
        validate_record(q)
        existing = self.load()
        require(q['id'] not in {x['id'] for x in existing}, 'ID already exists')
        validate_graph(existing + [q])
        self.check_artifacts([q])
        temporary = self.root / 'claims' / ('.pending-' + secrets.token_hex(12))
        final = self.root / 'claims' / (q['id'] + '.json')
        try:
            with temporary.open('x', encoding='utf-8') as stream:
                json.dump(q, stream, indent=2)
                stream.write('\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temporary, final)  # Complete atomic publication without overwriting another writer.
        finally:
            temporary.unlink(missing_ok=True)
        return dict(appended=q['id'], official_ledger_changed=False, broad_direction_closed=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--register', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--source-root', action='append', default=[], metavar='NAME=PATH')
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('check')
    p.add_argument('--artifacts', action='store_true')
    p.add_argument('--archive-dir', type=Path)
    p = sub.add_parser('lead'); p.add_argument('number', type=int); p.add_argument('--json', action='store_true')
    p = sub.add_parser('claim'); p.add_argument('id')
    p = sub.add_parser('find'); p.add_argument('text')
    p = sub.add_parser('add'); p.add_argument('file', type=Path)
    sub.add_parser('summary')
    args = parser.parse_args(argv)
    try:
        roots = {}
        for item in args.source_root:
            require('=' in item, 'Source root must be NAME=PATH')
            key, value = item.split('=', 1)
            require(bool(key) and bool(value) and key not in roots, 'Empty or duplicate source root')
            roots[key] = Path(value)
        register = Register(args.register, roots)
        if args.action == 'check':
            print(json.dumps(register.check(artifacts=args.artifacts, archive_dir=args.archive_dir), indent=2))
            return 0
        if args.action == 'add':
            print(json.dumps(register.append(read_json(args.file)), indent=2)); return 0
        claims = register.load()
        if args.action == 'summary':
            print(json.dumps(dict(claim_count=len(claims), open_leads=10, lean_verified_claims=0,
                                  raw_artifacts_included=register.sources.get('raw_artifacts_included', False)), indent=2))
            return 0
        if args.action == 'lead':
            require(1 <= args.number <= 10, 'Lead must be between1 and10')
            claims = [q for q in claims if q['lead'] == args.number]
            if args.json:
                print(json.dumps(claims, indent=2)); return 0
        elif args.action == 'claim':
            claims = [q for q in claims if q['id'] == args.id]
            require(len(claims) == 1, 'Unknown claim ID')
            print(json.dumps(claims[0], indent=2)); return 0
        elif args.action == 'find':
            claims = [q for q in claims if args.text.lower() in json.dumps(q).lower()]
        for q in sorted(claims, key=lambda q: (q['lead'], q['key'])):
            print(f"{q['id']} | lead {q['lead']} | {q['basis']} | Lean: {q['formal_verification']['status']}")
            for label, key in [('ESTABLISHES', 'statement'), ('SCOPE', 'scope'), ('LESSON', 'lesson'),
                               ('NEXT', 'next_discriminating_test')]:
                print(f'{label}: {q[key]}')
            print('DOES NOT ESTABLISH: ' + '; '.join(q['not_implied']) + '\n')
        return 0
    except (EvidenceError, OSError) as error:
        print(f'Cannot complete requested evidence check: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
