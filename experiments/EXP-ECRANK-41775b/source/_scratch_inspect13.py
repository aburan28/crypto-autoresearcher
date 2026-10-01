"""Scratch inspection 13: armB parameters - draws per stream, schedule mapping.
Not a protocol artifact."""
import json

B = 'experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R3-armB/raw-result.json'
b = json.load(open(B))
for s in b['streams']:
    print({k: v for k, v in s.items() if k not in ('class_attempts_hist',)})
