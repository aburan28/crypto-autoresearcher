#!/bin/sh
# Full counts (no early abort) for a J3 input file. Usage: run_j3.sh <infile in tmp/> <outfile> <demo 0|1> <logtag>
V=$(cd "$(dirname "$0")/.." && pwd)
cd "$V/tmp" || exit 1
echo "start $(date -u +%FT%TZ) $1" >> "$V/logs/j3_fullcount_time_$4.txt"
printf 'default(nbthreads,1);\nt0=getwalltime();\nfullcount("%s","%s",%d);\nprint("done ms ",getwalltime()-t0);\nquit;\n' "$1" "$2" "$3" \
  | gp -q --default parisize=200000000 --default parisizemax=3000000000 ../scripts/j3_fullcount.gp > "$V/logs/j3_fullcount_gp_$4.log" 2>&1
echo "end $(date -u +%FT%TZ)" >> "$V/logs/j3_fullcount_time_$4.txt"
