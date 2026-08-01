---
id: KN-LIT-5212
type: literature
title: "Non-Malleable Codes for Partial Functions with Manipulation Detection"
authors:
  - "Aggelos Kiayias"
  - "Feng-Hao Liu"
  - "Yiannis Tselekounis"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Non-malleable codes were introduced by Dziembowski, Pietrzak and Wichs (ICS ’10) and its main application is the protection of cryptographic devices against tampering attacks on memory. In this work, we initiate a comprehensive study on non-malleable codes for the class of partial functions, that read/write on an arbitrary subset of codeword bits with specific cardinality.

## Key claims (as reported)
- Our constructions are efficient in terms of information rate, while allowing the attacker to access asymptotically almost the entire codeword.
- In addition, they satisfy a notion which is stronger than non-malleability, that we call non-malleability with manipulation detection, guaranteeing that any modified codeword decodes to either the original message or to ⊥.
- Finally, our primitive implies AllOr-Nothing Transforms (AONTs) and as a result our constructions yield efficient AONTs under standard assumptions (only one-way functions), which, to the best of our knowledge, was an open question until now.
- In addition to this, we present a number of additional applications of our primitive in tamper resilience.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993170 (1).pdf`
- `downloads/10993170.pdf`
