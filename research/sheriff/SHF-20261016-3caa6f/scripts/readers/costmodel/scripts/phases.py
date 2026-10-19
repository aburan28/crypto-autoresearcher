import json, sys, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decode import load
P = '/tmp/claude-0/-home-user/bc80ee7c-3e63-5cdc-8921-64b426219182/scratchpad/cryptanalysis/experiments/koblitz-n83-stacked-20261016/run_github_38862448935/panel/'
rows = [json.loads(l) for l in open(P + 'runs.jsonl')]
want = sys.argv[1:]  # serials
for r in rows:
    if str(r['serial']) in want:
        o = load(P + r['stdout_file'])
        summ = [x for x in o['records'] if x.get('kind') == 'compact_orbit_dlp_summary']
        s = summ[0] if summ else {}
        print('=== serial', r['serial'], r['arm'], r['segment'], r['point_id'], 'process_wall_ms', r['process_wall_ms'])
        print(' fields:', {k: o['fields'][k] for k in o['fields'] if k not in ('relation',)})
        print(' cold_phase_ms:', json.dumps(s.get('cold_phase_ms'), indent=None))
        print(' timing_ms:', json.dumps(s.get('timing_ms')))
        print(' factor_log_table:', json.dumps(s.get('factor_log_table')))
        for k in ('state_fold','stored_states','root_table','root_table_slots','root_table_bytes','rank_canonicalizer','rank_order','rank_probe','index_canonicalizer','fold_plant','scan_order_selftest','index_digest'):
            print(' ', k, '=', json.dumps(s.get(k)))
