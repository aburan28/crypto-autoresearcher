---
id: KN-LIT-7659
type: literature
title: "Coppersmith's Method for Solving Modular Inversion Hidden Number Problem via Determinant-Based Elimination"
authors:
  - "Zhaopeng Ding"
  - "Zhaopeng Dai"
  - "Baofeng Wu"
  - "Rundong Wang"
  - "Yanshuo Zhang"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/423"
identifiers:
  eprint: "iacr:2026/423"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/423"
tags: [coppersmith, hidden-number-problem, mihnp, lattice, lll, shift-polynomial, prng, inversive-congruential, cryptanalysis, disproved-conjecture, elliptic-curve]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A **determinant-based strategy for selecting shift polynomials** in Coppersmith's
method for multivariate modular equations — the step the authors call the pivotal and
hardest part of instantiating Coppersmith.

Validated on the **Modular Inversion Hidden Number Problem (MIHNP)** and on predicting
the **Inversive Congruential Generator (ICG)**, where it is reported to outperform
prior methods in theory and in practice.

Applied to the **Modular Inversion Double Hidden Numbers Problem (MIDHNP)**, the
analysis is reported to show **MIDHNP is not harder than MIHNP**, thereby
**disproving a conjecture of Boneh, Halevi and Howgrave-Graham (Asiacrypt 2001)**.

## Key claims (as reported)
- New determinant-based shift-polynomial selection; an improved Coppersmith variant for
  certain multivariate modular equations.
- Outperforms prior MIHNP and ICG methods, theoretically and experimentally. No bounds
  or timings appear in the abstract.
- **MIDHNP ≤ MIHNP in hardness**, disproving a 25-year-old conjecture. This is the
  paper's strongest claim and it is a **negative result about an assumption**, not an
  attack on a deployed scheme.

## Relevance to this program
The **hidden number problem is the program's canonical lattice-meets-elliptic-curve
attack surface**: HNP with lattice reduction is how biased-nonce ECDSA key recovery
works, and the corpus tracks it under `hidden-number-problem` (19 entries) and
`ECDSA lattice attack` (50). MIHNP is its modular-inversion variant.

Two reasons to hold this entry:

- **Shift-polynomial selection is the reusable part.** Coppersmith's method is
  ubiquitous in this program's adjacent literature (RSA variants, HNP, small-root
  problems), and the recurring practical obstacle is exactly which shift polynomials to
  include — the lattice's determinant-versus-dimension trade decides whether LLL
  succeeds. A systematic determinant-based criterion is a technique, not a one-off.
- **A disproved hardness conjecture is a high-value corpus item.** Under
  `docs/inventor-protocol.md`, a documented case of an assumption believed hard for two
  decades turning out to reduce to a weaker one is exactly what the corpus should hold
  so the Idea Generator does not re-propose into a closed region — and so the program
  keeps calibrated on how often "long-standing conjecture" survives.

**Does not bear on the prime-field ECDLP** in the plain model. It bears on the
**leakage** model — MIHNP-style problems arise from partial-information side channels,
not from the group law. That boundary is the one [[KN-OPEN-011]] and [[KN-OPEN-018]]
already police.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/423,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, five authors, report number, year 2026.

NOT verified here: the determinant-based selection strategy; the claimed theoretical
and practical improvements over prior MIHNP/ICG methods (**no bounds or timings are
stated in the abstract**); and the MIDHNP result. **The disproof of the Boneh et al.
conjecture is relayed, not checked** — it is a strong claim resting on the paper's own
analysis, and the Asiacrypt 2001 source is not an entry in this corpus. Related but
distinct existing entries: [[KN-LIT-7020]] and [[KN-LIT-5145]] on MIHNP.
