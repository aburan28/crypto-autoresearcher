#!/usr/bin/env python3
"""Build the separate legacy certificate checker; never execute it."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = HERE / 'attempts/checker-build-v1'
    out.mkdir(parents=True, exist_ok=False)
    parent = HERE / 'attempts/build-v4/result.json'
    build = json.loads(parent.read_text())
    work = Path(build['work_path'])
    compiler = build['compiler']
    env = dict(os.environ, ZIG_GLOBAL_CACHE_DIR=str(HERE / '.work/zig-global'), ZIG_LOCAL_CACHE_DIR=str(HERE / '.work/zig-local'))
    steps = []
    names = ['checknminus1', 'checkcllucas', 'checkcertif']
    status = 'incomplete'
    for name in names:
        command = compiler + ['-c', str(work / 'ECPP/Ecpp/C/c' / (name + '.c')), '-o', str(work / ('check-' + name + '.o'))]
        p = subprocess.run(command, env=env, capture_output=True, timeout=180)
        (out / (name + '.stdout')).write_bytes(p.stdout)
        (out / (name + '.stderr')).write_bytes(p.stderr)
        steps.append({'command': command, 'exit_code': p.returncode})
        if p.returncode:
            status = 'failed_compile'
            break
    else:
        objects = [work / ('check-' + n + '.o') for n in names]
        objects += [work / ('ec-' + n + '.o') for n in ('ecmodp', 'lfactor', 'cllucas', 'clroutines', 'fastsieve')]
        objects += sorted(work.glob('bm-*.o')) + sorted(work.glob('bn-*.o'))
        exe = work / 'checkcertif'
        command = compiler + ['-static'] + list(map(str, objects)) + ['-lm', '-o', str(exe)]
        p = subprocess.run(command, env=env, capture_output=True, timeout=300)
        (out / 'link.stdout').write_bytes(p.stdout)
        (out / 'link.stderr').write_bytes(p.stderr)
        steps.append({'command': command, 'exit_code': p.returncode})
        status = 'built_unexecuted' if p.returncode == 0 else 'failed_link'
    result = {'status': status, 'parent_build_sha256': sha(parent), 'script_sha256': sha(__file__), 'steps': steps}
    if status == 'built_unexecuted':
        result['executable_sha256'] = sha(exe)
    (out / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': status, 'steps': len(steps)}))
    raise SystemExit(0 if status == 'built_unexecuted' else 1)


if __name__ == '__main__':
    main()
