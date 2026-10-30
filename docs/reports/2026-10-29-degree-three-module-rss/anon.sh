#!/bin/bash
# usage: anon.sh OUTFILE  -- samples RssAnon/RssFile of the running `lean` process every 0.5 s until none remains
out=$1; echo -e "t\tpid\tRssAnon_kb\tRssFile_kb\tVmHWM_kb\tThreads" > $out
seen=0
while :; do
  pid=$(pgrep -x lean | head -1)
  if [ -z "$pid" ]; then [ $seen = 1 ] && break; sleep 0.5; continue; fi
  seen=1
  awk -v t=$(date +%s.%N) -v p=$pid '/^RssAnon/{a=$2}/^RssFile/{f=$2}/^VmHWM/{h=$2}/^Threads/{th=$2}END{printf "%.1f\t%s\t%s\t%s\t%s\t%s\n",t,p,a,f,h,th}' /proc/$pid/status >> $out 2>/dev/null
  sleep 0.5
done
