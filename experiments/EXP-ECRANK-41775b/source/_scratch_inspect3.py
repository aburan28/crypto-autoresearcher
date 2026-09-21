"""Scratch inspection 3 (executor, EXP-ECRANK-41775b). Not a protocol artifact."""
import hashlib, json, os

def h(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

base = 'experiments/EXP-ECRANK-73275e'
v1 = os.path.join(base, 'source')
v2 = os.path.join(base, 'source-v2')
for d in (v1, v2):
    for f in sorted(os.listdir(d)):
        if f.endswith('.py'):
            print(os.path.relpath(os.path.join(d, f)), h(os.path.join(d, f)))

for p in (base + '/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json',
          base + '/runs/RUN-ECRANK-73275e-R14-construct-n8-rescoped/raw-result.json',
          base + '/amendments/v2_replication_protocol.yaml'):
    print(p, h(p))
