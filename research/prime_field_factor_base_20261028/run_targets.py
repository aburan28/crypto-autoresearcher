"""Admitted full-census natural target study on fixed preprocessing witnesses.

The input JSON embeds cells: fixture, source_order, preprocessing_rows,
target_indices. Global fields: target_domain, max_target_counters, multipliers.
It must freeze every cell and the hash recipe before target generation.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import target_completion as producer
from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.execution_gate import admit
from crypto_autoresearcher.index_calculus.target_relations import hash_public_target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('inputs', 'protocol', 'release', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('output directory already exists')
    root, old = producer.producer.ROOT, producer.producer.OLD
    here = Path(__file__).resolve().parent
    admit(root, args.protocol, args.inputs,
          [Path(__file__), here/'target_completion.py', here/'prym_completion.py',
           old/'relations.py', old/'arithmetic.py', old/'independent.py',
           root/'research/prym_factor_base_width_20261025/collect_width.py',
           root/'src/crypto_autoresearcher/index_calculus/target_relations.py',
           root/'src/crypto_autoresearcher/index_calculus/relation_quality.py',
           root/'src/crypto_autoresearcher/index_calculus/curve.py'],
          {'stopping_rule': 'full census regardless of recovery', 'include_zero': True}, args.release)
    data = json.loads(args.inputs.read_text())
    args.out.mkdir(parents=True)
    for cell in data['cells']:
        fixture = cell['fixture']
        if Path(fixture['uid']).name != fixture['uid']:
            raise ValueError('curve UID must be a plain file name')
        if len(cell['target_indices']) != len(set(cell['target_indices'])):
            raise ValueError('duplicate target indices')
        if any(type(index) is not int or index < 0 for index in cell['target_indices']):
            raise ValueError('nonnegative integer target indices required')
        curve = Curve(fixture['p'], fixture['a'], fixture['b'])
        for index in cell['target_indices']:
            stem = fixture['uid']+'-target-'+str(index)
            with (args.out/(stem+'.events.jsonl')).open('x') as events:
                def event(record):
                    events.write(json.dumps(record, sort_keys=True)+'\n')
                    events.flush()
                try:
                    recipe = hash_public_target(curve, fixture['r'], fixture['uid'], index,
                        domain=data['target_domain'], max_counters=data['max_target_counters'],
                        on_attempt=lambda record: event(dict(kind='target_hash_attempt', **record)))
                    event(dict(kind='target_generated', recipe=recipe))
                    result = producer.collect(fixture, cell['source_order'], cell['preprocessing_rows'],
                        recipe['point'], data['multipliers'], event, capability=producer._NATIVE_CAPABILITY)
                    result.update(target_recipe=recipe, inputs_sha256=sha256(args.inputs.read_bytes()).hexdigest())
                    with (args.out/(stem+'.json')).open('x') as stream:
                        json.dump(result, stream, indent=2)
                        stream.write('\n')
                except BaseException as error:
                    event(dict(kind='failure', error_type=type(error).__name__, error=str(error), complete=False))
                    raise
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
