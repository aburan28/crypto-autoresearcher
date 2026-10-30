"""Fresh v5 norm-completion index preserving the v4 residual-pool parent."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def encode(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def digest(p):return sha256(p.read_bytes()).hexdigest()
def load(p):
    paths=[q for q in (p,Path(str(p)+'.gz')) if q.is_file()]
    if len(paths)!=1:raise ValueError('missing/ambiguous encoding '+str(p))
    with (gzip.open(paths[0],'rt') if paths[0].suffix=='.gz' else paths[0].open()) as f:return json.load(f)


SCHEMA='''
CREATE TABLE norm_cells (
 id TEXT PRIMARY KEY,execution_id TEXT NOT NULL REFERENCES executions,base_sha256 TEXT NOT NULL REFERENCES bases,
 status TEXT NOT NULL,base_projection_json TEXT,source_path TEXT NOT NULL REFERENCES sources
);
CREATE TABLE norm_arms (
 id TEXT PRIMARY KEY,cell_id TEXT NOT NULL REFERENCES norm_cells,arm TEXT NOT NULL,status TEXT NOT NULL,
 accepted_witnesses INTEGER,norm_completed_witnesses INTEGER,distinct_equations INTEGER,new_rank INTEGER,
 combined_rank INTEGER,rank_gain INTEGER,base_nullity_after INTEGER,old_kernel_json TEXT,combined_kernel_json TEXT,summary_json TEXT NOT NULL
);
CREATE TABLE norm_rows (
 cell_id TEXT NOT NULL REFERENCES norm_cells,row_index INTEGER NOT NULL,witness_json TEXT NOT NULL,
 PRIMARY KEY(cell_id,row_index)
);
CREATE VIEW norm_rank_summary AS
 SELECT c.curve_uid,c.b,a.arm,a.status,a.accepted_witnesses,a.norm_completed_witnesses,a.distinct_equations,
 a.new_rank,a.combined_rank,a.rank_gain,a.base_nullity_after
 FROM norm_arms a JOIN norm_cells n ON a.cell_id=n.id JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid);
'''


def build(parent,run,inputs,out):
    if out.exists():raise ValueError('fresh v5 database required')
    before=digest(parent);original=sqlite3.connect('file:'+str(parent.resolve())+'?mode=ro',uri=True);c=sqlite3.connect(out)
    def source(path,kind):
        name=str(path.resolve().relative_to(ROOT));value=(name,digest(path),path.stat().st_size,kind)
        old=c.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if old and old!=value[1:3]:raise ValueError('historical source changed')
        c.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',value);return name
    try:
        original.backup(c);original.close()
        if c.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()!=(encode('prime-field-database/v4'),):raise ValueError('original v4 parent required')
        c.execute('PRAGMA foreign_keys=ON');c.executescript(SCHEMA)
        source(parent,'parent_database_v4');source(Path(__file__),'norm_v5_builder');source(inputs,'frozen_norm_inputs')
        export=load(run/'export.json');execution=load(run/'execution.json');analysis=load(run/'analysis.json');data=load(inputs)
        export_path=source(run/'export.json','unified_export');bound=set()
        for item in export['files']:
            path=(run/item['path']).resolve();path.relative_to(run.resolve())
            if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('native export file mismatch')
            source(path,'export_bound_norm_file');bound.add(path)
        if any((run/name).resolve() not in bound for name in ('analysis.json','execution.json')):raise ValueError('unbound analysis/execution')
        execution_id=str(run.resolve().relative_to(ROOT))
        c.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(execution_id,execution['source_commit'],export['protocol']['sha256'],1,0,encode(execution),export_path))
        summaries={(v['cell_id'],v['arm']):v for v in analysis['cells']}
        for definition in data['cells']:
            fixture=definition['fixture'];basis=c.execute('SELECT base_sha256,curve_uid FROM bases WHERE fixture_uid=?',(fixture['uid'],)).fetchone()
            if basis is None or basis[1]!=fixture['ec1']['curve_uid']:raise ValueError('curve/base identity differs')
            candidates=[p for stem in (definition['id']+'.json',definition['id']+'.collection.json') for p in (run/'raw'/stem,run/'raw'/(stem+'.gz')) if p.is_file()]
            path=candidates[0] if candidates else None;value=None if path is None else load(path)
            if path is not None and path.resolve() not in bound:raise ValueError('unbound native norm result')
            if value is not None and (value['inputs_sha256']!=digest(inputs) or value['curve_uid']!=fixture['uid']):raise ValueError('norm inputs/identity differs')
            cell_id=execution_id+':'+definition['id'];status='verified' if all(summaries[(definition['id'],arm)]['verified'] for arm in ('smooth','norm_completed')) else 'unverified_or_unknown'
            c.execute('INSERT INTO norm_cells VALUES (?,?,?,?,?,?)',(cell_id,execution_id,basis[0],status,None if value is None else encode(value['projection']),export_path if path is None else str(path.resolve().relative_to(ROOT))))
            if value is not None:
                for index,row in enumerate(value['rows']):c.execute('INSERT INTO norm_rows VALUES (?,?,?)',(cell_id,index,encode(row)))
            arms={} if value is None else {arm['arm']:arm for arm in value['arms']}
            for name in ('smooth','norm_completed'):
                s=summaries[(definition['id'],name)];arm_id=cell_id+':'+name;arm=arms.get(name)
                c.execute('INSERT INTO norm_arms VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(arm_id,cell_id,name,s['status'],s['accepted_witnesses'],s['norm_completed_witnesses'],s['distinct_equations'],s['new_rank'],s['combined_rank'],s['rank_gain'],s['base_nullity_after'],None if arm is None else encode(arm['old_kernel']),None if arm is None else encode(arm['kernel']),encode(s)))
        for key in ('schema','builder_sha256','schema_sha256'):
            prior=c.execute('SELECT value FROM metadata WHERE key=?',(key,)).fetchone()
            if prior:c.execute('INSERT INTO metadata VALUES (?,?)',('parent_v4_'+key,prior[0]))
        c.execute("UPDATE metadata SET value=? WHERE key='schema'",(encode('prime-field-database/v5'),))
        c.execute("UPDATE metadata SET value=? WHERE key='builder_sha256'",(encode(digest(Path(__file__))),))
        schema_sql=encode(c.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall())
        c.execute("UPDATE metadata SET value=? WHERE key='schema_sha256'",(encode(sha256(schema_sql.encode()).hexdigest()),))
        if c.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('foreign key failure')
        c.commit()
        if c.execute('PRAGMA integrity_check').fetchone()!=('ok',) or digest(parent)!=before:raise ValueError('integrity/parent preservation failure')
        tables=('curves','bases','executions','equations','cover_frames','subset_rows','target_rows','residual_pools','residual_arms','residual_rows','residual_cancellations','norm_cells','norm_arms','norm_rows','sources')
        return {table:c.execute('SELECT COUNT(*) FROM '+table).fetchone()[0] for table in tables}
    except BaseException:
        c.close();out.unlink(missing_ok=True);raise
    finally:original.close();c.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('parent','run','inputs','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();relative=str(Path(__file__).resolve().relative_to(ROOT))
    if sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest()!=digest(Path(__file__)):raise ValueError('commit exact database builder first')
    counts=build(a.parent,a.run,a.inputs,a.out);original=dict(path=str(a.out),bytes=a.out.stat().st_size,sha256=digest(a.out));archive=Path(str(a.out)+'.gz')
    with archive.open('xb') as f:f.write(gzip.compress(a.out.read_bytes(),compresslevel=6,mtime=0))
    if gzip.decompress(archive.read_bytes())!=a.out.read_bytes():raise ValueError('archive round-trip differs')
    with a.out.parent.joinpath('.gitignore').open('x') as f:f.write('/'+a.out.name+'\n')
    receipt=dict(schema='prime-field-norm-database-receipt/v5',builder_commit=commit,counts=counts,parent_unchanged=True,integrity_check='ok',foreign_key_findings=[],
        sources=[dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path)) for path in (a.parent,a.inputs,a.run/'export.json',Path(__file__))],
        original=original,archive=dict(path=str(archive),bytes=archive.stat().st_size,sha256=digest(archive)),encoding='gzip level6 mtime0; verified lossless',new_native_executions=0)
    with a.out.with_name('generation-v5.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(dict(counts=counts,archive=str(archive))))


if __name__=='__main__':main()
