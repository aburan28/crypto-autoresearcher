---
id: KN-TECH-041
type: technique
title: Basis profiles, the Geometric Series Assumption, and BKZ simulation
tags: [gsa, geometric-series-assumption, bkz, simulator, basis-profile, gram-schmidt, heuristic, block-size, security-estimate, lattice]
confidence: reported
complexity: not an algorithm cost; a predictor mapping block size b to the log Gram-Schmidt profile from which attack success conditions are read
applicability: every concrete lattice security estimate; the shared substrate of the primal attack, the dual attack, and NTRU fatigue analysis
source_refs: [KN-LIT-100, KN-LIT-101, KN-LIT-107, KN-LIT-123, KN-TECH-038, KN-TECH-039]
added: 2026-07-24
superseded_by: null
---

## Method
Lattice attack costs are not measured; they are predicted from the *shape of the
reduced basis*. Plot `log ||b*_i||` against `i` for a BKZ-reduced basis and the
resulting profile determines whether the attack succeeds. Two predictors are in
use:

- **The Geometric Series Assumption** (KN-LIT-100): the profile is a straight
  line, `||b*_i||^2 / ||b_1||^2 = q^(i-1)` with `3/4 <= q < 1`. Simple enough to
  invert analytically for a required block size, which is why success conditions
  are usually stated in closed form.
- **BKZ simulation** (KN-LIT-101): simulate BKZ's action on the profile
  numerically instead of assuming a line, giving approximate output quality and
  running time at block size `>= 50`.

## Known failure modes, stated by the sources themselves
This is a heuristic layer, and the sources say so plainly.

- Schnorr introduced the GSA to *simplify analysis* and immediately noted the
  quotients only approximate a geometric series; LLL-reduced bases have bad GSA
  behaviour, and only BKZ-reduced bases closely approximate the line.
- The profile deviates at the **head and tail** -- the first and last few `b*_i`
  routinely violate the GSA, and the tail behaviour is well enough understood to
  be simulated separately.
- KN-LIT-123 makes the general point: the worst-case theorems are asymptotic and
  not tight on cryptographic instances, so predictions rest on heuristics "some
  of which are known to fail for relevant corner cases."
- The most consequential known corner case is the NTRU overstretched regime,
  where reduction behaves far better than the profile predicts because a dense
  sublattice is present (KN-TECH-045). The failure was substantial enough to
  hide an entire attack regime for years.

## Applicability limits
A GSA-derived block size is a prediction from an assumption known to be false in
detail, calibrated in dimensions far below cryptographic ones. It is adequate for
parameter selection with margin -- its intended purpose -- and inadequate as the
sole support for a claim that one algorithm beats another by a modest factor,
since the modelling error is plausibly of that size. Where a claim depends on
the profile, the honest form states the predictor used, the dimensions where it
has been validated, and whether the instance class is one where the predictor is
known to fail.

## Verified vs reported
The GSA statement, its stated status as a simplification, and the observation
that LLL bases violate it while BKZ bases approximate it are read directly from
KN-LIT-100. The simulator's existence and stated range are read from
KN-LIT-101's abstract. The head/tail deviation is reported from secondary
sources encountered while verifying KN-LIT-100 and has not been checked against
a primary analysis. No basis profile has been computed in this repository.
