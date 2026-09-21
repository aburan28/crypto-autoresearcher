#!/usr/bin/env python3
"""
Run-record writer for EXP-ECQ-0e0cbb.

Writes DIRECTLY to experiments/EXP-ECQ-0e0cbb/runs/RUN-<id>/ with
run.experiment_id set from the start, per EXP-ECQ-0e0cbb run_path_requirement.
No post-hoc port is possible from this path because no other path is offered.

The manifest carries the VALIDATOR'S schema -- run.{id, experiment_id, status,
code, environment, inputs, timing, result} -- so tools/validate_ledger.py
check_run() accepts it without any mapping shim.  Producer-local detail lives
inside those blocks, never instead of them.
"""
import json
import os
import platform
import subprocess
import sys
import time

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    *([os.pardir] * 8)))
EXP = 'EXP-ECQ-0e0cbb'
RUNS = os.path.join(ROOT, 'experiments', EXP, 'runs')
TASK = 'TASK-20260823-827765'
SEED = 20260823


def git_state():
    def g(*a):
        return subprocess.run(['git', '-C', ROOT] + list(a),
                              capture_output=True, text=True).stdout.strip()
    dirty = bool(g('status', '--porcelain'))
    return {'commit': g('rev-parse', 'HEAD'),
            'branch': g('rev-parse', '--abbrev-ref', 'HEAD'),
            'dirty_tree': dirty}


def environment():
    try:
        import cypari
        pari_ver = str(cypari.pari.pari_version()) if hasattr(
            cypari.pari, 'pari_version') else 'cypari-installed'
    except Exception as e:                                    # pragma: no cover
        pari_ver = 'unavailable: %s' % e
    try:
        import importlib.metadata as md
        cypari_ver = md.version('cypari')
    except Exception:
        cypari_ver = 'unknown'
    return {
        'python': sys.version.split()[0],
        'platform': platform.platform(),
        'machine': platform.machine(),
        'cpu_count': os.cpu_count(),
        'cypari_version': cypari_ver,
        'pari_version': pari_ver,
        'network_calls_made': 0,
        'network_policy': 'NO NETWORK CALL MADE; NOTHING SUBMITTED TO ICARM',
    }


class Run:
    """One run record.  Use as a context manager."""

    def __init__(self, run_id, purpose, command, parameters,
                 wall_clock_budget_s, hypothesis_id='H-ECQ-0ed5c8'):
        self.id = run_id
        self.dir = os.path.join(RUNS, run_id)
        os.makedirs(self.dir, exist_ok=True)
        self.purpose = purpose
        self.command = command
        self.parameters = dict(parameters)
        self.budget = wall_clock_budget_s
        self.hypothesis_id = hypothesis_id
        self.out_lines = []
        self.err_lines = []
        self.result = {}
        self.status = 'running'
        self.exit_code = None
        self.deviations = []
        self.t0 = None

    # ------------------------------------------------------------------
    def log(self, msg):
        line = '[%7.1fs] %s' % (time.time() - (self.t0 or time.time()), msg)
        self.out_lines.append(line)
        print(line, flush=True)

    def warn(self, msg):
        line = '[%7.1fs] WARN %s' % (time.time() - (self.t0 or time.time()), msg)
        self.err_lines.append(line)
        print(line, file=sys.stderr, flush=True)

    def elapsed(self):
        return time.time() - self.t0

    def budget_reached(self):
        return self.elapsed() > self.budget

    # ------------------------------------------------------------------
    def __enter__(self):
        self.t0 = time.time()
        self.log('RUN %s start -- %s' % (self.id, self.purpose))
        return self

    def __exit__(self, exc_type, exc, tb):
        wall = time.time() - self.t0
        if exc_type is not None:
            self.status = 'failed'
            self.exit_code = 1
            self.err_lines.append('%s: %s' % (exc_type.__name__, exc))
            self.result.setdefault('failure_class', 'implementation_error')
        else:
            self.exit_code = 0
            if self.status == 'running':
                self.status = 'completed_valid'
        self.write(wall)
        return False

    # ------------------------------------------------------------------
    def write(self, wall):
        d = self.dir
        with open(os.path.join(d, 'command.txt'), 'w') as fh:
            fh.write(self.command + '\n')
        with open(os.path.join(d, 'environment.json'), 'w') as fh:
            json.dump(environment(), fh, indent=1)
        with open(os.path.join(d, 'stdout.log'), 'w') as fh:
            fh.write('\n'.join(self.out_lines) + '\n')
        with open(os.path.join(d, 'stderr.log'), 'w') as fh:
            fh.write('\n'.join(self.err_lines) + '\n')
        with open(os.path.join(d, 'raw-result.json'), 'w') as fh:
            json.dump(self.result, fh, indent=1, default=str)
        env = environment()
        manifest = {'run': {
            'id': self.id,
            'experiment_id': EXP,
            'hypothesis_id': self.hypothesis_id,
            'task_id': TASK,
            'batch_id': 'BATCH-8b08ef',
            'goal_id': 'GOAL-ECQ-002',
            'status': self.status,
            'purpose': self.purpose,
            'code': {
                'commit': git_state()['commit'],
                'branch': git_state()['branch'],
                'dirty_tree': git_state()['dirty_tree'],
                'dirty_tree_note': 'the producer writes its deliverables and '
                                   'run records into the worktree, so the tree '
                                   'is dirty by construction; the Coordinator '
                                   'commits the frozen receipt',
                'command': self.command,
                'scripts_dir': 'coordination/goals/GOAL-ECQ-002/batches/'
                               'BATCH-8b08ef/tasks/%s/scripts' % TASK,
            },
            'environment': env,
            'inference': {
                'requested_policy': 'executor-implementation',
                'resolved_model': os.environ.get(
                    'AUTORESEARCH_MODEL', 'claude-opus-5 (session model; '
                    'AUTORESEARCH_MODEL unset in this session)'),
                'backend': os.environ.get('AUTORESEARCH_BACKEND',
                                          'unset in this session'),
                'policy_env': os.environ.get('AUTORESEARCH_POLICY',
                                             'unset in this session'),
                'fallback_used': False,
                'degraded': False,
            },
            'inputs': {
                'parameters': self.parameters,
                'seed': SEED,
                'randomness_sources': self.parameters.get(
                    'randomness_sources',
                    ['python random.Random(20260823) only; no other source']),
            },
            'timing': {
                'wall_clock_seconds': wall,
                'wall_clock_budget_seconds': self.budget,
                'time_budget_reached': wall > self.budget,
                'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                             time.gmtime(self.t0)),
                'finished_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                              time.gmtime()),
            },
            'result': dict(self.result, **{
                'exit_code': self.exit_code,
                'certificate': self.result.get('certificate',
                                               {'kind': 'none'}),
            }),
            'protocol_deviations': self.deviations,
        }}
        with open(os.path.join(d, 'manifest.yaml'), 'w') as fh:
            yaml.safe_dump(manifest, fh, sort_keys=False, width=100,
                           default_flow_style=False, allow_unicode=True)
