# Exact250-billion public-point campaign

Standalone, resumable point-distribution measurement for P-192/P-224 and125
ordinary-prime control models. No agent, private key or model API is required.
Read [PROTOCOL.md](PROTOCOL.md) for the exact samples,99.99% nominal families,
power assumptions and data-retention differences.

On Debian/Ubuntu, install `build-essential libssl-dev python3-venv`; create a
Python virtual environment and `pip install -r requirements.txt`. S3 credentials
come from the configured SDK/profile; never paste them into a command or source.
PARI GP is needed only to prepare new models; checked inputs are included.

Full compact data on S3:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python campaign.py --output /work/250b --storage s3 --bucket crypto-autoresearcher
```

Full compact data on a large filesystem (reserve~70 GB):

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python campaign.py --output /large/250b-metadata --storage filesystem --archive-root /large/250b-data
```

Explicit bounded aggregate mode:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python campaign.py --output /work/250b --storage aggregate
```

The October14 launch uses aggregate mode because full-data storage is unavailable:

```sh
cd /workspace/solinas-250b/tasks/solinas_250b
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /workspace/solinas-runtime/report-venv/bin/python campaign.py --output /workspace/solinas-250b/tasks/solinas_250b/runs/campaign-250b-20261014 --storage aggregate --workers 3
```

Aggregate mode preserves exact sufficient counts and fixed full-coordinate
witness/example samples, rather than every bit string for later ML searches.
The identical command resumes after interruption; source/config/storage changes
or record corruption are refused. Failed attempt files remain. Samples stop at
exactly250,000,000,000 observations; analysis starts only after complete checks.

For a machine that will remain active for days, detach normally:

```sh
nohup env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python campaign.py --output /work/250b --storage aggregate --workers 3 > /work/250b-console.log 2>&1 < /dev/null &
```

The machine's lifecycle still controls process survival. `status.json` records
completed jobs/points; sealed chunk records determine resume state. There are
no interim p-value decisions. A stop or loss of storage is not negative science.
Use `--max-new-jobs N` for a bounded invocation of the same global fixed plan;
it does not declare the incomplete study completed. Engineering checks use
different seeds and small inputs: `python -m unittest -v test_campaign`.

The new source uses the previously checked affine-bit sampler and adds bounded
transfer, checksum seals,125 matched control models and planned rarer-event
contrasts. This experiment makes no ECDLP-strength or attack-cost claim.
