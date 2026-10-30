"""Source bindings and failed imports preserve the parent and refuse partial output."""
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

import pytest
import database as D


def parent(path):
    c=sqlite3.connect(path)
    c.executescript('''
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);
CREATE TABLE sources(path TEXT PRIMARY KEY,sha256 TEXT,bytes INTEGER,kind TEXT);
CREATE TABLE curves(curve_uid TEXT PRIMARY KEY,b TEXT);
CREATE TABLE bases(base_sha256 TEXT PRIMARY KEY,curve_uid TEXT,fixture_uid TEXT);
CREATE TABLE executions(execution_id TEXT PRIMARY KEY,source_commit TEXT,protocol_sha256 TEXT,physical_executions INTEGER,wall_valid INTEGER,resource_json TEXT,export_path TEXT);
CREATE TABLE equations(x TEXT); CREATE TABLE cover_frames(x TEXT);
CREATE TABLE cover_sources(base_sha256 TEXT,public_scalar TEXT,x TEXT,y TEXT);
''')
    c.execute('INSERT INTO metadata VALUES (?,?)',('schema',D.encode('prime-field-database/v2')))
    c.execute('INSERT INTO curves VALUES (?,?)',('marked-control-curve','3'))
    c.execute('INSERT INTO bases VALUES (?,?,?)',('marked-control-base','marked-control-curve','fixture'))
    c.commit();c.close()


def fixture(tmp_path,monkeypatch):
    monkeypatch.setattr(D,'ROOT',Path('/'))
    base=tmp_path/'parent.sqlite';parent(base)
    run=tmp_path/'run';run.mkdir();raw=run/'raw';raw.mkdir()
    inputs=tmp_path/'inputs.json';inputs.write_text(json.dumps(dict(cells=[dict(id='synthetic',shift=2,active_atoms=[0],fixture=dict(uid='fixture',ec1=dict(curve_uid='marked-control-curve'),r=7))])))
    summaries=[]
    for arm in ('baseline','shifted'):
        value=dict(inputs_sha256=D.digest(inputs),curve_uid='fixture',active_atoms=[0],projection=dict(U=1,native_to_projected=[['unknown',0,1]]),old_kernel=[[1]],kernel=[],rows=[dict(coefficients=[1],source_scalar=3)],old_kernel_syndromes=[[1]])
        (raw/('synthetic-'+arm+'.json')).write_text(json.dumps(value))
        summaries.append(dict(cell_id='synthetic',arm=arm,status='verified',attempts=1,witnesses=1,unique_equations=1,new_rank=1,preprocessing_rank=0,combined_rank=1,rank_gain=1))
    (run/'analysis.json').write_text(json.dumps(dict(cells=summaries)))
    (run/'execution.json').write_text(json.dumps(dict(source_commit='marked-software-control')))
    files=[dict(path=str(p.relative_to(run)),bytes=p.stat().st_size,sha256=D.digest(p)) for p in sorted(run.rglob('*.json'))]
    (run/'export.json').write_text(json.dumps(dict(schema='experiment.export/v1',protocol=dict(sha256='marked-control'),files=files)))
    return base,run,inputs


def test_parent_preserved_and_exact_bound_rows_imported(tmp_path,monkeypatch):
    base,run,inputs=fixture(tmp_path,monkeypatch);before=sha256(base.read_bytes()).hexdigest();out=tmp_path/'derived.sqlite'
    counts=D.build(base,run,inputs,None,None,out)
    assert counts['executions']==1 and counts['subset_cells']==counts['subset_rows']==2
    assert sha256(base.read_bytes()).hexdigest()==before
    with sqlite3.connect(out) as c:
        assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
        assert c.execute('SELECT coefficients_json,rhs FROM subset_rows').fetchall()==[('[1]','3')]*2
        assert c.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()==('"prime-field-database/v3"',)
    with pytest.raises(ValueError,match='fresh'):D.build(base,run,inputs,None,None,out)


def test_corrupt_bound_source_refuses_import_without_partial_database(tmp_path,monkeypatch):
    base,run,inputs=fixture(tmp_path,monkeypatch);before=base.read_bytes();out=tmp_path/'must-not-survive.sqlite'
    with (run/'raw/synthetic-shifted.json').open('a') as stream:stream.write(' ')
    with pytest.raises(ValueError,match='file mismatch'):D.build(base,run,inputs,None,None,out)
    assert not out.exists() and base.read_bytes()==before


def test_wrong_parent_schema_refuses_without_output(tmp_path,monkeypatch):
    base,run,inputs=fixture(tmp_path,monkeypatch);out=tmp_path/'must-not-survive.sqlite'
    with sqlite3.connect(base) as c:c.execute("UPDATE metadata SET value='\"prime-field-database/v3\"' WHERE key='schema'")
    with pytest.raises(ValueError,match='v2 parent'):D.build(base,run,inputs,None,None,out)
    assert not out.exists()
