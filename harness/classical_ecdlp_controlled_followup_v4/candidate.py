#!/usr/bin/env python3
"""Unmodified full run_public engine; no host/reference imports."""
from pathlib import Path
import argparse,json,sys,signal,time
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d
def run(repo,input_path,out,fixture_fault=None):
 root=d.dependencies(repo);x=d.input_check(d.read(input_path));out=Path(out);out.mkdir(parents=True,exist_ok=False)
 if fixture_fault:
  d.need(x['fixture_only'],'unit fault denied in production')
  d.write(out/'partial-marker.json',{'fixture_only':True,'fault':fixture_fault,'started_at':d.now()})
  if fixture_fault=='nonzero':raise RuntimeError('disclosed fixed unit child failure')
  if fixture_fault=='flood':
   while True:sys.stdout.write('X'*65536);sys.stdout.flush()
  if fixture_fault=='ignore-term':signal.signal(signal.SIGTERM,signal.SIG_IGN)
  d.need(fixture_fault in ('hang','ignore-term'),'unknown unit fault')
  print('Disclosed fixed unit child waiting for watchdog',flush=True);time.sleep(60)
 d.need(x['generation_status']=='complete','incomplete generation retained; no false candidate completion')
 sys.path.insert(0,str(root));import engine
 result=engine.run_public(x['plan'],x['public'],out/'raw',x['provenance'])
 return {'status':result['status'],'source':'unchanged engine.run_public','wall_valid':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--fixture-fault');a=p.parse_args();r=run(a.repo_root,a.input,a.out,a.fixture_fault);print(json.dumps(r));raise SystemExit(0 if r['status']=='complete' else 1)

