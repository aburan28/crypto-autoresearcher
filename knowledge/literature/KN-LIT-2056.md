---
id: KN-LIT-2056
type: literature
title: "A Framework for Practical Anonymous Credentials from Lattices"
authors:
  - "Jonathan Bootle⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, lattice, pairing, pqc, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a framework for building practical anonymous credential schemes based on the hardness of lattice problems. The running time of the prover and verifier is independent of the number of users and linear in the number of attributes.

## Key claims (as reported)
- The scheme is also compact in practice, with the proofs being as small as a few dozen kilobytes for arbitrarily 128 large (say up to 2 ) numbers of users with each user having several attributes.
- The security of our scheme is based on a new family of lattice assumptions which roughly states that given short pre-images of random elements in some set S, it is hard to create a pre-image for a fresh element in such a set.
- We show that if the set admits efficient zero-knowledge proofs of knowledge of a commitment to a set element and its pre-image, then this yields practically-efficient privacy-preserving primitives such as blind signatures, anonymous credentials, and group signatures.
- We propose a candidate instantiation of a function from this family which allows for such proofs and thus yields practical lattice-based primitives.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850431 (1).pdf`
- `downloads/140850431.pdf`
