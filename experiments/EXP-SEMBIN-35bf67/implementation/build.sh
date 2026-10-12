#!/bin/sh
# EXP-SEMBIN-35bf67 build. Usage: build.sh OUTDIR
# Builds M4RI release-20240729 (git d0a1ee18511714a2c33cc0920a068c05c1f0f8fb) from source
# into OUTDIR/m4ri-install (NOT the apt 0.0.20200125 package; DEC-20261005-c83e5a N2),
# then the two rank arms and the solution counters.
set -e
OUT=${1:?outdir}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
if [ ! -f "$OUT/m4ri-install/lib/libm4ri.a" ]; then
  git clone -q https://github.com/malb/m4ri.git "$OUT/m4ri-src"
  (cd "$OUT/m4ri-src" && git checkout -q d0a1ee18511714a2c33cc0920a068c05c1f0f8fb &&
   autoreconf --install >/dev/null 2>&1 &&
   ./configure --prefix="$OUT/m4ri-install" --enable-openmp=no CFLAGS="-O3 -march=native" >/dev/null &&
   make -j4 >/dev/null && make install >/dev/null)
fi
CF="-O3 -march=native -std=gnu11 -Wall -Wno-unused-result"
gcc $CF -I"$OUT/m4ri-install/include" -o "$OUT/solv4_A" "$HERE/solv4.c" "$HERE/kernel_a.c" "$OUT/m4ri-install/lib/libm4ri.a" -lm
gcc $CF -o "$OUT/solv4_B" "$HERE/solv4.c" "$HERE/kernel_b.c" -lm
if [ -f "$HERE/sols.c" ]; then gcc $CF -o "$OUT/sols" "$HERE/sols.c" -lm; fi
if [ -f "$HERE/exhaust.c" ]; then gcc $CF -o "$OUT/exhaust" "$HERE/exhaust.c" -lm; fi
sha256sum "$OUT"/solv4_A "$OUT"/solv4_B "$OUT/m4ri-install/lib/libm4ri.a" $( [ -f "$OUT/sols" ] && echo "$OUT/sols" ) $( [ -f "$OUT/exhaust" ] && echo "$OUT/exhaust" )
