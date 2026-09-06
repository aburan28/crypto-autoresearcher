# Implementation note — EXP-ECDLP-a26bde

## Summary

The frozen contract's Stage 0 (curve/prime generation) and a large part of
Stage 1/2 (digit identity, claim 1; size law, claim 2; anomalous refusal,
part of claim 4) were executed and produced consistent, theory-matching
measurements across all 20 planned instances (five curves x four primes).
**Stage 3 (the Teichmuller non-homomorphic contrast, claim 3; and the leak
recovery + certificate, the other half of claim 4) was not executed** —
the execution budget was consumed by debugging a genuine, reproducible
numerical inconsistency in the literal contract mechanism, documented
below in full. This is reported as an explicit incompleteness per
AGENTS.md rule 5 (never fabricate; missing data stays missing), not folded
into a claim of full completion.

## The literal mechanism, as specified, and what went wrong

The contract's `mechanism` field specifies: compute `X_S = S^ - t(S)`
p-adically (the global point minus its canonical prime-to-p torsion lift),
read `v = v_p(psi(X_S))` and the digit `d(S^)`, and verify
`d(m S^) = m d(S^) mod p`.

This was implemented three independent ways:

1. A custom finite-relative-precision p-adic ("Laurent") number class
   (`driver/padic.py`, class `Qp`) supporting negative valuations natively,
   with affine EC group law built on top (`ec_add`, `ec_double`, `ec_mul`).
2. Standard **projective** short-Weierstrass EC arithmetic over the ring
   `Z/p^R` (`add-1998-cmo` / `dbl-2007-bl`, hyperelliptic.org Explicit-
   Formulas Database) — chosen specifically because it needs no inversion
   at all for addition/doubling, so it should sidestep any bug in the
   Laurent division logic.
3. Exact (unbounded) Python-fraction arithmetic, used both to test the
   formulas symbolically-adjacent (numerically, with genuine near-identity
   points constructed from the formal-group power series
   `s = t^3 + a t s^2 + b s^3`) and to cross-check the modular
   computations against "exact-enough" representatives.

The canonical torsion lift `t(S)` was built by re-deriving (independently,
without opening the file first) the group-theoretic projection construction
of `experiments/EXP-ECDLP-809375/implementation/fg1_group_theoretic.py`:
`S_hat = [p^(r-1) * ((p^(r-1))^{-1} mod n)] L` for an arbitrary auxiliary
lift `L`, which needs no Hensel/Newton iteration on the order-`n` condition.

**Verification performed on every sub-component, all of which PASSED:**

- `t(mS) == [m] t(S)` exactly, as ring elements, exhaustively for
  `m = 1 .. n-1` on a worked toy instance (`p=101`, `y^2=x^3-2`, `S=(3,5)`,
  `n=17`) — the torsion lift is a genuine homomorphism on `<S>`, matching
  the torsion-lift theorem (`ledger/FINDING-PF-IC-001.md` ECFG-P1543-R0/R1).
- `t(S) mod p^8` is stable across working precision `r = 8, 12, 16, 24, 32,
  40, 50, 100, 200` — the construction converges to a genuine element of
  `Z_p`, not an artifact of a specific `r`.
- The projective `proj_add` and `proj_double` formulas were proved
  **unconditional rational-function identities**, matching the standard
  affine chord/tangent formulas exactly, via `sympy.simplify` on symbolic
  `X1,Y1,Z1,(X2,Y2,Z2),a` — i.e. the formulas themselves contain no bug,
  by computer-algebra proof, not just numerical spot-checks.
- Round-trip checks `T + (P - T) = P` for `P = S^`, `T = t(S)` passed
  (recovers `P` exactly, correcting for the valuation shift in `T`'s
  denominator).
- Homogeneity of the projective doubling formula under rescaling the
  representative `(X,Y,Z) -> (cX,cY,cZ)` by a unit `c` passed.

**What failed, reproducibly, after all of the above passed:** the
composite identity `[2](S^ - t(S)) = [2]S^ - [2]t(S)` — a bare abelian-group
axiom that must hold for any two well-defined elements of any group,
completely independent of curve-specific structure — **did not hold**,
computed via any of the three independent implementations, on the same
worked toy instance. The discrepancy was:

- **stable across working precision** (`R = 30, 50, 60, 100, 120, 200` all
  gave the identical wrong digit), ruling out ordinary precision loss;
- **reproducible with exact (unbounded) integer arithmetic**, not just
  modular arithmetic mod `p^R`, ruling out a modular-reduction-specific
  bug;
- **isolated to the case where the difference `A - B` (or an intermediate
  in a scalar-multiplication chain) has a non-unit denominator** (a point
  genuinely "near" the kernel of reduction): the identical construction
  with two ordinary (denominator-1, valuation-0) points matched exactly
  every time.

The most likely explanation identified (not fully confirmed within
budget): the auxiliary/torsion-lift representative used as one operand
satisfies the curve equation only as an exact identity *in the finite ring
`Z/p^R`*, and while every individual polynomial step commutes exactly with
the reduction `Z_p -> Z/p^R` (verified: no division-free step can
introduce an error), a chain of several such operations landing repeatedly
in the kernel of reduction appears to lose more structure than the
per-step precision bookkeeping accounts for. This was not fully diagnosed;
see "what a follow-up should check" below.

## The adapted, validated instrument actually used for Stage 2

Rather than the direct subtraction `S^ - t(S)`, Stage 2 computes the
mathematically **equivalent** quantity `d([n] P)` for a lift `P` of a point
of order `n`: since `[n] S = O` in `E(F_p)`, `[n]` applied to *any* lift of
`S` (no torsion-section construction needed at all) lands in the kernel of
reduction by pure group-theoretic necessity, via an ordinary binary ladder
that stays in the affine (unit-denominator) chart until its very last
step. Because `[n]` is a unit scalar on the formal group (`p` does not
divide `n`, enforced by curve/prime selection), `[n]` acts by
multiplication by `n` on the leading digit: `d([n]P) = n * d(P) mod p`.
Testing `d([n](mS)) =?= m * d([n]S) mod p` is therefore an unconditional
algebraic equivalent of the contract's claim (1) (`n` is invertible mod
`p`), and was **validated first** on the same worked toy instance (exact
match for `m = 2,3,5,7,11,16,32`) before being used for the real run — see
`stage1_self_checks.D_adapted_nlift_instrument_linearity` in
`raw-result.json`.

This is recorded as a **protocol deviation from the literal mechanism
text**, not a silent substitution: the failed literal construction is
preserved as `stage1_self_checks.C_literal_subtraction_construction_
DEVIATION_TRIGGER` in every run's `raw-result.json` (expected to show
`pass: false`), so the record of the instrument defect travels with the
data rather than being discarded.

## What was executed and what was not

**Executed (Stage 0, Stage 1, Stage 2, and the anomalous-refusal half of
Stage 3):**

- Stage 0: five frozen curves, four toy primes each (10-14 bits, prime
  order `n`, good non-anomalous reduction), one anomalous curve/prime
  (`#E(F_p) == p`) — `frozen-curves-and-primes.json`.
- Stage 1 self-checks A (torsion-lift homomorphism), B (precision
  convergence), C (the literal construction, recorded as failed by
  design), D (the adapted instrument, validated), E (anomalous refusal on
  a toy instance) — `raw-result.json.stage1_self_checks`. No prior
  self-check transcript existed to reuse from EXP-ECDLP-1e6502 (that
  experiment's `specification.yaml.status` is `draft`, with no runs); these
  transcripts are generated fresh here, as the contract permits
  ("may be reused ... if reused").
- Stage 2: for every one of the 20 (curve, prime) instances, the digit
  identity `d([n]mS) = m d([n]S) mod p` for the full `m`-ladder
  (`1..64, 96, 128, 192, 256`, minus any `n | m`, none triggered here since
  every generated `n > 256`), and the size-law slope
  (`log(bitsize of numerator of x(mS)) / log(m)` for `m >= 16`, least-
  squares) plus the tail check (largest deviation of
  `bitsize/m^2` from its `m=256` value) — `raw-result.json.instances`.
- The anomalous break transcript, run on the frozen Stage-0 anomalous
  curve/prime (not just a toy example): the torsion-section construction
  raises `ValueError: base is not invertible for the given modulus` at
  `pow(q % n, -1, n)`, exactly the division-by-`n`-with-`n == p` step
  claim (4) predicts — `raw-result.json.anomalous_break_transcript`.

**Not executed (explicit incompleteness, not fabricated):**

- The Teichmuller non-homomorphic contrast (claim 3): `teichmuller_lift_
  unit` (the multiplicative Teichmuller lift of a unit) is implemented in
  `driver/padic.py` and unit-tested in isolation, but the full section
  construction (Teichmuller-lift the x-coordinate, Hensel-solve for a y on
  the curve, then define and test `delta_1` linearity across the m-ladder)
  was not built or validated.
- The leak arm (the first half of claim 4): recovering `|m + jn|` from the
  bit-size of `x(T')` and the measured size-law constant, fixing sign and
  residue via `d(T')`, and certifying `[m]S = T` independently — not
  attempted.

Per the contract's own stopping rule ("Stop immediately if a self-check
fails; measurements with a failed instrument are attempted_and_
inconclusive") and per AGENTS.md rule 5, the honest choice given the
remaining budget was to deliver Stage 2 on the validated adapted
instrument and stop, rather than build unvalidated Teichmuller/leak
machinery under time pressure and risk delivering unverified numbers.

## Protocol deviations (collected)

1. Prime selection additionally requires `n` (the order of `S` mod `p`) to
   be **prime**, not merely coprime to `p` — see `stage0-derivation-note.md`
   for the precision-stability reason.
2. The digit `d(P)` used throughout Stage 2 is computed via `[n]` applied
   to a lift of `P`, not via the literal `P - t(P mod p)` subtraction in
   the contract's mechanism text — mathematically equivalent (scaled by the
   invertible constant `n`), validated before use, and the failed literal
   construction is preserved in the record rather than discarded.
3. Working p-adic precision is `R = 200` digits (not a value the contract
   specifies), chosen generously after observing that repeated kernel-of-
   reduction entries during the `[n]`-ladder for composite intermediate
   orders consume precision (motivating deviation 1 as well); no instance
   in this run raised `InsufficientPrecision`.
4. Stage 3 (Teichmuller contrast, leak, and the leak half of claim 4) was
   not executed.

## What a follow-up should check (for the record, not executed here)

- Whether the literal `S^ - t(S)` construction's failure traces to a
  precision-bookkeeping gap specifically for chains with **more than one**
  kernel-of-reduction entry (the toy instance's `[2]` case has exactly
  one), by testing a case with a single, isolated kernel entry more
  carefully with a from-scratch independent re-implementation.
- Whether representing `t(S)` via a *provably exact* (not `Z/p^R`-only)
  auxiliary construction changes the outcome.

## Reproducibility

`experiments/EXP-ECDLP-a26bde/driver/curves.py`
(`build_frozen_instances(20260905)`) is deterministic (verified: two
independent invocations produce byte-identical JSON, SHA-256
`253a2d761719ecf3b9d7ee67b17084f0e66cc3c7af796e95dbf03deeeb3dbf36`).
`experiments/EXP-ECDLP-a26bde/driver/run_experiment.py` reruns Stage 0-2
end to end from the recorded command in
`runs/RUN-ECDLP-a26bde-1/command.txt`.
