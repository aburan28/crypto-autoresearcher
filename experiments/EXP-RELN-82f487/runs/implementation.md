# Implementation notes and protocol deviations, EXP-RELN-82f487

This file is written by the Executor and covers every run under
`experiments/EXP-RELN-82f487/runs/`. It records deviations from the frozen
specification (`experiments/EXP-RELN-82f487/specification.yaml`), per
`agents/executor.md` responsibility 10 and the handoff's constraint that any
needed protocol change is a versioned amendment, never an inline edit --
none of the deviations below change any scientific field, threshold, seed,
or architecture text; they are implementation-level substitutions forced by
the executing environment, or scope reductions within the handoff's own
explicit partial-completion authorization.

## 1. No ML framework installed (environment constraint)

Checked at executor start: `import torch`, `import sklearn`, `import
xgboost`, `import lightgbm` all raise `ModuleNotFoundError` in this
environment. The spec's `gnn_architecture` and `non_graph_tree_baseline`
controls call for "a declared tensor library" and named GBT libraries
(the hypothesis record recalls GraphSAGE/GIN and XGBoost/LightGBM as
reference implementations, not requirements). The executor therefore wrote:

- `source/autodiff.py`: a minimal hand-written reverse-mode autodiff engine
  over numpy (matmul, add, relu, concat, segment_mean, gather, mse_loss,
  Adam), verified by a finite-difference gradient check
  (`autodiff.self_test()`, max error ~9e-11).
- `source/model_gnn.py`: the K=3, width-64 bipartite message-passing net
  described in the spec, built on that autodiff engine, trained end-to-end
  with Adam.
- `source/model_trees.py`: a from-scratch CART regression tree plus
  gradient-boosting ensemble (exact split search via sort + cumulative-sum
  SSE, not a quantile approximation), matching the frozen grid (depth in
  {4,6}, trees up to 200 with early stopping, learning_rate 0.05).

This is a real, working, gradient-verified implementation, not a stub or a
fabricated placeholder -- but it is NOT the named external libraries the
architecture text recalls as reference implementations, and its numerical
behavior (convergence, exact split thresholds, floating-point rounding) is
not guaranteed identical to what torch/XGBoost would produce. Reported as a
deviation on every run under this experiment.

## 2. Custom bipartite message-passing schedule

The spec's `gnn_architecture` text ("K=3 rounds; mean and sum aggregation;
readout MLP on (features(R), pooled context)") underdetermines the exact
per-round update schedule. This executor's construction (documented in
`model_gnn.py`'s module docstring): each round updates relation embeddings
from their 3 base neighbors' mean plus their associated training target's
embedding, then updates base and training-target embeddings from a mean
pool of their incident relations; after K=3 rounds the global context
`g = mean(final base embeddings)` is the only channel through which the
trained graph reaches a held-out target (which has no incident relation
node by construction, matching H-RELN-10ad6b's mechanism section). Readout
is an MLP on `concat(features(target), g)`. A different but spec-compatible
schedule could give different numbers; this is recorded, not hidden.

## 3. Grammar-reproduction fixture is an internal self-consistency check, not a reproduction of c5c614's unread exact values

specification.yaml's `sigma_one_and_frozen_grammar_reproduction_slices`
control (part ii) asks for depth-1/depth-k tree slices to match "a direct
implementation of c5c614's grammar members g1-g3" computed by "an
independent code path, never imported" -- but IDEA-20260830-c5c614 was read
only PARTIALLY by the hypothesis author (lines 1-130 and 355-515; see
H-RELN-10ad6b's citations block), so g1-g3's exact formulas are not fully
available to this executor either. `source/grammar_reference.py` therefore
implements ONE well-defined grammar-slice selection rule (rank discrete
feature-value groups -- Legendre class, or top-k bits of x -- by mean count,
take top groups until sigma density, tie-break the boundary group by count
then index) via two independently written code paths (a scalar loop and a
vectorized numpy path) INSIDE this module, and checks them for
floating-point-exact agreement. This is a genuine, passing correctness
fixture (`all_exact: true` on every arm/rung run so far), but it is a
narrower claim than "matches c5c614" -- it is an internal consistency check
on this executor's own reconstruction of the grammar rule, not a
reproduction of c5c614's own unrun reference numbers.

## 4. INV-6 theorem-arm indicator computed analytically, not via a trained model

The `inv6_theorem_arm_instrument_check` control's indicator ("some
translate R - P_i is 2-decomposable") is computed directly from the
Theta(B) pair-sum lookup table (`source/lookup_labels.py`) rather than
learned, per the spec's own description that this feature is "supplied,"
"cost-disqualified by construction," and is "an E-side instrument check,"
not a claim about the trained predictor class.

## 5. Scope reductions authorized by the handoff's partial-completion clause

Per `ledger/handoffs/TASK-20260907-2adca3.yaml`'s explicit prioritization
(full completion "NOT expected or required"), this executor session ran:
Stage 0 (leak audit + planted-leak diagnostic), Stage 1 fixtures inline per
arm, and the cheapest rung (N=2^14) at sigma=1/8 ONLY, with ONE curve
(curve_seed 101), ONE base seed (201), and ONE training seed (301), across
ALL FIVE arms, BOTH model classes, BOTH feature regimes (F0, F1) -- this
last point exceeds the handoff's minimum ask (which named sigma=1/8 "only,"
not regime, as the first-pass scope) but was affordable within the same
pass. The determinism re-run reuses the main run's SELECTED hyperparameters
(no re-run of the grid search) rather than re-selecting on the val split a
second and third time, which is faster and is still "the identical model"
per the spec's own wording for that control. Sigma=1/32, the second and
third curves/base seeds/training seeds (the full 3x3x3 replication), and
rungs 2^16/2^18/2^20/2^24 were NOT reached and are reported as `not_run`,
named concretely in the execution report, per the contract's own
inconclusive decision path.

## 6. Base-index-triple storage bounds relation-node count

`enumerate_counts.py`'s `enumerate_with_triples_*` functions store every
certifying (i,j,k) triple for every target (not just one), to support an
unbiased training graph; at B=48 (rung 2^14) this is C(50,3)=19600 triples,
cheap. At larger rungs (B up to 466 at 2^20) this grows to C(468,3) ~
1.7e7 triples, which is a real memory/time consideration for reaching those
rungs in a future session -- flagged here rather than encountered silently.
