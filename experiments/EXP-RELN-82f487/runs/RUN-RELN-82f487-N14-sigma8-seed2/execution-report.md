# Execution report: RUN-RELN-82f487-N14-sigma8-seed2

Cell: rung 2^14 (N=16829, p=16901), curve_index_j=2, curve_seed=102,
base_seed=202, training_seed=302, sigma=1/8 (0.125). All five arms, both
model classes (gnn, trees), both feature regimes (F0, F1). Label-permutation
null (this cell's own training_seed 302, run_cell.py's
`do_permutation_null=True` path, the identical code path the first cell used
with its own training_seed 301). Task: TASK-20260907-8b29e0, the contract's
declared second (curve_seed, base_seed, training_seed) replicate
(102/202/302), checking whether EV-RELN-cc045d's F1/gnn
E/random-vs-Z/N-random pipeline-fault disagreement (0.079 vs tolerance
0.064) replicates at this second seed. See `runs/implementation.md` for
deviations shared with the first cell (no torch/sklearn/xgboost/lightgbm
installed; hand-written, gradient-verified GNN and GBT), unchanged here.

## Provenance note (per the handoff's constraint)

This run reuses `experiments/EXP-RELN-82f487/source/` completely unchanged.
No file under `source/` was modified, added, or deleted. Two small run-local
driver scripts were written INSIDE this run's own directory (not under
`source/`), because `source/run_full_cell.py` hardcodes the first cell's
seed constants at module level rather than taking them as arguments:

- `driver_run_full_cell_seed2.py`: byte-for-byte the same logic as
  `source/run_full_cell.py`'s `main()`, with only the six constants at the
  top (`RUNG_K, CURVE_INDEX_J, CURVE_SEED, BASE_SEED, TRAINING_SEED, SIGMA`)
  changed to this cell's values (14, 2, 102, 202, 302, 0.125). Every function
  it calls (`curve_gen.generate_curve`, `enumerate_counts.*`,
  `run_cell.run_arm_cell`) is imported unchanged from `source/`.
- `build_artifacts.py`: turns `work/all_arms.json` into the full
  required-artifact set (fixtures, per-arm metrics/selection-null/
  count-vector-source, model cards, feature manifest, cost instrumentation,
  etc.), calling `source/leak_audit.py`, `source/run_stage4_analysis.py`,
  `source/cost_instrumentation.py`, `source/features.py`,
  `source/lookup_labels.py` unchanged. This mirrors how the first cell's
  equivalent artifacts were assembled (no such glue script was saved under
  `source/` for the first cell either, since it is run-specific plumbing,
  not part of the frozen scientific pipeline).

This is a parameter substitution, not a protocol or implementation change.
**No bug was found or fixed in `source/` this session** (see the "Genuine
implementation issue?" section below for the one thing that came close but
did not require a code change).

## Blocking gates

- Reproduction fixtures: **ALL PASS** on every arm (closed-form total-check
  deviation exactly 0; sigma=1 slice lambda=rho=1.0 exactly; grammar
  reproduction fixture exact-match true on every arm). Identical outcome to
  the first cell.
- Static leak audit: **PASS** on real feature/model modules; **CORRECTLY
  REJECTS** the planted-leak diagnostic. Identical outcome to the first cell
  (this check is deterministic and not seed-dependent; re-run for this run's
  own record).
- Z/N-interval positive control: **PASS** for both classes at both regimes
  (half-ceiling threshold 4.0, ceiling 8.0). F0_trees and F1_trees reach the
  ceiling exactly (8.001); F0_gnn is markedly weaker this seed at 4.541
  (barely above the 4.0 threshold, versus 7.996 in the first cell); F1_gnn is
  6.704/7.148. All four still individually PASS the gate, but F0_gnn's margin
  is thin -- reported plainly, not narrowed away.
- **Label-permutation null: LEAK DETECTED (new this seed).** Two cells sit
  clearly above their selection-null band: `ZN_interval_F0_trees` (lambda
  3.460, rho 3.219, vs bands with upper bounds 1.946 / 2.189) and
  `ZN_interval_F1_trees` (identical values -- the trees model does not use
  the F1 base-summary features differently here, matching the same
  F0/F1-identical pattern already seen for trees in the first cell).
  `E_x_interval_F0_gnn` is marginally above its rho band (1.0624 vs upper
  bound 1.0580, a 0.4% overshoot). **None of these three fired in the first
  cell** (seed1's worst permutation values were all inside band, several
  below band). Per the spec's own wording ("A permuted-label lift ABOVE band
  is a LEAK ... and halts the run"), this is a blocking, in-protocol stop.
- **Canary (E/log-interval): LEAK DETECTED (new this seed).**
  `E_log_interval_canary_F1_gnn` is above band on both lambda (2.526 vs upper
  1.895) and rho (3.008 vs upper 2.100). This did NOT fire in the first cell
  (all four canary cells were inside band there).
- **E/random vs Z/N-random pipeline-fault check: FAILED for regime F0, class
  gnn this seed** (not F1/gnn, which was the first cell's flagged
  combination). rho(E/random)=0.9856, rho(Z/N-random)=1.0579, difference
  0.0724 > tolerance (band half-width) 0.0594. Z/N-random (F0, gnn) also
  sits above its own selection-null band. F1/gnn -- the exact combination
  flagged in the first cell -- is INSIDE tolerance at this seed (difference
  0.0204 vs tolerance 0.0594), well inside.

Per specification.yaml's stopping rules, this cell hits THREE separate
blocking conditions (pipeline fault, label-permutation leak, canary leak),
versus the first cell's ONE (pipeline fault only). All are reported in
full below; the run's per-cell measurements are otherwise preserved
completely (nothing discarded).

## Genuine implementation issue?

No crash, exception, NaN, or import violation occurred anywhere in this run.
The static leak audit correctly passed the real modules and correctly
rejected the planted-leak diagnostic, exactly as in the first cell -- this
is strong evidence the audit and label/feature separation are working as
designed, not evidence of a code defect. The label-permutation and canary
gate failures are the protocol's OWN stopping rules firing on a SECOND,
independently drawn cell; per the handoff's constraint, this is reported as
an observation, not treated as license to modify `source/`.

**One candidate mechanism is recorded here as a hypothesis for a future
audit, not asserted as fact and not acted on**: `ZN_interval`'s base is the
fixed structural interval `+-[1, B_eff]` (not seed-dependent at all -- see
`source/enumerate_counts.py`'s `build_base_ZN_interval`, which takes no
`base_seed` argument), while its FEATURES (translates `r +- d_i`) are drawn
from `base_seed`. A gradient-boosted tree trained on PERMUTED labels over
this narrow, structurally regular residue interval could exploit
feature-space adjacency/collisions (small B=48 over N~16829, many nearby
residues sharing near-identical Legendre/translate feature vectors) to
memorize noise in a way correlated with the true count vector's own
regularities -- an overfitting artifact of a low-entropy feature space, not
necessarily a scalar/logarithm leak in the sense the audit's import/name
rules target. This is speculation offered for the record, not a diagnosis;
distinguishing it from a genuine information leak requires an audit this
executor session did not run (e.g. label-permutation with an INDEPENDENT
permutation seed per replicate, or checking the raw feature-collision rate
on `ZN_interval` directly). **This finding is flagged to the Coordinator as
worth a dedicated audit before further cells of this arm are trusted**,
per the handoff's review_reservation.

## The central comparison: E_random_vs_ZN_random, this cell vs the first cell

| class/regime | seed1 (101/201/301) E_random rho | seed1 ZN_random rho | seed1 abs diff | seed1 tolerance | seed1 agree? | seed2 (102/202/302) E_random rho | seed2 ZN_random rho | seed2 abs diff | seed2 tolerance | seed2 agree? |
|---|---|---|---|---|---|---|---|---|---|---|
| F0/gnn   | 1.0547 | 1.0245 | 0.0303 | 0.0644 | YES | 0.9856 | 1.0579 | 0.0724 | 0.0594 | **NO** |
| F0/trees | 1.0223 | 1.0245 | 0.0022 | 0.0644 | YES | 1.0553 | 1.0022 | 0.0531 | 0.0594 | YES |
| F1/gnn   | 1.0309 | 1.1104 | **0.0795** | 0.0644 | **NO** | 1.0270 | 1.0066 | 0.0204 | 0.0594 | YES |
| F1/trees | 1.0223 | 1.0245 | 0.0022 | 0.0644 | YES | 1.0553 | 1.0022 | 0.0531 | 0.0594 | YES |

**Verdict for F1/gnn specifically: DOES NOT REPLICATE.** The first cell's
F1/gnn disagreement (0.0795 vs tolerance 0.0644, a band miss) is INSIDE
tolerance at this second seed (0.0204 vs 0.0594) -- a materially smaller
difference, well inside band. Taken at face value, this is consistent with
the first cell's F1/gnn miss having been a single-seed statistical
fluctuation rather than a reproducible defect specific to the F1/gnn
combination.

**However, the pipeline-fault check as a WHOLE does not clear this seed
either**: a DIFFERENT combination, F0/gnn, misses band this time (0.0724 vs
0.0594), and this seed additionally trips the label-permutation and canary
gates (which the first seed did not). So while the SPECIFIC F1/gnn
disagreement does not replicate, the broader finding -- "this contract's
cells, at this rung and B, are prone to hitting at least one blocking gate
per cell" -- does replicate, just via a different gate each time. Per the
handoff's instruction, this is reported plainly with zero further
interpretation of mechanism.

For completeness, the other three combinations:
- F0/gnn: agrees at seed1 (0.0303 << 0.0644), disagrees at seed2 (0.0724 >
  0.0594) -- the mirror image of F1/gnn's pattern (agrees where the other
  seed disagreed).
- F0/trees: agrees at both seeds (0.0022 and 0.0531, both well/marginally
  inside 0.0644 / 0.0594).
- F1/trees: identical numbers to F0/trees at both seeds (the custom CART
  tree implementation does not differentiate F0 from F1 features in either
  cell's realized split choices here).

## Overall verdict for this cell

`all_blocking_gates_pass = false` (pipeline fault in F0/gnn, label-permutation
leak in ZN_interval/trees and marginally E_x_interval_F0_gnn, canary leak in
E_log_interval_canary_F1/gnn). **Branch classification: INCONCLUSIVE** per
specification.yaml's `decision_paths.inconclusive` -- not a
negative_observation, not evidence for or against H-RELN-10ad6b, per
AGENTS.md rule 3 and this contract's own falsification_criterion.

Independent of that gate, and reported for completeness/preservation (not as
a decided result): a SINGLE rung (2^14) can never fit the log-log decay
slope regardless; this cell alone could at most say whether E/x-interval's
excess sits inside or outside the selection-null band at THIS one rung,
which it does for both classes and both regimes (see numbers below) --
consistent with, but not proof of, the predicted branch, and equally
consistent with a small alive excess at the smallest rung.

## Measured numbers (E/x-interval, the primary object)

| regime | class | rho excess over null | lambda excess over null | inside band? |
|---|---|---|---|---|
| F0 | gnn   | +0.0533 | +0.0194 | yes/yes |
| F0 | trees | +0.0239 | +0.0353 | yes/yes |
| F1 | gnn   | -0.0130 | -0.0141 | yes/yes |
| F1 | trees | +0.0239 | +0.0353 | yes/yes |

GNN-minus-trees difference (E/x-interval): F0 rho_diff=+0.0294,
lambda_diff=-0.0159; F1 rho_diff=-0.0370, lambda_diff=-0.0494 -- both within
the selection-null band half-width at this rung (no replicated,
non-shrinking positive difference can be claimed from two rungs/two seeds
at one rung each).

## Cost instrumentation (measured, this machine, this implementation)

c_f (feature computation + a linear-probe inference proxy, NOT the full
trained GNN/tree inference cost -- see the first cell's deviation note,
which applies identically here) ~= 1.52e-5 s/target ~= 25.60
point-addition equivalents; Theta(B) lookup ~= 3.23e-5 s/target ~= 54.33
point-addition equivalents; c_f / (B lookups) = 0.533 < 1, so H3's
falsification condition is NOT triggered at this rung either -- consistent
with H3, not proof of it (two rungs now measured, both at 2^14, still one
implementation, one machine, never transferred). The theta_b lookup time per
target is notably higher this seed (54.3 vs 34.4 point-addition equivalents
in the first cell) -- both measurements used the same n_sample=50 targets
convention and the same B=48; the difference is measurement noise /
system-load variance on a very small, fast-running loop (microsecond-scale
timings on a shared machine), not a algorithmic change, and is reported
plainly rather than reconciled.

## What ran vs what did not (this session)

Completed: the leak audit + planted-leak diagnostic (re-run for this run's
own record; deterministic, unchanged from stage0), fixtures (inline per
arm), the full cell (rung 2^14, 1 curve [curve_seed 102], 1 base seed [202],
1 training seed [302], sigma=1/8, all 5 arms, both classes, both regimes,
label-permutation null), Stage 5 cost instrumentation (one measurement,
E/x-interval arm).

NOT run (named concretely, per the handoff's explicit scope limit -- "DO NOT
expand scope beyond this one cell"): the shuffled-seed determinism re-run;
sigma=1/32; a third curve/base/training seed; rungs 2^16, 2^18, 2^20, 2^24;
per-target slice-membership/permutation-importance/partial-dependence
tables (recorded as `not_run` in `handoff/*.csv`, matching the first cell's
convention, since this run is inconclusive and these tables would document
a null in either case).

## Wall-clock

Main cell (all 5 arms, both classes, both regimes, label-permutation null):
1421.5 seconds (~23.7 minutes), measured by the driver's own wall-clock log
(`stdout.log`, `work/run_log.txt`). Artifact assembly + cost instrumentation:
~118 seconds. **Total measured wall-clock this session for THIS run:
approximately 1539 seconds (~25.7 minutes) of compute** (excluding
code-authoring time for the two run-local driver scripts).
