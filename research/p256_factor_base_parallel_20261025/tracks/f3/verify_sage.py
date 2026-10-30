"""Independent verifier: uses Sage group arithmetic, never imports labelled.py.

Run inside cached sagemath/sagemath:10.6 with the track mounted read-only.
"""
import json
import sys
from pathlib import Path
from hashlib import sha256
from itertools import product
from sage.all import GF, EllipticCurve, PolynomialRing, Integer, version

root=Path(sys.argv[1]); records=root/'receipts'/'validation-02'
p=2**256-2**224+2**192+2**96-1
r=int('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551',16)
b=int('5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b',16)
E=EllipticCurve(GF(p),[-3,b]); O=E(0)
G=E(int('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296',16),
    int('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5',16))
checks=0
def check(v):
    global checks
    assert v
    checks+=1
check(r*G==O)
rows=[]
for name in ('natural_random','arranged_zero_Q','arranged_useful'):
    path=records/(name+'.json'); data=json.loads(path.read_text())
    Q=E(data['Q']); base=data['base']; points=[E(z['point']) for z in base]
    check(r*Q==O)
    for z,P in zip(base,points): check(z['a']*G+z['b']*Q==P)
    R=PolynomialRing(GF(p),'T'); T=R.gen()
    for part,coeffs in zip(data['partitions'],data['membership_polynomials_ascending']):
        polynomial=R(1)
        for i in part: polynomial*=T-points[i][0]
        check(polynomial==R(coeffs))
    found=[]; group_checks=0; coordinate_roots=[]
    for i,j,k in product(*data['partitions']):
        x,y,z=(points[l][0] for l in (i,j,k))
        value=(x-y)**2*z*z-2*((x+y)*(x*y-3)+2*b)*z+(x*y+3)**2-4*b*(x+y)
        if value==0: coordinate_roots.append([i,j,k])
        for sj,sk in product((1,-1),repeat=2):
            group_checks+=1
            if points[i]+sj*points[j]+sk*points[k]==O:
                found.append(dict(indices=[i,j,k],signs=[1,sj,sk]))
    check(found==data['hybrid']['relations'])
    check(found==data['exhaustive']['relations'])
    check(sorted(coordinate_roots)==sorted(data['hybrid']['coordinate_roots']))
    for relation,assessment in zip(found,data['assessments']):
        ids=relation['indices']; signs=relation['signs']
        A=sum(s*base[i]['a'] for i,s in zip(ids,signs))%r
        B=sum(s*base[i]['b'] for i,s in zip(ids,signs))%r
        check(A==assessment['A'] and B==assessment['B'])
        check(A*G+B*Q==O)
        if B:
            recovered=int(-Integer(A)*Integer(B).inverse_mod(r)%r)
            check(recovered*G==Q and recovered==assessment['recovered'])
        else: check(not assessment['useful'] and A==0)
    rows.append(dict(case=name,labels=len(base),complete_point_sum_checks=group_checks,
        coordinate_domain_triples=8**3,dependencies=len(found),
        useful=sum(z['useful'] for z in data['assessments']),
        input_sha256=sha256(path.read_bytes()).hexdigest()))
print(json.dumps(dict(schema='f3-independent-sage/v1',status='passed',sage=version(),
    independence='Sage group and polynomial arithmetic; imports no producer code',
    checks=checks,cases=rows),indent=2))
