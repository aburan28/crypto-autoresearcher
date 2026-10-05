#!/bin/bash
set -e
SP=/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/v7d2fb6
cd $SP/m4ri_src
git checkout -q release-20240729
autoreconf -fi
./configure --prefix=$SP/m4ri_prefix --disable-openmp
make -j2
make check
make install
echo BUILD_DONE
