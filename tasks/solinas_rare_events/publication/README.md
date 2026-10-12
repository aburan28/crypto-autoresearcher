# Fixed batches and artifact publication

`archive.py` seals completed, verified compact data into a lossless ZIP and
checks every entry against SHA256 and length. It refuses an existing archive.
The original scientific data remains on disk. Repository publication contains
small result records and the full entry manifest; large raw ZIPs are local
download artifacts unless a separate destination has explicitly been recorded.

To accumulate a predeclared number of independent seeds without an agent:

```sh
python publication/batch.py --root /large-disk/batch-a --seed-prefix batch-a --batches 4 --workers 3
```

This wrapper writes a source-hashed, fixed seed list before launch, runs every
seed, verifies each result, and pools all of them only after completion. The
default study is substantial; four seeds need substantially more disk and
time than one. The wrapper uses the same checked input models; additional
seeds increase independent starts, **not the number of independent primes**.

Pooling has nine exact paired rate tests, a separate nine-rate CP interval
family, and a separate24-tail CP interval family, each alpha0.001. Ordinary
field counts are descriptive in the pooler; it does not manufacture new field
replicates. A fresh prospective plan is needed to test additional models,
coordinate bits, thresholds or learned features. Do not choose seeds, drop
runs, stop, or enlarge the batch based on interim p-values. Repeatedly testing
until a favorable result appears invalidates fixed-sample inference.

The batch/pooling helpers are publication tools added after the current study's
source freeze. They are **not used to sample or analyze powered-20261012**.
They are checked with engineering fixtures using different seeds. Scientific
measurement code and that study's plan remain exactly as frozen.

For a future ML workflow, split train/test by complete seeds and, for a
prime-family task, by fields. Windows from one field or generator must not
leak into both training and held-out field cohorts. These bit strings and
public labels are research measurements; classifier accuracy alone does not
establish an ECDLP algorithm or a prime-family mechanism.
