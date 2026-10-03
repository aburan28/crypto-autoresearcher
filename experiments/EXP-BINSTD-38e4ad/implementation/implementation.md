# Implementation notes — EXP-BINSTD-38e4ad Stages 0–2

Task: `TASK-20261001-b78ef3`. Observations only; no H/EXP/IDEA status changes.
HOLD-S corrections bind. No deployed-curve break claim. No claim that fixed-target
orbit clauses are satisfiability-preserving. Amazon Bedrock not used. No AUXIN edits.

## Code

| Path | Role |
| --- | --- |
| `implementation/gf2n.py` | Schoolbook + table `F_{2^n}` (from EXP-CERTBIN-e94b27) |
| `implementation/curve.py` | Binary `Y^2+XY=X^3+AX^2+B` + Miller–Rabin |
| `implementation/soundness.py` | `ord_n(2)`, Phi_17 factorisation, `ker g(τ)`, census metrics, H2 counts |
| `implementation/runpack.py` | Immutable run packages (`certificate.kind: none`) |
| `implementation/stage0_run.py` | Lattice + citation/conversion/notation artifacts |
| `implementation/stage1_run.py` | n=17 m=2 l=8 exhaustive soundness census (4 seeds) |
| `implementation/stage2_run.py` | V' / ordinary-curve / H2 controls |

## Protocol notes / deviations

1. **S(R) representation:** unordered pairs stored as sorted `(x1,x2)` tuples;
   membership under coordinate squaring uses the same normalisation.
2. **closure_fraction definition:** fraction of eligible targets (`σ(R)≠±R`) with
   *nonempty* `S(R)` closed under squaring. Vacuous empty sets are not counted as
   H1-style closures (otherwise empty fraction would inflate the metric away from
   the frozen null `0`). Empty counts are reported separately as
   `n_targets_empty_S`.
3. **Stage 1 instrument:** exhaustive group-arithmetic 2-sum over the factor-base
   point list (`O(|FB|)` per target via subtract-and-lookup), not WDSat. Equivalent
   to the specified `V×V` unordered pair census.
4. **Stage 2 ordinary control:** `n_targets=40` random on-curve points (not
   necessarily prime-order); labeled control sample. Stage 1 remains the primary
   200×4 census.
5. **Stage 2 V' control:** `leave_Vprime_fraction` under squaring on a random
   dim-8 non-stable subspace (seed 2026100121).
6. Run manifests may record `code.dirty: true` at execution time because stage
   artifacts were written before the commit that archives them (immutable run
   records; not rewritten).
7. Auxiliary per-seed stash JSON under `stage1/_census_seed_*.json` retained for
   aggregate reproducibility; primary artifacts are the YAML summaries.

## Seeds / randomness

| Seed | Use |
| --- | --- |
| 2026100117..2026100120 | Stage 1 target draws (200 each); enumeration exhaustive given targets |
| 2026100121 | Stage 2 V' subspace |
| 2026100122 | Stage 2 ordinary-curve target draw |

Generator search uses `seed ^ 0x4731` as a derived RNG stream (recorded in code).

## Comparison vs frozen prediction (observations only)

| Item | Frozen | Observed |
| --- | --- | --- |
| Stage 0 empty mid-lanes {163,29,37} | true | true (`RUN-BINSTD-f9fb37`) |
| tau-stability dim-8 V | pass | pass |
| closure_fraction (pooled) | 0 | 0.0 (800 eligible) |
| conjugate_overlap (pooled) | 0 | 0 |
| equivariance_agreement (pooled) | 1 | 1.0 |
| leave_V' fraction | reported | 0.9921875 |
| ordinary equivariance fails | true | true (eq=0.0) |
| h2_count_agreement | true | true (103=103) |
| Break / satisfiability claim | none | none |

Distinguishable outcome id recorded in `stage1/heur-h1-verdict.yaml` as
`DO-1-null-confirms-HOLD-S` (metric comparison only; no hypothesis status edit).
