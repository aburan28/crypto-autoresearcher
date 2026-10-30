"""Retained-row single-target certificates with explicit remaining uncertainty.

Derived analysis only: no collector, scalar search, target draw or relabelling.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from certify_bases import check_weights,multiply
from database import load,project
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations


def isolated_certificate(base,vector,offset,t,modulus):
    identified=base.identify(vector)
    if not identified.identifiable:return None
    inverse=pow(t,-1,modulus);scalar=(identified.value-offset)*inverse%modulus
    weights=[w*inverse%modulus for w in identified.row_weights]+[-inverse%modulus]
    matrix=[row+[0] for row in base.rows]+[list(vector)+[-t%modulus]]
    rhs=base.rhs+[offset];unit=[0]*base.columns+[1]
    check_weights(matrix,rhs,unit,scalar,weights,modulus)
    return dict(scalar=scalar,row_weights=weights,augmented_rank=base.rank+1,
                remaining_base_nullity=base.columns-base.rank,
                row_order='all original preprocessing rows, followed by this one target row',
                unit_vector_checked=True)


def build(run,inputs):
    export=load(run/'export.json');bound={v['path']:v for v in export['files']}
    for name,item in bound.items():
        path=(run/name).resolve();path.relative_to(run.resolve())
        if sha256(path.read_bytes()).hexdigest()!=item['sha256'] or path.stat().st_size!=item['bytes']:
            raise ValueError('source export binding differs')
    definitions=load(inputs);analysis=load(run/'analysis.json');summaries={(c['curve_uid'],c['target_index']):c for c in analysis['cells']}
    cases=[]
    for definition in definitions['cells']:
        fixture=definition['fixture'];r=fixture['r']
        for index in definition['target_indices']:
            summary=summaries[(fixture['uid'],index)]
            result=dict(fixture_uid=fixture['uid'],curve_uid=definition['target_curve_uid'],target_index=index,status=summary['status'],isolated=None)
            cases.append(result)
            if not summary['verified']:continue
            stem=fixture['uid']+'-target-'+str(index)+'.json'
            if not any('raw/'+stem+end in bound for end in ('','.gz')):raise ValueError('unbound target result')
            value=load(run/'raw'/stem)
            if value['inputs_sha256']!=sha256(inputs.read_bytes()).hexdigest():raise ValueError('input binding differs')
            base=AffineRelations(r,value['projection']['U'])
            for row in definition['preprocessing_rows']:base.add(*project(row,value['projection'],r))
            accepted=[i+1 for i,status in enumerate(''.join(block['statuses'] for block in value['status_blocks'])) if status=='+']
            if len(accepted)!=len(value['rows']):raise ValueError('accepted status count differs')
            result.update(target=value['target'],base_rank=base.rank,base_columns=base.columns,
                          first_combined_augmented_rank=None if value['first_combined_recovery'] is None else value['first_combined_recovery']['certificate']['augmented_rank'])
            for j,row in enumerate(value['rows']):
                vector,offset=project(row,value['projection'],r)
                certificate=isolated_certificate(base,vector,offset,row['target_coefficient'],r)
                if certificate is None:continue
                if multiply(fixture['p'],0,fixture['a'],certificate['scalar'],tuple(fixture['P']))!=tuple(value['target']):
                    raise ValueError('target scalar fails separate public point multiplication')
                certificate.update(target_row_index=j,attempt=accepted[j],old_kernel_syndrome=list(base.identify(vector).syndrome),public_point_checked=True)
                t=row['target_coefficient'];multiple=multiply(fixture['p'],0,fixture['a'],t,tuple(value['target']));matches=[]
                for s in definition['source_order']:
                    public=multiply(fixture['p'],0,fixture['a'],s,tuple(fixture['P']))
                    if multiple==public:matches.append(dict(public_source_scalar=s,sign=1))
                    if multiple==(public[0],-public[1]%fixture['p']):matches.append(dict(public_source_scalar=s,sign=-1))
                certificate.update(multiplier=t,public_multiple=None if multiple is None else list(multiple),
                    public_multiplier_source_matches=matches,
                    multiplier_match_scope='Post-hoc public-point diagnostic; target recipe/primary result unchanged, no target filtering. A known-source collision is not evidence of a new descent mechanism.')
                result['isolated']=certificate;break
            if (result['isolated'] is None)!=(value['first_single_recovery'] is None):raise ValueError('native isolated result differs')
            if result['isolated'] is not None and any(result['isolated'][k]!=value['first_single_recovery'][k] for k in ('attempt','scalar')):
                raise ValueError('native isolated prefix/scalar differs')
    return dict(schema='prime-field-derived-isolated-target-certificates/v1',new_collection_attempts=0,
        source_export_sha256=sha256((run/'export.json').read_bytes()).hexdigest(),inputs_sha256=sha256(inputs.read_bytes()).hexdigest(),
        builder_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),cases=cases,
        interpretation='An isolated certificate uses only original M plus one naturally generated target row. Rank is rank(M)+1; base nullity remains U-rank(M). First combined prefix rank is a distinct observation. All frozen cases retained.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    value=build(a.run,a.inputs);a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(cases=len(value['cases']),isolated_certificates=sum(c['isolated'] is not None for c in value['cases']))))


if __name__=='__main__':main()
