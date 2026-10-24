# Joint small-root reach accounting

Start with [report.md](report.md), [report.pdf](report.pdf), and the
[named unresolved problem](../../problems/joint-smallroot-reach-baseline-and-oracle-unverified.md).
The [protocol](PROTOCOL.md) fixes the finite diagnostic scope. This directory
contains software accounting and exact fixtures, not a completed ECDLP experiment
or an IC improvement claim. See the publication update below for current review status;
the original report preserves the status at the time it was written.

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

The [replay check](artifacts/replay-check.json) records a second execution from
source commit `dd698edd7f9a4daa497041d85af0a0c1d2172684`. Its deterministic
finite-audit and exact-matrix files are byte-identical to the first execution,
and all 23 software tests pass again. This is a same-source replay, not the
prepared independent mathematical review. The replay's raw outputs are retained
under [artifacts/replay/](artifacts/replay/).

Publication update (2026-10-24): the user authorized publication after the initial
automatic-review refusal. The exact branch history is now published in
[PR #2547](https://github.com/aburan28/crypto-autoresearcher/pull/2547).
The [blind review](independent-review.md) TASK-20261024-da3810 is complete against
the committed input. It independently derives the determinant budget and exact
fixture; its verdict on the unseen calculator implementation remains inconclusive.
The [addendum](review-20261024/report.md) and [PDF](review-20261024/report.pdf)
record the parent's scoped source comparison. Hosted CI is queued. Auto-merge was separately refused by automatic
approval review because branch publication authorization did not cover a future
merge into `main`; no alternative merge route was attempted.

The full goal remains unresolved: an applicable optimized construction,
weighted-bound normalization, root extraction, and a verified IC pipeline improvement remain
separate obligations. The earlier report and raw artifacts have not been edited.
