---
id: KN-LIT-7664
type: literature
title: "Unified Dual Attack Analyses: Covariance-Based Score Distribution Prediction for LWE"
authors:
  - "Yechen Li"
  - "Qunxiong Zheng"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1048"
identifiers:
  eprint: "iacr:2026/1048"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1048"
tags: [dual-attack, lwe, kyber, ml-kem, dilithium, independence-heuristic, score-distribution, concrete-security, cost-model, modulus-switching, lattice-estimator, methodology]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A **unified predictive model for the expectation and variance of the score** in dual
attacks on LWE, covering three variants: the original dual attack, the dual attack with
modulus switching, and the dual attack with decoding (Crypto 2025).

The stated motivation is a **known defect in the literature**: analysis of the score
distribution for the correct guess has "consistently relied on a **flawed independence
assumption**," producing variance estimates far below the true score variance. The
authors note this has been highlighted in several studies, and that the
Bashiri–Wiemers (JMC 2025) variance estimate **performs poorly in medium-to-high
dimensions** in their experiments.

The key technical observation: the **cosine of the angle between distinct short vectors
is normally distributed**, which the authors use to estimate the covariance between
individual contributions rather than assuming independence.

## Key claims (as reported)
- A unified expectation/variance model across three dual-attack variants.
- The independence assumption underlying prior analyses is flawed; true variance is
  substantially larger than estimated.
- Bashiri–Wiemers's correction is reported to perform poorly in medium-to-high
  dimensions.
- Context relayed: **some prior dual-attack claims suggested CRYSTALS-KYBER security may
  fall below the NIST threshold.** This entry records that as a *claim in the
  literature the paper is responding to*, **not** as an assessment — and the paper's own
  contribution is a *correction to the analysis*, which historically has moved such
  claims back up rather than down.

## Relevance to this program
**A direct 2026 increment to [[KN-OPEN-016]]**, which asks what the dual attack actually
costs once its heuristics are repaired, and to [[KN-TECH-039]], which already records the
dual-sieve dispute and warns that this attack's analysis is error-prone. This paper is a
repair attempt on exactly the heuristic those entries flag.

The pattern: an attack's cost is estimated by treating many correlated contributions as
independent, because the independent case is analytically tractable. The estimate then
comes out too good. Ducas–Pulles (Crypto 2023) raised this for dual attacks
([[KN-LIT-111]]); it is still being litigated in 2026 across four independent papers
this sweep found — this one, [[KN-LIT-7665]], [[KN-LIT-7666]], and [[KN-LIT-7668]],
which hits the same defect inside a sieve cost model.

Why the program should care beyond lattices: **the same failure mode is available in
index-calculus yield estimation.** Relations harvested from a factor base are not
independent, and smoothness-probability models that assume they are will overstate
yield. `KN-TECH-035` and the program's own yield-calibration experiments
(`EV-ECDLP-008`..`010` in the ledger) are about exactly this. A well-documented external
instance of the failure mode, with a proposed covariance-based fix, is directly
reusable.

**Does not bear on the ECDLP** as a result; it bears on the program's *methodology* for
estimating any attack whose cost aggregates correlated trials.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1048,
retrieved 2026-08-01 (hence `confidence: reported`); the abstract is truncated in the
retrieved record. Citation checked against the ePrint record: title, two authors, report
number, year 2026.

NOT verified here: the covariance model; the normality claim for the cosine of angles
between short vectors; the experimental comparison against Bashiri–Wiemers (JMC 2025);
and the attributions to that work or to Crypto 2025. **The relayed context that some
dual-attack claims put Kyber below the NIST threshold is neither endorsed nor assessed
here** — no ML-KEM parameter set is evaluated by this program, and this paper is a
correction to the analysis rather than a break.
