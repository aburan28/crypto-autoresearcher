"""Admitted full-census natural target study on fixed preprocessing witnesses.

The input JSON embeds cells: fixture, source_order, preprocessing_rows,
target_indices. Global fields: target_domain, max_target_counters, multipliers.
It must freeze every cell and the hash recipe before target generation.
"""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter,process_time

import target_completion as producer
from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.execution_gate import admit
from crypto_autoresearcher.index_calculus.target_relations import hash_public_target
from check_targets import check,check_recipe


def write_once(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def phase(path,fixture,index,name,operation):
    wall,cpu=perf_counter(),process_time()
    record=dict(curve_uid=fixture['uid'],fixture_uid=fixture['uid'],target_index=index,phase=name,
                started_at=datetime.now(timezone.utc).isoformat(),status='complete',wall_valid=False)
    try:return operation()
    except BaseException as error:
        record.update(status='failed',error_type=type(error).__name__,error=str(error));raise
    finally:
        record.update(finished_at=datetime.now(timezone.utc).isoformat(),wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu)
        with path.open('a') as stream:stream.write(json.dumps(record,sort_keys=True)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('inputs', 'protocol', 'release', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('output directory already exists')
    root, old = producer.producer.ROOT, producer.producer.OLD
    here = Path(__file__).resolve().parent
    admission=admit(root, args.protocol, args.inputs,
          [Path(__file__), here/'target_completion.py', here/'prym_completion.py', here/'check_targets.py',
           here/'check_prym.py', old/'census.py',
           root/'research/prym_rank_census_20261025/check_census.py',
           root/'research/prym_factor_base_width_20261025/check_inputs.py',
           old/'relations.py', old/'arithmetic.py', old/'independent.py',
           root/'research/prym_factor_base_width_20261025/collect_width.py',
           root/'src/crypto_autoresearcher/index_calculus/target_relations.py',
           root/'src/crypto_autoresearcher/index_calculus/relation_quality.py',
           root/'src/crypto_autoresearcher/index_calculus/curve.py'],
          {'stopping_rule': 'full census regardless of recovery', 'include_zero': True,
           'target_identity':'full_ec1_curve_uid'}, args.release)
    data = json.loads(args.inputs.read_text())
    args.out.mkdir(parents=True)
    write_once(args.out/'admission.json',admission)
    if data.get('target_identity')!='full_ec1_curve_uid' or len(data['cells'])!=2:
        raise ValueError('fixed full-EC1 two-curve target study required')
    for cell in data['cells']:
        fixture = cell['fixture']
        if Path(fixture['uid']).name != fixture['uid']:
            raise ValueError('curve UID must be a plain file name')
        if len(cell['target_indices']) != len(set(cell['target_indices'])):
            raise ValueError('duplicate target indices')
        if any(type(index) is not int or index < 0 for index in cell['target_indices']):
            raise ValueError('nonnegative integer target indices required')
        curve = Curve(fixture['p'], fixture['a'], fixture['b'])
        if (cell.get('target_curve_uid')!=fixture['ec1']['curve_uid'] or cell['target_indices']!=[0,1,2,3] or
                fixture['p']!=4099 or len(fixture['factor_base'])!=16 or data['multipliers']!=list(range(1,65))):
            raise ValueError('wrong frozen public target or source policy')
        for index in cell['target_indices']:
            stem = fixture['uid']+'-target-'+str(index)
            with (args.out/(stem+'.events.jsonl')).open('x') as events:
                def event(record):
                    events.write(json.dumps(record, sort_keys=True)+'\n')
                    events.flush()
                try:
                    hash_attempts=[]
                    def hash_attempt(record):
                        hash_attempts.append(record);event(dict(kind='target_hash_attempt',**record))
                    hash_before=curve.ops.group_ops
                    recipe = phase(args.out/'phases.jsonl',fixture,index,'hash',lambda:hash_public_target(curve, fixture['r'], cell['target_curve_uid'], index,
                        domain=data['target_domain'], max_counters=data['max_target_counters'],on_attempt=hash_attempt))
                    event(dict(kind='target_generated', recipe=recipe))
                    hash_group_ops=curve.ops.group_ops-hash_before
                    result = phase(args.out/'phases.jsonl',fixture,index,'collection',lambda:producer.collect(fixture, cell['source_order'], cell['preprocessing_rows'],
                        recipe['point'], data['multipliers'], event, capability=producer._NATIVE_CAPABILITY))
                    result.update(target_recipe=recipe, inputs_sha256=sha256(args.inputs.read_bytes()).hexdigest(),target_hash_group_ops=hash_group_ops)
                    write_once(args.out/(stem+'.json'),result)
                    def verify():
                        result_check=check_recipe(fixture,cell['target_curve_uid'],data['target_domain'],index,data['max_target_counters'],recipe,hash_attempts)
                        result_check.update(check(fixture,cell['source_order'],cell['preprocessing_rows'],recipe['point'],data['multipliers'],result))
                        return result_check
                    verification=phase(args.out/'phases.jsonl',fixture,index,'verification',verify)
                    write_once(args.out/(stem+'.verification.json'),verification)
                except BaseException as error:
                    event(dict(kind='failure', error_type=type(error).__name__, error=str(error), complete=False))
                    raise
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
