"""Fresh, source-pinned publication generation over completed B2 and D1 exports."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import subprocess

import cancel_targets
import certify_targets
import database

ROOT=Path(__file__).resolve().parents[2]


def info(path):return dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=database.digest(path))


def write(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')


def pack(path,keep_original=False):
    original=info(path)
    if original['bytes']<1048576:return path,dict(original=original,archive=None)
    data=path.read_bytes();archive=Path(str(path)+'.gz')
    with archive.open('xb') as f:f.write(gzip.compress(data,compresslevel=6,mtime=0))
    if gzip.decompress(archive.read_bytes())!=data:raise ValueError('lossless encoding differs')
    record=dict(original=original,archive=info(archive),encoding='gzip level6 mtime0; verified lossless')
    if not keep_original:path.unlink()
    return archive,record


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--b2-run',type=Path,required=True);p.add_argument('--d1-run',type=Path,required=True)
    p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    b2_inputs=ROOT/'research/prime_field_b2_execution_20261030/inputs.json';d1_inputs=ROOT/'research/prime_field_d1_execution_20261030/inputs.json'
    b2_run=a.b2_run.resolve();d1_run=a.d1_run.resolve();base=a.base.resolve();out=a.out.resolve()
    if not all(database.load(r/'analysis.json')['panel_complete'] for r in (b2_run,d1_run)):raise ValueError('both native panels must be complete')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    sources=list(Path(__file__).resolve().parent.glob('*.py'))+[
        ROOT/'research/prym_experiment_design_20261019/implementation/independent.py',
        ROOT/'src/crypto_autoresearcher/index_calculus/relation_quality.py',ROOT/'src/crypto_autoresearcher/index_calculus/curve.py']
    for path in sources:
        name=str(path.relative_to(ROOT));committed=subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)
        if sha256(committed).hexdigest()!=database.digest(path):raise ValueError('uncommitted generation source '+name)
    out.mkdir(parents=True,exist_ok=False);parent_hash=database.digest(base)
    print('Checking isolated natural-target certificates',flush=True)
    isolated=certify_targets.build(d1_run,d1_inputs);isolated_path=out/'isolated-target-certificates.json';write(isolated_path,isolated)
    print('Checking target-column cancellation and dense rank identity',flush=True)
    partials=cancel_targets.build(d1_run,d1_inputs);partial_path=out/'target-partial-cancellations.json';write(partial_path,partials)
    partial_path,partial_encoding=pack(partial_path)
    atom_path=ROOT/'research/prime_field_b2_execution_20261030/database/atom-log-certificates.json'
    print('Building fresh database from original v2 parent',flush=True)
    db=out/'prime-fields-v3.sqlite'
    counts=database.build(base,b2_run,b2_inputs,d1_run,d1_inputs,db,[atom_path,isolated_path,partial_path])
    with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as c:
        sql_scores={(uid,index):delta for uid,index,delta in c.execute('SELECT b.fixture_uid,t.target_index,t.augmented_rank-(CASE WHEN t.witnesses>0 THEN 1 ELSE 0 END)-t.old_rank FROM target_cases t JOIN bases b USING(base_sha256) WHERE t.status=\'verified\'')}
        expected={(v['fixture_uid'],v['target_index']):v['score']['delta'] for v in partials['cases'] if v['score'] is not None}
        if sql_scores!=expected:raise ValueError('SQL partial score differs from independently checked cancellation')
        sql_isolated={(uid,index):(rank+1,nullity) for uid,index,rank,nullity in c.execute('SELECT b.fixture_uid,t.target_index,t.old_rank,t.old_nullity FROM target_cases t JOIN bases b USING(base_sha256) WHERE t.first_single_attempt IS NOT NULL')}
        expected={(v['fixture_uid'],v['target_index']):(v['isolated']['augmented_rank'],v['isolated']['remaining_base_nullity']) for v in isolated['cases'] if v['isolated'] is not None}
        if sql_isolated!=expected:raise ValueError('SQL isolated rank differs from checked unit certificate')
        target_summary=[dict(fixture_uid=uid,index=index,public_source_matches=json.loads(public),earlier_target_matches=json.loads(other),base_coincidence=bool(base_match),projected_anchor_coincidence=bool(anchor)) for uid,index,public,other,base_match,anchor in c.execute('SELECT b.fixture_uid,t.target_index,t.public_source_matches_json,t.intertarget_matches_json,t.base_coincidence,t.projected_anchor_coincidence FROM target_cases t JOIN bases b USING(base_sha256) ORDER BY b.fixture_uid,t.target_index')]
        integrity=c.execute('PRAGMA integrity_check').fetchone()[0];foreign_keys=c.execute('PRAGMA foreign_key_check').fetchall()
    if database.digest(base)!=parent_hash:raise ValueError('parent bytes changed')
    archive,db_encoding=pack(db,keep_original=True)
    if archive!=db:(out/'.gitignore').write_text('/prime-fields-v3.sqlite\n')
    files=[base,b2_inputs,d1_inputs,b2_run/'export.json',d1_run/'export.json',atom_path,isolated_path,partial_path]+sources
    receipt=dict(schema='prime-field-combined-database-receipt/v3',builder_commit=head,derived_only=True,new_native_executions=0,
        native_physical_executions_total=counts['executions'],counts=counts,parent_unchanged=True,
        integrity_check=integrity,foreign_key_findings=foreign_keys,sql_partial_scores_equal_dense_oracle=True,
        sql_isolated_ranks_equal_unit_certificates=True,target_coincidences=target_summary,
        files=[info(path) for path in files],database=db_encoding,partial_encoding=partial_encoding,
        isolated_certificates=sum(v['isolated'] is not None for v in isolated['cases']),
        isolated_cases_with_public_multiplier_collision=sum(bool(v['isolated'] and v['isolated']['public_multiplier_source_matches']) for v in isolated['cases']),
        scope='Two fixed p4099 curves; original v2 history preserved, one new B2 and one D1 native panel. Post-hoc certificates/cancellation add no native execution or scientific review. No complete S, novelty, holdout result, speedup or official status promotion.')
    write(out/'generation.json',receipt)
    store=[str(path.relative_to(ROOT)) for path in (archive,isolated_path,partial_path) if path.stat().st_size>65536]
    print(json.dumps(dict(directory=str(out.relative_to(ROOT)),counts=counts,isolated_certificates=receipt['isolated_certificates'],store_paths=store),sort_keys=True),flush=True)


if __name__=='__main__':main()
