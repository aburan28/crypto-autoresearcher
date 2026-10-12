"""Pinned curve metadata reader. Identity checks are not mathematical certification."""
import json
import re
from pathlib import Path, PurePosixPath

from tools.curve_identity import inspect_manifest, canonical
from .comparisons import _read, SHA

TRAITS = (
    ('characteristic', 'Field characteristic', 'field', 'characteristic'),
    ('degree', 'Field degree', 'field', 'degree'),
    ('representation', 'Field representation', 'field', 'representation'),
    ('modulus', 'Defining polynomial / modulus', 'field', 'modulus_exponents'),
    ('model', 'Curve model', 'curve', 'model'),
    ('order', 'Curve order', 'curve', 'order'),
    ('subgroup_order', 'Subgroup order', 'curve', 'subgroup_order'),
    ('cofactor', 'Cofactor', 'curve', 'cofactor'),
    ('trace', 'Trace of Frobenius', 'curve', 'trace'),
    ('j_invariant', 'j-invariant', 'curve', 'j_invariant'),
    ('cm_discriminant', 'CM discriminant', 'endomorphism', 'cm_discriminant'),
    ('endomorphism_order_conductor', 'Endomorphism order conductor', 'endomorphism', 'endomorphism_order_conductor'),
)


def source_pin(source):
    """Only immutable GitHub source links; no arbitrary URI schemes or paths."""
    repo, commit, path = (source[k] for k in ('repository', 'commit', 'path'))
    if (not isinstance(repo, str) or not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', repo)
            or not isinstance(commit, str) or not re.fullmatch(r'[a-f0-9]{40}', commit)
            or not isinstance(path, str) or not path or '\\' in path
            or PurePosixPath(path).is_absolute() or any(p in ('.', '..', '.git') for p in path.split('/'))
            or not SHA.fullmatch(str(source.get('sha256', '')))):
        raise ValueError('Invalid immutable source pin.')
    return {**{k: source[k] for k in ('repository', 'commit', 'path', 'sha256')},
            'url': f'https://github.com/{repo}/blob/{commit}/{path}'}


def exact_json(value):
    """Keep integers outside JavaScript's exact range lossless in display payloads."""
    if type(value) is int and abs(value) > 2**53 - 1:
        return str(value)
    if isinstance(value, dict):
        return {k: exact_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [exact_json(v) for v in value]
    return value


def payload(repo: Path):
    result = {'schema': 1, 'curves': [], 'errors': [],
              'coverage': 'Selected source-reported curve records; not an exhaustive catalog or mathematical certification.'}
    path = repo / 'ui/curves/catalog.json'
    if not path.exists():
        return exact_json(result)
    try:
        registry = json.loads((Path(__file__).parent / 'curves/dissect-traits.json').read_text())
        result['trait_registry'] = registry
        if path.stat().st_size > 131072:
            raise ValueError('Oversized catalog')
        catalog = json.loads(path.read_text())
        if catalog.get('schema') != 1 or not isinstance(catalog.get('capsules'), list) or len(catalog['capsules']) > 100:
            raise ValueError('Unsupported catalog')
        by_uid, aliases = {}, {}
        for spec in catalog['capsules']:
            raw, pin = _read(repo, spec)
            capsule = json.loads(raw)
            if capsule.get('schema') != 'curve-capsule/1':
                raise ValueError('Unsupported capsule')
            canonical(capsule)  # reject non-finite or inexact numeric metadata
            identity = inspect_manifest(capsule)
            if capsule.get('curve_uid') != identity['curve_uid']:
                raise ValueError('Curve UID mismatch')
            uid, alias = identity['curve_uid'], identity['curve_id']
            if alias in aliases and aliases[alias] != uid:
                raise ValueError('Conflicting curve alias')
            aliases[alias] = uid
            source = source_pin(capsule['source'])
            traits = {}
            for key, label, section, field in TRAITS:
                value = capsule.get(section, {}).get(field)
                if key == 'modulus' and value is None:
                    value = capsule['field'].get('modulus', capsule['field'].get('defining_polynomial'))
                traits[key] = {'label': label, 'value': value,
                               'status': 'source_reported' if value is not None else 'unknown',
                               'source': source if value is not None else None}
            # Definitions are not measurement evidence. Parameterized outputs remain
            # unknown until a separately reviewed, parameter-keyed result reader exists.
            for family in registry['families']:
                definition = source_pin(family['source'])
                for output in family['outputs']:
                    key = f"dissect.{family['key']}.{output['key']}"
                    traits[key] = {
                        'label': f"DiSSECT · {family['key']} · {output['label']}",
                        'value': None, 'status': 'unknown', 'source': None,
                        'definition': definition, 'description': family['description'],
                        'parameters': family['parameters'], 'output_type': output['type'],
                    }
            row = {**identity, 'field': capsule['field'], 'curve': capsule['curve'],
                   'traits': traits, 'sources': [source], 'capsule': pin}
            if uid in by_uid:
                previous = by_uid[uid]
                # Same identity may acquire supplementary traits, but conflicts fail closed.
                for key, trait in traits.items():
                    old = previous['traits'][key]
                    if old['value'] is not None and trait['value'] is not None and old['value'] != trait['value']:
                        raise ValueError('Conflicting sourced trait')
                    if old['value'] is None:
                        previous['traits'][key] = trait
                if source not in previous['sources']:
                    previous['sources'].append(source)
            else:
                by_uid[uid] = row
        result['curves'] = sorted(by_uid.values(), key=lambda r: r['curve_id'])
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
        result['curves'] = []
        result['errors'] = ['Curve catalog is missing, malformed, conflicting, or does not match its pins.']
    return exact_json(result)
