# Rare and higher-order Solinas point study

Public point-distribution measurements on P-192/P-224, with matched random
generators and random-field controls. See `PROTOCOL.md` and `config.json`.
No agent, GitHub credential, AWS key or model API is used by the scripts.

Linux prerequisites: Python 3.12+, C compiler, OpenSSL 3 development headers
and libcrypto. Install Python dependencies with `bash bootstrap.sh /path/to/venv`.

```sh
python research.py plan --output /path/to/new-run
python research.py batch --output /path/to/new-run --prior /path/to/cohorts-20261012 --workers 3
```

For the first run, `--prior` contains the previous immutable raw point dataset
and record shards. Later runs can reuse its derived features, included in the
completed higher-order dataset bundle, while generating genuinely new points:

```sh
python research.py batch --output /data/seed-002 --seed your-public-seed-002 --reuse-discovery /data/higher-order-20261012 --workers 3
```

Use a **new seed and a new output directory** for every independent batch.
The same command resumes only identical designs, checksums and sources. Stages
`discover`, `run`, `verify`, `analyze` can be invoked separately. The batch
stops on any failed job/check; preserve logs and fix code only in a new version
and a new output directory. Completed data and receipts are immutable.

Run on a schedule without agents, e.g. generate a deterministic batch number
in your scheduler, pass it as the public seed, and log stdout/stderr. Do not
overwrite a completed directory, stop because a p value looks favorable, or
pool repeated batches without a new prospective inference plan. Store raw
coordinates and checksum manifests in a filesystem/object store; lossless
JSONL feature shards support later statistical analyses without rescanning
billions of coordinate bytes. `archive.py` exports them and creates manifests.

Approximate Student/Welch intervals are clustered by actual block/field units.
Random generators and random starts are separate populations. The GF(2)
Hankel rank is a sequence descriptor, not elliptic-curve group rank. Exact
universal triple relations are arithmetic controls, not security findings.
