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

Continuation (2026-10-25): the user explicitly authorized merge. The earlier
approval refusal above is historical. The CI repair is published and the
artifact check passes; other applicable hosted checks are pending, so no merge
has occurred. See [weighted reach and readiness](readiness-20261025/report.md)
and its [PDF](readiness-20261025/report-compact.pdf). The pinned cuso backend runs its
documented univariate 1/3 calibration. Its optimal-shift routine calls a
Gröbner-basis computation, which must be included in costs. The three archived
joint certificate regions have no overlap with the stated conditional sub-rho
region. Neither observation supplies an optimized joint bound or root oracle.

The design workflow has not admitted a new joint experiment: the host goal
already has two open lanes, and no independent Coordinator runtime receipt
has been established here. Full-ledger validation also reports 106 errors
outside this PR's changed paths; the full output is retained. The repository's
scientific statuses remain unchanged. The continuation report gives the
specific next design and matched complete-cost measurement requirements.
The [operational follow-up](readiness-20261025/operational-followup.md) records
the direct Codex initialization failure on the read-only filesystem and the
two additional draft-tier fixes inherited from current main.

Coordination correction (2026-10-25): the failed nested CLI and two open lane
records did not establish a global runtime or capacity block. An authenticated
managed native Coordinator session is operating under the repository's native
runtime rule. The inspected old producer claims have completed releases. After
deepening history and hydrating historical blobs, the existing PFDR archive task
is ready, so the earlier absent-artifact observation was not queue corruption.
See the [additive operational correction](../../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/setup/additive-operational-correction.md).

Disjoint BATCH-3cfef2 and its zero-run design task TASK-20261025-b7e32e are
published and claimed in [PR #2557](https://github.com/aburan28/crypto-autoresearcher/pull/2557).
This advances applicability and contract preparation, not scientific execution.
The remaining audit publication gate includes owner-first shared artifact-tool
parity: its narrow fix is prepared, but has not landed in the owning `crypto`
repository. The earlier reports and scientific evidence remain unchanged.
