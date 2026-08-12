---
id: KN-LIT-4755
type: literature
title: "Linear VSS and Distributed Commitments Based on Secret Sharing and Pairwise Checks"
authors:
  - "Serge Fehr"
  - "Ueli Maurer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a general treatment of all non-cryptographic (i.e., information-theoretically secure) linear verifiable-secret-sharing (VSS) and distributed-commitment (DC) schemes, based on an underlying secret sharing scheme, pairwise checks between players, complaints, and accusations of the dealer. VSS and DC are main building blocks for unconditional secure multi-party computation protocols.

## Key claims (as reported)
- This general approach covers all known linear VSS and DC schemes.
- The main theorem states that the security of a scheme is equivalent to a pure linear-algebra condition on the linear mappings (e.g. described as matrices and vectors) describing the scheme.
- The security of all known schemes follows as corollaries whose proofs are pure linear-algebra arguments, in contrast to some hybrid arguments used in the literature.
- Our approach is demonstrated for the CDM DC scheme, which we generalize to be secure against mixed adversary settings (some curious and some dishonest players), and for the classical BGW VSS scheme, for which we show that some of the checks between players are superfluous, i.e., the scheme is not optimal.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420566 (1).pdf`
- `downloads/24420566 (2).pdf`
- `downloads/24420566.pdf`
