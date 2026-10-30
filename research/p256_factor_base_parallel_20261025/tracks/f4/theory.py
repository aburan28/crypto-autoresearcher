"""Exact counting controls derived in report.md; no random trial."""
from fractions import Fraction
import importlib.util
import json
from math import comb, factorial
from pathlib import Path
import sys
P=Path(__file__).resolve().parents[2]/'baseline'/'parameters.py'
spec=importlib.util.spec_from_file_location('constants',P)
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
c=next(v for v in module.CURVES if v['name']=='P-256')
p,r=c['p'],c['r']
values=[]
for m in range(2,9):
    numerator=comb(r+m-2,m)
    assert numerator%r==0
    count=numerator//r
    functions_projective=p**(m-1)
    probability=Fraction(count,functions_projective)
    values.append({'pole_order':m,'fully_rational_affine_effective_divisors':count,
                   'exact_pole_projective_functions':functions_projective,
                   'fully_rational_probability_numerator':probability.numerator,
                   'fully_rational_probability_denominator':probability.denominator,
                   'asymptotic_reference_denominator_factorial':factorial(m),
                   'interpretation':'all rational zeros anywhere on E, not factor-base yield'})
# Independent finite integer enumeration of the Burnside identity for small
# abstract cyclic groups. This checks the counting formula, not elliptic data.
from itertools import combinations_with_replacement
checks=[]
for order in [5,7,11,13]:
    for m in range(2,min(order,7)):
        observed=sum(sum(D)%order==0 for D in combinations_with_replacement(range(1,order),m))
        expected=comb(order+m-2,m)//order
        assert observed==expected
        checks.append({'abstract_cyclic_order':order,'degree':m,'enumerated':observed,'formula':expected})
record={'status':'passed','method':'exact integers; no sampled yield measurements',
        'p':p,'r':r,'formula':'C(r+m-2,m)/(r*p^(m-1)), for 2<=m<r',
        'controls':values,'abstract_counting_checks':checks,
        'command':[sys.executable]+sys.argv}
Path(sys.argv[1]).write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':'passed','pole_orders':len(values),'abstract_counting_checks':len(checks)}))
