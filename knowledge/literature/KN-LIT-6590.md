---
id: KN-LIT-6590
type: literature
title: "Short Pairing-Free Blind Signatures with Exponential Security"
authors:
  - "Stefano Tessaro"
  - "Chenzhi Zhu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, elliptic-curve, mov-fr, pairing, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proposes the first practical pairing-free threemove blind signature schemes that (1) are concurrently secure, (2) produce short signatures (i.e., three or four group elements/scalars), and (3) are provably secure either in the generic group model (GGM) or the algebraic group model (AGM) under the (plain or one-more) discrete logarithm assumption (beyond additionally assuming random oracles). We also propose a partially blind version of one of our schemes.

## Key claims (as reported)
- Our schemes do not rely on the hardness of the ROS problem (which can be broken in polynomial time) or of the mROS problem (which admits sub-exponential attacks).
- The only prior work with these properties is Abe’s signature scheme (EUROCRYPT ’02), which was recently proved to be secure in the AGM by Kastner et al.
- (PKC ’22), but which also produces signatures twice as long as those from our scheme.
- The core of our proofs of security is a new problem, called weighted fractional ROS (WFROS), for which we prove (unconditional) exponential lower bounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760224 (1).pdf`
- `downloads/132760224.pdf`
