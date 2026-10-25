#!/usr/bin/env python3
"""Engineering checks only; fail closed and retain all diagnostics."""
import hashlib
import json
import os
import random
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    out = HERE / 'attempts/arithmetic-v3'
    out.mkdir(parents=True, exist_ok=False)
    build_path = HERE / 'attempts/build-v4/result.json'
    build = json.loads(build_path.read_text())
    assert build['status'] == 'built_unexecuted'
    work = Path(build['work_path'])
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', '--platform', 'linux/386', 'alpine:3.20']))[0]
    assert image['Architecture'] == '386' and image['Os'] == 'linux'
    engine = subprocess.check_output(['docker', 'info', '--format', '{{.ServerVersion}} {{.KernelVersion}} {{.OSType}} {{.Architecture}}'], text=True).strip()
    bits = [1, 2, 16, 31, 32, 33, 63, 64, 65, 127, 128, 191, 192, 223, 224, 238, 239, 255, 256, 383, 384, 520, 521]
    vectors = []
    rng = random.Random(0x1997)
    for k in bits:
        for a, b in ((2 ** k - 1, 2 ** max(1, k // 2) + 1), (2 ** k, 2 ** max(1, k // 2) - 1), (rng.getrandbits(k), rng.getrandbits(max(1, k - 1)) + 1)):
            q, r = divmod(a, b)
            vectors.append({'a': str(a), 'b': str(b), 'expected': list(map(str, (a + b, a - b, a * b, q, r)))})
    fixture = json.dumps(vectors, indent=2, sort_keys=True).encode() + b'\n'
    (out / 'fixture.json').write_bytes(fixture)
    stdin = ''.join(v['a'] + ' ' + v['b'] + '\n' for v in vectors).encode()
    (out / 'input.txt').write_bytes(stdin)
    env = dict(os.environ, ZIG_GLOBAL_CACHE_DIR=str(HERE / '.work/zig-global'), ZIG_LOCAL_CACHE_DIR=str(HERE / '.work/zig-local'))
    exe = work / 'arithmetic_vectors_v3'
    objects = sorted(str(p) for p in work.glob('bn-*.o'))
    command = build['compiler'] + ['-static', str(HERE / 'arithmetic_vectors.c')] + objects + ['-lm', '-o', str(exe)]
    proc = subprocess.run(command, env=env, capture_output=True, timeout=180)
    (out / 'compile.stdout').write_bytes(proc.stdout)
    (out / 'compile.stderr').write_bytes(proc.stderr)
    started = {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'method': 'compatibility arithmetic controls; no ECPP candidate trial', 'script_sha256': sha(Path(__file__).read_bytes()), 'control_source_sha256': sha((HERE / 'arithmetic_vectors.c').read_bytes()), 'protocol_sha256': sha((HERE / 'CONTROL_PROTOCOL.md').read_bytes()), 'build_receipt_sha256': sha(build_path.read_bytes()), 'fixture_sha256': sha(fixture), 'image_id': image['Id'], 'image_repo_digests': image.get('RepoDigests', []), 'engine': engine, 'compile_command': command, 'compile_exit': proc.returncode, 'cases': len(vectors)}
    (out / 'started.json').write_text(json.dumps(started, indent=2, sort_keys=True) + '\n')
    assert proc.returncode == 0
    docker = ['docker', 'run', '--rm', '--platform', 'linux/386', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--memory', '128m', '--cpus', '1', '--pids-limit', '64', '-i', '--mount', 'type=bind,src=' + str(work) + ',dst=/work,readonly', image['RepoDigests'][0], '/work/arithmetic_vectors_v3']
    begin = time.monotonic()
    run = subprocess.run(docker, input=stdin, capture_output=True, timeout=30)
    (out / 'run.stdout').write_bytes(run.stdout)
    (out / 'run.stderr').write_bytes(run.stderr)
    result = {'command': docker, 'exit_code': run.returncode, 'elapsed_seconds': time.monotonic() - begin, 'executable_sha256': sha(exe.read_bytes()), 'stdout_sha256': sha(run.stdout), 'status': 'unchecked'}
    (out / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    assert run.returncode == 0, run.stderr.decode(errors='replace')
    lines = run.stdout.decode().splitlines()
    assert lines[0] == 'ABI 4 4 4 4'
    assert len(lines) == len(vectors) + 1
    for i, (line, vector) in enumerate(zip(lines[1:], vectors)):
        fields = line.split()
        assert fields[:2] == ['ROW', str(i)]
        assert fields[2:] == vector['expected'], (i, fields, vector)
    complete = {'status': 'passed', 'scope': '32-bit ABI and five integer operations on the fixed vectors only', 'cases': len(vectors), 'exact_comparisons': len(vectors) * 5, 'result_sha256': sha((out / 'result.json').read_bytes()), 'fixture_sha256': sha(fixture)}
    (out / 'ARITHMETIC_COMPLETE.json').write_text(json.dumps(complete, indent=2, sort_keys=True) + '\n')
    print(json.dumps(complete, sort_keys=True))


if __name__ == '__main__':
    main()
