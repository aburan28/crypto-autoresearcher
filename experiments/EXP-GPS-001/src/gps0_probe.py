#!/usr/bin/env python3
# EXP-GPS-001 RUN-a — probe/extract existing artifacts (forensics, no new matrices)
# 1) sha256-verify all 76 EXP-SIG-007 rank5 carries vs state.json; extract all
#    pivot ROW-position lists (P blocks) to work/pivots_rows_all.json.
# 2) Probe EXP-SIG-008 work pkls' structure (sem_kernels, sem_s2_base, sem_f345).
# Sage matrix payloads are SKIPPED via a stub unpickler (no sage import).
import json, pickle, hashlib, time, sys
from pathlib import Path

t0 = time.time()
ROOT = Path('/Volumes/Volume/crypto-autoresearcher')
R5 = ROOT / 'experiments/EXP-SIG-007/work/n21_s1/rank5'
W8 = ROOT / 'experiments/EXP-SIG-008/work'
OUT = ROOT / 'experiments/EXP-GPS-001/work'
OUT.mkdir(parents=True, exist_ok=True)

class _Stub:
    def __init__(self, *a, **k): pass
    def __setstate__(self, s): pass
class SkipSage(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith('sage') or module.startswith('cypari2'):
            return _Stub
        return pickle.Unpickler.find_class(self, module, name)

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()

st = json.load(open(R5 / 'state.json'))
res = {'run': 'RUN-EXP-GPS-001-a', 'carry_verify': [], 'n_carry_files_ok': 0,
       'total_pivots': 0, 'rank_acc_state': st['rank_acc'],
       'burst_unit': None, 'pkl_probes': {}}
all_p = []
ok = True
for c in st['carries']:
    p = R5 / c['file']
    h = sha256(p)
    match = (h == c['sha256'])
    ok &= match
    with open(p, 'rb') as f:
        P, _H = SkipSage(f).load()
    res['carry_verify'].append({'file': c['file'], 'sha256_ok': match,
                                'npiv_state': c['npiv'], 'npiv_loaded': len(P)})
    assert len(P) == c['npiv'], 'npiv mismatch %s' % c['file']
    all_p.append({'file': c['file'], 'P': P})
res['n_carry_files_ok'] = sum(1 for v in res['carry_verify'] if v['sha256_ok'])
res['total_pivots'] = sum(v['npiv_loaded'] for v in res['carry_verify'])
res['all_sha256_ok'] = bool(ok)
# burst unit = last carry (075): its P block
res['burst_unit'] = {'file': st['carries'][-1]['file'],
                     'npiv': st['carries'][-1]['npiv'],
                     'P_min': min(all_p[-1]['P']), 'P_max': max(all_p[-1]['P']),
                     'note': 'P entries are ROW-space pivot positions, not column indices'}
with open(OUT / 'pivots_rows_all.json', 'w') as f:
    json.dump({'carries': all_p, 'state_units': st['units']}, f)

def probe(fn):
    t = time.time()
    with open(W8 / fn, 'rb') as f:
        o = SkipSage(f).load()
    def desc(x, d=0):
        if d > 2: return type(x).__name__
        if isinstance(x, dict):
            return {'dict_keys': list(x.keys())[:12],
                    'vals': {str(k): desc(v, d + 1) for k, v in list(x.items())[:4]}}
        if isinstance(x, (list, tuple)):
            return {'%s[%d]' % (type(x).__name__, len(x)):
                    desc(x[0], d + 1) if len(x) else None}
        if hasattr(x, 'shape'):
            return 'ndarray%s/%s' % (x.shape, x.dtype)
        if isinstance(x, bytes): return 'bytes[%d]' % len(x)
        return repr(x)[:60]
    return {'load_s': round(time.time() - t, 2), 'top': desc(o)}

for fn in ['sem_kernels.pkl', 'sem_f345.pkl', 'sem_s1.pkl',
           'sem_s2_base_00.pkl', 'sem_s2_base_01.pkl', 'sem_s2_base_02.pkl',
           'sem_s2_base_03.pkl']:
    res['pkl_probes'][fn] = probe(fn)
res['wall_s'] = round(time.time() - t0, 2)
out = ROOT / 'experiments/EXP-GPS-001/runs/RUN-EXP-GPS-001-a/raw.json'
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(res, open(out, 'w'), indent=1)
print(json.dumps({k: res[k] for k in ('n_carry_files_ok', 'total_pivots',
                                      'rank_acc_state', 'all_sha256_ok',
                                      'burst_unit', 'wall_s')}, indent=1))
print('kernels keys:', res['pkl_probes']['sem_kernels.pkl']['top'])
