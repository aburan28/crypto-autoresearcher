# Methodological note — HOLD-N corrections absorbed (Stage 0)

Experiment `EXP-BINSTD-cf4bf7`, task `TASK-20261001-18804b`.
Source idea `IDEA-20260922-9e5383`; review
`analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-9e5383.yaml`
(verdict `sound_with_corrections` / HOLD-N). Hypothesis `H-BINSTD-4a2f99`.

## Defects absorbed (observations only; no claim status change)

1. **Null precondition.** Stable Frobenius subspaces of `F_{2^n}` number
   `2^f` with `f = 1 + (n-1)/ord_n(2)`. They are trivial
   (dimensions `{0,1,n-1,n}` only, `f=2`) **iff** `ord_n(2)=n-1`
   (primitive prime). The source wording "prime degree ⇒ no nontrivial
   stable subspace" is **rejected** as the general null claim and retained
   only as the named falsifiable alternative Stage 0/4 contrast against.

2. **n=31 disqualified as null.** Independent recomputation:
   `ord_31(2)=5` ⇒ `f=7` (128 stable subspaces, mid-dimension present).
   Retained **only** as contrast control (`role: contrast_not_null`).
   Never labeled as a null arm in any artifact of this experiment.

3. **n=41 is not a "poor" lattice control.** `ord_41(2)=20` ⇒ `f=3`
   (moderately rich). Rejected as poor-n control
   (`role: rejected_poor_control`).

4. **Ratio errors restated** after null re-selection to primitive primes:
   - pair 1: `(d,k)=(4,7)` vs `n=29`; error **+4.5pp**
   - pair 2 PRIMARY: `(d,k)=(2,17)` vs `n=37`; error **−17.0pp** (worst;
     disclosed beside any primary-cell finding)
   - pair 3: `(d,k)=(2,19)` vs `n=37`; error **−11.1pp**
   - pair 4: `(d,k)=(4,7)` vs `n=29`; error **+11.9pp**
   - pair 5: `(d,k)=(2,19)` vs `n=37`; error **+0.2pp** (best ratio match)

5. **WDSat gate.** Stages 2–3 optional; missing engine ⇒
   `instrument_unavailable` (infrastructure), **not** mathematical
   falsification of H1.

## Primary cell selection

Pair 2 remains primary for **lattice richness**
(`ord_17(4)=4`, `f=5`, 32 stable subspaces, dims
`{0,1,4,5,8,9,12,13,16,17}`), not for best ratio (pair 5).

## Claim boundary

Toy / instrument protocol. No exponent move. No break. No rho
competitiveness. No deployed-curve attack at `n>=131`.
`certificate.kind: none` for all Stage 0 arithmetic runs.
