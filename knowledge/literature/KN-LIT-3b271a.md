---
id: KN-LIT-3b271a
type: literature
title: The ePrint:2026/1591 Quantum Algorithm Does Not Solve DCP
authors:
- Aparna Gupte
- Seyoon Ragavan
- Mark Zhandry
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/1693
identifiers:
  eprint: iacr:2026/1693
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/1693
source:
  citation: Aparna Gupte, Seyoon Ragavan, Mark Zhandry. The ePrint:2026/1591 Quantum Algorithm Does Not Solve DCP. Cryptology
    ePrint Archive 2026/1693, 2026.
  url: https://eprint.iacr.org/2026/1693
tags:
- dcp
- quantum
- lwe
- svp
- refutation
- lean
- dihedral-coset
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

The authors prove Simon’s ePrint 2026/1591 algorithm cannot extract the least-significant bit of the DCP secret with non-negligible advantage, and extend the no-go to a broader algorithm family. Their abstract identifies the failure to use enough classical Fourier-label information during uncomputation and links Lean 4 formalization.

## Scope and evidence boundary

This refutes the specified DCP algorithm family, not the possibility of some different future quantum attack on LWE. The original Simon entry KN-LIT-e204ab remains a historical record of a claim at its initial publication date.

## Research follow-up

Use the primary proof and linked Lean artifact before citing an unconditional refutation; pair this entry with the independent analysis KN-LIT-a2a423.

Source: [https://eprint.iacr.org/2026/1693](https://eprint.iacr.org/2026/1693); ePrint received 2026-08-15. Abstract and metadata read on 2026-09-26; result not reproduced.
