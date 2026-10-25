"""Independent hiding-commitment, output-seal and final ECDLP checks."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'research/prym_experiment_design_20261019/implementation'))
from independent import dense_rank,multiply,verify_fixture,verify_row


def check_projection(fixture,output,public_source_bound):
    declared=output['projection'];r=fixture['r'];p=fixture['p'];a=fixture['a'];P=tuple(fixture['P']);known={}
    for derivation in declared['public_derivations']:
        j=derivation['column'];value=derivation['scalar'];source=derivation['derived_from_public_source_scalar']
        if not 1<=source<=min(public_source_bound,r-1) or value!=derivation['sign']*source%r:
            raise ValueError('undeclared public anchor schedule')
        if multiply(p,0,a,value,P)!=tuple(fixture['factor_base'][j]['point']):raise ValueError('false public anchor')
        known[j]=value
    unknown=[j for j in range(len(fixture['factor_base'])) if j not in known];M=[];aug=[]
    for row in output['source_rows']:
        verify_row(fixture,row);values=[row['coefficients'][j] for j in unknown]
        rhs=(row['source_scalar']-sum(row['coefficients'][j]*value for j,value in known.items()))%r
        M.append(values);aug.append(values+[rhs])
    rank=dense_rank(M,r);augmented=dense_rank(aug,r)
    if (len(unknown),rank,augmented)!=(declared['U'],declared['rank'],declared['augmented_rank']):
        raise ValueError('independent recovery rank mismatch')
    solution=declared['solution']
    if solution is not None:
        if rank!=len(unknown) or len(solution)!=len(unknown):raise ValueError('invalid solution size/rank')
        for j,value in zip(unknown,solution):
            if multiply(p,0,a,value,P)!=tuple(fixture['factor_base'][j]['point']):raise ValueError('false recovered base log')


def check_challenge(fixture,record,require_isolation=True,public_source_bound=64):
    verify_fixture(fixture)
    revealed=record['reveal_after_outputs'];k,salt=revealed['k'],revealed['salt'];identifier=record['challenge_id']
    commitment=sha256(f'prym-E/v1|{identifier}|{salt}|{k}'.encode()).hexdigest()
    if len(salt)!=64 or commitment!=record['commitment_before_attack']:raise ValueError('hiding commitment mismatch')
    Q=tuple(record['Q'])
    if not 0<k<fixture['r'] or multiply(fixture['p'],0,fixture['a'],k,tuple(fixture['P']))!=Q:
        raise ValueError('challenge/source mismatch')
    checked=[]
    for item in record['sealed_outputs']:
        text=item['sealed_output_utf8']
        if sha256(text.encode()).hexdigest()!=item['sealed_output_sha256'] or json.loads(text)!=item['output']:
            raise ValueError('attack output seal mismatch')
        output=item['output'];guess=output.get('k');verified=guess is not None and 0<guess<fixture['r'] and guess==k
        if require_isolation:
            isolation=output.get('isolation',{})
            if isolation.get('landlock_abi',0)<4 or isolation.get('fallback_used') is not False:
                raise ValueError('required worker isolation was not established')
        if guess is not None and not verified:raise ValueError('incorrect attack answer')
        if verified and multiply(fixture['p'],0,fixture['a'],guess,tuple(fixture['P']))!=Q:
            raise ValueError('final independent source check failed')
        if verified!=item['verified']:raise ValueError('verification flag mismatch')
        f=deepcopy(fixture);target=Q
        if item['arm']=='coordinate':
            p=f['p'];f['P'][1]=-f['P'][1]%p;target=(Q[0],-Q[1]%p)
            for atom in f['factor_base']:
                atom['point'][1]=-atom['point'][1]%p;atom['lift'][1]=-atom['lift'][1]%p
        if 'projection' in output:
            check_projection(f,output,public_source_bound)
        witness=output.get('descent_witness')
        if witness is not None:
            if not witness.get('target_coefficient',0)%f['r']:raise ValueError('noninvertible recovery multiplier')
            verify_row(f,witness,target=target)
        checked.append({'arm':item['arm'],'seed':item['seed'],'verified':verified,'status':output['status']})
    return checked


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,required=True);parser.add_argument('--run-dir',type=Path,required=True);args=parser.parse_args()
    config=json.loads(args.config.read_text());root=Path(__file__).resolve().parents[2];panel=json.loads((root/config['fixture_file']).read_text());fixtures={v['uid']:v for v in panel['fixtures']}
    path=args.run_dir/'raw-result.json';result=json.loads(path.read_text());failed=[];checks=[]
    try:
        if not result.get('complete') or len(result['challenges'])!=len(fixtures):raise ValueError('incomplete fixed challenge panel')
        if {v['curve_uid'] for v in result['challenges']}!=set(fixtures):raise ValueError('missing/duplicate fresh instance')
        for record in result['challenges']:
            expected={(arm,seed) for arm in config['arms'] for seed in config['seeds']}
            actual=[(v['arm'],v['seed']) for v in record['sealed_outputs']]
            if len(actual)!=len(expected) or set(actual)!=expected:raise ValueError('incomplete paired arm/seed workload')
            algorithm=config['algorithm']
            bound=max(algorithm['public_source_max'],algorithm.get('selector_training',{}).get('public_source_max',0) if algorithm.get('use_selector') else 0)
            checks.append(check_challenge(fixtures[record['curve_uid']],record,public_source_bound=bound))
    except Exception as exc:failed.append(repr(exc))
    with (args.run_dir/'verification.json').open('x') as stream:json.dump({'schema':'prym-blind-recovery-check/v1','status':'failed' if failed else 'passed','failed_checks':failed,'checks':checks,'raw_result_sha256':sha256(path.read_bytes()).hexdigest(),'complete_S_verified':False,'limits':['No release of matched-cost gain without independently verified complete weights, setup and workload.']},stream,indent=2)
    return bool(failed)

if __name__=='__main__':raise SystemExit(main())
