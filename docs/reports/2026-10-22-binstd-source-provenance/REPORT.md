# BINSTD source-citation and policy-attribution audit

This is a source-reading correction to `EV-BINSTD-030b4e`. It changes no frozen run, numerical result, hypothesis state or decision. The [editable graph](audit.dot), [SVG](audit.svg), [PNG](audit.png), [figure PDF](audit-figure.pdf), and [report PDF](report.pdf) show the source chain and the remaining scientific boundary.

## Finding

The archived evidence record has five `internal` citations without named readers. Its infrastructure note and limitation cite `AGENTS.md rule 3` as the reason an absent XOR-SAT pin is not mathematical evidence. The current `AGENTS.md` core rule 3 requires experiment controls and metrics; core rule 5 says timeout, crash or implementation failure is not mathematical evidence. The missing pin is an implementation impediment, so the attribution should be to core rule 5.

I read `H-BINSTD-3b1f2d`, `EXP-BINSTD-6f3434`, approval `DEC-20261003-bc5802`, `HEUR-BINSTD-161102-H1` in source proposal `IDEA-20261001-161102`, and `AGENTS.md`. The hypothesis and approved experiment restrict this test to n=17, ℓ=3,4; the source proposal's heuristic has a wider n=17,19,23 statement. The approved experiment requires a shared XOR-SAT pin and at least 40 matched targets for a scientific charged-cost comparison. The decision approves the protocol and explicitly asserts no hypothesis verdict. The archived evidence reports the pin absent, hence no such comparison occurred. These are attribution checks, not a new independent replay of the run.

## Additive replacement

The original record has SHA-256 `a65bd7986a542a3b5be392aafecd05e8e38a61669f0e764a02f1e2ca53804d18` and remains unchanged. The [replacement](../../../ledger/corrections/schema-supersessions/20261022/ledger__evidence__EV-BINSTD-030b4e.v2.yaml) has SHA-256 `159c0d02cac5b3622e360cec333d8f6d85273c1b9298004942270c645d125e54`. The schema-supersession registry binds both hashes. A [focused checker](verify.py) removes only the five new `verified_by` notes and reverses the three corrected rule references before asserting exact structured equality with the frozen record. Its [receipt](verification.json) records the result.

## Validation and limit

The complete-tree [baseline log](validator-baseline-main.log), [corrected log](validator.log)
and [delta receipt](validation.json) use the exact `origin/main` archive at
`13eb217678653267553dcbfa9601f2564f63706b`. The baseline has 141
unsuppressed errors in 39 paths; overlaying only this registered replacement
leaves 136 in 38 paths. Exactly the five `EV-BINSTD-030b4e` citation errors
disappear and no error is added. Both validator invocations exit 1, so the
all-corpus integrity gate remains red. The older 142-error count belongs to
the prior dated audit; an unrelated knowledge correction already on this
base removed one more line before this work. Stage 1 remains O-IMPEDIMENT,
with no scientific ratio, speedup, rho comparison or new performance-dashboard
value. The graph records the provenance repair only.
