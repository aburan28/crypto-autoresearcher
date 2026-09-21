# Corrected prospective Tate calibration runner

This package is the zero-scientific-run correction authorized by
`DEC-20260908-cfcacc`. It implements the unchanged frozen
`EXP-ECDLP-910fcd` protocol and does not create fixtures, evaluate a Tate
pairing, run controls, calibrate costs, create a run id, or mint authority.

The non-launching command is:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 driver.py --dry-run
```

A future measurement can enter only through `--launch-lock`. Before that path
can execute, it checks a detached Coordinator signature over all of the
following: the original and corrective approvals; frozen specification and
execution-plan hashes; the executing driver plus hash-bound transitive
predecessor; a clean implementation commit; a fresh review archive whose
reviewed snapshot and review commits each differ from that later executing
commit while their reviewed source closure matches the executing bytes; an
allocated run id and nonce;
the exact canonical output directory; a verified non-Bedrock runtime; and the
8 GiB / one-worker cancellation and watchdog protections. This task supplies
none of those future authority inputs.

`driver.py` corrects the archived defects as executable behavior:

| Requirement | Corrected implementation |
| --- | --- |
| Linear irreducibility | `rabin_irreducibility_certificate` compares both `X^(p^k)` and `X` after reduction modulo the monic modulus, so degree one is an Fp branch; higher degrees retain every Rabin gcd witness. |
| Scalar isolation | `PublicEvaluatorInput` has a closed batch schema. Parent serialization and the evaluator child each recursively allow only fixed public fields, exact vector widths, and no duplicate keys. |
| Fixed workload and alternation | `fixed_q64_labels` creates one verifier-only q=64 list per fixture/seed; q=1 is the literal prefix. The evaluator consumes `curve_first` or `character_first` and performs that order. |
| Cost and coverage | `_future_cell` writes per fixture/seed/q/block/repetition costs, setup allocation, table and output bytes, peak RSS, and unavailable operation-count markers. `validate_panel_coverage` gates the exact eight selected fixtures, both target seeds, all controls, and the mandatory calibration. |
| Candidate and partial custody | Fixture, generator, polynomial, extension-point, and T/shift rejection histories are retained. `ProgressiveRunWriter` checkpoints each completed stage before the immutable canonical package is atomically published. |
| Future protection | Parent and evaluator children set 8 GiB address-space limits, evaluator calls are serial, cancellation is checkpointed, timeout/RSS paths kill the started process group, and interrupted/search-exhausted outcomes are typed without a scientific inference. |

The final regression suite contains only fixed static, synthetic, and mock
checks. It uses no frozen selection, pairing, calibration, experimental
character/isotropy/coordinate control, or timing panel. Its actual command and
measurements are recorded in `regression-receipt.json` after execution.

The package is not measurement admission. `TASK-20260908-16ec11` must snapshot
the seven scoped files, and a fresh independent implementation review must
produce the review binding required by a future launch lock.
