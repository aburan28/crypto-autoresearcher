"""Frozen follow-up of the newly discovered single-prime resource-cap fit."""
import hashlib,json,pathlib
D=pathlib.Path(__file__).resolve().parent;P=D.parent
cfg=json.loads((D/'inputs.json').read_text())
for name,h in cfg['parent_files'].items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==h
rows=json.loads((P/'prior-rows.json').read_text());a=json.loads((P/'matrix.json').read_text());b=json.loads((P/'eigen.json').read_text());assert a['cells']==b['cells']
def gate(c,d):return c<=32 and d<=2048
assert gate(32,2048) and not gate(33,2048) and not gate(32,2049)
out=[]
for arm in ['at199_known','all_le199_known','at199_unknown']:
 rr=[]
 for i,r in enumerate(rows):
  cc=[c for c in a['cells'] if c['index']==i and (c['ell']==199 if arm.startswith('at199') else c['ell']<=199)];fail=[]
  for c in cc:
   candidates=c['cost'][5 if arm.endswith('unknown') else 1];degree=min(d for d,n in c['factor_degrees'])
   if not gate(candidates,degree):fail.append({'ell':c['ell'],'kind':c['kind'],'candidate_count':candidates,'min_factor_degree':degree})
  rr.append({'index':i,'name':r['name'],'label':r['label'],'accepted':not fail,'failed_cells':fail})
 p=sum(r['accepted'] and r['label']=='published' for r in rr);o=sum(r['accepted'] and r['label']=='omitted' for r in rr);out.append({'arm':arm,'published_retained':p,'omitted_retained':o,'rows':rr})
cp=json.loads((D/'counter-observations.json').read_text());visits=[{'name':r['name'],'profile':r['profile'],'status':r['status'],'max_auxiliary_prime':r['max_auxiliary_prime'],'reached199':r['max_auxiliary_prime']>=199,'log_directory':r['log_directory']} for r in cp['results']]
res={'status':'PASS','controls':'PASS','policy_arms':out,'counter_observations':visits,'source_limits':['Caps32/2048 were selected after inspecting the first exact-fit result; no source claims those values.','Known-degree and unknown-degree modes are both source-supported; original1997 mode is unknown.','Uniform policy applies all recorded primes through199, independent of actual visitation.','Later-counter maximum auxiliary primes are source observations, not original1997 run logs.'],'historical_criterion_identified':False};(D/'RESULT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print([(x['arm'],x['published_retained'],x['omitted_retained']) for x in out]);print('later verified y_direct reached199',sum(r['reached199'] for r in visits if r['profile']=='y_direct' and r['status']=='verified_order'),'of',sum(r['profile']=='y_direct' and r['status']=='verified_order' for r in visits))
