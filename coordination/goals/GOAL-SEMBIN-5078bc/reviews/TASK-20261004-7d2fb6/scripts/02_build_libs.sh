#!/bin/bash
# Build the UNMUTATED closure.c (copy of the git blob) in three configurations against my M4RI build,
# and the two exact counters. Usage: bash 02_build_libs.sh   (after sourcing 00_env.sh)
set -e
. $(dirname $0)/00_env.sh
B=$SP/work/build; mkdir -p $B
cp $CODE/closure.c $B/closure_orig.c
INC="-I$M4RI_PREFIX/include"; LIBS="-L$M4RI_PREFIX/lib -Wl,-rpath,$M4RI_PREFIX/lib -lm4ri"
gcc -O2 -Wall -fPIC -shared $INC $B/closure_orig.c -o $B/libclosure_orig.so $LIBS
gcc -O2 -Wall -fPIC -shared $INC -DECH_EVALCHECK $B/closure_orig.c -o $B/libclosure_orig_evalcheck.so $LIBS
gcc -O2 -Wall -fPIC -shared $CODE/count_m2.c -o $B/libcountm2.so
gcc -O2 -Wall -fPIC -shared $CODE/count_chain.c -o $B/libcountchain.so
sha256sum $B/*.so
