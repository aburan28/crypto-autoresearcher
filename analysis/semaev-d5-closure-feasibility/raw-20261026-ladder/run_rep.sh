#!/bin/bash
cd /home/user/scratch
export RAYON_NUM_THREADS=4
for f in u135_new u145_sel; do
  s=$(date +%s)
  prlimit --as=14500000000 python3 -c "
import subprocess,resource,json,sys
p=subprocess.run(['/home/user/tgt/release/examples/hky_par','ladder','$f.jsonl','--m','4','--cmax','4'],capture_output=True,text=True)
ru=resource.getrusage(resource.RUSAGE_CHILDREN)
open('$f.rss.json','w').write(json.dumps({'maxrss_mb':round(ru.ru_maxrss/1024),'exit':p.returncode,'stderr':p.stderr[-300:]}))
open('$f.result.jsonl','w').write(p.stdout)
"
  echo "$f wall=$(( $(date +%s) - s ))s" >> rep.log
done
echo DONE >> rep.log
