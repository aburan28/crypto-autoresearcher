"""Execute committed prospective sources in fresh immutable output directories."""
import datetime, hashlib, json, platform, shutil, subprocess, sys, time
from pathlib import Path

REPO=Path('/workspace/solinas-run');EXP=REPO/'experiments/EXP-ECDLP-5184f7';EXT=EXP/'extensions/nist-fullsize-20261011';RUN=EXP/'runs/RUN-ECDLP-d0e449'
PYTHON='/workspace/solinas-runtime/report-venv/bin/python';KERNEL='/workspace/solinas-runtime/nist-comparison/attack'
RUN.mkdir(exist_ok=False)
shutil.copytree(EXT/'implementation',RUN/'source',ignore=shutil.ignore_patterns('__pycache__'))
for name in ['contract.json','measurement-boundary.json','kernel-origin.json','execute_nist.py']:
    shutil.copyfile(EXT/name,RUN/name)
engineering=RUN/'engineering';engineering.mkdir()
for name in ['instrument-01','instrument-02','instrument-03']:
    shutil.copytree(Path('/workspace/solinas-runtime/nist-comparison')/name,engineering/name)
for name in ['probe_orders.py','check_kernel.py']:
    shutil.copyfile(Path('/workspace/solinas-runtime/nist-comparison')/name,engineering/name)
shutil.copyfile(EXT/'make_kernel.py',engineering/'make_kernel.py')
commands={
 'preparation':[PYTHON,str(RUN/'source/prepare_nist.py'),'--plan',str(RUN/'contract.json'),'--out',str(RUN/'preparation'),'--probe',str(engineering/'instrument-01/results.json')],
 'attacks':[PYTHON,str(RUN/'source/run_attacks_nist.py'),'--prep',str(RUN/'preparation'),'--out',str(RUN/'attacks'),'--kernel',KERNEL],
 'arithmetic':[PYTHON,str(RUN/'source/arithmetic_nist.py'),'--prep',str(RUN/'preparation'),'--out',str(RUN/'arithmetic')],
 'analysis':[PYTHON,str(RUN/'source/analyze_nist.py'),'--run',str(RUN)]}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n')
manifest={'experiment_id':'EXP-ECDLP-5184f7','run_id':RUN.name,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
 'origin_main':subprocess.check_output(['git','rev-parse','origin/main'],cwd=REPO,text=True).strip(),
 'dirty_state':subprocess.check_output(['git','status','--porcelain'],cwd=REPO,text=True).splitlines(),
 'commands':commands,'source_hashes':{p.name:sha(p)for p in sorted((RUN/'source').iterdir())if p.is_file()},
 'kernel_sha256':sha(KERNEL),'contract_sha256':sha(RUN/'contract.json'),'platform':platform.platform(),'python':platform.python_version(),
 'dependency_versions':{'NumPy':__import__('numpy').__version__,'SciPy':__import__('scipy').__version__,'Boost':'1.83.0-4.2 Debian headers','Boost_deb_SHA256':'1f11fc6fb2ffe9378a0f0ebc8f2fd9223fb958b4a40bb9381c67a8857d947ca3'},
 'build_command':['g++','-std=c++20','-O3','-Wno-deprecated-declarations','-I/workspace/solinas-runtime/nist-comparison/boost/usr/include',str(EXT/'implementation/attack.cpp'),'-lcrypto','-o',KERNEL],
 'instrument_checks':json.loads((engineering/'instrument-03/checks.json').read_text()),
 'engineering_failures':[{'event':'initial compile','reason':'Boost header not installed; downloaded/extracted fixed Debian header package before successful build','scientific_trials_started':False},
    {'event':'instrument-02','reason':'guard at 20 subgroup bits rejected earlier toy BSGS instrument jobs at up to 26 bits; broadened kernel instrumentation guard to 26 while prospective scientific subgroup cap remains 20; all failed attempt files preserved','scientific_trials_started':False},
    {'event':'instrument-03','reason':'engineering assertion incorrectly required every tiny rho job to recover before its cap; one order-7 rho32 censored validly. Original attempt retained and corrected checks evaluate existing outputs, without rerunning kernel jobs.','scientific_trials_started':False}],
 'authorization':'User explicitly confirmed P-192/P-224 and requested larger controls, wider samples, higher confidence and PRs',
 'inference':{'requested_policy':'executor-implementation','model':'GPT-6, system identity','model_verified':False,'independent_review':None,'delivery':'interactive'},
 'git_policy':'Own stacked branch; prior Solinas runs and source history not rebased; origin/main inspected without merging unrelated science into raw records',
 'publication_at_start':'GitHub API HTTP401; no ready configured credentials in managed environment'}
write(RUN/'manifest.json',manifest)
phases=[]
for name,cmd in commands.items():
    begin=time.monotonic();print('START',name,flush=True)
    with (RUN/(name+'.stdout')).open('x')as so,(RUN/(name+'.stderr')).open('x')as se:
        result=subprocess.run(cmd,stdout=so,stderr=se,cwd=REPO)
    row={'phase':name,'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-begin,'stdout_sha256':sha(RUN/(name+'.stdout')),'stderr_sha256':sha(RUN/(name+'.stderr'))}
    write(RUN/(name+'-execution.json'),row);phases.append(row);print('FINISH',name,row['exit_code'],round(row['elapsed_seconds'],3),flush=True)
    if result.returncode:
        write(RUN/'execution-failure.json',{'phases':phases,'failure':name});print((RUN/(name+'.stderr')).read_text()[-2500:],flush=True);sys.exit(result.returncode)
write(RUN/'execution-result.json',{'complete':True,'phases':phases,'finished_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print('RUN_COMPLETE',RUN.name,flush=True)
