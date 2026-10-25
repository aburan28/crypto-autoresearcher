"""Independent fixture, source-equation, divisor and projected-rank audit."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import resource
import sys
from time import perf_counter,process_time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'research/prym_experiment_design_20261019/implementation'))
from independent import verify_fixture,verify_rank


def check(config,panel,result,events):
    if not result['complete'] or result['experiment_id']!='EXP-ECDLP-ad0ffe':raise ValueError('incomplete/wrong run')
    fixtures={f['uid']:f for f in panel['fixtures']}
    for fixture in fixtures.values():verify_fixture(fixture)
    expected={(uid,seed) for uid in fixtures for seed in config['seeds']}
    cells={(v['curve_uid'],v['seed']):v for v in result['cells']}
    if set(cells)!=expected or len(cells)!=len(result['cells']):raise ValueError('missing/duplicate fixed cells')
    groups={key:[] for key in expected}
    for record in events:groups[(record['curve_uid'],record['seed'])].append(record)
    checks=[]
    for key,cell in cells.items():
        fixture=fixtures[key[0]];rows=cell['rows'];stream=groups[key]
        n=min(config['public_source_max'],fixture['r']-1)*config['branches_per_source']
        if len(stream)!=n or cell['attempts']!=n:raise ValueError('finite stream size mismatch')
        if [v['attempt'] for v in stream]!=list(range(1,n+1)):raise ValueError('lost/repeated attempt')
        if dict(Counter(v['status'] for v in stream))!=cell['reasons']:raise ValueError('reason counts differ')
        if Counter(v['scalar'] for v in stream)!=Counter({a:config['branches_per_source'] for a in range(1,min(64,fixture['r']-1)+1)}):
            raise ValueError('public-source grid changed')
        successful=[v for v in stream if v['status']=='accepted']
        if len(successful)!=len(rows) or len(cell['transported_witness_hashes'])!=len(rows):raise ValueError('row coverage mismatch')
        for i,(record,row) in enumerate(zip(successful,rows)):
            if record['row_index']!=i or record['scalar']!=row['source_scalar']:
                raise ValueError('row-event source mismatch')
        checks.append({'curve_uid':key[0],'seed':key[1],**verify_rank(fixture,cell)})
    if len(result['controls'])!=11 or any(v['observed']!=v['expected'] for v in result['controls']):
        raise ValueError('software control mismatch')
    return checks


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--run-dir',type=Path,required=True);args=parser.parse_args()
    start,clock=perf_counter(),process_time();failed=[];checks=[]
    config=json.loads(args.config.read_text());root=Path(__file__).resolve().parents[2]
    panel=json.loads((root/config['fixture_file']).read_text());raw=args.run_dir/'raw-result.json'
    try:
        result=json.loads(raw.read_text())
        if result['config_sha256']!=sha256(args.config.read_bytes()).hexdigest():raise ValueError('config hash mismatch')
        with (args.run_dir/'events.jsonl').open() as stream:
            checks=check(config,panel,result,(json.loads(line) for line in stream))
    except Exception as exc:failed.append(repr(exc))
    verification={'schema':'prym-witness-independent/v1','status':'failed' if failed else 'passed',
        'failed_checks':failed,'cells':checks,'raw_result_sha256':sha256(raw.read_bytes()).hexdigest(),
        'producer_arithmetic_imported':False,'verifier_log_table_present':False,
        'scope':'Independent order recount, public source/divisor equation and rank certificates; event coverage. Rejection arithmetic is not independently replayed.',
        'wall_seconds':perf_counter()-start,'cpu_seconds':process_time()-clock,
        'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
    with (args.run_dir/'verification.json').open('x') as stream:json.dump(verification,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':verification['status'],'failed_checks':failed,'cells':len(checks)}))
    return bool(failed)

if __name__=='__main__':raise SystemExit(main())
