"""Scratch inspection 14: check premerge fixed H-ECRANK-a84737.sha256 and EXP spec hashes.
Not a protocol artifact."""
import hashlib

def h(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

print('specification.yaml:', h('experiments/EXP-ECRANK-41775b/specification.yaml'))
print('H-ECRANK-a84737.yaml:', h('ledger/hypotheses/H-ECRANK-a84737.yaml'))
print('DEC-20260910-c10298.yaml:', h('ledger/decisions/DEC-20260910-c10298.yaml'))
print('v2 amendment:', h('experiments/EXP-ECRANK-73275e/amendments/v2_replication_protocol.yaml'))
print('R12 raw:', h('experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json'))
print('R14 raw:', h('experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R14-construct-n8-rescoped/raw-result.json'))
print('armB raw:', h('experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R3-armB/raw-result.json'))
