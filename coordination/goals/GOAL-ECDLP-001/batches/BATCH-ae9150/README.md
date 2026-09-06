# First-fall proposal and experiment design package

User-requested formalization under `RQ-PFDR-ae2fba`, published in
[PR #757](https://github.com/aburan28/crypto-autoresearcher/pull/757).
See [intake.md](intake.md) for source provenance and the prior-work boundary.

| Priority | Formal idea | Hypothesis | Experiment | Question |
|---|---|---|---|---|
| 1 | [IDEA-20260905-df55e9](../../../../../ledger/proposals/IDEA-20260905-df55e9.yaml) | [H-PFDR-2139a5](../../../../../ledger/hypotheses/H-PFDR-2139a5.yaml) | [EXP-PFDR-f32e6c](../../../../../experiments/EXP-PFDR-f32e6c/specification.yaml) | Does the certificate refute the same definition, domain, and quantified claim? |
| 2 | [IDEA-20260905-e6e2e5](../../../../../ledger/proposals/IDEA-20260905-e6e2e5.yaml) | [H-PFDR-232b3a](../../../../../ledger/hypotheses/H-PFDR-232b3a.yaml) | [EXP-PFDR-782085](../../../../../experiments/EXP-PFDR-782085/specification.yaml) | Which top-form cancellations survive as independent nonzero degree falls? |
| 3 | [IDEA-20260905-850460](../../../../../ledger/proposals/IDEA-20260905-850460.yaml) | [H-PFDR-d5f90f](../../../../../ledger/hypotheses/H-PFDR-d5f90f.yaml) | [EXP-PFDR-25057c](../../../../../experiments/EXP-PFDR-25057c/specification.yaml) | What degree growth is certified on a finite digit ladder with retained controls? |

The proposals precede their experiment designs through separate exact-path
snapshot archives. The [dispatch queue](dispatch_queue.json) binds the source
paths, hashes, parent commits and snapshot commits. The archive manifests do
not assert their own containing commit hash.

Experiment contracts are for review, with `approved_by: null`. This batch runs
zero experiments and changes no existing hypothesis or goal status. Novelty
remains unverified. No first-fall theorem, disproof, ECDLP speedup or asymptotic
impossibility result is established by this package.

Finite witnesses can refute a stated universal equality or a bound with a
specified constant. Refuting an unspecified asymptotic constant requires a
separate argument for an unbounded family. Layer first fall, ordinary first
fall, last fall and solving degree retain their own definitions. A finite
dimension counterexample need not refute a first-fall degree formula.

The two small-prime counterexample candidates in the intake are replication
leads; their untracked local reviews are not imported as evidence. Every future
fixture must pass its declared domain checks, including the distinction
between an arbitrary affine x-value and the x-coordinate of a rational curve
point. Incomplete computations report bounds or censoring.

Future execution requires a committed approval and bounded execution queue.
Any proposed contradiction or closure then requires the prescribed independent
review at the appropriate claim tier. The present archive checks establish
record integrity only.

See the [design report](design-report.md) for the seven CPU-hour total of proposed
execution caps and the [operational receipt](operational-receipt.md) for checks,
archive bindings, and disclosed process limitations.
