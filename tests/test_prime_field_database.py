"""Archive import controls: no collector, target sampling or scalar oracle."""
import importlib.util
import json
from pathlib import Path
import sqlite3

import pytest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'research/prime_field_database_20261029'
spec = importlib.util.spec_from_file_location('prime_field_database',HERE/'build.py')
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)
CATALOG = ROOT/'research/prime_field_symmetries_20261029/catalog.json'
FIXTURES = ROOT/'research/prym_factor_base_width_20261025/fixtures.json'


def test_fresh_retained_import_and_explicit_unknown_attempts(tmp_path):
    out = tmp_path/'retained.sqlite'
    counts = database.build(CATALOG,FIXTURES,[],out)
    assert counts['curves'] == counts['bases'] == counts['observations'] == 2
    assert counts['atoms'] == 30 and counts['equations'] == 0
    with sqlite3.connect(out) as connection:
        assert connection.execute('PRAGMA integrity_check').fetchone() == ('ok',)
        assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
        assert connection.execute('SELECT COUNT(*) FROM observations WHERE attempts IS NULL').fetchone() == (2,)
        assert connection.execute('SELECT additional_rank_after_constraints FROM actions').fetchall() == [(0,),(0,)]
        assert connection.execute('SELECT COUNT(*) FROM new_completed_equations').fetchone() == (0,)
        # A full-width field element is stored as exact decimal text, not REAL.
        large = str(2**256-189)
        connection.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)',('marked-software-control',large,'2','3',large,'[0,1]'))
        assert connection.execute('SELECT p,typeof(p) FROM curves WHERE curve_uid=?',('marked-software-control',)).fetchone() == (large,'text')
    with pytest.raises(ValueError,match='fresh'):
        database.build(CATALOG,FIXTURES,[],out)


def test_base_hash_corruption_is_rejected_and_database_removed(tmp_path):
    catalog = json.loads(CATALOG.read_text())
    catalog['retained_bases'][0]['ordered_projected_points'][0][0] += 1
    path = tmp_path/'altered-catalog.json'
    path.write_text(json.dumps(catalog))
    # Source provenance requires an in-repository path; isolate that helper only
    # for this marked filesystem test, without changing its fixture hash check.
    old_root = database.ROOT
    database.ROOT = Path('/')
    catalog['input_sha256'] = {str(FIXTURES.resolve().relative_to(Path('/'))):database.sha256(FIXTURES.read_bytes()).hexdigest()}
    path.write_text(json.dumps(catalog))
    out = tmp_path/'must-be-removed.sqlite'
    try:
        with pytest.raises(ValueError,match='ordered base hash'):
            database.build(path,FIXTURES,[],out)
    finally:
        database.ROOT = old_root
    assert not out.exists()


def test_affine_normalization_preserves_rhs_and_public_anchor_sign():
    row = dict(coefficients=[2,3,4],source_scalar=5)
    projection = dict(U=1,native_to_projected=[['known',6],['unknown',0,-1],['zero']])
    assert database.project(row,projection,7) == ([4],0)
    assert database.normalize([4],0,7) == [1,0]
    assert database.normalize([0],3,7) == [0,1]
    assert database.normalize([0],0,7) == [0,0]
    with pytest.raises(ValueError):
        database.project(dict(coefficients=[1],source_scalar=0),projection,7)


def test_cubic_grouping_preserves_existing_deck_and_negation_orbit():
    from itertools import product
    p = 101
    for coefficients in product((0,1,2),repeat=4):
        key = database.canonical_cubic(coefficients,p)
        for sign,deck in product((1,-1),repeat=2):
            transformed = [sign*c*pow(deck,j,p) % p for j,c in enumerate(coefficients)]
            assert database.canonical_cubic(transformed,p) == key
            for x in (0,1,7,p-1):
                y = sum(c*pow(x,j,p) for j,c in enumerate(coefficients)) % p
                # C's even sextic is unchanged by deck, while negation flips y.
                assert sum(c*pow(deck*x,j,p) for j,c in enumerate(transformed)) % p == sign*y % p
    assert database.canonical_cubic([3],p) == database.canonical_cubic([3,0,0,0],p)
    with pytest.raises(ValueError):database.canonical_cubic([0]*5,p)
    with pytest.raises(ValueError):database.canonical_cubic([1],2)
