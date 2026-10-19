#!/bin/sh
# build.sh -- EXP-SEMBIN-d9767f. Stages the hash-bound implementation sources
# into a build directory and compiles the four C sources (plus the evaluation-
# check variant of closure.c and the block-local eliminator) there, so the
# bound source tree is never written to and every run builds from source.
#
#   build.sh <source_dir> <build_dir>
#
# Writes <build_dir>/build-info.json: m4ri_available, compiler, libm4ri
# package version, and sha256 of every staged source and built library.
# libm4ri is optional: when closure.c cannot be linked, m4ri_available is
# false, the other libraries are still built and the trial degrades to the
# independent eliminator (design memo). Exit 0 on a usable build (the
# independent eliminator and both enumerators compiled), 1 otherwise.
set -u
SRC="$1"; OUT="$2"
CC="${CC:-gcc}"
CFLAGS="-O2 -Wall -fPIC -shared"
mkdir -p "$OUT/vendor" || exit 1
for f in pilot2_lib.py pilot_lib.py worker.py pilot3.py worker3.py \
         myclosure.c myclosure_local.c count_chain.c count_affu.c; do
  cp "$SRC/$f" "$OUT/$f" || exit 1
done
for f in boolsys.py closure.c closure_cert.py gf2n.py curve.py gf2_chained_builder.py; do
  cp "$SRC/vendor/$f" "$OUT/vendor/$f" || exit 1
done
cd "$OUT" || exit 1
LOG="$OUT/build.log"; : > "$LOG"
ok=1
$CC $CFLAGS myclosure.c -o libmyclosure.so >>"$LOG" 2>&1 || ok=0
$CC $CFLAGS myclosure_local.c -o libmyclosure_local.so >>"$LOG" 2>&1 || ok=0
$CC $CFLAGS count_chain.c -o libcountchain.so >>"$LOG" 2>&1 || ok=0
$CC $CFLAGS count_affu.c -o libcountaffu.so >>"$LOG" 2>&1 || ok=0
m4ri=true
$CC $CFLAGS vendor/closure.c -o vendor/libclosure.so -lm4ri >>"$LOG" 2>&1 || m4ri=false
if [ "$m4ri" = true ]; then
  $CC $CFLAGS -DECH_EVALCHECK vendor/closure.c -o vendor/libclosure_eval.so -lm4ri >>"$LOG" 2>&1 || m4ri=false
fi
if [ "$m4ri" = false ]; then rm -f vendor/libclosure.so vendor/libclosure_eval.so; fi
m4ri_pkg=$(dpkg-query -W -f='${Version}' libm4ri-dev 2>/dev/null || echo "")
ccver=$($CC --version 2>/dev/null | head -n 1)
{
  printf '{\n  "m4ri_available": %s,\n' "$m4ri"
  printf '  "libm4ri_dev_package": "%s",\n' "$m4ri_pkg"
  printf '  "compiler": "%s",\n' "$ccver"
  printf '  "cflags": "%s",\n' "$CFLAGS"
  printf '  "sha256": {\n'
  first=1
  for f in $(ls *.py *.c vendor/*.py vendor/*.c *.so vendor/*.so 2>/dev/null | sort); do
    h=$(sha256sum "$f" | cut -d' ' -f1)
    if [ $first = 1 ]; then first=0; else printf ',\n'; fi
    printf '    "%s": "%s"' "$f" "$h"
  done
  printf '\n  }\n}\n'
} > build-info.json
[ $ok = 1 ] || exit 1
exit 0
