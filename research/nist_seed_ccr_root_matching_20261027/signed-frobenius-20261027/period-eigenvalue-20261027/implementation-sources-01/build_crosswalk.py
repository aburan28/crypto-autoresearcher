"""Map recovered Ma94 passages to retained evidence; no new curve trial."""
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[4]
G = ROOT / 'research/nist_seed_ccr_root_matching_20261027'
INPUTS = {
    'cohort': G / 'signed-frobenius-20261027/prior-rows.json',
    'fibers': ROOT / 'research/nist_seed_modular_coordinate_guards_20261027/FIBER-AUDIT.json',
    'fiber_bundle': ROOT / 'research/nist_seed_modular_coordinate_guards_20261027/BUNDLE.json',
    'matching': G / 'y-coordinate-matching-20261027/AUDIT.json',
    'matching_bundle': G / 'y-coordinate-matching-20261027/BUNDLE-REPLAY.json',
    'cm': P.parent / 'RESULT.json',
    'cm_bundle': P.parent / 'BUNDLE.json',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def derive():
    a = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    rows, fibers, cm, matching = a['cohort'], a['fibers'], a['cm'], a['matching']
    assert sha(INPUTS['cohort']) == 'e8d6a874e3dc77970c88957f4bca075a0cc7a431dd8bcb25e5c5d7bcba6eeb0f'
    assert len(rows) == 21 and len({r['curve_uid'] for r in rows}) == 21
    assert collections.Counter(r['label'] for r in rows) == {'omitted': 11, 'published': 10}
    assert len({r['timestamp'] for r in rows}) == 6
    assert fibers['status'] == cm['status'] == matching['status'] == 'PASS'
    assert fibers['cohort_cells'] == 1281 and fibers['cohort_fibers'] == 2071
    assert fibers['cohort_nonconstant_gcd_Y'] == 0
    assert fibers['cohort_nonconstant_gcd_X'] == 0
    assert matching['cohort_calls'] == 411 and matching['cohort_first_y_wrong_trace_kernels'] == 0
    assert any(c['status'] == 'EXCEPTION' and c['record']['type'] == 2
               and c['record']['gcd_Y_degree'] > 0 for c in fibers['control_fibers'])
    cells = {(r['index'], r['ell']): r for r in fibers['cells'] if r['index'] < 21}
    assert len(cells) == 1281
    output = []
    for i, r in enumerate(rows):
        rr = [f for f in fibers['rows'] if f['index'] == i]
        cc = [c for (idx, ell), c in cells.items() if idx == i]
        assert len(cc) == 61
        p, b = int(r['p']), int(r['b'])
        J = 1728 * (-108) * pow((-108 + 27*b*b) % p, -1, p) % p
        assert all((int(c['p']), int(c['j'])) == (p, J) for c in cc)
        cr = cm['rows'][i]
        assert (cr['curve_uid'], cr['p'], cr['b'], cr['n']) == (r['curve_uid'], r['p'], r['b'], r['n'])
        assert cr['source_special_route'] is False
        output.append({
            'index': i, 'name': r['name'], 'label': r['label'],
            'stream': r['timestamp'], 'ordinal': r['ordinal'],
            'curve_uid': r['curve_uid'], 'seed_hex': r['seed_hex'],
            'p': r['p'], 'A': '-3', 'b': r['b'], 'n': r['n'], 'j': str(J),
            'levels': len(cc),
            'parameter_roots': sum(len(c['roots']) for c in cc),
            'type1_source_and_fricke_fibers': sum(f['type'] == 1 for f in rr),
            'type2_fibers': sum(f['type'] == 2 for f in rr),
            'repeated_fibers': sum(f['gcd_Y_degree'] > 0 for f in rr),
            'special_CM_route': int(cr['source_special_route']),
        })
    assert sum(r['type2_fibers'] for r in output) == 299
    assert sum(r['type1_source_and_fricke_fibers'] for r in output) == 1772
    stream_summary = []
    for stream in sorted({r['stream'] for r in output}):
        group = [r for r in output if r['stream'] == stream]
        stream_summary.append({
            'stream': stream, 'curves': len(group),
            'published': sum(r['label'] == 'published' for r in group),
            'omitted': sum(r['label'] == 'omitted' for r in group),
            'type2_fibers': sum(r['type2_fibers'] for r in group),
            'repeated_fibers': sum(r['repeated_fibers'] for r in group),
        })
    manifest = {
        'status': 'PASS', 'kind': 'source-to-existing-evidence crosswalk',
        'new_scientific_trials': 0,
        'scope': 'Ma94 p93 repeated-fiber condition crosswalk to all retained later-table fibers; not execution of eco1994 or the 1997 caller.',
        'inputs': {name: {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                          'sha256': sha(path)} for name, path in INPUTS.items()},
        'cohort': {'curves': 21, 'published': 10, 'omitted': 11, 'streams': 6,
                   'cells': 1281, 'parameters': 1185, 'fibers': 2071,
                   'type1_source_and_fricke_fibers': 1772, 'type2_fibers': 299,
                   'repeated_fibers': 0, 'special_CM_routes': 0},
        'positive_fiber_control': next(c for c in fibers['control_fibers']
                                      if c['status'] == 'EXCEPTION' and c['record']['type'] == 2),
        'streams': stream_summary,
        'literal_Ma94_guard': {
            'printed_page': 111, 'initial_KOMB': 1, 'initial_PROD': 2,
            'guard': 'PROD <= 4*sqrt(p) AND KOMB > MAXKOMB',
            'deduction': 'For every integer MAXKOMB>=1, the second conjunct is false at initialization for every curve. Literal pseudocode visits no odd prime; not a selective historical mechanism.',
            'classification': 'documentary inconsistency; no native eco defect asserted',
        },
        'historical_criterion_identified': False,
    }
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(output[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(output)
    return manifest, stream.getvalue()


if __name__ == '__main__':
    manifest, csv_text = derive()
    expected = {'CROSSWALK.json': json.dumps(manifest, indent=2, sort_keys=True)+'\n',
                'cohort-crosswalk.csv': csv_text}
    for name, content in expected.items():
        if '--check' in sys.argv:
            assert (P/name).read_text() == content, name
        else:
            assert not (P/name).exists(), 'Refuse overwrite: '+name
            (P/name).write_text(content)
    print(json.dumps({'status': 'PASS', **manifest['cohort'], 'new_scientific_trials': 0}))
