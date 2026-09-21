---
id: KN-LIT-1827
type: literature
title: "Quantum algorithm for Discrete Gaussian Sampling"
authors:
  - "Univ Rennes"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/984"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/984"
tags: [cryptanalysis, lattice, pairing, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Discrete Gaussian Sampling on lattices is a fundamental problem in lattice-based cryptography. It appears both in basic cryptographic primitives such as digital signatures and as an important cryptanalysis building block for solving hard lattice problems.

## Key claims (as reported)
- In this paper, we show a quantum algorithm based on the quantum rejection sampling technique whose complexity is asymptotically quadratically faster than its classical counterpart in [Wang & Ling, IEEE Trans.
- Our sampler outputs a quantum state which can either be measured to get the desired distribution or be used directly as such in other quantum algorithms.
- By doing so, we derive two versions of quantum dual attacks that improve upon the previous ones in [Pouly & Shen, EUROCRYPT 2024].
- The two versions are incomparable, each having distinct advantages (speed vs memory requirement).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-984.pdf`
