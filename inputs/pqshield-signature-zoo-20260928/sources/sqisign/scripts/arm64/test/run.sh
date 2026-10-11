#!/bin/sh
# usage: run.sh <c> <t> [asmfile]   -- generate (or use) asm, build, run, verify
# Runs natively on any AArch64 host (macOS or Linux); the harness and the
# Python referee are shared with scripts/Broadwell/test.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
BW=$ROOT/scripts/Broadwell/test
c=$1; t=$2; asm=${3:-}
SHIFT=$(python3 -c "p=$1*(1<<$2)-1; b=p.bit_length(); N=(b+63)//64; print(b-64*(N-1))")
N=$(python3 -c "p=$c*(1<<$t)-1; print((p.bit_length()+63)//64)")
if [ -z "$asm" ]; then
  asm=/tmp/gen_arm64_${c}_${t}.S
  python3 "$ROOT/scripts/gen_fp/gen_fp_asm_arm64.py" --c "$c" --t "$t" -o "$asm" 2>&1 | head -3
  [ -s "$asm" ] || { echo "  GENERATION FAILED"; exit 2; }
fi
cc -O2 -I "$ROOT/include" -I "$ROOT/src/gf/sat64/include" -DDISABLE_NAMESPACING \
   -DN=$N -DSHIFT=$SHIFT -DFP2_FUSED -o /tmp/h_arm64_${c}_${t} "$BW/harness.c" "$asm" 2>&1 | head -5
[ -x /tmp/h_arm64_${c}_${t} ] || { echo "  BUILD FAILED"; exit 2; }
echo "  p = $c*2^$t-1   N=$N limbs"
/tmp/h_arm64_${c}_${t} "${ITERS:-2000}" | python3 "$BW/check.py" "$c" "$t" "$N"
