# FFD_SEMAEV_MEASUREMENT1 — First-fall degree of Weil-descended Semaev S_3 systems, against a support-matched null

- **ID:** FFD-SEMAEV-MEASUREMENT1
- **Task:** TASK-20260916-ae946f (theory/measurement track for RQ-DREG-bd6c86)
- **Author:** top-level session, 2026-09-16
- **Instruments:** `research/verification/ffd_semaev_core.py`, `ffd_semaev_measure.py`, `ffd_s3_formula_control.py`
- **Raw outputs:** `ffd_semaev_measure_results.txt`, `ffd_semaev_results.json`, `ffd_s3_formula_control_results.txt`
- **Status:** MEASUREMENT at toy scale. Not an approved `EXP-*`, no run record, no hypothesis moved.

## 0. What was measured

For `E : y² + xy = x³ + a₂x² + a₆` over `F_{2ⁿ}`, factor base `V ⊆ F_{2ⁿ}` an
`F₂`-subspace of dimension `n'`, and a target `x_R` drawn from a real point of
`E`: the decomposition system `S₃(x₁, x₂, x_R) = 0` with `x₁, x₂ ∈ V`, Weil
descended to `n` Boolean equations in `N = 2n'` variables.

The observable is the fall profile, which by Caminata–Gorla eq. (1)
(`V_{F,D} = rowsp(M_D)` for a degree-compatible order) and Thm 2.8 is exactly
the object in the definition, not a proxy:

```
falls(D)     = dim( V_D ∩ R_{≤D−1} )
new_falls(D) = falls(D) − dim V_{D−1}
d_ff         = min{ D : new_falls(D) > 0 }
```

**Null object** (required by `RQ-DREG-bd6c86`): a random Boolean system with the
**same equation count and the same per-equation monomial-degree profile**.

## 1. Correctness control, run first

`S₃(X₁,X₂,X₃) = (X₁X₂ + X₁X₃ + X₂X₃)² + X₁X₂X₃ + a₆` was **not** taken from
memory. It was checked against genuine point arithmetic on `E(F_{2ⁿ})` for
`n = 3,4,5`: **560/560** genuine decompositions vanish. Negative control: random
unrelated triples vanish **30/800 ≈ 3.8%**, consistent with `~2^{-n}` — so the
polynomial is not vanishing trivially.

## 2. Result

10 Semaev draws per cell (random target `x_R`, random independent `V`), 25 null draws.

| cell | N | Semaev `d_ff` | null `d_ff` | median deficit |
| --- | --- | --- | --- | --- |
| n=4, n'=3 | 6 | {2: 9, 3: 1} | {2: 3, 3: 22} | 1 |
| n=4, n'=4 | 8 | {2: 6, 3: 4} | {3: 1, 4: 24} | 2 |
| n=5, n'=3 | 6 | {2: 10} | {2: 3, 3: 22} | 1 |
| n=5, n'=4 | 8 | {2: 7, 3: 3} | {3: 1, 4: 24} | 2 |
| n=6, n'=3 | 6 | {2: 10} | {3: 25} | 1 |
| n=6, n'=4 | 8 | {2: 10} | {3: 2, 4: 23} | 2 |
| n=7, n'=3 | 6 | {2: 9, 3: 1} | {2: 13, 3: 12} | 0 |
| n=7, n'=4 | 8 | {2: 9, 3: 1} | {3: 22, 4: 3} | 1 |

**Semaev's `d_ff` is pinned at 2 in every cell**, stable under both `n` and the
random draws. **The null's `d_ff` rises with `n'`** — 3 at `n'=3`, 4 at `n'=4`.
The deficit therefore widens with the factor-base dimension, which is the
parameter index calculus actually pays for.

**The deficit is driven by the null rising, not by Semaev falling.** `d_ff = 2`
is the floor for a degree-2 system: it cannot drop further. Any statement of the
form "the Semaev systems fall faster and faster" is not what this shows.

## 3. The degree-2 collapse is Lemma 1 appearing in data

The descended equations have total degree **2**, not 4. `S₃` is degree 4 in the
`x_i`, but `(e₂)²` collapses: squaring is Frobenius, and on `F₂`-valued descent
coordinates `u² = u`, so the square costs no degree. That is exactly
`THM_SEMAEV_FALL1` Lemma 1 (`g^q ≡ g^φ mod I_q`) showing up as an observable.

This also rules out the cheap explanation of the deficit. At `n' = 4` there are
`C(8,2) = 28` quadratic monomials and at most 7 equations, so a linear
dependence among top parts is **not** forced by counting — and the matched null
confirms it, needing degree 4. The degree-2 fall is structure.

The natural attribution, per `RQ-DREG-bd6c86`'s requirement, is the **Frobenius
syzygy class**: the `n` Weil components are coefficient-Frobenius conjugates of
one another, so `THM_SEMAEV_FALL1` Corollary 1 predicts free low-degree
relations among them at a degree set by `deg(g)` and `q`, not by `n`. **This is
a hypothesis consistent with the data, not a verified attribution.** Confirming
it means exhibiting the explicit syzygy and checking it is not in `Triv`.

## 3a. ADDENDUM (2026-09-16, TASK-20260916-43505c) — the attribution is now DERIVED

Section 3 stated the Frobenius attribution as "a hypothesis consistent with the
data, not a verified attribution". **It is now derived, and it is uniform.**

The degree-2 coefficients of the descended system are exactly

    c_{jk} = t² + t·x_R ,   t = v_j v_k

An `F₂`-combination killing the whole degree-2 part is an `F₂`-linear
functional, i.e. `Tr(μ·—)` for some `μ ≠ 0`. Using `Tr(z) = Tr(z²)` in the form
`Tr(μ t²) = Tr(μ^{1/2} t)`:

    Tr( μ (t² + t·x_R) ) = Tr( (μ^{1/2} + μ·x_R) · t )

which vanishes for **all** `t` as soon as `μ^{1/2} + μ·x_R = 0`. Taking
`μ = x_R^{−2}` gives `μ^{1/2} = x_R^{−1}` and `μ·x_R = x_R^{−1}`, whose sum is
zero in characteristic 2.

**So a degree-2 fall exists for every `n`, every `n'`, and every `V`, whenever
`x_R ≠ 0`** — which is exactly the pinning at `d_ff = 2` that §2 measured, now
explained rather than observed. Squaring `μ^{1/2} = μ x_R` gives
`μ(1 + μ x_R²) = 0`, so `x_R^{−2}` is the unique nonzero root of *that* equation.

Verified in `research/verification/ffd_frobenius_witness.py`: the witness
annihilates the degree-2 part in **every** cell over `n = 2..9`, `n' = 1..5`,
6 random `(V, x_R)` draws each.

**Uniqueness of the annihilating `μ` is FALSE in general and is not claimed.**
The same script finds 7 annihilating `μ` at `n=9, n'=3` and 63 at `n=9, n'=2`:
when the products `v_j v_k` span a proper subspace, accidental solutions exist,
and a negative control finds 14/106 non-witness `μ` that also work at small
`n'`. Uniqueness returns once the products span enough of the field. The unique
object is the nonzero root of `μ^{1/2} + μ x_R = 0`, not the annihilator.

This upgrades the Frobenius attribution from hypothesis to derivation and is
filed as Lean target `formal/targets/semaev-s3-degree2-fall-witness.yaml`. It
still proves only that a degree-2 fall **exists**; §4 below is unchanged.

## 4. What this does NOT show

- **`d_ff` is not the solving degree.** Caminata–Gorla §4 proves `d_ff` can be
  arbitrarily larger *or* smaller than the solving degree, the last fall degree
  and the degree of regularity. A `d_ff` deficit is **not** evidence of a
  solving-degree deficit, and nothing here touches the subexponential question.
- **The null is matched on degree profile only.** It does *not* reproduce the
  block-multiaffine structure (`m` blocks of `n'` variables) or the `S_m`
  symmetry. `IDEA-20260916-9d2fa6` predicts precisely that a count-matched null
  overstates the deficit, so this result is fully consistent with the deficit
  being partly or wholly absorbed by the next rung of that null tower. **Until
  that rung is run, the honest reading is an upper bound on the real deficit.**
- **Scale.** `N ≤ 8` variables, `n ≤ 7`. The Boolean ring saturates fast at this
  size. No claim transfers to cryptographic parameters.
- One curve shape (`a₂ = a₆ = 1`), characteristic 2 only, `m = 2` summands only.

## 5. Next

- **(N1)** Run the block-multiaffine null (`IDEA-20260916-9d2fa6` rung 3). It
  decides how much of the deficit survives. This is the single highest-value
  follow-up and the result above should not be cited without it.
- **(N2)** Attribute the degree-2 fall to an explicit syzygy and check it
  against `Triv` — this is `formal/targets/semaev-frobenius-collapse` made
  concrete.
- **(N3)** Push `n'` to 5–6 (`N = 10–12`) to see whether the null keeps rising
  linearly while Semaev stays pinned, which is the trend claim.
- **(N4)** `m = 3` (`S₄`), where the symmetry class becomes non-trivial.
