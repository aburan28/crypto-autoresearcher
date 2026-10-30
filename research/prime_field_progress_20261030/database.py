"""Fresh derived SQLite generation over immutable source-bound native records."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[2]


def encode(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def digest(path):return sha256(path.read_bytes()).hexdigest()
def load(path):
    candidates=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(candidates)!=1:raise ValueError('missing/ambiguous source '+str(path))
    with (gzip.open(candidates[0],'rt') if candidates[0].suffix=='.gz' else candidates[0].open()) as stream:return json.load(stream)


SCHEMA='''
CREATE TABLE subset_cells (
 id TEXT PRIMARY KEY,execution_id TEXT NOT NULL REFERENCES executions,base_sha256 TEXT NOT NULL REFERENCES bases,
 case_id TEXT NOT NULL,arm TEXT NOT NULL,h TEXT NOT NULL,active_atoms_json TEXT NOT NULL,
 status TEXT NOT NULL,attempts INTEGER,witnesses INTEGER,unique_equations INTEGER,new_rank INTEGER,
 old_rank INTEGER,combined_rank INTEGER,rank_gain INTEGER,projection_json TEXT,old_kernel_json TEXT,
 combined_kernel_json TEXT,source_path TEXT NOT NULL REFERENCES sources
);
CREATE TABLE subset_rows (
 cell_id TEXT NOT NULL REFERENCES subset_cells,row_index INTEGER NOT NULL,coefficients_json TEXT NOT NULL,
 rhs TEXT NOT NULL,old_syndrome_json TEXT NOT NULL,witness_json TEXT NOT NULL,PRIMARY KEY(cell_id,row_index)
);
CREATE TABLE target_cases (
 id TEXT PRIMARY KEY,execution_id TEXT NOT NULL REFERENCES executions,base_sha256 TEXT NOT NULL REFERENCES bases,
 target_index INTEGER NOT NULL,hash_curve_uid TEXT NOT NULL,status TEXT NOT NULL,point_json TEXT,
 attempts INTEGER,witnesses INTEGER,old_rank INTEGER,old_nullity INTEGER,augmented_rank INTEGER,
 identified INTEGER,scalar TEXT,first_single_attempt INTEGER,first_combined_attempt INTEGER,first_combined_rank INTEGER,
 base_coincidence INTEGER,projected_anchor_coincidence INTEGER,public_source_matches_json TEXT,
 intertarget_matches_json TEXT,recipe_json TEXT,certificate_json TEXT,source_path TEXT NOT NULL REFERENCES sources
);
CREATE TABLE target_rows (
 case_id TEXT NOT NULL REFERENCES target_cases,row_index INTEGER NOT NULL,coefficients_json TEXT NOT NULL,
 offset TEXT NOT NULL,target_coefficient TEXT NOT NULL,witness_json TEXT NOT NULL,PRIMARY KEY(case_id,row_index)
);
CREATE TABLE target_isolated_certificates (
 case_id TEXT PRIMARY KEY REFERENCES target_cases,multiplier TEXT NOT NULL,augmented_rank INTEGER NOT NULL,
 remaining_base_nullity INTEGER NOT NULL,public_multiplier_source_matches_json TEXT NOT NULL,
 certificate_json TEXT NOT NULL,source_path TEXT NOT NULL REFERENCES sources
);
CREATE VIEW subset_rank_summary AS
 SELECT c.b,s.case_id,s.arm,s.h,s.status,s.attempts,s.witnesses,s.unique_equations,s.new_rank,s.old_rank,s.combined_rank,s.rank_gain
 FROM subset_cells s JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid);
CREATE VIEW target_recovery_summary AS
 SELECT c.b,t.target_index,t.status,t.attempts,t.witnesses,t.old_rank,t.old_nullity,t.augmented_rank,t.identified,
 t.first_combined_attempt,t.first_combined_rank,t.public_source_matches_json
 FROM target_cases t JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid);
CREATE VIEW isolated_target_summary AS
 SELECT c.b,t.target_index,t.first_single_attempt,t.old_rank+1 AS isolated_augmented_rank,
 t.old_nullity AS remaining_base_nullity,i.multiplier,i.public_multiplier_source_matches_json
 FROM target_cases t JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid)
 LEFT JOIN target_isolated_certificates i ON i.case_id=t.id
 WHERE t.status='verified' AND t.first_single_attempt IS NOT NULL;
CREATE VIEW target_partial_score_summary AS
 SELECT c.b,t.target_index,t.old_rank,t.augmented_rank,
 CASE WHEN t.witnesses>0 THEN 1 ELSE 0 END AS outside_rank,
 t.augmented_rank-(CASE WHEN t.witnesses>0 THEN 1 ELSE 0 END)-t.old_rank AS delta,
 2*t.attempts AS charged_collection_and_replay_branches
 FROM target_cases t JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid)
 WHERE t.status='verified';
'''


def project(row,projection,r):
    v,b=[0]*projection['U'],row['source_scalar']
    for c,m in zip(row['coefficients'],projection['native_to_projected'],strict=True):
        if m[0]=='known':b-=c*m[1]
        elif m[0]=='unknown':v[m[1]]+=c*m[2]
        elif m!=['zero']:raise ValueError('bad source projection')
    return [x%r for x in v],b%r


def build(base_path,b2_run,b2_inputs,d1_run,d1_inputs,out,derived_sources=()):
    if out.exists():raise ValueError('fresh derived database required')
    original=sqlite3.connect('file:'+str(base_path.resolve())+'?mode=ro',uri=True)
    c=sqlite3.connect(out)
    try:
        original.backup(c)
        if c.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()!=(encode('prime-field-database/v2'),):
            raise ValueError('original v2 parent required')
        c.execute('PRAGMA foreign_keys=ON');c.executescript(SCHEMA)
    except BaseException:
        c.close();out.unlink(missing_ok=True);raise
    finally:original.close()
    def source(path,kind):
        path=path.resolve();name=str(path.relative_to(ROOT));data=path.read_bytes();value=(name,sha256(data).hexdigest(),len(data),kind)
        prior=c.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if prior and prior!=value[1:3]:raise ValueError('historical source path changed: '+name)
        c.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',value);return name
    def bind(run):
        export=load(run/'export.json');execution=load(run/'execution.json');source(run/'export.json','unified_export')
        if export['schema']!='experiment.export/v1':raise ValueError('unified export required')
        bound=set()
        for item in export['files']:
            path=(run/item['path']).resolve();path.relative_to(run.resolve())
            if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('native export file mismatch')
            source(path,'export_bound_file');bound.add(path)
        for name in ('analysis.json','execution.json'):
            if (run/name).resolve() not in bound:raise ValueError('unbound native analysis/execution')
        ident=str(run.resolve().relative_to(ROOT))
        c.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(ident,execution['source_commit'],export['protocol']['sha256'],1,0,encode(execution),source(run/'export.json','unified_export')))
        return ident,load(run/'analysis.json'),bound
    def raw(run,name,bound):
        options=[p for p in (run/'raw'/name,run/'raw'/(name+'.gz')) if p.is_file()]
        if not options:return None,None
        if len(options)!=1 or options[0].resolve() not in bound:raise ValueError('unbound/ambiguous raw result')
        return load(run/'raw'/name),str(options[0].resolve().relative_to(ROOT))
    def base(fixture):
        row=c.execute('SELECT base_sha256,curve_uid FROM bases WHERE fixture_uid=?',(fixture['uid'],)).fetchone()
        if row is None or row[1]!=fixture['ec1']['curve_uid']:raise ValueError('original curve/base identity mismatch')
        return row[0]
    try:
        source(base_path,'parent_database');source(Path(__file__),'builder')
        for path in derived_sources:source(path,'derived_certificates_or_scores')
        for key in ('builder_sha256','schema_sha256'):
            prior=c.execute('SELECT value FROM metadata WHERE key=?',(key,)).fetchone()
            if prior:c.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('parent_'+key,prior[0]))
        c.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('schema',encode('prime-field-database/v3')))
        c.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('progress_builder_sha256',encode(digest(Path(__file__)))))
        c.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('builder_sha256',encode(digest(Path(__file__)))))
        schema_sql=encode(c.execute("SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name").fetchall())
        c.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('schema_sha256',encode(sha256(schema_sql.encode()).hexdigest())))
        c.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('schema_digest_recipe',encode('SHA256 of canonical JSON [[name,sql],...] from sqlite_master WHERE sql IS NOT NULL ORDER BY name')))
        if b2_run is not None:
            definitions=load(b2_inputs);source(b2_inputs,'frozen_subset_inputs');execution,analysis,bound=bind(b2_run)
            summaries={(x['cell_id'],x['arm']):x for x in analysis['cells']}
            for definition in definitions['cells']:
                fixture=definition['fixture'];basis=base(fixture)
                for arm in ('baseline','shifted'):
                    value,path=raw(b2_run,definition['id']+'-'+arm+'.json',bound);summary=summaries[(definition['id'],arm)]
                    ident=execution+':'+definition['id']+':'+arm
                    if value is not None and (value['inputs_sha256']!=digest(b2_inputs) or value['curve_uid']!=fixture['uid'] or value['active_atoms']!=definition['active_atoms']):raise ValueError('subset input/identity differs')
                    c.execute('INSERT INTO subset_cells VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (ident,execution,basis,definition['id'],arm,str(0 if arm=='baseline' else definition['shift']),encode(definition['active_atoms']),summary['status'],summary['attempts'],summary['witnesses'],summary['unique_equations'],summary['new_rank'],summary.get('preprocessing_rank'),summary['combined_rank'],summary['rank_gain'],None if value is None else encode(value['projection']),None if value is None else encode(value['old_kernel']),None if value is None else encode(value['kernel']),path or str((b2_run/'export.json').resolve().relative_to(ROOT))))
                    if value is not None:
                        for i,row in enumerate(value['rows']):
                            v,b=project(row,value['projection'],fixture['r'])
                            c.execute('INSERT INTO subset_rows VALUES (?,?,?,?,?,?)',(ident,i,encode(v),str(b),encode(value['old_kernel_syndromes'][i]),encode(row)))
        if d1_run is not None:
            definitions=load(d1_inputs);source(d1_inputs,'frozen_target_inputs');execution,analysis,bound=bind(d1_run)
            summaries={(x['curve_uid'],x['target_index']):x for x in analysis['cells']}
            for definition in definitions['cells']:
                fixture=definition['fixture'];basis=base(fixture);field=fixture['p']
                known=c.execute('SELECT DISTINCT public_scalar,x,y FROM cover_sources WHERE base_sha256=?',(basis,)).fetchall()
                for index in definition['target_indices']:
                    summary=summaries[(fixture['uid'],index)];value,path=raw(d1_run,fixture['uid']+'-target-'+str(index)+'.json',bound)
                    ident=execution+':'+fixture['uid']+':'+str(index);matches=[];duplicates=[]
                    point=None if value is None else value['target']
                    if value is not None and (value['inputs_sha256']!=digest(d1_inputs) or value['target_recipe']['curve_uid']!=definition['target_curve_uid']):raise ValueError('target input/hash identity differs')
                    if point is not None:
                        for s,x,y in known:
                            if point==[int(x),int(y)]:matches.append(dict(public_source_scalar=int(s),sign=1))
                            if point==[int(x),-int(y)%field]:matches.append(dict(public_source_scalar=int(s),sign=-1))
                        for other_id,other_point in c.execute('SELECT id,point_json FROM target_cases WHERE base_sha256=? AND point_json IS NOT NULL',(basis,)).fetchall():
                            prior=json.loads(other_point)
                            if point==prior:duplicates.append(dict(case_id=other_id,sign=1))
                            if point==[prior[0],-prior[1]%field]:duplicates.append(dict(case_id=other_id,sign=-1))
                    final=None if value is None else value['final_target_certificate'];first=None if value is None else value['first_combined_recovery']
                    c.execute('INSERT INTO target_cases VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (ident,execution,basis,index,definition['target_curve_uid'],summary['status'],None if point is None else encode(point),summary['attempts'],summary['witnesses'],summary['base_rank'],summary['base_nullity'],summary['augmented_rank'],summary['identified_target'],None if final is None else str(final['scalar']),summary['first_single_attempt'],summary['first_combined_attempt'],None if first is None else first['certificate']['augmented_rank'],None if value is None else int(value['target_is_signed_base_point']),None if value is None else int(value['target_is_public_anchor']),encode(matches),encode(duplicates),None if value is None else encode(value['target_recipe']),None if final is None else encode(final),path or str((d1_run/'export.json').resolve().relative_to(ROOT))))
                    if value is not None:
                        for i,row in enumerate(value['rows']):
                            v,b=project(row,value['projection'],fixture['r'])
                            c.execute('INSERT INTO target_rows VALUES (?,?,?,?,?,?)',(ident,i,encode(v),str(b),str(row['target_coefficient']),encode(row)))
        for path in derived_sources:
            record=load(path)
            if record.get('schema')!='prime-field-derived-isolated-target-certificates/v1':continue
            if d1_run is None or record['source_export_sha256']!=digest(d1_run/'export.json') or record['inputs_sha256']!=digest(d1_inputs):
                raise ValueError('isolated certificate provenance differs')
            for item in record['cases']:
                certificate=item['isolated']
                if certificate is None:continue
                case_id,scalar,rank,nullity=c.execute('SELECT t.id,t.scalar,t.old_rank,t.old_nullity FROM target_cases t JOIN bases b USING(base_sha256) WHERE b.fixture_uid=? AND t.target_index=?',(item['fixture_uid'],item['target_index'])).fetchone()
                if str(certificate['scalar'])!=scalar or certificate['augmented_rank']!=rank+1 or certificate['remaining_base_nullity']!=nullity:
                    raise ValueError('isolated certificate/native result differs')
                c.execute('INSERT INTO target_isolated_certificates VALUES (?,?,?,?,?,?,?)',(case_id,str(certificate['multiplier']),certificate['augmented_rank'],nullity,encode(certificate['public_multiplier_source_matches']),encode(certificate),str(path.resolve().relative_to(ROOT))))
        if c.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('derived database foreign key failure')
        c.commit()
        if c.execute('PRAGMA integrity_check').fetchone()!=('ok',):raise ValueError('derived database integrity failure')
        return {table:c.execute('SELECT COUNT(*) FROM '+table).fetchone()[0] for table in ('curves','bases','executions','equations','cover_frames','subset_cells','subset_rows','target_cases','target_rows','target_isolated_certificates','sources')}
    except BaseException:
        c.close();out.unlink(missing_ok=True);raise
    finally:c.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True);p.add_argument('--b2-run',type=Path);p.add_argument('--b2-inputs',type=Path)
    p.add_argument('--d1-run',type=Path);p.add_argument('--d1-inputs',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--derived-source',type=Path,action='append',default=[])
    args=p.parse_args();print(encode(build(args.base,args.b2_run,args.b2_inputs,args.d1_run,args.d1_inputs,args.out,args.derived_source)))


if __name__=='__main__':main()
