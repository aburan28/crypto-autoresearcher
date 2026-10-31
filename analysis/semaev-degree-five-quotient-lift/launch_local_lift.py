#!/usr/bin/env python3
"""Launch one frozen retained-seed lift with local admission and durable S3 checkpoints."""

import argparse
import fcntl
import json
from math import comb
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from launch_local_panel import save, sha, wait_for_memory


def validate_request_dimensions(request):
    variables = 2 * len(request['record']['V_basis_hex'])
    policy = request['disk_policy']
    if policy['N'] != variables:
        raise ValueError('disk_policy.N must equal the Boolean variable count 2k')
    seed_columns = sum(comb(variables, degree) for degree in range(policy['degree']))
    seed_words = (request['seed_codimension'] + 63) // 64
    if request['seed_bytes'] != 32 + 8 * seed_columns * (1 + seed_words):
        raise ValueError('seed size disagrees with frozen dimensions')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    protocol = json.loads(args.protocol.read_text())
    if protocol['freeze']['status'] != 'frozen' or sha(args.plan) != protocol['links']['plan_sha256']:
        raise ValueError('plan does not match frozen protocol')
    for name, digest in plan['hashes'].items():
        if sha(name) != digest:
            raise ValueError('pinned source mismatch: ' + name)
    request = json.loads(Path(plan['request']).read_text())
    validate_request_dimensions(request)
    root = Path(plan['output_root']).resolve()
    if request['memory_bytes'] != plan['memory_bytes']:
        raise ValueError('request/plan memory cap mismatch')
    if Path(request['disk_policy']['work_root']).resolve() != root:
        raise ValueError('request/plan work root mismatch')
    if request['disk_policy']['certificate_relative_path'] != 'attempt-001/certificate.bin':
        raise ValueError('unexpected certificate path')
    if not re.fullmatch(r's3://[a-z0-9][a-z0-9.-]+/[^\s]+', plan['checkpoint_prefix']):
        raise ValueError('invalid checkpoint prefix')
    root.mkdir(parents=True, exist_ok=False)
    locks = []
    try:
        for name in plan['locks']:
            handle = Path(name).open('a')
            locks.append(handle)
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        admission = wait_for_memory(plan, root)
        save(root/'admission.json', admission)
        if not admission['admitted']:
            return 73
        if sha(args.plan) != protocol['links']['plan_sha256']:
            raise ValueError('plan changed after admission')
        for name, digest in plan['hashes'].items():
            if sha(name) != digest:
                raise ValueError('pinned source changed after admission: ' + name)
        bundle = root/'bundle'
        shutil.copytree(plan['source_bundle'], bundle)
        argv = [plan['python'], str(bundle/'run_lift_worker_checkpoint.py'),
                '--bundle', str(bundle), '--request', plan['request'],
                '--protocol', str(args.protocol.resolve()), '--out', str(root/'attempt-001'),
                '--checkpoint-prefix', plan['checkpoint_prefix']]
        save(root/'launch.json', dict(argv=argv, unix_time=time.time(),
                                     protocol_sha256=protocol['freeze']['protocol_sha256'],
                                     plan_sha256=sha(args.plan)))
        with (root/'stdout').open('xb') as stdout, (root/'stderr').open('xb') as stderr:
            child = subprocess.Popen(argv, stdout=stdout, stderr=stderr,
                                     start_new_session=True,
                                     pass_fds=tuple(handle.fileno() for handle in locks))
            save(root/'child.json', dict(pid=child.pid, argv=argv))
            code = child.wait()
        save(root/'terminal.json', dict(returncode=code, unix_time=time.time()))
        return code
    finally:
        for handle in reversed(locks):
            handle.close()


if __name__ == '__main__':
    raise SystemExit(main())
