# EXP-FCP-001 Fixed-curve preprocessing pilot

## Metadata

- **Experiment ID**: EXP-FCP-001
- **Hypothesis**: none (no formal H-* record exists; this experiment was not
  routed through the `/design-experiment` lifecycle)
- **Bound question**: RQ-ECDLP-001 (toy-scale S_3 decomposition cost behavior)
- **Status**: analyzed (Coordinator review; see EV-FCP-001, DEC-20260726-001)
- **Claim tier**: toy (max field bits = 16, well under the 32-bit toy ceiling)

## Protocol governance gaps

This experiment was executed informally. The following governance artifacts are
missing and must be noted before interpreting any result:

1. **No `specification.yaml`** — there is no frozen, approved protocol. The
   experiment was not routed through the `/design-experiment` lifecycle, so
   there is no pre-registered primary metric, success criterion, falsification
   criterion, or stopping rule. The metrics reported below are descriptive, not
   tested against a pre-defined threshold.
2. **`dirty: true` on all 72 runs** — every manifest references commit
   `16c37dcf1fece7b27a9f8ace226745f18e90a728`, which is a ledger-only commit
   (it changed only `ledger/goals/GOAL-ECDLP-001.yaml`). The harness module
   `harness/fixed_curve_preprocessing.py` was uncommitted at run time and was
   first committed in `e648670d`, after the runs. The exact code that produced
   these results is therefore not captured by the commit SHA in the manifests.
3. **No formal hypothesis record** — the experiment is not linked to any `H-*`
   hypothesis in `ledger/hypotheses/`.
4. **No `execution_report`** — this file is the Coordinator-rewritten analysis;
   no separate Executor execution report exists.

These gaps do not invalidate the runs themselves (certificates verify, controls
are comparable, manifests are complete), but they limit the evidence to
**preliminary** strength and prevent a scoped rejection of the preprocessing
hypothesis.

## Observation

### Run inventory

72 runs, all `status: completed_valid`.

| Category | Count | Description |
|---|---|---|
| precompute | 9 | One per (bits, seed) pair; records factor-base construction time |
| fixed | 27 | S_3 decomposition reusing a precomputed factor base |
| naive | 27 | S_3 decomposition rebuilding the factor base per target |
| rho | 9 | Pollard-rho discrete-log baseline on the same curves |

- Bit sizes: 8, 10, 12, 14, 16
- Seeds: 1, 2 (bits 12 has only seed 1)
- Factor base size: 14
- Decomposition arity: m=2 (S_3)
- Targets per (bits, seed): 3
- Environment: macOS 26.6 arm64, Python 3.13.1, sympy 1.14.0, pyyaml 6.0.3
- Solver: sympy Gröbner basis (no Sage)
- All runs at commit `16c37dcf`, `dirty: true`

### Certificate verification

The Coordinator independently re-checked four certificates by recomputing the
curve arithmetic from scratch:

- **RUN-FCP-fixed-b8-s1-t1** — decomposition: (70,201) + (4,222) = (71,117)
  on y^2=x^3+70x+17 mod 241. **VERIFIED.**
- **RUN-FCP-naive-b8-s1-t1** — decomposition: (70,201) + (4,222) = (71,117)
  on the same curve. **VERIFIED.**
- **RUN-FCP-rho-b8-s1-t-fixed-1-42** — discrete log: 6*(37,64) = (56,197)
  on the same curve. **VERIFIED.**
- **RUN-FCP-rho-b16-s1-t-fixed-1-42** — discrete log: 6*(11943,17033) =
  (31716,8363) on y^2=x^3+3028x+22807 mod 52721. **VERIFIED.**

Runs that found no solution correctly carry `certificate: kind: none,
verified: true, verifier: no-claim`. Rho runs that solved carry
`certificate: kind: discrete_log, verified: true,
verifier: independent-recompute`.

### Control comparability

Fixed and naive runs at matched (bits, seed, target_index) use identical
`curve_id` and target points. Rho baselines at matched (bits, seed) use the
same curves. This was checked exhaustively for all 24 matched fixed/naive pairs
at bits 8, 10, 14, 16 (bits 12 has only seed 1, giving 3 pairs). No mismatches
found.

### Precompute cost

Factor-base precompute time per curve (9 runs):

| Statistic | Value (s) |
|---|---|
| median | 0.000146 |
| min | 0.000106 |
| max | 0.000195 |

Precompute cost is negligible relative to per-target Groebner time at all
tested bit sizes.

### Per-target wall-time (mean, s)

Wall-time is the total per-target wall clock from the manifest, which includes
factor-base construction (naive mode), precompute lookup (fixed mode), and
Groebner solving.

| Bits | Fixed (mean, s) | Naive (mean, s) | n (fixed) | n (naive) |
|---|---|---|---|---|
| 8 | 0.105801 | 0.045763 | 6 | 6 |
| 10 | 0.050504 | 0.093672 | 6 | 6 |
| 12 | 0.050618 | 0.040923 | 3 | 3 |
| 14 | 0.060108 | 0.051790 | 6 | 6 |
| 16 | 0.079249 | 0.057301 | 6 | 6 |

### Decomposition success

| Bits | Fixed (found/total) | Naive (found/total) |
|---|---|---|
| 8 | 4/6 | 4/6 |
| 10 | 3/6 | 3/6 |
| 12 | 0/3 | 0/3 |
| 14 | 0/6 | 0/6 |
| 16 | 0/6 | 0/6 |

Decomposition success is identical between fixed and naive at every bit size.

### Pollard-rho baselines

All 9 rho runs solved successfully. Group operations range from 6 (bits 8,
seed 2) to 123 (one of the bits 10 runs). All carry verified discrete-log
certificates.

## Comparison

### Fixed vs naive wall-time

There is no robust constant-factor win for fixed preprocessing:

- At bits 8, fixed is **slower** (0.106 vs 0.046, ratio 2.31x).
- At bits 10, fixed is **faster** (0.051 vs 0.094, ratio 0.54x).
- At bits 12, 14, 16, fixed and naive are within 1.4x of each other, with fixed
  slightly slower at 14 and 16.

The direction of the effect is inconsistent across bit sizes. The largest
apparent "win" (bits 10) and the largest apparent "loss" (bits 8) are both
driven by single-target outliers in the wall-time distribution, not by a
systematic shift.

### Decomposition success

Fixed and naive produce identical success counts at every bit size (4/6, 3/6,
0/3, 0/6, 0/6). The factor-base reuse strategy does not change which targets
are decomposable.

### Rho baseline context

All rho baselines solved at trivial cost (6–123 group operations). At these
toy group orders (e.g., n=23 at bits 8), rho is vastly cheaper than any
index-calculus-style decomposition. This is expected at toy scale and does not
bear on the fixed-vs-naive comparison, which is about preprocessing overhead,
not about beating rho.

## Inference

The following explanations are compatible with the observed data:

1. **Factor-base construction is not the dominant cost at this scale.** The
   precompute time (~0.0001 s) is orders of magnitude smaller than the Groebner
   solving time (~0.04–0.11 s). Reusing a precomputed factor base saves
   negligible time when construction is already cheap.

2. **The fixed and naive modes solve the same polynomial systems.** Because
   both modes use the same factor base size (14) and the same targets on the
   same curves, the Gröbner systems they solve are structurally identical. The
   decomposition success counts being identical is consistent with this.

3. **Wall-time variance is dominated by per-instance Gröbner solving
   fluctuations**, not by factor-base construction strategy. The inconsistent
   direction of the fixed-vs-naive ratio across bit sizes supports this.

4. **The absence of a preprocessing win at toy scale does not imply absence at
   larger scale.** If factor-base construction cost grows superlinearly with
   field size while Gröbner solving cost grows at a different rate, the
   trade-off could shift. This experiment cannot distinguish these scaling
   regimes.

## Limitation

This experiment cannot establish:

- That fixed-curve preprocessing fails at medium or cryptographic scale (only
  toy fields 8–16 bits were tested).
- That all parameterizations fail (only factor base 14, m=2, 3 targets per
  curve were tested).
- That no batching or multi-target amortization strategy can help (only
  single-target reuse of one factor base was tested).
- A scoped rejection of the preprocessing hypothesis, because no frozen
  protocol with a pre-defined success threshold existed.
- Any claim about P-256 or other cryptographic curves.

The evidence is **preliminary**: valid runs with verified certificates and
comparable controls, but limited instances (2 seeds, 3 targets), no frozen
protocol, and `dirty: true` on all runs.
