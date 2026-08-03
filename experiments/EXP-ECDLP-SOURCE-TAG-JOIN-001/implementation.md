# Implementation note v2

The first draft was classified `REVISE` before any repository development run.
Its contract is preserved as `contract-v1.md`. V2 received independent theory,
benchmark, and red-team GO decisions for the one-seed noncanonical development
sweep. Those decisions are preserved in `pre-run-review-v2.md`.

The generator will inherit only clean curve generation, factor-base
construction, operation counters, Pollard rho, fixed-base BSGS, and the tested
D2/D4 support primitives. Source-tag assignment, both null generators, streaming
route compilation, exact D2-complement and partial-D4 baselines, and query
execution are new and must be independently replayed.

Candidate route construction streams unordered D2 pairs and does not retain a
materialized D4 workspace. Full D4/D5 supports are constructed separately as
audit and baseline objects. The raw artifact reports those audit operations
separately from candidate attack operations.

The v2 output has two gates:

- `source_signal_gate_passed`: candidate beats both null families under exact
  coverage and scalar-separation checks;
- `compiler_gate_passed`: the source signal also beats the exact-D2 and
  payload-matched partial-D4 decomposition comparators, plus task-matched DLP
  comparators. Full materialized D4 is included in an envelope only when its
  corresponding advice fits the candidate cap; otherwise it is reported as a
  storage/query Pareto diagnostic. The same-outer-schedule theorem still rules
  out strict online dominance over full D4 for the present inner scanner.

No canonical command is authorized by this file.
