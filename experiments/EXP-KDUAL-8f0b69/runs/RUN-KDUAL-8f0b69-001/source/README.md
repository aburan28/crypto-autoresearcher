# Upstream source is NOT vendored here

The determination in `../raw-result.json` was made by reading nine files of
lattice-estimator at commit `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`. Those
files are third-party (malb/lattice-estimator, LGPL) and are deliberately **not
committed** to this repository: they are large, they carry their own licence,
and committing them would add nothing that the hashes do not already give.

What binds the determination instead is stronger than a copy:

- the upstream **commit SHA**, which is content-addressed by git, and
- the per-file **sha256** of exactly the bytes that were read, recorded in
  `../manifest.yaml` under `run.code.path_sha256`.

Re-fetch and verify in two commands:

```sh
./fetch.sh                                   # writes le_*.py here
sha256sum -c ../manifest-hashes.txt          # must pass on all nine files
```

Then reproduce the determination:

```sh
grep -ciE 'decod|polar|syndrome' le_*.py     # only le_reduction.py is nonzero
grep -niE 'decod|polar|syndrome' le_reduction.py   # all hits are list_decoding
grep -ciE 'fft' le_lwe_dual.py               # negative control: 54
```
