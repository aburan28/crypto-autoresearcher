# BINSTD n=17 invariant-dimension table lacks a Lean module bridge

- **Status:** open
- **Kind:** formalization and semantic-fidelity gap
- **Affected work:** `EXP-BINSTD-8bdf86` Stage-1 admissible-dimension
  files, `H-BINSTD-5a212b`, and any claim that the table
  `{0,1,8,9,16,17}` is completely certified in Lean
- **Next action owner:** formal proof lane for the factor and module
  lemmas; independent Reviewer for semantic fidelity
- **Last updated:** 2026-10-22

## Problem

The frozen n=17 BINSTD runs use the factorization of `x^17-1` over
`F₂` to label dimensions 3 and 4 structurally inadmissible and
dimensions 8 and 9 admissible. The
[Lean product theorem](../formal/CryptoResearch/Binstd/Factorization.lean)
proves the archived bitmask polynomials 3, 313 and 471 multiply to
`X^17+1`. The
[Lean irreducibility theorem](../formal/CryptoResearch/Binstd/Irreducibility.lean)
proves both degree-eight factors irreducible. These theorems do not
connect the factors to every Frobenius-invariant subspace of the
archived field. A
[canonical-field theorem](../formal/CryptoResearch/Binstd/CanonicalFrobenius.lean)
identifies the minimal polynomial of Mathlib's `GaloisField 2 17`
Frobenius with the same product, but does not bind the runner's
polynomial-basis implementation to that canonical field.

## Evidence and uncertainty

- **Observed:** Both frozen Stage-1 dimension files have SHA-256
  `6f09e6c620fc3765a8ef97951d5c6f84f9b1290a908f487c998bdef51bc60e74`.
  The [source-binding receipt](../docs/reports/2026-10-22-binstd-factor17-lean/source-binding.json)
  decodes the Lean definitions back to bitmasks 3, 313 and 471.
- **Machine proved:** The
  [formal receipt](../docs/reports/2026-10-22-binstd-factor17-lean/proof-verification.json)
  reports `machine_verified` for the exact product identity under
  Lean 4.35.0-rc1. The
  [irreducibility receipt](../docs/reports/2026-10-22-binstd-irred-lean/proof-verification.json)
  reports `machine_verified` for both degree-eight factors, a passing
  full build, standard axioms only across 625 audited theorems, and a
  passing target audit. Independent semantic review remains pending.
- **Canonical model:** The
  [Frobenius receipt](../docs/reports/2026-10-22-binstd-canonical-frobenius/proof-verification.json)
  reports `machine_verified` for order 17 and the factor-product
  minimal polynomial on `GaloisField 2 17`, with a passing full build,
  standard axioms only across 630 audited theorems, and a passing
  target audit. This is an abstract-field result, not a runner model
  binding; independent semantic review remains pending.
- **Separate finite check:** The
  [source-pinned toy replay](../docs/reports/2026-10-22-binstd-ell89-replay/report.md)
  performed independent Rabin and polynomial-product calculations
  and reproduced both archived yield matrices. It is not a Lean
  invariant-subspace theorem.
- **Missing capability:** Lean proofs that the archived field modulus
  defines the claimed 17-dimensional field, that its `x↦x²` map
  agrees with the canonical-field Frobenius, and that this map has
  exactly the invariant-subspace dimensions given by the subset
  sums of the three simple factors.
- **What this does not establish:** The gap is not evidence that the
  archived toy table is false. It does not change any hit count,
  empirical yield decision, attack cost, security status or
  performance dashboard value.

## What would unblock it

- [x] Prove the two degree-eight factors irreducible over `ZMod 2`
  and bind their coefficients to frozen bitmasks 313 and 471.
- [ ] Prove the archived modulus `t^17+t^3+1` gives the intended
  finite field and identify the actual runner Frobenius with the
  canonical `GaloisField 2 17` Frobenius. The canonical map's order
  and minimal polynomial are proved; the runner binding is not.
- [ ] Prove that invariant subspaces correspond to ideals or
  direct sums of the three simple factors, yielding exactly
  `{0,1,8,9,16,17}`; bind the construction used by the runner
  to those kernels.
- [ ] Obtain independent semantic review of the exact Lean
  statements against the frozen experiment and source.

These steps would certify the structural dimension table in Lean.
They would not prove the empirical relation-yield counts or any
performance claim.

## Next discriminating step

Formalize the archived field modulus and the normal-basis module
bridge, then show that the runner's subspace constructor realizes the
factor-kernel classification.
Preserve the frozen runs and their existing review decisions; this
problem authorizes no new experiment.

## Resolution and history

2026-10-22: Named after the exact factor product was machine verified.
The [factorization graph](../docs/reports/2026-10-22-binstd-factor17-lean/factorization.dot)
marks the then remaining steps as open. Later the
[irreducibility graph](../docs/reports/2026-10-22-binstd-irred-lean/irreducibility.dot)
records the two degree-eight factors as proved and the module bridge
as open. The later
[canonical Frobenius graph](../docs/reports/2026-10-22-binstd-canonical-frobenius/canonical-frobenius.dot)
adds its abstract-field minimal polynomial while keeping the runner
binding and classification open. No canonical performance graph changes
because these are structural proof obligations.
