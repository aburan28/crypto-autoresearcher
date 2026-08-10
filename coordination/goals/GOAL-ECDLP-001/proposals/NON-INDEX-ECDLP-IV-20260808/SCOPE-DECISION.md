# Proposed scope decision — prime-field non-generic hardness census

## Status

`PROPOSED / NOT DISPATCHED`

This is a Coordinator design artifact created in response to the redirect from
the broad isogeny-class lane. It does not change the official goal status and
does not promote a mathematical conclusion. Dispatch remains blocked by the
harness preflight's missing-backend check.

## Decision target

Determine whether ordinary prime-order curves over a prime field can be measurably
easier than matched random curves through either of two public mechanisms:

1. an efficiently computable automorphism quotient of Pollard rho; or
2. a short, invertible, explicitly computed isogeny to a target with a useful
   automorphism or endomorphism quotient.

The primary comparison is charged end-to-end work, not a feature score, raw
scalar-multiplication timing, or a transfer-only observation.

## Scope in

- ordinary curves over `F_p` with a recorded large prime subgroup order `ell`,
- explicitly defined `F_p`-rational automorphisms and subgroup eigenvalues,
- negation-only, automorphism-quotiented, and baseline Pollard-rho walks,
- low-degree `F_p`-rational isogeny chains with kernel/order checks,
- same-order and same-field matched controls,
- one-shot and amortized-many-target cost models,
- curve, subgroup, twist, anomalousness, embedding-degree, and cofactor checks,
- deterministic seeds, held-out primes, held-out curve families, and raw walk
  receipts,
- explicit fruitless-cycle, collision-correctness, and inverse-map checks.

## Scope out

- hidden scalar labels, chosen-input oracles, side channels, and fault models,
- supersingular-only conclusions unless separately labelled as a positive
  calibration control,
- extension-field descent claims presented as prime-field results,
- uncharged precomputation or an isogeny graph traversed to cryptographic size,
- a claim that a constant-factor quotient changes the generic ECDLP exponent,
- interpreting a timeout, missing backend, or failed implementation as a
  mathematical negative.

## Admission gates

1. The instance certificate must reject anomalous curves, small cofactors, and
   unintended small embedding degree from the primary ordinary-curve sample.
2. The automorphism must be defined over `F_p`, preserve the measured subgroup,
   and have a verified eigenvalue or a verified quotient action.
3. Every isogeny transfer must be invertible on the subgroup used by the DLP;
   the kernel intersection and degree/order gcd must be recorded.
4. Baseline, negation-only, full-quotient, and transfer runs must use matched
   seeds and the same success criterion.
5. Any positive signal must survive the independent Validator and Red Team
   tasks before it can affect a goal decision.

## Current operational gate

The design is frozen locally but not archived. `preflight.py --doctor` reports
that no inference backend is usable. Until a supported backend is configured,
the Executor, Validator, Red Team, snapshot, and ledger tasks remain queued.
