#!/usr/bin/env python3
"""Offline runtime engineering controls. No named curve orders are accepted."""
import argparse
import gzip
import hashlib
import json
import os
import platform
import re
import stat
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / '.work/build-v4'
RUNTIME = HERE / '.work/qemu-runtime'
QEMU = '/opt/homebrew/bin/qemu-system-i386'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def cpio(entries):
    out = bytearray()
    for i, (name, mode, payload, major, minor) in enumerate(entries + [('TRAILER!!!', 0, b'', 0, 0)], 1):
        name = name.encode() + b'\0'
        fields = (i, mode, 0, 0, 1, 0, len(payload), 0, 0, major, minor, len(name), 0)
        out.extend(b'070701' + ''.join(f'{v:08x}' for v in fields).encode() + name)
        out.extend(b'\0' * (-len(out) % 4))
        out.extend(payload)
        out.extend(b'\0' * (-len(out) % 4))
    out.extend(b'\0' * (-len(out) % 512))
    return gzip.compress(bytes(out), mtime=0)


def image(init, program, args, payload=b'', data_mode=None, cpu_limit=30, stdin=b''):
    entries = []
    directories = {'dev', 'proc', 'tmp', 'ecpp', 'ecpp/Data'}
    data_files = []
    if data_mode:
        root = WORK / 'ECPP/Ecpp/Data'
        for p in sorted(root.rglob('*')):
            rel = 'ecpp/Data/' + p.relative_to(root).as_posix()
            if p.is_dir():
                directories.add(rel)
            elif p.is_file():
                if p.name == 'ecpp.DfD' and data_mode == 'missing':
                    continue
                data_files.append((rel, b'' if p.name == 'ecpp.DfD' and data_mode == 'empty' else p.read_bytes()))
    for name in sorted(directories, key=lambda x: (x.count('/'), x)):
        entries.append((name, stat.S_IFDIR | (0o1777 if name == 'tmp' else 0o755), b'', 0, 0))
    entries.append(('dev/console', stat.S_IFCHR | 0o600, b'', 5, 1))
    files = [('init', init, 0o555), ('program', program, 0o555),
             ('argv', ('\n'.join(['/program'] + args) + '\n').encode(), 0o444),
             ('input', payload, 0o444), ('stdin', stdin, 0o444),
             ('cpu_limit', str(cpu_limit).encode(), 0o444)]
    for name, blob, mode in files:
        entries.append((name, stat.S_IFREG | mode, blob, 0, 0))
    for name, blob in data_files:
        entries.append((name, stat.S_IFREG | 0o444, blob, 0, 0))
    return cpio(entries)


def vm(out, init, program, args, payload=b'', data_mode=None, stdin=b'', cpu_limit=30, host_limit=90):
    out.mkdir(parents=True, exist_ok=False)
    ramdisk = image(init, program, args, payload, data_mode, cpu_limit, stdin)
    # Bulky replay images stay on the data volume; raw output and bindings are durable.
    images = RUNTIME / 'images'
    images.mkdir(exist_ok=True)
    image_path = images / (sha(ramdisk) + '.cpio.gz')
    if not image_path.exists(): image_path.write_bytes(ramdisk)
    command = [QEMU, '-machine', 'pc,accel=tcg', '-cpu', 'max', '-m', '256', '-smp', '1',
               '-nodefaults', '-no-user-config', '-display', 'none', '-serial', 'stdio',
               '-monitor', 'none', '-nic', 'none', '-no-reboot',
               '-device', 'isa-debug-exit,iobase=0xf4,iosize=4',
               '-kernel', str(RUNTIME / 'vmlinuz-lts'), '-initrd', str(image_path),
               '-append', 'console=ttyS0 rdinit=/init panic=1 loglevel=3 random.trust_cpu=on']
    start = time.monotonic()
    record(out / 'started.json', {'utc': datetime.now(timezone.utc).isoformat(), 'command': command,
        'program_sha256': sha(program), 'init_sha256': sha(init), 'initramfs_sha256': sha(ramdisk),
        'input_sha256': sha(payload), 'stdin_sha256': sha(stdin), 'data_mode': data_mode,
        'guest_limit_seconds': cpu_limit, 'host_limit_seconds': host_limit})
    reason = None
    try:
        p = subprocess.run(command, capture_output=True, timeout=host_limit)
        code, stdout, stderr = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        code, stdout, stderr, reason = None, e.stdout or b'', e.stderr or b'', 'host_watchdog'
    (out / 'serial.raw').write_bytes(stdout)
    (out / 'qemu.stderr').write_bytes(stderr)
    text = stdout.replace(b'\r\n', b'\n').decode(errors='replace')
    exits = re.findall(r'^__ECPP_CHILD_EXIT__ (\d+) timeout=(\d+)$', text, re.M)
    valid = (code == 33 and reason is None and len(exits) == 1 and exits[0][1] == '0'
             and text.count('__ECPP_GUEST_BEGIN__\n') == 1
             and text.count('__ECPP_GUEST_COMPLETE__\n') == 1
             and '__ECPP_INIT_ABI__ 4 4 4\n' in text)
    child_code = int(exits[0][0]) if len(exits) == 1 else None
    body = text.split('__ECPP_GUEST_BEGIN__\n', 1)[-1].split('\n__ECPP_CHILD_EXIT__', 1)[0]
    (out / 'program.stdout').write_text(body)
    certs = re.findall(r'__ECPP_CERTIFICATE_BEGIN__\n(.*?)\n__ECPP_CERTIFICATE_END__', text, re.S)
    if len(certs) == 1: (out / 'certificate.cformat').write_text(certs[0])
    result = {'vm_valid': valid, 'qemu_exit': code, 'child_exit': child_code,
              'reason': reason, 'elapsed_host_seconds': time.monotonic() - start,
              'serial_sha256': sha(stdout), 'certificate_count': len(certs)}
    record(out / 'result.json', result)
    return result, body.encode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--attempt', required=True)
    ap.add_argument('--arithmetic-only', action='store_true')
    opt = ap.parse_args()
    assert re.fullmatch(r'[a-z0-9-]+', opt.attempt)
    out = HERE / 'attempts' / opt.attempt
    out.mkdir(exist_ok=False)
    summary = json.loads((HERE / 'summary.json').read_text())
    for item in summary['artifacts']:
        assert sha(Path(item['path']).read_bytes()) == item['sha256']
    kernel = json.loads((RUNTIME / 'kernel-receipt.json').read_text())
    assert sha((RUNTIME / 'vmlinuz-lts').read_bytes()) == kernel['kernel_sha256']
    compile_command = ['/opt/homebrew/bin/zig', 'cc', '-target', 'x86-linux-musl', '-static',
                       '-std=c11', '-O2', str(HERE / 'qemu_init.c'), '-o', str(RUNTIME / 'init')]
    env = dict(os.environ, ZIG_GLOBAL_CACHE_DIR=str(RUNTIME / 'zig-global'),
               ZIG_LOCAL_CACHE_DIR=str(RUNTIME / 'zig-local'), TMPDIR=str(RUNTIME))
    p = subprocess.run(compile_command, env=env, capture_output=True, timeout=180)
    (out / 'compile.stdout').write_bytes(p.stdout)
    (out / 'compile.stderr').write_bytes(p.stderr)
    record(out / 'started.json', {'scope': 'runtime engineering controls only', 'named_orders': 0,
        'script_sha256': sha(Path(__file__).read_bytes()), 'init_source_sha256': sha((HERE / 'qemu_init.c').read_bytes()),
        'protocol_sha256': sha((HERE / 'QEMU_CONTROL_PROTOCOL.md').read_bytes()),
        'kernel': kernel, 'qemu_version': subprocess.check_output([QEMU, '--version'], text=True).splitlines()[0],
        'host': platform.platform(), 'compile_command': compile_command, 'compile_exit': p.returncode})
    assert p.returncode == 0
    init = (RUNTIME / 'init').read_bytes()
    rows = []
    def run(name, exe, args, payload=b'', data_mode=None, stdin=b''):
        result, body = vm(out / name, init, (WORK / exe).read_bytes(), args, payload, data_mode, stdin)
        assert result['vm_valid'], (name, result)
        rows.append({'name': name, **result})
        print(json.dumps(rows[-1]), flush=True)
        return result, body
    old = HERE / 'attempts/arithmetic-v3'
    result, body = run('arithmetic', 'arithmetic_vectors_v3', [], stdin=(old / 'input.txt').read_bytes())
    assert result['child_exit'] == 0
    lines = body.decode().strip().splitlines()
    vectors = json.loads((old / 'fixture.json').read_text())
    assert lines[0] == 'ABI 4 4 4 4' and len(lines) == len(vectors) + 1
    for i, (line, vector) in enumerate(zip(lines[1:], vectors)):
        assert line.split() == ['ROW', str(i)] + vector['expected'], i
    if not opt.arithmetic_only:
        prover = [('prime101', 101, 'full', [], 'prime', 0),
                  ('prime65537', 65537, 'full', [], 'prime', 0),
                  ('composite15', 15, 'full', [], 'composite', 0),
                  ('composite341', 341, 'full', [], 'composite', 0),
                  ('cm-only101', 101, 'full', ['-nm', '-np'], 'prime', 0),
                  ('empty-catalog101', 101, 'empty', ['-nm', '-np'], 'composite', 0),
                  ('missing-catalog101', 101, 'missing', ['-nm', '-np'], None, 139)]
        for name, n, mode, extra, expectation, code in prover:
            result, body = run(name, 'runecpp', ['-l', '/ecpp/', '-f', '/input', '-Fc', '-C', '/tmp/certificate'] + extra,
                               str(n).encode() + b'\n', mode)
            labels = re.findall(rb'^(?:% )?This number is (prime|composite)\b.*$', body, re.M)
            assert [x.decode() for x in labels] == ([] if expectation is None else [expectation]), (name, labels)
            assert result['child_exit'] == code, (name, result)
        prime101 = (HERE / 'attempts/small-v1/prime-101/certificate.cformat').read_bytes()
        source = WORK / 'ECPP/Ecpp/C/Ex'
        fixtures = [('source-certif1', (source / 'certif1_c').read_bytes(), True),
            ('source-certif2', (source / 'certif2_c').read_bytes(), False),
            ('source-certif2-variant', (HERE / 'fixtures/certif2_variant_current_reader.cformat').read_bytes(), True),
            ('prime101-cert', prime101, True),
            ('prime65537-cert', (HERE / 'attempts/small-v1/prime-65537/certificate.cformat').read_bytes(), True),
            ('cm-only101-cert', (HERE / 'attempts/cm-only-v1/cm-only-101/certificate.cformat').read_bytes(), True),
            ('empty-cert', b'', False), ('truncated-cert', prime101[:8], False),
            ('mutated-root-cert', prime101.replace(b'101\n', b'105\n', 1), False)]
        from checker_controls_v2 import accepted
        for name, payload, expectation in fixtures:
            result, body = run(name, 'checkcertif', ['-f', '/input'], payload)
            (out / name / 'input.cformat').write_bytes(payload)
            assert accepted(result['child_exit'], body, payload) == expectation, name
    record(out / 'COMPLETE.json', {'status': 'passed', 'named_orders': 0, 'arithmetic_cases': 69,
        'exact_arithmetic_comparisons': 345, 'scope': 'runtime controls only', 'rows': rows,
        'prover_controls': 0 if opt.arithmetic_only else 7, 'checker_controls': 0 if opt.arithmetic_only else 9})
    print('CONTROLS_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
