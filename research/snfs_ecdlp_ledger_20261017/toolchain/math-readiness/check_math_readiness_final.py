from pathlib import Path
import os,subprocess,json,datetime
root=Path('/workspace/snfs-toolchains');env=os.environ.copy()
env.update(PIXI_HOME=str(root/'pixi-home'),PIXI_CACHE_DIR=str(root/'pixi-cache'),XDG_CACHE_HOME=str(root/'cache'),XDG_CONFIG_HOME=str(root/'config'),DOT_SAGE=str(root/'sage-state'),MPLCONFIGDIR=str(root/'matplotlib'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
env['PATH']=str(root/'msolve/bin')+os.pathsep+env['PATH']
base=[str(root/'bin/pixi'),'run','--manifest-path',str(root/'sage-pixi/pixi.toml')]
cmds={'cryptominisat_version':['cryptominisat5','--version'],'msolve_help':[str(root/'msolve/bin/msolve'),'-h'],'sage_version':['sage','--version'],'sage_python_import':['python','-c','import sage.all; import sage.version; print("Sage import:", sage.version.version)'],'pari_version':['gp','--version'],'optional_solver_paths':['python','-c','import shutil,json; print(json.dumps({n:shutil.which(n) for n in ("Singular","fplll","mwrank","cryptominisat5","msolve")}))']}
checks={}
for name,argv in cmds.items():
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(base+argv,env=env,text=True,capture_output=True,timeout=120)
 checks[name]={'argv':base+argv,'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 print(name,p.returncode,p.stdout.strip(),p.stderr.strip())
out={'scope':'Software installation/version/import readiness only; no scientific trials, rank certificates or protocol approval','checks':checks,'all_commands_returned_zero':all(p['returncode']==0 for p in checks.values()),'prior_failed_health_check':'sage-readiness.log retains the unsupported sage -python invocation','environment_paths':{k:env[k] for k in ('PIXI_HOME','PIXI_CACHE_DIR','XDG_CACHE_HOME','XDG_CONFIG_HOME','DOT_SAGE','MPLCONFIGDIR','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')}}
(root/'math-readiness-final.json').write_text(json.dumps(out,indent=2)+'\n')
assert out['all_commands_returned_zero']
