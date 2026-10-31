# Two predicates on all 21 NIST/ANSI curves

The historical selector remains unresolved. The frozen finite library contains
1,913 Boolean predicates, giving 495 distinct complemented observation
signatures. All 122,265 unordered signature pairs and their 16 truth tables
were evaluated: **zero robust or possible fits**, including when unknown
validation observations take favorable values. Single-signature rules also
have no fit. This excludes only the declared library of two atoms.

Read the [report](report.md), inspected [three-page PDF](report.pdf),
[library and scope](LIBRARY.md), [exact cohort observations](cohort-features.csv),
[audit](AUDIT.json) and [archive binding](BUNDLE.json). The P-224 cubic-j
pattern survives, but no second library atom extends it to all six streams.
CM-field ramification, Frobenius conductor and actual endomorphism conductor
remain separate quantities.

Python integer arithmetic and bitset bins agree with independent GP arithmetic
and rowwise truth-table enumeration on every feature, fit and collision witness.
The first verifier stop, exact-warning-only correction, both frozen protocols,
all process receipts and both exports are retained. There were four original
implementation evaluations: three successful and one failed. A complete replay
after archive extraction and relocation also passed; it is validation on the
same data, not another independent sample.

To replay with Python 3.14 and `/opt/homebrew/bin/gp`, extract into a fresh
directory:

```sh
zstd -dc evidence.tar.zst | tar -xf -
cd evidence/attempt-02
python3 -B run.py
```

The archive includes 70 sealed files. Its manifest covers 69 payload files;
the archive binding separately seals the manifest itself. Each non-fitting
pair has a packed publication/omission collision witness; the encoding and
iteration order are documented in LIBRARY.md. Source imports are shared
prior observations, not newly executed original historical programs.

Both original exports pass `check-export --verify-files`. The original failed
execution retains `status=failed`; the export checker calls terminal failures
`outcome_class=completed`, which does not mean scientific success.

Canonical artifact upload returned HeadObject403. Exact archive bytes remain
in Git under PR2602's existing `large-file-ok` exception. No store or CI success
is implied. Original third-party source-package, email and paper bytes are
excluded; URLs, source digests and newly derived observations are retained.
