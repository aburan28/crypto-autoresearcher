import json, sys, yaml
RUNS = '/home/user/crypto-autoresearcher/experiments/EXP-CMFB-cea1d2/runs'
RE = '/tmp/claude-0/-home-user/f3553d8c-d92f-57ed-aee6-36992723a751/scratchpad/rerun'
IGN = {'timings', 'peak_rss_bytes', 'recount_timing', 'workers_rss', 'per_member'}
ids = ['RUN-CMFB-2373be', 'RUN-CMFB-5905c0', 'RUN-CMFB-66b0fe', 'RUN-CMFB-3dc120', 'RUN-CMFB-42a578', 'RUN-CMFB-e13f0e', 'RUN-CMFB-c71d35', 'RUN-CMFB-2010d3']


def diff(a, b, path=''):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in IGN:
                continue
            if k not in a or k not in b:
                out.append(f'{path}/{k}: key missing')
            else:
                out += diff(a[k], b[k], f'{path}/{k}')
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f'{path}: len {len(a)} vs {len(b)}')
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out += diff(x, y, f'{path}[{i}]')
    else:
        if a != b:
            out.append(f'{path}: {str(a)[:60]} vs {str(b)[:60]}')
    return out


for r in ids:
    try:
        a = json.load(open(f'{RUNS}/{r}/raw-result.json'))
        b = json.load(open(f'{RE}/{r}/raw-result.json'))
    except Exception as e:
        print(r, 'ERR', e)
        continue
    d = diff(a, b)
    ma = yaml.safe_load(open(f'{RUNS}/{r}/manifest.yaml'))['run']
    mb = yaml.safe_load(open(f'{RE}/{r}/manifest.yaml'))['run']
    mdiff = []
    for k in ('seeds', 'trial_id', 'id'):
        if ma[k] != mb[k]:
            mdiff.append(k)
    if ma['code']['source_sha256'] != mb['code']['source_sha256']:
        mdiff.append('source_sha256')
    if ma['result'] != mb['result']:
        mdiff.append('result summary')
    print(f"{r}: raw-result deterministic-field differences: {len(d)} {d[:3]} | manifest diffs {mdiff} | rerun commit {mb['code']['commit'][:10]} dirty {mb['code']['dirty']} | tau recorded {ma['timing']['tau_seconds_per_triple']} rerun {mb['timing']['tau_seconds_per_triple']}")
