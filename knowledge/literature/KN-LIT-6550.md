---
id: KN-LIT-6550
type: literature
title: "Semi-Honest to Malicious Oblivious Transfer"
authors:
  - "The Black-Box Way"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, pairing, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Until recently, all known constructions of oblivious transfer protocols based on general hardness assumptions had the following form. First, the hardness assumption is used in a black-box manner (i.e., the construction uses only the input/output behavior of the primitive guaranteed by the assumption) to construct a semi-honest oblivious transfer, a protocol whose security is guaranteed to hold only against adversaries that follow the prescribed protocol.

## Key claims (as reported)
- Then, the latter protocol is “compiled” into a (malicious) oblivious transfer using non-black techniques (a Karp reduction is carried in order to prove an NP statement in zeroknowledge).
- In their recent breakthrough result, Ishai, Kushilevitz, Lindel and Petrank (STOC ’06) deviated from the above paradigm, presenting a blackbox reduction from oblivious transfer to enhanced trapdoor permutations and to homomorphic encryption.
- Here we generalize their result, presenting a black-box reduction from oblivious transfer to semi-honest oblivious transfer.
- Consequently, oblivious transfer can be black-box reduced to each of the hardness assumptions known to imply a semi-honest oblivious transfer in a black-box manner.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49480407 (1).pdf`
- `downloads/49480407 (2).pdf`
- `downloads/49480407 (3).pdf`
- `downloads/49480407.pdf`
