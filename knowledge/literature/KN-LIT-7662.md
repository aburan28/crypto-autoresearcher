---
id: KN-LIT-7662
type: literature
title: "Refined Approx-SVP Rank Reduction Conditions and Adaptive Lattice Reduction for MSIS Security Estimation"
authors:
  - "Xiaohan Zhang"
  - "Zijian Zhou"
  - "Longjiang Qu"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/607"
identifiers:
  eprint: "iacr:2026/607"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/607"
tags: [lattice, approx-svp, msis, bkz, sieving, dimension-for-free, gram-schmidt, concrete-security, cost-model, dilithium, security-estimate, lattice-estimator]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Systematizes and **refines the Approx-SVP rank reduction conditions** used in concrete
lattice security estimation, on the grounds that existing conditions are **overly
aggressive**: they implicitly assume access to a large number of extremely short lattice
vectors.

The authors identify that in the **dimension-for-free (D4f)** setting the essential
requirement is the existence of **a single sufficiently short vector**, and derive two
refined compact conditions — one from geometric properties of lattice sieving, one
incorporating a basis-quality-dependent probabilistic bound. Reported validated by
experiments in high dimensions, where the compact condition **outperforms prior methods
by up to a factor of 60 in dimensions 850 and 925**.

To realize the conditions they present **APBKZ**, an adaptive Pump-based reduction
strategy selecting blocksize and D4f parameters from the evolving **Gram–Schmidt
profile**, and **HeadAPBKZ**, a head-focused mode restricting reduction to a critical
prefix once the condition is met. These are combined into an improved concrete security
estimation framework for **MSIS**, applied to **Dilithium**.

## Key claims (as reported)
- Prior rank reduction conditions are too aggressive; the D4f-essential requirement is
  a single sufficiently short vector.
- Two refined compact conditions, validated experimentally; up to **60×** improvement
  over prior methods at dimensions 850 and 925.
- APBKZ / HeadAPBKZ adaptive reduction strategies.
- An improved MSIS concrete security estimation framework, applied to Dilithium. **The
  abstract is truncated at the point where the Dilithium conclusion is stated**, so the
  direction and size of any change to Dilithium's estimated security **is not recorded
  here**.

## Relevance to this program
A 2026 increment to [[KN-TECH-041]] (basis profiles, the Geometric Series Assumption,
and BKZ simulation) and to [[KN-TECH-040]] (core-SVP costing and the cost-model zoo),
complementing [[KN-LIT-7661]]'s reduction-tightness side.

- **This is a paper about the honesty of a cost model, not about a new attack.** Its
  claim is that a standard condition inside every MSIS/Dilithium estimate assumes more
  than an attacker gets. That is exactly the class of finding `KN-TECH-035` exists to
  surface — a cost model that quietly grants the adversary a free resource.
- **The Gram–Schmidt profile as the adaptive signal** is the reusable technique: choosing
  blocksize and D4f from the observed basis quality rather than from a fixed schedule.
  The corpus has 42 `BKZ` entries and 3 on `progressive BKZ`; adaptive strategies are
  under-covered relative to how much concrete estimation depends on them.
- **Direction of effect is unrecorded and must not be guessed.** A *refined* (less
  aggressive) rank-reduction condition would ordinarily make attacks look *harder* and
  security estimates *higher* — but the paper also reports a 60× improvement in the
  condition's effectiveness, which cuts the other way. **This entry does not state which
  way Dilithium moves**, because the abstract as retrieved does not.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/607,
retrieved 2026-08-01 (hence `confidence: reported`); the abstract is **truncated in the
retrieved record** at the Dilithium conclusion. Citation checked against the ePrint
record: title, three authors, report number, year 2026.

NOT verified here: the refined conditions; the 60× figure or the experimental setup
producing it; APBKZ/HeadAPBKZ; the estimation framework; and — explicitly — **any
conclusion about Dilithium's concrete security, which this entry does not state in
either direction**. No parameter recommendation in this program's ledger changes.
