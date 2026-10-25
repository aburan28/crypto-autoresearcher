#!/usr/bin/env python3
"""Recompute determinant, LLL transform and integer zero lift from emitted rows."""
import hashlib,json
from pathlib import Path
import sympy as S
H=Path(__file__).resolve().parent
r=json.loads((H/'receipt.json').read_text());d=json.loads((H/'bounded_lattice_certificate.json').read_text())
p=r['curve']['p'];M=S.Matrix(d['basis_rows']);L=S.Matrix(d['lll_rows'])
T=L*M.inv();assert all(v.q==1 for v in T) and abs(T.det())==1
assert abs(M.det())==p**8*2**18 and abs(L.det())==abs(M.det())
x,y=S.symbols('x y');polys=[]
for row in L.tolist():
    if 9*sum(c*c for c in row)>=p*p:continue
    coefficients=[]
    for c,(a,b) in zip(row,d['mons']):
        assert int(c)%2**(a+b)==0;coefficients.append(int(c)//2**(a+b))
    assert sum(coefficients)==0
    polys.append(sum(c*x**a*y**b for c,(a,b) in zip(coefficients,d['mons'])))
G=S.groebner(polys,x,y,domain=S.QQ);assert list(G)==[x-1,y-1]
for c in r['finite_cases']:
    s,e,D,m=c['variables'],c['individual_degree'],c['D'],c['m']
    n=(D+1)**s;K=sum((D-e*k+1)**s for k in range(1,min(m,D//e)+1))
    assert n==c['n'] and K==c['K']
    b=c['largest_admissible_power_of_two_b']; rhs=p**(4*K)
    exp=n*(n-1);bexp=2*s*D*n
    if exp>=rhs.bit_length():assert b is None
    else:
        lhs=n**(2*n)<<exp
        if b is None:assert lhs>=rhs
        else:
            assert lhs<<(b*bexp)<rhs
            assert lhs<<((b+1)*bexp)>=rhs
for c in r['digit_box']['cases']:
    D=c['D'];n=S.binomial(D+4,4);A=S.binomial(D+4,5)
    K=sum(S.binomial(D-4*k+4,4) for k in range(1,D//4+1))
    assert (int(n),int(A),int(K))==(c['n'],c['A_per_digit'],c['K'])
    # All these emitted cases were rejected already by the exact bit-length bound.
    assert int(n*(n-1)) >= (p**int(4*K)).bit_length()
    assert c['largest_admissible_power_of_two_b'] is None
out={'completion_sentinel':True,'unimodular_lll_transform':True,'lifted_polynomials':len(polys),
     'integer_groebner_basis':[str(g) for g in G],'parameter_cases_rechecked':len(r['finite_cases']),
     'digit_parameter_cases_rechecked':len(r['digit_box']['cases']),
     'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [H/'check_bounds.py',Path(__file__)]},
     'scope':'Separate artifact recheck; same session, not independent review'}
(H/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
