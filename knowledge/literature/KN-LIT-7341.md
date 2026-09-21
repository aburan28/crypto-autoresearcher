---
id: KN-LIT-7341
type: literature
title: "Unbounded HIBE with Tight Security"
authors:
  - "Roman Langrehr"
  - "Jiaxin Pan"
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
We propose the first tightly secure and unbounded hierarchical identity-based encryption (HIBE) scheme based on standard assumptions. Our main technical contribution is a novel proof strategy that allows us to tightly randomize user secret keys for identities with arbitrary hierarchy depths using low entropy hidden in a small and hierarchy-independent master public key.

## Key claims (as reported)
- The notion of unbounded HIBE is proposed by Lewko and Waters (Eurocrypt 2011).
- In contrast to most HIBE schemes, an unbounded scheme does not require any maximum depth to be specified in the setup phase, and user secret keys or ciphertexts can be generated for identities of arbitrary depths with hierarchy-independent system parameters.
- While all the previous unbounded HIBE schemes have security loss that grows at least linearly in the number of user secret key queries, the security loss of our scheme is only dependent on the security parameter, even in the multi-challenge setting, where an adversary can ask for multiple challenge ciphertexts.
- We prove the adaptive security of our scheme based on the Matrix Decisional Diffie-Hellman assumption in prime-order pairing groups, which generalizes a family of standard Diffie-Hellman assumptions such as k-Linear.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491313 (1).pdf`
- `downloads/12491313.pdf`
