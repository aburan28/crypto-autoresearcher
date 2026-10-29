"""Build a fresh, derived SQLite index; imports archives and never collects rows.

This database reports source verification scope. Hash checks do not confer an
independent mathematical review, subgroup proof, or performance qualification.
"""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def load(path):
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as stream:
        return json.load(stream)


def project(row, projection, modulus):
    vector, rhs = [0]*projection['U'], row['source_scalar']
    for c, mapping in zip(row['coefficients'], projection['native_to_projected'], strict=True):
        if mapping[0] == 'known':
            rhs -= c*mapping[1]
        elif mapping[0] == 'unknown':
            vector[mapping[1]] += c*mapping[2]
        elif mapping != ['zero']:
            raise ValueError('unknown projection mapping')
    return [x % modulus for x in vector], rhs % modulus


def normalize(vector, rhs, modulus):
    affine = vector+[rhs]
    first = next((v for v in affine if v % modulus), None)
    return [(v*pow(first, -1, modulus)) % modulus for v in affine] if first else [0]*len(affine)


def canonical_cubic(coefficients, modulus):
    """Orbit under v(X) -> sign*v(deck*X) on the existing even sextic.

    This is a function-grouping key, not a relation or cache-validity proof.
    In particular it intentionally does not erase source-specific obligations.
    """
    if modulus <= 3 or modulus % 2 == 0 or not 1 <= len(coefficients) <= 4:
        raise ValueError('odd characteristic >3 and degree at most three required')
    padded = list(coefficients)+[0]*(4-len(coefficients))
    return min(tuple(sign*c*pow(deck,j,modulus) % modulus for j,c in enumerate(padded))
               for sign in (1,-1) for deck in (1,-1))


def build(catalog_path, fixture_path, run_dirs, output, cover_runs=()):
    if output.exists():
        raise ValueError('database output must be fresh')
    catalog, fixtures = load(catalog_path), load(fixture_path)
    expected = catalog['input_sha256'].get(str(fixture_path.resolve().relative_to(ROOT)))
    if expected != sha256(fixture_path.read_bytes()).hexdigest():
        raise ValueError('fixture bytes differ from retained catalog input')
    connection = sqlite3.connect(output)
    try:
        connection.executescript((HERE/'schema.sql').read_text())
        def source(path, kind):
            relative = str(path.resolve().relative_to(ROOT))
            data = path.read_bytes()
            row = (relative, sha256(data).hexdigest(), len(data), kind)
            prior = connection.execute('SELECT * FROM sources WHERE path=?', (relative,)).fetchone()
            if prior and prior != row:
                raise ValueError('source path has changed during import')
            connection.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)', row)
            return relative
        for key, value in {'schema':'prime-field-database/v2', 'derived_only':True,
                           'new_collection_performed':False, 'schema_sha256':sha256((HERE/'schema.sql').read_bytes()).hexdigest(),
                           'builder_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}.items():
            connection.execute('INSERT INTO metadata VALUES (?,?)', (key, encode(value)))
        source(Path(__file__), 'builder'); source(HERE/'schema.sql', 'schema')
        catalog_source = source(catalog_path, 'retained_catalog')
        source(fixture_path, 'frozen_fixture')
        fixture_map = {f['uid']:f for f in fixtures['fixtures']}
        base_map = {}
        for base in catalog['retained_bases']:
            fixture = fixture_map[base['fixture_uid']]
            if any(int(base[k]) != fixture[k] for k in ('p','a','b','r')):
                raise ValueError('catalog/fixture curve mismatch')
            if base['curve_uid'] != fixture['ec1']['curve_uid']:
                raise ValueError('EC1 identity mismatch')
            points = base['ordered_projected_points']
            if sha256(encode(points).encode()).hexdigest() != base['base_sha256']:
                raise ValueError('ordered base hash mismatch')
            base_map[base['fixture_uid']] = base
            connection.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)',
                (base['curve_uid'], str(base['p']), str(base['a']), str(base['b']), str(base['r']), encode(base['generator'])))
            connection.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)',
                (base['base_sha256'], base['curve_uid'], base['fixture_uid'], base['native_atoms'],
                 base['projected_columns'], 'ordered signed canonical unknowns after public-anchor removal', catalog_source))
            connection.executemany('INSERT INTO atoms VALUES (?,?,?,?)',
                [(base['base_sha256'], i, str(x), str(y)) for i,(x,y) in enumerate(points)])
            connection.executemany('INSERT INTO native_atoms VALUES (?,?,?,?,?,?)',
                [(base['base_sha256'],i,*map(str,atom['point']),*map(str,atom['lift']))
                 for i,atom in enumerate(fixture['factor_base'])])
            audit = base['negation_action_audit']
            action = audit['action']
            connection.execute('INSERT INTO actions VALUES (?,?,?,?,?,?)',
                (base['base_sha256'], 'negation', str(action['eigenvalue']), action['known_constraint_rank'],
                 audit['additional_rank_after_known_action'], encode(audit)))
            connection.execute('INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                ('retained:'+base['fixture_uid'],base['base_sha256'],None,'retained_historical_nonzero',
                 None,base['native_witnesses'],None,base['original_rank'],base['original_nullity'],
                 'Retained catalog source reports; no new replay in database builder',catalog_source))
        for run_dir in run_dirs:
            export_path = run_dir/'export.json'
            export, execution = load(export_path), load(run_dir/'execution.json')
            if export['schema'] != 'experiment.export/v1':
                raise ValueError('unified export required before import')
            source(export_path,'unified_export')
            # Bind every original/compressed raw file before importing values.
            for item in export['files']:
                path = (run_dir/item['path']).resolve()
                path.relative_to(run_dir.resolve())
                data = path.read_bytes()
                if sha256(data).hexdigest() != item['sha256'] or len(data) != item['bytes']:
                    raise ValueError('export file hash mismatch: '+item['path'])
                source(path, 'export_bound_file')
            bound_paths = {(run_dir/f['path']).resolve() for f in export['files']}
            if (run_dir/'execution.json').resolve() not in bound_paths:
                raise ValueError('execution receipt absent from export file hashes')
            execution_id = str(run_dir.resolve().relative_to(ROOT))
            connection.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',
                (execution_id,execution['source_commit'],export['protocol']['sha256'],1,0,
                 encode(execution),str(export_path.resolve().relative_to(ROOT))))
            for fixture_uid, base in base_map.items():
                for arm in ('historical_nonzero','completed_zero'):
                    stem = fixture_uid+'-'+arm
                    paths = [p for p in (run_dir/'raw'/(stem+'.json'),run_dir/'raw'/(stem+'.json.gz')) if p.is_file()]
                    if not paths:
                        continue  # Missing cells stay absent, never rank-zero data.
                    if len(paths) != 1:
                        raise ValueError('ambiguous compressed/uncompressed source')
                    path = paths[0]
                    if not any((run_dir/f['path']).resolve() == path.resolve() for f in export['files']):
                        raise ValueError('result absent from export file hashes')
                    result = load(path)
                    if (result.get('curve_uid') != fixture_uid or
                            result.get('include_zero') is not (arm == 'completed_zero') or
                            result.get('inputs_sha256') != expected or
                            result.get('source_order') != fixture_map[fixture_uid]['width_binding']['source_order']):
                        raise ValueError('raw result identity differs from fixture/arm/input binding')
                    if result['projection']['unknown_points'] != base['ordered_projected_points']:
                        raise ValueError('base columns differ; a new base identity is required')
                    verification_path = run_dir/'raw'/(stem+'.verification.json')
                    if verification_path.is_file() and verification_path.resolve() not in bound_paths:
                        raise ValueError('verification absent from export file hashes')
                    verification = load(verification_path) if verification_path.is_file() else {}
                    if verification.get('checked') and (verification.get('attempts_replayed') != result['attempts'] or
                            any(verification.get(k) != result['quality'][k] for k in ('rows','rank','nullity','columns','unique_affine_equations'))):
                        raise ValueError('source verification summary differs from result')
                    scope = ('Source reports complete separate branch replay' if verification.get('checked')
                             else 'Collected source only; no completed separate replay')
                    observation_id = execution_id+':'+stem
                    q = result['quality']
                    connection.execute('INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                        (observation_id,base['base_sha256'],execution_id,arm,result['attempts'],len(result['rows']),
                         q['unique_affine_equations'],q['rank'],q['nullity'],scope,
                         str(path.resolve().relative_to(ROOT))))
                    connection.executemany('INSERT INTO statuses VALUES (?,?,?)',
                        [(observation_id,k,v) for k,v in result['statuses'].items()])
                    if len(result['kernel']) != q['nullity'] or any(len(v) != q['columns'] for v in result['kernel']):
                        raise ValueError('kernel shape differs from source quality')
                    connection.executemany('INSERT INTO kernels VALUES (?,?,?)',
                        [(observation_id,i,encode(vector)) for i,vector in enumerate(result['kernel'])])
                    syndromes = result.get('old_kernel_syndromes')
                    if syndromes is not None and len(syndromes) != len(result['rows']):
                        raise ValueError('syndrome count mismatch')
                    for index,row in enumerate(result['rows']):
                        vector,rhs = project(row,result['projection'],int(base['r']))
                        cubic = canonical_cubic(row['v_coefficients'],int(base['p']))
                        function_id = sha256(encode(dict(curve_uid=base['curve_uid'],cubic=cubic)).encode()).hexdigest()
                        connection.execute('INSERT OR IGNORE INTO principal_functions VALUES (?,?,?)',
                            (function_id,base['curve_uid'],encode(cubic)))
                        connection.execute('INSERT INTO equations VALUES (?,?,?,?,?,?,?,?,?,?)',
                            (observation_id,index,encode(normalize(vector,rhs,int(base['r']))),encode(vector),str(rhs),
                             int(row['constraints'][0][0] == 0),int(any(p[0] == 0 for p in row['constraints'][1:])),
                             None if syndromes is None else encode(syndromes[index]),encode(row),function_id))
        for run_dir in cover_runs:
            export_path=run_dir/'export.json'
            export=load(export_path)
            if export['schema']!='experiment.export/v1':raise ValueError('cover unified export required')
            source(export_path,'unified_export')
            bound_paths=set()
            for item in export['files']:
                path=(run_dir/item['path']).resolve();path.relative_to(run_dir.resolve())
                data=path.read_bytes()
                if sha256(data).hexdigest()!=item['sha256'] or len(data)!=item['bytes']:
                    raise ValueError('cover export file hash mismatch')
                source(path,'export_bound_file');bound_paths.add(path)
            raw_paths=[p for p in (run_dir/'raw/survey.json',run_dir/'raw/survey.json.gz') if p.is_file()]
            if len(raw_paths)!=1 or raw_paths[0].resolve() not in bound_paths:
                raise ValueError('unambiguous export-bound cover survey required')
            for p in (run_dir/'execution.json',run_dir/'raw/verification.json'):
                if p.resolve() not in bound_paths:raise ValueError('cover execution/verification unbound')
            execution=load(run_dir/'execution.json');raw=load(raw_paths[0]);verification=load(run_dir/'raw/verification.json')
            if raw.get('schema')!='prime-field-shifted-cover-survey/v1' or raw.get('inputs_sha256')!=expected or raw.get('complete') is not True:
                raise ValueError('cover schema/input mismatch')
            if not verification.get('checked') or verification.get('frames_checked')!=sum(f['p'] for f in fixtures['fixtures']):
                raise ValueError('complete cover verification absent')
            if len(raw['cells'])!=len(base_map) or {c['fixture_uid'] for c in raw['cells']}!=set(base_map):
                raise ValueError('cover fixture coverage differs')
            execution_id=str(run_dir.resolve().relative_to(ROOT))
            connection.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',
                (execution_id,execution['source_commit'],export['protocol']['sha256'],1,0,encode(execution),
                 str(export_path.resolve().relative_to(ROOT))))
            for cell in raw['cells']:
                base=base_map[cell['fixture_uid']];fixture=fixture_map[cell['fixture_uid']]
                if cell['curve_uid']!=base['curve_uid'] or cell['source_order']!=fixture['width_binding']['source_order'] or any(cell[k]!=fixture[k] for k in ('p','a','b','r')):
                    raise ValueError('cover curve/source identity differs')
                if len(cell['rows'])!=cell['p'] or [row['h'] for row in cell['rows']]!=list(range(cell['p'])):
                    raise ValueError('cover frame coverage differs')
                connection.executemany('INSERT INTO cover_sources VALUES (?,?,?,?,?,?)',
                    [(execution_id,base['base_sha256'],i,str(s),str(point[0]),str(point[1]))
                     for i,(s,point) in enumerate(zip(cell['source_order'],cell['source_points'],strict=True))])
                connection.executemany('INSERT INTO cover_frames VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    [(execution_id,base['base_sha256'],str(row['h']),str(row['c4']),str(row['c2']),str(row['c0']),
                      int(row['singular']),int(row['eligible']),row['base_square_mask'],row['base_zero_mask'],
                      row['source_square_mask'],row['source_zero_mask']) for row in cell['rows']])
        if connection.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('foreign key failure')
        connection.commit()
        return {table:connection.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
                for table in ('curves','bases','atoms','native_atoms','actions','executions','observations','equations','kernels','principal_functions','cover_frames','cover_sources','sources')}
    except BaseException:
        connection.close()
        output.unlink(missing_ok=True)
        raise
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',type=Path,default=ROOT/'research/prime_field_symmetries_20261029/catalog.json')
    parser.add_argument('--fixtures',type=Path,default=ROOT/'research/prym_factor_base_width_20261025/fixtures.json')
    parser.add_argument('--run',type=Path,action='append',default=[])
    parser.add_argument('--cover-survey',type=Path,action='append',default=[])
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    print(encode(build(args.catalog,args.fixtures,args.run,args.out,args.cover_survey)))


if __name__ == '__main__':
    main()
