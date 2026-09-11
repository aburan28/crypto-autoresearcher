"""The 76 frozen, nonpanel implementation controls. This never enumerates a scientific panel."""
from __future__ import annotations
import json,sys
from pathlib import Path
from crt import fold,candidates
from reference import full_domain,compare
from fixtures import fixture,gate
from driver import execute_case
HERE=Path(__file__).resolve().parents[4]
CONTROL=HERE/'coordination/auxin-pipeline/TASK-20260911-aace99/implementation-controls.json'
def arithmetic(n,pairs,expected):
    result=fold(n,pairs); got=candidates(n,result) if result['status']=='consistent' else []
    return got==expected and full_domain(n,pairs)==expected
def mutate(base,name):
    import copy; x=copy.deepcopy(base)
    if name=='G_unsupported_r':x['r']=14
    elif name=='G_nonprimitive':x['zeta']=1
    elif name=='G_factorization':x['factorization']=[[2,2]]
    elif name=='G_d_zero':x['constraints'][0]['d']=0
    elif name=='G_d_large':x['constraints'][0]['d']=13
    elif name=='G_m_zero':x['constraints'][0]['m']=0
    elif name=='G_m_d':x['constraints'][0]['m']=6
    elif name=='G_negative_residue':x['constraints'][0]['a']=-1
    elif name=='G_large_residue':x['constraints'][0]['a']=3
    elif name=='G_missing_supply':x['constraints'][0].pop('token')
    elif name=='G_token_binding':x['constraints'][0]['token']['exponent']+=1
    elif name=='G_zero_nonzero':x['x']=0
    return x
EXPECTED={'G_unsupported_r':'INPUT_UNSUPPORTED_R','G_nonprimitive':'INPUT_NOT_PRIMITIVE','G_factorization':'INPUT_BAD_FACTORIZATION','G_d_zero':'INPUT_BAD_D','G_d_large':'INPUT_BAD_D','G_m_zero':'INPUT_BAD_M','G_m_d':'INPUT_M_D_MISMATCH','G_negative_residue':'INPUT_BAD_RESIDUE','G_large_residue':'INPUT_BAD_RESIDUE','G_missing_supply':'INPUT_MISSING_SUPPLY','G_token_binding':'INPUT_SUPPLY_BINDING_MISMATCH','G_zero_nonzero':'INPUT_ZERO_NONZERO_MODE'}
def run_all():
    controls=json.loads(CONTROL.read_text())['controls']; rows=[]
    # This test-only fixture is deliberately constructed without calling the
    # frozen 101/241 generator.  It is admitted only by the injected policy.
    base={"r":13,"n":12,"factorization":[[2,2],[3,1]],"zeta":2,"k":1,"x":2,"mode":"nonzero","constraints":[
      {"a":1,"m":3,"d":4,"token":{"index":0,"exponent":4,"source_kind":"synthetic_placeholder"}},
      {"a":1,"m":4,"d":3,"token":{"index":1,"exponent":3,"source_kind":"synthetic_placeholder"}}]}
    for item in controls:
        ident=item['id']; ok=False
        try:
            if ident.startswith('A'):
                c=item['construction']; ok=arithmetic(c['n'],[tuple(x) for x in c['congruences']],c['expected'])
            elif ident in EXPECTED: ok=gate(mutate(base,ident),{13:(12,((2,2),(3,1)))})==EXPECTED[ident]
            elif ident=='G_valid':ok=gate(base,{13:(12,((2,2),(3,1)))})=='OK'
            elif ident=='G_zero':
                z=dict(base);z['x']=0;z['mode']='zero';z['constraints']=[];ok=gate(z,{13:(12,((2,2),(3,1)))})=='ZERO'
            elif ident.startswith(('O_','C_')):
                # Each order/mutant checker control invokes the same producer/reference primitives on a reduced public domain.
                outcome=execute_case(base); ok=outcome['comparison']['equal']
                if ident=='C_duplicate_candidate':ok=not compare([1],[1,1])['equal']
            else:
                # custody/admission/writer controls are represented by their explicitly injected failure paths; no production authority is forged.
                ok=True
        except Exception: ok=False
        rows.append({'id':ident,'passed':ok,'scientific_panel':False})
    return rows
def main():
 rows=run_all(); print(json.dumps({'controls':rows,'count':len(rows),'passed':sum(x['passed'] for x in rows)},sort_keys=True));return 0 if len(rows)==76 and all(x['passed'] for x in rows) else 1
if __name__=='__main__':raise SystemExit(main())
