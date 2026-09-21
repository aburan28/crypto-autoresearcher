# INVALID RUN -- implementation_error

This execution of `python3 -m driver.run_impl` (first attempt) is INVALID and
superseded by a fresh execution at `../RUN-ECTD-9e4248-impl/`.

Reason (implementation_error, caught and fixed per AGENTS.md rule 4 -- recorded,
not silently discarded): `orchestrate.run_pipeline` passed `n_needed` (the number
of edges THIS RUN attempts to build, =1 for the smoke test) into
`decision.decide`'s `min_vertical_edges` parameter, which controls the
`resource_incomplete` threshold in the FROZEN decision table. Because
`min_vertical_edges` was set to 1 instead of the spec's frozen 8
(`spec.inputs.min_vertical_edges`), `decide()` incorrectly evaluated
`continuity_scoped` off a single completed edge, bypassing `resource_incomplete`
entirely. This is exactly the "designed scope of a 1-edge smoke run" case
EXP-ECTD-001's own precedent documents as `resource_incomplete`, not a data-bearing
branch.

Fixed in `driver/orchestrate.py` (`FROZEN_MIN_VERTICAL_EDGES = 8`, always passed to
`decide()` regardless of how many edges a given run attempts to build). This run
directory is kept, per the "never overwrite, delete, or re-key" rule, and marked
invalid rather than silently discarded. All raw data in this directory (the vertical
edge construction, certificates, meters, rho/bsgs receipts) were themselves
CORRECT and are consistent with what the corrected run reproduces -- only the
final `decision_branch` field was wrong.
