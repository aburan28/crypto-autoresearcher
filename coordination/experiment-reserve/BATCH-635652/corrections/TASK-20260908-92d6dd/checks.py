"""Forty fixed abstract definition checks; zero curves, scientific null panels or runs."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time,signal,resource,yaml
HERE=Path(__file__).resolve().parent
DATA={k:yaml.safe_load((HERE/('EXP-ECDLP-'+k+'.yaml')).read_text())['protocol_amendment'] for k in ['184fc4','1e6502','2c3d20','709063']}
RESULT=[]

def dec(n):
    if type(n) is not int or n<0:raise ValueError('unsigned canonical integer')
    return str(n)

def tag(exp,kind,bits,stratum,replicate):
    if exp not in ('EXP-ECDLP-184fc4','EXP-ECDLP-1e6502') or stratum not in ('A','B'):raise ValueError('domain')
    kinds=('primary','control-2q') if exp.endswith('184fc4') else ('ordinary','anomalous')
    if kind not in kinds:raise ValueError('kind')
    return exp+'|'+kind+'|bits='+dec(bits)+'|stratum='+stratum+'|replicate='+dec(replicate)

def map_digest(V,n):
    if not 1<=n<=2**256 or not 0<=V<2**256:raise ValueError('range')
    M=n*((2**256)//n)
    return V%n if V<M else None

def draw(n,prefix,digest=None):
    for c in range(4096):
        V=digest(c) if digest else int.from_bytes(hashlib.sha256((prefix+'|counter='+dec(c)).encode()).digest(),'big')
        value=map_digest(V,n)
        if value is not None:return value,c+1
    raise ValueError('digest_rejection_exhausted')

def certificate(n,choices=None):
    if type(n) is not int or not 1<=n<=2**256:raise ValueError('N')
    S={};out=[]
    for i in range(min(1000,n)):
        offset=choices(i,n-i) if choices else draw(n-i,'STATIC-FIXED-CERTIFICATE|N='+dec(n)+'|draw='+dec(i))[0]
        if not 0<=offset<n-i:raise ValueError('offset')
        j=i+offset;out.append(S.get(j,j));S[j]=S.get(i,i);S.pop(i,None)
    return out

def slope_candidate(obs,null):
    if len(null)!=64 or obs is None or any(x is None for x in null):return False
    null=list(map(F,null));obs=F(obs);mean=sum(null)/64;var=sum((x-mean)**2 for x in null)/63;ordered=sorted(null);median=(ordered[31]+ordered[32])/2
    rank=(1+sum(x>=obs for x in null))
    return rank==1 and var>0 and obs-mean>0 and (obs-mean)**2>=4*var and obs>F(-1,4) and median<0

def grid(a,b):
    if len(a)!=4 or len(b)!=4 or any(x is None for x in a+b):return 'NONMONOTONE_OR_INCONCLUSIVE'
    def classify(x):
        signs=[v>=0 for v in x]
        if not any(signs):return 'ALL_TESTED_RUNGS_BSGS_LOWER'
        if all(signs):return 'ALL_TESTED_RUNGS_BSGS_NOT_LOWER'
        k=signs.index(True)
        return ('REPLICATED_TESTED_GRID_SIGN_CHANGE',k-1,k) if all(signs[k:]) else 'NONMONOTONE_OR_INCONCLUSIVE'
    x,y=classify(a),classify(b);return x if x==y else 'NONMONOTONE_OR_INCONCLUSIVE'

def raises(fn):
    try:fn()
    except ValueError:return True
    return False

def case(name,fn):
    assert len(RESULT)<40
    row={'name':name,'status':'started'};RESULT.append(row);start=time.perf_counter();cpu=time.process_time();signal.alarm(10)
    try:
        assert fn(),name;row['status']='passed'
    except BaseException as e:row.update(status='failed',error=type(e).__name__+': '+str(e))
    finally:signal.alarm(0);row.update(wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu)

def run():
    case('canonical zero decimal',lambda:dec(0)=='0')
    case('boolean not numeric field',lambda:raises(lambda:dec(True)))
    case('negative index refused',lambda:raises(lambda:dec(-1)))
    case('fractional field refused',lambda:raises(lambda:dec(F(3,2))))
    case('primary actual-value tag bytes',lambda:tag('EXP-ECDLP-184fc4','primary',12,'A',20260905)=='EXP-ECDLP-184fc4|primary|bits=12|stratum=A|replicate=20260905')
    case('control domain separated',lambda:tag('EXP-ECDLP-184fc4','control-2q',12,'A',20260905)!=tag('EXP-ECDLP-184fc4','primary',12,'A',20260905))
    case('ordinary anomalous separated',lambda:tag('EXP-ECDLP-1e6502','ordinary',10,'A',20260905)!=tag('EXP-ECDLP-1e6502','anomalous',10,'A',20260905))
    case('stratum distinguished',lambda:tag('EXP-ECDLP-184fc4','primary',12,'A',20260905)!=tag('EXP-ECDLP-184fc4','primary',12,'B',20260905))
    case('replicate distinguished',lambda:tag('EXP-ECDLP-184fc4','primary',12,'A',20260905)!=tag('EXP-ECDLP-184fc4','primary',12,'A',20260906))
    case('malformed stratum refused',lambda:raises(lambda:tag('EXP-ECDLP-184fc4','primary',12,'A|replicate=0',20260905)))
    case('wrong kind refused',lambda:raises(lambda:tag('EXP-ECDLP-184fc4','ordinary',12,'A',20260905)))
    case('unbiased rejection boundary',lambda:map_digest(3*((2**256)//3),3) is None)
    case('below rejection boundary accepted',lambda:map_digest(3*((2**256)//3)-1,3)==2)
    case('n1 consumes exactly one digest',lambda:draw(1,'STATIC',lambda c:2**256-1)==(0,1))
    case('rejected digest advances counter',lambda:draw(3,'STATIC',lambda c:2**256-1 if c==0 else 4)==(1,2))
    case('bounded digest exhaustion refuses without replacement',lambda:raises(lambda:draw(3,'STATIC',lambda c:2**256-1)))
    case('invalid range refused',lambda:raises(lambda:map_digest(0,0)))
    case('singleton certificate distinct complete',lambda:certificate(1)==[0])
    case('fixed three-index partial shuffle',lambda:certificate(3,lambda i,n:n-1)==[2,0,1])
    case('fixed seven-index certificate is permutation',lambda:sorted(certificate(7))==list(range(7)))
    case('1000 cap on fixed abstract index universe',lambda:len(certificate(1001,lambda i,n:0))==1000)
    case('zero group order refused',lambda:raises(lambda:certificate(0)))
    case('negative sparse-shuffle offset refused',lambda:raises(lambda:certificate(3,lambda i,n:-1)))
    case('null YAML section is stable named string',lambda:'permutation_null' in DATA['1e6502']['effective_contract']['spectral_null_and_delta_thresholds'] and None not in DATA['1e6502']['effective_contract']['spectral_null_and_delta_thresholds'])
    case('corrected sibling hash resolves',lambda:hashlib.sha256((HERE/'EXP-ECDLP-184fc4.yaml').read_bytes()).hexdigest()==DATA['1e6502']['effective_contract']['spectral_null_and_delta_thresholds']['sibling_definition_binding']['sha256'])
    # The following fixed rational trajectories are the archived analytic counterexample, not a generated scientific null panel.
    case('original slope counterexample remains eligible',lambda:slope_candidate(F(0),[F(-49,100)-F(2*u,6300) for u in range(64)]))
    case('zero dispersion slope cannot fabricate infinite effect',lambda:not slope_candidate(F(0),[F(-1,2)]*64))
    case('missing null trajectory refuses candidate',lambda:not slope_candidate(F(0),[F(-1,2)]*63+[None]))
    case('true slope threshold is strict',lambda:not slope_candidate(F(-1,4),[F(-49,100)-F(2*u,6300) for u in range(64)]))
    case('nondecaying null refuses original falsifier',lambda:not slope_candidate(F(2),[F(u,100) for u in range(64)]))
    case('slope route not hidden behind scalar top-rung test',lambda:'does not inherit' in DATA['2c3d20']['null_inference_and_decisions']['review_candidate'])
    case('slope inventory eligibility restored',lambda:next(x for x in DATA['2c3d20']['null_inference_and_decisions']['statistic_inventory'] if x['key']=='sigma_center_slope')['candidate_eligible'] is True)
    case('itinerary slope stays descriptive',lambda:next(x for x in DATA['2c3d20']['null_inference_and_decisions']['statistic_inventory'] if x['key']=='itinerary_summary_slope')['candidate_eligible'] is False)
    case('all-negative tested grid label',lambda:grid([-1,-1,-1,-1],[-2,-2,-2,-2])=='ALL_TESTED_RUNGS_BSGS_LOWER')
    case('all-nonnegative tested grid label',lambda:grid([0,1,2,3],[1,2,3,4])=='ALL_TESTED_RUNGS_BSGS_NOT_LOWER')
    case('adjacent tested sign pair',lambda:grid([-2,-1,0,1],[-3,-1,1,2])==('REPLICATED_TESTED_GRID_SIGN_CHANGE',1,2))
    case('nonmonotonic signs stay inconclusive',lambda:grid([-1,1,-1,1],[-1,1,-1,1])=='NONMONOTONE_OR_INCONCLUSIVE')
    case('replicate disagreement stays inconclusive',lambda:grid([-1,-1,1,1],[-1,1,1,1])=='NONMONOTONE_OR_INCONCLUSIVE')
    case('missing tested rung stays inconclusive',lambda:grid([-1,-1,None,1],[-1,-1,1,1])=='NONMONOTONE_OR_INCONCLUSIVE')
    case('unapproved zero-science contract boundary',lambda:all(d['approved_by'] is None and d['scientific_runs']==0 and d['execution_authorized'] is False for d in DATA.values()))

if __name__=='__main__':
    start=time.perf_counter();cpu=time.process_time();run();receipt={'schema':'crypto.autoresearch.fixed_definition_checks.v1','task_id':'TASK-20260908-92d6dd','executed_cases':len(RESULT),'passed':sum(x['status']=='passed' for x in RESULT),'failed':sum(x['status']!='passed' for x in RESULT),'cases':RESULT,'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'peak_RSS_native':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'RSS_units':'bytes_on_Darwin','workers':1,'scientific_runs':0,'contract_sha256':{k:hashlib.sha256((HERE/('EXP-ECDLP-'+k+'.yaml')).read_bytes()).hexdigest() for k in DATA},'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};print(json.dumps(receipt,indent=2));raise SystemExit(bool(receipt['failed']))
