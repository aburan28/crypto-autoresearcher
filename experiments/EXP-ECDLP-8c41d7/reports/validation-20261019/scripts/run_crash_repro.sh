#!/bin/bash
# Check 2: standalone msolve crash reproduction. Everything pinned to <= 2 cores (cores given as $1 $2). Outputs -> $OUT
C0=${1:-2}; C1=${2:-3}
V=/tmp/claude-0/validator4; OUT=$V/crash; cd $OUT
echo "== 17-bit: RUN-03 L=4 inst 0 rebuilt with committed code (p=65551): msolve -g 2 -v 2 -t 1 (A_elim with -e 12)" | tee repro_17bit.out
for a in B_ms A_drl_ms; do taskset -c $C0 python3 $V/probe_msolve.py run03_L4_i0_p65551/$a.ms 120 | tee -a repro_17bit.out; done
taskset -c $C0 python3 $V/probe_msolve.py run03_L4_i0_p65551/A_elim_ms.ms 120 -e 12 | tee -a repro_17bit.out
echo "== 19-bit: RUN-04 L=4 inst 0 rebuilt with committed code (p=262271): 90 s probes, two cores" | tee repro_19bit.out
(taskset -c $C0 python3 $V/probe_msolve.py run04_L4_i0_p262271/B_ms.ms 90 | tee -a repro_19bit.out &
 taskset -c $C1 python3 $V/probe_msolve.py run04_L4_i0_p262271/A_drl_ms.ms 90 | tee -a repro_19bit.out & wait)
echo "== tiny 2-variable system x^2+y^2-1, x*y-2 over F_p" | tee repro_tiny.out
mkdir -p tiny; for p in 65003 65519 65539 65551 131111 256499 262139 262147 262271 300007; do printf 'x,y\n%s\nx^2+y^2-1,\nx*y-2\n' $p > tiny/t_$p.ms
  echo "p=$p bits=$(python3 -c "print(int($p).bit_length())") $(taskset -c $C0 python3 $V/probe_msolve.py tiny/t_$p.ms 20 | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d['status'],d['wall_s'])")" | tee -a repro_tiny.out; done
