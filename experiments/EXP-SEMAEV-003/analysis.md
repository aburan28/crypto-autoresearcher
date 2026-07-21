# EXP-SEMAEV-003 — analysis

Powered redesign of EXP-SEMAEV-002 (per DEC-20260721-001). Same H-SEMAEV-002
claim, now with 2000 targets, 5 seeds/bit, a min-count power gate, and Katz 95%
CIs read from pooled per-bit counts.

## 1. Observation (pooled across 5 seeds per bit)
| bits | found_random | interval/random ratio [95% CI] | ap/random ratio [95% CI] |
|---|---|---|---|
| 12 | 2708 | 1.005 [0.960, 1.051] | 1.013 [0.968, 1.060] |
| 14 |  786 | 1.041 [0.947, 1.143] | 0.968 [0.880, 1.065] |
| 16 |  148 | 1.061 [0.849, 1.326] | 1.027 [0.820, 1.286] |

All 15 runs completed_valid; one decomposition certificate per run verified.

## 2. Comparison to predefined criteria (H-SEMAEV-002)
Success criterion: in the powered regime, no structured/random ratio 95% CI
lower bound exceeds 1.5x. **Met.** Every pooled CI lies entirely below 1.5x
(max upper bound 1.326); no per-run cell set structured_advantage_ci_excludes_1p5.

## 3. Inference
Under adequate statistical power, neither structured factor base (consecutive
interval, arithmetic progression) beats a matched random base on m=2 S_3
decomposition yield at toy scale: all ratios are consistent with 1.0. The
EXP-SEMAEV-002 threshold excursions (up to 2.33x) are confirmed to have been
low-count sampling noise — they do not survive powering. This is an
independent m=2 corroboration, in spirit, of the campaign's m=3 rejected_scoped
H-FB-001.

## 4. Limitations
- Toy prime fields (12-16 bits), m=2 (S_3), factor base size 20. No d_reg,
  solver-cost, or crypto-scale claim; claim tier toy.
- The conclusion is a scoped null (no >1.5x structured advantage); it does not
  exclude smaller constant-factor effects or a different m.
