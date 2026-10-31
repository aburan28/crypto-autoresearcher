"""Map newly read source conditions to retained observations, without trials."""
import collections
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
OLD = P.parent / 'implementation-sources-01'
ROOT = P.parents[4]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def derive():
    prior = json.loads((OLD/'CROSSWALK.json').read_text())
    for meta in prior['inputs'].values():
        p = ROOT/meta['path']
        assert p.stat().st_size == meta['bytes'] and sha(p) == meta['sha256']
    rows = list(csv.DictReader(io.StringIO((OLD/'cohort-crosswalk.csv').read_text())))
    assert len(rows) == 21 and len({r['curve_uid'] for r in rows}) == 21
    assert collections.Counter(r['label'] for r in rows) == {'omitted': 11, 'published': 10}
    assert len({r['stream'] for r in rows}) == 6
    out = []
    for row in rows:
        p, j, n = (int(row[k]) for k in ['p', 'j', 'n'])
        # These properties were already established in the bound cohort and CM audit.
        assert p > 3 and j not in (0, 1728) and p+1-n != 0
        assert row['special_CM_route'] == row['repeated_fibers'] == '0'
        assert int(row['levels']) == 61
        out.append({**row, 'Le94_p_gt_3': '1', 'Le94_generic_j': '1',
                    'Le94_ordinary': '1', 'special_CM_class': '0',
                    'cube_root_j_requirement_in_documented_interface': '0'})
    o = io.StringIO(newline='')
    w = csv.DictWriter(o, fieldnames=list(out[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(out)
    data = {
        'status': 'PASS', 'kind': 'source-to-retained-evidence crosswalk',
        'new_scientific_trials': 0, 'historical_criterion_identified': False,
        'source': {'title': 'Lehmann 1994 diploma thesis',
                   'sha256': '244fc341ec6785f1b779614d155d71205a967359a46e151f1995ed44bc6339c1',
                   'printed_pages': [21, 23, 24, 57, 59, 62, 66, 85, 86, 92, 94, 119, 120, 121, 122]},
        'imported_crosswalk': {'path': str((OLD/'CROSSWALK.json').relative_to(ROOT)),
                               'sha256': sha(OLD/'CROSSWALK.json')},
        'imported_csv': {'path': str((OLD/'cohort-crosswalk.csv').relative_to(ROOT)),
                         'sha256': sha(OLD/'cohort-crosswalk.csv')},
        'retained_input_bindings': prior['inputs'],
        'cohort': prior['cohort'], 'streams': prior['streams'],
        'documented_curve_precondition_failures': {'omitted': 0, 'published': 0},
        'positive_fiber_control': prior['positive_fiber_control'],
        'limitations': [
            'No execution of original eco, MEQ, LiDIA package or NIST caller.',
            'The existing fiber audit uses later LiDIA coefficient tables and rational parameter roots.',
            'It is not an exhaustive squarefreeness certificate for every polynomial over every extension field.',
            'No proof that the original 1997 program used these tables, methods, defaults or functions.',
            'No new evaluation of arbitrary conductor, endomorphism or transfer criteria.',
        ],
    }
    return data, o.getvalue()


if __name__ == '__main__':
    record, csv_text = derive()
    for name, body in {'CROSSWALK.json': json.dumps(record, indent=2, sort_keys=True)+'\n',
                       'cohort-crosswalk.csv': csv_text}.items():
        if '--check' in sys.argv:
            assert (P/name).read_text() == body
        else:
            assert not (P/name).exists(), 'Refuse overwrite: '+name
            (P/name).write_text(body)
    if '--check' in sys.argv:
        rows = list(csv.DictReader(io.StringIO(gzip.decompress((P/'package-members.csv.gz').read_bytes()).decode())))
        assert len(rows) == 1461
        hashes = json.loads(gzip.decompress((P/'package-file-hashes.json.gz').read_bytes()))
        assert len(hashes) == 1285
        assert {r['name'] for r in rows if r['type'] == '0'} == {r['name'] for r in hashes}
    print(json.dumps({'status': 'PASS', 'curves': 21, 'omitted': 11, 'published': 10,
                      'streams': 6, 'new_scientific_trials': 0,
                      'documented_precondition_failures': 0}))
