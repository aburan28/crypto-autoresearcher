"""Reader-only contracts: real pinned data, conservative gaps and static/local parity."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest

from ui import curves, comparisons, crypto_traits, payloads, provenance
from ui.build import build
from ui.index import ResearchIndex, Record

ROOT = Path(__file__).resolve().parents[1]
CRYPTO_COMMIT = 'd22253655de460de5fbf4774959c97d8a03de682'
# DiSSECT outputs whose pinned definition is exactly a crypto curve_traits value.
SAME_QUANTITY_SLOTS = {
    'dissect.cofactor.order', 'dissect.cofactor.cofactor', 'dissect.embedding.complement_bit_length',
    'dissect.discriminant.cm_disc', 'dissect.discriminant.factorization', 'dissect.discriminant.max_conductor',
}


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
    assert len(data['curves']) == 4
    assert {r['field']['degree'] for r in data['curves']} == {13, 19}
    for row in data['curves']:
        assert len(row['traits']) == 63 + len(crypto_traits.ROWS)
        assert row['traits']['j_invariant']['value'] is None
        for trait in row['traits'].values():
            assert (trait['value'] is None) == (trait['status'] == 'unknown')
            if trait['value'] is not None:
                assert trait['source']['commit'] in trait['source']['url']


def test_dissect_registry_covers_all_pinned_families_without_claiming_results():
    data = curves.payload(ROOT)
    registry = data['trait_registry']
    expected = {
        'brainpool_overlap': 1, 'class_number': 2, 'cofactor': 2,
        'conductor': 2, 'discriminant': 3, 'division_polynomials': 2,
        'embedding': 2, 'hamming_x': 3, 'isogeny_extension': 3,
        'isogeny_neighbors': 1, 'kn_factorization': 4, 'multiples_x': 4,
        'pow_distance': 4, 'q_torsion': 1, 'small_prime_order': 2,
        'square_4p1': 2, 'torsion_extension': 3, 'trace_factorization': 3,
        'twist_order': 2, 'volcano': 2, 'weierstrass': 2, 'x962_invariant': 1,
    }
    assert {f['key']: len(f['outputs']) for f in registry['families']} == expected
    keys = {f"dissect.{f['key']}.{o['key']}" for f in registry['families'] for o in f['outputs']}
    assert len(keys) == 51
    for row in data['curves']:
        assert {k for k in row['traits'] if k.startswith('dissect.')} == keys
        filled = SAME_QUANTITY_SLOTS if 'crypto_traits' in row else set()
        for key in keys:
            trait = row['traits'][key]
            assert registry['upstream_commit'] in trait['definition']['url']
            if key in filled:
                assert trait['status'] == 'source_reported' and trait['evidence_status'] == 'proved'
                assert trait['source']['path'] == 'docs/curves/traits.json' and trait['mapping']
                continue
            assert trait['value'] is None and trait['status'] == 'unknown'
            assert trait['source'] is None  # a definition is not result provenance
        assert row['traits']['dissect.volcano.depth']['parameters'] == {'l': [2, 3, 5, 7, 11, 13, 17, 19]}
        assert row['traits']['dissect.twist_order.twist_cardinality']['parameters'] == {'deg': [1, 2]}
        # Similar names do not justify mapping binary model coefficients or
        # endomorphism-order conductors into unrelated DiSSECT outputs.
        assert row['traits']['dissect.weierstrass.a']['value'] is None
        assert row['traits']['dissect.conductor.ratio_sqrt']['value'] is None


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
    assert len(curves.payload(tmp_path)['curves']) == 4
    data = json.loads(duplicate.read_text()); data['endomorphism']['cm_discriminant'] = -3
    duplicate.write_text(json.dumps(data)); catalog['capsules'][-1] = pin(duplicate, tmp_path)
    data = json.loads(p.read_text()); data['endomorphism']['cm_discriminant'] = -7
    p.write_text(json.dumps(data)); catalog['capsules'][0] = pin(p, tmp_path)
    catalog_path.write_text(json.dumps(catalog))
    assert curves.payload(tmp_path)['errors']


def by_id(data):
    return {r['curve_id']: r for r in data['curves']}


def test_crypto_traits_fill_only_same_quantities_with_status():
    rows = by_id(curves.payload(ROOT))
    k13 = rows['EC1N13Ce0h1dfa32cdf623']['traits']
    assert rows['EC1N13Ce0h1dfa32cdf623']['crypto_traits']['slug'] == 'icv1-f2m13-t181-515ee569'
    expected = {'dissect.discriminant.cm_disc': -7, 'dissect.discriminant.factorization': [7],
                'dissect.discriminant.max_conductor': 1, 'dissect.cofactor.order': 2003,
                'dissect.cofactor.cofactor': 4, 'dissect.embedding.complement_bit_length': 7,
                'cm_discriminant': -7, 'endomorphism_order_conductor': 1, 'order': 8012, 'trace': 181}
    for key, value in expected.items():
        assert k13[key]['value'] == value and k13[key]['evidence_status'] == 'proved', key
        assert CRYPTO_COMMIT in k13[key]['source']['url']
    k19 = rows['EC1N19Ce0h1e2a8f558313']['traits']
    assert k19['dissect.discriminant.factorization']['value'] == [7, 457, 457]
    assert k19['dissect.discriminant.max_conductor']['value'] == 457
    # Supplementary rows keep crypto's own names and statuses.
    assert k13['crypto.frobenius.class_number']['value'] == 1
    assert k13['crypto.frobenius.class_number']['evidence_status'] == 'proved'
    assert k13['crypto.twist.order']['value'] == '8374'
    assert k13['crypto.small_primes']['evidence_status'] is None and k13['crypto.small_primes']['note']
    assert 'TRAITS.md' in k13['crypto.frobenius.conductor']['definition']['url']
    # Similar labels stay unknown: class-number bounds, extension conductor
    # ratios, parameterized families and values that would need arithmetic.
    for key in ('dissect.class_number.upper', 'dissect.class_number.lower', 'dissect.conductor.ratio_sqrt',
                'dissect.conductor.factorization', 'dissect.twist_order.twist_cardinality',
                'dissect.volcano.depth', 'dissect.trace_factorization.trace', 'dissect.weierstrass.a',
                'dissect.embedding.embedding_degree_complement', 'j_invariant'):
        assert k13[key]['value'] is None and k13[key]['status'] == 'unknown', key


def test_other_representations_of_the_same_curve_get_no_crypto_traits():
    # binary13 is the degree-13 Koblitz curve under another modulus and generator:
    # a different record, so nothing joins and nothing is aliased by order or degree.
    row = by_id(curves.payload(ROOT))['EC1N13Ckb1h0f132ba0b5e2']
    assert 'crypto_traits' not in row
    for key, trait in row['traits'].items():
        if key.startswith('crypto.'):
            assert trait['value'] is None and trait['evidence_status'] is None and trait['source'] is None
    assert row['traits']['dissect.discriminant.cm_disc']['value'] is None
    assert row['traits']['cm_discriminant']['value'] is None


def edit_snapshot(repo, change):
    path = repo / 'ui/curves/crypto-traits.json'
    snap = json.loads(path.read_text())
    change(snap)
    path.write_text(json.dumps(snap))
    catalog_path = repo / 'ui/curves/catalog.json'
    catalog = json.loads(catalog_path.read_text())
    catalog['supplementary_traits'][0] = {'adapter': 'crypto-curve-traits/1', **pin(path, repo)}
    catalog_path.write_text(json.dumps(catalog))


def other_commit(s):
    s['sources']['definitions']['commit'] = '0' * 40


def duplicate_uid(s):
    s['records'][1]['representations'].append(s['records'][0]['representations'][0])


def wrong_alias(s):
    s['records'][0]['representations'][0]['ec1'] = 'EC1N13Ce0h000000000000'


def wrong_field(s):
    s['records'][0]['representations'][0]['field_sha256'] = '0' * 64


def subgroup_conflict(s):
    s['records'][0]['traits']['subgroup']['order'] = '2011'


def bad_status(s):
    s['records'][0]['traits']['frobenius']['status'] = 'certain'


@pytest.mark.parametrize('change', [
    lambda s: s.update(registry_sha256='0' * 64), other_commit, duplicate_uid,
    wrong_alias, wrong_field, subgroup_conflict, bad_status, lambda s: s.update(adapter='other/1'),
])
def test_crypto_traits_identity_and_pin_conflicts_fail_closed(tmp_path, change):
    copy_data(tmp_path)
    edit_snapshot(tmp_path, change)
    out = curves.payload(tmp_path)
    assert out['curves'] == [] and out['errors']


@pytest.mark.parametrize('field', ['sha256', 'adapter', 'path'])
def test_crypto_traits_catalog_pin_mismatch_fails_closed(tmp_path, field):
    copy_data(tmp_path)
    catalog_path = tmp_path / 'ui/curves/catalog.json'
    catalog = json.loads(catalog_path.read_text())
    catalog['supplementary_traits'][0][field] = {
        'sha256': '0' * 64, 'adapter': 'crypto-curve-traits/2', 'path': '../crypto-traits.json'}[field]
    catalog_path.write_text(json.dumps(catalog))
    out = curves.payload(tmp_path)
    assert out['curves'] == [] and out['errors']


def test_crypto_traits_snapshot_re_derives_from_pinned_crypto_commit():
    crypto = Path(os.environ.get('CRYPTO_CHECKOUT', ROOT.parent / 'crypto'))
    probe = subprocess.run(['git', '-C', str(crypto), 'cat-file', '-e', f'{CRYPTO_COMMIT}^{{commit}}'],
                           capture_output=True)
    if probe.returncode:
        pytest.skip('no aburan28/crypto checkout containing the pinned commit')
    from tools import export_crypto_curve_traits
    assert export_crypto_curve_traits.main(['--crypto', str(crypto), '--commit', CRYPTO_COMMIT, '--check']) == 0


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
