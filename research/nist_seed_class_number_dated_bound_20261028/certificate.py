"""Bounded deterministic witness producer. Main launcher fails closed."""
import json,sys,traceback
from pathlib import Path
P=Path(__file__).resolve().parent
def prime(n):
    if n<2:return False
    return all(n%d for d in range(2,__import__('math').isqrt(n)+1))
def split(D,q):
    if q==2:return D%8==1
    return pow(D%q,(q-1)//2,q)==1
def cert(D,k):
    qs=[];Q=1
    for q in range(2,10001):
        if prime(q) and split(D,q):
            qs.append(q);Q*=q
            if len(qs)==k:return [qs,Q,int(4*Q<abs(D))]
    raise RuntimeError('fixed prime-search cap reached')
def fundamental_from_factors(D,factors):
    # Factors are of |Delta_pi|. Exact primes are independently proved by GP.
    core=1
    for q,e in factors:
        if e%2:core*=q
    expected=-core if (-core)%4==1 else -4*core
    return D==expected
def body():
    if '--fault-exception' in sys.argv:raise RuntimeError('injected exception')
    if '--fault-early' in sys.argv:return False
    assert cert(-23,1)==[[2],2,1] and cert(-15,1)==[[2],2,1]
    assert cert(-7,1)==[[2],2,0]
    assert not fundamental_from_factors(-75,[(3,1),(5,2)])
    assert json.dumps(cert(-23,1))==json.dumps(cert(-23,1))
    print('CONTROLS PASS',flush=True)
    for i,r in enumerate(json.loads((P/'INPUTS.json').read_text())['rows']):
        v=r['cm_record']
        if v is None:out=[i,0,24,[],0,0]
        else:
            p,n=int(r['p']),int(r['n']);D=int(v['D_K']);f=int(v['f_pi']);delta=int(v['delta']);factors=[(int(q),e) for q,e in v['factors']]
            assert delta==(p+1-n)**2-4*p==f*f*D and D<0
            assert len({q for q,e in factors})==len(factors) and all(q>1 and e>0 for q,e in factors)
            assert __import__('math').prod(q**e for q,e in factors)==-delta
            assert fundamental_from_factors(D,factors)
            qs,Q,ok=cert(D,24);out=[i,D,24,qs,Q,ok]
        print(json.dumps(out,separators=(',',':')),flush=True)
    return True
if __name__=='__main__':
    try:
        if body() is not True:raise RuntimeError('missing completion sentinel')
        print('COMPLETE',flush=True)
    except BaseException:
        traceback.print_exc();sys.exit(1)
