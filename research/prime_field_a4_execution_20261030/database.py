"""Fresh v7 holdout/target index, retaining all historical v6 tables and rows."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def encode(value): return json.dumps(value,sort_keys=True,separators=(',',':'))
def digest(path): return sha256(path.read_bytes()).hexdigest()
def load(path):
    choices=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(choices)!=1: raise ValueError('missing/ambiguous encoding '+str(path))
    with (gzip.open(choices[0],'rt') if choices[0].suffix=='.gz' else choices[0].open()) as stream: return json.load(stream)

SCHEMA='''
CREATE TABLE holdout_cells(id TEXT PRIMARY KEY,execution_id TEXT NOT NULL REFERENCES executions,
 base_sha256 TEXT NOT NULL REFERENCES bases,source_path TEXT NOT NULL REFERENCES sources,summary_json TEXT NOT NULL);
CREATE TABLE holdout_source_rows(cell_id TEXT NOT NULL REFERENCES holdout_cells,row_index INTEGER NOT NULL,
 witness_json TEXT NOT NULL,PRIMARY KEY(cell_id,row_index));
CREATE TABLE holdout_targets(cell_id TEXT NOT NULL REFERENCES holdout_cells,target_index INTEGER NOT NULL,
 point_json TEXT NOT NULL,collision_json TEXT NOT NULL,PRIMARY KEY(cell_id,target_index));
CREATE TABLE holdout_target_rows(cell_id TEXT NOT NULL REFERENCES holdout_cells,row_index INTEGER NOT NULL,
 target_index INTEGER NOT NULL,witness_json TEXT NOT NULL,PRIMARY KEY(cell_id,row_index),
 FOREIGN KEY(cell_id,target_index) REFERENCES holdout_targets);
CREATE TABLE holdout_prefixes(cell_id TEXT NOT NULL REFERENCES holdout_cells,prefix INTEGER NOT NULL,
 base_rank INTEGER NOT NULL,base_nullity INTEGER NOT NULL,single_targets INTEGER NOT NULL,joint_targets INTEGER NOT NULL,
 joint_base_nullity INTEGER NOT NULL,summary_json TEXT NOT NULL,certificates_json TEXT NOT NULL,PRIMARY KEY(cell_id,prefix));
CREATE VIEW holdout_rank_summary AS SELECT c.curve_uid,c.p,c.b,p.prefix,p.base_rank,p.base_nullity,
 p.single_targets,p.joint_targets,p.joint_base_nullity FROM holdout_prefixes p JOIN holdout_cells h ON p.cell_id=h.id
 JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid);
'''


def build(parent,run,inputs,out):
    if out.exists(): raise ValueError('fresh v7 database required')
    before=digest(parent);original=sqlite3.connect('file:'+str(parent.resolve())+'?mode=ro',uri=True);c=sqlite3.connect(out)
    def source(path,kind):
        name=str(path.resolve().relative_to(ROOT));values=(name,digest(path),path.stat().st_size,kind)
        old=c.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if old and old!=values[1:3]: raise ValueError('historical source bytes changed')
        c.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',values);return name
    try:
        original.backup(c);original.close()
        if c.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()!=(encode('prime-field-database/v6'),): raise ValueError('v6 parent required')
        c.execute('PRAGMA foreign_keys=ON');c.executescript(SCHEMA)
        source(parent,'parent_database_v6');source(Path(__file__),'holdout_v7_builder');source(inputs,'frozen_holdout_rules')
        export=load(run/'export.json');execution=load(run/'execution.json');analysis=load(run/'analysis.json');generated=load(run/'raw/generated.json')
        export_path=source(run/'export.json','unified_export');bound=set()
        for item in export['files']:
            path=(run/item['path']).resolve();path.relative_to(run.resolve())
            if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']: raise ValueError('export file differs')
            source(path,'export_bound_holdout_file');bound.add(path)
        if not analysis['panel_complete'] or any((run/name).resolve() not in bound for name in ('analysis.json','execution.json')): raise ValueError('complete bound panel required')
        execution_id=str(run.resolve().relative_to(ROOT));c.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(execution_id,execution['source_commit'],export['protocol']['sha256'],1,0,encode(execution),export_path))
        summaries={(v['cell_id'],v['prefix']):v for v in analysis['cells']}
        generation_path=run/'raw/generated.json';generation_path=generation_path if generation_path.is_file() else Path(str(generation_path)+'.gz')
        for cell in generated['cells']:
            f=cell['fixture'];uid=f['ec1']['curve_uid'];c.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)',(uid,str(f['p']),str(f['a']),str(f['b']),str(f['r']),encode(f['P'])))
            result=load(run/'raw'/(cell['id']+'.json'));stem=run/'raw'/(cell['id']+'.json');path=stem if stem.is_file() else Path(str(stem)+'.gz')
            if path.resolve() not in bound or result['inputs_sha256']!=digest(inputs): raise ValueError('unbound holdout result')
            base_key=sha256(encode(dict(schema='holdout-base/v1',curve_uid=uid,atoms=f['factor_base'],projection=result['projection'])).encode()).hexdigest()
            c.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)',(base_key,uid,f['uid'],len(f['factor_base']),result['projection']['U'],'holdout-base/v1: curve, native norm atoms and full64 signed public projection',str(generation_path.resolve().relative_to(ROOT))))
            cell_id=execution_id+':'+cell['id'];c.execute('INSERT INTO holdout_cells VALUES (?,?,?,?,?)',(cell_id,execution_id,base_key,str(path.resolve().relative_to(ROOT)),encode(result['total_counters'])))
            for i,row in enumerate(result['rows']): c.execute('INSERT INTO holdout_source_rows VALUES (?,?,?)',(cell_id,i,encode(row)))
            for target,collision in zip(result['target_generation']['targets'],result['collision_diagnostics'],strict=True):
                c.execute('INSERT INTO holdout_targets VALUES (?,?,?,?)',(cell_id,target['index'],encode(target['point']),encode(collision)))
            for i,row in enumerate(result['target_collection']['rows']): c.execute('INSERT INTO holdout_target_rows VALUES (?,?,?,?)',(cell_id,i,row['target_index'],encode(row)))
            for prefix in result['prefixes']:
                s=summaries[cell['id'],prefix['prefix']]
                if not s['verified']: raise ValueError('unverified prefix')
                c.execute('INSERT INTO holdout_prefixes VALUES (?,?,?,?,?,?,?,?,?)',(cell_id,prefix['prefix'],s['base_rank'],s['base_nullity'],s['single_targets'],s['joint_targets'],s['joint_base_nullity'],encode(s),encode(prefix)))
        for key in ('schema','builder_sha256','schema_sha256'):
            prior=c.execute('SELECT value FROM metadata WHERE key=?',(key,)).fetchone()
            if prior: c.execute('INSERT INTO metadata VALUES (?,?)',('parent_v6_'+key,prior[0]))
        c.execute("UPDATE metadata SET value=? WHERE key='schema'",(encode('prime-field-database/v7'),));c.execute("UPDATE metadata SET value=? WHERE key='builder_sha256'",(encode(digest(Path(__file__))),))
        sql=encode(c.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall());c.execute("UPDATE metadata SET value=? WHERE key='schema_sha256'",(encode(sha256(sql.encode()).hexdigest()),))
        if c.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('foreign key failure')
        c.commit()
        if c.execute('PRAGMA integrity_check').fetchone()!=('ok',) or digest(parent)!=before: raise ValueError('integrity/parent preservation failure')
        names=[v[0] for v in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {name:c.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name in names}
    except BaseException:
        c.close();out.unlink(missing_ok=True);raise
    finally: original.close();c.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('parent','run','inputs','out'): parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();args.out.parent.mkdir(parents=True,exist_ok=True);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if sha256(subprocess.check_output(['git','show',commit+':'+str(Path(__file__).resolve().relative_to(ROOT))],cwd=ROOT)).hexdigest()!=digest(Path(__file__)): raise ValueError('commit exact builder first')
    counts=build(args.parent,args.run,args.inputs,args.out);archive=Path(str(args.out)+'.gz')
    with archive.open('xb') as stream: stream.write(gzip.compress(args.out.read_bytes(),compresslevel=6,mtime=0))
    if gzip.decompress(archive.read_bytes())!=args.out.read_bytes(): raise ValueError('gzip roundtrip differs')
    with (args.out.parent/'.gitignore').open('x') as stream: stream.write('/'+args.out.name+'\n')
    value=dict(schema='prime-field-holdout-database-receipt/v7',builder_commit=commit,parent_unchanged=True,integrity_check='ok',foreign_key_findings=[],counts=counts,
               sources=[dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size) for p in (args.parent,args.inputs,args.run/'export.json',Path(__file__))],
               original=dict(path=str(args.out),sha256=digest(args.out),bytes=args.out.stat().st_size),archive=dict(path=str(archive),sha256=digest(archive),bytes=archive.stat().st_size),new_native_executions=0)
    with (args.out.parent/'generation-v7.json').open('x') as stream: json.dump(value,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(counts=counts,archive=str(archive))))


if __name__=='__main__': main()
