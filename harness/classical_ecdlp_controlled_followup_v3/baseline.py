#!/usr/bin/env python3
"""Separate local process, unchanged host BSGS and independent trace checks."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d

def local_seal(candidate,host):
 candidate=Path(candidate);p=d.read(candidate/'process.json');s=d.read(candidate/'seal.json');d.need(p['arm']=='candidate' and p['returncode']==0 and p['termination_ack']=={'wait_returned':True,'returncode':0},'candidate not terminated successfully');d.need(s['process_sha256']==d.sha((candidate/'process.json').read_bytes()) and s['tree_sha256']==d.sha(d.canonical(s['files'])),'local seal contradiction')
 root=candidate/'result';actual={q.relative_to(root).as_posix() for q in root.rglob('*') if q.is_file()};d.need(actual=={q['path'] for q in s['files']} and len(actual)==len(s['files']),'seal file closure');files={}
 for q in s['files']:
  path=root/q['path'];d.need(not path.is_symlink() and '..' not in Path(q['path']).parts and path.stat().st_size==q['bytes'] and d.sha(path.read_bytes())==q['sha256'],'local member mismatch');files[path.name]=path
 d.need(set(files)==set(host.FILES),'exact seven old raw files required')
 # This capability is constructed only after actual local wait and complete
 # byte validation. No VM UID/quiescence fields are manufactured.
 return host.SealedInput(files,s['tree_sha256'],{'local_seal':s,'scope':'local process termination, no VM/UID claim'})
def run(repo,input_path,out,candidate):
 root=d.verify_dependencies(repo);sys.path.insert(0,str(root/'host'));host=d.module(root/'host/verify.py','verify');ref=d.module(root/'host/reference.py','reference');seal=local_seal(candidate,host);x=d.read(input_path);d.input_check(x,x['fixture_only']);d.need(d.sha(Path(input_path).read_bytes())==d.read(Path(candidate)/'process.json')['input']['sha256'],'same actual public input required');out=Path(out);out.mkdir(parents=True,exist_ok=False);rows=[];checked=0;diagnostics=[]
 traces={c['curve_id']:[] for c in x['public']['curves']}
 for line in seal.files['traces.jsonl'].read_bytes().splitlines():
  trace=d.loads(line);traces[trace['curve_id']].append(trace)
 cells={}
 for line in seal.files['decoder-cells.jsonl'].read_bytes().splitlines():
  cell=d.loads(line);cells.setdefault(cell['trace_id'],[]).append(cell)
 analytical=[]
 for c in x['public']['curves']:
  oracle=host.Oracle(seal,c['model'],c['base'])
  for trace in traces[c['curve_id']]:
   host.check_engine_trace(oracle,host.ARMS['circuit2.a1'],trace)
   d.need(len(cells[trace['trace_id']])==6,'six cells required')
   for cell in cells[trace['trace_id']]:
    bits=[q['answer']['bit'] for q in trace['incremental']['predicate_trace']];host.check_engine_cell(oracle,trace,bits,cell);checked+=1;analytical.append({'cell_id':cell['cell_id'],'M':cell['M'],'fraction':[min(cell['M'],c['model']['r']-1),c['model']['r']-1],'physical_invocations':0})
  diagnostics.append({'curve_id':c['curve_id'],'phase':'diagnostic_independent_oracle_trace_cell_verification','counts':dict(oracle.group.counts),'paid_but_excluded_from_bsgs_solver_vectors':True})
  # Separate BSGS group excludes oracle's full-orbit counters, but both are paid
  # baseline-process work and no matched primitive/fullcost claim is made.
  group=host.Group(c['model']);bsgs=ref.BSGS(seal,group,tuple(c['base']))
  for target in c['targets']:
   answer=bsgs.solve(tuple(target['point']));rows.append({'curve_id':c['curve_id'],'target_id':target['target_id'],'point':target['point'],'answer':answer,'public_equation_verified':answer['status']=='success' and group.mul(answer['scalar'],tuple(c['base']))==tuple(target['point'])})
 d.write(out/'bsgs.json',{'rows':rows,'independent_decoder_cells_checked':checked,'baseline_process_includes_independent_oracle_work':True,'diagnostic_verification':diagnostics,'bsgs_solver_input_scope':'Only public E/G/Q/r; independent oracle/logs and candidate recoveries never passed to BSGS','primitive_units_matched':False,'wall_valid':False});d.write(out/'analytical-reference.json',{'kind':'analytical_summary_not_physical_arm','rows':analytical});return {'status':'complete','targets':len(rows),'decoder_cells_checked':checked,'wall_valid':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();print(json.dumps(run(a.repo_root,a.input,a.out,a.candidate),sort_keys=True))
