#!/usr/bin/env python3
"""Run the committed prospective extension in separate sequential phases."""
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path('/workspace/solinas-run')
EXP = REPO / 'experiments/EXP-ECDLP-5184f7'
EXT = EXP / 'extensions/wide-20261011'
RUN = EXP / 'runs/RUN-ECDLP-07aad1'
RUN.mkdir(exist_ok=False)
shutil.copytree(EXT / 'implementation', RUN / 'source', ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(EXT / 'contract.json', RUN / 'contract.json')
shutil.copyfile(EXT / 'measurement-boundary.json', RUN / 'measurement-boundary.json')
shutil.copyfile(__file__, RUN / 'execute_wide.py')
PYTHON = '/workspace/solinas-runtime/report-venv/bin/python'
KERNEL = '/workspace/solinas-runtime/prime-comparison/attack'
commands = {
 'preparation': [PYTHON, str(RUN/'source/prepare.py'), '--plan', str(RUN/'contract.json'), '--boundary', str(RUN/'measurement-boundary.json'), '--out', str(RUN/'preparation')],
 'attacks': [PYTHON, str(RUN/'source/run_attacks.py'), '--prep', str(RUN/'preparation'), '--kernel', KERNEL, '--out', str(RUN/'attacks')],
 'arithmetic': [PYTHON, str(RUN/'source/arithmetic.py'), '--prep', str(RUN/'preparation'), '--out', str(RUN/'arithmetic')],
 'analysis': [PYTHON, str(RUN/'source/analyze_wide.py'), '--run', str(RUN)]}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest = {'experiment_id':'EXP-ECDLP-5184f7','run_id':RUN.name,
 'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
 'origin_main':subprocess.check_output(['git','rev-parse','origin/main'],cwd=REPO,text=True).strip(),
 'dirty_state':subprocess.check_output(['git','status','--porcelain'],cwd=REPO,text=True).splitlines(),
 'commands':commands,'source_hashes':{p.name:sha(p)for p in sorted((RUN/'source').iterdir())if p.is_file()},
 'kernel_sha256':sha(KERNEL),'contract_sha256':sha(RUN/'contract.json'),
 'authorization':'User: wider sample set, larger control and higher confidence for all prime results',
 'predecessor':'RUN-ECDLP-a24605, all its 126 moduli excluded; no baseline observations pooled',
 'status_at_freeze':'Sources and analysis committed before selection; observed outcomes not prewritten',
 'inference':{'requested_policy':'executor-implementation','model':'GPT-6, system identity','model_verified':False,'independent_review':None},
 'publication_at_freeze':'GitHub API HTTP401; git push cannot authenticate; user is enabling connection'}
with (RUN/'manifest.json').open('x')as f:json.dump(manifest,f,indent=2);f.write('\n')
phases=[]
for phase, command in commands.items():
    start=time.monotonic()
    print('START',phase,flush=True)
    with (RUN/(phase+'.stdout')).open('x')as so,(RUN/(phase+'.stderr')).open('x')as se:
        result=subprocess.run(command,stdout=so,stderr=se,cwd=REPO)
    row={'phase':phase,'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-start,
         'stdout_sha256':sha(RUN/(phase+'.stdout')),'stderr_sha256':sha(RUN/(phase+'.stderr'))}
    with (RUN/(phase+'-execution.json')).open('x')as f:json.dump(row,f,indent=2);f.write('\n')
    phases.append(row)
    print('FINISH',phase,row['exit_code'],round(row['elapsed_seconds'],3),flush=True)
    if result.returncode:
        print((RUN/(phase+'.stderr')).read_text()[-2500:],flush=True)
        sys.exit(result.returncode)
with (RUN/'execution-result.json').open('x')as f:json.dump({'complete':True,'phases':phases},f,indent=2);f.write('\n')
print('RUN_COMPLETE',RUN.name,flush=True)
