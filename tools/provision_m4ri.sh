#!/usr/bin/env bash
# Provision m4ri (fast bit-sliced exact GF(2) linear algebra) without Sage/conda.
# The proxy blocks conda and GitHub tarballs, but the git protocol to GitHub
# works, and Ubuntu ships a C toolchain -- so we build m4ri from source and
# compile the ctypes shim. Idempotent.
set -euo pipefail
PREFIX=/usr/local
SHIM_SRC="$(cd "$(dirname "$0")" && pwd)/m4ri_shim.c"
if [ ! -f "$PREFIX/lib/libm4ri.so" ]; then
  command -v libtool >/dev/null || apt-get install -y -q libtool >/dev/null
  rm -rf /tmp/m4ri_src
  git clone --depth 1 https://github.com/malb/m4ri /tmp/m4ri_src
  cd /tmp/m4ri_src
  autoreconf --install
  ./configure --disable-png --prefix="$PREFIX"
  make -j"$(nproc)"
  make install
  ldconfig
fi
gcc -shared -fPIC -O2 "$SHIM_SRC" -o "$PREFIX/lib/m4ri_shim.so" \
    -I"$PREFIX/include" -L"$PREFIX/lib" -lm4ri
echo "m4ri provisioned: $PREFIX/lib/libm4ri.so + m4ri_shim.so"
