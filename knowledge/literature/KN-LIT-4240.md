---
id: KN-LIT-4240
type: literature
title: "Homomorphic Signatures for Polynomial Functions"
authors:
  - "Dan Boneh"
  - "David Mandell Freeman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, finite-field, lattice, pairing, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first homomorphic signature scheme that is capable of evaluating multivariate polynomials on signed data. Given the public key and a signed data set, there is an efficient algorithm to produce a signature on the mean, standard deviation, and other statistics of the signed data.

## Key claims (as reported)
- Previous systems for computing on signed data could only handle linear operations.
- For polynomials of constant degree, the length of a derived signature only depends logarithmically on the size of the data set.
- Our system uses ideal lattices in a way that is a “signature analogue” of Gentry’s fully homomorphic encryption.
- Security is based on hard problems on ideal lattices similar to those in Gentry’s system.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320147 (1).pdf`
- `downloads/66320147 (2).pdf`
- `downloads/66320147 (3).pdf`
- `downloads/66320147.pdf`
