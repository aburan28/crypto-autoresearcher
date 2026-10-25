#!/usr/bin/env python3
"""Bounded engineering build; never invokes the produced executable."""
import hashlib
import io
import json
import os
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BN = ['bn/bnInit.c', 'bn/bnCmp.c', 'bn/bnMult.c', 'bn/bnDivide.c', 'KerN.c', 'bz.c']
BM = ['bntobnn', 'bztobzz', 'bnnmisc', 'mod', 'jacobi', 'gcd', 'exp', 'bzio', 'chinese', 'bmsmall', 'prprime', 'nextprime']
EC = ['ecpp', 'findd', 'cornacchia', 'hacks', 'factorm', 'fastsieve', 'ecppsieve', 'ecppio', 'certif', 'tactics', 'poly', 'rootdeg2', 'rootpoly', 'binroot', 'girstmair', 'proof', 'finde', 'findj', 'ecmodp', 'lfactor', 'ifactor', 'sieve', 'rho', 'pollard', 'lucaslehmer', 'nminus1', 'cllucas', 'clroutines', 'pratt']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    receipt = HERE / 'attempts/build-v2'
    receipt.mkdir(parents=True, exist_ok=False)
    work = HERE / '.work/build-v2'
    work.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env['ZIG_GLOBAL_CACHE_DIR'] = str(HERE / '.work/zig-global')
    env['ZIG_LOCAL_CACHE_DIR'] = str(HERE / '.work/zig-local')
    source = '/private/tmp/nist-ecpp.V3.4.1.tar.Z'
    assert digest(source) == '0387e7d180e570d0cf1ff957ed281a46711fb20d50ae0b0669a01a3464d9160f'
    payload = subprocess.check_output(['gzip', '-dc', source])
    with tarfile.open(fileobj=io.BytesIO(payload)) as arc:
        for m in arc.getmembers():
            if not m.isfile():
                continue
            path = (work / m.name).resolve()
            assert path.is_relative_to(work.resolve())
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(arc.extractfile(m).read())
    root = work / 'ECPP'
    includes = [root / 'Bigmod/h', root / 'Bignum/distrib/h', root / 'Ecpp/C/h']
    compiler = ['/opt/homebrew/bin/zig', 'cc', '-target', 'x86-linux-musl', '-std=gnu89', '-O0', '-fcommon', '-fwrapv', '-Wno-implicit-function-declaration', '-Wno-implicit-int', '-Wno-deprecated-non-prototype', '-Wno-int-conversion']
    compiler += ['-I' + str(p) for p in includes]
    steps = []
    result = {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'method': 'compatibility engineering build, no produced executable run', 'source_sha256': digest(source), 'build_script_sha256': digest(__file__), 'compiler_version': subprocess.check_output(['/opt/homebrew/bin/zig', 'version'], text=True).strip(), 'compiler': compiler, 'patches': [], 'amendment': 'Bigmod include directory first so bntobnn.h does not resolve to Bignum BntoBnn.h on a case-insensitive host; source bytes unchanged; build failures now exit nonzero', 'steps': steps, 'work_path': str(work), 'status': 'incomplete'}

    def call(cmd, label, timeout=180):
        begin = time.monotonic()
        try:
            proc = subprocess.run(cmd, env=env, capture_output=True, timeout=timeout)
            code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
            reason = None
        except subprocess.TimeoutExpired as e:
            code, stdout, stderr, reason = None, e.stdout or b'', e.stderr or b'', 'process watchdog'
        (receipt / (label + '.stdout')).write_bytes(stdout)
        (receipt / (label + '.stderr')).write_bytes(stderr)
        steps.append({'command': cmd, 'label': label, 'exit_code': code, 'reason': reason, 'elapsed_seconds': time.monotonic() - begin})
        return code == 0

    groups = [('bn', [root / 'Bignum/distrib/c' / f for f in BN]), ('bm', [root / 'Bigmod/c' / (n + '.c') for n in BM]), ('ec', [root / 'Ecpp/C/c' / (n + '.c') for n in EC])]
    objects = {}
    for group, sources in groups:
        objects[group] = []
        for src in sources:
            label = group + '-' + src.stem
            obj = work / (label + '.o')
            if not call(compiler + ['-c', str(src), '-o', str(obj)], label):
                result['status'] = 'failed_compile'
                result['failed_step'] = label
                (receipt / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
                print(json.dumps({'status': result['status'], 'failed_step': label, 'completed_steps': len(steps)}))
                raise SystemExit(1)
            objects[group].append(str(obj))
    control = work / 'arithmetic_control'
    if not call(compiler + ['-static', str(HERE / 'arithmetic_control.c')] + objects['bn'] + ['-lm', '-o', str(control)], 'link-arithmetic', 300):
        result['status'] = 'failed_link'
    else:
        executable = work / 'runecpp'
        obj = work / 'ec-runecpp.o'
        if call(compiler + ['-c', str(root / 'Ecpp/C/c/runecpp.c'), '-o', str(obj)], 'ec-runecpp') and call(compiler + ['-static', str(obj)] + objects['ec'] + objects['bm'] + objects['bn'] + ['-lm', '-o', str(executable)], 'link-runecpp', 300):
            result['status'] = 'built_unexecuted'
            result['artifacts'] = {str(p): digest(p) for p in (control, executable)}
        else:
            result['status'] = 'failed_link_or_caller_compile'
    (receipt / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'completed_steps': len(steps)}))
    raise SystemExit(0 if result['status'] == 'built_unexecuted' else 1)


if __name__ == '__main__':
    main()
