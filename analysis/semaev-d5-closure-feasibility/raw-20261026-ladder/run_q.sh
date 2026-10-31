#!/bin/bash
cd /home/user/scratch
export RAYON_NUM_THREADS=4
for f in q15 q14_rest q16; do
  s=$(date +%s)
  prlimit --as=15000000000 python3 -c "
import subprocess,resource,json
out=open('$f.result.jsonl','w')
p=subprocess.run(['/home/user/tgt/release/examples/hky_par','ladder','$f.jsonl','--m','4','--cmax','4'],stdout=out,stderr=subprocess.PIPE,text=True)
ru=resource.getrusage(resource.RUSAGE_CHILDREN)
open('$f.rss.json','w').write(json.dumps({'maxrss_mb':round(ru.ru_maxrss/1024),'exit':p.returncode,'stderr':p.stderr[-300:]}))
"
  echo "$f wall=$(( $(date +%s) - s ))s" >> q.log
done
echo DONE >> q.log
