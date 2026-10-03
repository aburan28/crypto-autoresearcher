# Implementation notes — EXP-BINSTD-842864 / TASK-20261001-25b6dd

## Instrument

- `implementation/exact_targets_g56.py` — Rolle-pruned DFS + rational Sturm box test
  (square-free aware), congruence pin for filtered last coefficient.
- `implementation/run_stages.py` — stage driver + immutable run packages.
- `implementation/finalize_remaining.py` — post-IMP finalize for g=6 infra stop,
  Stage 1 summaries, sympy sample, Stage 2 (does not overwrite prior runs).

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
4. **IMP-H1-runtime-g6 fired.** g=6 unfiltered after ~5.6e6 exact tests /
   ~3044s wall found only 99/164937 LMFDB classes (checkpoint preserved).
   Naive linear-in-classes projection ~1377h ≫ 10× HEUR-H1 modeled "hours"
   and advisory 86400s wall. Recorded as `failed_infrastructure` /
   `RUN-BINSTD-69747c` — **not** outcome A / exclusion. g=6 filtered
   (`RUN-BINSTD-eb2003`) not launched (shares levels 1..5 tree cost).
5. Stage 1 summaries (`exact_targets_g56.json`, unfiltered/filtered/sympy
   YAML) therefore cover g=5 complete + g=6 partial/infra; sympy hit
   re-verify applies to the 24 completed g=5 hits; dual-box random sample
   still covers both dims 5 and 6.

## Observed (no interpretation)

- Stage 0 ceilings 6725/51 and 39201/299 match; g<=4 unfiltered 5,35,215,1645;
  filtered hits 0; ambiguous 0.
- Stage 1 g=5 unfiltered classes=14325 (LMFDB match); filtered hits=24;
  ambiguous=0; all 24 hits sympy-agree; `jacobian_sufficiency_claimed=false`.
- Stage 1 g=6: infrastructure failure (partial checkpoint only).
- Stage 2: mod5@g1 finds 5-point class; mod1 equals unfiltered at g=1,2,3;
  toy surface presence only at n=19 among ladder primes.

## Not claimed

- No break / factor-base / rho competitiveness.
- `a_r >= 0` never upgraded to "is a Jacobian".
- Timeout / IMP stop never recorded as outcome A.
- No hypothesis status change.
