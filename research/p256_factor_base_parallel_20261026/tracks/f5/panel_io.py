"""Guarded observation I/O. Imports collect no arithmetic observations."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
STUDY = HERE.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO, text=True).strip()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def begin(args, task):
    protocol_path = HERE/'protocol.json'
    protocol = json.loads(protocol_path.read_text())
    frozen = protocol.get('freeze', {})
    raw = {k: v for k, v in protocol.items() if k != 'freeze'}
    canonical = json.dumps(raw, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()
    if frozen.get('status') != 'frozen' or frozen.get('protocol_sha256') != digest(canonical):
        raise RuntimeError('An intact frozen protocol is required before observation data')
    if args.seed != protocol['extensions']['fixed_seed']:
        raise RuntimeError('Seed differs from the prospectively fixed panel seed')
    implementation_commit = protocol['arms'][0]['instrument']['commit']
    if not implementation_commit:
        raise RuntimeError('Protocol instrument commit is not pinned')
    source_paths = [HERE/name for name in ['run.py', 'field.py', 'panel_io.py', 'analysis.py', 'export.py']]
    if (HERE/'balanced.py').is_file():
        source_paths.append(HERE/'balanced.py')
    sources = []
    for path in source_paths:
        rel = str(path.relative_to(REPO))
        committed = subprocess.check_output(['git', 'show', implementation_commit+':'+rel], cwd=REPO)
        actual = path.read_bytes()
        if committed != actual:
            raise RuntimeError('Current source differs from pinned implementation: '+rel)
        sources.append({'path': rel, 'bytes': len(actual), 'sha256': digest(actual),
                        'verified_against_commit': implementation_commit})
    inputs = []
    for record in protocol['extensions']['input_files']:
        path = REPO/record['path']
        data = path.read_bytes()
        if digest(data) != record['sha256'] or len(data) != record['bytes']:
            raise RuntimeError('Frozen input bytes differ: '+record['path'])
        inputs.append({'path': record['path'], 'bytes': len(data), 'sha256': digest(data)})
    gate_module = load_module(STUDY/'runtime/checkpoint_gate.py', 'p256_checkpoint_gate')
    gate = gate_module.require_gate(REPO, args.release, protocol, task)
    out = Path(args.out).resolve()
    if out.exists():
        raise FileExistsError('Refusing to overwrite earlier attempt: '+str(out))
    out.mkdir(parents=True)
    # Two GiB protects the shared host; it is not a research budget.
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
    binary = Path(sys.executable).resolve()
    cpu = next((line.split(':', 1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines()
                if line.startswith('model name')), None)
    mem = next((int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines()
                if line.startswith('MemTotal:')), None)
    metadata = {
        'task': task, 'started_at': now(), 'command': [sys.executable, *sys.argv],
        'implementation_commit': implementation_commit, 'runtime_head': git('rev-parse', 'HEAD'),
        'tracked_worktree_dirty': bool(git('status', '--porcelain', '--untracked-files=no')),
        'source_files': sources, 'input_files': inputs,
        'gate_helper_sha256': digest((STUDY/'runtime/checkpoint_gate.py').read_bytes()),
        'interpreter': {'path': str(binary), 'sha256': digest(binary.read_bytes()),
                        'python': platform.python_version()},
        'host': {'cpu_model': cpu, 'logical_cpus': os.cpu_count(), 'memory_bytes': mem,
                 'kernel': platform.release(), 'hypervisor': None, 'isolation_tier_max': 'none'},
        'isolation': {'tier': 'none', 'contended': None, 'blockers': ['shared managed host; no isolated timing claim']},
        'checkpoint_gate': gate, 'release_path': str(Path(args.release).resolve()),
        'release_sha256': digest(Path(args.release).read_bytes()),
        'protocol_sha256': frozen['protocol_sha256'],
        'producer': {'runtime': 'native Codex subagent', 'model': None,
                     'session': '/root/pass2_geometry', 'role': 'executor-implementation'},
        'model_policy_note': 'Inherited native model binding unprobed; canonical admission not claimed.',
    }
    write_once(out/'metadata.json', metadata)
    return out, protocol, metadata


class Panel:
    def __init__(self, out):
        self.out = out
        self.checks = []
        self.cases = []
        self.case_arms = {}
        self.active_arm = 'candidate'
        self.arm_results = {}

    def set_arm(self, arm):
        if arm not in ('candidate', 'reference'):
            raise ValueError('Unknown arm')
        self.active_arm = arm

    def mark_arm(self, arm, values):
        if arm in self.arm_results:
            raise ValueError('Arm already completed')
        self.arm_results[arm] = dict(values)

    def check(self, condition, name):
        row = {'name': name, 'passed': bool(condition), 'arm': self.active_arm}
        self.checks.append(row)
        if not condition:
            raise AssertionError(name)

    def case(self, name, data):
        if name in self.cases:
            raise ValueError('Duplicate case identity')
        self.cases.append(name)
        self.case_arms[name] = self.active_arm
        write_once(self.out/'cases'/(name+'.json'), data)


def run_main(callback, task, metric_names):
    parser = argparse.ArgumentParser(description='Frozen exact panel; root Phase B release and actual S3 gate required.')
    parser.add_argument('--out', required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--release', default=str(STUDY/'runtime/releases'/(task+'.json')))
    args = parser.parse_args()
    try:
        out, protocol, metadata = begin(args, task)
    except Exception as exc:
        print(type(exc).__name__+': '+str(exc), file=sys.stderr)
        return 2
    panel = Panel(out)
    started = time.monotonic()
    status, error, values = 'succeeded', None, {}
    try:
        values = callback(panel, args.seed)
        if not isinstance(values, dict) or values.pop('_completion_sentinel', None) != task:
            raise RuntimeError('Panel ended without its final completion sentinel')
    except Exception as exc:
        status, error = 'failed', {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
        values = {}
    elapsed = time.monotonic()-started
    usage = resource.getrusage(resource.RUSAGE_SELF)
    write_once(out/'checks.json', panel.checks)
    summary = {'schema': 'p256-second-pass-panel/v1', 'task': task, 'status': status,
               'seed': args.seed, 'cases': panel.cases, 'case_files': len(panel.cases),
               'assertions_passed': sum(c['passed'] for c in panel.checks),
               'assertions_failed': sum(not c['passed'] for c in panel.checks),
               'values': values, 'arm_results': panel.arm_results, 'case_arms': panel.case_arms, 'error': error, 'scope': 'exact fixed-panel observations; no ECDLP advantage or official transition',
               'finished_at': now()}
    write_once(out/'result.json', summary)
    rows = []
    for arm in ['candidate', 'reference']:
        completed = arm in panel.arm_results
        if completed:
            arm_status, verification = 'succeeded', 'verified'
        elif status == 'failed' and panel.active_arm == arm:
            arm_status, verification = 'failed', 'error'
        else:
            arm_status, verification = 'cancelled', 'not_run'
        if status == 'failed' and error and 'completion sentinel' in error['message']:
            arm_status, verification = 'failed', 'error'
        row = {'run_id': task+'-'+out.name+'-'+arm, 'arm': arm, 'instance_id': '0',
               'seed': args.seed, 'replicate': 0, 'warmup': False, 'status': arm_status,
               'verification': verification,
               'assertions_passed': sum(c['passed'] and c['arm'] == arm for c in panel.checks),
               'case_files': sum(owner == arm for owner in panel.case_arms.values()),
               'wall_seconds': None, 'tier': 'none'}
        for metric in metric_names:
            value = panel.arm_results.get(arm, {}).get(metric)
            if isinstance(value, (int, float, str)):
                row[metric] = value
        rows.append(row)
    with (out/'rows.jsonl').open('x') as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True)+'\n')
    write_once(out/'resources.json', {'wall_seconds': elapsed, 'wall_valid': False,
               'cpu_user_seconds': usage.ru_utime, 'cpu_sys_seconds': usage.ru_stime,
               'max_rss_bytes': usage.ru_maxrss*1024, 'finished_at': summary['finished_at']})
    print(json.dumps({'task': task, 'status': status, 'cases': len(panel.cases),
                      'assertions_passed': summary['assertions_passed'], 'out': str(out)}))
    return 0 if status == 'succeeded' else 1
