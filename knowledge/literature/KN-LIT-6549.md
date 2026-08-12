---
id: KN-LIT-6549
type: literature
title: "Semi-Homomorphic Encryption and Multiparty Computation"
authors:
  - "Rikke Bendlin"
  - "Ivan Damgård"
  - "Claudio Orlandi"
  - "Sarah Zakarias"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pairing, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An additively-homomorphic encryption scheme enables us to compute linear functions of an encrypted input by manipulating only the ciphertexts. We define the relaxed notion of a semi-homomorphic encryption scheme, where the plaintext can be recovered as long as the computed function does not increase the size of the input “too much”.

## Key claims (as reported)
- We show that a number of existing cryptosystems are captured by our relaxed notion.
- In particular, we give examples of semi-homomorphic encryption schemes based on lattices, subset sum and factoring.
- We then demonstrate how semi-homomorphic encryption schemes allow us to construct an efficient multiparty computation protocol for arithmetic circuits, UC-secure against a dishonest majority.
- The protocol consists of a preprocessing phase and an online phase.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320167 (1).pdf`
- `downloads/66320167 (2).pdf`
- `downloads/66320167 (3).pdf`
- `downloads/66320167.pdf`
