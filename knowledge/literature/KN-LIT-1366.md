---
id: KN-LIT-1366
type: literature
title: "Cryptanalysis of Isogeny-Based Quantum Money with Rational Points"
authors:
  - "Hyeonhak Kim"
  - "Donghoe Heo"
  - "Seokhie Hong⋆"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/201"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/201"
tags: [class-group, cryptanalysis, curve-arithmetic, dlp, elliptic-curve, isogeny, number-theory, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Quantum money is the cryptographic application of the quantum no-cloning theorem. It has recently been instantiated by Montgomery and Sharif (Asiacrypt ’24) from class group actions on elliptic curves.

## Key claims (as reported)
- In this work, we propose a concrete cryptanalysis by leveraging the efficiency of evaluating division polynomials with the coordinates of rational points, offering a speedup of O(log4 p) compared to the bruteforce attack.
- Since our attack still requires exponential time, it remains impractical to forge a quantum banknote.
- Interestingly, due to the inherent properties of quantum money, our attack method also results in a more efficient verification procedure.
- Our algorithm leverages the properties of quadratic twists to utilize rational points in verifying the cardinality of the superposition of elliptic curves.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-201.pdf`
