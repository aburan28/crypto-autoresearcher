"""Run a source-bound paired zero-completion stream after canonical admission."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import prym_completion as producer
from check_prym import check
from crypto_autoresearcher.index_calculus.execution_gate import admit
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, type=Path)
    parser.add_argument('--protocol', required=True, type=Path)
    parser.add_argument('--release', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('output directory already exists')
    here = Path(__file__).resolve().parent
    admit(producer.ROOT, args.protocol, args.inputs,
          [Path(__file__), here/'prym_completion.py', producer.OLD/'relations.py',
           producer.OLD/'arithmetic.py', producer.OLD/'independent.py',
           producer.OLD/'census.py',
           producer.ROOT/'research/prym_rank_census_20261025/check_census.py',
           producer.ROOT/'research/prym_factor_base_width_20261025/check_inputs.py',
           producer.ROOT/'src/crypto_autoresearcher/index_calculus/relation_quality.py',
           producer.ROOT/'src/crypto_autoresearcher/index_calculus/curve.py',
           here/'check_prym.py', producer.ROOT/'research/prym_factor_base_width_20261025/collect_width.py'],
          {'arms': ['historical_nonzero', 'completed_zero']}, args.release)
    data = json.loads(args.inputs.read_text())
    args.out.mkdir(parents=True)
    for fixture in data['fixtures']:
        sources = fixture['width_binding']['source_order']
        baseline = None
        for arm, zero in [('historical_nonzero', False), ('completed_zero', True)]:
            stem = fixture['uid']+'-'+arm
            with (args.out/(stem+'.events.jsonl')).open('x') as events:
                def event(record):
                    events.write(json.dumps(record, sort_keys=True)+'\n')
                    events.flush()
                try:
                    result = producer.collect(fixture, sources, event, include_zero=zero,
                                              capability=producer._NATIVE_CAPABILITY)
                except BaseException as error:
                    event(dict(kind='failure', error_type=type(error).__name__, error=str(error), complete=False))
                    raise
            if baseline is None:
                baseline = result
            else:
                # Same base/source/projection: compare new equations against the old kernel.
                from collect_width import project
                old = AffineRelations(fixture['r'], result['projection']['U'])
                for row in baseline['rows']:
                    old.add(*project(row, baseline['projection'], fixture['r']))
                result['old_kernel_syndromes'] = [list(old.identify(project(row, result['projection'], fixture['r'])[0]).syndrome)
                                                 for row in result['rows']]
            result['verification'] = check(fixture, sources, result)
            result['inputs_sha256'] = sha256(args.inputs.read_bytes()).hexdigest()
            with (args.out/(stem+'.json')).open('x') as stream:
                json.dump(result, stream, indent=2)
                stream.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
