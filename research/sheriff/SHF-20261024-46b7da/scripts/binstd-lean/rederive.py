import fractions
import hashlib
import json
import subprocess

repo = '/home/ec2-user/crypto-autoresearcher-sheriff-20261024'
base = 'experiments/EXP-BINSTD-8bdf86/'

def blob(path):
    return subprocess.check_output(['git', '-C', repo, 'show', 'origin/main:' + base + path])

# Re-derive the ceiling from the parameters, before using archived measurements.
assert all(4 * tau < 5 * targets for targets in range(1, 41) for tau in range(targets + 1))
assert not (5 * 40 < 5 * 40)  # Deliberately false shifted-band control.
print('blind_bound: all 860 finite witnesses pass; equality counterexample rejects shifted band')

for tag, run in [('ell89', 'RUN-BINSTD-43abd4'), ('ell89r1', 'RUN-BINSTD-a2a24c')]:
    panel_bytes = blob(f'stage1-{tag}/yield-matrix.json')
    panel = json.loads(panel_bytes)
    raw = json.loads(blob(f'runs/{run}/raw-result.json'))['result']
    digest = hashlib.sha256(panel_bytes).hexdigest()
    assert digest == raw['artifact_sha256']['stage1/yield-matrix.json']
    print(f'{tag}: digest={digest} matched=True')
    for cell in panel['cells']:
        tau, opn, targets = cell['hits_tau'], cell['hits_open'], cell['target_count']
        assert targets > 0 and opn == targets and 0 <= tau <= targets
        ratio = fractions.Fraction(tau, opn)
        assert float(ratio) == cell['ratio_tau_over_open']
        assert 4 * tau < 5 * opn
        assert cell['band'] == 1.25
        print(f"  ell={cell['ell']} tau={tau} open={opn} targets={targets} ratio={ratio}")

first = blob('stage1-ell89/admissible-phi-dims.json')
second = blob('stage1-ell89r1/admissible-phi-dims.json')
assert first == second
factors = [row['poly'] for row in json.loads(first)['factors']]

def carryless_mul(a, b):
    product = 0
    while b:
        if b & 1:
            product ^= a
        a <<= 1
        b >>= 1
    return product

product = 1
for factor in factors:
    product = carryless_mul(product, factor)
assert product == (1 << 17) | 1
print(f'factorization: factors={factors} product={product} expected={(1 << 17) | 1}')
