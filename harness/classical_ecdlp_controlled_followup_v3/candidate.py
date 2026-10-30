#!/usr/bin/env python3
"""Truth-free adapter around unchanged paired_attempt; explicit public schedule."""
from pathlib import Path
import argparse,sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d

def run(repo,input_path,out):
 root=d.verify_dependencies(repo);sys.path.insert(0,str(root));import engine
 from curve import Curve,point_from_json,point_json
 from constructor import prepare
 x=d.read(input_path);d.input_check(x,x['fixture_only']);out=Path(out);out.mkdir(parents=True,exist_ok=False);raw=out/'raw';raw.mkdir()
 paths={'setups':'setups.jsonl','singles':'single-points.jsonl','intents':'attempt-intents.jsonl','traces':'traces.jsonl','cells':'decoder-cells.jsonl'};handles={k:(raw/n).open('xb') for k,n in paths.items()};counts={k:0 for k in paths}
 def emit(k,row):handles[k].write(d.canonical(row));counts[k]+=1
 try:
  arm=next(a for a in engine.arm_specs() if a['id']=='circuit2.a1')
  for c in x['public']['curves']:
   cid=c['curve_id'];m=c['model'];G=point_from_json(c['base']);group=Curve(m['p'],m['a'],m['b']);prepared=prepare(m,G,arm)
   emit('setups',engine.record('setup',curve_id=cid,arm_id=arm['id'],model=m,base=c['base'],prepared_base=point_json(G),arm=arm,setup_reason=prepared.setup_reason,counts={'common':group.counter.snapshot(),'setup':prepared.setup_counts}))
   for t in c['targets']:
    Q=point_from_json(t['point']);answer,vector=prepared.evaluate(Q);emit('singles',engine.record('single-point',single_id=cid+'/'+t['target_id'],curve_id=cid,arm_id=arm['id'],point=t['point'],sampling=None,answer=answer,counts=vector))
    for i,b in enumerate(x['blindings'][cid]):
     ident=cid+'/'+t['target_id']+'/rep'+str(i);shared={'trace_id':ident,'curve_id':cid,'target_id':t['target_id'],'arm_id':arm['id'],'target':t['point'],'base_multiplier':1,'target_multiplier':b,'draw':{'explicit_fixed_multiplier':b,'entropy_draws':0}}
     emit('intents',engine.record('intent',**shared));pair=engine.paired_attempt(prepared,G,Q,1,b);emit('traces',engine.record('trace',**shared,original=pair['original'],incremental=pair['incremental'],equal=pair['equal']))
     for cell in pair['cells']:emit('cells',engine.record('decoder-cell',cell_id=ident+f"/t{cell['radius']}.e{cell['erasure_cap']}",trace_id=ident,**cell))
 finally:
  for f in handles.values():f.close()
 summary=engine.record('summary',status='complete',observed=counts,errors=[],wall_valid=False,input_sha256=d.sha(Path(input_path).read_bytes()));d.write(raw/'engine-summary.json',summary)
 files={n:{'sha256':d.sha((raw/n).read_bytes()),'bytes':(raw/n).stat().st_size,'records':counts[k]} for k,n in paths.items()};files['engine-summary.json']={'sha256':d.sha((raw/'engine-summary.json').read_bytes()),'bytes':(raw/'engine-summary.json').stat().st_size,'records':1};d.write(raw/'engine-completion.json',engine.record('completion',status='complete',files=files,wall_valid=False,termination_ack=False));return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--input',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(run(a.repo_root,a.input,a.out),sort_keys=True))
