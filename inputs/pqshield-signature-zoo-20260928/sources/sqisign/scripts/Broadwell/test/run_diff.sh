#!/bin/bash
# usage: run_diff.sh <lvl1|lvl5|newprime c t> [iters]  -- differential/property
# test of fp_generic against the shipping gf reference, on x86-64.
set -e
cd "$(dirname "$0")/../../.."   # repo root
ITERS=${ITERS:-1000000}
STUB=$(mktemp -d); echo "/* stub */" > "$STUB/sqisign_namespace.h"
CF="-O2 -march=native -fno-strict-aliasing -DRADIX_64 -DSQISIGN_GF_IMPL_SAT64 -DTARGET_AMD64 -I $STUB -I src/gf/sat64/include -I src/common/generic/include"
GEN=scripts/gen_fp/gen_fp_asm_broadwell.py
case "$1" in
  lvl1) c=5; t=248; lvl=lvl1; gft=gf5248 ;;
  lvl5) c=27; t=500; lvl=lvl5; gft=gf27500 ;;
  newprime) c=$2; t=$3 ;;
esac
D=$(mktemp -d)
python3 scripts/Broadwell/test/mkparams.py "$c" "$t" > "$D/fp_generic_params.h"
python3 "$GEN" --c "$c" --t "$t" -o "$D/fp_asm.S" > /dev/null
if [ -n "${lvl:-}" ]; then
  gcc $CF -I "$D" -I "src/gf/sat64/$lvl/include" -I "src/precomp/ref/$lvl/include" \
    -DHAVE_REF=1 -DGFHDR="\"$gft.h\"" -DGFT=$gft \
    -Dfp_inv=ref_fp_inv -Dfp_sqrt=ref_fp_sqrt -Dfp_exp3div4=ref_fp_exp3div4 -Dfp_is_square=ref_fp_is_square \
    -c "src/gf/sat64/$lvl/fp.c" -o "$D/ref_fp.o"
  gcc $CF -I "src/gf/sat64/$lvl/include" -c "src/gf/sat64/$lvl/$gft.c" -o "$D/gf.o"
  gcc $CF -I "$D" -c src/gf/sat64/lvlx/fp_generic.c -o "$D/fpg.o"
  gcc $CF -I "$D" -I "src/gf/sat64/$lvl/include" -DHAVE_REF=1 -DGFHDR="\"$gft.h\"" -DGFT=$gft \
    scripts/Broadwell/test/diff_fpg.c "$D/fpg.o" "$D/gf.o" "$D/ref_fp.o" "$D/fp_asm.S" -o "$D/diff"
else
  python3 scripts/Broadwell/test/mkconsts.py "$c" "$t" > "$D/consts.c"
  gcc $CF -I "$D" -c src/gf/sat64/lvlx/fp_generic.c -o "$D/fpg.o"
  gcc $CF -I "$D" -DHAVE_REF=0 scripts/Broadwell/test/diff_fpg.c "$D/fpg.o" "$D/consts.c" "$D/fp_asm.S" -o "$D/diff"
fi
"$D/diff" "$ITERS"
rc=$?
rm -rf "$D" "$STUB"
exit $rc
