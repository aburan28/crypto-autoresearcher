#set page(paper: "us-letter", margin: 0.75in)
#set text(font: "Libertinus Serif", size: 10pt)
= EXP-ECTD-cb23c5 execution report

*Observation-only record for* `RUN-ECTD-f96d04` (*least-prime-one-edge*).

== Scope and disposition

The repository supervisor classified this single frozen trial as
`infrastructure_error` and `needs_reconciliation`. No scientific output was
produced and no hypothesis or goal status changes.

#image("graph.svg", width: 100%)

== Frozen inputs and custody

- Experiment: `EXP-ECTD-cb23c5`; trial: `least-prime-one-edge`; run: `RUN-ECTD-f96d04`.
- Plan SHA-256: `5f29a49a3539cdbfcd6a1ec260b23b8f84ff99dea670c1cddc1b1f8430e54dae`.
- Execution checkout: `fd715c3ee81d51ff90cb10031cc5a3d99f5d7a42`.
- Dispatch-plan SHA-256: `8e37027ee0f052c2b23a9a02a64419645c83d2e7dcd4eb9ccab93f685318671d`.
- Owner and lease: `executor-ectd-cb23c5`, epoch `1`.
- Container: `crypto-ci-python:20261008`; network disabled; virtual-memory limit 131072 KB.

== Recorded observation

The producer returned code `1`. Its traceback ends at
`implementation/run.py` line 219:

#raw(block: true, "AttributeError: 'resource.struct_rusage' object has no attribute 'ru_max'.\nDid you mean: 'ru_maxrss'?")

The checker was not reached. The run receipt records
`status: infrastructure_error`, `check_returncode: null`, `published: false`,
and no scientific conclusion. Raw logs and supervisor records are preserved.

== Interpretation boundary

This record establishes only that the execution environment rejected the
producer's resource-usage attribute access before result emission. It does not
evaluate the curve construction, prime selection, quotient map, or any
mathematical mechanism. A portability correction requires a separately
coordinated additive implementation change and a new frozen run.
