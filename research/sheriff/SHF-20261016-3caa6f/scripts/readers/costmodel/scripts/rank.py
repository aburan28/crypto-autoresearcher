import json, sys, os, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decode import load
P = '/tmp/claude-0/-home-user/bc80ee7c-3e63-5cdc-8921-64b426219182/scratchpad/cryptanalysis/experiments/koblitz-n83-stacked-20261016/run_github_38862448935/panel/'
rows = [json.loads(l) for l in open(P + 'runs.jsonl')]
out = {}
for r in rows:
    if not r['segment'].startswith('K'): continue
    o = load(P + r['stdout_file'])
    s = [x for x in o['records'] if x.get('kind') == 'compact_orbit_dlp_summary'][0]
    ns, pr = s['rank_attempt_ns'], s['rank_attempt_probes']
    h = len(ns)//2
    nspp1 = sum(ns[:h])/sum(pr[:h]); nspp2 = sum(ns[h:])/sum(pr[h:])
    print('%-5s %s serial=%3d fin=%.0f rank_stage_s=%.1f attempts=%d sum_att_s=%.1f probes_tot=%d ns/probe=%.1f (1st half %.1f, 2nd half %.1f) cold_in_proc_s=%.1f index_s=%.1f LA_ms=%.1f relblake=%s logs_eq=%s wrote=%s' % (
        r['arm'], r['segment'], r['serial'], r['finished_unix_s'], s['timing_ms']['rank_stage']/1e3, len(ns), sum(ns)/1e9, sum(pr),
        sum(ns)/sum(pr), nspp1, nspp2, s['cold_in_process_ms']/1e3, s['timing_ms']['index_build']/1e3, s['timing_ms']['linear_algebra'],
        s['rank_relations_blake3'][:8], o['fields'].get('logs_equal_archived'), o['records'][2].get('factor_log_table_written_sha256','')[:8]))
    out[(r['arm'], r['segment'])] = (ns, pr)
# paired per-attempt comparison kP vs kS same block
for blk in ('K1','K2'):
    a = out[('kP',blk)]; b = out[('kS',blk)]
    same = sum(1 for x,y in zip(a[1],b[1]) if x==y)
    print(blk, 'kP vs kS attempts with identical probe count:', same, 'of', len(a[1]))
    print(blk, 'probe ratio kP/kS', sum(a[1])/sum(b[1]), 'time ratio', sum(a[0])/sum(b[0]))
