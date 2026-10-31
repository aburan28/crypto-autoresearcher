"""Execute the recovered GETPAA/GETALL, with explicitly reconstructed dependencies.

Neither the ZL adapters, the root enumerator nor CHARLA is historical source.
No candidate label, order or trace is supplied to the native routines.
"""
import ctypes as ct
import hashlib,json,math,os,platform,shutil,subprocess,sys,time,traceback
from functools import lru_cache
from pathlib import Path
from flint import fmpz_mod_poly_ctx
P=Path(__file__).resolve().parent
C=Path(os.environ.get('GETALL_PARENT',str(P.parents[1]/'canonical-equations-01')))
COHORT_SHA='93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
    with p.open('x') as out:json.dump(x,out,indent=2,sort_keys=True);out.write('\n')
def coeffs(poly):return [int(x) for x in poly.coeffs()]
def load_tables():
    result={}
    for r in json.loads((P/'TABLES.json').read_text()):
        q=r['ell'];v=(r['columns']-1)//2
        tokens=list(map(int,(P/'tables'/r['file']).read_text().split()));m=r['columns']
        table=[tokens[i*m:(i+1)*m] for i in range(q+2)]
        assert table[-1]==[1]+[0]*(m-1)
        for power,row in enumerate(table[:-1]):
            limit=v*(2*q-power)//q
            assert all(c==0 for c in row[limit+1:]),(q,power,limit)
        result[q]=(v,table)
    return result
def polyA(table,j,p):return [sum(c*pow(j,k,p) for k,c in enumerate(row))%p for row in table]
def polyJ(table,a,p):return [sum(row[k]*pow(a,i,p) for i,row in enumerate(table))%p for k in range(len(table[0]))]
def derivatives(table,a,j,p):
    out=[0]*5
    for i,row in enumerate(table):
        for k,c in enumerate(row):
            if i:out[0]+=i*c*pow(a,i-1,p)*pow(j,k,p)
            if k:out[1]+=k*c*pow(a,i,p)*pow(j,k,p)
            if i>=2:out[2]+=i*(i-1)*c*pow(a,i-2,p)*pow(j,k,p)
            if i and k:out[3]+=i*k*c*pow(a,i-1,p)*pow(j,k,p)
            if k:out[4]+=k*k*c*pow(a,i,p)*pow(j,k,p)
    return [x%p for x in out]
def recovery(R,A,B,u,v,w,q):
    p=int(R.modulus());d=(q-1)//2;s=[0]*max(3,d);s[0]=u
    s[1]=((A-v)*pow(10,-1,p)-d*A)*pow(3,-1,p)%p
    s[2]=((B-w)*pow(14,-1,p)-3*A*u-2*d*B)*pow(5,-1,p)%p
    def ck(a,b,n):
        c=[0]*n
        if n:c[0]=-a*pow(5,-1,p)%p
        if n>=2:c[1]=-b*pow(7,-1,p)%p
        for k in range(3,n+1):c[k-1]=3*sum(c[h-1]*c[k-2-h] for h in range(1,k-1))*pow((k-2)*(2*k+3),-1,p)%p
        return c
    c,ct=ck(A,B,d-1),ck(v,w,d-1);x=R.gen();G=x**3+A*x+B;mu=x
    for k in range(1,d):
        mu=4*G*mu.derivative().derivative()+(6*x*x+2*A)*mu.derivative()
        if k>=3:
            lower=sum(int(mu[j])*(d if j==0 else s[j-1]) for j in range(k+1))
            s[k]=(math.factorial(2*k)*(ct[k-1]-c[k-1])*pow(2,-1,p)-lower)*pow(int(mu[k+1]),-1,p)%p
    K=[1]
    for k in range(1,d+1):K.append(-sum(K[k-j]*s[j-1] for j in range(1,k+1))*pow(k,-1,p)%p)
    return R(list(reversed(K))),s[:d]
def kernel_checks(R,A,B,u,v,w,q,K):
    p=int(R.modulus());x=R.gen();G=x**3+A*x+B;G2=16*G*G
    @lru_cache(None)
    def psi(k):
        if k==0:return R.zero()
        if k in [1,2]:return R.one()
        if k==3:return (3*x**4+6*A*x*x+12*B*x-A*A)%K
        if k==4:return (2*(x**6+5*A*x**4+20*B*x**3-5*A*A*x*x-4*A*B*x-8*B*B-A**3))%K
        m=k//2
        if k%2:
            a=psi(m+2)*psi(m)**3;b=psi(m-1)*psi(m+1)**3
            return ((a-G2*b) if m%2 else (G2*a-b))%K
        return (psi(m)*(psi(m+2)*psi(m-1)**2-psi(m-2)*psi(m+1)**2))%K
    rem=psi(q);cyclic=False
    if rem.is_zero():
        d=(q-1)//2
        primitive=next(a for a in range(2,q) if next(k for k in range(1,d+1) if pow(a,k,q) in [1,q-1])==d)
        k=primitive;den=psi(k)**2;num=psi(k-1)*psi(k+1)
        if k%2:num*=4*G
        else:den*=4*G
        try:
            xk=(x-num*den.inverse_mod(K))%K;z=R.zero()
            for c in reversed(coeffs(K)):z=(z*xk+int(c))%K
            cyclic=z.is_zero()
        except ZeroDivisionError:pass
    cs=list(reversed(coeffs(K)));mm=[];d=K.degree()
    for k in range(1,4):
        z=-sum(cs[j]*mm[k-j-1] for j in range(1,min(k,d+1)))
        if k<=d:z-=k*cs[k]
        mm.append(z%p)
    coherent=(mm[0]==u and (A-10*(3*mm[1]+d*A))%p==v and (B-14*(5*mm[2]+3*A*mm[0]+2*d*B))%p==w)
    return coeffs(rem),cyclic,coherent
class Native:
    def __init__(self,bits,tables):
        self.bits=bits;self.tables=tables;self.lib=ct.CDLL(str(P/'native.dylib'))
        ptr=ct.POINTER(ct.c_int);self.Callback=ct.CFUNCTYPE(None,*([ptr]*10))
        self.roots_cb=self.Callback(self.roots);self.check_cb=self.Callback(self.check)
        self.lib.snapshot_.restype=ct.c_char_p
    def setup(self):
        self.lib.setup_(ct.byref(ct.c_int(self.bits)),self.roots_cb,self.check_cb)
        self.calls=[];self.errors=[];self.neighbors=[]
    def read(self,a):
        n=int(a[0]);assert 1<=n<=24;nval=0
        for i in range(1,n+1):nval=(nval<<self.bits)+int(a[i])
        return nval
    def pack(self,n,size=25):
        a=(ct.c_int*size)();self.write(a,n);return a
    def write(self,a,n):
        assert n>=0;v=[]
        while n:v.append(n%2**self.bits);n>>=self.bits
        v=v or [0];a[0]=len(v)
        for i,x in enumerate(reversed(v),1):a[i]=x
    def cuf(self,q,p):
        v,table=self.tables[q];digits=self.pack(p)[0];stride=digits+1
        out=(ct.c_int*(stride*(q+1)*(2*v+1)))()
        for k in range(2*v+1):
            for L in range(1,q+2):
                value=self.pack(table[q+1-L][k]%p)
                pos=stride*((L-1)+(q+1)*k)
                for i in range(value[0]+1):out[pos+i]=value[i]
        return out
    def paa(self,q,p,a,j):
        self.setup();v,table=self.tables[q];out=[self.pack(0) for _ in range(5)]
        self.lib.getpaa_(self.pack(a),self.pack(j),*out,self.pack(p),ct.byref(ct.c_int(q)),ct.byref(ct.c_int(2)),ct.byref(ct.c_int(v)),self.cuf(q,p))
        return [self.read(x) for x in out],json.loads(self.lib.snapshot_())
    def roots(self,r,d,a,j,q,p,v,c,unused,unused2):
        try:
            prime=self.read(p);R=fmpz_mod_poly_ctx(prime);alpha=self.read(a);J=self.read(j)
            poly=R(polyJ(self.tables[q[0]][1],alpha,prime));rr=sorted(int(z) for z,m in poly.roots() if int(z)!=J)
            assert len(rr)*p[0]<=1000
            for k,z in enumerate(rr):
                for i in range(p[0]-1,-1,-1):r[k*p[0]+i]=z%2**self.bits;z>>=self.bits
            d[0]=len(rr);self.neighbors=rr
        except BaseException:self.errors.append(traceback.format_exc());d[0]=-1
    def check(self,s,a,b,v,w,k,q,p,f,unused):
        try:
            prime=self.read(p);A,B,u,V,W=map(self.read,[a,b,s,v,w]);R=fmpz_mod_poly_ctx(prime)
            K,ss=recovery(R,A,B,u,V,W,q[0]);rem,cyclic,coherent=kernel_checks(R,A,B,u,V,W,q[0],K)
            passed=not rem and cyclic and coherent
            self.calls.append({'s1':u,'aq':V,'bq':W,'kernel':coeffs(K),'moments':ss,'remainder':rem,'cyclic':cyclic,'coherent':coherent,'pass':passed})
            f[0]=0 if passed else -1
            # GETALL only observes FLAG; ELKCOF is not consumed in this study.
            k[0]=1;k[1]=0
        except BaseException:self.errors.append(traceback.format_exc());f[0]=-1
    def all(self,q,p,A,B,alpha):
        self.setup();J=1728*4*pow(A,3,p)*pow((4*pow(A,3,p)+27*B*B)%p,-1,p)%p
        v,table=self.tables[q];out=[self.pack(0) for _ in range(3)];flag=ct.c_int(99);kernel=self.pack(0,size=10000)
        self.lib.getall_(self.pack(alpha),self.pack(J),self.pack(A),self.pack(B),*out,self.pack(p),ct.byref(ct.c_int(q)),ct.byref(flag),ct.byref(ct.c_int(v)),kernel,self.cuf(q,p))
        return {'bits':self.bits,'q':q,'p':p,'A':A,'B':B,'alpha':alpha,'j':J,'flag':flag.value,'outputs':[self.read(x) for x in out], 'neighbors':self.neighbors,'checks':self.calls,'errors':self.errors,'arithmetic':json.loads(self.lib.snapshot_())}
def prepare():
    assert not (P/'PROTOCOL.json').exists()
    src=P.parent/'author-and-release-links/payload-06.raw';text=src.read_text()
    first=text.index('      SUBROUTINE GETPAA(');last=text.index('    *****This is FLLPTS')
    extract=text[first:last];(P/'atkin-original.f').write_text(extract)
    meta=[x for x in json.loads((C/'TABLES.json').read_text()) if x['type']==2]
    (P/'tables').mkdir();
    for x in meta:shutil.copyfile(C/'tables'/x['file'],P/'tables'/x['file'])
    put(P/'TABLES.json',meta);load_tables()
    for n in ['rows.json','cohort-inputs.json']:shutil.copyfile(C/n,P/n)
    assert sha(P/'cohort-inputs.json')==COHORT_SHA
    cells=[x for x in json.loads((C/'FIBER-AUDIT.json').read_text())['cells'] if x['type']==2 and x['index']<21]
    assert len(cells)==315 and sum(len(x['roots']) for x in cells)==299
    put(P/'CELLS.json',cells)
    put(P/'SOURCE.json',{'url':'https://www.lix.polytechnique.fr/~morain/AtkinEmails/19930305.txt','email_sha256':sha(src),'extracted_fortran_sha256':sha(P/'atkin-original.f'),'extraction':'Exact text from SUBROUTINE GETPAA through GETALL END; no substitutions.','source_date':'1993-03-05','not_recovered':['ZL arithmetic library','GETJQN','BLVNOC','CHARLA','original coefficient tables','NIST/Reiter caller']})
    commands=[['/opt/homebrew/bin/gfortran','-c','-O0','-fPIC','-std=legacy','-ffixed-line-length-none','atkin-original.f','-o','atkin.o'],['/usr/bin/clang++','-c','-O2','-fPIC','-std=c++17','-I/opt/homebrew/include','adapter.cc','-o','adapter.o'],['/opt/homebrew/bin/gfortran','-dynamiclib','atkin.o','adapter.o','-L/opt/homebrew/lib','-lgmpxx','-lgmp','-lstdc++','-o','native.dylib']]
    # Apple's libc++ is selected explicitly; no GNU C++ library dependency.
    commands[-1][-3:]=['-L/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib','-lc++','-o','native.dylib']
    for i,cmd in enumerate(commands):
        with (P/f'compile-{i}.stdout').open('wb') as out,(P/f'compile-{i}.stderr').open('wb') as err:r=subprocess.run(cmd,cwd=P,stdout=out,stderr=err,timeout=120)
        put(P/f'COMPILE-{i}.json',{'command':cmd,'returncode':r.returncode});assert r.returncode==0
    freeze()
def freeze():
    put(P/'PROTOCOL.json',{'id':'ATKIN-NATIVE-GETALL-01','frozen_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'question':'Does the recovered 1993 type-II modular-to-elliptic routine exhibit an exception or validation failure separating all eleven reconstructed omissions from ten publications?', 'cohort_sha256':COHORT_SHA,'cells':315,'rational_parameters':299,'streams':6,'arms':[26,30],
        'controls':{'derivatives':'15 type-II tables at p=1009 and 2^61-1, alpha37,j34, both limb widths; compare all five outputs to direct ordinary/Euler coefficient-weighted partials.','regular':'p1009, A990,B660,j34,ell53, enumerate all rational parameters, require one accepted kernel.','exception':'p1009,A199,B469,j24,ell53,alpha98; require a recorded zero division.','multiword':'MSW limb roundtrip of 2^26 and 2^30 at both widths.','AA':'Repeat the first successful regular input after the cohort and require identical observations.'},
        'adapters':{'ZL':'New exact GMP implementation with normalized most-significant-word-first unsigned limbs. Original format not established.','GETJQN':'New FLINT complete rational-root enumeration, sorted ascending, source j removed. Original ordering not recovered.','CHARLA':'New corrected CCR power-sum/Newton kernel reconstruction; verify division-polynomial remainder, cyclicity and Velu quotient coherence. Original routine unavailable.','ELKCOF':'Not used after GETALL; adapter returns a placeholder. No eigenvalue/CRT/point-counting execution.'},
        'inputs':'p,A,B,alpha,ell and tables only. Labels/orders/seeds not passed to native source or validator. Full labels joined after observations.',
        'fixed_order':'Controls before cohort; level then index then sorted alpha, width26 followed by30. Exact deterministic arithmetic, no timing comparison.','watchdog_seconds':1800,'checkpoint':'No resume; partial and errors retained.','metrics':['source calls','candidate neighbor attempts','zero divisions','FLAG success/failure','kernel validity','cross-width equality'],'uncertainty':'Exact counts on the fixed finite cohort; no population extrapolation or p-value.','stopping':'Fail closed before cohort if control checks fail. Stop after every fixed parameter in both arms and A/A repeat.','claims':'Source-body execution with reconstructed dependencies and modern coefficient tables; not an original 1997 program run or an attribution of historical use.',
        'source_dependencies':{'Morain1995':'Previously read corrected CCR kernel formulas, printed pages275-276; local canonical-equations-01/PAPER-SOURCE.json','Atkin19930303':'Previously read derivative conventions and canonical interface','Atkin19930305':'Actual GETPAA/GETALL body read from retained author-hosted email'},
        'code_and_input_hashes':{str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f.suffix not in ['.o','.dylib']}})
    print('PREPARED',sha(P/'PROTOCOL.json'),flush=True)
def run():
    assert not (P/'STARTED.json').exists();plan=json.loads((P/'PROTOCOL.json').read_text())
    for f,h in plan['code_and_input_hashes'].items():assert sha(P/f)==h,f
    tables=load_tables();put(P/'STARTED.json',{'protocol_sha256':sha(P/'PROTOCOL.json'),'native_sha256':sha(P/'native.dylib'),'host':platform.platform(),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    controls=[];rows=json.loads((P/'rows.json').read_text());start=time.monotonic()
    with (P/'observations.jsonl').open('x') as out:
        def emit(z):out.write(json.dumps(z,separators=(',',':'))+'\n');out.flush()
        for bits in plan['arms']:
            native=Native(bits,tables)
            for p in [1009,2**61-1]:
                for q,(v,table) in tables.items():
                    value,ops=native.paa(q,p,37,34);expected=derivatives(table,37,34,p)
                    emit({'kind':'derivative_control','bits':bits,'p':p,'q':q,'actual':value,'expected':expected,'arithmetic':ops});assert value==expected
            for z in [0,1,2**26,2**30,2**60,2**520-1]:assert native.read(native.pack(z))==z
            regular=[];R=fmpz_mod_poly_ctx(1009);roots=sorted(int(z) for z,m in R(polyA(tables[53][1],34,1009)).roots())
            for a in roots:
                z=native.all(53,1009,990,660,a);z['kind']='regular_control';emit(z);regular.append(z)
                assert not z['errors']
            assert any(z['flag']==0 and not z['arithmetic']['zero_divisions'] for z in regular)
            ex=native.all(53,1009,199,469,98);ex['kind']='exception_control';emit(ex);assert ex['arithmetic']['zero_divisions']>0
            controls.append((bits,next(z for z in regular if z['flag']==0 and not z['arithmetic']['zero_divisions'])))
        print('CONTROLS_COMPLETE',flush=True)
        for cell in json.loads((P/'CELLS.json').read_text()):
            i,q,p=cell['index'],cell['ell'],cell['p'];A=p-3;B=int(rows[i]['b'])
            for a in cell['roots']:
                paired=[]
                for bits in plan['arms']:
                    z=Native(bits,tables).all(q,p,A,B,a);z.update(kind='cohort',index=i);emit(z);paired.append(z)
                    assert not z['errors'],z['errors']
                normalized=[{k:v for k,v in z.items() if k not in ['bits','arithmetic']} for z in paired];assert normalized[0]==normalized[1]
            print('CELL_COMPLETE',q,i,len(cell['roots']),flush=True)
        for bits,ref in controls:
            z=Native(bits,tables).all(ref['q'],ref['p'],ref['A'],ref['B'],ref['alpha']);z['kind']='regular_control';assert z==ref;z['kind']='AA_control';emit(z)
        emit({'kind':'complete','cohort_source_calls':598,'cells':315});print('COHORT_COMPLETE',flush=True)
    put(P/'RESULT.json',{'status':'terminal','returncode':0,'elapsed_seconds_diagnostic_only':time.monotonic()-start,'observations_sha256':sha(P/'observations.jsonl')})
if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
