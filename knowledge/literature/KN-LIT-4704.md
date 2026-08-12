---
id: KN-LIT-4704
type: literature
title: "Learning a Zonotope and More: Cryptanalysis of NTRUSign Countermeasures"
authors:
  - "Dept. Informatique"
  - "rue d’Ulm"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, ecdsa, fhe, lattice, pairing, provable-security, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
NTRUSign is the most practical lattice signature scheme. Its basic version was broken by Nguyen and Regev in 2006: one can efficiently recover the secret key from about 400 signatures.

## Key claims (as reported)
- However, countermeasures have been proposed to repair the scheme, such as the perturbation used in NTRUSign standardization proposals, and the deformation proposed by Hu et al. at IEEE Trans.
- These two countermeasures were claimed to prevent the NR attack.
- Surprisingly, we show that these two claims are incorrect by revisiting the NR gradientdescent attack: the attack is more powerful than previously expected, and actually breaks both countermeasures in practice, e.g.
- 8,000 signatures suffice to break NTRUSign-251 with one perturbation as submitted to IEEE P1363 in 2003.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580428 (1).pdf`
- `downloads/76580428 (2).pdf`
- `downloads/76580428 (3).pdf`
- `downloads/76580428.pdf`
