#!/usr/bin/env python3
"""Independently bind typed rows to local process, input, source and file facts."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d

def check(out,protocol_path,export_path,repo,contracts):
 out=Path(out);p=d.read(protocol_path);b=d.read(export_path);base=Path(export_path).parent;exp=d.module(Path(__file__).with_name('export.py'),'v3_export_check');ep=exp.ep_module(contracts);f=ep.schema_errors(b,'experiment.export/v1')+ep.lint_export(b,p,base,True);d.need(not f,'typed export findings: '+str(f));reg=d.read(out/'registry.json');d.need(reg['physical_invocations']==2 and reg['analytical_reference_is_arm'] is False,'two real arms required');d.need({r['arm'] for r in reg['processes']}=={'candidate','baseline'} and len({r['pid'] for r in reg['processes']})==2,'missing or cloned process')
 rows={r['arm']:r for r in b['runs']};d.need(len(b['runs'])==2 and set(rows)=={'candidate','baseline'},'two actual rows only');d.need(p['analysis_plan']['script']['sha256']==d.sha(Path(__file__).with_name('export.py').read_bytes()) and b['analysis']['script']['sha256']==p['analysis_plan']['script']['sha256'],'analysis source mismatch')
 inputs=set();contexts=set();publications=set()
 for arm in ('candidate','baseline'):
  root=out/arm;pr=d.read(root/'process.json');sr=d.read(root/'seal.json');rr=next(r for r in reg['processes'] if r['arm']==arm);row=rows[arm]
  d.need(pr['arm']==arm and type(pr['pid']) is int and pr['pid']==rr['pid'] and rr['process_sha256']==d.sha((root/'process.json').read_bytes()),'arm/process identity');d.need(pr['termination_ack']=={'wait_returned':True,'returncode':pr['returncode']},'missing termination wait');d.need(pr['source_before']['files']==pr['source_after']['files'],'source mutation');
  for path,v in pr['source_before']['files'].items():
   import base64
   payload=base64.b64decode(v['base64'],validate=True);d.need(len(payload)==v['bytes'] and d.sha(payload)==v['sha256'],'captured source contradiction');d.need(Path(path).read_bytes()==payload,'executed source differs from current pinned fixture source')
  d.need(sr['process_sha256']==d.sha((root/'process.json').read_bytes()) and sr['tree_sha256']==d.sha(d.canonical(sr['files'])),'seal mismatch');actual={q.relative_to(root/'result').as_posix() for q in (root/'result').rglob('*') if q.is_file()};d.need(actual=={r['path'] for r in sr['files']} and len(actual)==len(sr['files']),'missing or duplicate member')
  for obj in sr['files']:
   q=root/'result'/obj['path'];d.need('..' not in Path(obj['path']).parts and not Path(obj['path']).is_absolute() and not q.is_symlink() and q.stat().st_size==obj['bytes'] and d.sha(q.read_bytes())==obj['sha256'],'member hash mismatch')
  for name in ('stdout','stderr'):
   q=(root/(name+'.log')).read_bytes();d.need(pr[name]=={'bytes':len(q),'sha256':d.sha(q)},'process log contradiction')
  d.need(row['instance_id']==reg['instance_id'] and row['backend_ref']==arm+'/'+str(pr['pid']) and row['worker']==str(pr['pid']),'physical row reused or instance mismatch');d.need(row['status']==('succeeded' if pr['returncode']==0 else 'infra_error'),'false completion');d.need(row['measurements']['counted']=={'physical_invocations':1},'invocation count');d.need(d.sha(Path(pr['input']['path']).read_bytes())==pr['input']['sha256']==reg['input_sha256'],'input hash mismatch');inputs.add(pr['input']['sha256']);contexts.add(pr['launch_context_commit']);publications.add(pr['source_publication_commit']);d.need(next(a for a in p['arms'] if a['id']==arm)['instrument']['commit']==pr['source_publication_commit'],'instrument commit falsely identifies execution source')
 d.need(len(inputs)==len(contexts)==len(publications)==1 and b['source']['commit']==next(iter(publications)),'source/public-input identities differ');d.verify_dependencies(repo)
 for arm in ('candidate','baseline'):
  pr=d.read(out/arm/'process.json')
  if pr['returncode']==0:d.need(d.read(out/arm/'result'/('raw/engine-summary.json' if arm=='candidate' else 'bsgs.json')).get('status','complete')=='complete','false complete payload')
 if d.read(out/'candidate/process.json')['returncode']==0:
  x=d.read(d.read(out/'candidate/process.json')['input']['path']);raw=out/'candidate/result/raw';wanted={'setups':len(x['public']['curves']),'singles':sum(len(c['targets']) for c in x['public']['curves']),'traces':sum(len(c['targets'])*len(x['blindings'][c['curve_id']]) for c in x['public']['curves'])};wanted['intents']=wanted['traces'];wanted['cells']=6*wanted['traces']
  for kind,name in {'setups':'setups.jsonl','singles':'single-points.jsonl','traces':'traces.jsonl','intents':'attempt-intents.jsonl','cells':'decoder-cells.jsonl'}.items():
   data=(raw/name).read_bytes();d.need(not data or data.endswith(b'\n'),'partial JSONL row');records=[d.loads(line) for line in data.splitlines()];d.need(len(records)==wanted[kind],'missing scientific rows: '+kind)
  d.need(d.read(raw/'engine-summary.json')['observed']==wanted,'summary coverage contradiction')
 return {'status':'pass','physical_processes':2,'operational_status':'complete' if all(d.read(out/a/'process.json')['returncode']==0 for a in ('candidate','baseline')) else 'incomplete','fixture_only':True,'performance_qualified':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--protocol',required=True);p.add_argument('--export',required=True);p.add_argument('--repo-root',required=True);p.add_argument('--contracts-root',required=True);a=p.parse_args();print(json.dumps(check(a.out,a.protocol,a.export,a.repo_root,a.contracts_root)));raise SystemExit(0)
