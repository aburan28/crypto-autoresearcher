#!/bin/sh
# Launch the early-abort re-census shards (attempt 2). Usage: run_recensus.sh <tag> <W>
V=$(cd "$(dirname "$0")/.." && pwd); tag=$1; W=$2
cd "$V/tmp" || exit 1
sha256sum shard${tag}_*.gp >> "$V/logs/recensus_inputs.sha256"
echo "start $(date -u +%FT%TZ) tag=$tag W=$W" >> "$V/logs/recensus_time_attempt2.txt"
j=0
while [ $j -lt $W ]; do
  printf 'default(nbthreads,1);\nt0=getwalltime();\ncensus("shard%s_%d.gp","../out/recensus_raw_%s_%d.txt",0);\nprint("shard %d ms ",getwalltime()-t0);\nquit;\n' "$tag" $j "$tag" $j $j \
    | gp -q --default parisize=200000000 --default parisizemax=3000000000 ../scripts/recensus.gp > "$V/logs/recensus_gp_${tag}_$j.log" 2>&1 &
  j=$((j+1))
done
wait
echo "end $(date -u +%FT%TZ)" >> "$V/logs/recensus_time_attempt2.txt"
