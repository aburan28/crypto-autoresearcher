#!/usr/bin/env python3
"""Corrupt copies of certificates, using only this review's independent code."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import sympy as sp
import independent_checks as c

HERE=Path(__file__).resolve().parent
OUTPUT=HERE/'adversarial-results.json'
assert not OUTPUT.exists(), 'write-once output path already exists'
events=[]


def reject(name,fn):
    try:
        fn()
    except AssertionError as error:
        events.append({'control':name,'expected_rejection_observed':True,'reason':str(error)})
        return
    raise AssertionError('invalid control accepted: '+name)


folder=c.TRACKS/'f4'/'receipts'/'check-04'
ctx=c.flint.fmpz_mod_poly_ctx(c.P)
original=c.read(folder/'pole3.json')
for kind in ['norm','zero_multiplicity','signed_row','anchor_multiplicity']:
    obj=deepcopy(original)
    if kind=='norm':
        obj['norm'][0]=(obj['norm'][0]+1)%c.P
    elif kind=='zero_multiplicity':
        obj['zeros'][0]['multiplicity']+=1
    elif kind=='signed_row':
        key=next(iter(obj['row']))
        obj['row'][key]+=1
    else:
        obj['declared_anchors']=[obj['declared_anchors'][0]]*4
    reject('F4_corrupt_'+kind,lambda obj=obj:c.f4_case(obj,ctx))

graph=c.read(folder/'graph_one_outside.json')
raw=[c.read(folder/(name+'.json'))['row'] for name in graph['case_ids']]
outside=graph['outside_columns']
combination=deepcopy(graph['cancelled_rows'][0]['combination'])
column=outside[0]
at=next(i for i,row in enumerate(raw) if row.get(column,0)%c.R)
combination[at]=(combination[at]+1)%c.R
reject('F4_corrupt_stitching_coefficient',lambda:c.require(
    all(sum(a*row.get(key,0) for a,row in zip(combination,raw))%c.R==0 for key in outside),'outside coefficient fails to cancel'))
reject('F4_corrupt_reported_rank',lambda:c.require(
    c.rank([[row.get(key,0) for key in graph['all_columns']] for row in raw],c.R)==graph['rank_before_all_columns']+1,
    'reported rank differs from independent elimination'))

fixture=c.read(c.TRACKS/'f3'/'receipts'/'validation-02'/'arranged_useful.json')
obj=deepcopy(fixture['base'][0])
obj['a']=(obj['a']+1)%c.R
q=tuple(fixture['Q'])
reject('F3_corrupt_label',lambda:c.require(c.EP.add(c.EP.mul(obj['a'],c.GP),c.EP.mul(obj['b'],q))==tuple(obj['point']),
    'forged label is not the declared point'))
reject('F3_integer_nonzero_implies_useful_law',lambda:c.require(c.R%c.R!=0,
    'c=(r) is zero in F_r and forces B=0'))

cert=c.read(c.TRACKS/'f6'/'bounded_lattice_certificate.json')
matrix=sp.Matrix(cert['basis_rows'])
mutant=sp.Matrix(cert['lll_rows'])
mutant[0,0]+=1
transform=mutant*matrix.inv()
reject('F6_corrupt_lattice_row',lambda:c.require(all(v.q==1 for v in transform) and abs(transform.det())==1,
    'corrupt row has no integral unimodular change of basis'))
x,y=sp.symbols('x y')
reject('F6_one_lifted_polynomial_proves_extraction',lambda:c.require(
    sp.groebner([x-1],x,y,domain=sp.QQ).is_zero_dimensional,'a single linear polynomial leaves a positive-dimensional solution set'))
require_known_offsets=cert['offsets']
require_points=c.read(c.TRACKS/'f6'/'receipt.json')['public_constructed_points']
c.require(require_known_offsets==[require_points['P'][0]-1,require_points['Q'][0]-1],'known-root fixture remains explicit')

orbit=c.read(c.TRACKS/'f8'/'orbit_certificate.json')
factor=(orbit['compression_factor'][0]+1)%c.KR
reject('F8_corrupt_orbit_factor',lambda:c.require(
    c.EK.mul(factor,tuple(orbit['representatives'][orbit['representative_index'][0]]))==tuple(orbit['points'][0]),
    'orbit factor does not act as certified'))
reject('F8_false_full_rank_row',lambda:c.require(c.EK.linear([1]+[0]*7,[tuple(v) for v in orbit['representatives']]) is None,
    'false full-rank row sums to the nonidentity representative G'))

record={'schema':'local-adversarial-certificate-controls/v1','task':'TASK-20261025-6d88b2',
    'producer_imports':False,'status':'passed','rejected_invalid_controls':events,
    'known_root_offsets_are_not_ordinary_target_evidence':True,'command':[sys.executable,*sys.argv]}
OUTPUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':'passed','expected_rejections':len(events),'output':str(OUTPUT)}))
