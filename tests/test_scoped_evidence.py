"""Synthetic guard tests; no private research artifacts or network are required."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.scoped_evidence import (
    DEFAULT_ROOT, EvidenceError, Register, digest, validate_graph, validate_record,
)


def sample_claim(sha: str) -> dict:
    return dict(schema_version='1.0', id='C-000000000001', lead=1, key='synthetic',
        created_at='2026-10-17T00:00:00+00:00', record_type='observation',
        basis='execution_limit', statement='The synthetic process reached its limit.',
        scope='One synthetic run.', scope_kind='specified_runs', assumptions=['Named input.'],
        not_implied=['No algorithm exists.'], lesson='Distinguish execution from mathematics.',
        next_discriminating_test='Change the implementation while retaining the input.',
        revisit_when='A new implementation is available.',
        support=[dict(source='fixture', path='result.json', sha256=sha, provenance='internal')],
        artifact_assertions=[dict(source='fixture', path='result.json', pointer=['value'], expected=3)],
        depends_on=[], supersedes=[], contradicts=[],
        formal_verification=dict(status='not_formalized', assistant='Lean',
                                 checked_theorem=None, kernel_receipt=None, axiom_audit=None),
        review=dict(register_author='test', independent_agent_review=False, official_ledger_imported=False),
        broad_direction_closed=False)


@pytest.fixture
def registry(tmp_path):
    root = tmp_path / 'register'
    inputs = tmp_path / 'authorized-inputs'
    inputs.mkdir()
    (inputs / 'result.json').write_text(json.dumps({'value': 3}))
    for name in ('claims', 'leads'):
        (root / name).mkdir(parents=True)
    q = sample_claim(digest(inputs / 'result.json'))
    (root / 'claims' / (q['id'] + '.json')).write_text(json.dumps(q))
    (root / 'sources.json').write_text(json.dumps({'roots': {}, 'archives': []}))
    (root / 'relations.json').write_text(json.dumps({'edges': []}))
    for number in range(1, 11):
        lead = dict(lead=number, research_question_status='open', exhausted=False,
                    official_status_changed=False,
                    claim_ids_at_initial_import=[q['id']] if number == 1 else [])
        (root / 'leads' / f'L{number:02d}.json').write_text(json.dumps(lead))
    return root, inputs, q


def test_portable_structural_check_reports_no_artifact_verification(registry):
    root, _, _ = registry
    result = Register(root).check()
    assert result['artifacts_checked'] is False
    assert result['scientific_truth_newly_certified'] is False
    assert result['unique_bound_artifacts'] == 0


def test_missing_private_access_is_a_diagnostic(registry):
    root, _, _ = registry
    with pytest.raises(EvidenceError, match='Missing access is not negative scientific evidence'):
        Register(root).check(artifacts=True)


def test_explicit_roots_verify_hash_and_recorded_value(registry):
    root, inputs, _ = registry
    result = Register(root, {'fixture': inputs}).check(artifacts=True)
    assert result['unique_bound_artifacts'] == result['artifact_value_assertions'] == 1


def test_changed_artifact_is_rejected(registry):
    root, inputs, _ = registry
    (inputs / 'result.json').write_text(json.dumps({'value': 4}))
    with pytest.raises(EvidenceError, match='Artifact changed'):
        Register(root, {'fixture': inputs}).check(artifacts=True)


def test_bool_does_not_match_integer_assertion(registry):
    root, inputs, q = registry
    (inputs / 'result.json').write_text(json.dumps({'value': True}))
    q['support'][0]['sha256'] = digest(inputs / 'result.json')
    q['artifact_assertions'][0]['expected'] = 1
    with pytest.raises(EvidenceError, match='Recorded value differs'):
        Register(root, {'fixture': inputs}).check_artifacts([q])


def test_assertion_must_use_bound_artifact(registry):
    root, inputs, q = registry
    q['artifact_assertions'][0]['path'] = 'unbound.json'
    with pytest.raises(EvidenceError, match='bound artifact'):
        Register(root, {'fixture': inputs}).check_artifacts([q])


@pytest.mark.parametrize('mutation', ['scope', 'closure', 'lean', 'id', 'path'])
def test_false_promotions_and_escaping_paths_are_rejected(registry, mutation):
    _, _, q = registry
    if mutation == 'scope':
        q['scope'] = ''
    elif mutation == 'closure':
        q['broad_direction_closed'] = True
    elif mutation == 'lean':
        q['formal_verification'].update(status='checked', kernel_receipt='trust me')
    elif mutation == 'id':
        q['id'] = '../../elsewhere'
    else:
        q['support'][0]['path'] = '../../elsewhere'
    with pytest.raises(EvidenceError):
        validate_record(q)


def test_symlink_cannot_escape_authorized_root(registry, tmp_path):
    root, inputs, q = registry
    target = tmp_path / 'other.json'
    target.write_text('{}')
    (inputs / 'outside.json').symlink_to(target)
    q['support'][0].update(path='outside.json', sha256=digest(target))
    with pytest.raises(EvidenceError, match='escapes source root'):
        Register(root, {'fixture': inputs}).check_artifacts([q])


@pytest.mark.parametrize('dependency', ['self', 'missing'])
def test_invalid_dependency_graph_rejected(registry, dependency):
    _, _, q = registry
    q['depends_on'] = [q['id'] if dependency == 'self' else 'C-000000000999']
    with pytest.raises(EvidenceError):
        validate_graph([q])


def test_concurrent_append_publishes_one_complete_record(registry):
    root, inputs, q = registry
    q['id'] = 'C-000000000002'
    register = Register(root, {'fixture': inputs})

    def append():
        try:
            register.append(q)
            return True
        except (EvidenceError, FileExistsError):
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: append(), range(2)))
    assert sum(outcomes) == 1
    assert json.loads((root / 'claims' / (q['id'] + '.json')).read_text()) == q
    assert not list((root / 'claims').glob('.pending-*'))


def test_invalid_append_leaves_no_record(registry):
    root, inputs, q = registry
    q['id'] = 'C-000000000002'
    q['support'][0]['sha256'] = '0' * 64
    with pytest.raises(EvidenceError):
        Register(root, {'fixture': inputs}).append(q)
    assert len(list((root / 'claims').glob('C-*.json'))) == 1


def test_python_optimization_cannot_disable_validation(registry):
    root, _, q = registry
    q['broad_direction_closed'] = True
    (root / 'claims' / (q['id'] + '.json')).write_text(json.dumps(q))
    command = [sys.executable, '-O', str(Path(__file__).resolve().parents[1] / 'tools/scoped_evidence.py'),
               '--register', str(root), 'check']
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 2
    assert 'cannot close a direction' in result.stderr


def test_checked_in_records_preserve_imported_bytes():
    manifest = json.loads((DEFAULT_ROOT / 'provenance/shared-register-import.json').read_text())
    for relative, expected in manifest['record_files_preserved_byte_for_byte'].items():
        assert digest(DEFAULT_ROOT / relative) == expected, relative
    result = Register().check()
    assert result['claims'] == 19
    assert result['leads'] == 10
    assert result['lean_verified_claims'] == 0


def test_json_schema_agrees_with_imported_records():
    import jsonschema
    schema = json.loads((DEFAULT_ROOT / 'claim.schema.json').read_text())
    for q in Register().load():
        jsonschema.Draft202012Validator(schema).validate(q)
