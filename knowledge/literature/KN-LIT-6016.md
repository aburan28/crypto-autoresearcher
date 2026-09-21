---
id: KN-LIT-6016
type: literature
title: "Public-Coin Statistical Zero-Knowledge Batch Verification against Malicious Verifiers?"
authors:
  - "Inbar Kaslasi"
  - "Ron D. Rothblum"
  - "Prashant Nalini Vasudevanr"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, lattice, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Suppose that a problem Π has a statistical zero-knowledge (SZK) proof with communication complexity m. The question of batch verification for SZK asks whether one can prove that k instances x1 , . . . , xk all belong to Π with a statistical zero-knowledge proof whose communication complexity is better than k · m (which is the complexity of the trivial solution of executing the original protocol independently on each input).

## Key claims (as reported)
- In a recent work, Kaslasi et al.
- (TCC, 2020) constructed such a batch verification protocol for any problem having a non-interactive SZK (NISZK) proof-system.
- Two drawbacks of their result are that their protocol is private-coin and is only zero-knowledge with respect to the honest verifier.
- In this work, we eliminate these two drawbacks by constructing a public-coin malicious-verifier SZK protocol for batch verification of NISZK.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960092 (1).pdf`
- `downloads/126960092.pdf`
