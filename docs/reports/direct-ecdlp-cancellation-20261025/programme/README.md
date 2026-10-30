# Classical ECDLP experiments

A separate experimental card for every classical lead in the parent plan, plus a shared direct-response protocol, correctness scaffolding and explicit success/failure criteria. Classical CPU/GPU only; no index calculus.

**Objective clarified:** a correct working algorithm and an improvement over its explicit baseline are valid milestones. Novelty is a separate assessment. See the [report interpretation clarification](../../../../experiments/EXP-ECDLP-7c0b1e/reports/run-20261025T0651Z/interpretation-clarification.md); the completed follow-up did not measure runtime against a named solver baseline.

**Execution update, 25 October 2026:** the finite all-track pilot is now implemented and complete. [Actual report](../../../../experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z/HEADER.md), [observations](../../../../experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z/observations.md), [PDF](../../../../experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z/report.pdf) and [runnable harness](../../../../harness/classical_ecdlp_pilot/README.md). One admitted batch ran five C++ programs with three measurement workers, covering all ten tracks on eight toy fixtures: 241 rows, zero failed modules, no remaining pilot trials. This is smaller than the original discovery/confirmation design and establishes no new solver or speedup.

**Fresh follow-up completed:** [projection/decoder/basis report](../../../../experiments/EXP-ECDLP-7c0b1e/reports/run-20261025T0651Z/HEADER.md) and [harness](../../../../harness/classical_ecdlp_followup/README.md) cover 24 fresh curves, 192 public targets and 3,624 rows. Pair-entropy gaps shrink, the public decoder has no established advantage over controls, and the expanded basis audit yields a local characteristic-two AND obstruction. Toy witness verification and complete execution do not establish a novel ECDLP algorithm. Frozen readiness files below remain historical design snapshots.

- [Programme, measurements and shared controls](EXPERIMENTS.md)
- [Nine lead-specific experiment cards](LEADS.md)
- [Readiness and missing implementations](READINESS.json)
- [Development checks and exact limits](CHECKS.md)
- [Printable programme](report.pdf)
- [Editable diagram](programme.dot) and [SVG](programme.svg)
- [C++ reference and launcher](reference/README.md)
- [Exact scalar-window control](window-control.md)
- [Preliminary methodology criticism](methodology-review.md)

At the original design snapshot, only the point-level reference and its 13,731 development assertions existed. The subsequent implementation supplies a gate-level compiler, per-lead diagnostics, certified local synthetic fixtures and genuine admission/execution receipts. The frozen [readiness snapshot](READINESS.json) and earlier planning PDF describe that earlier state. A new EC-specific cancellation identity, fast locators/decoders, solver advantage and novelty remain unverified.

| Track | First discriminating measurement | Main gap |
| --- | --- | --- |
| Direct tagged response | Every tagged block boundary, composition and full construction cost | Gate circuit and EC-specific rewrite |
| Prime-to-p sections | Computable section defects and scalar-profile/null comparison | Lift implementation and explicit decoder |
| EDS / elliptic nets | Linear complexity, 15-monomial predictor and orientation ambiguity | Nonlinear locator constructor |
| Endomorphism observables | Exact eigenvalue/certificate redundancy | Information beyond known scalar action |
| Matchgate successor | Exact identities for a finite ≤81-arm basis grammar | Global planar/tag construction |
| Radical-ladder successor | Branch count versus reduced algebra dimension | Target-local constructive invariant |
| Reverse automata | Full state/label sizes and target ambiguity | Uniform constructor and orientation |
| Conditional coefficients | Exact prefix coefficients versus truth | Cheap coefficient evaluator |
| Ax–Katz successor | Empty/nonempty receipt collisions and degree hypotheses | Exact singleton residue evaluator |
| Lossy propagation | Entropy, fibres, candidate support and relabeling nulls | Repaired calibration and inference decoder |

Every card separates a correct measurement, a falsified candidate, a scoped null and an inconclusive or blocked computation. Shared costs include construction, failed paths, recovery, verification and peak storage. Existing IC-specific or retired records remain unchanged; direct successors are distinct proposals.

Rebuild the report with `./build.sh`. Development checks can run with `./reference/test.sh`; they do not launch scientific experiments.

[PDF formatting and original-byte provenance](../FORMAT-NOTICE.md) document the compact export. Historical readiness and exact raw evidence remain unchanged.
