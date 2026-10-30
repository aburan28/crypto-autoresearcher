"""Derive usable atom-log certificates from immutable, full-rank B2 cells.

No collection, search for discrete logs, target sampling or target labels.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from database import load,project
sys.path.insert(0,str(ROOT/'research/prym_experiment_design_20261019/implementation'))
from independent import multiply
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations


def check_weights(matrix,rhs,unit,value,weights,modulus):
    if len(weights)!=len(matrix) or len(rhs)!=len(matrix):
        raise ValueError('certificate row count differs')
    if any(len(row)!=len(unit) for row in matrix):
        raise ValueError('certificate column count differs')
    if [sum(w*row[j] for w,row in zip(weights,matrix))%modulus for j in range(len(unit))]!=unit:
        raise ValueError('certificate does not reproduce unit vector')
    if sum(w*b for w,b in zip(weights,rhs))%modulus!=value:
        raise ValueError('certificate does not reproduce scalar')


def build(run,inputs):
    export=load(run/'export.json');definitions=load(inputs)
    bound={item['path']:item for item in export['files']}
    for name,item in bound.items():
        path=(run/name).resolve();path.relative_to(run.resolve())
        if path.stat().st_size!=item['bytes'] or sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('export source binding differs')
    analysis=load(run/'analysis.json');out=[]
    for summary in analysis['cells']:
        if not summary['verified'] or summary['combined_nullity']!=0:continue
        definition=next(c for c in definitions['cells'] if c['id']==summary['cell_id'])
        fixture=definition['fixture'];r=fixture['r']
        stem=summary['cell_id']+'-'+summary['arm']+'.json'
        if not any('raw/'+stem+ending in bound for ending in ('','.gz')):raise ValueError('unbound cell')
        value=load(run/'raw'/stem)
        if value['inputs_sha256']!=sha256(inputs.read_bytes()).hexdigest():raise ValueError('input binding differs')
        projection=value['projection'];system=AffineRelations(r,projection['U'])
        for row in definition['preprocessing_rows']+value['rows']:system.add(*project(row,projection,r))
        if system.rank!=projection['U']:raise ValueError('reported full rank differs')
        atoms=[]
        for j,point in enumerate(projection['unknown_points']):
            unit=[int(i==j) for i in range(projection['U'])];identified=system.identify(unit)
            if not identified.identifiable:raise ValueError('unit vector not identifiable')
            weights=list(identified.row_weights);scalar=identified.value
            check_weights(system.rows,system.rhs,unit,scalar,weights,r)
            if multiply(fixture['p'],0,fixture['a'],scalar,tuple(fixture['P']))!=tuple(point):
                raise ValueError('atom scalar fails separate public point multiplication')
            atoms.append(dict(projected_column=j,canonical_point=point,scalar=scalar,row_weights=weights,
                              unit_vector_checked=True,public_point_checked=True))
        out.append(dict(cell_id=summary['cell_id'],arm=summary['arm'],curve_uid=fixture['ec1']['curve_uid'],
                        fixture_uid=fixture['uid'],rank=system.rank,columns=projection['U'],
                        row_order='all original preprocessing rows, then all retained cell rows',
                        preprocessing_rows=len(definition['preprocessing_rows']),new_rows=len(value['rows']),atoms=atoms))
    return dict(schema='prime-field-derived-atom-log-certificates/v1',new_collection_attempts=0,
                target_labels_generated=False,d1_preprocessing_unchanged=True,
                source_export=str(run/'export.json'),source_export_sha256=sha256((run/'export.json').read_bytes()).hexdigest(),
                inputs_sha256=sha256(inputs.read_bytes()).hexdigest(),builder_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                cells=out,scope='Derived exact certificates over previously replayed finite cells; no performance or novelty claim.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True)
    p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    value=build(args.run,args.inputs);args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(path=str(args.out),full_rank_cells=len(value['cells']),checked_atoms=sum(len(c['atoms']) for c in value['cells']))))


if __name__=='__main__':main()
