from pathlib import Path
import sys,os,importlib.util,json,hashlib,shutil,time
R=Path('/workspace/review-lean-evidence');F=Path('/workspace/lean-review-inputs/crypto-autoresearcher/orchestration/formal/cli.py');S=Path('/tmp/j3-lean-review/frozen-cli');A=Path(__file__).resolve().parent
os.environ.update(PATH='/workspace/.elan/bin:'+os.environ['PATH'],ELAN_HOME='/workspace/.elan',XDG_CACHE_HOME='/workspace/.cache',PYTHONDONTWRITEBYTECODE='1');sys.path.insert(0,str(R))
module=importlib.util.spec_from_file_location('orchestration.formal.cli',F);cli=importlib.util.module_from_spec(module);sys.modules['orchestration.formal.cli']=cli;module.loader.exec_module(cli)
shutil.copytree('/tmp/j3-lean-review/cli',S,ignore=shutil.ignore_patterns('.lake'),dirs_exist_ok=True)
helper=S/'formal/CryptoResearch/Helper.lean';target=S/'formal/CryptoResearch/Test.lean';target.write_text('import CryptoResearch.Helper\nnamespace Control\ntheorem good : P := by trivial\nend Control\n');helper.write_text('namespace Control\ndef P : Prop := False\nend Control\n');rows=[]
for name,mutation in [('frozen-cli-loadbearing-before',False),('frozen-cli-stale-loadbearing-import',True)]:
 real=cli.subprocess.run
 def wrapped(cmd,*args,**kwargs):
  result=real(cmd,*args,**kwargs)
  if mutation and list(cmd)==['lake','env','lean','--version']:helper.write_text('namespace Control\ndef P : Prop := True\nend Control\n')
  return result
 cli.subprocess.run=wrapped
 try:code=cli.main(['--repo-root',str(S),'verify','--task-file',str(S/'spec.yaml'),'--artifact-out',str(A/(name+'.json')),'--build-timeout','120'])
 finally:cli.subprocess.run=real
 rows.append({'name':name,'exit_code':code});print(name,code,flush=True)
(A/'frozen-cli-confirmation.json').write_text(json.dumps({'loaded_cli_source':str(F),'loaded_cli_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'expected_sha256':'71a42bd8fd9325f1a38881cd672ad55d0aeff4b356bb796cc67a590fc133c964','controls':rows},indent=2)+'\n')
