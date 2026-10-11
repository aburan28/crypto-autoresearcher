#!/bin/sh
# Build the J1 verifier's C kernels into a scratch directory (never into the
# repository). Usage: sh build.sh <outdir>
set -e
OUTDIR="${1:?usage: build.sh <outdir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUTDIR"
gcc -O3 -march=native -fPIC -shared -o "$OUTDIR/libgf2k.so" "$HERE/gf2k.c"
gcc --version | head -1
sha256sum "$HERE/gf2k.c" "$OUTDIR/libgf2k.so"
