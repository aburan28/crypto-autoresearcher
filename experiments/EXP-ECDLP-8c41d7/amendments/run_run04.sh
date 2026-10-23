#!/bin/bash
# AMD-03: m = 4, L = 4, msolve arms, prime 262271.
cd /home/user/crypto-autoresearcher || exit 1
R=experiments/EXP-ECDLP-8c41d7/runs/RUN-ECDLP-8c41d7-04
mkdir -p $R
jq -r .command experiments/EXP-ECDLP-8c41d7/amendments/trial-plan-run04.json > $R/command.txt
python3 - > $R/environment.json <<'PY'
import json,platform,subprocess,os
print(json.dumps(dict(python=platform.python_version(),platform=platform.platform(),cpus=os.cpu_count(),
 msolve=subprocess.run(["dpkg-query","-W","-f=${Version}","msolve"],capture_output=True,text=True).stdout,
 singular=subprocess.run(["Singular","-v","-q","-c","quit;"],capture_output=True,text=True).stdout.splitlines()[0],
 git_head=subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip(),
 git_dirty=subprocess.run(["git","status","--porcelain","--untracked-files=no"],capture_output=True,text=True).stdout!=""),indent=1))
PY
date -u +%FT%TZ > $R/started_at
bash $R/command.txt > $R/stdout.log 2> $R/stderr.log
echo "exit=$?" >> $R/stdout.log
date -u +%FT%TZ > $R/finished_at
