---
id: KN-LIT-3710
type: literature
title: "Essentially Optimal"
authors:
  - "Rajmohan Rajaraman"
  - "Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a t-out-of-n robust secret sharing scheme, a secret message is shared among n parties who can reconstruct the message by combining their shares. An adversary can adaptively corrupt up to t of the parties, get their shares, and modify them arbitrarily.

## Key claims (as reported)
- The scheme should satisfy privacy, meaning that the adversary cannot learn anything about the shared message, and robustness, meaning that the adversary cannot cause the reconstruction procedure to output an incorrect message.
- Such schemes are only possible in the case of an honest majority, and here we focus on unconditional security in the maximal corruption setting where n = 2t + 1.
- In this scenario, to share an m-bit message with a reconstruction failure probability of at most 2−k , a known lower-bound shows that the share size must be at least m+k bits.
- On the other hand, all prior constructions have share size that scales linearly with the number of parties n, and the prior state-of-the-art scheme due to Cevallos et al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650259 (1).pdf`
- `downloads/96650259.pdf`
