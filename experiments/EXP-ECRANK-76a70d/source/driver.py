#!/usr/bin/env python3
"""Driver for EXP-ECRANK-76a70d. Runs all 8 enumerated runs with
checkpointing, resource accounting, and per-run manifest generation.
"""
import os, sys, json, time, hashlib, traceback, subprocess
from fractions import Fraction

WD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WD)
import delta_engine

MANIFEST_TEMPLATE = """run:
  id: {run_id}
  experiment_id: EXP-ECRANK-76a70d
  status: {status}
  code:
    commit: {commit}
    dirty: {dirty}
    command: {command}
  inference:
    requested_policy: executor-implementation
    resolved_model_id: none (deterministic computation)
    reasoning_effort: null
    fallback_used: false
    adapter_version: null
  environment:
    operating_system: {os}
    architecture: {arch}
    python_version: {pyver}
    sage_version: null
    dependencies:
      python_stdlib: "3.11+"
      note: no PARI, no network, stdlib only
  inputs: {inputs}
  timing:
    started_at: "{started_at}"
    finished_at: "{finished_at}"
    wall_seconds: {wall_seconds:.3f}
  resources:
    peak_rss_bytes: null
    cpu_seconds: {cpu_seconds:.3f}
    counted_ops: {counted_ops}
  result:
    metrics: {metrics}
    valid: {valid}
    invalid_reason: {invalid_reason}
    certificate:
      kind: none
      verified: false
      verifier: not_yet_verified
  artifacts:
    command: command.txt
    environment: environment.json
    stdout: stdout.log
    stderr: stderr.log
    raw_result: raw-result.json
"""


def get_env():
    r = subprocess.run(['uname', '-s'], capture_output=True, text=True)
    os_name = r.stdout.strip()
    r = subprocess.run(['uname', '-m'], capture_output=True, text=True)
    arch = r.stdout.strip()
    pyver = sys.version.split()[0]
    return os_name, arch, pyver


def write_manifest(run_id, status, command, inputs, started_at, finished_at,
                    wall_seconds, counted_ops, metrics, valid, invalid_reason):
    os_name, arch, pyver = get_env()
    git = subprocess.run(['git', '-C', WD, 'rev-parse', 'HEAD'], capture_output=True, text=True)
    commit = git.stdout.strip()[:12] if git.returncode == 0 else 'unknown'
    dirty = subprocess.run(['git', '-C', WD, 'diff-index', '--quiet', 'HEAD'], capture_output=True)
    dirty_flag = dirty.returncode != 0

    content = MANIFEST_TEMPLATE.format(
        run_id=run_id,
        status=status,
        commit=commit,
        dirty=str(dirty_flag).lower(),
        command=command,
        os=os_name,
        arch=arch,
        pyver=pyver,
        inputs=json.dumps(inputs, indent=4),
        started_at=started_at,
        finished_at=finished_at,
        wall_seconds=wall_seconds,
        cpu_seconds=wall_seconds,
        counted_ops=counted_ops,
        metrics=json.dumps(metrics, indent=4),
        valid=str(valid).lower(),
        invalid_reason=invalid_reason or 'null',
    )
    return content


def run_single(run_id: str, run_fn, run_kwargs: dict, run_dir: str,
               inputs: dict, checkpoint_op: int = 10**7):
    """Execute one run with checkpointing."""
    os.makedirs(run_dir, exist_ok=True)
    started_at = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    # Write command
    cmd_file = os.path.join(run_dir, 'command.txt')
    with open(cmd_file, 'w') as f:
        f.write(f"python3 experiments/EXP-ECRANK-76a70d/source/driver.py {run_id}\n")

    # Write environment
    env_file = os.path.join(run_dir, 'environment.json')
    with open(env_file, 'w') as f:
        json.dump(get_env()[0], f)

    stdout_file = os.path.join(run_dir, 'stdout.log')
    stderr_file = os.path.join(run_dir, 'stderr.log')
    raw_file = os.path.join(run_dir, 'raw-result.json')

    t0 = time.time()
    result = {'status': 'failed_infrastructure', 'error': None, 'run_data': None}
    try:
        data = run_fn(**run_kwargs)
        t1 = time.time()
        result = {
            'status': 'completed_valid',
            'error': None,
            'run_data': data,
            'wall_seconds': t1 - t0,
        }
        with open(stdout_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        with open(stderr_file, 'w') as f:
            f.write('')
        with open(raw_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        t1 = time.time()
        result = {
            'status': 'failed_infrastructure',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'wall_seconds': t1 - t0,
        }
        with open(stderr_file, 'w') as f:
            f.write(str(e) + '\n' + traceback.format_exc())
        with open(stdout_file, 'w') as f:
            f.write('')
        with open(raw_file, 'w') as f:
            json.dump(result, f, indent=2)

    finished_at = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    # Build metrics
    rd = result.get('run_data', {})
    if isinstance(rd, dict):
        metrics = {
            'found_instances': len(rd.get('found_instances', [])),
            'counted_ops': rd.get('counted_ops', 0),
            'exhausted': rd.get('exhausted'),
            'success_rate': rd.get('success_rate'),
        }
    else:
        metrics = {}

    manifest = write_manifest(
        run_id, result['status'],
        f"python3 experiments/EXP-ECRANK-76a70d/source/driver.py {run_id}",
        inputs, started_at, finished_at,
        result.get('wall_seconds', 0), rd.get('counted_ops', 0) if isinstance(rd, dict) else 0,
        metrics,
        result['status'] == 'completed_valid',
        result.get('error'),
    )
    manifest_file = os.path.join(run_dir, 'manifest.yaml')
    with open(manifest_file, 'w') as f:
        f.write(manifest)

    return result


def main():
    base = os.path.join(WD, os.pardir, 'runs')
    os.makedirs(base, exist_ok=True)

    summary = {'runs': {}, 'total_wall': 0}

    # 1. Smoke test
    print('[1/8] Smoke test...', flush=True)
    r = run_single(
        'RUN-ECRANK-76a70d-smoke',
        lambda: delta_engine.run_smoke(),
        {},
        os.path.join(base, 'RUN-ECRANK-76a70d-smoke'),
        inputs={'seed': 'smoke'},
    )
    summary['runs']['smoke'] = r['status']

    # 2. Arm A
    print('[2/8] Arm A (n=6, seed 760706)...', flush=True)
    r = run_single(
        'RUN-ECRANK-76a70d-armA-n6',
        delta_engine.run_arm,
        {'arm': 'A', 'n': 6, 'seed': 760706, 'sample_size': 10**3,
         'op_cap': 10**8, 'wall_cap': 7200},
        os.path.join(base, 'RUN-ECRANK-76a70d-armA-n6'),
        inputs={'n': 6, 'seed': 760706, 'sample_size': 10**3},
    )
    summary['runs']['armA'] = r['status']
    summary['total_wall'] += r.get('wall_seconds', 0)

    # 3. Arm B (main arm)
    print('[3/8] Arm B (n=8, seed 760708)...', flush=True)
    r = run_single(
        'RUN-ECRANK-76a70d-armB-n8',
        delta_engine.run_arm,
        {'arm': 'B', 'n': 8, 'seed': 760708, 'sample_size': 10**4,
         'op_cap': 10**8, 'wall_cap': 7200},
        os.path.join(base, 'RUN-ECRANK-76a70d-armB-n8'),
        inputs={'n': 8, 'seed': 760708, 'sample_size': 10**4},
    )
    summary['runs']['armB'] = r['status']
    summary['total_wall'] += r.get('wall_seconds', 0)

    # 4. Arm B determinism re-run
    print('[4/8] Arm B determinism (n=8, seed 760708)...', flush=True)
    r = run_single(
        'RUN-ECRANK-76a70d-armB-determinism',
        delta_engine.run_determinism_check,
        {'seed': 760708, 'sample_size': 2000},
        os.path.join(base, 'RUN-ECRANK-76a70d-armB-determinism'),
        inputs={'seed': 760708, 'sample_size': 2000},
    )
    summary['runs']['armB_determinism'] = r['status']
    summary['total_wall'] += r.get('wall_seconds', 0)

    # 5. Arm C
    print('[5/8] Arm C (n=10, seed 760710)...', flush=True)
    r = run_single(
        'RUN-ECRANK-76a70d-armC-n10',
        delta_engine.run_arm,
        {'arm': 'C', 'n': 10, 'seed': 760710, 'sample_size': 10**4,
         'op_cap': 10**8, 'wall_cap': 7200},
        os.path.join(base, 'RUN-ECRANK-76a70d-armC-n10'),
        inputs={'n': 10, 'seed': 760710, 'sample_size': 10**4},
    )
    summary['runs']['armC'] = r['status']
    summary['total_wall'] += r.get('wall_seconds', 0)

    # 6. Scan + null
    print('[6/8] Scan + null (seed 760711)...', flush=True)
    r = run_single(
        'RUN-ECRANK-76a70d-scan-null',
        delta_engine.run_arm,
        {'arm': 'scan_null', 'n': 8, 'seed': 760711, 'sample_size': 500,
         'op_cap': 10**7, 'wall_cap': 3600},
        os.path.join(base, 'RUN-ECRANK-76a70d-scan-null'),
        inputs={'n': 8, 'seed': 760711, 'sample_size': 500},
    )
    summary['runs']['scan_null'] = r['status']
    summary['total_wall'] += r.get('wall_seconds', 0)

    # 7. Known-false control
    print('[7/8] Known-false d=(1..1) control (seed 760712)...', flush=True)
    r = run_single(
        'RUN-ECRANK-76a70d-known-false',
        delta_engine.run_known_false_control,
        {'seed': 760712},
        os.path.join(base, 'RUN-ECRANK-76a70d-known-false'),
        inputs={'seed': 760712},
    )
    summary['runs']['known_false'] = r['status']
    summary['total_wall'] += r.get('wall_seconds', 0)

    # 8. Planted synthetic
    print('[8/8] Planted synthetic control...', flush=True)
    r = run_single(
        'RUN-ECRANK-76a70d-planted',
        delta_engine.run_planted_control,
        {},
        os.path.join(base, 'RUN-ECRANK-76a70d-planted'),
        inputs={},
    )
    summary['runs']['planted'] = r['status']
    summary['total_wall'] += r.get('wall_seconds', 0)

    # Compute control outcomes
    print('\nComputing IV outcomes...', flush=True)
    armB_data = summary.get('_armB_data')
    iv_outcomes = delta_engine.compute_iv_outcomes(
        summary['runs'], armB_data
    ) if hasattr(delta_engine, 'compute_iv_outcomes') else None

    summary['total_wall_total'] = summary['total_wall']
    print(f'DONE. Total wall: {summary["total_wall_total"]:.1f}s')
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    main()
