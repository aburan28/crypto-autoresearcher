"""Source-pin custody controls with real independent temporary Git checkouts."""
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('dependency_pins', ROOT / 'tools/check_lean_dependency_pins.py')
PINS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PINS)


def command(path, *args):
    return subprocess.check_output(
        ['git', '-C', str(path), '-c', 'user.name=Fixture', '-c',
         'user.email=fixture@example.invalid', *args], text=True).strip()


@pytest.fixture
def dependency(tmp_path):
    installed = tmp_path / '.lake/packages/example'
    installed.mkdir(parents=True)
    command(installed, 'init', '-q')
    (installed / 'Example.lean').write_text('theorem fixture : True := trivial\n')
    (installed / '.gitignore').write_text('.lake/\n')
    command(installed, 'add', '.')
    command(installed, 'commit', '-qm', 'original source')
    revision = command(installed, 'rev-parse', 'HEAD')
    manifest = {'packagesDir': '.lake/packages', 'packages': [
        {'type': 'git', 'name': 'example', 'rev': revision}]}
    (tmp_path / 'lake-manifest.json').write_text(json.dumps(manifest))
    return tmp_path, installed, manifest


def test_exact_clean_revision_with_ignored_build_files_passes(dependency):
    workspace, installed, _ = dependency
    (installed / '.lake').mkdir()
    (installed / '.lake/Example.olean').write_bytes(b'ignored build output')
    result = PINS.audit(workspace)
    assert result['passed'] and len(result['dependencies']) == 1
    assert result['dependencies'][0]['clean_sources']
    assert result['binary_or_independent_kernel_recheck'] is False


@pytest.mark.parametrize('change', ['dirty', 'untracked', 'wrong_revision', 'missing'])
def test_changed_missing_or_wrong_dependency_is_rejected(dependency, change):
    workspace, installed, _ = dependency
    if change == 'missing':
        installed.rename(installed.with_name('elsewhere'))
    elif change == 'untracked':
        (installed / 'Injected.lean').write_text('axiom injected : False\n')
    else:
        (installed / 'Example.lean').write_text('changed source\n')
        if change == 'wrong_revision':
            command(installed, 'add', '.')
            command(installed, 'commit', '-qm', 'different revision')
    with pytest.raises(ValueError):
        PINS.audit(workspace)


@pytest.mark.parametrize('change', ['moving_revision', 'duplicate', 'escaping_path', 'empty'])
def test_invalid_or_unpinned_manifest_is_rejected(dependency, change):
    workspace, _, manifest = dependency
    if change == 'moving_revision':
        manifest['packages'][0]['rev'] = 'main'
    elif change == 'duplicate':
        manifest['packages'].append(manifest['packages'][0].copy())
    elif change == 'empty':
        manifest['packages'] = []
    else:
        manifest['packagesDir'] = '../../outside'
    (workspace / 'lake-manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        PINS.audit(workspace)
