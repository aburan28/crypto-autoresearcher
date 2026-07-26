---
id: KN-LIT-5825
type: literature
title: "Practical and Employable Protocols for UC-Secure Circuit Evaluation over Zn ?"
authors:
  - "Jan Camenisch"
  - "Robert R. Enderlein"
  - "Victor Shoup"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, fhe, pairing, protocol, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a set of new, efficient, universally composable two-party protocols for evaluating reactive arithmetic circuits modulo n, where n is a safe RSA modulus of unknown factorization. Our protocols are based on a homomorphic encryption scheme with message space Zn , zero-knowledge proofs of existence, and a novel “mixed” trapdoor commitment scheme.

## Key claims (as reported)
- Our protocols are proven secure against adaptive corruptions (assuming secure erasures) under standard assumptions in the CRS model (without random oracles).
- Our protocols appear to be the most efficient ones that satisfy these security requirements.
- In contrast to prior protocols, we provide facilities that allow for the use of our protocols as building blocks of higher-level protocols.
- An additional contribution of this paper is a universally composable construction of the variant of the Dodis-Yampolskiy oblivious pseudorandom function in a group of order n as originally proposed by Jarecki and Liu.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/ces13.pdf`
