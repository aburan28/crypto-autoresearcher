# Graph trial adapter regression control

Date: 2026-10-22 America/Los_Angeles. This implementation control replays one
P29 vertex-0 `low_x` prepared input with eight fixed public target coefficients.
It does not use study admission and cannot estimate discovery yield.

The first attempt (`native/`) failed before the wrapper created its phased
receipt: the control-only runner imported the Coordinator admission module at
startup and the pinned Python lacked PyYAML. I moved that import into the
study-admission branch so bounded controls keep their narrower dependency set.
The retained failure output remains unchanged.

The retry (`retry1/`) completed all four wrapper phases. The separate checker
reported `status: valid`, eight targets, zero useful targets, and zero rank
increments. The independent ordered-count oracle matched the collector. The
prepared group-law checker passed on eight targets and 512 signed base points.
The raw logs, source and binary digests, execution receipt, command, and checker
output are retained beside this report.

This validates the direct prepared-input control path after lazy admission
loading. It does not validate scientific admission, full-quota P37 resource
behavior, graph-wide relation yield, or complete ECDLP cost. The first attempt
is an import/environment failure and is not a zero-yield observation.

[Inspected PDF](report.pdf) · [Control diagram](control_flow.svg)
