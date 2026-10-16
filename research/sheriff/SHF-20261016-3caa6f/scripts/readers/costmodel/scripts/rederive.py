"""Blind-ish re-derivation of the primary from raw stdout records (not via verify_receipt.py)."""
import json, sys, os, statistics, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decode import load
P = '/tmp/claude-0/-home-user/bc80ee7c-3e63-5cdc-8921-64b426219182/scratchpad/cryptanalysis/experiments/koblitz-n83-stacked-20261016/run_github_38862448935/panel/'
rows = [json.loads(l) for l in open(P + 'runs.jsonl')]
cold = {}; rank = {}; rho = {}; probes = {}
for r in rows:
    o = load(P + r['stdout_file'])
    if r['arm'] == 'rT':
        rho[r['point_id']] = o; continue
    s = [x for x in o['records'] if x.get('kind') == 'compact_orbit_dlp_summary'][0]
    t = [x for x in o['records'] if x.get('kind') == 'compact_orbit_dlp_target'][0]
    if r['segment'].startswith('C'):
        cold.setdefault(r['arm'], {})[r['point_id']] = s['cold_in_process_ms']
        probes.setdefault(r['arm'], {})[r['point_id']] = t['probes']
    elif r['segment'].startswith('K'):
        rank.setdefault(r['arm'], []).append((s['timing_ms']['rank_stage'], s['cold_in_process_ms'], s['timing_ms']['linear_algebra'], s['rank_probes_total'], s['rank_root_calls_total']))
pts = sorted(cold['cP'])
print('points', len(pts))
def E(k, c):
    return statistics.mean(x[0] for x in rank[k]) + statistics.mean(cold[c][p] for p in pts)
R = E('kP','cP')/E('kS','cS')
print('E2E kP+cP ms', round(E('kP','cP'),1), 'E2E kS+cS ms', round(E('kS','cS'),1), 'R', round(R,4))
# include LA from rank processes explicitly (cold arms already include log-table load+verify)
print('LA ms per rank process kP', [round(x[2],1) for x in rank['kP']], 'kS', [round(x[2],1) for x in rank['kS']])
# process-pairing sensitivity: every choice of one kP process and one kS process
vals = []
for a in rank['kP']:
    for b in rank['kS']:
        vals.append((a[0] + statistics.mean(cold['cP'][p] for p in pts)) / (b[0] + statistics.mean(cold['cS'][p] for p in pts)))
print('R over single-process pairings min/max', round(min(vals),4), round(max(vals),4))
# single-process in-process E2E (rank processes' own cold_in_process incl. setup+rank+LA+one target)
sp = statistics.mean(x[1] for x in rank['kP']) / statistics.mean(x[1] for x in rank['kS'])
print('single-process E2E kP/kS', round(sp,4), [round(x[1]/1e3,1) for x in rank['kP']], [round(x[1]/1e3,1) for x in rank['kS']])
# op-count proxies
pk = sum(x[3] for x in rank['kP']); ps = sum(x[3] for x in rank['kS'])
rk = sum(x[4] for x in rank['kP']); rs = sum(x[4] for x in rank['kS'])
tk = sum(x[0] for x in rank['kP']); ts = sum(x[0] for x in rank['kS'])
print('rank probes ratio kP/kS', round(pk/ps,4), 'root_calls ratio', round(rk/rs,4), 'time ratio', round(tk/ts,4), 'ns/probe kP', round(tk*1e6/pk,1), 'kS', round(ts*1e6/ps,1), 'per-probe ratio', round((tk/pk)/(ts/ps),4))
# online probes
op = sum(probes['cP'].values()); os_ = sum(probes['cS'].values())
print('online probes cP/cS', round(op/os_,6), 'points where cS<cP', sum(1 for p in pts if probes['cS'][p] < probes['cP'][p]))
# share of E2E
print('rank share of E2E: cP', round(statistics.mean(x[0] for x in rank['kP'])/E('kP','cP'),4), 'cS', round(statistics.mean(x[0] for x in rank['kS'])/E('kS','cS'),4))
# what R would be if only setup changed (rank stage held at kP) and if only rank changed
cpm = statistics.mean(cold['cP'][p] for p in pts); csm = statistics.mean(cold['cS'][p] for p in pts)
rkp = statistics.mean(x[0] for x in rank['kP']); rks = statistics.mean(x[0] for x in rank['kS'])
print('R if only cold-without-rank changed', round((rkp+cpm)/(rkp+csm),4), '; R if only rank changed', round((rkp+cpm)/(rks+cpm),4))
# R with a hypothetical common unmeasured base-construction cost X added to both
for X in (0, 1e3, 1e4, 6e4, 3e5):
    print('  common X=%.0f ms -> R=%.4f' % (X, (rkp+cpm+X)/(rks+csm+X)))
