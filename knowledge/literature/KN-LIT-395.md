---
id: KN-LIT-395
type: literature
title: "From Weak to Strong Zero-Knowledge and Applications?"
authors:
  - "Kai-Min Chung"
  - "Edward Lui"
  - "Rafael Pass"
year: 2013
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2013/260"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2013/260"
tags: [complexity-theory, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The notion of zero-knowledge [20] is formalized by requiring that for every malicious efficient verifier V ∗ , there exists an efficient simulator S that can reconstruct the view of V ∗ in a true interaction with the prover, in a way that is indistinguishable to every polynomial-time distinguisher. Weak zero-knowledge weakens this notions by switching the order of the quantifiers and only requires that for every distinguisher D, there exists a (potentially different) simulator SD .

## Key claims (as reported)
- In this paper we consider various notions of zero-knowledge, and investigate whether their weak variants are equivalent to their strong variants.
- Although we show (under complexity assumption) that for the standard notion of zero-knowledge, its weak and strong counterparts are not equivalent, for meaningful variants of the standard notion, the weak and strong counterparts are indeed equivalent.
- Towards showing these equivalences, we introduce new non-black-box simulation techniques permitting us, for instance, to demonstrate that the classical 2-round graph non-isomorphism protocol of Goldreich-Micali-Wigderson [18] satisfies a “distributional” variant of zero-knowledge.
- Our equivalence theorem has other applications beyond the notion of zero-knowledge.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90140066 (1).pdf`
- `downloads/90140066.pdf`
