#!/bin/bash
# usage: run.sh <c> <t> [asmfile]   -- generate (or use) asm, build, run, verify
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
c=$1; t=$2; asm=${3:-}
SHIFT=$(python3 -c "p=$1*(1<<$2)-1; b=p.bit_length(); N=(b+63)//64; print(b-64*(N-1))")
N=$(python3 -c "p=$c*(1<<$t)-1; print((p.bit_length()+63)//64)")
if [ -z "$asm" ]; then
  asm=/tmp/gen_bw_${c}_${t}.S
  python3 "$ROOT/scripts/gen_fp/gen_fp_asm_broadwell.py" --c "$c" --t "$t" -o "$asm" 2>&1 | head -3
  [ -s "$asm" ] || { echo "  GENERATION FAILED"; exit 2; }
fi
# The broadwell asm reads the p/p2 arrays, so link the standalone constants.
python3 "$HERE/mkconsts.py" "$c" "$t" > /tmp/consts_${c}_${t}.c
${CC:-cc} -O2 -I "$ROOT/include" -I "$ROOT/src/gf/sat64/include" -DDISABLE_NAMESPACING \
   -DN=$N -DSHIFT=$SHIFT -o /tmp/h_bw_${c}_${t} "$HERE/harness.c" /tmp/consts_${c}_${t}.c "$asm" 2>&1 | head -5
[ -x /tmp/h_bw_${c}_${t} ] || { echo "  BUILD FAILED"; exit 2; }
echo "  p = $c*2^$t-1   N=$N limbs"
/tmp/h_bw_${c}_${t} "${ITERS:-2000}" | python3 "$HERE/check.py" "$c" "$t" "$N"
