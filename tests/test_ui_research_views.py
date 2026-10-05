"""Reader-only contracts: real pinned data, conservative gaps and static/local parity."""
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest

from ui import curves, comparisons, payloads, provenance
from ui.build import build
from ui.index import ResearchIndex, Record

ROOT = Path(__file__).resolve().parents[1]


def copy_data(repo):
    (repo / 'ui').mkdir(parents=True, exist_ok=True)
    for directory in ('curves', 'benchmarks'):
        shutil.copytree(ROOT / 'ui' / directory, repo / 'ui' / directory)
    shutil.copy(ROOT / 'ui/receipts.json', repo / 'ui/receipts.json')


def pin(path, repo):
    return {'path': path.relative_to(repo).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def test_real_curves_have_exact_ids_and_sourced_traits():
    data = curves.payload(ROOT)
    assert not data['errors']
    assert len(data['curves']) == 2
    assert {r['field']['degree'] for r in data['curves']} == {13, 19}
    for row in data['curves']:
        assert len(row['traits']) == 12
        assert row['traits']['j_invariant']['value'] is None
        for trait in row['traits'].values():
            assert (trait['value'] is None) == (trait['status'] == 'unknown')
            if trait['value'] is not None:
                assert trait['source']['commit'] in trait['source']['url']


@pytest.mark.parametrize('change', ['identity', 'path', 'pin', 'source', 'nan'])
def test_invalid_curve_catalog_fails_closed(tmp_path, change):
    copy_data(tmp_path)
    p = tmp_path / 'ui/curves/binary13.json'
    data = json.loads(p.read_text())
    catalog_path = tmp_path / 'ui/curves/catalog.json'
    catalog = json.loads(catalog_path.read_text())
    if change == 'identity':
        data['curve']['generator'] = [1, 2]
    if change == 'source':
        data['source']['path'] = '../private'
    if change == 'nan':
        data['endomorphism']['cm_discriminant'] = float('nan')
    p.write_text(json.dumps(data))
    catalog['capsules'][0] = pin(p, tmp_path)
    if change == 'path':
        catalog['capsules'][0]['path'] = '../outside.json'
    if change == 'pin':
        catalog['capsules'][0]['sha256'] = '0' * 64
    catalog_path.write_text(json.dumps(catalog))
    out = curves.payload(tmp_path)
    assert out['curves'] == [] and out['errors']


def test_same_uid_deduplicates_but_conflicting_traits_refused(tmp_path):
    copy_data(tmp_path)
    p = tmp_path / 'ui/curves/binary13.json'
    duplicate = p.with_name('duplicate.json')
    duplicate.write_bytes(p.read_bytes())
    catalog_path = p.parent / 'catalog.json'
    catalog = json.loads(catalog_path.read_text())
    catalog['capsules'].append(pin(duplicate, tmp_path))
    catalog_path.write_text(json.dumps(catalog))
    assert len(curves.payload(tmp_path)['curves']) == 2
    data = json.loads(duplicate.read_text()); data['endomorphism']['cm_discriminant'] = -3
    duplicate.write_text(json.dumps(data)); catalog['capsules'][-1] = pin(duplicate, tmp_path)
    data = json.loads(p.read_text()); data['endomorphism']['cm_discriminant'] = -7
    p.write_text(json.dumps(data)); catalog['capsules'][0] = pin(p, tmp_path)
    catalog_path.write_text(json.dumps(catalog))
    assert curves.payload(tmp_path)['errors']


def test_real_comparison_package_registers_all_rows():
    out = comparisons.payload(ROOT)
    assert not out['errors'] and len(out['receipts']) == 9
    for row in out['receipts']:
        assert not row['fixture'] and row['package_schema'] == 'comparison-package/1'
        assert row['environment'] is None and row['excluded_costs'] is None
        assert row['workload_sha256'] and row['curve_uid']
        assert all('/blob/' in s['url'] for s in row['sources'].values())


def test_package_retains_failure_zero_and_unknown(tmp_path):
    copy_data(tmp_path)
    p = tmp_path / 'ui/benchmarks/cryptanalysis-primary.json'
    data = json.loads(p.read_text())
    data['rows'][0].update(status='timeout', verification='unknown', wall_ns=0, ic_online_ns=0, rho_online_ns=None)
    p.write_text(json.dumps(data))
    catalog_path = tmp_path / 'ui/receipts.json'
    catalog = json.loads(catalog_path.read_text())
    for row in catalog['receipts']:
        row['snapshot'] = pin(p, tmp_path)
    catalog_path.write_text(json.dumps(catalog))
    row = comparisons.payload(tmp_path)['receipts'][0]
    assert row['status'] == 'timeout' and not row['complete']
    assert row['metrics']['total_wall_seconds'] == 0
    assert row['metrics']['ic_online_ns'] == 0 and row['metrics']['rho_online_ns'] is None


def test_package_missing_row_is_visible_error(tmp_path):
    copy_data(tmp_path)
    p = tmp_path / 'ui/receipts.json'
    data = json.loads(p.read_text()); data['receipts'][0]['row_id'] = 'nonexistent'
    p.write_text(json.dumps(data))
    out = comparisons.payload(tmp_path)
    assert len(out['receipts']) == 8 and out['errors'][0]['id'] == 'primary-1'


def trail_fixture():
    exp = SimpleNamespace(record_id='EXP-UI-001', title='UI fixture', path='experiments/EXP-UI-001/specification.yaml',
                          status='completed', dated='2026-10-01', contract='specification.yaml',
                          runs=[{'id':'RUN-UI-001', 'status':'incomplete', 'path':'experiments/EXP-UI-001/runs/RUN-UI-001', 'finished':''}])
    def record(id, kind, refs):
        return Record(id,kind,'ledger/record.yaml',None,id,'recorded','2026-10-02',None,{},frozenset(refs))
    records = {'EV-UI-001':record('EV-UI-001','EV',{'RUN-UI-001'}),
               'DEC-UI-001':record('DEC-UI-001','DEC',{'EV-UI-001'}),
               'KN-FIND-001':record('KN-FIND-001','KN',{'DEC-UI-001'}),
               'EV-UI-002':record('EV-UI-002','EV',{'H-UI-001'})}
    backlinks = {'RUN-UI-001':{'EV-UI-001'},'EV-UI-001':{'DEC-UI-001'},'DEC-UI-001':{'KN-FIND-001'},'H-UI-001':{'EV-UI-002'}}
    return SimpleNamespace(experiments=[exp], records=records, backlinks=backlinks), exp


def test_trail_joins_citations_without_claiming_archival():
    index, exp = trail_fixture()
    row = provenance.experiment_trail(index,exp)
    assert {e['id'] for e in row['events']} == {'EXP-UI-001','RUN-UI-001','EV-UI-001','DEC-UI-001','KN-FIND-001'}
    assert row['gaps'] == ['incomplete_or_failed_run']
    assert row['archive_state'] == 'unknown'
    exp.status = 'archived'; exp.runs[0]['status'] = 'completed'
    row = provenance.experiment_trail(index, exp)
    assert row['archive_state'] == 'declared_archived' and row['gaps'] == []


def test_missing_manifest_and_citations_stay_unknown():
    index, exp = trail_fixture(); index.backlinks = {}; exp.runs[0]['status'] = 'no-manifest'
    row = provenance.experiment_trail(index, exp)
    assert set(row['gaps']) == {'missing_or_unreadable_manifest','no_linked_evidence','no_linked_decision'}
    assert row['archive_state'] == 'unknown'
    assert provenance.payload(index)['needs_follow_up'] == 1


def test_static_payload_parity_and_determinism(tmp_path, monkeypatch):
    monkeypatch.delenv('AWS_ACCESS_KEY_ID', raising=False)
    repo, out = tmp_path/'repo', tmp_path/'site'
    copy_data(repo)
    build(repo, out, verbose=False)
    index = ResearchIndex(repo).build()
    for name, fn in [('curves',payloads.curves_payload),('provenance',payloads.provenance_payload),('comparisons',payloads.comparisons_payload)]:
        expected = fn(index)
        assert json.loads((out/f'data/{name}.json').read_text()) == expected
        assert fn(index) == expected


def test_large_curve_integers_are_lossless_display_values():
    from ui.curves import exact_json
    assert exact_json({'p': 2**256 - 189, 'small': 181, 'points': [2**100, 0]}) == {
        'p': str(2**256 - 189), 'small': 181, 'points': [str(2**100), 0]}


def test_http_and_static_routes_agree(tmp_path, monkeypatch):
    from http.server import ThreadingHTTPServer
    import threading
    from urllib.request import urlopen
    from ui.server import Handler, IndexHolder
    monkeypatch.delenv('AWS_ACCESS_KEY_ID', raising=False)
    repo, out = tmp_path/'repo', tmp_path/'site'
    copy_data(repo)
    build(repo, out, verbose=False)
    holder = IndexHolder(repo)
    holder.index = ResearchIndex(repo).build()
    holder.state = 'ready'
    server = ThreadingHTTPServer(('127.0.0.1', 0), type('TestHandler', (Handler,), {'holder':holder}))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        for name in ('curves', 'provenance', 'comparisons'):
            with urlopen(f'http://127.0.0.1:{server.server_port}/data/{name}.json') as response:
                assert json.load(response) == json.loads((out/f'data/{name}.json').read_text())
    finally:
        server.shutdown(); server.server_close(); thread.join()
