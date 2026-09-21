---
id: KN-LIT-706
type: literature
title: "Reducing the Cost of Implementing AES as a Quantum Circuit"
authors:
  - "Brandon Langenberg"
  - "Hai Pham"
  - "Rainer Steinwandt"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/854"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/854"
tags: [binary-field, cryptanalysis, pqc, provable-security, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
To quantify security levels in a post-quantum scenario, it is common to use the quantum resources needed to attack AES as a reference value. Specifically, in NIST’s ongoing post-quantum standardization effort, different security categories are defined that reflect the quantum resources needed to attack AES-128, AES-192, and AES-256.

## Key claims (as reported)
- This paper presents a quantum circuit to implement the S-box of AES.
- Leveraging also an improved implementation of the key expansion, we identify new quantum circuits for all three AES key lengths.
- For AES-128, the number of Toffoli gates can be reduced by more than 88% compared to Almazrooie et al.’s and Grassl et al.’s estimates, while simultaneously reducing the number of qubits.
- Our circuits can be used to simplify a Grover-based key search for AES.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2019-854.pdf`
