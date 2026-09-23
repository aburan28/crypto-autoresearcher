#!/bin/sh
# INVOCATIONS 2 (EcGFp5) and 3 (EcMasFp5), one chunk of each, run in parallel inside ONE hold of the
# shared solver lock (taken by the caller with flock). Each sweep stops itself after $1 seconds and
# resumes from its witnesses.jsonl on the next chunk.
cd "$(dirname "$0")"
CH=${1:-1500}
date -u +"chunk start %Y-%m-%dT%H:%M:%SZ"
python3 sweep.py --curve EcGFp5 --out inv2 --chunk-seconds "$CH" >> inv2/stdout.log 2>> inv2/stderr.log &
A=$!
python3 sweep.py --curve EcMasFp5 --out inv3 --chunk-seconds "$CH" >> inv3/stdout.log 2>> inv3/stderr.log &
B=$!
wait $A; echo "EcGFp5 exit=$?"
wait $B; echo "EcMasFp5 exit=$?"
date -u +"chunk end %Y-%m-%dT%H:%M:%SZ"
