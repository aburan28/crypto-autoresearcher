"""Exact independent remainder/Jacobian checks and complete stratum recombination."""
import hashlib,itertools,json,math,sys
from pathlib import Path
from flint import fmpz_mod_poly_ctx
from cubic import ROOT,V,p,remainder_circuit,repeated_equations,fixture,oracle,record,write,evaluate,f1


def det(M):
    return sum((-1)**sum(q[i]>q[j] for i in range(3) for j in range(i+1,3))*
        M[0][q[0]]*M[1][q[1]]*M[2][q[2]] for q in itertools.permutations(range(3)))%p

def plus(a,b):return tuple((x+y)%p for x,y in zip(a,b))
def times(a,b):return (a[0]*b[0]%p,)+tuple((a[0]*b[j]+a[j]*b[0])%p for j in range(1,4))
def constant(x):return (x%p,0,0,0)

def dual_remainder(k,c,s):
    """Automatic differentiation plus generic long polynomial reduction.

This uses independent coefficient convolution/long reduction, rather than the
closed-form t^4 coefficient expressions used in the symbolic solver.
"""
    u,v,w=[(value,)+tuple(int(j==i) for j in range(3)) for i,value in enumerate(s)]
    r=[constant(0),constant(1),constant(0)]
    for _ in range(k):
        q=[constant(0) for _ in range(5)]
        for i,x in enumerate(r):
            for j,y in enumerate(r):q[i+j]=plus(q[i+j],times(x,y))
        # t^3 = u*t^2 - v*t + w, applied high-to-low.
        for degree in [4,3]:
            lead=q[degree]
            q[degree-1]=plus(q[degree-1],times(lead,u))
            q[degree-2]=plus(q[degree-2],times(lead,tuple(-z%p for z in v)))
            q[degree-3]=plus(q[degree-3],times(lead,w))
        r=q[:3];r[0]=plus(r[0],constant(-2))
    r[0]=plus(r[0],constant(-c))
    return [a[0] for a in r],[list(a[1:]) for a in r]

def point_add(P,Q):
    if P is None:return Q
    if Q is None:return P
    x,y=P;z,w=Q
    if x==z and (y+w)%p==0:return None
    if P==Q:num,den=3*x*x+f1.a,2*y
    else:num,den=w-y,z-x
    slope=num*pow(den,p-2,p)%p
    X=(slope*slope-x-z)%p
    return X,(slope*(x-X)-y)%p

def triple_solutions(F,Q):
    out=[]
    for i,j,k in itertools.combinations_with_replacement(range(len(F)),3):
        if point_add(point_add(F[i],F[j]),F[k])==Q:out.append((i,j,k))
    return out

def polynomial_checks():
    C=fmpz_mod_poly_ctx(p);T=C([0,1]);records=[];random_checks=0
    for k in range(2,6):
        c=7;eqs,levels=remainder_circuit(k,c);F=T
        for _ in range(k):F=F*F-2
        F-=c
        for i in range(10):
            vals=tuple(int.from_bytes(hashlib.sha256(f'cubic/{k}/{i}/{j}'.encode()).digest(),'big')%p for j in range(3))
            h=C([-vals[2],vals[1],-vals[0],1]);rem=F%h
            independent,J=dual_remainder(k,c,vals)
            assert independent==[int(rem[j]) for j in range(3)]
            assert [evaluate(f,vals) for f in eqs]==independent
            assert [[evaluate(f.diff(v),vals) for v in V] for f in eqs]==J
            random_checks+=1
        records.append({'k':k,'coefficient_shapes':levels[-1]['coefficients'],'identity_cases':10})
    exact=[]
    for k in [2,3,4]:
        fix=fixture(ROOT.parent/'checks-02'/f'generic-k{k}.json')
        xs,c=fix['xs'],fix['c'];F=T
        for _ in range(k):F=F*F-2
        F-=c;fact=C([1])
        for x in xs:fact*=T-x
        assert fact==F and F.gcd(F.derivative()).degree()==0
        jcount=0
        for triple in itertools.combinations(xs,3):
            s=f1.elementary(triple);h=C([-s[2],s[1],-s[0],1]);q=F//h
            assert not F%h and h.gcd(q).degree()==0
            val,J=dual_remainder(k,c,s);assert val==[0,0,0]
            M=[]
            columns=[(q*T**j)%h for j in range(3)]
            for i in range(3):M.append([int(column[i]) for column in columns])
            assert det(J)==det(M) and det(J)!=0;jcount+=1
        distinct=math.comb(len(xs),3);two=len(xs)*(len(xs)-1);same=len(xs)
        assert distinct+two+same==math.comb(len(xs)+2,3)
        exact.append({'k':k,'S':len(xs),'factor_identity':True,'separable':True,
                      'jacobians_nonzero_and_equal_quotient_resultant':jcount,
                      'distinct_states':distinct,'twoequal_states':two,'allequal_states':same})
    # Scope control: at ramified c=2 the three distinct roots (-2,0,2) divide F,
    # but F/h shares t with h, so the Jacobian is zero. No reduced claim applies.
    val,J=dual_remainder(3,2,(0,p-4,0))
    assert val==[0,0,0] and det(J)==0
    return {'symbolic_numeric_remainder_and_gradient_cases':random_checks,'representation':records,
            'complete_separable_domains':exact,'outside_scope_control':{
             'k':3,'c':2,'h':'t^3-4t','three_distinct_roots':[-2,0,2],
             'remainder_zero':True,'jacobian_determinant':0,'status':'expected hypothesis failure'}}

def deep_checks():
    out=[]
    for k in [6,7,8,16,32,64,96]:
        c,_,j,w=f1.torus_roots(k,2,enumerate_roots=False);z=f1.torus(2);xs=[]
        assert c not in (2,p-2)
        for _ in range(3):xs.append(f1.trace(z));z=f1.cmul(z,w)
        assert len(set(xs))==3
        s=f1.elementary(xs);val,J=dual_remainder(k,c,s)
        assert val==[0,0,0] and det(J)!=0
        out.append({'k':k,'S':1<<k,'c':c,'three_distinct_roots':xs,'symmetric':s,
             'remainder':val,'jacobian_determinant':det(J),'complete_solver_claim':False,
             'witness_only':True})
    return out

def combine():
    folder=ROOT/'attempts-01';receipt=json.loads((folder/'receipt.json').read_text());groups={}
    for r in receipt:
        label=r['label']
        if label.endswith('-membership'):continue
        stratum,depth,target=label.split('-');key=(int(depth[1:]),target)
        groups.setdefault(key,{})[stratum]=r
    combined=[]
    for (k,target),rs in groups.items():
        fix=fixture(ROOT.parent/'checks-02'/('generic-k4.json' if k==4 else 'generic-k3.json'),k,target)
        F,Q=fix['F'],fix['Q'];direct=triple_solutions(F,Q)
        rec={'k':k,'target_kind':target,'Q':Q,'domain':fix['xs'],'signed_base':F,
             'full_signed_oracle':direct,'strata':{},'complete_algebraic_combination':False}
        union=set()
        for s in ['distinct','twoequal','allequal']:
            r=rs[s];row={'status':r['status']}
            if r['status']=='PASS':
                d=json.loads((folder/(r['label']+'.json')).read_text())
                assert d['complete_stratum_points']==[list(z) for z in oracle(fix,s)]
                got=[tuple(x) for x in d['signed_decompositions']];union.update(got)
                row.update(point_count=d['complete_point_count'],signed_solution_count=len(got))
            rec['strata'][s]=row
        if all(r['status']=='PASS' for r in rs.values()):
            assert sorted(union)==direct;rec['complete_algebraic_combination']=True
        else:
            assert union<=set(direct)
            rec['unknown_reason']='At least one solver stratum stopped; full oracle is reference, not a completed algebraic solve.'
        combined.append(rec)
    return combined

def main():
    out=ROOT/'checks-01';out.mkdir(exist_ok=False)
    proof={'status':'PASS','polynomial_checks':polynomial_checks(),'deep_distinct_witnesses':deep_checks()}
    write(out/'identities.json',proof)
    records=combine();summary=[]
    for rec in records:
        name=f'query-k{rec["k"]}-{rec["target_kind"]}.json';write(out/name,rec)
        summary.append({'file':name,'k':rec['k'],'target':rec['target_kind'],
            'signed_solutions':len(rec['full_signed_oracle']),
            'complete_algebraic_combination':rec['complete_algebraic_combination']})
    write(out/'receipt.json',{'status':'PASS','independent_code_path':'Polynomial long division/dual gradients, explicit factorization, and signed triple sums; same session',
      'queries':summary,'fully_completed_queries':sum(r['complete_algebraic_combination'] for r in records),
      'partial_unknown_queries':sum(not r['complete_algebraic_combination'] for r in records)})
    print(json.dumps({'proof_checks':'PASS','complete_queries':sum(r['complete_algebraic_combination'] for r in records),
       'partial_unknown':sum(not r['complete_algebraic_combination'] for r in records),'deep_distinct_witnesses':7}),flush=True)

if __name__=='__main__':main()
