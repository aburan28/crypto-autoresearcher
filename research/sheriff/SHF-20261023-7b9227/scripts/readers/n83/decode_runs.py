"""Decode every raw producer record of a cryptanalysis ic panel into one flat JSON list.
Blind: reads only runs.jsonl (wrapper rows) and runs/NNNNN.stdout.txt (raw_b64 producer records).
Checks sha256(raw) == wrapper raw_result_sha256 for every row."""
import json, base64, hashlib, sys, os
d = sys.argv[1]; out = sys.argv[2]
rows = [json.loads(l) for l in open(os.path.join(d, 'runs.jsonl'))]
flat = []; bad = 0
for r in rows:
    fn = os.path.join(d, 'runs', os.path.basename(r['stdout_file']))
    first = open(fn).read().split('\n')[0]
    raw = base64.b64decode(first.split('=', 1)[1])
    ok = hashlib.sha256(raw).hexdigest() == r['fields'].get('raw_result_sha256')
    bad += (not ok)
    rec = json.loads(raw)
    summ = [x for x in rec.get('records', []) if isinstance(x, dict) and x.get('kind', '').endswith('summary')]
    tm = summ[0].get('timing_ms', {}) if summ else {}
    flat.append(dict(serial=r['serial'], arm=r['arm'], role=r.get('role'), side=r.get('side'), pair=r.get('pair'), block=r.get('block'), unit=r.get('unit'),
                     position=r.get('position'), point=r.get('point_id'), seed=r.get('seed'), segment=r.get('segment'),
                     status=r['status'], verified=r['fields'].get('verified'), sha_ok=ok,
                     scalar=rec.get('fields', {}).get('recovered_scalar'),
                     rank_stage_ms=tm.get('rank_stage'), linear_algebra_ms=tm.get('linear_algebra'),
                     index_build_ms=tm.get('index_build'), base_load_ms=tm.get('base_load'),
                     setup_total_ms=tm.get('setup_total'), process_total_ms=tm.get('process_total'),
                     cold_in_process_ms=(summ[0].get('cold_in_process_ms') if summ else None),
                     online_ms=rec.get('fields', {}).get('online_ms'),
                     scan_selftest_ms=rec.get('fields', {}).get('scan_selftest_ms'),
                     rank_attempts=(summ[0].get('rank_attempts') if summ else None),
                     rank_probes_total=(summ[0].get('rank_probes_total') if summ else None),
                     process_wall_ms=r.get('process_wall_ms'),
                     cpu_ms=(r.get('child_cpu_user_ms') or 0) + (r.get('child_cpu_system_ms') or 0),
                     finished_unix_s=r.get('finished_unix_s')))
json.dump(flat, open(out, 'w'), indent=0)
print('rows', len(flat), 'sha_mismatch', bad)
