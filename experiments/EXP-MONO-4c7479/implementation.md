# Implementation note: EXP-MONO-4c7479 (Stage 0 + Stage 1 only)

Handoff: `ledger/handoffs/TASK-20260830-25b8c3.yaml`. Contract:
`experiments/EXP-MONO-4c7479/specification.yaml` (frozen, `approved_by:
coordinator`, `2026-08-30`). This note is observations-and-implementation
only; it renders no verdict on `H-MONO-0b3def`.

## Layout

All code lives under `experiments/EXP-MONO-4c7479/implementation/`, pure
Python 3 standard library (confirmed by `grep -n "^import\|^from"` across
every file: only `json, os, sys, time, platform, subprocess, resource,
hashlib, collections, __future__` appear anywhere in this experiment's
code — no `sympy`, `sage`, `numpy`, `g6k`, or `fpylll`).

- `mpoly.py`, `stage0.py` — Stage 0 only: a hand-rolled dict-of-monomials
  multivariate integer-polynomial engine and the exact-integer identity
  checks. Not imported by any Stage 1 module.
- `fp_common.py` — generic F_p / F_p2 / F_p4 field arithmetic (Legendre
  symbol, Tonelli-Shanks, a general Fp2 "complex-method" square root, and a
  from-scratch Fp4 tower `Fp2[z]/(z^2-e)` with its Frobenius derived from
  the characteristic-p freshman's-dream identity `(A+B)^p = A^p + B^p`).
  Shared plumbing (like a shared `mulmod`), imported by both arms — carries
  no notion of `t1,t2` or `c1,c0` itself.
- `arm_a.py` — **Path 1, direct group arithmetic.** Computes t1,t2 from
  (e1,e2) or accepts an already-given ordered (t1,t2) pair
  (`classify_from_t_pair`, reused by the ordered-base control), lifts to
  actual curve points (going into `Fp4` via `fp_common.Fp4` whenever a
  y-coordinate is a non-square in `Fp2`), applies Frobenius directly to
  point coordinates, and reads off the resulting permutation of the fixed
  labelled set `{P1,-P1,P2,-P2}`. **Never computes `c1`, `c0`, or `h(Y)`.**
- `polymod.py`, `arm_b.py` — **Path 2, closed-form quartic factoring.**
  `arm_b.py` computes `c1, c0` directly from `(e1,e2,A,B)` by the STEP-3
  formulas and forms `h(Y)=Y^4-c1Y^2+c0`; `polymod.py` is a generic
  univariate-polynomial-mod-p engine implementing full distinct-degree
  factorization (`x^{p^d} mod h` via repeated squaring, then
  `gcd(x^{p^d}-x, h)`, for `d=1,2,...`) — this finds linear factors via the
  same DDF mechanism as the quadratic/quartic split, which is the "faster
  root-finder" the contract explicitly permits in place of testing all `p`
  residues, and is definitionally NOT the biquadratic `Z=Y^2` shortcut (it
  never substitutes `Z=Y^2` or solves a quadratic in `Z`). **`arm_b.py`
  never computes `t1`, `t2`, `f(t1)`, or `f(t2)`.**
- `recipe.py` — the third, character-triple (S6) check. Explicitly allowed
  by the contract to use quantities from both arms (`chi(f(t1)),chi(f(t2))`
  from arm (a)'s own computation for the split regime; `chi(c0)` — arm
  (b)'s quantity — for the inert regime), since it is not one of the two
  independence-bound arms.
- `ordered_base_control.py`, `random_quartic_control.py` — the two
  controls that need dedicated code (matched-ordered-base and
  random-quartic-null); the factor-base-sublocus control is a pure
  re-filter computed inline in `run_experiment.py` from already-produced
  Stage-1 data (no separate module, per the contract: "No separate
  computation is required").
- `run_experiment.py` — the driver: Stage 0 gate, then the 6-cell census,
  the three controls, and all required artifacts.

## Independence verification (approval_requirements item 3)

- `arm_a.py` imports only `fp_common`. `arm_b.py` imports only `polymod`.
  Neither imports the other, and `grep -n "arm_a\|arm_b" *.py` shows no
  third module importing both into a shared computation that mixes their
  intermediates (`run_experiment.py` calls both, but only to *compare*
  their already-independently-produced outputs — it does not feed one
  arm's intermediate value into the other).
- `arm_a.classify_point`/`classify_from_t_pair` never references `c1`,
  `c0`, or `h` — `grep -n "c1\|c0\|arm_b\." arm_a.py` returns nothing.
- `arm_b.classify_point` never references `t1`, `t2`, or `f(` — `grep -n
  "t1\|t2\|f_of\|lift_y" arm_b.py` returns nothing.
- The character-triple recipe (`recipe.py`) is fed pre-computed `f1,f2`
  (from the caller's arm-(a) result) and `c0` (from the caller's arm-(b)
  result) by `run_experiment.py`; it does not itself recompute either from
  the other's internals, and it is explicitly a third, non-independence-
  bound check per the contract's own text.

## Stage 0 result

`PASS`, all 8 sub-checks (see `runs/*/stage0_transcript.json`, identical in
both runs since it is pure symbolic/exact-integer and touches no run
input): the three `s3_expr` T-coefficients match the claimed `(e1,e2)`
forms exactly as integer polynomials in `Z[x1,x2,A,B]`; `c1 = f(t1)+f(t2)`
and `c0 = f(t1) f(t2)` match the STEP-3 formulas exactly; and
`disc_T(S_3) = T1^2-4 T2 T0 = 16 f(x1) f(x2)` (KN-FIND-a8990a's cited
identity) holds as an exact term-by-term integer-coefficient identity.
Stage 1 was therefore run, per the frozen gate.

## Correctness self-checks performed before trusting the Fp4 tower

Because roughly a quarter of all base points (the inert-regime, `chi(c0)=-1`
subpopulation) require lifting a y-coordinate into `Fp4` (this is common,
not an edge case — see the mechanism note below), the from-scratch `Fp4`
tower was validated exhaustively for `p in {101, 211, 13}` before use in
Stage 1:

- Fp2's general square-root routine verified against every one of the
  `(p^2-1)/2` genuine squares in `Fp2` (exact match, all `p` tested).
- Fp4's Frobenius verified as a ring homomorphism (`frob(xy)=frob(x)frob(y)`
  on 100 random pairs per `p`), as fixing the Fp2 subfield after two
  applications, and as satisfying `frob^4 = identity`, for every `p` tested.
- `Fp4.sqrt_of_fp2_nonsquare` verified against **every** non-square element
  of `Fp2` for `p in {101, 211, 13}` (5100 / 22260 / 84 elements
  respectively, zero failures).

## Why an Fp4 lift is common, not an edge case

Squaring both sides of the norm identity `z^{(p^2-1)/2} = chi(Norm(z))`
shows that an `Fp2` element `f(t1)` (in the inert regime, `t2 = conj(t1)`,
so `f(t2)=conj(f(t1))` and their product is the Fp-rational `Norm(f(t1)) =
c0`) is a square in `Fp2` **iff** `chi(c0) = +1`. Since `chi(c0)=-1` occurs
on a genuine ~1/4 density of all base points (the `four_cycle` class), the
Fp4 branch is exercised on a large, non-degenerate fraction of the census,
not a rare corner case — building it correctly was necessary, not optional.

## Deviations and declared interpretation choices (recorded per AGENTS.md
rule 8 / core rule 12, not resolved here)

1. **Matched-ordered-base control object.** The contract's own paragraph
   instructs classifying "the SAME labelled four-point object" from the
   ordered `(t1,t2)` pair reused from Stage 1's split regime. Read against
   the cited finding `KN-FIND-a8990a` Theorem B, that theorem's forced
   two-cycle-type law concerns a *different*, smaller object: the two roots
   of `S_3(t1,t2,T)` under the regular `(Z/2)^{m-2}=Z/2` action (a regular
   action is fixed-point-free on every non-identity element by
   construction, so "no 2.1.1/single-sign-flip type" is close to definitional
   there). This implementation follows the control paragraph's own literal
   instruction — arm (a)'s four-point Frobenius machinery, fed the ordered
   `(t1,t2)` pair directly rather than derived from a symmetric `(e1,e2)` —
   documented as `ordered_base_control.py`'s own docstring. **Observed
   result does not match the contract's forced value**: see Observations
   below. This is reported as an anomaly, not resolved or reinterpreted
   here; if the intended object is the Theorem-B T-root object instead, a
   different (much smaller) control would need to be implemented as a
   protocol amendment.
2. **HEUR-WREATH-2 check ("realized-class count over F_p2 vs F_p").** An
   exhaustive Frobenius census over an `F_{p^2}`-rational base (`(e1,e2)`
   ranging over `F_{p^2}^2`, size `p^4`) is not costed anywhere in the
   contract's own `cost_note` and is infeasible within the 1200s/1GB
   budget (`p^4` at `p=211` is `~2*10^9` points). This implementation
   instead reports the partition of the already-computed F_p-base census's
   realized permutations between the split-regime subpopulation
   (F_p-rational `t` values) and the inert-regime subpopulation (genuinely
   `F_{p^2}` `t` values), and checks that these two subsets are disjoint
   and jointly cover all 8 permutations. See
   `cells[*].heur_wreath_2_check` in each run's `raw-result.json`.
3. **Random-quartic control's per-coefficient counter.** The seed rule
   specifies rejection sampling "with `counter` incremented on each
   rejection" but does not state whether the counter resets between the
   four coefficients of one draw. This implementation resets the counter
   to 0 at the start of each coefficient's own draw (each of `b0..b3` for a
   given `(p,j)` has its own independent counter sequence starting at 0),
   which is the reading consistent with the domain string's own
   `decimal(i)` (coefficient index) slot distinguishing the four draws.

## Timing and resources (measured, both runs)

Both runs completed in ~36 seconds wall-clock, ~68.6-68.7 MB peak RSS —
far under the 1200s / 1GB budget (see `runs/*/manifest.yaml`). No
infrastructure failure, no timeout, no budget breach.
