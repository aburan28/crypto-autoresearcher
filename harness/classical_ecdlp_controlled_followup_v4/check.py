#!/usr/bin/env python3
"""Bind typed physical rows to retained actual process/source/workload evidence."""
from pathlib import Path
from itertools import zip_longest
import argparse,base64,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d
def records(path,cap=64<<20):
 with Path(path).open('rb') as f:
  while True:
   b=f.readline(cap+1)
   if not b:break
   d.need(len(b)<=cap and b.endswith(b'\n'),'partial/oversized JSONL row')
   yield d.loads(b)
def check(out,protocol_path,export_path,repo,contracts):
 out=Path(out);p=d.read(protocol_path);b=d.read(export_path);base=Path(export_path).parent
 exp=d.module(d.HERE/'export.py','v4_export_check');ep=exp.ep_module(contracts)
 findings=ep.schema_errors(b,'experiment.export/v1')+ep.lint_export(b,p,base,True);d.need(not findings,'typed export findings: '+str(findings))
 reg=d.read(out/'registry.json');d.need(reg['physical_invocations']==2 and reg['analytical_reference_is_arm'] is False,'actual two physical arms')
 d.need(len(reg['processes'])==2 and {x['arm'] for x in reg['processes']}=={'candidate','baseline'} and len({x['pid'] for x in reg['processes']})==2,'missing or cloned process')
 rows={x['arm']:x for x in b['runs']};d.need(len(b['runs'])==2 and set(rows)=={'candidate','baseline'},'missing/cloned physical rows')
 d.need(p['analysis_plan']['script']['sha256']==d.sha_file(d.HERE/'export.py')==b['analysis']['script']['sha256'],'analysis binding')
 contexts=set();pubs=set();inputs=set();maps=[];allcomplete=True
 for arm in ('candidate','baseline'):
  root=out/arm;pr=d.read(root/'process.json');seal=d.read(root/'seal.json');r=next(x for x in reg['processes'] if x['arm']==arm);row=rows[arm]
  d.need(pr['arm']==arm and type(pr['pid']) is int and pr['pid']>0 and pr['pid']==r['pid'] and pr['run_id']==r['run_id']==row['run_id'] and r['process_sha256']==d.sha_file(root/'process.json'),'arm/process identity')
  d.need(pr['termination_ack']=={'wait_returned':True,'returncode':pr['returncode']},'actual wait missing')
  d.need(pr['source_before']['files']==pr['source_after']['files'],'source mutation')
  for rel,v in pr['source_before']['files'].items():
   raw=base64.b64decode(v['base64'],validate=True);d.need(len(raw)==v['bytes'] and d.sha(raw)==v['sha256'],'source capture contradiction')
   path=d.HERE/rel[len(d.PREFIX):] if rel.startswith(d.PREFIX) else Path(repo)/rel
   d.need(path.read_bytes()==raw,'current/executed source mismatch: '+rel)
   if not pr['fixture_only']:d.need(d.sha(d.git(repo,'show',pr['source_publication_commit']+':'+rel))==v['sha256'],'published source mismatch')
  d.need(pr['interpreter']['sha256']==d.sha_file(Path(pr['interpreter']['path']).resolve()),'interpreter bytes differ')
  maps.append(d.source_map(pr['source_before']))
  d.need(seal['process_sha256']==d.sha_file(root/'process.json') and seal['tree_sha256']==d.sha(d.canonical(seal['files'])) and seal['returncode']==pr['returncode'] and seal['wait_returned'] is True,'local seal contradiction')
  actual={q.relative_to(root/'result').as_posix() for q in (root/'result').rglob('*') if q.is_file()};d.need(actual=={q['path'] for q in seal['files']} and len(actual)==len(seal['files']),'member closure')
  for obj in seal['files']:
   path=d.safe(root/'result',obj['path']);d.need(path.stat().st_size==obj['bytes'] and d.sha_file(path)==obj['sha256'],'member hash')
  for name in ('stdout','stderr'):
   path=root/(name+'.log');d.need(pr[name]=={'bytes':path.stat().st_size,'sha256':d.sha_file(path)},'log identity')
  expected_complete=pr['returncode']==0 and pr['resource_stop'] is None
  d.need(type(pr['operational_complete']) is bool and pr['operational_complete']==expected_complete,'false completion')
  d.need(row['status']==('succeeded' if expected_complete else 'infra_error'),'false typed completion')
  d.need(row['worker']==str(pr['pid']) and row['backend_ref']==arm+'/'+str(pr['pid']) and row['instance_id']==reg['instance_id'],'row/process/instance reuse')
  d.need(row['measurements']['counted']=={'physical_invocations':1},'physical count')
  x=d.input_check(d.read(pr['input']['path']));d.need(x['fixture_only']==pr['fixture_only']==reg['fixture_only'],'fixture identity')
  d.need(d.sha_file(pr['input']['path'])==pr['input']['sha256']==reg['input_sha256'],'input identity')
  d.need(x['provenance']['source_fingerprint']==d.sha(d.canonical(d.source_map(pr['source_before']))) and x['provenance']['protocol_sha256']==p['freeze']['protocol_sha256'],'input/source/protocol binding')
  d.need(next(a for a in p['arms'] if a['id']==arm)['instrument']['commit']==pr['source_publication_commit'],'false instrument source publication')
  if pr['fixture_only']:d.need(pr['source_publication_commit'] is None and pr['native_parent'] is None,'fixture falsely claims production authority')
  else:
   n=pr['native_parent'];d.need(n is not None and n['source_publication_commit']==pr['source_publication_commit'] and n['launch_context_commit']==pr['launch_context_commit'],'native parent identity')
   cfg=d.read(n['config_path']);d.need(d.sha_file(n['config_path'])==n['config_sha256'] and cfg['child_run_ids'][arm]==pr['run_id'],'native config/child identity')
   plan=d.read(Path(repo)/n['plan_path']);d.need(d.sha_file(Path(repo)/n['plan_path'])==n['plan_sha256'] and plan['experiment_id']==n['experiment_id'] and plan['approved_by']==n['approved_by'] and plan['task_id']==n['task_id'],'native frozen plan identity')
  inputs.add(pr['input']['sha256']);contexts.add(pr['launch_context_commit']);pubs.add(pr['source_publication_commit']);allcomplete&=expected_complete
 d.need(len(inputs)==len(contexts)==len(pubs)==1 and maps[0]==maps[1] and b['source']['commit']==next(iter(pubs)),'paired source/input/context mismatch')
 d.dependencies(repo)
 adapter=d.module(d.HERE/'cohort_adapter.py','v4_check_schedule');pr=d.read(out/'candidate/process.json');x=d.input_check(d.read(pr['input']['path']));wanted=adapter.expected_from_jobs(x['public'],x['plan']) if x['generation_status']=='complete' else x['plan']['expected']
 if x['generation_status']!='complete':d.need(not any(d.read(out/a/'process.json')['operational_complete'] for a in ('candidate','baseline')),'incomplete generation cannot become a completed solve')
 if pr['operational_complete']:
  raw=out/'candidate/result/raw';summary=d.read(raw/'engine-summary.json')
  d.need(summary['status']=='complete' and not summary['errors'] and summary['expected']==summary['observed']==wanted and summary['provenance']==x['provenance'],'false complete summary')
  jobgroups={'singles':('single-points.jsonl','single_id',[j for j in x['plan']['jobs'] if j['kind']=='single']),'traces':('traces.jsonl','trace_id',[j for j in x['plan']['jobs'] if j['kind']!='single']),'intents':('attempt-intents.jsonl','trace_id',[j for j in x['plan']['jobs'] if j['kind']!='single'])}
  for kind,(name,key,jobs) in jobgroups.items():
   count=0
   for job,row in zip_longest(jobs,records(raw/name)):
    d.need(job is not None and row is not None and row[key]==job['id'] and row['curve_id']==job['curve_id'] and row['arm_id']==job['arm_id'],'missing/duplicate job row: '+kind);count+=1
   d.need(count==wanted[kind],'observed row count')
  d.need(sum(1 for _ in records(raw/'setups.jsonl'))==wanted['setups'] and sum(1 for _ in records(raw/'decoder-cells.jsonl'))==wanted['cells'],'missing setup/cell rows')
 if d.read(out/'baseline/process.json')['operational_complete']:
  baseline=d.read(out/'baseline/result/bsgs.json');v=d.read(out/'baseline/result/verification.json')
  d.need(v['status']=='complete' and v['observed']==wanted and len(baseline['rows'])==sum(len(c['targets']) for c in x['public']['curves']) and all(r['public_equation_verified'] is True for r in baseline['rows']),'baseline verification incomplete')
 return {'status':'pass','operational_status':'complete' if allcomplete else 'incomplete','physical_processes':2,'fixture_only':x['fixture_only'],'scientific_validity':'not_assessed','performance_qualified':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--protocol');p.add_argument('--export');p.add_argument('--repo-root',required=True);p.add_argument('--contracts-root');a=p.parse_args()
 root=Path(a.out);native=(root/'execution').is_dir()
 if native:
  reg=d.read(root/'execution/registry.json');pr=d.read(root/'execution/candidate/process.json');config=d.read(pr['native_parent']['config_path']);protocol=d.safe(a.repo_root,config['protocol']['path']);export=root/'typed-export/export.json';out=root/'execution'
 else:out=root;protocol=a.protocol;export=a.export
 print(json.dumps(check(out,protocol,export,a.repo_root,a.contracts_root or a.repo_root)));return 0
if __name__=='__main__':raise SystemExit(main())

