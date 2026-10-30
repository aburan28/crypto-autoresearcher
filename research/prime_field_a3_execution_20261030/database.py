"""Fresh v6 direct-collector database, preserving every byte of the v5 parent."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def encode(v): return json.dumps(v,sort_keys=True,separators=(',',':'))
def digest(path): return sha256(path.read_bytes()).hexdigest()
def load(path):
    paths=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(paths)!=1: raise ValueError('missing/ambiguous encoding '+str(path))
    with (gzip.open(paths[0],'rt') if paths[0].suffix=='.gz' else paths[0].open()) as stream: return json.load(stream)


SCHEMA='''
CREATE TABLE direct_cells (
 id TEXT PRIMARY KEY, execution_id TEXT NOT NULL REFERENCES executions,
 base_sha256 TEXT NOT NULL REFERENCES bases, source_path TEXT NOT NULL REFERENCES sources,
 verification_json TEXT NOT NULL
);
CREATE TABLE direct_arms (
 id TEXT PRIMARY KEY, cell_id TEXT NOT NULL REFERENCES direct_cells, arm TEXT NOT NULL,
 status TEXT NOT NULL, accepted_witnesses INTEGER, distinct_equations INTEGER,
 new_rank INTEGER, combined_rank INTEGER, rank_gain INTEGER, counters_json TEXT,
 analysis_json TEXT, summary_json TEXT NOT NULL
);
CREATE TABLE direct_rows (
 arm_id TEXT NOT NULL REFERENCES direct_arms, row_index INTEGER NOT NULL,
 witness_json TEXT NOT NULL, PRIMARY KEY(arm_id,row_index)
);
CREATE TABLE direct_norm_matches (
 cell_id TEXT NOT NULL REFERENCES direct_cells, archived_index INTEGER NOT NULL,
 direct_row_index INTEGER NOT NULL, PRIMARY KEY(cell_id,archived_index)
);
CREATE VIEW direct_rank_summary AS
 SELECT c.curve_uid,c.b,a.arm,a.status,a.accepted_witnesses,a.distinct_equations,
 a.new_rank,a.combined_rank,a.rank_gain
 FROM direct_arms a JOIN direct_cells d ON a.cell_id=d.id
 JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid);
'''


def build(parent,run,inputs,out):
    if out.exists(): raise ValueError('fresh v6 database required')
    before=digest(parent);original=sqlite3.connect('file:'+str(parent.resolve())+'?mode=ro',uri=True);connection=sqlite3.connect(out)
    def source(path,kind):
        name=str(path.resolve().relative_to(ROOT));value=(name,digest(path),path.stat().st_size,kind)
        old=connection.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if old and old!=value[1:3]: raise ValueError('historical source changed')
        connection.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',value);return name
    try:
        original.backup(connection);original.close()
        if connection.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()!=(encode('prime-field-database/v5'),): raise ValueError('v5 parent required')
        connection.execute('PRAGMA foreign_keys=ON');connection.executescript(SCHEMA)
        source(parent,'parent_database_v5');source(Path(__file__),'direct_v6_builder');source(inputs,'frozen_direct_inputs')
        export=load(run/'export.json');execution=load(run/'execution.json');analysis=load(run/'analysis.json');data=load(inputs)
        export_path=source(run/'export.json','unified_export');bound=set()
        for item in export['files']:
            path=(run/item['path']).resolve();path.relative_to(run.resolve())
            if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']: raise ValueError('export file mismatch')
            source(path,'export_bound_direct_file');bound.add(path)
        if any((run/name).resolve() not in bound for name in ('analysis.json','execution.json')): raise ValueError('unbound analysis/execution')
        execution_id=str(run.resolve().relative_to(ROOT))
        connection.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(execution_id,execution['source_commit'],export['protocol']['sha256'],1,0,encode(execution),export_path))
        summaries={(s['cell_id'],s['arm']):s for s in analysis['cells']}
        for definition in data['cells']:
            fixture=definition['fixture'];basis=connection.execute('SELECT base_sha256,curve_uid FROM bases WHERE fixture_uid=?',(fixture['uid'],)).fetchone()
            if basis is None or basis[1]!=fixture['ec1']['curve_uid']: raise ValueError('base identity differs')
            stem=run/'raw'/(definition['id']+'.json');path=stem if stem.is_file() else Path(str(stem)+'.gz')
            verification=load(run/'raw'/(definition['id']+'.verification.json'));value=load(stem)
            if path.resolve() not in bound or value['inputs_sha256']!=digest(inputs) or value['curve_uid']!=fixture['uid']: raise ValueError('native result binding differs')
            if verification['checked']is not True: raise ValueError('verified direct result required')
            cell_id=execution_id+':'+definition['id']
            connection.execute('INSERT INTO direct_cells VALUES (?,?,?,?,?)',(cell_id,execution_id,basis[0],str(path.resolve().relative_to(ROOT)),encode(verification)))
            for arm in value['arms']:
                name=arm['arm'];s=summaries[(definition['id'],name)];arm_id=cell_id+':'+name;q=arm['analysis']
                if s['verified']is not True: raise ValueError('unverified summary')
                connection.execute('INSERT INTO direct_arms VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    (arm_id,cell_id,name,s['status'],len(arm['rows']),q['distinct_equations'],q['new']['rank'],q['combined']['rank'],q['rank_gain'],encode(q['total_counters']),encode(q),encode(s)))
                for index,row in enumerate(arm['rows']): connection.execute('INSERT INTO direct_rows VALUES (?,?,?)',(arm_id,index,encode(row)))
            for index,row in enumerate(verification['archived_norm_subset']['direct_row_indices']):
                connection.execute('INSERT INTO direct_norm_matches VALUES (?,?,?)',(cell_id,index,row))
        for key in ('schema','builder_sha256','schema_sha256'):
            prior=connection.execute('SELECT value FROM metadata WHERE key=?',(key,)).fetchone()
            if prior: connection.execute('INSERT INTO metadata VALUES (?,?)',('parent_v5_'+key,prior[0]))
        connection.execute("UPDATE metadata SET value=? WHERE key='schema'",(encode('prime-field-database/v6'),))
        connection.execute("UPDATE metadata SET value=? WHERE key='builder_sha256'",(encode(digest(Path(__file__))),))
        sql=encode(connection.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall())
        connection.execute("UPDATE metadata SET value=? WHERE key='schema_sha256'",(encode(sha256(sql.encode()).hexdigest()),))
        if connection.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('foreign key failure')
        connection.commit()
        if connection.execute('PRAGMA integrity_check').fetchone()!=('ok',) or digest(parent)!=before: raise ValueError('integrity/parent preservation failure')
        tables=('curves','bases','executions','equations','cover_frames','subset_rows','target_rows','residual_rows','residual_cancellations','norm_rows','direct_cells','direct_arms','direct_rows','direct_norm_matches','sources')
        return {table:connection.execute('SELECT COUNT(*) FROM '+table).fetchone()[0] for table in tables}
    except BaseException:
        connection.close();out.unlink(missing_ok=True);raise
    finally: original.close();connection.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('parent','run','inputs','out'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();args.out.parent.mkdir(parents=True,exist_ok=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();relative=str(Path(__file__).resolve().relative_to(ROOT))
    if sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest()!=digest(Path(__file__)): raise ValueError('commit exact builder first')
    counts=build(args.parent,args.run,args.inputs,args.out);original=dict(path=str(args.out),bytes=args.out.stat().st_size,sha256=digest(args.out));archive=Path(str(args.out)+'.gz')
    with archive.open('xb') as stream: stream.write(gzip.compress(args.out.read_bytes(),compresslevel=6,mtime=0))
    if gzip.decompress(archive.read_bytes())!=args.out.read_bytes(): raise ValueError('gzip round trip differs')
    with args.out.parent.joinpath('.gitignore').open('x') as stream: stream.write('/'+args.out.name+'\n')
    receipt=dict(schema='prime-field-direct-database-receipt/v6',builder_commit=commit,counts=counts,parent_unchanged=True,integrity_check='ok',foreign_key_findings=[],
                 sources=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in (args.parent,args.inputs,args.run/'export.json',Path(__file__))],
                 original=original,archive=dict(path=str(archive),bytes=archive.stat().st_size,sha256=digest(archive)),encoding='gzip level6 mtime0; verified lossless',new_native_executions=0)
    with args.out.with_name('generation-v6.json').open('x') as stream: json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(counts=counts,archive=str(archive))))


if __name__=='__main__': main()
