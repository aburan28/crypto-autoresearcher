"""Additive ECPP integration driver; importing this module executes no boundary.

The real route is deferred until a later admitted packet explicitly supplies its
admission callback. Synthetic callers must inject the entire legacy boundary.
Python driver streams are captured here; the frozen QEMU helper independently
uses subprocess capture_output for the child process streams. This wrapper is
synchronous and must not be used concurrently in one Python interpreter.
"""
from __future__ import annotations

import argparse
import contextlib
import gzip
import hashlib
import importlib.util
import json
import math
import os
import re
import stat
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
EXP = ROOT / 'experiments/EXP-NISTSEED-6886da'
COMPAT = ROOT / 'research/nist_seed_ecpp_compat_20261024'
DATA = COMPAT / '.work/build-v4/ECPP/Ecpp/Data'
MANIFEST = 'coordination/goals/GOAL-NISTSEED-ab8949/integration-admission-20261027/source-inputs.json'
MANIFEST_SHA256 = '47341a3e609a595e80c82042029377eec129dc9a29347bf75430e1e1d4339f62'
EXTRA_PINS = {
    'research/nist_seed_ecpp_compat_20261024/qemu_controls.py': '255b415ebf5a8eaa5514a02fbd0fb9886f27a2065f8686586a2c336e9f9372e7',
    'research/nist_seed_ecpp_compat_20261024/qemu_init.c': '1c5a2a11ecabf081a61fdf79f04ae343ea0348dbf7fa08d5ad1be738ca5e56e0',
    'research/nist_seed_ecpp_compat_20261024/guest_framing.py': 'ce4f7a8b320826c09d9b947d306883d83b695b83ebfc496ec1d3e38ca6a76bf5',
    'research/nist_seed_ecpp_compat_20261024/certificate_admission.py': '6cf50c95da246c7033dbb2cda8f8d70c07e2d5e366c1f1c9f163e7b115740c68',
    'experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_schema.json': 'c8f4f81ef3a092b3ea9360d568802b0b7e346245d02cae7e4f7a01e4af3d3087',
    'agents/executor.md': '89eda99ea575b966c5780762d2d13810fd6ed5abe1a5dc76a57ed51680784cc7',
    'agents/validator.md': '33947db8c7cc8663ac79f1eff4b183e75d0546915feb23e77654cd03a249c9d2',
    'orchestration/model-policies.yaml': 'a5a86d0e2be07f3c4e0ee67cfacad1cf667228046e832f24fb4e480ec0dc7a92',
    'tools/research_dispatch.py': '5919013342391e9b9ec30811c0f4c458e78030915c1afd8b799340b14fadb437',
}
SUPERVISOR = frozenset(('launch.json', 'environment.json', 'command.txt', 'stdout.log', 'stderr.log'))
PROVER_ARGV = ['/program', '-l', '/ecpp/', '-f', '/input', '-Fc', '-C', '/tmp/certificate']
CHECKER_ARGV = ['/program', '-f', '/input']
QEMU = '/opt/homebrew/bin/qemu-system-i386'
ENVELOPE = 'integration-envelope.json'
COUNTERS = 'counter-evidence.json'
RECOVERY = 'integration-recovery.json'
FAILURE = 'integration-failure.json'
BOUNDARY = 'integration-boundary-call.json'
MAX_JSON_BYTES = 16 * 1024 * 1024
PHASE_RULE = {
    'source': 'ECPP/Ecpp/C/c/ecpp.c',
    'source_sha256': '16766d2b73a5424b4252d0d75ba5a4346fae1d908ecc04eb7bca8bf1930071e2',
    'archive_sha256': '0387e7d180e570d0cf1ff957ed281a46711fb20d50ae0b0669a01a3464d9160f',
    'rule': '^% Starting phase (1: building the sequence of primes|2: proving)$',
    'scope': 'Printed original-program output signature; not proof of successful exec or complete computation.',
}


class Refusal(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def safe_path(path: Path) -> Path:
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise Refusal(f'symlink path or ancestor: {part}')
    return path.resolve(strict=False)


def read(path: Path) -> bytes:
    path = safe_path(path)
    if not path.is_file():
        raise Refusal(f'absent or nonregular file: {path}')
    return path.read_bytes()


def load(path: Path) -> Any:
    payload = read(path)
    if len(payload) > MAX_JSON_BYTES:
        raise Refusal(f'JSON exceeds bounded reader limit: {path}')
    return json.loads(payload.decode('utf-8'))


def write_json(path: Path, value: Any) -> None:
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def error_record(error: BaseException) -> dict[str, str]:
    return {'type': type(error).__name__, 'message': str(error)[:4096]}


def guarded(name: str, function: Callable[[], Any], errors: list[dict[str, Any]]) -> Any:
    try:
        return function()
    except BaseException as error:
        errors.append({'operation': name, **error_record(error)})
        return None


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Refusal(f'cannot load source module: {path}')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def source_pins() -> dict[str, str]:
    raw = read(ROOT / MANIFEST)
    if digest(raw) != MANIFEST_SHA256:
        raise Refusal('source manifest digest mismatch')
    manifest = json.loads(raw)
    if manifest.get('source_commit') != '4c7298e5212f523642c782483cd28f4bd5000d66' or len(manifest.get('inputs', [])) != 23:
        raise Refusal('source manifest identity mismatch')
    pins = {MANIFEST: MANIFEST_SHA256}
    for item in manifest['inputs']:
        relative, expected = item['path'], item['sha256']
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts or path.as_posix() != relative:
            raise Refusal('unsafe source manifest path')
        if relative in pins or digest(read(ROOT / relative)) != expected:
            raise Refusal(f'source binding mismatch: {relative}')
        pins[relative] = expected
    for relative, expected in EXTRA_PINS.items():
        if digest(read(ROOT / relative)) != expected:
            raise Refusal(f'additional source binding mismatch: {relative}')
        pins[relative] = expected
    return pins


def inventory(directory: Path) -> dict[str, str]:
    directory = safe_path(directory)
    if not directory.is_dir():
        raise Refusal(f'absent directory: {directory}')
    answer = {}
    for path in sorted(directory.rglob('*')):
        safe_path(path)
        if path.is_dir():
            continue
        if not path.is_file():
            raise Refusal(f'nonregular artifact: {path}')
        answer[path.relative_to(directory).as_posix()] = digest(read(path))
    return answer


def runtime_material(runtime: dict[str, Any]) -> dict[str, Any]:
    """Read and verify real runtime bytes; no executable module is imported."""
    blobs = {}
    for item in runtime['artifacts']:
        relative = Path(item['logical_path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise Refusal('unsafe runtime payload path')
        payload = read(ROOT / relative)
        if len(payload) != item['bytes'] or digest(payload) != item['sha256']:
            raise Refusal(f'runtime payload mismatch: {relative}')
        if relative.name in blobs:
            raise Refusal('duplicate runtime payload basename')
        blobs[relative.name] = payload
    kernel = read(COMPAT / '.work/qemu-runtime/vmlinuz-lts')
    if len(kernel) != runtime['kernel']['kernel_bytes'] or digest(kernel) != runtime['kernel']['kernel_sha256']:
        raise Refusal('real kernel mismatch')
    if inventory(DATA) != runtime['original_data']:
        raise Refusal('real original Data inventory mismatch')
    return {'blobs': blobs, 'kernel': kernel, 'catalog': DATA}


def image_bytes(material: dict[str, Any], stage: str, payload: bytes) -> bytes:
    """Pure reconstruction of the source-pinned helper's exact newc recipe."""
    proving = stage == 'prover'
    program = 'runecpp' if proving else 'checkcertif'
    argv = PROVER_ARGV if proving else CHECKER_ARGV
    seconds = 300 if proving else 30
    entries = []
    directories = {'dev', 'proc', 'tmp', 'ecpp', 'ecpp/Data'}
    data_files = []
    if proving:
        catalog = material['catalog']
        for path in sorted(catalog.rglob('*')):
            safe_path(path)
            relative = 'ecpp/Data/' + path.relative_to(catalog).as_posix()
            if path.is_dir():
                directories.add(relative)
            elif path.is_file():
                data_files.append((relative, read(path)))
            else:
                raise Refusal('nonregular original Data member')
    for name in sorted(directories, key=lambda value: (value.count('/'), value)):
        entries.append((name, stat.S_IFDIR | (0o1777 if name == 'tmp' else 0o755), b'', 0, 0))
    entries.append(('dev/console', stat.S_IFCHR | 0o600, b'', 5, 1))
    files = [('init', material['blobs']['qemu-init'], 0o555),
             ('program', material['blobs'][program], 0o555),
             ('argv', ('\n'.join(argv) + '\n').encode(), 0o444),
             ('input', payload, 0o444), ('stdin', b'', 0o444),
             ('cpu_limit', str(seconds).encode(), 0o444)]
    entries.extend((name, stat.S_IFREG | mode, body, 0, 0) for name, body, mode in files)
    entries.extend((name, stat.S_IFREG | 0o444, body, 0, 0) for name, body in data_files)
    out = bytearray()
    for ordinal, (name, mode, body, major, minor) in enumerate(entries + [('TRAILER!!!', 0, b'', 0, 0)], 1):
        encoded = name.encode() + b'\0'
        fields = (ordinal, mode, 0, 0, 1, 0, len(body), 0, 0, major, minor, len(encoded), 0)
        out.extend(b'070701' + ''.join(f'{number:08x}' for number in fields).encode() + encoded)
        out.extend(b'\0' * (-len(out) % 4))
        out.extend(body)
        out.extend(b'\0' * (-len(out) % 4))
    out.extend(b'\0' * (-len(out) % 512))
    return gzip.compress(bytes(out), mtime=0)


def expected_started(output: Path, stage: str, payload: bytes, runtime: dict[str, Any], material: dict[str, Any] | None, synthetic: dict[str, Any] | None) -> dict[str, Any]:
    if stage not in ('prover', 'checker'):
        raise Refusal('unknown stage')
    if synthetic is None:
        if material is None:
            raise Refusal('real runtime material unavailable')
        image_sha = digest(image_bytes(material, stage, payload))
    else:
        image_sha = synthetic['image_sha256'][stage]
        if re.fullmatch(r'[0-9a-f]{64}', image_sha) is None:
            raise Refusal('synthetic image identity malformed')
    cache = output / 'runtime-cache'
    command = [QEMU, '-machine', 'pc,accel=tcg', '-cpu', 'max', '-m', '256', '-smp', '1',
               '-nodefaults', '-no-user-config', '-display', 'none', '-serial', 'stdio',
               '-monitor', 'none', '-nic', 'none', '-no-reboot',
               '-device', 'isa-debug-exit,iobase=0xf4,iosize=4',
               '-kernel', str(cache / 'vmlinuz-lts'),
               '-initrd', str(cache / 'images' / (image_sha + '.cpio.gz')),
               '-append', 'console=ttyS0 rdinit=/init panic=1 loglevel=3 random.trust_cpu=on']
    payloads = {Path(item['logical_path']).name: item['sha256'] for item in runtime['artifacts']}
    proving = stage == 'prover'
    return {'command': command, 'program_sha256': payloads['runecpp' if proving else 'checkcertif'],
            'init_sha256': payloads['qemu-init'], 'initramfs_sha256': image_sha,
            'input_sha256': digest(payload), 'stdin_sha256': digest(b''),
            'data_mode': 'full' if proving else None,
            'guest_limit_seconds': 300 if proving else 30,
            'host_limit_seconds': 390 if proving else 90}


def frame_probe(serial: bytes) -> dict[str, Any]:
    """Strict source-shaped frame probe. Raw serial remains authoritative."""
    normalized = serial.replace(b'\r\n', b'\n')
    expressions = {
        'abi': rb'^__ECPP_INIT_ABI__ 4 4 4\n',
        'begin': rb'^__ECPP_GUEST_BEGIN__\n',
        'exit': rb'^__ECPP_CHILD_EXIT__ ([0-9]+) timeout=([0-9]+)\n',
        'complete': rb'^__ECPP_GUEST_COMPLETE__\n',
    }
    prefixes = {'abi': b'__ECPP_INIT_ABI__', 'begin': b'__ECPP_GUEST_BEGIN__',
                'exit': b'__ECPP_CHILD_EXIT__', 'complete': b'__ECPP_GUEST_COMPLETE__'}
    matches = {name: list(re.finditer(pattern, normalized, re.M)) for name, pattern in expressions.items()}
    if any(len(matches[name]) != 1 or normalized.count(prefixes[name]) != 1 for name in expressions):
        raise Refusal('absent, duplicate or malformed guest marker')
    abi, begin, exit_event, complete = (matches[name][0] for name in ('abi', 'begin', 'exit', 'complete'))
    if not abi.start() < begin.start() < exit_event.start() < complete.start():
        raise Refusal('misordered guest markers')
    if normalized[exit_event.start() - 1:exit_event.start()] != b'\n':
        raise Refusal('exit does not delimit a complete body')
    body = normalized[begin.end():exit_event.start() - 1]
    cert_begins = list(re.finditer(rb'^__ECPP_CERTIFICATE_BEGIN__\n', normalized, re.M))
    cert_ends = list(re.finditer(rb'^__ECPP_CERTIFICATE_END__\n', normalized, re.M))
    if len(cert_begins) != len(cert_ends) or len(cert_begins) > 1:
        raise Refusal('truncated or duplicate certificate frame')
    if normalized.count(b'__ECPP_CERTIFICATE_BEGIN__') != len(cert_begins) or normalized.count(b'__ECPP_CERTIFICATE_END__') != len(cert_ends):
        raise Refusal('malformed certificate marker')
    certificates = []
    if cert_begins:
        start, stop = cert_begins[0], cert_ends[0]
        if not exit_event.end() <= start.start() < stop.start() < complete.start():
            raise Refusal('misordered certificate markers')
        if normalized[stop.start() - 1:stop.start()] != b'\n':
            raise Refusal('truncated certificate body')
        certificates.append(normalized[start.end():stop.start() - 1])
    return {'body': body, 'certificates': certificates,
            'child_exit': int(exit_event.group(1)), 'timeout': int(exit_event.group(2))}


def recover_stage(output: Path, stage: str) -> dict[str, Any]:
    """Every secondary operation has a distinct bounded exception guard."""
    errors: list[dict[str, Any]] = []
    directory = output / 'legacy-child' / stage
    serial = guarded('read_serial', lambda: read(directory / 'serial.raw'), errors) if (directory / 'serial.raw').exists() else None
    status = guarded('parse_status', lambda: load(directory / 'result.json'), errors) if (directory / 'result.json').exists() else None
    started = guarded('parse_launch_intent', lambda: load(directory / 'started.json'), errors) if (directory / 'started.json').exists() else None
    framing = guarded('parse_framing', lambda: frame_probe(serial), errors) if serial is not None else None
    trace = None
    if serial is not None:
        trace_module = guarded('load_trace_extractor', lambda: module(EXP / 'integration/printed_trace.py', '_integration_runner_trace'), errors)
        if trace_module is not None:
            trace = guarded('derive_supplemental_trace', lambda: trace_module.extract(serial), errors)
    return {'serial': serial, 'status': status, 'started': started,
            'frame': framing, 'trace': trace, 'errors': errors}


def evidence(output: Path, path: Path, stage: str, kind: str, offset: int | None = None, length: int | None = None, source_rule: Any = None, synthetic: bool = False) -> dict[str, Any]:
    payload = read(path)
    return {'path': path.relative_to(output).as_posix(), 'sha256': digest(payload),
            'stage': stage, 'kind': kind, 'byte_offset': offset, 'byte_length': length,
            'source_rule': source_rule, 'synthetic': synthetic}


def stage_account(output: Path, stage: str, recovered: dict[str, Any], expected: dict[str, Any] | None, synthetic: bool) -> dict[str, Any]:
    serial, started, status, frame = (recovered[key] for key in ('serial', 'started', 'status', 'frame'))
    errors = list(recovered['errors'])
    proofs = []
    launch = False
    started_path = output / 'legacy-child' / stage / 'started.json'
    if started is not None:
        if not isinstance(started, dict) or expected is None:
            errors.append({'operation': 'launch_identity', 'type': 'Refusal', 'message': 'launch record or independently derivable input unavailable'})
        elif set(started) != set(expected) | {'utc'} or not isinstance(started['utc'], str) or not started['utc'] or any(started.get(key) != value for key, value in expected.items()):
            errors.append({'operation': 'launch_identity', 'type': 'Refusal', 'message': 'exact command/program/init/image/input/configuration/limits mismatch'})
        else:
            launch = True
            proofs.append(evidence(output, started_path, stage, 'launch_intent_before_subprocess', source_rule='qemu_controls.py: vm writes started.json before subprocess.run', synthetic=synthetic))
    guest = False
    program_output = False
    if serial is not None:
        path = output / 'legacy-child' / stage / 'serial.raw'
        abi = list(re.finditer(rb'^__ECPP_INIT_ABI__ 4 4 4\r?\n', serial, re.M))
        begin = list(re.finditer(rb'^__ECPP_GUEST_BEGIN__\r?\n', serial, re.M))
        guest = len(abi) == len(begin) == 1 and abi[0].start() < begin[0].start()
        for kind, events in (('guest_abi', abi), ('guest_init_begin_before_fork_exec', begin)):
            for event in events:
                proofs.append(evidence(output, path, stage, kind, event.start(), event.end() - event.start(), 'qemu_init.c: ABI and begin precede fork/execv', synthetic))
        if stage == 'prover':
            signatures = list(re.finditer(rb'^% Starting phase (?:1: building the sequence of primes|2: proving)\r?\n', serial, re.M))
            program_output = bool(signatures)
            for event in signatures:
                proofs.append(evidence(output, path, stage, 'source_backed_program_output', event.start(), event.end() - event.start(), PHASE_RULE, synthetic))
        proofs.append(evidence(output, path, stage, 'raw_serial_retained', synthetic=synthetic))
    status_ok = False
    if status is not None and frame is not None and serial is not None:
        elapsed = status.get('elapsed_host_seconds') if isinstance(status, dict) else None
        status_ok = (isinstance(status, dict) and type(status.get('vm_valid')) is bool
                     and type(status.get('qemu_exit')) is int and status['qemu_exit'] == 33
                     and type(status.get('child_exit')) is int and status['child_exit'] == frame['child_exit']
                     and status.get('reason') is None and frame['timeout'] == 0
                     and status.get('vm_valid') is True and status.get('serial_sha256') == digest(serial)
                     and type(status.get('certificate_count')) is int
                     and status['certificate_count'] == len(frame['certificates'])
                     and type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0)
        body_path = output / 'legacy-child' / stage / 'program.stdout'
        body = guarded('read_program_stdout', lambda: read(body_path), errors)
        status_ok = status_ok and body == frame['body']
        if not status_ok:
            errors.append({'operation': 'status_reconciliation', 'type': 'Refusal', 'message': 'complete frame, raw body and primitive status do not reconcile'})
        proofs.append(evidence(output, output / 'legacy-child' / stage / 'result.json', stage, 'retained_primitive_status', synthetic=synthetic))
    active = launch or guest or serial is not None
    return {'launch_intent': int(launch), 'guest_init_observed': int(guest),
            'program_output_observed': int(program_output),
            'stage_completed_success': int(status_ok and frame['child_exit'] == 0),
            'stage_completed_failure': int(status_ok and frame['child_exit'] != 0),
            'exact_program_starts': None,
            'program_start_observed_lower_bound': int(program_output),
            'program_start_unobserved_or_ambiguous': int(active and not program_output),
            'framing_state': 'COMPLETE' if frame is not None else 'UNAVAILABLE' if serial is None else 'MALFORMED',
            'status_state': 'UNAVAILABLE' if status is None else 'RECONCILED' if status_ok else 'UNRECONCILED',
            'errors': errors, 'evidence': proofs}


def cache_check(output: Path, material: dict[str, Any] | None, recovered: dict[str, Any], payload: bytes, synthetic: dict[str, Any] | None) -> dict[str, Any]:
    cache = output / 'runtime-cache'
    if synthetic is not None:
        if cache.exists():
            raise Refusal('synthetic boundary must not create a real runtime cache')
        return {'state': 'SYNTHETIC_NO_RUNTIME_CACHE', 'sha256': {}}
    if not cache.exists():
        return {'state': 'ABSENT', 'sha256': {}}
    if material is None:
        raise Refusal('real cache lacks verified runtime material')
    expected = {'vmlinuz-lts': digest(material['kernel'])}
    for stage in ('prover', 'checker'):
        item = recovered[stage]
        if item['started'] is None:
            continue
        stage_payload = payload
        if stage == 'checker':
            prover_frame = recovered['prover']['frame']
            if prover_frame is None or len(prover_frame['certificates']) != 1:
                raise Refusal('checker cache cannot be reconstructed without one exact certificate')
            stage_payload = prover_frame['certificates'][0]
        image = image_bytes(material, stage, stage_payload)
        expected['images/' + digest(image) + '.cpio.gz'] = digest(image)
    actual = inventory(cache)
    if actual != expected:
        raise Refusal('real private cache exact kernel/image inventory mismatch')
    return {'state': 'VERIFIED_RECONSTRUCTIBLE', 'sha256': actual}


def validate_synthetic(profile: dict[str, Any] | None) -> dict[str, Any] | None:
    if profile is None:
        return None
    if not isinstance(profile, dict) or set(profile) != {'scope', 'catalog_directory', 'image_sha256'}:
        raise Refusal('synthetic profile schema mismatch')
    if profile['scope'] != 'EXPLICIT_SYNTHETIC_FIXTURE_ONLY' or set(profile['image_sha256']) != {'prover', 'checker'}:
        raise Refusal('synthetic profile identity mismatch')
    for value in profile['image_sha256'].values():
        if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{64}', value) is None:
            raise Refusal('synthetic image digest malformed')
    catalog = safe_path(Path(profile['catalog_directory']))
    if not catalog.is_dir() or catalog == DATA.resolve(strict=False):
        raise Refusal('synthetic trace catalogue must be a distinct explicit fixture directory')
    return {'scope': profile['scope'], 'catalog_directory': str(catalog), 'image_sha256': dict(profile['image_sha256'])}


def deferred_real_boundary(index: int, child: Path, cache: Path) -> dict[str, Any]:
    """Complete deferred real execution seam; never selected by imports or tests.

    run_trial requires the later packet's admission callback before choosing this
    seam. The frozen V9 implementation owns execution and its existing limits.
    """
    source_pins()
    frozen = module(EXP / 'implementation/cohort_runner.py', '_integration_deferred_v9')
    return frozen._default_legacy_call(index, child, cache)


def run_trial(index: int, output: Path, binding: Path, capture_directory: Path, *, legacy_call: Callable[[int, Path, Path], dict[str, Any]] | None = None, synthetic_profile: dict[str, Any] | None = None, real_admission: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Run one exact frozen index and finalize its additive custody envelope.

    A future real caller supplies real_admission, which must perform that
    packet's external protocol/approval/ready-state checks and return its bound
    receipt. This function does not grant or manufacture scientific authority.
    Synthetic callers supply both an explicit profile and whole-boundary fake.
    """
    if type(index) is not int or not 0 <= index < 21:
        raise Refusal('cohort index outside [0,20]')
    pins = source_pins()
    v9 = module(EXP / 'implementation/cohort_runner.py', '_integration_runner_v9')
    frozen = v9.verify_frozen()
    rows, runtime = v9.load_cohort()
    prior = v9.prior_mapping(rows)
    output, binding, capture = safe_path(output), safe_path(binding), safe_path(capture_directory)
    if output == capture or output.is_relative_to(capture) or capture.is_relative_to(output):
        raise Refusal('capture and supervisor directories are equal or nested')
    if binding.is_relative_to(output) or binding.is_relative_to(capture):
        raise Refusal('external binding must be outside output and capture directories')
    if not output.is_dir() or capture.exists() or not capture.parent.is_dir():
        raise Refusal('output must exist and capture destination must be fresh with an existing parent')
    if output.stat().st_uid != os.geteuid() or capture.parent.stat().st_uid != os.geteuid():
        raise Refusal('output or capture parent is not owned by the current user')
    external = v9.verify_supervisor(output, binding, index, frozen)
    if external.get('driver_capture_directory') != str(capture):
        raise Refusal('external binding does not declare the exact distinct driver capture directory')
    supervisor_before = {name: digest(read(output / name)) for name in sorted(SUPERVISOR)}
    binding_sha = digest(read(binding))
    profile = validate_synthetic(synthetic_profile)
    mode = 'synthetic' if profile is not None else 'real'
    material = None if profile is not None else runtime_material(runtime)
    authorization = None
    if profile is not None:
        if legacy_call is None or legacy_call is deferred_real_boundary:
            raise Refusal('synthetic execution requires an injected whole-boundary fake')
        v9.DATA = Path(profile['catalog_directory'])
    else:
        if real_admission is None:
            raise Refusal('real execution requires the later admitted packet callback')
        request = {'index': index, 'row': rows[index], 'binding_sha256': binding_sha,
                   'output_directory': str(output), 'capture_directory': str(capture),
                   'source_pins': pins, 'runtime': runtime, 'limits': v9.LIMITS,
                   'primary_configuration': v9.PRIMARY, 'prover_argv': PROVER_ARGV,
                   'checker_argv': CHECKER_ARGV}
        authorization = real_admission(request)
        required = {'protocol_sha256', 'approval_decision', 'ready_receipt_sha256', 'request_sha256'}
        if not isinstance(authorization, dict) or set(authorization) != required:
            raise Refusal('real admission callback did not return an exact bound admission receipt')
        if authorization['request_sha256'] != canonical(request) or not isinstance(authorization['approval_decision'], str) or not authorization['approval_decision']:
            raise Refusal('real admission receipt is not bound to this exact request')
        if any(not isinstance(authorization[key], str) or re.fullmatch(r'[0-9a-f]{64}', authorization[key]) is None for key in ('protocol_sha256', 'ready_receipt_sha256', 'request_sha256')):
            raise Refusal('real admission receipt digest malformed')
    boundary = legacy_call if legacy_call is not None else deferred_real_boundary
    capture.mkdir(mode=0o700)
    boundary_attempts = 0
    boundary_exceptions = []
    original_error = None
    recovery_errors: list[dict[str, Any]] = []
    finalization_errors: list[dict[str, Any]] = []
    recovered: dict[str, Any] = {}
    returned = None

    def counted_boundary(selected: int, child: Path, cache: Path):
        nonlocal boundary_attempts
        if boundary_attempts:
            raise Refusal('one-index wrapper refuses a repeated boundary call')
        boundary_attempts += 1
        write_json(output / BOUNDARY, {'schema': 'crypto.autoresearch.nistseed_ecpp_boundary_call.v1',
                                     'cohort_index': selected, 'mode': mode,
                                     'evidence_kind': 'whole_boundary_call_attempt_not_program_start'})
        try:
            return boundary(selected, child, cache)
        except BaseException as error:
            boundary_exceptions.append(error_record(error))
            raise

    # These handles initially live outside the five-file supervisor directory.
    # Frozen real child subprocesses retain their own capture_output mechanism.
    with (capture / 'stdout.log').open('x', encoding='utf-8', errors='backslashreplace') as stdout_capture, (capture / 'stderr.log').open('x', encoding='utf-8', errors='backslashreplace') as stderr_capture:
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            try:
                returned = v9.run_trial(index, output, binding, counted_boundary)
            except BaseException as error:
                original_error = error_record(error)
            finally:
                for stage in ('prover', 'checker'):
                    recovered[stage] = guarded('recover_' + stage, lambda stage=stage: recover_stage(output, stage), recovery_errors)
                stdout_capture.flush()
                stderr_capture.flush()
    # Both driver handles are closed before logs enter the trial directory.
    for source_name, destination_name in (('stdout.log', 'driver.stdout.log'), ('stderr.log', 'driver.stderr.log')):
        try:
            with (output / destination_name).open('xb') as target:
                target.write(read(capture / source_name))
        except BaseException as error:
            finalization_errors.append({'operation': 'place_' + destination_name, **error_record(error)})
    payload = (rows[index]['n'] + '\n').encode('ascii')
    serial_recovery = {}
    supplemental = {'schema': 'crypto.autoresearch.nistseed_ecpp_supplemental_trace.v1', 'stages': {}}
    stage_counters = {}
    for stage in ('prover', 'checker'):
        item = recovered.get(stage)
        if item is None:
            item = {'serial': None, 'status': None, 'started': None, 'frame': None, 'trace': None, 'errors': [{'operation': 'stage_recovery', 'type': 'Unavailable', 'message': 'outer recovery guard caught an error'}]}
            recovered[stage] = item
        serial = item['serial']
        frame = item['frame']
        serial_recovery[stage] = {
            'serial_sha256': digest(serial) if serial is not None else None,
            'serial_bytes': len(serial) if serial is not None else None,
            'strict_frame_available': frame is not None,
            'strict_body_sha256': digest(frame['body']) if frame is not None else None,
            'strict_certificate_sha256': [digest(cert) for cert in frame['certificates']] if frame is not None else None,
            'status_available': item['status'] is not None, 'errors': item['errors'],
        }
        if item['trace'] is not None:
            supplemental['stages'][stage] = {'raw_path': f'legacy-child/{stage}/serial.raw',
                                             'raw_sha256': digest(serial), 'printed_trace': item['trace']}
        expected = None
        stage_payload = payload
        if stage == 'checker':
            prover_frame = recovered['prover']['frame']
            stage_payload = prover_frame['certificates'][0] if prover_frame is not None and len(prover_frame['certificates']) == 1 else None
            retained_input = output / 'legacy-child/prover/certificate.cformat'
            if stage_payload is None and retained_input.exists():
                stage_payload = guarded('read_retained_checker_input', lambda: read(retained_input), recovery_errors)
        if stage_payload is not None:
            expected = guarded('expected_' + stage + '_identity', lambda stage=stage, stage_payload=stage_payload: expected_started(output, stage, stage_payload, runtime, material, profile), recovery_errors)
        stage_counters[stage] = guarded('account_' + stage, lambda stage=stage, item=item, expected=expected: stage_account(output, stage, item, expected, profile is not None), recovery_errors)
    counter_record = {
        'schema': 'crypto.autoresearch.nistseed_ecpp_integration_counters.v1', 'mode': mode,
        'selected_cohort_indices': [index],
        'boundary_calls_attempted': {'synthetic': boundary_attempts if profile is not None else 0,
                                     'real': boundary_attempts if profile is None else 0},
        'boundary_evidence_path': BOUNDARY if boundary_attempts else None,
        'boundary_evidence_sha256': digest(read(output / BOUNDARY)) if boundary_attempts else None,
        'legacy_selected_work_field': {'path': 'raw-result.json', 'field': 'named_orders_executed',
                                       'value': returned.get('named_orders_executed') if isinstance(returned, dict) else None,
                                       'meaning': 'frozen selected-work literal; never a program-start count'},
        'stages': stage_counters, 'certificate_admitted': None,
        'certificate_admission_state': 'DEFERRED_TO_INDEPENDENT_CHECKER',
        'exact_program_start_total': None,
        'synthetic_evidence_contributes_to_real_execution_totals': False,
    }
    guarded('write_counter_record', lambda: write_json(output / COUNTERS, counter_record), finalization_errors)
    guarded('write_recovery_record', lambda: write_json(output / RECOVERY, {
        'schema': 'crypto.autoresearch.nistseed_ecpp_integration_recovery.v1',
        'original_exception': original_error, 'boundary_exceptions': boundary_exceptions, 'stages': serial_recovery,
        'secondary_errors': recovery_errors,
        'scope': 'Raw retention and bounded recovery; no substitute V9 success or raw envelope is created.'}), finalization_errors)
    if supplemental['stages']:
        guarded('write_supplemental_trace', lambda: write_json(output / 'supplemental-trace.json', supplemental), finalization_errors)
    cache_state = guarded('verify_private_cache', lambda: cache_check(output, material, recovered, payload, profile), finalization_errors)
    capsule_result = None
    capsule_module = guarded('load_capsule_helper', lambda: module(EXP / 'integration/capsule.py', '_integration_runner_capsule'), finalization_errors)
    if capsule_module is not None:
        capsule_result = guarded('create_raw_capsule', lambda: capsule_module.create(output), finalization_errors)
    supervisor_after = guarded('rehash_supervisor', lambda: {name: digest(read(output / name)) for name in sorted(SUPERVISOR)}, finalization_errors)
    if supervisor_after != supervisor_before:
        finalization_errors.append({'operation': 'supervisor_equality', 'type': 'Refusal', 'message': 'one or more supervisor files changed during driver execution/finalization'})
    if original_error is not None or recovery_errors or finalization_errors:
        # The original V9 failure.json and every other V9 envelope stay untouched.
        guarded('write_integration_failure', lambda: write_json(output / FAILURE, {
            'schema': 'crypto.autoresearch.nistseed_ecpp_integration_failure.v1',
            'classification': 'INDETERMINATE', 'original_exception': original_error,
            'boundary_exceptions': boundary_exceptions, 'recovery_errors': recovery_errors, 'finalization_errors': finalization_errors,
            'capsule_constructed': capsule_result is not None,
            'scientific_admission': False}), finalization_errors)
    sidecars = {}
    for path in sorted(output.iterdir()):
        if path.name in SUPERVISOR or path.name == ENVELOPE:
            continue
        if path.name in ('legacy-child', 'runtime-cache') and path.is_dir() and not path.is_symlink():
            continue
        if path.is_symlink() or not path.is_file():
            finalization_errors.append({'operation': 'outer_inventory', 'type': 'Refusal', 'message': 'unexpected nonregular outer artifact: ' + path.name})
            continue
        body = guarded('bind_sidecar_' + path.name, lambda path=path: read(path), finalization_errors)
        if body is not None:
            sidecars[path.name] = {'bytes': len(body), 'sha256': digest(body)}
    result = {
        'schema': 'crypto.autoresearch.nistseed_ecpp_integration.v1',
        'mode': mode, 'cohort_index': index,
        'identity': {'source_pins': pins, 'frozen_input_sha256': frozen, 'curve': rows[index],
                     'ordered_cohort': rows, 'prior_primality_mapping': prior,
                     'runtime': runtime, 'limits': v9.LIMITS, 'primary_configuration': v9.PRIMARY,
                     'prover_argv': PROVER_ARGV, 'checker_argv': CHECKER_ARGV},
        'external_binding': {'path': str(binding), 'sha256': binding_sha},
        'supervisor_artifact_sha256': supervisor_before,
        'capture_directory': str(capture),
        'synthetic_profile': profile,
        'real_admission_receipt': authorization,
        'runtime_cache': cache_state,
        'sidecars': sidecars,
        'finalization': {'state': 'COMPLETE' if capsule_result is not None and not finalization_errors else 'INCOMPLETE',
                         'errors': list(finalization_errors),
                         'capsule': 'raw-artifacts.tar.gz' if capsule_result is not None else None,
                         'inventory': 'raw-artifact-inventory.json' if capsule_result is not None else None},
        'claim_scope': 'Engineering custody envelope; independent checking and later research review determine admissibility.',
    }
    write_json(output / ENVELOPE, result)
    return result


def render_report(task_directory: Path) -> None:
    """Pure rendering entry point; call only after the PDF operation marker.

    Root supplies actual IMPLEMENTATION_REPORT.md, test-report.txt and the SVG
    rendered from custody.dot. This function launches no process and performs no
    experiment. Root renders and visually inspects every resulting PDF page.
    """
    from html import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
    from svglib.svglib import svg2rlg
    task_directory = safe_path(task_directory)
    report = read(task_directory / 'IMPLEMENTATION_REPORT.md').decode('utf-8')
    tests = read(task_directory / 'test-report.txt').decode('utf-8')
    drawing = svg2rlg(str(task_directory / 'custody.svg'))
    if drawing is None or drawing.width <= 0 or drawing.height <= 0:
        raise Refusal('custody SVG could not be rendered')
    scale = min(6.8 * inch / drawing.width, 4.4 * inch / drawing.height, 1)
    drawing.scale(scale, scale)
    drawing.width *= scale
    drawing.height *= scale
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 9
    styles['BodyText'].leading = 12
    styles['Code'].fontSize = 6
    styles['Code'].leading = 8
    story = [Paragraph('ECPP integration: source and guarded synthetic controls', styles['Title']),
             Paragraph('TASK-20261027-275b12 | EXP-NISTSEED-6886da | GOAL-NISTSEED-ab8949', styles['BodyText']),
             Spacer(1, 12), drawing, Spacer(1, 12)]
    for paragraph in report.split('\n\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        style = styles['Heading2'] if paragraph.startswith('#') else styles['BodyText']
        story.extend((Paragraph(escape(paragraph.lstrip('# ').replace('\n', ' ')), style), Spacer(1, 6)))
    story.append(Paragraph('Actual retained test receipt', styles['Heading2']))
    for line in tests.splitlines():
        # Wrap long native receipt lines without discarding any characters.
        chunks = [line[offset:offset + 112] for offset in range(0, len(line), 112)] or ['']
        story.append(Preformatted('\n'.join(chunks), styles['Code']))
    def footer(canvas, document):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor('#475569'))
        canvas.setFont('Helvetica', 8)
        canvas.drawString(0.65 * inch, 0.35 * inch, 'Engineering observations; no scientific state transition')
        canvas.drawRightString(7.85 * inch, 0.35 * inch, str(document.page))
        canvas.restoreState()
    document = SimpleDocTemplate(str(task_directory / 'report.pdf'), pagesize=(8.5 * inch, 11 * inch),
                                 rightMargin=0.65 * inch, leftMargin=0.65 * inch,
                                 topMargin=0.55 * inch, bottomMargin=0.65 * inch)
    document.build(story, onFirstPage=footer, onLaterPages=footer)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Explicit-fake quiet integration CLI or report renderer; no public real execution CLI.')
    parser.add_argument('--explicit-fake', action='store_true')
    parser.add_argument('--workspace', type=Path)
    parser.add_argument('--render-report', type=Path)
    args = parser.parse_args(argv)
    if args.render_report is not None:
        if args.explicit_fake or args.workspace is not None:
            return 2
        render_report(args.render_report)
        return 0
    if not args.explicit_fake or args.workspace is None:
        return 2
    # The only executable CLI fixture is the new test module beside this file.
    # No compatibility CLI or caller-selected module path can be selected.
    try:
        fixture = module(HERE / 'test_integration.py', '_integration_explicit_fake_cli')
        result = fixture.quiet_cli(safe_path(args.workspace))
        return 0 if result is True else 1
    except BaseException:
        # No traceback or JSON is written to the supervisor's outer streams.
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
