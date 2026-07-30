---
id: KN-LIT-7550
type: literature
title: "Zero-Knowledge Elementary Databases with More Expressive Queries"
authors:
  - "Huaxiong Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, lattice, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Zero-knowledge elementary databases (ZK-EDBs) are cryptographic schemes that allow a prover to commit to a set D of key-value pairs so as to be able to prove statements such as “x belongs to the support of D and D(x) = y” or “x is not in the support of D”. Importantly, proofs should leak no information beyond the proven statement and even the size of D should remain private.

## Key claims (as reported)
- (Eurocrypt’05) showed that ZK-EDBs are implied by a special flavor of non-interactive commitment, called mercurial commitment, which enables efficient instantiations based on standard number theoretic assumptions.
- On the other hand, the resulting ZK-EDBs are only known to support proofs for simple statements like (non-)membership and value assignments.
- In this paper, we show that mercurial commitments actually enable significantly richer queries.
- We show that, modulo an additional security property met by all known efficient constructions, they actually enable range queries over keys and values – even for ranges of super-polynomial size – as well as membership/non-membership queries over the space of values.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420255 (1).pdf`
- `downloads/114420255.pdf`
