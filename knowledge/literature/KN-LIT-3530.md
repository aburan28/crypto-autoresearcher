---
id: KN-LIT-3530
type: literature
title: "Efficient Batch Zero-Knowledge Arguments for Low Degree Polynomials?"
authors:
  - "Jonathan Bootle"
  - "Jens Groth"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, mov-fr, pairing, provable-security, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
(EUROCRYPT 2016) construct an extremely efficient zero-knowledge argument for arithmetic circuit satisfiability in the discrete logarithm setting. However, the argument does not treat relations involving commitments, and furthermore, for simple polynomial relations, the complex machinery employed is unnecessary.

## Key claims (as reported)
- In this work, we give a framework for expressing simple relations between commitments and field elements, and present a zero-knowledge argument which, by contrast with Bootle et al., is constant-round and uses fewer group operations, in the case where the polynomials in the relation have low degree.
- Our method also directly yields a batch protocol, which allows many copies of the same relation to be proved and verified in a single argument more efficiently with only a square-root communication overhead in the number of copies.
- We instantiate our protocol with concrete polynomial relations to construct zero-knowledge arguments for membership proofs, polynomial evaluation proofs, and range proofs.
- Our work can be seen as a unified explanation of the underlying ideas of these protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770182 (1).pdf`
- `downloads/10770182 (2).pdf`
- `downloads/10770182 (3).pdf`
- `downloads/10770182 (4).pdf`
- `downloads/10770182.pdf`
