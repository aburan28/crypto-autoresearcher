"""Immutable root gate for real C3/M3 source aliases; read-only Git only."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,required=True);p.add_argument('--inventory',type=Path,required=True);p.add_argument('--preserved-hashes',type=Path,required=True);a=p.parse_args();repo=a.repo.resolve();d=json.loads(a.inventory.read_text());control=json.loads(a.preserved_hashes.read_text());calls=[]
 def need(ok,msg):
  if not ok:raise ValueError(msg)
 def sha(data):return hashlib.sha256(data).hexdigest()
 def git(*args):
  calls.append(['git',*args]);return subprocess.check_output(['git',*args],cwd=repo,stderr=subprocess.PIPE)
 def safe(path):
  need(isinstance(path,str) and not Path(path).is_absolute() and '..' not in Path(path).parts,'Unsafe source alias path');x=(repo/path).resolve();need(x.is_relative_to(repo),'Escaping source alias');return x
 need(d.get('schema')=='classical.ecdlp.controlled-followup.export-source-inventory/v1','Wrong export inventory schema')
 commits={k:d.get(k) for k in ['code_commit','manifest_metadata_commit']}
 for role,c in commits.items():
  need(isinstance(c,str) and re.fullmatch('[0-9a-f]{40}',c),'Actual full C3/M3 commit required')
  git('cat-file','-e',c+'^{commit}');git('merge-base','--is-ancestor',c,'HEAD');need(git('for-each-ref','--contains='+c,'--format=%(refname)','refs/remotes/origin/').strip(),'C3/M3 must actually be pushed')
 git('merge-base','--is-ancestor',commits['code_commit'],commits['manifest_metadata_commit'])
 aliases=d.get('aliases');expected=control['mutable_aliases'];need(isinstance(aliases,list) and len(aliases)==len(expected)==4,'Exactly four authorized source/manifest aliases required')
 seen=set()
 for e in aliases:
  real,mirror,role=e.get('path'),e.get('mirror'),e.get('commit_role');need(real in expected and expected[real]==mirror and real not in seen,'Unknown/duplicate alias');seen.add(real)
  wanted='manifest_metadata_commit' if real.endswith('-source-manifest.json') else 'code_commit';need(role==wanted,'Incorrect actual source commit role')
  blob=git('show',commits[role]+':'+real);need(sha(blob)==e.get('sha256') and blob==safe(real).read_bytes()==safe(mirror).read_bytes(),'Actual commit/live/mirror bytes differ: '+real)
  if wanted=='manifest_metadata_commit':
   m=json.loads(blob);need(m.get('source_revision')==commits['code_commit'],'Manifest does not bind actual C3')
   for path,h in m['files'].items():
    need(not path.endswith('-source-manifest.json'),'Circular manifest source binding')
    data=git('show',commits['code_commit']+':'+path);need(sha(data)==h and data==safe(path).read_bytes(),'Manifest file differs from actual C3/live input: '+path)
 need(seen==set(expected),'Missing source aliases');frozen=control['preserved_source_sha256'];need(d.get('preserved_source_sha256')==frozen,'Incomplete independent preserved-source map')
 for path,h in frozen.items():need(sha(safe(path).read_bytes())==h==sha(git('show',commits['code_commit']+':'+path)),'Preserved C2 math/lifecycle/parser/interface/schema source changed: '+path)
 print(json.dumps({'status':'checked','code_commit':commits['code_commit'],'manifest_metadata_commit':commits['manifest_metadata_commit'],'alias_count':len(aliases),'preserved_count':len(frozen),'read_only_git_calls':calls,'scientific_approval':False},sort_keys=True,indent=2))
if __name__=='__main__':main()
