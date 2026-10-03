# Implementation notes — EXP-BINSTD-cedae5 / TASK-20261001-e57118

## Protocol

Stages 0–4 per `specification.yaml`. Stage 0 artifacts committed before
Stage 1. Stage 5 only on concentration trigger.

## Arithmetic

Lifted `gf2n.py` / `curve.py` from `experiments/EXP-CERTBIN-e94b27/impl/`
into this write_scope (numpy present; IMP-numpy cleared by availability).

## Certificate discipline (char-2 correction)

Matching on `x(L)` identifies `{L,-L}`. Combined-relation re-sum:

- `L_a == L_b` → `P1+P2+(-P3)+(-P4) = O` (cancel shared residual)
- `L_a == -L_b` → `P1+P2+P3+P4 = O`

A naive four-sum `P1+P2+P3+P4` when sums are equal is **wrong** in
characteristic 2 (doubling ≠ identity). The Z/(4ℓ) replica uses the
same signed cancellation. Adversarial 8-bit truncation produces keys
that are neither equal nor opposite residuals → measurable failure.

## Deviations

- Char-2 certificate form documented above (required correctness fix vs a
  naive four-sum); metrics otherwise follow the frozen protocol.
- Stage-4 exhaustive verification of all truncated-key matched pairs
  (large C(k,2) count); wall-clock recorded in run package.
- Stage 5 ran because `curve_over_generic_ratio ≈ 3.13` left `[0.5, 2]`.
  n=19 Koblitz `y^2+xy=x^3+1`, modulus `t^19+t^5+t^2+t+1`, window
  `deg(x)<10`, plus matched `Z/(4·130873)` replica.

## Out of scope

GTTD not implemented. No deployed-curve attack. No F7 advice claim.
No H/EXP/IDEA status edits.
