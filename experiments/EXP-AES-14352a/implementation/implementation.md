# Implementation note — EXP-AES-14352a Stage 1

## Package

- `predicates.py` — program-local P_RD / F_fp / diagonals / ID sets
- `fips197_pin.py` — FIPS-197 KAT pin vs `aes_reduced.py`
- `stats.py` — pre-registered Stage-1 statistics (observations only)
- `run_stage1.py` — Stage-1 runner (ordering: pin → schedule → controls → AES primary)
- `README.md` — byte sets, B, structure size, joint ACCEPT definition
- `trial-plan.json` — mirrored from latest run for admission visibility

## Runs

| Run ID | Status | Note |
|--------|--------|------|
| `RUN-AES-0739d9` | completed_valid | First attempt; HEUR zero-event labeling overly harsh |
| `RUN-AES-a36d0b` | completed_valid | **Primary deliverable**; corrected degenerate HEUR labeling |

Both use the same frozen pilot budget. Stage 2 not executed.

## Pin

- `file_sha256` = `2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447` (match)
- KAT App B / C.1 / C.2 / C.3 pass under `final_mix_columns=False`

## Pilot budget (THIS attempt)

- `structure_size=256`, `n_pairs_per_key=32`, `B=4`, `idj_subset=[0,1]`
- Toy tier; program-local; not published-figure scale

## Measured primary (RUN-AES-a36d0b)

- AES r=5 joint: **0 / 512**
- Control r=10 joint: **0 / 512**
- Gap: **0.0**; one-sided Fisher p: **1.0**
- Control FPR bits (joint): **≥9.0** lower bound (`log2(512)`); 0 events
- Graded joint: r=4 **512/512**, r=5 **0/512**, r=6 **0/512** (decays; no non-decay tell)
- Sibling misaligned r=5: **0/512**
- Ablation ratios: **undefined** (zero P_RD mass at r=5 and r=10)

## Decidability (observation only)

- Success criterion: **decidable, NOT met** (no AES>control gap at r=5)
- Preferential random suppression: **not adjudicable** at this budget (no P_RD accepts on primary/control)
- HEUR-FP1: degenerate zero-events (pass as joint==product==0)
- HEUR-FP2: undefined (no P_RD accepts)
- Graded r=4 saturation vs r≥5 null is a recorded observation; does not alone meet Stage-1 success (primary is r=5 vs r=10)

## Protocol deviations

- Cheap pilot structure (declared before AES arms; hash-committed)
- `idj_subset=[0,1]` not all four inverse diagonals

## Not claimed

- Published ACC/ACP margins (R3)
- Stage-2 CM-3 vs REF-B
- Full-round / deployed AES
