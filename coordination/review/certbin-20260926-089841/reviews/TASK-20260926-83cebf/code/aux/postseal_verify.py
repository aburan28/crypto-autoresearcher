"""Post-seal verification (read-only on the sealed files). Separate process.
(1) re-check every wdag-v1 record with the checker, f_k rebuilt from the
    pool monomial lists / the sealed stream-replay row hex;
(2) re-generate the N-CONV stream with direct numpy calls and compare every
    attempt's row hex and outcome with the sealed stream-replay;
(3) consistency of the keep rule in the sealed log; s re-counted by the
    unpacked exhaustive route on every kept system.
"""
import sys, json, gzip, hashlib
CODE = '/home/user/crypto-autoresearcher/coordination/review/certbin-20260926-089841/reviews/TASK-20260926-83cebf/code'
sys.path.insert(0, CODE)
import numpy as np
import br_system as S, br_wdag_check as WC, br_sat as SAT
TD = '/home/user/crypto-autoresearcher/coordination/review/certbin-20260926-089841/reviews/TASK-20260926-83cebf'
BI = '/home/user/crypto-autoresearcher/coordination/review/certbin-20260926-089841/blind/blind-inputs.json'
inp = json.load(open(BI))
B = inp['curve']['B']
att = [json.loads(l) for l in gzip.open(TD + '/stream-replay.jsonl.gz', 'rt')]
nconv = [a for a in att if a['arm'] == 'N-CONV']
out = {}
# (1)
pool = {s['label']: s['equations'] for s in inp['systems']}
kept = {}
for a in nconv:
    if a['outcome'] in ('kept_unsat', 'kept_sat'):
        kept[(a['slot'], a['outcome'][5:])] = a['row_hex']
def eqs_from_hex(rh):
    eqs = []
    for h in rh:
        x = int(h, 16); eq = []; j = 0
        while x:
            if x & 1: eq.append(list(S.E_MONOS[j]))
            x >>= 1; j += 1
        eqs.append(eq)
    return eqs
n = ok = 0
for line in gzip.open(TD + '/wcerts.jsonl.gz', 'rt'):
    c = json.loads(line)
    key = c['label_or_replay_key']
    if key in pool: eqs = pool[key]
    else:
        _, slot, role = key.split(':'); eqs = eqs_from_hex(kept[(int(slot), role)])
    res = WC.Checker(eqs).check(c)
    n += 1; ok += res['valid']
out['recheck_certificates'] = {'records': n, 'valid': ok}
# (2)
U = S.union_support(B); SL = S.S_L_positions(U)
g = np.random.Generator(np.random.PCG64(2026092450101))
xr = [s['x_R'] for s in inp['slots']]
mism = 0; idx = 0; keys = set()
for slot in range(144):
    ES3 = S.E_S3(xr[slot], B)
    have = {'unsat': False, 'sat': False}
    for a in range(256):
        bits = g.integers(0, 2, size=len(SL))
        E = np.zeros_like(ES3); E[:, 19:] = ES3[:, 19:]
        for (k, cc), b in zip(SL, bits): E[k, cc] = b
        rec = nconv[idx]; idx += 1
        if rec['slot'] != slot or rec['attempt'] != a or rec['row_hex'] != S.row_hex(E): mism += 1
        key = E.tobytes()
        rej = np.array_equal(E, ES3) or key in keys
        s, _ = SAT.count_s(E)
        if s != rec['s']: mism += 1
        if rej: exp = 'rejected'
        elif s == 0: exp = 'discarded' if have['unsat'] else 'kept_unsat'
        else: exp = 'discarded' if have['sat'] else 'kept_sat'
        if exp != rec['outcome']: mism += 1
        if exp.startswith('kept'):
            have[exp[5:]] = True; keys.add(key)
        if have['unsat'] and have['sat']: break
out['stream_regeneration'] = {'attempts_compared': idx, 'attempts_in_sealed_log': len(nconv), 'mismatches': mism}
# (3) unpacked exhaustive s on kept systems
bad = 0
for (slot, role), rh in kept.items():
    E = np.zeros((17, 172), dtype=np.uint8)
    for k, h in enumerate(rh):
        x = int(h, 16); j = 0
        while x:
            if x & 1: E[k, j] = 1
            x >>= 1; j += 1
    s2 = SAT.count_s_unpacked(E)
    if (role == 'unsat') != (s2 == 0): bad += 1
out['kept_systems_role_vs_unpacked_s'] = {'systems': len(kept), 'disagreements': bad}
print(json.dumps(out))
