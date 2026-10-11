import hashlib
import json
from pathlib import Path

from ui import benchmarks, payloads
from ui.index import ResearchIndex

ROOT = Path(__file__).resolve().parents[1]


def copy_snapshot(tmp_path, mutate=None):
    data = json.loads((ROOT / 'ui/benchmarks/cryptanalysis-primary.json').read_text())
    if mutate:
        mutate(data)
    path = tmp_path / 'ui/benchmarks/sample.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(data))
    (path.parent / 'catalog.json').write_text(json.dumps({'path': 'ui/benchmarks/sample.json', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}))
    return path


def test_real_archive_hashes_and_shared_payload(tmp_path):
    copy_snapshot(tmp_path)
    result = benchmarks.payload(tmp_path)
    assert len(result['rows']) == 9
    assert len(result['identities']) == 1
    assert result['rows'][0]['curve_id'] == 'EC1N13Ckb1h0f132ba0b5e2'
    assert payloads.comparisons_payload(ResearchIndex(tmp_path))['benchmarks'] == result


def test_pin_corruption_refuses_rows(tmp_path):
    path = copy_snapshot(tmp_path)
    path.write_text(path.read_text() + ' ')
    assert benchmarks.payload(tmp_path)['error']


def test_alias_collision_refuses_rows(tmp_path):
    copy_snapshot(tmp_path, lambda d: next(iter(d['identities'].values()))['curve'].update(generator=[1,2]))
    assert benchmarks.payload(tmp_path)['error']


def test_external_link_injection_refused(tmp_path):
    copy_snapshot(tmp_path, lambda d: next(iter(d['sources'].values())).update(url='javascript:alert(1)'))
    assert benchmarks.payload(tmp_path)['error']


def test_failed_rows_zero_and_missing_survive(tmp_path):
    copy_snapshot(tmp_path, lambda d: d['rows'][0].update(status='timeout', verification='unknown', ic_online_ns=0, rho_online_ns=None))
    row = benchmarks.payload(tmp_path)['rows'][0]
    assert row['status'] == 'timeout' and row['ic_online_ns'] == 0 and row['rho_online_ns'] is None


def test_static_builder_uses_same_benchmark_rows(tmp_path):
    from ui.build import build
    repo = tmp_path / 'repo'
    copy_snapshot(repo)
    out = tmp_path / 'site'
    build(repo, out, verbose=False)
    built = json.loads((out / 'data/comparisons.json').read_text())['benchmarks']
    assert built == benchmarks.payload(repo)
