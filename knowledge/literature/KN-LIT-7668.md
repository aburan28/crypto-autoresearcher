---
id: KN-LIT-7668
type: literature
title: "Sharper and Closed-Form Attacks on SIS When Modulus Is Small"
authors:
  - "Navid Abapour"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1349"
identifiers:
  eprint: "iacr:2026/1349"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1349"
tags: [sis, isis, large-norm-attack, bdgl-sieve, falcon, mitaka, dilithium, forgery, cost-model, independence-heuristic, concrete-security, lattice]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Two extensions of the **Large Norm attacks** of Ducas–Espitau–Postlethwaite (Crypto
2023) on the **ISIS** problem, which showed small `q` permits recovery of short
solutions and were applied to Falcon and Mitaka.

The two identified defects and their fixes:

1. **The cost model oversimplifies the BDGL sieve**: it does not account for how long
   vectors are distributed, and **treats two dependent probabilistic events as
   independent**, overestimating attack cost. The authors incorporate the principal
   sieve length distribution into the success-probability estimate and use a **joint
   probability** rather than an approximate factor where possible.
2. **The analysis covers only the `ℓ₂` norm**, not `ISIS^∞`, which underlies
   Dilithium-type systems. The authors add a closed-form `ℓ_∞` variant.

## Key claims (as reported)
- Large Norm cost on **Falcon-256** reduced by an ≈**11× cheaper model**.
- A **Mitaka-512 signature forged in ≈4.5 seconds** at a higher success rate.
- A closed-form `ℓ_∞` "Z-shape" attack against Dilithium-type `ISIS^∞` at
  small-to-moderate modulus, succeeding in **≤1.6 seconds across three presets**.

**Scope, stated plainly:** Falcon-**256** and Mitaka-**512** are not the deployed
Falcon-512/1024 parameter sets, and the `ℓ_∞` result is qualified as
*small-to-moderate modulus*. Nothing here is claimed against a standardised parameter
set, and this entry claims nothing.

## Relevance to this program
The **third independent instance in this one sweep of the same methodological defect**:
a cost model that treats dependent probabilistic events as independent, and thereby gets
the attack's cost wrong. [[KN-LIT-7664]] finds it in dual-attack score variance;
[[KN-LIT-7666]] navigates around it via the contradictory-regime argument; here it
appears inside a sieve cost model, where correcting it makes the attack **cheaper** by
≈11×.

That direction is worth emphasizing. The independence heuristic is usually discussed as
something that makes attacks look *too good*; here removing it made an attack look
*better still*, because the dependence was in the defender's favour in the original
accounting. **The lesson is not "independence assumptions flatter attackers" — it is
that an unexamined independence assumption makes a cost model unreliable in an
unpredictable direction.** That is a sharper statement of what `KN-TECH-035` requires,
and it generalizes directly to this program's own yield estimates for index calculus,
where relation-harvesting trials are not independent either.

Also relevant: the **norm matters**. An analysis valid in `ℓ₂` does not transfer to
`ℓ_∞` for free, and Dilithium-type schemes live in `ℓ_∞`. Compare [[KN-LIT-7669]],
which attacks SIS in *any* norm from the Gaussian-sampling side.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1349,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, sole author Navid Abapour, report number, year 2026.

NOT verified here: the sieve-length-distribution correction; the joint-probability
treatment; the ≈11× Falcon-256 figure; the 4.5-second Mitaka-512 forgery; the
≤1.6-second `ℓ_∞` results or which three presets they cover; and the attribution to
Ducas–Espitau–Postlethwaite (Crypto 2023). **No claim is made or implied about
Falcon-512/1024 or any standardised Dilithium parameter set.**
