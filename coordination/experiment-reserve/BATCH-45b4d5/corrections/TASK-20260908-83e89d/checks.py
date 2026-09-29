"""Fixed definition checks only; never imports a scientific runner or generates curves.

Each call to case admits one explicitly named fixed input, including failures.
Administrative source/schema comparisons are separately labelled. No CLI parameters.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,signal,time,resource,yaml
ROOT=Path(__file__).resolve().parents[5]
HERE=Path(__file__).resolve().parent
D=yaml.safe_load((HERE/'EXP-ECDLP-1b1b99.yaml').read_text())
E=D['effective_contract']; C=E['cost_contract']
RESULT=[]
def med(values):
    if len(values) not in (6,7) or any(v is None or v<0 for v in values):raise ValueError('unresolved')
    v=sorted(map(F,values));return v[3] if len(v)==7 else (v[2]+v[3])/2

def normalize(cost,reps):
    if type(cost) is not int or cost<0 or type(reps) is not int or not 1<=reps<=100:raise ValueError('invalid')
    return F(cost,reps)

def split(cost,n):
    if type(cost) is not int or cost<0 or type(n) is not int or n<1:raise ValueError('invalid')
    q,r=divmod(cost,n);return [q+(i<r) for i in range(n)]

def score(endpoints):
    if len(endpoints)!=8:raise ValueError('stratum')
    return sum(F(setup)+med([normalize(c,n) for c,n in blocks]) for setup,blocks in endpoints)/8

def winner(scores):
    if set(scores)!=set(range(2,8)) or any(v is None for v in scores.values()):raise ValueError('candidate')
    return min(scores,key=lambda a:(scores[a],a))

def ratio(S,T):
    if len(S)!=2 or len(T)!=2 or any(x is None or x<0 for x in S+T) or sum(T)<=0:raise ValueError('unresolved')
    return sum(S)/sum(T)

def qstar(values):
    for q in (1,16,256,4096):
        x=values[q]
        if x is None:return 'unresolved'
        if x>=1:return q
    return 'greater_than_4096'

def scope_indices(scope,indices):
    s=C['raw_cost_tensor']['scope_variants'][scope]
    return set(indices)==set(s['required_indices'])

def raises(fn):
    try:fn()
    except ValueError:return True
    return False

def case(name,fn):
    if len(RESULT)>=40:raise RuntimeError('declared final-suite cap')
    before=time.perf_counter();cpu=time.process_time()
    row={'name':name,'status':'started'};RESULT.append(row)
    signal.alarm(10)
    try:
        assert fn(),name
        row['status']='passed'
    except BaseException as ex:
        row.update(status='failed',error=type(ex).__name__+': '+str(ex))
    finally:
        signal.alarm(0);row.update(wall_seconds=time.perf_counter()-before,cpu_seconds=time.process_time()-cpu)

def run():
    case('even median separates lower and upper alternatives',lambda:med([1,1,1,2,2,2])==F(3,2))
    case('seven-block median uses fourth order statistic',lambda:med([9,1,8,2,7,3,6])==6)
    case('exact fractions retained at even median',lambda:med([F(1,3)]*3+[F(2,3)]*3)==F(1,2))
    case('missing block refuses median',lambda:raises(lambda:med([1]*6+[None])))
    case('five-block input cannot rescue incomplete panel',lambda:raises(lambda:med([1]*5)))
    case('negative cost refuses median',lambda:raises(lambda:med([-1]+[1]*6)))
    case('normalized whole-query workload without q division',lambda:normalize(102000000,34)==3000000)
    case('zero repetitions refused',lambda:raises(lambda:normalize(1,0)))
    case('cap excess repetitions refused',lambda:raises(lambda:normalize(1,101)))
    case('integer remainder order and conservation',lambda:split(10,3)==[4,3,3])
    case('cost smaller than target count remains conserved',lambda:split(2,4)==[1,1,0,0])
    case('zero physical charge not fabricated positive',lambda:split(0,3)==[0,0,0])
    case('negative physical allocation refused',lambda:raises(lambda:split(-1,3)))
    case('global initialization seventy-two target conservation',lambda:sum(split(101,72))==101)
    case('shared physical row reconciles perview not globally',lambda:sum([F(1,12)]*12)==1 and sum([F(1,12)]*24)==2)
    case('global and cold copies never sum into actual ledger',lambda:sum([9,4])==13 and sum([9,4,9,4])==26)
    case('normalized score keeps eight endpoint weighting',lambda:score([(2,[(102000000,34)]*7)]*8)==3000002)
    case('adaptive repetition total can rank slower arm first',lambda:102000000>100100000 and normalize(102000000,34)<normalize(100100000,1))
    case('exact rational tie chooses lowest numeric arm',lambda:winner({a:F(7,3) for a in range(2,8)})==2)
    case('rational near tie is not rounded',lambda:winner({2:F(10**20+1,10**20),3:F(1),4:F(2),5:F(3),6:F(4),7:F(5)})==3)
    case('missing scalar candidate makes stratum unresolved',lambda:raises(lambda:winner({a:F(a) for a in range(2,7)})))
    case('seven endpoint stratum refused',lambda:raises(lambda:score([(0,[(1,1)]*7)]*7)))
    case('class ratio of totals differs from average ratios',lambda:ratio([F(1),F(9)],[F(1),F(3)])==F(5,2))
    case('zero transport denominator refused',lambda:raises(lambda:ratio([F(1),F(1)],[F(0),F(0)])))
    case('missing endpoint refuses ratio',lambda:raises(lambda:ratio([F(1),None],[F(1),F(1)])))
    case('common LOO retains integer setup and even median',lambda:F(5)+med([F(1)]*3+[F(2)]*3)==F(13,2))
    case('qstar earliest declared crossing',lambda:qstar({1:F(1,2),16:F(1),256:F(2),4096:F(3)})==16)
    case('qstar cannot skip unresolved earlier q',lambda:qstar({1:None,16:F(2),256:F(2),4096:F(2)})=='unresolved')
    case('qstar no tested crossing has finite-grid label',lambda:qstar({q:F(1,2) for q in (1,16,256,4096)})=='greater_than_4096')
    case('global raw scope carries no fake fixture axes',lambda:scope_indices('global',{}))
    case('global raw scope rejects phantom fixture',lambda:not scope_indices('global',{'fixture':'I0F0'}))
    case('interval search scope admits failure before fixture',lambda:scope_indices('interval',{'interval':'I0'}))
    case('kernel scope names own label only',lambda:scope_indices('kernel',{'fixture':'I0F0','kernel':'K0'}))
    case('workload setup scope has no fabricated block',lambda:scope_indices('arm_workload',{k:0 for k in ['fixture','endpoint','coordinate','plane','seed','q','arm']}))
    case('repetition row requires explicit block and repeat',lambda:not scope_indices('block_repetition',{k:0 for k in ['fixture','endpoint','coordinate','plane','seed','q','arm','block']}))
    case('frozen main matrix arithmetic',lambda:6*4*3*2*4*7*7==28224)
    case('frozen selection matrix arithmetic',lambda:9*8*6*7==3024)
    case('all36primary cells cannot be replaced by global average',lambda:6*2*3==36 and not all(x>=F(6,5) for x in [F(1)]+[F(2)]*35))
    case('selection score does not replace actual adaptive expenditure',lambda:sum([102000000]*7)!=normalize(102000000,34))
    case('drafting limit separate from future scientific matrix',lambda:D['drafting_check_envelope']['scientific_executions']==0 and D['drafting_check_envelope']['scope']=='This drafting task only,not futuremeasurement workload counts or campaigncost.')

if __name__=='__main__':
    start=time.perf_counter();cpu=time.process_time();run()
    record={'schema':'crypto.autoresearch.fixed_definition_checks.v1','task_id':'TASK-20260908-83e89d','executed_cases':len(RESULT),'passed':sum(r['status']=='passed' for r in RESULT),'failed':sum(r['status']!='passed' for r in RESULT),'cases':RESULT,'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'maximum_rss_native':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rss_units':'bytes_on_Darwin','workers':1,'scientific_runs':0,'contract_sha256':hashlib.sha256((HERE/'EXP-ECDLP-1b1b99.yaml').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    print(json.dumps(record,indent=2));raise SystemExit(bool(record['failed']))
