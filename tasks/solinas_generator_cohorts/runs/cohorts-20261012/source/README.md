# Portable Solinas point-distribution cohorts

Run on Linux with Python 3.10+, a C compiler, and OpenSSL development headers.
No model, agent, API key, GitHub connection, or network is used during a batch.
All curve/field inputs are bundled. Scripts use public deterministic scalars;
this measures geometry and sequences, with no target logs or key recovery.

On Debian/Ubuntu, install `python3-venv build-essential libssl-dev`, then:

```bash
bash bootstrap.sh
bash run_batch.sh /large-filesystem/ec-study/batch-0001 batch-0001 3
```

The same command resumes after interruption. For a new independent seed:

```bash
bash run_batch.sh /large-filesystem/ec-study/batch-0002 batch-0002 3
```

Individual stages and a data-volume preview:

```bash
.venv/bin/python research.py plan --output /large-filesystem/ec-study/batch-0001
.venv/bin/python research.py run --output /large-filesystem/ec-study/batch-0001 --seed batch-0001 --workers 3
.venv/bin/python research.py verify --output /large-filesystem/ec-study/batch-0001
.venv/bin/python research.py analyze --output /large-filesystem/ec-study/batch-0001
```

Default: 46,399,488 exact point pairs, roughly 2.41 GB raw coordinates per
batch, plus JSON/CSV metadata. Each standard curve gets two generator cohorts,
each with 10,485,760 ordered-walk points and 262,144 independent-multiple points.
Also 3,328 random-model controls: 512 models per standard prime and four models
on each of 144 random +144 residue-matched fields per case. Pure scalar
multiplication and P-224 square roots are costly: inspect elapsed/CPU records
on your machine; increase workers only within actual memory/CPU resources.

`points/*.raw` is the large filesystem dataset: successive big-endian x,y
coordinates, 24 bytes each for P-192 and 28 each for P-224. `records/*.json`
links every raw chunk to its model, generator, sampling seed, SHA-256 and
features. `design.json` freezes source/config; `inputs.json` snapshots fields.
`comparisons.csv` and `analysis.json` are the statistical outputs. Raw data is
kept outside Git; archive it with its manifests, not as an unlabelled binary.
`source/` preserves the executable version with each batch; if software changes,
resume or analyze using that frozen copy and the matching Python dependencies.

Build/update a deduplicated index over completed batches using standard SQLite:

```bash
.venv/bin/python catalog.py --root /large-filesystem/ec-study --output /large-filesystem/ec-study/catalog.sqlite
```

The database retains field/model/generator IDs and block features for statistical
or ML analysis. Duplicate copies of the same seed/design do not add samples.
Use held-out seeds and preserve field/model clustering for future ML splits.
The 99.9% nominal simultaneous intervals apply to one batch's 20 comparisons;
repeatedly examining batches needs a prospective pooled or sequential testing
policy. The catalog indexes data without declaring pooled results.

For a larger **prospective** batch, copy `config.json`, change block counts or
points per block before execution, then pass `--config custom.json` to `run`.
Keep 20 primary comparisons unless you also prospectively change the analysis.
Never edit a completed batch or tune the analysis against its results. For
long-term use schedule `run_batch.sh` yourself using cron, systemd or a batch
queue with a new seed and output path each time. Keep completed directories
read-only, copy whole batches to durable storage, verify checksums after
transfer, and analyze confirmation batches separately from discovery data.

Additional points do not add independent prime fields. The field control pool
is fixed; broaden it through a separately frozen input-generation study.
On one prime-order curve, uniform kG is generator-independent mathematically;
ordered sequences can depend on G. See [PROTOCOL.md](PROTOCOL.md) for controls,
statistical units, corrected confidence intervals and identification limits.
