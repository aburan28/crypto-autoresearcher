"""Prospective canonical-storage adapter around the unchanged native supervisor.

Scientific launchers/checkers and all native admission checks are retained.
Offload completes before the native execution receipt is sealed. Credentials
are inherited only at runtime and are never written by this module.
"""
import argparse
from contextlib import contextmanager, redirect_stderr
from hashlib import sha256, shake_256
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'tools'))
import artifact_store
import experiment_execution as native

spec = importlib.util.spec_from_file_location('prym_canonical_artifacts', ROOT/'tools/artifacts/artifacts.py')
canonical = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = canonical
spec.loader.exec_module(canonical)

REMOTE = 's3://setec-astronomy-artifacts/store'
MINIMUM = 65537
EXPERIMENT = 'EXP-ECDLP-d6d8e8'
RUN = 'RUN-ECDLP-ea49a6'
DELIVERY = ROOT/f'experiments/{EXPERIMENT}/artifact-deliveries/{RUN}'


class DeliveryFailure(RuntimeError):
    """Fatal publication failure; deliberately not swallowed as optional offload."""


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


class Publisher:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.directory.relative_to(ROOT)
        self.cfg = canonical.Config.load(ROOT)
        if self.cfg.remote.rstrip('/') != REMOTE:
            raise DeliveryFailure('Canonical artifact destination mismatch')
        self.remote = canonical.Remote(self.cfg)
        self.entries = []

    def initialize(self):
        """Fixed output coverage even when no compressed artifact needs offload."""
        self.directory.mkdir(parents=True, exist_ok=True)
        if not (self.directory/'.artifacts.json').exists():
            canonical.write_manifest(self.directory, {})
        if not (self.directory/'.gitignore').exists():
            canonical.write_gitignore(self.directory, [])

    def command(self, *args):
        completed = subprocess.run([sys.executable, str(ROOT/'tools/artifacts/artifacts.py'), *map(str, args)],
                                   cwd=ROOT, capture_output=True, text=True)
        if completed.returncode:
            raise DeliveryFailure(f'Canonical artifact command {args[0]} failed (exit {completed.returncode})')
        return completed

    def put(self, source, expected):
        source = Path(source)
        if artifact_store.sha256_file(source) != expected:
            raise DeliveryFailure('Refusing forged stored-file digest')
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self.directory/(expected+'.bin')
        if target.exists() and artifact_store.sha256_file(target) != expected:
            raise DeliveryFailure('Existing delivery copy has different content')
        if not target.exists():
            shutil.copyfile(source, target)
        self.command('push', target)
        self.command('verify', self.directory, '--remote')
        manifest = json.loads((self.directory/'.artifacts.json').read_text())
        entry = manifest['files'][target.name]
        if entry['sha256'] != expected or entry['bytes'] != source.stat().st_size:
            raise DeliveryFailure('Canonical manifest does not bind the selected bytes')
        # A real fresh GET verifies content independently of the publisher cache.
        # Cache population afterward lets existing native readers use these same
        # verified bytes without requiring a second storage SDK in this session.
        cache = artifact_store.cache_dir()/'sha256'/expected[:2]/expected
        cache.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='prym-storage-readback-') as scratch:
            fetched = Path(scratch)/'object'
            try:
                with redirect_stderr(io.StringIO()):
                    self.remote.get(expected, fetched)
            except SystemExit as error:
                raise DeliveryFailure('Canonical object readback failed') from error
            if artifact_store.sha256_file(fetched) != expected or fetched.stat().st_size != entry['bytes']:
                raise DeliveryFailure('Canonical object readback digest/size mismatch')
            shutil.copyfile(fetched, cache)
        uri = REMOTE+'/sha256/'+expected[:2]+'/'+expected
        self.entries.append(dict(uri=uri, sha256=expected, bytes=entry['bytes'],
                                 manifest=str((self.directory/'.artifacts.json').relative_to(ROOT)),
                                 manifest_name=target.name, fresh_get_sha256_verified=True))
        return uri


@contextmanager
def storage_adapter(publisher):
    old_compact, old_factory = artifact_store.compact, artifact_store.store_from_env
    def strict_compact(directory, names, store=None, **kwargs):
        result = old_compact(directory, names, publisher, compress_min=MINIMUM, offload_min=MINIMUM)
        if any(entry.get('offload_error') for entry in result.values()):
            raise DeliveryFailure('Required canonical offload failed; native receipt must not be sealed')
        return result
    artifact_store.compact = strict_compact
    artifact_store.store_from_env = lambda: publisher
    try:
        yield
    finally:
        artifact_store.compact, artifact_store.store_from_env = old_compact, old_factory


def probe():
    directory = HERE/'probe-native'
    directory.mkdir(parents=True, exist_ok=True)
    source = directory/'payload.bin'
    payload = shake_256(b'prym-canonical-storage-positive-control-v1').digest(90000)
    with source.open('xb') as stream:
        stream.write(payload)
    publisher = Publisher(HERE/'probe-delivery')
    with storage_adapter(publisher):
        storage = artifact_store.compact(directory, ['payload.bin'])
    entry = storage['payload.bin']
    if not entry['path'].endswith('.blob.json'):
        raise DeliveryFailure('Positive storage control was not offloaded')
    if not artifact_store.stored_matches(directory, 'payload.bin', entry, sha256(payload).hexdigest()):
        raise DeliveryFailure('Native stored-form control did not match')
    if artifact_store.read_bytes(source) != payload:
        raise DeliveryFailure('Native reader roundtrip differs')
    return dict(probe='deterministic incompressible planted bytes; no relation data',
                content_bytes=len(payload), content_sha256=sha256(payload).hexdigest(),
                native_storage=entry, objects=publisher.entries, status='passed')


def historical():
    directory = ROOT/'experiments/EXP-ECDLP-cded08/runs/RUN-ECDLP-d25f6a'
    receipt = json.loads((directory/'execution-receipt.json').read_text())
    publisher = Publisher(HERE/'historical-W2')
    records = []
    for name in ['events.jsonl', 'raw-result.json']:
        source = directory/name
        content_sha = artifact_store.sha256_file(source)
        if content_sha != receipt['artifact_sha256'][name]:
            raise DeliveryFailure('Historical file differs from immutable native receipt')
        with tempfile.TemporaryDirectory(prefix='prym-historical-copy-') as scratch:
            packed = Path(scratch)/(name+'.gz')
            artifact_store.gzip_deterministic(source, packed)
            packed_sha = artifact_store.sha256_file(packed)
            if artifact_store.gunzip_digest(packed) != (content_sha, source.stat().st_size):
                raise DeliveryFailure('Historical compressed copy differs')
            uri = publisher.put(packed, packed_sha)
        if artifact_store.sha256_file(source) != content_sha:
            raise DeliveryFailure('Historical source changed during additive publication')
        records.append(dict(source=str(source.relative_to(ROOT)), content_sha256=content_sha,
                            content_bytes=source.stat().st_size, gzip_sha256=packed_sha,
                            uri=uri, original_unchanged=True))
    proof = dict(schema='prym-additive-historical-custody/v1', source_run='RUN-ECDLP-d25f6a',
                 source_receipt_sha256=artifact_store.sha256_file(directory/'execution-receipt.json'),
                 mode='additional exact-content delivery; original run files stay unchanged',
                 records=records, objects=publisher.entries)
    dump(HERE/'historical-W2/custody.json', proof)
    return proof


def run(plan, owner, epoch):
    plan = plan.resolve()
    bound = json.loads(plan.read_text())
    if (bound['experiment_id'] != EXPERIMENT or len(bound['trials']) != 1
            or bound['trials'][0]['run_id'] != RUN):
        raise DeliveryFailure('Adapter is restricted to the fixed census experiment/run')
    publisher = Publisher(DELIVERY)
    publisher.initialize()
    with storage_adapter(publisher):
        code = native.main(['run', '--repo', str(ROOT), '--plan', str(plan), '--owner', owner, '--epoch', str(epoch)])
    if code:
        return code
    run_dir = ROOT/f'experiments/{EXPERIMENT}/runs/{RUN}'
    receipt = json.loads((run_dir/'execution-receipt.json').read_text())
    if native.trial_state(ROOT, bound, bound['trials'][0], native.sha256(plan)) != 'output_validated':
        raise DeliveryFailure('Native post-seal trial state did not validate')
    proof = dict(schema='prym-census-storage-custody/v1', experiment_id=EXPERIMENT, run_id=RUN,
                 execution_receipt_sha256=artifact_store.sha256_file(run_dir/'execution-receipt.json'),
                 artifact_sha256=receipt['artifact_sha256'], artifact_storage=receipt['artifact_storage'],
                 objects=publisher.entries, offload_before_native_receipt=True,
                 fresh_object_readback_verified=True, scientific_interpretation='not assessed')
    dump(DELIVERY/'custody.json', proof)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['probe', 'historical', 'run'])
    parser.add_argument('--plan', type=Path, default=ROOT/f'experiments/{EXPERIMENT}/trial-plan.json')
    parser.add_argument('--owner')
    parser.add_argument('--epoch', type=int)
    args = parser.parse_args()
    os.environ.setdefault('CRYPTO_AR_BLOB_CACHE', '/tmp/prym-native-blob-cache')
    if args.mode == 'run':
        if not args.owner or not args.epoch:
            parser.error('run needs owner and positive epoch')
        return run(args.plan, args.owner, args.epoch)
    result = probe() if args.mode == 'probe' else historical()
    if args.mode == 'probe':
        dump(HERE/'probe-result.json', result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except DeliveryFailure as error:
        print('Canonical storage impediment: '+str(error), file=sys.stderr)
        raise SystemExit(2)
