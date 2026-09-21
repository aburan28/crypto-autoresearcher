---
id: KN-LIT-7524
type: literature
title: "Witness Indistinguishability for any"
authors:
  - "Single-Round Argument"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Consider an access policy for some resource which only allows access to users of the system who own a certain set of attributes. Specifically, we consider the case where such an access structure is defined by some monotone function f : {0, 1}N → {0, 1}, belonging to some class of function F (e.g. conjunctions, space bounded computation), where N is the number of possible attributes.

## Key claims (as reported)
- In this work we show that any succinct single-round delegation scheme for the function class F can be converted into a succinct single-round private access control protocol.
- That is, a verifier can be convinced that an approved user (i.e. one which holds an approved set of attributes) is accessing the system, without learning any additional information about the user or the set of attributes.
- As a main tool of independent interest, we show that assuming a quasipolynomially secure two-message oblivious transfer scheme with statistical sender privacy (which can be based on quasi-polynomial hardness of the DDH, QR, DCR or LWE assumptions), we can convert any singleround protocol into a witness indistinguishable one, with similar communication complexity.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110280 (1).pdf`
- `downloads/12110280.pdf`
