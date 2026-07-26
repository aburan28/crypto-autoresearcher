---
id: KN-LIT-1461
type: literature
title: "Recursion Enabled: Improved Cryptanalysis of the Permuted Kernel Problem"
authors:
  - "Alessandro Budroni"
  - "Marco Defranceschi"
  - "Federico Pintore"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/2073"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/2073"
tags: [binary-field, cryptanalysis, finite-field, lattice, pairing, pqc, provable-security, quantum, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Permuted Kernel Problem (PKP) is a computational problem for linear codes over finite fields that has emerged as a promising hard problem for constructing post-quantum cryptographic schemes, with its main application found in the digital signature scheme PERK, submitted to the NIST standardization process for quantum-secure additional signatures. Upon reviewing the first version of PERK, NIST recommended further research on the concrete complexity of PKP.

## Key claims (as reported)
- In this work, we follow this recommendation and investigate algorithmic improvements to the known methods for solving PKP.
- Specifically, we build upon the state-of-the-art work of Santini, Baldi, and Chiaraluce (IEEE Trans.
- Theory, 2024), and introduce a new algorithm that outperforms it over a wide range of parameters, yielding double-digit bit reductions in estimated complexity on representative instances.
- Nevertheless, our analysis shows that these improvements do not affect the parameter-set choices in PERK, thereby reinforcing confidence in its security.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-2073.pdf`
