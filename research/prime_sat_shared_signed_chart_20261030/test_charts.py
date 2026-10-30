"""Only the preregistered fixed software cases; no fixture discovery or solver."""
import argparse,copy,datetime,hashlib,json,signal,traceback
from pathlib import Path
import quotient as q
import charts,projectors,signed_recovery,check_chart

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CONTRACT=ROOT/'coordination/prime_sat_shared_signed_chart_20261030/fixed-software-contract.json'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    out=Path(args.output);q.require(out.resolve()==HERE/'software-results.json','owned result path')
    contract=json.loads(CONTRACT.read_text())
    prior=json.loads(out.read_text()) if out.exists() else {'schema':'prime-shared-chart-software-results/v1','attempts':[]}
    q.require(len(prior['attempts'])<contract['producer_maximum_suite_attempts'],'fixed suite attempt allowance')
    sources={p.name:p.read_text() for p in HERE.iterdir() if p.suffix in ('.py','.md')}
    hashes={name:hashlib.sha256(text.encode()).hexdigest() for name,text in sources.items()}
    attempt={'attempt':len(prior['attempts'])+1,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running','source_sha256':hashes,'source_snapshot':sources,'contract_sha256':hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),'assertions':[],'chart_cases':[],'projector_cases':[],'events':{},'scientific_runs':0,'solver_invocations':0,'remote_jobs':0}
    prior['attempts'].append(attempt)
    def save():
        attempt['events']=dict(q.EVENTS);out.write_text(json.dumps(prior,indent=2,sort_keys=True)+'\n')
    def record(name,holds,detail=None):
        attempt['assertions'].append({'name':name,'holds':bool(holds),'detail':detail});save()
    def rejection(name,fn):
        try:fn()
        except q.ObligationError as error:record(name,True,str(error))
        except Exception as error:record(name,False,{'unexpected':type(error).__name__,'message':str(error)})
        else:record(name,False,'invalid value accepted')
    def alarm(*args):raise TimeoutError('fixed suite watchdog')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(contract['suite_watchdog_seconds']);save();cache={}
    try:
        for fixture in contract['chart_fixtures']:
            name=fixture['id'];curve={key:fixture[key] for key in ['p','a','b']};interval={key:fixture[key] for key in ['t','s']}
            entry={'id':name,'expected':fixture['expected']};attempt['chart_cases'].append(entry)
            try:
                if fixture['expected'].startswith('reject'):
                    rejection(name,lambda:charts.construct_from_signed_multiset(curve,interval,fixture['points'],fixture['target']));entry['status']='rejection_checked';continue
                w=charts.construct_from_signed_multiset(curve,interval,fixture['points'],fixture['target'])
                cert=projectors.recover_interval_factors(w['U'],fixture['t'],fixture['s'],w['e']);w['factors']=cert
                recovered=signed_recovery.recover_signed_divisor(curve,w['target'],w['A'],w['B'],w['U'],cert,w['root_lifts'])
                expected=sorted(fixture['points'])+[None]*(5-len(fixture['points']))
                verdict=check_chart.check_chart(w,recovered)
                record(name+'.exact_multiset',recovered==expected,{'actual':recovered,'expected':expected})
                record(name+'.independent_series_checker',verdict['status']=='valid',verdict)
                record(name+'.quotient_equations',q.verify_quotient_witness(w['U'],fixture['t'],fixture['s'],w['e'],curve))
                entry.update(status='checked',witness=w,recovered=recovered,checker=verdict);cache[name]=(w,recovered)
                if name=='finite_five_characteristic5':record(name+'.literal_chart',w['A']==[2,0,0,1] and w['B']==[3] and w['U']['coeffs']==[0,0,0,0,0,1])
                if name=='identity_five_two_torsion':record(name+'.literal_chart',w['A']==[3,6] and w['B']==[4,1] and w['U']['coeffs']==[0,0,0,2,1,1])
                if name=='wrapped_five_balanced':record(name+'.literal_chart',w['A']==[0,0,1,1] and w['B']==[0])
                if name=='target_outside_interval':record(name+'.literal_chart',w['A']==[4,2] and w['B']==[1] and w['U']['coeffs']==[0,0,1])
            except Exception as error:
                entry.update(status='error',traceback=traceback.format_exc());record(name+'.unexpected_exception',False,{'type':type(error).__name__,'message':str(error)})
            finally:save()
        for fixture in contract['projector_fixtures']:
            name=fixture['id'];U={'p':fixture['p'],'coeffs':fixture['U']};entry={'id':name};attempt['projector_cases'].append(entry)
            try:
                if fixture.get('expected','').startswith('reject'):
                    rejection('projector.'+name,lambda:projectors.recover_interval_factors(U,fixture['t'],fixture['s'],fixture['e']));entry['status']='rejection_checked'
                else:
                    certificate=projectors.recover_interval_factors(U,fixture['t'],fixture['s'],fixture['e'])
                    record('projector.'+name,certificate['factors']==fixture['expected_factors'],certificate)
                    record('projector.'+name+'.factor_certificate',projectors.check_factor_certificate(U,certificate))
                    entry.update(status='checked',certificate=certificate)
            except Exception as error:entry.update(status='error',traceback=traceback.format_exc());record('projector.'+name+'.unexpected_exception',False,str(error))
            finally:save()
        # Literal mutations named by the fixed contract, not discovered instances.
        U={'p':5,'coeffs':[1,3,1]};n=q.rem([4,1],U['coeffs'],5)
        record('mutation.nilpotence_not_equality',n!=[0] and q.powmod(n,2,U['coeffs'],5)==[0] and q.verify_quotient_witness(U,0,1,[[1]]))
        bad={'p':5,'t':0,'s':1,'factors':[[1,0]]}
        rejection('mutation.trace_not_dimension',lambda:projectors.check_factor_certificate({'p':5,'coeffs':[4,0,0,0,0,1]},bad))
        rejection('mutation.changed_idempotent',lambda:projectors.recover_interval_factors(U,0,1,[[0]]))
        rejection('mutation.late_boolean_coefficient',lambda:projectors.recover_interval_factors(U,0,1,[[1,True]]))
        record('mutation.nonsquare_interval_passes',q.verify_quotient_witness(U,0,1,[[1]]))
        rejection('mutation.nonsquare_rationality_rejects',lambda:q.verify_quotient_witness(U,0,1,[[1]],{'p':5,'a':1,'b':1}))
        def output_mutation(case,name,transform):
            w,rec=cache[case];bad=copy.deepcopy(rec);transform(bad);v=check_chart.check_chart(w,bad)
            record(name,v['status']=='invalid',v)
        output_mutation('finite_one','mutation.subtract_R_not_negative_R',lambda x:x.__setitem__(0,[0,4]))
        output_mutation('identity_two_inverse','mutation.collapse_opposite_sign',lambda x:x.__setitem__(1,[0,1]))
        output_mutation('identity_four','mutation.drop_common_contribution',lambda x:x.__setitem__(3,None))
        output_mutation('finite_two_torsion','mutation.duplicate_branch_sign',lambda x:x.__setitem__(1,[3,0]))
        w,rec=cache['target_outside_interval'];original=signed_recovery.norm_support
        try:
            signed_recovery.norm_support=lambda factors,target:list(factors['factors'])
            rejection('mutation.drop_outside_target',lambda:signed_recovery.recover_signed_divisor(w['curve'],w['target'],w['A'],w['B'],w['U'],w['factors'],w['root_lifts']))
        finally:signed_recovery.norm_support=original
        w,rec=cache['finite_one']
        mutations=[('norm_coefficient',lambda z:z['A'].__setitem__(0,1)),('leading_modulus',lambda z:z['U']['coeffs'].__setitem__(-1,2)),('factor_multiplicity',lambda z:z['factors']['factors'][0].__setitem__(1,2)),('target_ordinate',lambda z:z['target'].__setitem__(1,2)),('boolean_arity',lambda z:z.__setitem__('k',True)),('boolean_interval',lambda z:z['interval'].__setitem__('t',False)),('wrong_factor_interval',lambda z:z['factors'].__setitem__('t',1)),('trailing_idempotent_zero',lambda z:z.__setitem__('e',[[0,0]])),('wrong_quotient_field',lambda z:z['U'].__setitem__('p',7)),('wrong_factor_field',lambda z:z['factors'].__setitem__('p',7))]
        for name,change in mutations:
            bad=copy.deepcopy(w);change(bad);v=check_chart.check_chart(bad,rec);record('mutation.'+name,v['status']=='invalid',v)
        record('inventory.chart_cases',len(attempt['chart_cases'])==15)
        record('inventory.projector_cases',len(attempt['projector_cases'])==8)
    except Exception as error:
        record('suite_exception',False,{'type':type(error).__name__,'traceback':traceback.format_exc()})
    finally:
        signal.alarm(0)
        after={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in sources}
        attempt['after_source_sha256']=after
        record('source_immutability',after==hashes)
        record('contract_immutability',hashlib.sha256(CONTRACT.read_bytes()).hexdigest()==attempt['contract_sha256'])
        attempt['status']='passed' if all(x['holds'] for x in attempt['assertions']) else 'failed'
        attempt['ended_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
    print(json.dumps({'attempt':attempt['attempt'],'status':attempt['status'],'assertions':len(attempt['assertions']),'failures':[x for x in attempt['assertions'] if not x['holds']],'chart_cases':len(attempt['chart_cases']),'projector_cases':len(attempt['projector_cases'])},indent=2))
    return 0 if attempt['status']=='passed' else 1


if __name__=='__main__':raise SystemExit(main())
