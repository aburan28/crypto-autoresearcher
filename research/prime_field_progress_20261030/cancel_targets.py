"""Post-hoc base-only scoring of natural target rows as one-outside-point partials.

This reuses immutable D1 witnesses. It does not collect residual-point partials
or provide target scalar labels to cancellation.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from time import process_time_ns

from flint import nmod_mat
from certify_bases import multiply,check_weights
from database import load,project
from independent import add
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations,cancel_outside


def dense_gain(base,B,U):
    p=base.modulus;outside=len(U[0]) if U else 0
    rank_u=nmod_mat(U,p).rank() if U else 0
    matrix=[row+[0]*outside for row in base.rows]+[b+u for b,u in zip(B,U)]
    stacked=nmod_mat(matrix,p).rank() if matrix else 0
    return dict(stacked_rank=stacked,outside_rank=rank_u,base_rank=base.rank,delta=stacked-rank_u-base.rank)


def verify_cancellation(B,U,rhs,certificate,modulus):
    weights=certificate['partial_row_weights'];vector=certificate['coefficients'];value=certificate['rhs']
    check_weights(B,rhs,vector,value,weights,modulus)
    if any(sum(w*u[j] for w,u in zip(weights,U))%modulus for j in range(len(U[0]) if U else 0)):
        raise ValueError('outside-point column did not cancel')


def build(run,inputs):
    started=process_time_ns();export=load(run/'export.json');bound={v['path']:v for v in export['files']}
    for name,item in bound.items():
        path=(run/name).resolve();path.relative_to(run.resolve())
        if sha256(path.read_bytes()).hexdigest()!=item['sha256'] or path.stat().st_size!=item['bytes']:
            raise ValueError('source export binding differs')
    definitions=load(inputs);analysis=load(run/'analysis.json');summaries={(c['curve_uid'],c['target_index']):c for c in analysis['cells']}
    cases=[]
    for definition in definitions['cells']:
        fixture=definition['fixture'];p,r=fixture['p'],fixture['r']
        for index in definition['target_indices']:
            summary=summaries[(fixture['uid'],index)]
            result=dict(fixture_uid=fixture['uid'],curve_uid=definition['target_curve_uid'],target_index=index,status=summary['status'],score=None)
            cases.append(result)
            if not summary['verified']:continue
            stem=fixture['uid']+'-target-'+str(index)+'.json'
            if not any('raw/'+stem+end in bound for end in ('','.gz')):raise ValueError('unbound target result')
            value=load(run/'raw'/stem)
            if value['inputs_sha256']!=sha256(inputs.read_bytes()).hexdigest():raise ValueError('input binding differs')
            start=process_time_ns();base=AffineRelations(r,value['projection']['U'])
            for row in definition['preprocessing_rows']:base.add(*project(row,value['projection'],r))
            projected=[project(row,value['projection'],r) for row in value['rows']]
            B=[v for v,b in projected];rhs=[b for v,b in projected];U=[[-row['target_coefficient']%r] for row in value['rows']]
            construction=process_time_ns()-start;start=process_time_ns()
            cancelled=cancel_outside(base,B,U,rhs);elimination=process_time_ns()-start;start=process_time_ns()
            oracle=dense_gain(base,B,U)
            if (oracle['delta'],oracle['outside_rank'])!=(cancelled['rank_gain'],cancelled['outside_rank']):raise ValueError('dense rank identity differs')
            oracle_time=process_time_ns()-start;start=process_time_ns()
            for certificate in cancelled['cancellations']:
                verify_cancellation(B,U,rhs,certificate,r)
                point=None
                for c,atom in zip(certificate['coefficients'],value['projection']['unknown_points']):
                    point=add(p,0,fixture['a'],point,multiply(p,0,fixture['a'],c,tuple(atom)))
                if point!=multiply(p,0,fixture['a'],certificate['rhs'],tuple(fixture['P'])):
                    raise ValueError('cancelled base equation fails separate public point check')
            checking=process_time_ns()-start
            charged=summary['attempts']+summary['verification_attempts'];ratio=Fraction(cancelled['rank_gain'],charged) if charged else None
            result.update(target=value['target'],score=oracle,cancellation=cancelled,
                verified_cancellation_equations=len(cancelled['cancellations']),public_point_checks=True,
                charged_collection_branches=summary['attempts'],charged_replay_branches=summary['verification_attempts'],
                delta_per_collection_and_replay_branch=None if ratio is None else dict(numerator=ratio.numerator,denominator=ratio.denominator),
                diagnostic_cpu_ns=dict(construction=construction,outside_elimination_and_extraction=elimination,dense_oracle=oracle_time,certificate_and_point_checks=checking))
    return dict(schema='prime-field-derived-target-partials/v1',new_collection_attempts=0,target_scalar_labels_used=False,
        source_export_sha256=sha256((run/'export.json').read_bytes()).hexdigest(),inputs_sha256=sha256(inputs.read_bytes()).hexdigest(),
        builder_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),cases=cases,total_diagnostic_cpu_ns=process_time_ns()-started,
        score_identity='rank([[M,0],[B,-t]])-rank(-t)-rank(M); carried original partial-row weights cancel the outside target column',
        scope='Post-hoc reuse of a fixed independently hashed target panel, one outside column per case, all outcomes retained. Branch charge is an exact work count, not complete S. CPU clocks are shared-host diagnostics. No residual-outside collector, scalable speedup, holdout result or scientific promotion is claimed.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    value=build(a.run,a.inputs);a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(cases=len(value['cases']),scores=[c['score'] for c in value['cases']]),sort_keys=True))


if __name__=='__main__':main()
