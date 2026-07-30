---
id: KN-LIT-1894
type: literature
title: "Suppressing Hidden Extension-Field Linearity in Rank-Metric Cryptography via Structural Incompatibility"
authors:
  - "Dengchuan Liao"
  - "Xiangxue Li"
  - "Yu Yu"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/992"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/992"
tags: [cryptanalysis, extension-field, lattice, mov-fr, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A prominent line of rank-metric code-based cryptography has long relied on highly structured algebraic code families, such as Gabidulin codes, for their optimal rank-distance properties and efficient decoding. However, this structure exposes algebraic invariants (most notably extension-field linearity and Frobenius invariance) that enable powerful polynomial-time distinguishers and effective key-recovery attacks.

## Key claims (as reported)
- In this work, we revisit this structural tension from a new perspective.
- Rather than relying solely on masking, we identify a simple yet fundamental structural incompatibility that rules out the direct extension-field linear representation on which these attacks rely.
- Building on this insight, we introduce Enhanced Gabidulin Matrix Subcodes (EnGMS), a family of masked matrix codes obtained from K ′ dimensional Fq -subcodes of expanded Gabidulin codes.
- For m ∤ K ′ , where m is the extension degree, this dimension mismatch is not merely a randomization heuristic.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-992.pdf`
