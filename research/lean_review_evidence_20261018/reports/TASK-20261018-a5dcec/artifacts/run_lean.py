import json,os,pathlib,subprocess,sys,time
ART=pathlib.Path(__file__).resolve().parent
FROZEN=pathlib.Path('/workspace/lean-review-inputs/crypto-autoresearcher/formal')
CACHE=pathlib.Path('/workspace/crypto-autoresearcher/formal')
BUILD=ART/'build'
env=os.environ.copy();env.update(PATH='/workspace/.elan/bin:'+env['PATH'],ELAN_HOME='/workspace/.elan',XDG_CACHE_HOME='/workspace/.cache',ELAN_TOOLCHAIN='leanprover/lean4:v4.35.0-rc1')
env['LEAN_PATH']=':'.join([str(BUILD),str(CACHE/'.lake/build/lib/lean')]+[str(p/'.lake/build/lib/lean') for p in (CACHE/'.lake/packages').iterdir() if p.is_dir()])
results=[]
if sys.argv[1:] == ['producer']:
 jobs=[(FROZEN/'CryptoResearch'/(p+'.lean'),BUILD/'CryptoResearch'/(p+'.olean')) for p in ['Semaev/Certificate','NCP/AffineNormalForm','NCP/CommutatorIdeal']]
else:
 jobs=[(pathlib.Path(p).resolve(),None) for p in sys.argv[1:]]
for source,output in jobs:
 cmd=['lean']
 if output:
  output.parent.mkdir(parents=True,exist_ok=True);cmd+=['-o',str(output)]
 cmd+=[str(source)]
 cwd=FROZEN if output else ART
 started=time.time();p=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True)
 stem=source.stem+('-fresh' if output else '')
 index=1
 while (ART/(stem+f'-attempt-{index:02d}.log')).exists(): index+=1
 stem+=f'-attempt-{index:02d}'
 (ART/(stem+'.log')).write_text(p.stdout+p.stderr)
 r=dict(command=cmd,cwd=str(cwd),exit_code=p.returncode,elapsed_seconds=time.time()-started,log=stem+'.log')
 results.append(r);print(json.dumps(r));print(p.stdout+p.stderr)
(ART/('producer-rebuild.json' if sys.argv[1:] == ['producer'] else 'last-control-run.json')).write_text(json.dumps(results,indent=2)+'\n')
