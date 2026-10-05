#!/bin/bash
# Scratch copy of the producer's python modules next to MY builds of the libraries (so the producer's own
# closure_cert/soundness_probe/solcount code can be driven without loading the producer's binaries).
. $(dirname $0)/00_env.sh
P=$SP/work/prodcopy; mkdir -p $P
for f in boolsys.py eq4sys.py closure_cert.py soundness_probe.py solcount.py sumpoly_check.py; do cp $CODE/$f $P/; done
cp $SP/work/build/libclosure_orig.so $P/libclosure.so
cp $SP/work/build/libcountm2.so $SP/work/build/libcountchain.so $P/
sha256sum $P/*.py $P/*.so
