---
id: KN-LIT-1874
type: literature
title: "Single-Trace Power Analysis of LESS Key Generation Süleyman Emir Akın1[0009−0002−7684−4763]"
authors:
  - "Abdullah Talayhan"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/990"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/990"
tags: [cryptanalysis, dlp, ecdsa, factoring, isogeny, lattice, mov-fr, pqc, quantum, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a side-channel attack on the Linear Equivalence Signature Scheme (LESS) v2.0. LESS derives its security from the Linear Equivalence Problem and was evaluated as a candidate during Round 2 of the NIST post-quantum cryptography standardization process.

## Key claims (as reported)
- LESS secret keys are used to generate monomial matrices, which are stored efficiently in two one-dimensional lists: the permutation list and the coefficient list.
- Recovering the secret monomial matrices is sufficient to forge signatures, as they are the values actually used during signing.
- We propose a profiled, single-trace horizontal attack that recovers the full secret monomial matrices.
- First, monomial coefficients that are multiplied by the dense part of the public generator matrix are recovered via power analysis of the matrix multiplication function.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-990.pdf`
