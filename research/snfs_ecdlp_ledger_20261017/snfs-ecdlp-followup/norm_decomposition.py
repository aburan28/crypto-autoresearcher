"""Dedicated quadratic-norm point decomposition on synthetic small curves.

For f=A(x)y^2+B(x)y+C(x) and L=2^s,
  Res_y(f,y^L-1)=A^L+C^L-U_L,
where U_1=-B and U_2n=U_n^2-2(AC)^n.
All x-polynomial arithmetic is performed modulo x^L-1.
This is a standard resultant/power-sum identity, not a novelty claim.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/'snfs-ecdlp-experiments'
sys.path.insert(0,str(PREV))
from core import EC, isprime, rng, time, json
import flint
from flint import nmod_poly, nmod
from sympy import primitive_root, sqrt_mod
from statistics import median


class LiteEC(EC):
    def __init__(self,p,a,b):
        assert isprime(p) and (4*a**3+27*b*b)%p
        self.p,self.a,self.b=p,a%p,b%p;self.ops=0
    def xpoints(self,x):
        if getattr(self,'backend','sympy')=='flint':
            try:y=int(nmod((x**3+self.a*x+self.b)%self.p,self.p).sqrt())
            except flint.utils.flint_exceptions.DomainError:return []
            return [(x,v) for v in sorted({y,(-y)%self.p})]
        return [(x,int(y)) for y in sqrt_mod((x**3+self.a*x+self.b)%self.p,self.p,all_roots=True)]


def modulus(p,L):return nmod_poly([-1]+[0]*(L-1)+[1],p)


def norm_poly(E,R,L,M):
    p=E.p;z=R[0];a=E.a;b=E.b
    A=nmod_poly([z*z,-2*z,1],p)
    B=nmod_poly([-2*a*z-4*b,-2*(z*z+a),-2*z],p)
    C=nmod_poly([a*a-4*b*z,-2*a*z-4*b,z*z],p)
    U=-B;Q=(A*C)%M;AP=A%M;CP=C%M
    for step in range(L.bit_length()-1):
        U=(U*U-2*Q)%M
        Q=(Q*Q)%M;AP=(AP*AP)%M;CP=(CP*CP)%M
    return (AP+CP-U)%M,(A,B,C)


def norm_solve(E,R,L,M):
    begin=time.perf_counter();N,(A,B,C)=norm_poly(E,R,L,M)
    gcd=N.gcd(M);roots=gcd.roots();checked=0;degenerate=False
    for xx,mult in roots:
        x0=int(xx);fx=nmod_poly([int(C(x0)),int(B(x0)),int(A(x0))],E.p)
        if fx.is_zero():
            degenerate=True;g=int(primitive_root(E.p));zeta=pow(g,(E.p-1)//L,E.p)
            ys=[];v=1
            for _ in range(L):ys.append((v,1));v=v*zeta%E.p
        else:ys=fx.roots()
        for yy,mult2 in ys:
            y0=int(yy)
            if pow(y0,L,E.p)!=1:continue
            checked+=1
            for P in E.xpoints(x0):
                for Q in E.xpoints(y0):
                    if E.add(P,Q)==R:
                        return dict(found=True,points=[P,Q],candidate_x_roots=len(roots),
                            gcd_degree=gcd.degree(),checked_xy=checked,
                            degenerate_quadratic=degenerate,wall_seconds=time.perf_counter()-begin)
    return dict(found=False,candidate_x_roots=len(roots),gcd_degree=gcd.degree(),
        checked_xy=checked,degenerate_quadratic=degenerate,wall_seconds=time.perf_counter()-begin)


def build_fb(E,L):
    start=time.perf_counter();g=int(primitive_root(E.p));zeta=pow(g,(E.p-1)//L,E.p)
    xs=[];v=1;FB=[]
    for _ in range(L):
        xs.append(v);FB.extend(E.xpoints(v));v=v*zeta%E.p
    assert len(set(xs))==L and v==1
    return FB,set(FB),time.perf_counter()-start


def enumeration(E,FB,allowed,R):
    start=time.perf_counter();tested=0
    for P in FB:
        tested+=1;Q=E.add(R,E.neg(P))
        if Q in allowed:
            assert E.add(P,Q)==R
            return dict(found=True,wall_seconds=time.perf_counter()-start,points_tested=tested)
    return dict(found=False,wall_seconds=time.perf_counter()-start,points_tested=tested)


def run(backend='sympy',extended=False):
    rows=[];checks=[];start_all=time.perf_counter()
    sizes=(2048,4096,8192,16384,32768) if extended else (4,8,16,32,64,128,256,512,1024)
    for L in sizes:
        p=next(k*L+1 for k in range(L,3*L) if isprime(k*L+1))
        for case in range(3):
            gen=rng('SNFS-A3',f'round2-norm:{L}:{case}')
            while True:
                a,b=gen.randrange(p),gen.randrange(p)
                if (4*a**3+27*b*b)%p:break
            E=LiteEC(p,a,b);E.backend=backend
            FB,allowed,fbtime=build_fb(E,L)
            assert FB
            begin=time.perf_counter();M=modulus(p,L);normsetup=time.perf_counter()-begin
            if L<=16:
                # Independent resultants at arbitrary x, including possible A=0.
                R=FB[0]
                N,(A,B,C)=norm_poly(E,R,L,M)
                # Before reduction, evaluate the same recurrence as scalars.
                for xx in [R[0]]+[gen.randrange(p) for _ in range(8)]:
                    aa,bb,cc=int(A(xx)),int(B(xx)),int(C(xx));U=-bb%p;Q=aa*cc%p
                    AP,CP=aa,cc
                    for _ in range(L.bit_length()-1):
                        U=(U*U-2*Q)%p;Q=Q*Q%p;AP=AP*AP%p;CP=CP*CP%p
                    direct=int(nmod_poly([cc,bb,aa],p).resultant(modulus(p,L)))
                    assert (AP+CP-U)%p==direct%p
                    checks.append(dict(p=p,L=L,x=xx,resultant_identity=True))
            for mode in ('fresh','planted'):
                for trial in range(8):
                    if mode=='planted':
                        for _ in range(1000):
                            R=E.add(gen.choice(FB),gen.choice(FB))
                            if R is not None:break
                        else:raise RuntimeError('No finite planted sum')
                    else:
                        while True:
                            pts=E.xpoints(gen.randrange(p))
                            if pts:R=gen.choice(pts);break
                    nr=norm_solve(E,R,L,M);er=enumeration(E,FB,allowed,R)
                    assert nr['found']==er['found']
                    rows.append(dict(p=p,L=L,a=a,b=b,case=case,mode=mode,trial=trial,R=R,
                        factor_base_points=len(FB),enumeration_setup_seconds=fbtime,
                        norm_setup_seconds=normsetup,norm=nr,enumeration=er,
                        norm_cold_total_seconds=normsetup+nr['wall_seconds'],
                        enumeration_cold_total_seconds=fbtime+er['wall_seconds']))
            print(json.dumps(dict(stage='norm',L=L,p=p,case=case,rows=len(rows))),flush=True)
    summary=[]
    for L in sorted({r['L'] for r in rows}):
        cohort=[r for r in rows if r['L']==L and r['mode']=='fresh'];cold=[];batch=[]
        for r in cohort:cold.append(r['norm_cold_total_seconds']/r['enumeration_cold_total_seconds'])
        for case in range(3):
            cc=[r for r in cohort if r['case']==case]
            nt=cc[0]['norm_setup_seconds']+sum(r['norm']['wall_seconds'] for r in cc)
            et=cc[0]['enumeration_setup_seconds']+sum(r['enumeration']['wall_seconds'] for r in cc)
            batch.append(nt/et)
        summary.append(dict(L=L,p=cohort[0]['p'],fresh_cases=len(cohort),
            decomposable_fresh=sum(r['norm']['found'] for r in cohort),
            cold_norm_to_enumeration_median=median(cold),
            eight_target_batch_norm_to_enumeration_median=median(batch),
            solver_only_norm_to_enumeration_median=median(r['norm']['wall_seconds']/r['enumeration']['wall_seconds'] for r in cohort)))
    result=dict(provisional_id='SNFS-A3',scope='Dedicated norm/gcd decomposition over repeated-power subgroup bases; synthetic small fields only',
        algorithm_identity='Res_y(A y^2+B y+C,y^L-1)=A^L+C^L-U_L; U_2n=U_n^2-2(AC)^n',
        novelty='No novelty claimed for the standard resultant/power-sum identity.',
        solver_input='Curve coefficients, target point, p, L, x^L-1. No enumerated factor base or planted answer is passed to the norm solver.',
        cost_scope='Norm cold cost includes polynomial modulus construction and candidate root/point verification. Enumeration cold cost includes primitive-root selection, all subgroup x values, square roots, hashing and verified target search. Target/curve generation is excluded equally.',
        rows=rows,summary=summary,checks=checks,wall_seconds=time.perf_counter()-start_all,
        flint_version=flint.__version__,point_root_backend=backend,limitations=[
            'm=2 only; factor-base size is about sqrt(p), so this is not a completed index-calculus advantage over rho.',
            'Explicit polynomial arithmetic still has degree L. Speedups can reflect avoiding per-element square roots and native arithmetic, not a smaller asymptotic exponent.',
            'Only one enumeration implementation is compared; exhaustive shared precomputation for arbitrarily many targets is a different cost model.',
            'The three curves at each size and eight fresh targets per curve are finite controls, not an exponent study.'
        ])
    filename='norm-extended-results.json' if extended else ('norm-native-results.json' if backend=='flint' else 'norm-results.json')
    (ROOT/filename).write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else 'sympy',len(sys.argv)>2 and sys.argv[2]=='extended')
