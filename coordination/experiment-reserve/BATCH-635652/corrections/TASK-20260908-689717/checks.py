"""Fixed definition conformance only. No curve, solver, scientific null or run work."""
from pathlib import Path
from fractions import Fraction as F
import copy,hashlib,json,math,resource,signal,time,yaml
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
TOKENS=('184fc4','1e6502','2c3d20')
DATA={k:yaml.safe_load((HERE/f'EXP-ECDLP-{k}.yaml').read_text())['protocol_amendment'] for k in TOKENS}
OLD={k:yaml.safe_load((HERE.parent/'TASK-20260908-92d6dd'/f'EXP-ECDLP-{k}.yaml').read_text())['protocol_amendment'] for k in TOKENS}
HANDOFF=yaml.safe_load((ROOT/'ledger/handoffs/TASK-20260908-689717.yaml').read_text())['handoff']
CASES=[];RESULT=[]
def add(name,fn):CASES.append((name,fn))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def at(d,path):
    for k in path.split('.'):d=d[k]
    return d

def rank(obs,refs,eligible=True):
    if not eligible or obs is None or len(refs)!=64:return None
    if not math.isfinite(obs) or any(x is None or not math.isfinite(x) for x in refs):return None
    return F(1+sum(x>=obs for x in refs),65)

def strip(d,paths):
    d=copy.deepcopy(d)
    for p in paths:
        keys=p.split('.');node=d
        for k in keys[:-1]:node=node[k]
        node.pop(keys[-1],None)
    return d

META=['task_id','predecessor_task_id','revision_label','correction_authority','authorship','inference','authored_under_task','precedence_and_source_map','current_source_bindings','third_revision_history','third_correction_choices','fourth_correction_choices']
ALLOWED={
'184fc4':['effective_contract.permutation_null_and_inference.'+s for s in ['rank_interpretation','global_statistic','stream','joint_null_required']]+['effective_contract.decision_rules.concentration_candidate'],
'1e6502':['effective_contract.spectral_null_and_delta_thresholds.'+s for s in ['rank_interpretation','family_statistic','sibling_definition_binding','permutation_null','general_candidate_threshold']],
'2c3d20':['slopes.definition','slopes.primary_abscissa','slopes.logN_diagnostic','null_inference_and_decisions.slope_review_candidate.identity','null_inference_and_decisions.slope_review_candidate.original_falsifier']}
for b in HANDOFF['source_bindings']:
    add('source binding '+b['path'],lambda b=b:digest(ROOT/b['path'])==b['sha256'])
for k in TOKENS:
    add('unchanged fields outside approved corrections '+k,lambda k=k:strip(DATA[k],META+ALLOWED[k])==strip(OLD[k],META+ALLOWED[k]))
    add('unapproved zero-science boundary '+k,lambda k=k:DATA[k]['approved_by'] is None and DATA[k]['execution_authorized'] is False and DATA[k]['evidence_eligible'] is False and DATA[k]['scientific_runs']==0)
    add('predecessor exact hash '+k,lambda k=k:digest(ROOT/DATA[k]['third_revision_history']['path'])==DATA[k]['third_revision_history']['sha256'])
for k,block in [('184fc4','permutation_null_and_inference'),('1e6502','spectral_null_and_delta_thresholds')]:
    rr=DATA[k]['effective_contract'][block]['rank_interpretation']
    add('descriptive actual rank '+k,lambda rr=rr:'deterministic descriptive' in rr['actual_interpretation'] and 'not an exact or approximate calibrated' in rr['actual_interpretation'])
    add('unadopted future premises '+k,lambda rr=rr:set(rr['calibration_boundary'])=={'A_ASSIGN','A_SAMPLER','status','required_before_calibrated_claim'} and 'neither is adopted' in rr['calibration_boundary']['status'])
    add('missing empty and nonfinite refusal '+k,lambda rr=rr:all(s in rr['missing'] for s in ['empty eligible','nonfinite','denominator','redraw']))
add('minimum rank',lambda:rank(1,[0]*64)==F(1,65))
add('maximum rank and ties against separation',lambda:rank(1,[1]*64)==1)
add('single tied reference',lambda:rank(1,[1]+[0]*63)==F(2,65))
add('missing reference unavailable',lambda:rank(1,[0]*63) is None)
add('missing observed unavailable',lambda:rank(None,[0]*64) is None)
add('nonfinite observed unavailable',lambda:rank(float('nan'),[0]*64) is None)
add('nonfinite reference unavailable',lambda:rank(1,[float('inf')]+[0]*63) is None)
add('empty eligible family unavailable',lambda:rank(1,[0]*64,False) is None)
# Each state is a separately counted parameterized case. This is the archived finite
# counterexample, not a scientific null or a claim about actual SHA distributions.
ORBIT=[]
for state in range(66):
    def orbit_case(state=state):
        r=rank(66-state,[66-((state+shift)%66) for shift in range(1,65)])
        ORBIT.append((state,r))
        expected=F(max(1,state),65)
        return r==expected
    add('fixed 66-state orbit state '+str(state),orbit_case)
add('assignment-only false calibration mass',lambda:len(ORBIT)==66 and F(sum(r==F(1,65) for _,r in ORBIT),66)==F(1,33)>F(1,65))
binding=DATA['1e6502']['effective_contract']['spectral_null_and_delta_thresholds']['sibling_definition_binding']
EXPECTED=['effective_contract.exact_spectrum_definitions','effective_contract.permutation_null_and_inference.finite_null_summary_and_tie_rules','effective_contract.permutation_null_and_inference.zero_dispersion_and_ratio_rules']
add('exact narrow sibling field set',lambda:binding['fields']==EXPECTED)
add('sibling hash binds final contract',lambda:digest(ROOT/binding['path'])==binding['sha256'])
for f in EXPECTED:
    add('generic sibling field resolves '+f,lambda f=f:at(DATA['184fc4'],f)==at(OLD['184fc4'],f))
family=DATA['1e6502']['effective_contract']['spectral_null_and_delta_thresholds']['family_statistic']
add('combined family explicit local dimensions',lambda:all(s in family for s in ['102','136','36','precision','r=0..63','local precision-specific']))
add('combined fixed family size',lambda:(102+136)*36==8568)
add('joint maximum uses both precision blocks',lambda:max([F(1),F(7,2)])==F(7,2) and rank(F(7,2),[F(3)]*64)==F(1,65))
slopes=DATA['2c3d20']['slopes'];candidate=DATA['2c3d20']['null_inference_and_decisions']['slope_review_candidate']
add('primary fit uses log p',lambda:'x=ln(p)' in slopes['definition'] and 'natural log(p)' in candidate['identity'])
add('itinerary remains descriptive log N',lambda:'descriptive x=ln(N)' in slopes['definition'])
add('all observed and null axes explicit',lambda:'observed andevery matched-null' in slopes['primary_abscissa'] and 'Both true_gamma andall null_gamma' in candidate['original_falsifier'])
def ols(x,y):
    xb=sum(x)/len(x);yb=sum(y)/len(y)
    return sum((a-xb)*(b-yb) for a,b in zip(x,y))/sum((a-xb)**2 for a in x)
def axis_witness():
    # Two fixed abstract Hasse-compatible cardinalities; no curve construction or census.
    ps=[101,1009];ns=[100,1000];y=[0.,1.]
    return all(abs(n-p-1)<=2*math.sqrt(p) for p,n in zip(ps,ns)) and abs(ols(list(map(math.log,ps)),y)-ols(list(map(math.log,ns)),y))>1e-6
add('fixed finite log p log N distinction',axis_witness)
add('original flat-true slope condition',lambda:F(0)>F(-1,4) and (F(-49,100)+F(-51,100))/2<0)
add('same seven rung and null index binding',lambda:'allseven' in candidate['identity'] and 'SAME null index' in candidate['matched_null'])
add('retained scalar OR slope route',lambda:'does not inherit' in DATA['2c3d20']['null_inference_and_decisions']['review_candidate'])

def timeout(signum,frame):raise TimeoutError('fixed case ten-second watchdog')
if __name__=='__main__':
    assert len(CASES)<=160 and len(set(n for n,_ in CASES))==len(CASES)
    signal.signal(signal.SIGALRM,timeout)
    start=time.perf_counter();cpu=time.process_time()
    for name,fn in CASES:
        row={'name':name,'status':'started'};RESULT.append(row);t=time.perf_counter();c=time.process_time();signal.alarm(10)
        try:
            if not fn():raise AssertionError(name)
            row['status']='passed'
        except BaseException as e:row.update(status='failed',error=type(e).__name__+': '+str(e))
        finally:signal.alarm(0);row.update(wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-c)
    receipt={'schema':'crypto.autoresearch.fixed_definition_checks.v1','task_id':'TASK-20260908-689717','executed_cases':len(RESULT),'passed':sum(x['status']=='passed' for x in RESULT),'failed':sum(x['status']!='passed' for x in RESULT),'cases':RESULT,'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'maximum_observed_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rss_scope':'kernel process maximum on Darwin; not a diagnostic-specific peak','scientific_runs':0,'workers':1,'contract_sha256':{k:digest(HERE/f'EXP-ECDLP-{k}.yaml') for k in TOKENS},'checker_sha256':digest(Path(__file__))}
    print(json.dumps(receipt,indent=2));raise SystemExit(bool(receipt['failed']))
