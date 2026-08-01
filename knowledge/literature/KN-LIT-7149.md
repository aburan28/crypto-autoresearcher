---
id: KN-LIT-7149
type: literature
title: "Tightly secure hierarchical identity-based encryption"
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
tags: [pairing, provable-security, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first tightly secure hierarchical identitybased encryption (HIBE) scheme based on standard assumptions, which solves an open problem from Blazy, Kiltz, and Pan (CRYPTO 2014). At the core of our constructions is a novel randomization technique that enables us to randomize user secret keys for identities with flexible length.

## Key claims (as reported)
- The security reductions of previous HIBEs lose at least a factor of Q, which is the number of user secret key queries.
- Different to that, the security loss of our schemes is only dependent on the security parameter.
- Our schemes are adaptively secure based on the Matrix Diffie-Hellman assumption, which is a generalization of standard Diffie-Hellman assumptions such as k-Linear.
- We have two tightly secure constructions, one with constant ciphertext size, and the other with tighter security at the cost of linear ciphertext size.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420254 (1).pdf`
- `downloads/114420254.pdf`
