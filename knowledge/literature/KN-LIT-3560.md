---
id: KN-LIT-3560
type: literature
title: "Efficient Fully Structure-Preserving Signatures for Large Messages"
authors:
  - "Jens Groth"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, mpc, pairing, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct both randomizable and strongly existentially unforgeable structure-preserving signatures for messages consisting of many group elements. To sign a message consisting of N = mn group elements we have a verification key size of m group elements and signatures contain n+2 elements.

## Key claims (as reported)
- Verification of a signature requires evaluating n+1 pairing product equations.
- We also investigate the case of fully structure-preserving signatures where it is required that the secret signing key consists of group elements only.
- We show a variant of our signature scheme allowing the signer to pick part of the verification key at the time of signing is still secure.
- This gives us both randomizable and strongly existentially unforgeable fully structure-preserving signatures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520108 (1).pdf`
- `downloads/94520108.pdf`
