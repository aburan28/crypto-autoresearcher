"""Public targetwise ordered-count control at P37 transport vertex 24.

This reuses the fixed public 128-scalar control stream from the first P37 check.
It is excluded from discovery and confirmation inference.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PATH_TRANSPORT = HERE.parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(PATH_TRANSPORT))
import transport_count_control as prior

CP = PATH_TRANSPORT / 'controls' / 'p37-twoedge-attempt1'
TERMINAL = 24
SCHEMA = 'ectd-transport-count-control/v2'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare() -> dict:
    replay = prior.verify('P37', CP)
    if replay['status'] != 'pass' or replay['edges_checked'] != TERMINAL:
        raise ValueError('checkpoint extent or replay differs')
    walk = ROOT / 'research/isogeny_relation_yield_scan_20261016/walk-p37-256.jsonl'
    header = json.loads(walk.open(encoding='utf-8').readline())
    targets = prior.scalar_targets('P37', header['r'])
    records = {}
    for label, index in (('source', 0), ('transported', TERMINAL)):
        checkpoint = CP / f'edge-{index:04d}.json'
        record = json.loads(checkpoint.read_text())
        payload = prior.make_input(record, header['p'], header['r'], targets)
        output = HERE / f'{label}.txt'
        with output.open('xb') as stream:
            stream.write(payload)
        records[label] = {'checkpoint_index': index, 'checkpoint_sha256': sha(checkpoint),
                          'input_sha256': sha(output), 'j': record['model']['j']}
    result = {'schema': SCHEMA, 'stratum': 'P37', 'mode': 'public_implementation_control',
              'targets': len(targets), 'target_rule': 'same public scalar_targets(P37) as first check',
              'domain_utf8': prior.DOMAIN.decode(), 'checkpoints': records,
              'checkpoint_replay': replay, 'script_sha256': sha(Path(__file__)),
              'prior_control_script_sha256': sha(Path(prior.__file__)),
              'counter_source_sha256': sha(ROOT / 'research/conductor_relation_yield_20261014/count_verify.cpp')}
    with (HERE / 'manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
    return result


def compare() -> dict:
    manifest = json.loads((HERE / 'manifest.json').read_text())
    if manifest['schema'] != SCHEMA or manifest['script_sha256'] != sha(Path(__file__)):
        raise ValueError('manifest or producer hash differs')
    if manifest['prior_control_script_sha256'] != sha(Path(prior.__file__)):
        raise ValueError('public target rule dependency differs')
    if manifest['counter_source_sha256'] != sha(ROOT / 'research/conductor_relation_yield_20261014/count_verify.cpp'):
        raise ValueError('counter source differs')
    if prior.verify('P37', CP) != manifest['checkpoint_replay']:
        raise ValueError('checkpoint replay differs')
    parsed = {}
    for label in ('source', 'transported'):
        item = manifest['checkpoints'][label]
        checkpoint = CP / f'edge-{item["checkpoint_index"]:04d}.json'
        if sha(checkpoint) != item['checkpoint_sha256']:
            raise ValueError('checkpoint digest differs')
        record = json.loads(checkpoint.read_text())
        path = HERE / f'{label}.txt'
        if sha(path) != item['input_sha256'] or record['model']['j'] != item['j']:
            raise ValueError('prepared input identity differs')
        curve, base, targets = prior.parse_input(path)
        generator = tuple(record['generator'])
        prior.certify_group(curve, generator)
        if base != [tuple(point) for point in record['base']]:
            raise ValueError('base differs from checkpoint')
        q = prior.multiply(7, generator, curve)
        for alpha, beta, point in targets:
            if prior.add(prior.multiply(alpha, generator, curve), prior.multiply(beta, q, curve), curve) != point:
                raise ValueError('target equation differs')
        counts = prior.count_lines(HERE / f'{label}.count', curve, len(base), manifest['targets'])
        parsed[label] = ([(alpha, beta) for alpha, beta, _ in targets], counts)
    if parsed['source'][0] != parsed['transported'][0]:
        raise ValueError('coefficient stream differs')
    source, transported = parsed['source'][1], parsed['transported'][1]
    if source != transported:
        first = next(i for i, pair in enumerate(zip(source, transported)) if pair[0] != pair[1])
        raise ValueError(f'targetwise mismatch at {first}: {source[first]} != {transported[first]}')
    result = {'schema': 'ectd-transport-count-comparison/v2', 'stratum': 'P37',
              'destination_index': TERMINAL, 'targets_compared': len(source),
              'nonempty_targets': sum(x > 0 for x in source), 'total_ordered_relations': sum(source),
              'source_count_sha256': sha(HERE / 'source.count'),
              'transported_count_sha256': sha(HERE / 'transported.count'),
              'status': 'pass', 'scope': 'fixed public control, excluded from discovery inference'}
    with (HERE / 'comparison.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('prepare', 'compare'))
    command = parser.parse_args().command
    print(json.dumps(prepare() if command == 'prepare' else compare(), sort_keys=True))
