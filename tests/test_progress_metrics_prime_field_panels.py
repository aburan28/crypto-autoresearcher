"""Fixed-panel metrics cannot read dirty bytes or count incomplete trials."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess

spec=importlib.util.spec_from_file_location('fixed_panel_metrics',Path(__file__).resolve().parents[1]/'tools/progress_metrics.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)


def test_committed_only_exact_panels_and_invalid_recoveries(tmp_path,monkeypatch):
    def git(*args):
        return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test',
             '-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    path='research/prime_field_d1_execution_20261030/runs/d1-fixed-panel-a91d96/analysis.json'
    target=tmp_path/path;target.parent.mkdir(parents=True)
    data=dict(panel_complete=True,cells=[dict(curve_uid='marked-control-'+str(i//4),target_index=i%4,
         attempts=11,verified=True,status='verified',identified_target=i%2) for i in range(8)])
    def commit(value):
        target.write_text(json.dumps(value));git('add',path);git('commit','-qm','fixture');return git('rev-parse','HEAD')
    def read(ref):
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):M.prime_field_fixed_panels(ref,'2026-10-30')
        return [json.loads(line) for line in stream.getvalue().splitlines()]
    first=commit(data);samples=read(first)
    assert {r['metric'].rsplit('.',1)[-1]:r['value'] for r in samples}==dict(collection_branches=88,verified_cells=8,identified_targets=4)
    assert all(r['source']==path+'@'+first and r['better']=='neutral' for r in samples)
    target.write_text('{}');assert read(first)==samples
    for transform in (lambda d:d.update(panel_complete=False),lambda d:d['cells'][0].update(identified_target=True),
                      lambda d:d['cells'][0].update(attempts=None),lambda d:d['cells'][0].update(verified=False),
                      lambda d:d['cells'].__setitem__(1,copy.deepcopy(d['cells'][0]))):
        bad=copy.deepcopy(data);transform(bad);assert read(commit(bad))==[]
    assert read(first)==samples


def test_residual_metrics_subtract_unknowns_and_charge_shared_stream_once(tmp_path,monkeypatch):
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    path='research/prime_field_a1_execution_20261030/runs/a1-fixed-panel-8e34c5/analysis.json';p=tmp_path/path;p.parent.mkdir(parents=True)
    cells=[dict(cell_id=b,arm=a,verified=True,status='verified',delta=1,direct_base_gain=0,cross_row_cancellation_gain=1,stacked_rank=4,outside_rank=2,base_rank_before=1) for b in ('b13','b16') for a in ('smooth','pool16','pool32')]
    data=dict(panel_complete=True,cells=cells,physical_collection_attempts_observed=4587520,physical_replay_attempts_observed=4587520)
    def commit(value):p.write_text(json.dumps(value));git('add',path);git('commit','-qm','marked-source-control');return git('rev-parse','HEAD')
    def read(ref):
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):M.prime_field_residual_panels(ref,'2026-10-30')
        return [json.loads(line) for line in stream.getvalue().splitlines()]
    first=commit(data);rows=read(first)
    assert len(rows)==9 and next(r['value'] for r in rows if r['metric'].endswith('.collection_branches'))==4587520
    assert all(r['value']==1 for r in rows if r['metric'].endswith('.base_rank_gain'))
    p.write_text('{}');assert read(first)==rows
    bad=copy.deepcopy(data);bad['cells'][0]['delta']=3;assert read(commit(bad))==[]
    bad=copy.deepcopy(data);bad['physical_collection_attempts_observed']*=3;assert read(commit(bad))==[]
