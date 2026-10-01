# Implementation notes — EXP-BINSTD-842864 / TASK-20261001-25b6dd

## Instrument

- `implementation/exact_targets_g56.py` — Rolle-pruned DFS + rational Sturm box test
  (square-free aware), congruence pin for filtered last coefficient.
- `implementation/run_stages.py` — stage driver + immutable run packages.

## Deliberate non-reuse

Does **not** import or call `analysis/couveignes-lercier-131/weil_census.py`.

## Deviations from protocol text

1. Baseline g<=4 reports Rolle DFS `exact_tests_performed` rather than the
   per-target head-product `candidates_scanned` from `exact_targets.py`
   (104 / 234220). Protocol-comparable metrics are unfiltered class counts
   and filtered hit counts (expected 5,35,215,1645 and 0 hits).
2. Unfiltered Stage-1 census uses modulus=131 only to tag hits in the same
   pass; a separate `--filtered-only` pass congruence-pins `a_g`.
3. First Stage-1 g=5 attempt (~77 min wall) exited without writing the final
   JSON (captured-stdout driver swallowed the child's trail); instrument
   hardened with live logs, checkpoints, pre-enrich snapshots, and capped
   ambiguous storage; g=5/6 re-run under the hardened driver. That aborted
   attempt is infrastructure, not a mathematical observation.

## Not claimed

- No break / factor-base / rho competitiveness.
- `a_r >= 0` never upgraded to "is a Jacobian".
- Timeout never recorded as outcome A.
