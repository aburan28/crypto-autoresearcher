"""Scratch inspection 10: R2 static ast trace smoke (read-only).
Not a protocol artifact."""
import sys
sys.path.insert(0, 'experiments/EXP-ECRANK-41775b/source')
import json
import run_package as RP

t1 = RP.trace_source(RP.BOUND_V1 + '/construct.py', 'source/construct.py')
t2 = RP.trace_source(RP.BOUND_V2 + '/construct_v2.py', 'source-v2/construct_v2.py')
print(json.dumps({'v1': t1, 'v2': t2}, indent=1)[:6000])
