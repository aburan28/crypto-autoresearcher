#!/bin/bash
# AMD-01 (this experiment) then AMD-01 (EXP-ECDLP-20a588): run the two unexecuted sets of cells back to back
# so no two runs share the 4 cores.
cd /home/user/crypto-autoresearcher || exit 1
run() {  # $1 = run dir, $2 = plan with .command
  R=$1; mkdir -p $R
  jq -r .command $2 > $R/command.txt
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
}
run experiments/EXP-ECDLP-8c41d7/runs/RUN-ECDLP-8c41d7-02 experiments/EXP-ECDLP-8c41d7/amendments/trial-plan-run02.json
run experiments/EXP-ECDLP-20a588/runs/RUN-ECDLP-20a588-02 experiments/EXP-ECDLP-20a588/amendments/trial-plan-run02.json
