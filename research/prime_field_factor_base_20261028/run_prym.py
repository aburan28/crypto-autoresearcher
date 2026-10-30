"""Run a source-bound paired zero-completion stream after canonical admission."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter, process_time

import prym_completion as producer
from check_prym import check
from crypto_autoresearcher.index_calculus.execution_gate import admit
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations


def write_once(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def phase(journal, fixture, arm, name, operation):
    """Keep diagnostic collection/replay cost and every failure separately."""
    started = datetime.now(timezone.utc).isoformat()
    wall, cpu = perf_counter(), process_time()
    record = dict(curve_uid=fixture['uid'], arm=arm, phase=name, started_at=started,
                  wall_valid=False, status='complete')
    try:
        return operation()
    except BaseException as error:
        record.update(status='failed', error_type=type(error).__name__, error=str(error))
        raise
    finally:
        record.update(finished_at=datetime.now(timezone.utc).isoformat(),
                      wall_seconds=perf_counter()-wall, cpu_seconds=process_time()-cpu)
        with journal.open('a') as stream:
            stream.write(json.dumps(record, sort_keys=True)+'\n')


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
    admission = admit(producer.ROOT, args.protocol, args.inputs,
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
    write_once(args.out/'admission.json', admission)
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
                    result = phase(args.out/'phases.jsonl', fixture, arm, 'collection',
                        lambda: producer.collect(fixture, sources, event, include_zero=zero,
                                                 capability=producer._NATIVE_CAPABILITY))
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
            result['inputs_sha256'] = sha256(args.inputs.read_bytes()).hexdigest()
            # Replay can fail or be interrupted: the complete collected stream
            # already exists, independently of a later verification artifact.
            write_once(args.out/(stem+'.json'), result)
            verification = phase(args.out/'phases.jsonl', fixture, arm, 'verification',
                                 lambda: check(fixture, sources, result))
            write_once(args.out/(stem+'.verification.json'), verification)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
