#!/usr/bin/env python3
"""
Reproduction-package harness: run one command as an immutable run record.

Creates  runs/<RUN-ID>/{manifest.yaml, command.txt, environment.json,
stdout.log, stderr.log, raw-result.json}  per docs/evidence-and-reproducibility.md.
Refuses to overwrite an existing run directory (run records are immutable; a
corrected run gets a NEW id).

usage: python3 run_harness.py RUN-ID RAW-RESULT-PATH TIMEOUT_SECONDS -- cmd args...
"""
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import time

TASK = 'TASK-20260823-01d3d9'
GOAL = 'GOAL-ECQ-002'
BATCH = 'BATCH-f2341e'
HYP = 'H-ECQ-d60d07'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.abspath(os.path.join(ROOT, '..', '..', '..', '..', '..', '..'))


def git(*args):
    return subprocess.run(['git'] + list(args), cwd=REPO, capture_output=True,
                          text=True).stdout.strip()


def main():
    run_id, raw_rel, timeout = sys.argv[1], sys.argv[2], int(sys.argv[3])
    assert sys.argv[4] == '--'
    cmd = sys.argv[5:]
    rundir = os.path.join(ROOT, 'runs', run_id)
    if os.path.exists(rundir):
        sys.exit('REFUSING to overwrite existing run record %s (runs are '
                 'immutable; use a new run id)' % rundir)
    os.makedirs(rundir)

    env = {
        'python': sys.version,
        'platform': platform.platform(),
        'machine': platform.machine(),
        'cpu_count': os.cpu_count(),
        'packages': {'cypari': __import__('cypari').__version__,
                     'pari_version': None},
        'stdlib_only_verifier': 'exact_certify.py uses fractions/math only',
        'inference': {
            'requested_policy': 'executor-implementation',
            'resolved_model_id': os.environ.get('AUTORESEARCH_RESOLVED_MODEL',
                                                'claude-opus-5'),
            'backend': os.environ.get('AUTORESEARCH_BACKEND', 'claude_code session'),
            'reasoning_effort': os.environ.get('AUTORESEARCH_EFFORT', 'medium'),
            'model_verified': False,
            'fallback_used': False,
            'degraded_requirements': [],
        },
    }
    try:
        import cypari
        env['packages']['pari_version'] = str(cypari.pari('version()'))
    except Exception:
        pass
    json.dump(env, open(os.path.join(rundir, 'environment.json'), 'w'), indent=1)
    open(os.path.join(rundir, 'command.txt'), 'w').write(
        ' '.join(cmd) + '\n(cwd: %s)\n' % os.path.dirname(os.path.abspath(__file__)))

    t0 = time.time()
    status = 'completed_valid'
    reason = ''
    with open(os.path.join(rundir, 'stdout.log'), 'w') as so, \
         open(os.path.join(rundir, 'stderr.log'), 'w') as se:
        try:
            p = subprocess.run(cmd, stdout=so, stderr=se, timeout=timeout,
                               cwd=os.path.dirname(os.path.abspath(__file__)))
            rc = p.returncode
            if rc != 0:
                status = 'invalid_measurement'
                reason = 'non-zero exit code %d' % rc
        except subprocess.TimeoutExpired:
            rc = None
            status = 'resource_exhaustion'
            reason = ('wall-clock limit %ds exceeded -- INFRASTRUCTURE outcome, '
                      'never mathematical evidence' % timeout)
    wall = time.time() - t0
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)

    raw_abs = os.path.join(ROOT, raw_rel) if raw_rel != '-' else None
    if raw_abs and os.path.exists(raw_abs):
        shutil.copyfile(raw_abs, os.path.join(rundir, 'raw-result.json'))
    elif raw_abs:
        json.dump({'note': 'producer wrote no raw result', 'status': status},
                  open(os.path.join(rundir, 'raw-result.json'), 'w'), indent=1)
        if status == 'completed_valid':
            status = 'invalid_measurement'
            reason = 'declared raw result missing'

    manifest = [
        'run:',
        '  id: %s' % run_id,
        '  task_id: %s' % TASK,
        '  goal_id: %s' % GOAL,
        '  batch_id: %s' % BATCH,
        '  hypothesis_id: %s' % HYP,
        '  started_utc: %s' % time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t0)),
        '  wall_clock_seconds: %.2f' % wall,
        '  max_rss_kb: %d' % ru.ru_maxrss,
        '  user_cpu_seconds: %.2f' % ru.ru_utime,
        '  exit_code: %s' % rc,
        '  status: %s' % status,
        '  status_reason: %s' % json.dumps(reason),
        '  git_commit: %s' % git('rev-parse', 'HEAD'),
        '  git_dirty: %s' % ('true' if git('status', '--porcelain') else 'false'),
        '  seeds: [20260823]   # only the random-sample control uses randomness',
        '  certificate:',
        '    kind: %s' % os.environ.get('RUN_CERT_KIND', 'rank_lower_bound'),
        '    verified_by: exact_certify.py (exact, stdlib-only, independent of '
        'the PARI search that produced the points)',
        '  budget:',
        '    wall_clock_limit_seconds: %d' % timeout,
        '  artifacts: [manifest.yaml, command.txt, environment.json, '
        'stdout.log, stderr.log, raw-result.json]',
    ]
    open(os.path.join(rundir, 'manifest.yaml'), 'w').write('\n'.join(manifest) + '\n')
    print('%s -> %s (%s, %.1fs)' % (run_id, rundir, status, wall))
    return 0 if status == 'completed_valid' else 1


if __name__ == '__main__':
    sys.exit(main())
