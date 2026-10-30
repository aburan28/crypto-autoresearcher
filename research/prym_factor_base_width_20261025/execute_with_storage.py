"""Fixed width experiment storage route around the frozen native delivery adapter.

Only module-instance destination/identity constants are rebound. Publisher,
storage_adapter, run, their fatal delivery behavior, and native admission remain
the frozen implementations. This file grants no launch authority.
"""
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXPERIMENT = 'EXP-ECDLP-a9b6a5'
RUN = 'RUN-ECDLP-967315'
DELIVERY = ROOT/f'experiments/{EXPERIMENT}/artifact-deliveries/{RUN}'
FROZEN_ADAPTER = ROOT/'research/prym_rank_census_20261025/storage-delivery-20261025/execute_with_storage.py'
FROZEN_ADAPTER_SHA256 = 'c5f1b06bfdf10f863c6635d61d5491922f157b87455e59fed48620757bc218c6'

if sha256(FROZEN_ADAPTER.read_bytes()).hexdigest() != FROZEN_ADAPTER_SHA256:
    raise RuntimeError('Frozen storage adapter source hash mismatch')
_spec = importlib.util.spec_from_file_location('prym_width_frozen_storage_adapter', FROZEN_ADAPTER)
_adapter = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _adapter
_spec.loader.exec_module(_adapter)
_adapter.EXPERIMENT = EXPERIMENT
_adapter.RUN = RUN
_adapter.DELIVERY = DELIVERY
_adapter.HERE = HERE

DeliveryFailure = _adapter.DeliveryFailure
Publisher = _adapter.Publisher
storage_adapter = _adapter.storage_adapter
run = _adapter.run
native = _adapter.native
artifact_store = _adapter.artifact_store


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['run', 'probe'])
    parser.add_argument('--plan', type=Path, default=ROOT/f'experiments/{EXPERIMENT}/trial-plan.json')
    parser.add_argument('--owner')
    parser.add_argument('--epoch', type=int)
    args = parser.parse_args(argv)
    os.environ.setdefault('CRYPTO_AR_BLOB_CACHE', '/tmp/prym-width-native-blob-cache')
    if args.mode == 'run':
        if not args.owner or args.epoch is None or args.epoch <= 0:
            parser.error('run needs owner and positive epoch')
        return run(args.plan, args.owner, args.epoch)
    # Future public-byte storage probe only, with separately configured identity;
    # no probe or network work is performed by import or software tests.
    result = _adapter.probe()
    _adapter.dump(HERE/'probe-result.json', result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except DeliveryFailure as error:
        print('Canonical storage impediment: '+str(error), file=sys.stderr)
        raise SystemExit(2)
