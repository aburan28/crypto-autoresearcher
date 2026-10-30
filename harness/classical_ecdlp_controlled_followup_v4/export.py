#!/usr/bin/env python3
"""Typed two-real-process export; analytical reference remains linked data."""
from pathlib import Path
import argparse,copy,json,os,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d

def ep_module(contracts):
 sys.path.insert(0,str(Path(contracts)/'tools'));return d.module(Path(contracts)/'tools/experiment_protocol.py','v4_experiment_protocol')
def entry(p,base,kind='raw'):
 p=Path(p);return {'path':os.path.relpath(p,base),'sha256':d.sha_file(p),'bytes':p.stat().st_size,'kind':kind}
def fixture_protocol(contracts):
 ep=ep_module(contracts);p=d.read(HERE/'fixtures.json')['protocol_template'];p=copy.deepcopy(p)
 p['protocol_id']='EXP-FIXTURE-29dff8';p['question']='Fixed disclosed unit fixture for two real local subprocess arms, not scientific admission.'
 first=p['arms'][0];p['arms']=[]
 for name,role in [('candidate','candidate'),('baseline','baseline')]:
  arm=copy.deepcopy(first);arm.update(id=name,role=role,description='One actual local '+name+' subprocess over the same disclosed public bundle.',parameters={'fixture_only':True});arm['instrument'].update(repo='unpublished-outside-v4-source',commit=None,binary_sha256=None,build=[],env={},flags={'fixture_only':'true'});p['arms'].append(arm)
 p['variable_ledger']['comparisons']=[{'id':'typed-contract','arms':['candidate','baseline'],'design':'absolute','differs_in':[],'threshold':'Real distinct processes and exact byte/source identity; no performance inference.'}]
 p['randomization']['arm_order_reason']='Fixed candidate then baseline for actual post-termination source/data custody; no timing inference.'
 p['metrics']={'primary':[{'id':'physical_invocations','name':'Actual local child invocations','unit':'calls','kind':'counted','definition':'One actual local Popen plus wait per physical arm.','source':'process.json','aggregation':'per_row','uncertainty':'none_exact'}],'secondary':[]}
 p['analysis_plan']['script']={'path':str(HERE/'export.py'),'sha256':d.sha((HERE/'export.py').read_bytes())};p['extensions']={'fixture_only':True,'controlled_followup_v4':{'physical_instance':'shared-public-bundle','physical_arms':['candidate','baseline'],'analytical_reference_is_arm':False,'source_publication_commit':None}}
 p['freeze']={'status':'frozen','protocol_sha256':None,'commit':None,'frozen_at':d.now(),'filed_before_affected_data':True};p['freeze']['protocol_sha256']=ep.protocol_hash(p);return p

def make(protocol_path,out,contracts,destination):
 ep=ep_module(contracts);p=d.read(protocol_path);out=Path(out);dest=Path(destination);dest.mkdir(parents=True,exist_ok=False)
 b=ep.export_skeleton(p,os.path.relpath(protocol_path,dest),'local',p['protocol_id']+'.local-v4');records=[d.read(out/a/'process.json') for a in ('candidate','baseline')];pubs={r['source_publication_commit'] for r in records};d.need(len(pubs)==1,'source publication identities differ');pub=pubs.pop();b['source']={'repo':p['repository'],'commit':pub,'dirty':None}
 for a in b['arms']:a['commit']=pub
 paths={q.resolve() for q in out.rglob('*') if q.is_file()}
 for r in records:
  ip=Path(r['input']['path']);paths.add(ip)
  paths.update(ip.parent.glob('generation*.json'))
 files=[entry(q,dest,'receipt' if q.name.endswith(('.json','.yaml')) else 'raw') for q in sorted(paths)];rows=[]
 for a,r in zip(('candidate','baseline'),records):
  rows.append(ep.run_row(run_id=r['run_id'],arm=a,instance_id='shared-public-bundle',replicate=0,seed='fixed00_no_entropy' if records[0]['fixture_only'] else None,status='succeeded' if r['operational_complete'] else 'infra_error',measurements={'counted':{'physical_invocations':1},'counters':{},'wall_valid':False},verification={'status':'no_claim' if r['operational_complete'] else 'error','verifier':'Separate local process registry and pinned independent host checks; no attack claim.'},exclusion={'excluded':False,'rule':None},artifacts=[f for f in files if '/'+a+'/' in f['path']],worker=str(r['pid']),backend_ref=a+'/'+str(r['pid'])))
 b['runs']=rows;b['flow']=ep.compute_flow(rows);b['files']=files;b['analysis']={'script':entry(HERE/'export.py',dest,'analysis'),'outputs':[entry(out/'baseline/result/analytical-reference.json',dest,'analysis')] if (out/'baseline/result/analytical-reference.json').is_file() else [],'blinded':False,'blinding_key_sha256':None,'unmasked_at':None};b['host']['path']=os.path.relpath(out/'registry.json',dest);b['host']['sha256']=d.sha((out/'registry.json').read_bytes());b['backend_record']={'registry':d.read(out/'registry.json'),'source_publication_commit':pub,'launch_context_commit':records[0]['launch_context_commit'],'native_matched_cost_qualified':False,'historical_records_unchanged':True};b['notes']=[{'kind':'observation','by':'v4-local-adapter','text':'Two actual local child processes, one shared input bundle. Candidate methods/six cells and analytic reference are linked artifacts, never cloned runs. BSGS solve phase precedes separately labeled streaming diagnostic oracle checks. No matched primitive/fullcost/RSS/clock/performance qualification.'}]
 d.write(dest/'export.json',b);findings=ep.schema_errors(b,'experiment.export/v1')+ep.lint_export(b,p,dest,True);d.write(dest/'export.validation.json',{'findings':findings,'schema_compliant':not ep.schema_errors(b,'experiment.export/v1'),'fixture_only':records[0]['fixture_only']});return b,findings
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('--protocol',required=True);q.add_argument('--out',required=True);q.add_argument('--contracts-root',required=True);q.add_argument('--destination',required=True);a=q.parse_args();b,f=make(a.protocol,a.out,a.contracts_root,a.destination);print(json.dumps({'findings':f}));raise SystemExit(bool(f))
