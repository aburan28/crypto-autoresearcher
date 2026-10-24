---
id: KN-FIND-c71e5d
type: internal_finding
title: >-
  F_p^* calibration of Smart-style section recovery: Teichmuller kills
  log_p, the naive integer section succeeds exactly when g^d mod p^2 < p
  (archimedean no-carry region), so a 1/p null is wrong for structured
  sections
tags:
  - ecdlp
  - p-adic-lift
  - smart-attack
  - fermat-quotient
  - multiplicative-group
  - section-calibration
  - exact-null
  - negative-boundary
  - toy-tier
  - czlift
confidence: established
confidence_note: >-
  Established for the scoped statement only. The success and homomorphism
  criteria are elementary consequences of Eisenstein's logarithmic property
  of the Fermat quotient (derivation, EV-CZLIFT-f2a401) and were reproduced
  on 3200/3200 archived rows by two independent implementations (validator
  sealed blind code; red-team own code). The rates are toy-scale
  measurements on two seeds. Reviewer model identities are reported, not
  probe-verified.
evidence_level: toy_tier_two_seed_with_derivation
source_refs: []
internal_refs:
  - EV-CZLIFT-f2a401
  - DEC-20261023-039ddf
  - EXP-CZLIFT-bdae69
  - H-CZLIFT-d37231
  - RUN-CZLIFT-0cefcd
  - RUN-CZLIFT-a5c1da
related_refs:
  - RQ-CZLIFT-b9f765
  - GOAL-CZLIFT-1516d5
  - DEC-20261009-44c288
  - KN-TECH-73630e
proof_status: derivation
proof_refs:
  - experiments/EXP-CZLIFT-bdae69/analysis.md
  - experiments/EXP-CZLIFT-bdae69/reports/validation-20261022/validation_report.yaml
  - experiments/EXP-CZLIFT-bdae69/reports/validation-20261022/blind/fq_blind.py
  - experiments/EXP-CZLIFT-bdae69/reports/redteam-20261023/redteam_report.yaml
  - experiments/EXP-CZLIFT-bdae69/reports/redteam-20261023/r2_nulls.py
  - experiments/EXP-CZLIFT-bdae69/reports/redteam-20261023/r2_nulls_output.json
added: '2026-10-23'
superseded_by: null
---

# Exact nulls for Smart-style section recovery on F_p^*

A scoped boundary from `DEC-20261023-039ddf` (`reject_scoped`, strong,
toy). It records what a non-canonical section of Z_p^* -> F_p^* recovers
under the functional log_p(s(x)^{p-1}) and why a uniform 1/p null is wrong
for structured sections. It is a calibration, not a discrete-log result.

## Exact observed scope

F_p^* only. Two seeds (`RUN-CZLIFT-0cefcd` seed 20261009,
`RUN-CZLIFT-a5c1da` seed 20261010), each 40 seeded primes 50 < p < 2000 with
40 pairs (1600 pairs per seed), d uniform in [2, p-3], precision 4, g the
smallest primitive root (sympy.primitive_root, frozen in run.py). Sections:
Teichmuller, naive integer representative in [1, p-1], random-digit Hensel.

| quantity | seed 20261009 | seed 20261010 |
|---|---|---|
| Teichmuller hom / vanishing / ratio defined | 1600 / 1600 / 0 | 1600 / 1600 / 0 |
| naive success (z vs mean 1/p) | 13 (7.65) | 20 (9.14) |
| naive sub-p / band / rest successes | 11/11, 0/14, 2/1575 | 13/13, 0/20, 7/1567 |
| naive exact conditional expectation | 11.55 | 17.64 |
| Hensel success (z) | 1 (-0.73) | 2 (-0.73) |
| naive hom (exact P(xy < p) expectation) | 10 (9.35) | 10 (12.96) |
| Hensel hom (p^-3 expectation) | 0 (2.2e-5) | 0 (2.3e-4) |

Pooled: naive 33 against 5.39 at mean 1/p (ratio 6.13, 95% CI 4.22-8.61),
but 33 against 29.19 under the exact null (1.13, CI 0.78-1.59); Hensel 3
against 5.39 (0.56, CI 0.12-1.63).

## The rule (derivation)

For the naive section the functional reads the Fermat quotient
q_p(a) = (a^{p-1} - 1)/p mod p. By Eisenstein's logarithmic property, with
g^d = r + kp (0 <= r < p), the Smart-style ratio is d + k/(r q_p(g)) mod p.
So, when q_p(g) != 0 mod p:

- success iff g^d mod p^2 < p;
- every pair with g^d < p succeeds (the no-carry region);
- no pair with p <= g^d < p^2 can succeed;
- pairs with g^d >= p^2 succeed at about 1/p (rule-A population ratio
  0.984 +/- 0.085, review-side).

The naive section is homomorphic exactly when x*y < p as integers; a
random-digit Hensel section with probability p^-3 per pair. The Teichmuller
section is a homomorphism into mu_{p-1} and log_p vanishes on it, so its
ratio is never defined.

## Use

- A contract that scores a non-canonical section against 1/p must first
  compute the exact null for that section and generator. Under the smallest
  primitive root the frozen 4-sigma test falsifies a 1/p prediction with
  probability about 0.94 per seed (red-team rule-A simulation); under a
  uniformly random primitive root the expected z is 0.18 +/- 1.21
  (review-side, not run evidence).
- Successor G_m calibrations carry the red-team controls: generator-rule
  arms, the per-row exact null split into sub-p, band and rest with a
  clumping-aware variance, homomorphism predictions P(xy < p) and p^-3, and
  power sized for a 1.5x excess (about 64 expected null events).

## Limits

- No discrete-log leverage: the certain instances (g^d < p) are solved by
  an O(log p) integer logarithm; elsewhere success is about 1/p per attempt,
  dominated by Pollard rho and index calculus.
- Does not refute Hom(Z/(p-1), Z_p) = 0; the refuted part was an implicit
  random-model assumption about a structured section.
- G_m only; no elliptic-curve or deployed-curve statement. A review-side
  computation (RT-20261023-2411b8, not a run record) shows that an elliptic
  analogue exists. The integral section on a small-coefficient global model
  recovers d exactly at the integral multiples of the global lift: 37a1 short
  model, 1420/1420 at d = 2..6, and y^2 = x^3 + 17, 287/287 at d = 2. That set
  is Siegel-finite (recalled) and does not grow with p. The analogue depends
  on the Weierstrass model and the lift convention.
- Not carried from the source records: the specification's on_positive note
  as worded, the claim that non-canonical sections are homomorphic on about
  1/p of pairs, and the sentence of DEC-20261009-44c288 that the excess has
  no elliptic analogue.
