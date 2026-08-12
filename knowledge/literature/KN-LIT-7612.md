---
id: KN-LIT-7612
type: literature
title: "Security Analysis on UOV Families with Odd Characteristics: Using Symmetric Algebra"
authors:
  - "Yi Jin"
  - "Yuansheng Pan"
  - "Xiaoou He"
  - "Boru Gong"
  - "Jintai Ding"
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2025/1137 (last updated 2026-07-29)'
identifiers:
  eprint: iacr:2025/1137
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2025/1137
tags: [uov, qr-uov, multivariate, xl-algorithm, exterior-algebra, symmetric-algebra, key-recovery, odd-characteristic, polynomial-system, nist-pqc, algebraic-attack, adjacent]
confidence: reported
citation_verified: web
added: "2026-07-29"
superseded_by: null
---

## Contribution
Generalizes Lars Ran's exterior-algebra XL key-recovery attack on UOV, which applied
**only in characteristic 2**, to UOV instances over fields of **any characteristic**.

The vehicle is a proposed notion of **reduced symmetric algebra**, which the authors
state degenerates to symmetric algebra when `char = 0` and to exterior algebra when
`char = 2` — so Ran's construction becomes the characteristic-2 special case of a
single object.

## Key claims (as reported)
- A new XL attack against all UOV families, built on the reduced symmetric algebra,
  extending Ran's approach past the characteristic-2 restriction.
- It applies to the 12 recommended **QR-UOV** instances submitted to NIST's PQC
  standardization project.
- **It does not outperform existing key-recovery attacks on those instances.** The
  authors state this directly; the contribution is reach and structural insight, not a
  reduced attack cost.
- The analysis exposes a connection between the field characteristic `p` and the
  concrete hardness of UOV instances.

## Relevance to this program
Ingested for the **algebraic-attack machinery**, not for UOV. The program's
index-calculus work turns on solving structured polynomial systems, and
`KN-TECH-053` (XL / BooleanSolve / crossbred) is the existing technique entry for
exactly this family of solvers.

The transferable observation is methodological and narrow: an attack whose reach was
believed to be a **characteristic-2 phenomenon** turned out to be the degenerate case
of a construction that works in any characteristic, once the right algebra was named.
The program's summation-polynomial and Weil-descent work is heavily characteristic- and
field-specific, so a worked instance of "the characteristic restriction was an artifact
of the chosen algebra, not of the problem" is worth having on file.

That is an **analogy, not a result**. Nothing here bears on the ECDLP, on summation
polynomials, or on any elliptic-curve system. UOV is a multivariate-quadratic
signature family and the systems involved are unrelated in structure to Semaev
summation polynomials. **Does not bear on the ECDLP.** No claim-tier change and no
revision to `KN-TECH-053` is asserted.

Note also the honesty pattern worth mirroring: the paper states plainly that its new
attack does **not** beat existing attacks. That is the Pareto-domination honesty
`KN-TECH-056` requires.

## Not verified here
Full paper not read; all claims relayed from the ePrint abstract retrieved
2026-07-29 (hence `confidence: reported`). ePrint metadata: Paper 2025/1137,
category "Attacks and cryptanalysis", last updated 2026-07-29.

NOT verified here: that the reduced symmetric algebra specializes as described; that
the resulting XL attack is correct or applies to the 12 QR-UOV instances; the claimed
characteristic-hardness connection; and the comparison against existing key-recovery
attacks. No independent complexity check was performed.
