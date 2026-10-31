"""Only admitted fixed fixtures and named corruptions; every suite attempt retained."""
import argparse,copy,datetime,hashlib,json,signal,traceback
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CONTRACT=ROOT/'coordination/prime_sat_rationality_software_20261031/fixed-software-contract.json'
BASE=HERE.parent/'prime_sat_shared_signed_chart_20261030'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    out=Path(args.output)
    if out.resolve()!=HERE/'software-results.json':raise ValueError('owned output only')
    contract=json.loads(CONTRACT.read_text())
    data=json.loads(out.read_text()) if out.exists() else {'schema':'prime-rationality-fixed-software-results/v1','attempts':[]}
    if len(data['attempts'])>=contract['maximum_suite_attempts']:raise ValueError('suite attempt allowance')
    sources={p.name:p.read_text() for p in HERE.iterdir() if p.suffix in ('.py','.md')}
    hashes={n:hashlib.sha256(s.encode()).hexdigest() for n,s in sources.items()}
    base_hashes={n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in ['quotient.py','charts.py','projectors.py','signed_recovery.py','check_chart.py']}
    attempt={'attempt':len(data['attempts'])+1,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running','source_snapshot':sources,'source_sha256':hashes,'base_sha256':base_hashes,'contract_sha256':hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),'assertions':[],'chart_cases':[],'guard_cases':[],'nilpotent_cases':[],'F1_cases':[],'scientific_runs':0,'solver_instances':0,'remote_jobs':0}
    data['attempts'].append(attempt)
    def save():out.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    def record(name,holds,detail=None):
        attempt['assertions'].append({'name':name,'holds':bool(holds),'detail':detail});save()
    def reject(name,fn):
        try:
            result=fn();record(name,type(result) is dict and result.get('status')=='invalid',result)
        except Exception as error:record(name,False,{'unexpected_exception':type(error).__name__,'message':str(error)})
    def alarm(*args):raise TimeoutError('fixed suite watchdog')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(contract['suite_watchdog_seconds']);save()
    try:
        import rationality as rat
        import checker as ck
        import quotient as q
        import charts,projectors,signed_recovery
        arms=contract['arms'][1:]
        cache={};examples={}
        def expected(kind,k,curve,inputs):
            return {'p':curve['p'],'curve':{'a':curve['a'],'b':curve['b']},'kind':kind,'k':k,'inputs':inputs,'projection':list(inputs)}
        for fixture in contract['chart_fixtures']:
            name=fixture['id'];curve={k:fixture[k] for k in ['p','a','b']};interval={k:fixture[k] for k in ['t','s']}
            row={'id':name,'expected':fixture['expected'],'arms':[]};attempt['chart_cases'].append(row)
            try:
                if fixture['expected'].startswith('reject'):
                    try:charts.construct_from_signed_multiset(curve,interval,fixture['points'],fixture['target'])
                    except q.ObligationError as error:record(name+'.impossible_chart_rejected',True,str(error))
                    except Exception as error:record(name+'.impossible_chart_rejected',False,{'unexpected':str(error)})
                    else:record(name+'.impossible_chart_rejected',False,'accepted impossible chart')
                    row['status']='rejection_checked';continue
                w=charts.construct_from_signed_multiset(curve,interval,fixture['points'],fixture['target'])
                target=sorted(fixture['points'])+[None]*(5-len(fixture['points']))
                ref=ck.reference_check(w,target);record(name+'.full_euler_reference',ref['status']=='valid',ref)
                for arm in arms:
                    candidate=rat.construct_auxiliaries_from_checked_chart(w,target,arm)
                    verdict=ck.check_candidate_chart(w,candidate)
                    record(name+'.'+arm+'.candidate',verdict['status']=='valid',verdict)
                    record(name+'.'+arm+'.signed_projection',ck.same(candidate['recovered'],target))
                    row['arms'].append({'arm':arm,'candidate_status':verdict['status'],'reference_status':ref['status'],'block_sha256':digest(candidate['block']),'recovered':candidate['recovered'],'counts':verdict.get('counts')})
                    cache[(name,arm)]=(w,candidate)
                    if arm=='uniform_nilpotent_square':
                        k=w['k'];counts=verdict.get('counts',{})
                        record(name+'.nilpotent_symbolic_count',counts.get('auxiliaries')==[0,3,9,15,21,36][k] and counts.get('equations')==[0,3,9,15,21,36][k],counts)
                        examples[k]=candidate['block']
                row['status']='checked'
            except Exception as error:row['status']='error';record(name+'.unexpected',False,traceback.format_exc())
            finally:save()
        record('coverage.nilpotent_k0_to_5',set(examples)==set(range(6)),sorted(examples))
        for fixture in contract['nilpotent_fixtures']:
            name=fixture['id'];curve={k:fixture[k] for k in ['p','a','b']};k=len(fixture['U'])-1
            block=rat.nilpotent_square_block(k,curve['p'],curve['a'],curve['b'],fixture['U'],fixture['C'])
            exp=expected('nilpotent',k,curve,{'u'+str(i):v for i,v in enumerate(fixture['U'][:-1])})
            verdict=ck.check_assignment(block['circuit'],block['assignment'],exp)
            record('nilpotent.'+name,verdict['status']==('valid' if fixture['valid'] else 'invalid'),verdict)
            attempt['nilpotent_cases'].append({'id':name,'expected_valid':fixture['valid'],'status':verdict['status'],'block_sha256':digest(block)})
            if name=='repeated_branch':
                exact=q.rem(q.sub(q.mul(fixture['C'],fixture['C'],curve['p']),[curve['b'],curve['a'],0,1],curve['p']),fixture['U'],curve['p'])
                record('control.exact_square_rejects_repeated_branch',exact!=[0],exact)
        for fixture in contract['guard_fixtures']:
            name=fixture['id'];p=fixture['p'];curve={'p':p,'a':1,'b':fixture['F']}
            inputs={'A0':fixture['c'],'A1':0,'A2':0,'A3':0,'b0':0,'b1':1}
            block=rat.linear_B_square_block(p,1,fixture['F'],'guard',[fixture['c']],[0,1],fixture['beta'])
            for key in ['e','u','beta']:block['assignment'][key]=fixture[key]
            exp=expected('guard',None,curve,inputs)
            verdict=ck.check_assignment(block['circuit'],block['assignment'],exp)
            record('guard.'+name,verdict['status']==('valid' if fixture['valid'] else 'invalid'),verdict)
            slack=rat.linear_B_square_block(p,1,fixture['F'],'slack',[fixture['c']],[0,1],fixture['beta'])
            sv=ck.check_assignment(slack['circuit'],slack['assignment'],expected('slack',None,curve,inputs))
            predicate=fixture['c']!=0 or fixture['beta']**2%p==fixture['F']
            record('slack.'+name,sv['status']==('valid' if predicate else 'invalid'),sv)
            attempt['guard_cases'].append({'id':name,'guard_status':verdict['status'],'slack_status':sv['status']})
        # The literal F1 construction is part of the frozen contract, not fixture discovery.
        f1=contract['signed_recovery_regressions'][0];curve={k:f1[k] for k in ['p','a','b']}
        pts=[[0,1]]*4+[[0,4]];w=charts.construct_from_signed_multiset(curve,{'t':0,'s':0},pts,None)
        record('F1.literal_chart',w['A']==f1['A'] and w['B']==f1['B'] and w['U']['coeffs']==f1['U'])
        identities=[]
        for beta in f1['guard_beta_values']:
            cand=rat.construct_auxiliaries_from_checked_chart(w,pts,'stratified_guard_with_nilpotent_zero_B',beta)
            v=ck.check_candidate_chart(w,cand);ref=ck.reference_check(w,cand['recovered'])
            record('F1.beta'+str(beta),v['status']=='valid' and ref['status']=='valid' and ck.same(cand['recovered'],pts),{'candidate':v,'reference':ref})
            identities.append(cand['chart']);attempt['F1_cases'].append({'beta':beta,'recovered':cand['recovered'],'candidate_status':v['status'],'reference_status':ref['status']})
            bad=copy.deepcopy(cand);bad['recovered']=[[0,1]]+[[0,4]]*4
            reject('F1.swapped_multiplicities.beta'+str(beta),lambda:ck.check_candidate_chart(w,bad))
            reject('F1.reference_swapped.beta'+str(beta),lambda:ck.reference_check(w,bad['recovered']))
            bad=copy.deepcopy(cand);bad['recovered']=[[0,1]]*2+[[0,4]]*2+[None]
            reject('F1.balanced_substitution.beta'+str(beta),lambda:ck.check_candidate_chart(w,bad))
        record('F1.identical_normalized_projection',ck.same(identities[0],identities[1]))
        # Every mutation is explicitly prescribed and operates on a fixed example.
        w, cand=cache[('finite_five_characteristic5','uniform_nilpotent_square')]
        block=cand['block'];exp=expected('nilpotent',w['k'],w['curve'],{'u'+str(i):v for i,v in enumerate(w['U']['coeffs'][:-1])})
        def mutate_block(name,change):
            bad=copy.deepcopy(block);change(bad)
            reject('mutation.'+name,lambda:ck.check_assignment(bad['circuit'],bad['assignment'],exp))
        mutate_block('quotient',lambda z:z['assignment'].__setitem__('C2.Q0',(z['assignment']['C2.Q0']+1)%5))
        mutate_block('remainder',lambda z:z['assignment'].__setitem__('C2.P0',(z['assignment']['C2.P0']+1)%5))
        late=block['circuit']['auxiliaries'][-1]
        mutate_block('late_noncanonical',lambda z:z['assignment'].__setitem__(late,5))
        mutate_block('late_boolean',lambda z:z['assignment'].__setitem__(late,True))
        mutate_block('missing_assignment',lambda z:z['assignment'].pop(late))
        mutate_block('unknown_assignment',lambda z:z['assignment'].__setitem__('unknown',0))
        mutate_block('duplicate_variable',lambda z:z['circuit']['auxiliaries'].append(late))
        mutate_block('undeclared_monomial',lambda z:z['circuit']['equations'][0]['terms'][0].__setitem__('variables',['undeclared']))
        mutate_block('projection',lambda z:z['circuit']['projection'].pop())
        mutate_block('field_binding',lambda z:z['circuit'].__setitem__('p',7))
        mutate_block('unknown_schema_field',lambda z:z['circuit'].__setitem__('cached_valid',True))
        mutate_block('missing_equation',lambda z:z['circuit']['equations'].pop())
        fw=charts.construct_from_signed_multiset({'p':5,'a':0,'b':1},{'t':0,'s':0},pts,None)
        gc=rat.construct_auxiliaries_from_checked_chart(fw,pts,'stratified_guard_with_nilpotent_zero_B',1)
        bad=copy.deepcopy(gc);bad['block']['assignment']['e']=0
        reject('mutation.guard',lambda:ck.check_candidate_chart(fw,bad))
        bad=copy.deepcopy(gc);bad['stratum']='zero'
        reject('mutation.stratum',lambda:ck.check_candidate_chart(fw,bad))
        bad=copy.deepcopy(gc);bad['chart']['A'][1]=True
        reject('mutation.chart_boolean_binding',lambda:ck.check_candidate_chart(fw,bad))
        record('coverage.chart_fixtures',len(attempt['chart_cases'])==15)
        record('coverage.guard_fixtures',len(attempt['guard_cases'])==8)
        record('coverage.nilpotent_fixtures',len(attempt['nilpotent_cases'])==8)
        record('coverage.F1_both_signs',len(attempt['F1_cases'])==2)
        attempt['events']={'candidate':dict(rat.EVENTS),'checker':dict(ck.EVENTS),'shared_arithmetic':dict(q.EVENTS)}
    except Exception:
        record('suite_exception',False,traceback.format_exc())
    finally:
        signal.alarm(0)
        after={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in sources}
        attempt['after_source_sha256']=after
        record('source_immutability',after==hashes)
        after_base={n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in base_hashes}
        record('base_immutability',after_base==base_hashes)
        record('contract_immutability',hashlib.sha256(CONTRACT.read_bytes()).hexdigest()==attempt['contract_sha256'])
        attempt['status']='passed' if all(x['holds'] for x in attempt['assertions']) else 'failed'
        attempt['ended_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
    failures=[x for x in attempt['assertions'] if not x['holds']]
    print(json.dumps({'attempt':attempt['attempt'],'status':attempt['status'],'assertions':len(attempt['assertions']),'failures':failures},indent=2))
    return 0 if not failures else 1


if __name__=='__main__':raise SystemExit(main())
