"""Export actual panel receipts; never fill absent observed identities from plans."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def export(directory, protocol_path, output):
    directory, protocol_path, output = Path(directory).resolve(), Path(protocol_path).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError('An export is write-once')
    tool = module(REPO/'tools/experiment_protocol.py', 'p256_canonical_export_tool')
    analysis_module = module(HERE/'analysis.py', 'p256_frozen_record_analysis')
    protocol = tool.read_json(protocol_path)
    errors = tool.schema_errors(protocol, 'experiment.protocol/v1') or tool.lint_protocol(protocol, protocol_path.parent)
    if errors or protocol['freeze']['status'] != 'frozen':
        raise ValueError('Protocol not valid and frozen: '+repr(errors))
    analysis_path = directory/'analysis.json'
    analysis_module.analyze(directory, analysis_path)
    metadata = tool.read_json(directory/'metadata.json')
    summary = tool.read_json(directory/'result.json')
    resources = tool.read_json(directory/'resources.json')
    prefix = os.path.relpath(directory, output.parent)
    export_id = summary['task']+'-'+directory.name
    e = tool.from_rows(directory/'rows.jsonl', protocol, os.path.relpath(protocol_path, output.parent),
                       export_id, {}, files_prefix=prefix if prefix != '.' else '')
    e['producer'] = metadata['producer']
    e['source'] = {'repo': protocol['repository'], 'commit': metadata['implementation_commit'],
                   'dirty': metadata['tracked_worktree_dirty']}
    e['backend'] = 'local'
    e['host'] = {'path': os.path.relpath(directory/'metadata.json', output.parent),
                 'sha256': tool.sha256_file(directory/'metadata.json'), 'class_id': 'shared-managed-host',
                 'summary': metadata['host']}
    for arm in e['arms']:
        arm['commit'] = metadata['implementation_commit']
        arm['binary_sha256'] = metadata['interpreter']['sha256']
    for row in e['runs']:
        row['measurements']['wall_seconds'] = None
        row['measurements']['wall_valid'] = False
        row['measurements']['cpu_user_seconds'] = None
        row['measurements']['cpu_sys_seconds'] = None
        row['measurements']['max_rss_bytes'] = resources['max_rss_bytes']
        # Exact native per-arm counters only. Shared process clocks remain in resources.json.
        row['measurements']['counters'] = {k: value for k, value in summary['arm_results'].get(row['arm'], {}).items()
                                            if isinstance(value, (int, float, str))}
        row['isolation'] = metadata['isolation']
        row['verification']['verifier'] = 'Native arithmetic control checks; raw checks.json retains per-arm coverage.'
        row['started_at'], row['finished_at'] = metadata['started_at'], resources['finished_at']
        row['worker'] = metadata['producer']['session']
    e['files'] = []
    for path in sorted(directory.rglob('*')):
        if path.is_file() and path not in (output, analysis_path):
            rel = os.path.relpath(path, output.parent)
            kind = 'host' if path.name == 'metadata.json' else 'summary' if path.name == 'result.json' else 'raw'
            e['files'].append({'path': rel, 'sha256': tool.sha256_file(path), 'bytes': path.stat().st_size, 'kind': kind})
    e['analysis'] = {'script': {'path': os.path.relpath(HERE/'analysis.py', output.parent),
                                'sha256': tool.sha256_file(HERE/'analysis.py')},
                     'blinded': False, 'blinding_key_sha256': None,
                     'outputs': [{'path': os.path.relpath(analysis_path, output.parent),
                                  'sha256': tool.sha256_file(analysis_path), 'bytes': analysis_path.stat().st_size,
                                  'kind': 'analysis'}], 'unmasked_at': None}
    e['notes'] = [{'kind': 'observation', 'by': '/root/pass2_geometry',
                  'text': 'Two actual arithmetic arms share one guarded process and setup. Clocks are diagnostic only; no method timing or population-yield inference.'}]
    errors = tool.schema_errors(e, 'experiment.export/v1') or tool.lint_export(e, protocol, output.parent, True)
    if errors:
        raise ValueError('Export refused: '+repr(errors))
    tool.write_once(output, e)
    print(tool.render_flow(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('--protocol', default=str(HERE/'protocol.json'))
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    export(args.directory, args.protocol, args.out)
