---
id: KN-LIT-7516
type: literature
title: "Why Proving HIBE Systems Secure is Difficult"
authors:
  - "Allison Lewko"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Proving security of Hierarchical Identity-Based Encryption (HIBE) and Attribution Based Encryption scheme is a challenging problem. There are multiple well-known schemes in the literature where the best known (adaptive) security proofs degrade exponentially in the maximum hierarchy depth.

## Key claims (as reported)
- However, we do not have a rigorous understanding of why better proofs are not known.
- (For ABE, the analog of hierarchy depth is the maximum number of attributes used in a ciphertext.) In this work, we define a certain commonly found checkability property on ciphertexts and private keys.
- Roughly the property states that any two different private keys that are both “supposed to” decrypt a ciphertext will decrypt it to the same message.
- We show that any simple black box reduction to a non-interactive assumption for a HIBE or ABE system that contains this property will suffer an exponential degradation of security.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410161 (1).pdf`
- `downloads/84410161 (2).pdf`
- `downloads/84410161 (3).pdf`
- `downloads/84410161.pdf`
