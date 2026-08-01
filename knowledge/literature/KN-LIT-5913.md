---
id: KN-LIT-5913
type: literature
title: "Private Coins versus Public Coins in Zero-Knowledge Proof Systems"
authors:
  - "Rafael Pass"
  - "Muthuramakrishnan Venkitasubramaniam"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Goldreich-Krawczyk (Siam J of Comp’96) showed that only languages in BPP have constant-round public-coin black-box zero-knowledge protocols. We extend their lower bound to “fully black-box” privatecoin protocols based on one-way functions.

## Key claims (as reported)
- More precisely, we show that only languages in BPPSam —where Sam is a “collision-finding” oracle in analogy with Simon (Eurocrypt’98) and Haitner et. al (FOCS’07)—can have constant-round fully black-box zero-knowledge proofs; the same holds for constant-round fully black-box zero-knowledge arguments with sublinear verifier communication complexity.
- We also establish nearlinear lower bounds on the round complexity of fully black-box concurrent zero-knowledge proofs (or arguments with sublinear verifier communication) for languages outside BPPSam .
- The technique used to establish these results is a transformation from private-coin protocols into Sam-relativized public-coin protocols; for the case of fully black-box protocols based on one-way functions, this transformation preserves zero knowledge, round complexity and communication complexity.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59780584 (1).pdf`
- `downloads/59780584 (2).pdf`
- `downloads/59780584 (3).pdf`
- `downloads/59780584.pdf`
