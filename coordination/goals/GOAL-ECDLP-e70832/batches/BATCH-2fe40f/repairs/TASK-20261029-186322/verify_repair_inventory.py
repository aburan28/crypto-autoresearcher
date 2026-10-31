"""Root snapshot gate: compare real published C2/metadata bytes to source mirrors.

Read-only Git only. Inventory schema is documented by --help description and
the required keys below. This cannot approve, archive, claim or launch a run.
"""
import argparse,hashlib,json,re,subprocess
from pathlib import Path

SHA=re.compile(r'[0-9a-f]{64}\Z');COMMIT=re.compile(r'[0-9a-f]{40}\Z')
def need(x,msg):
 if not x:raise ValueError(msg)
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--repo',type=Path,required=True);p.add_argument('--inventory',type=Path,required=True)
 p.add_argument('--preserved-hashes',type=Path,required=True)
 a=p.parse_args();repo=a.repo.resolve();inventory=json.loads(a.inventory.read_text());calls=[]
 def git(*args):
  calls.append(['git',*args]);return subprocess.check_output(['git',*args],cwd=repo,stderr=subprocess.PIPE)
 def safe(path):
  need(isinstance(path,str) and not Path(path).is_absolute() and '..' not in Path(path).parts,'Unsafe relative path')
  q=(repo/path).resolve();need(q.is_relative_to(repo),'Path escapes repo');return q
 need(inventory.get('schema')=='classical.ecdlp.controlled-followup.repair-source-inventory/v1','Inventory schema mismatch')
 commits={k:inventory.get(k) for k in ['code_commit','manifest_metadata_commit']}
 for k,c in commits.items():
  need(isinstance(c,str) and COMMIT.fullmatch(c),f'Actual full {k} required')
  git('cat-file','-e',c+'^{commit}');git('merge-base','--is-ancestor',c,'HEAD')
  need(git('for-each-ref',f'--contains={c}','--format=%(refname)','refs/remotes/origin/').strip(),f'{k} not visible in origin refs')
 git('merge-base','--is-ancestor',commits['code_commit'],commits['manifest_metadata_commit'])
 prefix='harness/classical_ecdlp_controlled_followup'
 allowed={prefix+'/'+n for n in ['controller.py','driver.py','host/verify.py','postrun/run_postrun.py','postrun/analysis.py','postrun/render_report.py','test_transport.py','host/test_verify.py','postrun/test_postrun.py','worker-source-manifest.json','host-source-manifest.json']}
 expected_preserved=json.loads(a.preserved_hashes.read_text())['unchanged_candidate_and_interface_sha256']
 entries=inventory.get('aliases');need(isinstance(entries,list) and len(entries)==11,'Exactly eleven real code/test/manifest aliases required')
 paths=set();mirrors=set();observed=[]
 for e in entries:
  real,mirror,role,expected=e.get('path'),e.get('mirror'),e.get('commit_role'),e.get('sha256')
  need(role in commits and isinstance(expected,str) and SHA.fullmatch(expected),'Actual commit role/hash missing')
  need(real in allowed and mirror=='coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-2fe40f/repairs/TASK-20261029-186322/source/'+real,'Alias outside authorized actual/mirror map')
  need(role==('manifest_metadata_commit' if real.endswith('-source-manifest.json') else 'code_commit'),'Source alias uses wrong real commit role')
  need(real not in paths and mirror not in mirrors,'Duplicate real/mirror alias');paths.add(real);mirrors.add(mirror)
  commit=commits[role];blob=git('show',f'{commit}:{real}');actual=safe(real).read_bytes();copy=safe(mirror).read_bytes()
  need(digest(blob)==expected and blob==actual==copy,f'Real commit/live/mirror bytes differ: {real}')
  if real.endswith('-source-manifest.json'):
   need(role=='manifest_metadata_commit','Manifests must bind actual metadata commit')
   manifest=json.loads(blob);need(manifest.get('source_revision')==commits['code_commit'],'Manifest revision differs from actual C2')
   files=manifest.get('files');need(isinstance(files,dict) and files,'Manifest map absent')
   for source,h in files.items():
    need(not source.endswith('-source-manifest.json'),'Manifest may not hash itself/another source manifest')
    pinned=git('show',f'{commits["code_commit"]}:{source}')
    need(digest(pinned)==h and pinned==safe(source).read_bytes(),f'Manifest source differs: {source}')
  observed.append({'path':real,'mirror':mirror,'commit':commit,'sha256':expected,'checked':True})
 need(paths==allowed,'Incomplete authorized alias map')
 frozen=inventory.get('preserved_source_sha256');need(frozen==expected_preserved,'Preserved hashes must equal complete independent amendment map')
 for source,h in frozen.items():
  need(isinstance(h,str) and SHA.fullmatch(h),'Preserved hash invalid')
  need(digest(safe(source).read_bytes())==h and digest(git('show',f'{commits["code_commit"]}:{source}'))==h,f'Preserved source changed: {source}')
 print(json.dumps({'status':'checked','aliases':observed,'preserved_source_sha256':frozen,'read_only_git_calls':calls,'scientific_approval':False},sort_keys=True,indent=2))
if __name__=='__main__':main()
