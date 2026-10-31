#!/usr/bin/env python3
"""Run the original fixed n43/n44 D4 panel once, with per-input memory admission."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()


def available_bytes():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable missing')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'data', 'dossier', 'binary', 'count-binary', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text())
    original_path = args.data / 'expansion/plan.json'
    if sha(original_path) != plan['original_plan_sha256']:
        raise RuntimeError('original 190-input plan hash mismatch')
    if sha(args.binary) != plan['binary_sha256'] or sha(args.count_binary) != plan['count_binary_sha256']:
        raise RuntimeError('binary hash mismatch')
    source = args.dossier / 'submission-20261029'
    for name, expected in plan['source_sha256'].items():
        if sha(source / name) != expected:
            raise RuntimeError('source hash mismatch: ' + name)
    for name, expected in plan['dossier_sha256'].items():
        if sha(args.dossier / name) != expected:
            raise RuntimeError('dossier hash mismatch: ' + name)
    if sha(Path(__file__)) != plan['driver_sha256']:
        raise RuntimeError('driver hash mismatch')
    original = json.loads(original_path.read_text())
    ids = [item['id'] for item in original['items'] if item['degree'] == 4 and item['record']['n'] in (43, 44)]
    if len(ids) != 20 or ids != plan['ids']:
        raise RuntimeError('fixed n43/n44 input selection changed')
    by_id = {item['id']: item for item in original['items']}
    sys.path.insert(0, str(source))
    spec = importlib.util.spec_from_file_location('frozen_expand_instances', source / 'expand_instances.py')
    expansion = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(expansion)
    handles = []
    try:
        for path in plan['locks']:
            handle = Path(path).open('a')
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            handles.append(handle)
        args.out.mkdir(parents=True, exist_ok=False)
        summary = {'schema': 'semaev.expansion-resume-window/v1',
                   'plan_sha256': sha(args.plan), 'original_plan_sha256': plan['original_plan_sha256'],
                   'items': [], 'status': 'started'}
        save(args.out / 'started.json', summary)
        worker = SimpleNamespace(out=args.data / 'expansion', dossier=args.dossier,
                                 binary=args.binary, count_binary=args.count_binary,
                                 source_commit=plan['source_commit'],
                                 memory=plan['memory_bytes'], chunk=plan['chunk_rows'],
                                 timeout=plan['timeout_seconds'])
        try:
            for name in ids:
                root = args.data / 'expansion' / name
                if list(root.glob('attempt-*/result.json')):
                    raise RuntimeError(name + ': already terminal; reconcile before a second invocation')
                if list(root.glob('attempt-*')):
                    raise RuntimeError(name + ': partial attempt; recover before rerunning closure')
                free = available_bytes()
                gate = {'id': name, 'available_bytes': free,
                        'required_bytes': plan['memory_bytes'] + plan['reserve_bytes'],
                        'admitted': free >= plan['memory_bytes'] + plan['reserve_bytes']}
                save(args.out / f'{name}.gate.json', gate)
                if not gate['admitted']:
                    summary['status'] = 'capacity_paused'
                    break
                result = expansion.process(by_id[name], worker, plan['original_plan_sha256'])
                path = root / 'attempt-001/result.json'
                if not path.is_file():
                    raise RuntimeError(name + ': producer did not close attempt-001')
                row = {'id': name, 'status': result['status'], 'result_sha256': sha(path),
                       'inference_files': sorted(p.name for p in root.glob('inference-*.json'))}
                summary['items'].append(row)
                save(args.out / f'{name}.closed.json', row)
            else:
                summary['status'] = 'complete'
        except BaseException as exc:
            summary.update(status='failed', error=repr(exc))
            raise
        finally:
            save(args.out / 'terminal.json', summary)
    finally:
        for handle in handles:
            handle.close()
    print(json.dumps({'status': summary['status'], 'closed': len(summary['items'])}), flush=True)
    return int(summary['status'] == 'failed')


if __name__ == '__main__':
    raise SystemExit(main())
