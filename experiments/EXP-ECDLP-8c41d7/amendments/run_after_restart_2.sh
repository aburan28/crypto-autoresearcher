#!/bin/bash
# After the second VM restart: EXP-ECDLP-20a588 AMD-01 (m = 3, L = 7) first (short), then this experiment's AMD-02 (m = 4, L = 4).
cd /home/user/crypto-autoresearcher || exit 1
run() {  # $1 = run dir, $2 = plan holding .command
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
run experiments/EXP-ECDLP-20a588/runs/RUN-ECDLP-20a588-03 experiments/EXP-ECDLP-20a588/amendments/trial-plan-run03.json
run experiments/EXP-ECDLP-8c41d7/runs/RUN-ECDLP-8c41d7-03 experiments/EXP-ECDLP-8c41d7/amendments/trial-plan-run03.json
