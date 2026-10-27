"""Independent signed matching using division-polynomial derivative jets.

The GP producer uses sequential affine addition. This verifier constructs
x([k]P) from division polynomials and y([k]P)/y from its formal derivative,
not by differentiating a reduced representative modulo the kernel.
"""
import collections,csv,hashlib,json,sys,time
from functools import lru_cache
from pathlib import Path
from flint import fmpz_mod_poly_ctx,__version__ as FLINT_VERSION
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
def cv(f):return [int(c) for c in f.coeffs()]
def count(p,A,B):return 1+sum(1 if (g:=(x*x*x+A*x+B)%p)==0 else 2 if pow(g,(p-1)//2,p)==1 else 0 for x in range(p))
def fullpsi(R,A,B,q):
    x=R.gen();g=x**3+A*x+B;g2=16*g*g
    @lru_cache(None)
    def ps(n):
        if n==0:return R.zero()
        if n<=2:return R.one()
        if n==3:return 3*x**4+6*A*x*x+12*B*x-A*A
        if n==4:return 2*(x**6+5*A*x**4+20*B*x**3-5*A*A*x*x-4*A*B*x-8*B*B-A**3)
        m=n//2
        if n%2:
            a,b=ps(m+2)*ps(m)**3,ps(m-1)*ps(m+1)**3
            return a-g2*b if m%2 else g2*a-b
        return ps(m)*(ps(m+2)*ps(m-1)**2-ps(m-2)*ps(m+1)**2)
    return ps(q)
def jet_multiples(R,A,B,q,K):
    p=int(R.modulus());x=R.gen();G=x**3+A*x+B
    def J(f):return f%K,f.derivative()%K
    def M(a,b):return (a[0]*b[0])%K,(a[1]*b[0]+a[0]*b[1])%K
    def C(a,c):return a[0]*c,a[1]*c
    def S(a,b):return a[0]-b[0],a[1]-b[1]
    gj=J(G);g2=C(M(gj,gj),16)
    def cube(a):return M(M(a,a),a)
    @lru_cache(None)
    def psi(n):
        if n==0:return R.zero(),R.zero()
        if n<=2:return R.one(),R.zero()
        if n==3:return J(3*x**4+6*A*x*x+12*B*x-A*A)
        if n==4:return J(2*(x**6+5*A*x**4+20*B*x**3-5*A*A*x*x-4*A*B*x-8*B*B-A**3))
        m=n//2
        if n%2:
            a=M(psi(m+2),cube(psi(m)));b=M(psi(m-1),cube(psi(m+1)))
            return S(a,M(g2,b)) if m%2 else S(M(g2,a),b)
        return M(psi(m),S(M(psi(m+2),M(psi(m-1),psi(m-1))),M(psi(m-2),M(psi(m+1),psi(m+1)))))
    assert psi(q)[0].is_zero()
    def multiple(k):
        N=M(psi(k-1),psi(k+1));D=M(psi(k),psi(k))
        if k%2:N=M(N,C(gj,4))
        else:D=M(D,C(gj,4))
        inv=D[0].inverse_mod(K);xx=(x-N[0]*inv)%K
        dx=(1-(N[1]*D[0]-N[0]*D[1])*inv*inv)%K
        yy=dx*pow(k,-1,p)%K
        return xx,yy
    return multiple
def main():
    started=time.monotonic();receipt=json.loads((P/'RESULT.json').read_text());assert receipt['status']=='terminal' and receipt['returncode']==0
    for n,h in json.loads((P/'INPUT-HASHES.json').read_text()).items():assert sha(P/n)==h,n
    assert sha(P/'native.stdout')==receipt['stdout_sha256'] and sha(P/'native.stderr')==receipt['stderr_sha256']
    assert (P/'native.stderr').read_text().strip() in ['','***   Warning: new maximum stack size = 512000000 (488.281 Mbytes).']
    expected=[json.loads(x) for x in (P/'native-inputs.gp').read_text().splitlines()];assert len(expected)==411
    bindings=json.loads((P/'CASE-BINDINGS.json').read_text());assert len(bindings)==411
    rows=json.loads((P/'rows.json').read_text());assert len(rows)==21 and len({r['timestamp'] for r in rows})==6 and sum(r['label']=='omitted' for r in rows)==11
    assert sha(P/'cohort-inputs.json')=='93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545'
    case_map={z[0]:z for z in expected};assert set(case_map)==set(range(3,414))
    for b in bindings:assert rows[b['index']]['curve_uid']==b['curve_uid']
    data=[];markers=[];constructor=None
    for line in (P/'native.stdout').read_text().splitlines():
        if not line.startswith('['):markers.append(line);continue
        z=json.loads(line)
        if z[0]==1:assert constructor is None;constructor=z
        else:assert z[0]==0 and len(z)==17;data.append(z)
    assert markers==['CONTROLS_COMPLETE','Y_MATCH_COMPLETE 415'] and [z[1] for z in data]==list(range(415))
    assert constructor[:5]==[1,103,0,1,7]
    Rc=fmpz_mod_poly_ctx(103);cf=Rc(constructor[5]);assert cf==fullpsi(Rc,0,1,7)
    product=Rc.one();split=Rc.one();cubics=[]
    for fv,m in constructor[6]:
        f=Rc(fv);assert m==1 and f.leading_coefficient()==1;product*=f**m
        if f.degree()==1:split*=f
        if f.degree()==3:cubics.append(f)
    assert product*int(cf.leading_coefficient())==cf and split.degree()==3 and len(cubics)==1
    assert data[0][7]==cv(split) and data[1][7]==cv(cubics[0])
    results=[];profile=collections.Counter();contexts={};independent=(P/'independent.jsonl').open('x')
    for z in data:
        _,id,idx,q,p,A,B,kv,s1,xfv,yfv,ym,xy,first,d,denoms,shape=z
        assert d==(q-1)//2 and denoms==max(0,d-1) and shape==[0,0]
        if id in case_map:
            assert [id,idx,q,p,A,B,kv]==case_map[id];r=rows[idx];assert (p,A,B)==(int(r['p']),p-3,int(r['b']));n=int(r['n'])
        elif id in [0,1]:assert (idx,q,p,A,B)==(-1,7,103,0,1);n=count(p,A,B);assert n==84
        else:assert id in [2,414] and (idx,q,p,A,B,kv)==(-2,7,101,1,1,[10,47,70,1]);n=count(p,A,B);assert n==105
        R=contexts.setdefault(p,fmpz_mod_poly_ctx(p));K=R(kv);x=R.gen();g=x**3+A*x+B
        assert K.degree()==d and K.leading_coefficient()==1 and K.gcd(K.derivative()).degree()==0 and K.gcd(g).degree()==0
        assert (-int(K[d-1]))%p==s1 and cv(x.pow_mod(p,K))==xfv and cv(g.pow_mod((p-1)//2,K))==yfv
        multiple=jet_multiples(R,A,B,q,K);xf=R(xfv);yf=R(yfv);ey=[];ex=[];efirst=0;points={}
        for k in range(1,d+1):
            u,v=multiple(k);points[k]=(u,v);assert ((g*v*v-u**3-A*u-B)%K).is_zero()
            for sign,scalar in [(1,k),(-1,q-k)]:
                if v*sign%K==yf:
                    ey.append(scalar)
                    if not efirst:efirst=scalar
                    if u==xf:ex.append(scalar)
            profile['independent_scalar_coordinate_checks']+=1
        independent.write(json.dumps({'id':id,'index':idx,'ell':q,'p':p,'A':A,'B':B,'kernel':kv,'S1':(-int(K[d-1]))%p,'x_frobenius':cv(x.pow_mod(p,K)),'y_frobenius':cv(g.pow_mod((p-1)//2,K)),'y_matches':sorted(ey),'full_matches':sorted(ex),'first_y_match':efirst,'scalar_checks':d},separators=(',',':'))+'\n');independent.flush()
        assert ym==sorted(ey) and xy==sorted(ex) and first==efirst and len(xy)==1
        primitive=next(a for a in range(1,d+1) if next(k for k in range(1,d+1) if pow(a,k,q) in [1,q-1])==d)
        xx=points[primitive][0];composition=R.zero()
        for c in reversed(kv):composition=(composition*xx+c)%K
        assert composition.is_zero()
        t=p+1-n;lam=xy[0];assert (lam*lam-t*lam+p)%q==0
        false=set(ym)-set(xy)
        if false:assert q%3==1 and s1==0
        if s1:assert not false
        results.append({'id':id,'index':idx,'ell':q,'S1':str(s1),'y_matches':ym,'full_matches':xy,'false_y_matches':sorted(false),'first_y_match':first,'first_y_is_full_match':first in xy,'first_y_trace_matches_order':(first*first-t*first+p)%q==0,'cohort':id in case_map})
    independent.close()
    assert [{**r,'id':0} for r in [results[2]]]==[{**r,'id':0} for r in [results[-1]]]
    assert all(len(results[i]['y_matches'])==3 and len(results[i]['false_y_matches'])==2 for i in [0,1])
    cohort=[r for r in results if r['cohort']];assert len(cohort)==411 and {r['index'] for r in cohort}==set(range(21))
    with (P/'curve-summary.csv').open('x',newline='') as f:
        names=['index','name','curve_uid','timestamp','ordinal','label','kernels','S1_zero_kernels','ambiguous_y_kernels','first_y_wrong_trace_kernels','unique_full_matches'];w=csv.DictWriter(f,fieldnames=names);w.writeheader()
        for i,row in enumerate(rows):
            rr=[r for r in cohort if r['index']==i];w.writerow({'index':i,**{k:row[k] for k in ['name','curve_uid','timestamp','ordinal','label']},'kernels':len(rr),'S1_zero_kernels':sum(int(r['S1'])==0 for r in rr),'ambiguous_y_kernels':sum(len(r['y_matches'])>1 for r in rr),'first_y_wrong_trace_kernels':sum(not r['first_y_trace_matches_order'] for r in rr),'unique_full_matches':sum(len(r['full_matches'])==1 for r in rr)})
    put(P/'AUDIT.json',{'status':'PASS','scope':'411 retained valid cyclic kernels across21 curves plus four control calls; not every possible historical kernel or implementation.','native_calls':415,'cohort_calls':411,'curves':21,'omitted':11,'published':10,'streams':6,'cohort_S1_zero_kernels':sum(int(r['S1'])==0 for r in cohort),'cohort_ambiguous_y_kernels':sum(len(r['y_matches'])>1 for r in cohort),'cohort_false_y_matches':sum(len(r['false_y_matches']) for r in cohort),'cohort_first_y_wrong_trace_kernels':sum(not r['first_y_trace_matches_order'] for r in cohort),'independent_scalar_coordinate_checks':profile['independent_scalar_coordinate_checks'],'controls':results[:3]+results[-1:],'AA_exact':True,'rows':results,'FLINT_version':FLINT_VERSION,'elapsed_seconds_diagnostic_only':time.monotonic()-started,'native_output_sha256':sha(P/'native.stdout')})
    print(json.dumps({'status':'PASS','calls':415,'kernels':411,'cohort_ambiguous_y_kernels':sum(len(r['y_matches'])>1 for r in cohort),'scalar_checks':profile['independent_scalar_coordinate_checks'],'seconds_diagnostic':time.monotonic()-started}),flush=True)
if __name__=='__main__':main()
