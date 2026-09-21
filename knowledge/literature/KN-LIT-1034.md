---
id: KN-LIT-1034
type: literature
title: "Revisiting Related-Key Boomerang attacks on AES using computer-aided tool"
authors:
  - "Patrick Derbez"
  - "Marie Euler"
  - "Pierre-Alain Fouque"
  - "Phuong Hoa"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/725"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/725"
tags: [cryptanalysis, hash, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In recent years, several MILP models were introduced to search automatically for boomerang distinguishers and boomerang attacks on block ciphers. However, they can only be used when the key schedule is linear.

## Key claims (as reported)
- Here, a new model is introduced to deal with nonlinear key schedules as it is the case for AES.
- This model is more complex and actually it is too slow for exhaustive search.
- However, when some hints are added to the solver, it found the current best related-key boomerang attack on AES-192 with 2124 time, 2124 data, and 279.8 memory complexities, which is better than the one presented by Biryukov and Khovratovich at ASIACRYPT 2009 with complexities 2176 /2123 /2152 respectively.
- This represents a huge improvement for the time and memory complexity, illustrating the power of MILP in cryptanalysis.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910302 (1).pdf`
- `downloads/137910302.pdf`
- `downloads/2022-725.pdf`
