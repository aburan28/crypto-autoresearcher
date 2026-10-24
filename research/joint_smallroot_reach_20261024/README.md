# Joint small-root reach accounting

Start with [report.md](report.md), [report.pdf](report.pdf), and the
[named unresolved problem](../../problems/joint-smallroot-reach-baseline-and-oracle-unverified.md).
The [protocol](PROTOCOL.md) fixes the finite diagnostic scope. This directory
contains software accounting and exact fixtures, not a completed ECDLP experiment
or an IC improvement claim. The independent blind review is prepared, not run.

Reproduce into a **fresh** directory, preserving committed outputs:

```bash
python3 research/joint_smallroot_reach_20261024/reproduce.py \
  --output /tmp/joint-smallroot-replay
```

The Python environment needs pytest, sympy, matplotlib, and typst. If dependencies
were installed in a separate directory, pass `--deps /path/to/dependencies`.
The replay retains commands, source hashes, exact coefficient matrices,
deterministic counts and pytest output and generates a graph and PDF. It refuses
to reuse an existing artifacts directory. The report-producing source is bound
by the manifest; later source changes do not rewrite earlier artifacts.

The complete IC baseline, random-target relation yield/rank, optimized external
shift selection, higher-rank GAPs and root extraction remain outstanding. No
pipeline speedup or optimality follows from the finite determinant counts.
