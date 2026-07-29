---
id: KN-LIT-1408
type: literature
title: "INKE: Isogeny-Based PKE Using Intermediate Curves"
authors:
  - "Hyeonhak Kim"
  - "Won Kim"
  - "Changmin Lee"
  - "Suhri Kim"
  - "Seokhie Hong"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1458"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1458"
tags: [class-group, cryptanalysis, elliptic-curve, finite-field, isogeny, lattice, number-theory, pqc, protocol, provable-security, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
POKÉ (POint-based Key Exchange), proposed by Basso and Maino at Eurocrypt 2025, is currently the fastest known isogeny-based public-key encryption scheme. Although POKÉ is secure against currently known key-recovery attacks, there is no known reduction from key-recovery security to IND-CPA security.

## Key claims (as reported)
- In this work, we propose INKE, a variant of POKÉ that replaces torsion points in the encryption process with intermediate elliptic curves.
- This modification enables a quantum reduction from key-recovery security to IND-CPA security in the algebraic isogeny model (AIM), while maintaining the practical performance.
- Although INKE is overall slower than POKÉ and has larger public-key and ciphertext sizes, it remains more efficient than other group-actionbased key exchange protocols such as CSIDH and CORAL that admit reductions from key-recovery security to shared-secret security in algebraic group action model (AGAM).
- To illustrate the practical overhead of INKE compared to POKÉ, we provide an optimized C implementation together with detailed benchmark comparisons at each security level.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1458.pdf`
