"""Import already recorded identities/discriminants; does not evaluate witnesses."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
rows=R/'research/nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/prior-rows.json'
census=R/'research/nist_seed_exact_conductor_census_20261023/runs/census-20261023T1733Z/results.json'
assert sha(rows)=='e8d6a874e3dc77970c88957f4bca075a0cc7a431dd8bcb25e5c5d7bcba6eeb0f'
c={x['curve_uid']:x for x in json.loads(census.read_text()) if x['curve_uid']}
out=[]
for r in json.loads(rows.read_text()):
    r=dict(r);v=c.get(r['curve_uid']);r['cm_record']=None if v is None else v['value']
    if v:assert v['receipt']['status']=='completed' and v['receipt']['exit_code']==0
    out.append(r)
assert len(out)==21 and len({r['curve_uid'] for r in out})==21
write(P/'INPUTS.json',{'sources':{str(p.relative_to(R)):sha(p) for p in (rows,census)},'rows':out})
gp=[]
for i,r in enumerate(out):
    v=r['cm_record'];factors='[]' if v is None else '['+','.join('['+str(q)+','+str(e)+']' for q,e in v['factors'])+']'
    gp.append('['+','.join(map(str,[i,r['p'],r['n'],v['D_K'] if v else 0,v['f_pi'] if v else 0,v['delta'] if v else 0]))+','+factors+']')
(P/'inputs.gp').write_text('rows=['+','.join(gp)+'];\n')
print('Imported 21 frozen identities and existing discriminant records; no witness evaluation.')
